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

class PropertyAnalyzer(object):
    def __init__(self, url, k_neighbors = 6, verbose = False, distance_weight = 1, num_comps = 20):
        self.url = url
        self.property_id =  url[url.rfind('/')+1: url.rfind('?')]
        self.token = os.environ['AIRDNA_API_TOKEN']
        self.amenities =  pd.DataFrame()
        self.comps =  pd.DataFrame()
        self.my_property =  pd.DataFrame()
        self.k = k_neighbors
        self.verbose = verbose
        self.distance_weight = distance_weight
        self.ReadAPI = ReadAPI(self.token, verbose = self.verbose, num_comps = num_comps)
        self.get_comps()

    def get_comps(self):
        comps, my_property, amenities =  self.ReadAPI.get_comps_from_id(self.property_id)
        self.amenities =  amenities.to_frame().reset_index()[0]
        self.comps = comps.dropna(axis = 1)
        self.my_property =  my_property[comps.columns]

    def cluster(self, amenity_x, scaling = True):
        scaler =  StandardScaler()

        query_df  = self.my_property[[ 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude']]
        df  = self.comps[['rev_pot', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', amenity_x]]
        w_amenity = df[df[amenity_x].astype('bool')].drop(columns = [amenity_x])
        w_out_amenity = df[~df[amenity_x].astype('bool')].drop(columns = [amenity_x])


        y_w = w_amenity.pop('rev_pot')
        w_amenity = w_amenity.append(query_df)
        y_w_out = w_out_amenity.pop('rev_pot')
        w_out_amenity = w_out_amenity.append(query_df)

        if scaling:
            X_w = scaler.fit_transform(w_amenity)
            X_w_out = scaler.fit_transform(w_out_amenity)
        else:
            X_w = np.array(w_amenity)
            X_w_out = np.array(w_out_amenity)
        X_w[:, 3:] = X_w[:, 3:]*self.distance_weight
        w_predict =  X_w[-1].reshape(1, -1)
        X_w =  X_w[:-1, :]


        X_w_out[:, 3:] = X_w_out[:, 3:]*self.distance_weight
        w_out_predict =  X_w_out[-1].reshape(1, -1)
        X_w_out =  X_w_out[:-1, :]

        if (X_w_out.shape[0] < self.k) or (X_w.shape[0] < self.k) :
            return 0
        kn_w = KNeighborsRegressor(n_neighbors = self.k, weights = 'distance', n_jobs =-1)
        kn_w_out = KNeighborsRegressor(n_neighbors = self.k, weights = 'distance', n_jobs =-1)
        kn_w.fit(X_w, y_w)
        kn_w_out.fit(X_w_out, y_w_out)
        w_distance, w_neighbors = kn_w.kneighbors(w_predict)
        w_neighbors_df = w_amenity.iloc[w_neighbors.flatten()]
        w_out_distance, w_out_neighbors = kn_w_out.kneighbors(w_out_predict)
        w_out_neighbors_df = w_out_amenity.iloc[w_out_neighbors.flatten()]

        w_revenue  = kn_w.predict(w_predict)[0]
        w_out_revenue = kn_w_out.predict(w_out_predict)[0]
        rev_pot = w_revenue -  w_out_revenue
        if self.verbose:
            print(f'Average yearly revenue with {amenity_x}: $ {w_revenue:.0f} \n Without: $ {w_out_revenue:.0f} \n Yearly revenue potential :  $ { rev_pot:.0f}')
        return rev_pot

    def best_amenities(self):
        # self.get_comps()
        revenue_potentials = pd.DataFrame(columns =['revenue_potential'])
        for amenity in self.amenities:
            rev_pot = self.cluster(amenity)
            revenue_potentials.loc[amenity] = rev_pot
        return revenue_potentials.sort_values(by = 'revenue_potential', ascending = False)

    def run_local_regression(self):
        # self.get_comps()
        not_included_in_property = self.my_property.loc[self.my_property == 0].index
        y = self.comps.pop('rev_pot')
        # X = self.comps[not_included_in_property]
        # import pdb; pdb.set_trace()
        X = self.comps.drop(columns = [ 'latitude', 'longitude',  'cover_img', 'airbnb_property_id', 'cover_img', 'distance_meters', 'listing_url', 'location', 'property_type', 'room_type', 'stats', 'title', 'amenities','extra_person_charge'], errors = 'ignore')
        X['constant'] = 1


        scaler = StandardScaler()
        X_scale =  scaler.fit_transform(X)
        X_train, X_test, y_train,y_test = train_test_split(X_scale, y, test_size =  0.1, random_state = 5)
        en = ElasticNetCV(l1_ratio = [.1, .5, .7, .9, .95, .99, 1], eps=1e-3, n_jobs = -1)
        en.fit(X_train, y_train)
        train_score  = en.score(X_train, y_train)
        test_score  = en.score(X_test, y_test)
        print(f"ElasticNet R^2:\n Train {train_score: .3f} \n Test {test_score:.3f} \n Alpha: {en.alpha_ : .3f} \n l1_ratio: {en.l1_ratio_}")
        coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, en.coef_)), orient='index').sort_values(by=0)

        to_markdown(coefficients_df)

        lm = LinearRegression()
        lm.fit(X_train, y_train)
        train_score  = lm.score(X_train, y_train)
        test_score  = lm.score(X_test, y_test)
        coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, lm.coef_)), orient='index').sort_values(by=0)

        print(f"Standard Linear R^2: train: {train_score: .3f}\n test: {test_score: .3f}")
        to_markdown(coefficients_df)

def main():
    # url = input("URL: ")
    url = "https://www.airbnb.com/rooms/13574493?location=Denver%2C%20CO%2C%20United%20States&s=EPFNH_so"
    prp = PropertyAnalyzer(url, verbose = True, num_comps = 40)
    to_markdown(prp.best_amenities())
    prp.run_local_regression()

if __name__ == '__main__':
    main()
