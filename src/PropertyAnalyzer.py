# Local Amenities
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNetCV, LinearRegression, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from KNeighborsMedianRegressor import KNeighborsMedianRegressor
from sklearn.preprocessing import StandardScaler
from ReadAPI import ReadAPI
import pandas as pd
import numpy as np
from utils import to_markdown
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords
from string import punctuation
from spacy.lang.en import English
parser = English()


class PropertyAnalyzer(object):
    """Finds amenity values for neighbors given an airbnb url"""
    def __init__(self, url, k_neighbors=6, verbose=False, distance_weight=1, num_comps=20):
        self.url = url
        self.property_id = url[url.rfind('/')+1: url.rfind('?')] # quick isolation of ID
        self.token = os.environ['AIRDNA_API_TOKEN'] #API key
        self.amenities = pd.DataFrame()
        self.comps = pd.DataFrame()
        self.my_property = pd.DataFrame()
        self.k = k_neighbors
        self.verbose = verbose
        self.distance_weight = distance_weight #Increase distance weight to find closer neighbors
        self.ReadAPI = ReadAPI(self.token, verbose=self.verbose, num_comps=num_comps)

    def get_comps(self):
        """Uses the airDNA API to return comps, data for the current property and a list of amenities included in the dataframe
        Returns:
        comps: pd.DataFrame size=(Number of comps, info columns)
        amenities: pd.DataFrame size=(amenities, )
        my_property: pd.DataFrame size =(, info columns)"""
        comps, my_property, amenities = self.ReadAPI.get_comps_from_id(self.property_id)
        self.amenities = amenities.to_frame().reset_index()[0] # create df from list for consistency
        self.comps = comps.dropna(axis=1) # drop all null axes
        self.my_property = my_property[comps.columns] #Only select columns present in comps

    def load_comps(self, comps, my_property, amenities):
        """Initialize class from saved variables"""
        self.comps = comps
        self.my_property = my_property
        self.amenities =  my_amenities

    def create_test_df(self, query_df, mat):
        """Split and scale df"""

        scaler = StandardScaler()

        y = mat.pop('rev_pot') #Pop target for properties with the amenity
        X = mat.append(query_df) #add the query to the bottom so it can be scaled with the data
        # Scale the feature matrices
        X = scaler.fit_transform(X)

        X[:, 3:] = X[:, 3:]*self.distance_weight
        #Multiply latitude and longitude by distance_weight, increasing this makes tighter clusters
        X[:, 3:] = X[:, 3:]*self.distance_weight
        #Remove the query property and put it in its own dataframe
        predict = X[-1].reshape(1, -1)
        X = X[:-1, :]
        return X, y, predict

    def find_revenue_potential(self, amenity_x, scaling=True):
        """ Finds the revenue potential for an amenity
        returns rev_pot: float
        """

        #Datafame to find neighbors from, made from a 'query property'
        query_df = self.my_property[['bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude']].astype('float')

        #Comp dataframe to find neighbors in
        df = self.comps[['rev_pot', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', amenity_x]].astype('float')
        #Creates two dataframes, one for properties that have the amenity and one for those who don't
        w_amenity = df[df[amenity_x].astype('bool')].drop(columns=[amenity_x])
        w_out_amenity = df[~df[amenity_x].astype('bool')].drop(columns=[amenity_x])

        #Split and scale df
        X_w, y_w, w_predict = self.create_test_df(query_df, w_amenity)

        X_w_out, y_w_out, w_out_predict = self.create_test_df(query_df, w_out_amenity)

        #Check to make sure dataframes have enough neighbors
        k = min(X_w_out.shape[0], X_w.shape[0])
        #Don't return results if there's not enough neighbors
        if k < 3:
            return 0

        #Initialize & fit neighbors
        kn_w = KNeighborsRegressor(n_neighbors=k, weights='distance', n_jobs=-1)
        kn_w_out = KNeighborsRegressor(n_neighbors=k, weights='distance', n_jobs=-1)
        kn_w.fit(X_w, y_w)
        kn_w_out.fit(X_w_out, y_w_out)

        # find neighbors and their similarity(distance) to the query
        w_distance, w_neighbors = kn_w.kneighbors(w_predict)
        w_neighbors_df = w_amenity.iloc[w_neighbors.flatten()]

        w_out_distance, w_out_neighbors = kn_w_out.kneighbors(w_out_predict)
        w_out_neighbors_df = w_out_amenity.iloc[w_out_neighbors.flatten()]

        # predict revenue for nearby properties with and without the amenity
        w_revenue = kn_w.predict(w_predict)[0]
        w_out_revenue = kn_w_out.predict(w_out_predict)[0]
        rev_pot = w_revenue - w_out_revenue # calculate the potential upside

        if self.verbose:
            print(f"with amenity {w_amenity['accommodates'].mean()}")
            print(f"without amenity {w_out_amenity['accommodates'].mean()}")
            print(
                f'Average yearly revenue with {amenity_x}: $ {w_revenue:.0f} \n Without: $ {w_out_revenue:.0f} \n Yearly revenue potential :  $ { rev_pot:.0f}')
        return rev_pot

    def best_amenities(self):
        """Iterates through amenities to find the revenue potentual for each"""
        revenue_potentials = pd.DataFrame(columns=['revenue_potential'])
        for amenity in self.amenities:
            rev_pot = self.find_revenue_potential(amenity)
            revenue_potentials.loc[amenity] = rev_pot
        return revenue_potentials.sort_values(by='revenue_potential', ascending=False)

    def spacy_tokenizer(self, doc):
        """Tokenizer for property text fields"""
        tokens = parser(doc)
        tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
        tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuation)]
        return tokens

    def NLP(self):
        """Performs a linear regression on a TF-IDF matrix of property titles vs. revenue potential"""

        #load and vectorize titles
        corpus = self.comps['title']
        target =  self.comps['rev_pot']
        vec =  TfidfVectorizer(tokenizer = self.spacy_tokenizer, max_features = 15, max_df = 1.0, ngram_range = (1,1))
        matrix = vec.fit_transform(corpus)

        #perform ridge regression and return dataframe of coefficients
        ls = RidgeCV()
        ls.fit(matrix, target)
        coefficients_df = pd.DataFrame.from_dict(dict(zip(vec.get_feature_names(), ls.coef_)), orient='index').sort_values(by=0)
        score = ls.score(matrix, target)
        print(f"R^2 = {score: .3f} \n Alpha: {ls.alpha_ : .3f}")

        return coefficients_df


def main():
    """Analyzes a single property from a url"""
    # url = input("URL: ")
    url = 'https://www.airbnb.com/rooms/14143174?location=Breckenridge%2C%20CO%2C%20United%20States&adults=1&children=0&infants=0&s=nwtUEb3-'
    prp = PropertyAnalyzer(url, verbose=True, num_comps=40)
    prp.get_comps()
    # prp.NLP()

    # Print formatted tables of results
    to_markdown(prp.best_amenities())
    to_markdown(prp.NLP())


if __name__ == '__main__':
    main()
