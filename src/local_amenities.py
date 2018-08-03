# Local Amenities

from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNetCV, LinearRegression, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from get_data_from_api import ReadAPI
import pandas as pd
import numpy as np
from utils import to_markdown
import os
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords
from string import punctuation
from sklearn.linear_model import LassoCV, RidgeCV
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
        # self.get_comps() # get comps from AirDNA API

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

    def cluster(self, amenity_x, scaling=True):
        """ Finds the revenue potential for an amenity
        returns rev_pot: float
        """

        #Datafame to find neighbors from, made from a 'query property'
        query_df = self.my_property[['bedrooms', 'bathrooms',
                                     'accommodates', 'latitude', 'longitude']]

        #Comp dataframe to find neighbors in
        df = self.comps[['rev_pot', 'bedrooms', 'bathrooms',
                         'accommodates', 'latitude', 'longitude', amenity_x]]

        #Creates two dataframes, one for properties that have the amenity and one for those who don't
        w_amenity = df[df[amenity_x].astype('bool')].drop(columns=[amenity_x])
        w_out_amenity = df[~df[amenity_x].astype('bool')].drop(columns=[amenity_x])

        #Split and scale df
        X_w, y_w, w_predict = self.create_test_df(query_df, w_amenity)

        X_w_out, y_w_out, w_out_predict = self.create_test_df(query_df, w_out_amenity)

        #Check to make sure dataframes have enough neighbors
        if (X_w_out.shape[0] < self.k) or (X_w.shape[0] < self.k):
            return 0

        #Initialize & fit neighbors
        kn_w = KNeighborsRegressor(n_neighbors=self.k, weights='distance', n_jobs=-1)
        kn_w_out = KNeighborsRegressor(n_neighbors=self.k, weights='distance', n_jobs=-1)
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
            print(
                f'Average yearly revenue with {amenity_x}: $ {w_revenue:.0f} \n Without: $ {w_out_revenue:.0f} \n Yearly revenue potential :  $ { rev_pot:.0f}')
        return rev_pot

    def best_amenities(self):
        """Iterates through amenities to find the revenue potentual for each"""
        revenue_potentials = pd.DataFrame(columns=['revenue_potential'])
        for amenity in self.amenities:
            rev_pot = self.cluster(amenity)
            revenue_potentials.loc[amenity] = rev_pot
        return revenue_potentials.sort_values(by='revenue_potential', ascending=False)

    def run_local_regression(self):
        """Beta code to run regressions on returned data"""
        # self.get_comps()
        not_included_in_property = self.my_property.loc[self.my_property == 0].index
        y = self.comps.pop('rev_pot')
        # X = self.comps[not_included_in_property]
        X = self.comps.drop(columns=['latitude', 'longitude',  'cover_img', 'airbnb_property_id', 'cover_img', 'distance_meters',
                                     'listing_url', 'location', 'property_type', 'room_type', 'stats', 'title', 'amenities', 'extra_person_charge'], errors='ignore')
        X['constant'] = 1

        scaler = StandardScaler()
        X_scale = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scale, y, test_size=0.1, random_state=5)
        en = ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, .99, 1], eps=1e-3, n_jobs=-1)
        en.fit(X_train, y_train)
        train_score = en.score(X_train, y_train)
        test_score = en.score(X_test, y_test)
        print(
            f"ElasticNet R^2:\n Train {train_score: .3f} \n Test {test_score:.3f} \n Alpha: {en.alpha_ : .3f} \n l1_ratio: {en.l1_ratio_}")
        coefficients_df = pd.DataFrame.from_dict(
            dict(zip(X.columns, en.coef_)), orient='index').sort_values(by=0)

        to_markdown(coefficients_df)

        lm = LinearRegression()
        lm.fit(X_train, y_train)
        train_score = lm.score(X_train, y_train)
        test_score = lm.score(X_test, y_test)
        coefficients_df = pd.DataFrame.from_dict(
            dict(zip(X.columns, lm.coef_)), orient='index').sort_values(by=0)

        print(f"Standard Linear R^2: train: {train_score: .3f}\n test: {test_score: .3f}")
        to_markdown(coefficients_df)

    def spacy_tokenizer(self, doc):
        tokens = parser(doc)
        tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
        tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuation)]
        return tokens

    def do_NLP(self):
        # comps = pd.read_pickle('cwtitle.pkl')
        corpus = self.comps['title']
        target =  self.comps['rev_pot']
        vec =  TfidfVectorizer(tokenizer = self.spacy_tokenizer, max_features = None, max_df = 1.0, ngram_range = (1,1))
        matrix = vec.fit_transform(corpus)

        ls = RidgeCV()
        print("fitting model")
        ls.fit(matrix, target)
        print("done")
        coefficients_df = pd.DataFrame.from_dict(dict(zip(vec.get_feature_names(), ls.coef_)), orient='index').sort_values(by=0)
        score = ls.score(matrix, target)
        print(f"R^2 = {score: .3f} \n Alpha: {ls.alpha_ : .3f}")
        most_common_words = np.array(vec.get_feature_names())[matrix.toarray().sum(axis=0).argsort()[::-1]]

        return coefficients_df


def main():
    # url = input("URL: ")
    url = "https://www.airbnb.com/rooms/13574493?location=Denver%2C%20CO%2C%20United%20States&s=EPFNH_so"
    prp = PropertyAnalyzer(url, verbose=True, num_comps=40)
    prp.do_NLP()
    to_markdown(prp.best_amenities())
    # prp.run_local_regression()


if __name__ == '__main__':
    main()
