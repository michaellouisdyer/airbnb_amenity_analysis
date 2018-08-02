from utils import to_markdown
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNetCV, LinearRegression, LassoCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor

def run_local_regression(comps, my_property):
    not_included_in_property = my_property.loc[my_property == 0].index
    y = comps.pop('rev_pot')
    # X = comps[not_included_in_property]
    # import pdb; pdb.set_trace()
    X = comps.drop(columns = [ 'latitude', 'longitude',  'cover_img', 'airbnb_property_id', 'cover_img', 'distance_meters', 'listing_url', 'location', 'property_type', 'room_type', 'stats', 'title', 'amenities','extra_person_charge'], errors = 'ignore')
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



    # rf = RandomForestRegressor(n_estimators = 100000, n_jobs = -1, max_depth = 1)
    # rf.fit(X_train, y_train)
    # train_score  = rf.score(X_train, y_train)
    # test_score  = rf.score(X_test, y_test)
    # coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, rf.feature_importances_)), orient='index').sort_values(by=0)
    #
    # to_markdown(coefficients_df)
    # print(f"Random forest R^2: train: {train_score: .3f}\n test: {test_score: .3f}")
    rf =  RandomForestRegressor(n_jobs=-1)

    param_grid = {'bootstrap': [True, False], 'max_depth': [1,2,3,4,5,6,7,8,9,10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None], 'max_features': ['auto', 'sqrt'], 'min_samples_leaf': [1, 2, 4], 'min_samples_split': [2, 5, 10], 'n_estimators': [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000,4000,20000]}

    # param_grid = {'bootstrap': [True, False], 'max_depth': [1,2, None], 'max_features': ['auto', 'sqrt'], 'min_samples_leaf': [4], 'min_samples_split': [2], 'n_estimators': [200, 400]}

    rf_random = RandomizedSearchCV(estimator = rf, param_distributions = param_grid, n_iter = 1000, cv = 3, verbose=2, random_state=42, n_jobs = -1)
    rf_random.fit(X_train, y_train)

 # rf = RandomForestRegressor(n_estimators = 100000, n_jobs = -1, max_depth = 1)
 #    rf.fit(X_train, y_train)
    # train_score  = rf.score(X_train, y_train)
    # test_score  = rf.score(X_test, y_test)
    # coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, rf.feature_importances_)), orient='index').sort_values(by=0)
    #
    # to_markdown(coefficients_df)
    # print(f"Random forest R^2: train: {train_score: .3f}\n test: {test_score: .3f}")

    # gb = GradientBoostingRegressor(n_estimators = 100000, max_depth = 1, learning_rate =0.0001, max_features = None, loss = 'huber')
    # gb.fit(X_train, y_train)
    # train_score  = gb.score(X_train, y_train)
    # test_score  = gb.score(X_test, y_test)
    # coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, gb.feature_importances_)), orient='index').sort_values(by=0)
    #
    # to_markdown(coefficients_df)
    # print(f"Gradient_boosting R^2: train: {train_score: .3f}\n test: {test_score: .3f}")
    # import pdb; pdb.set_trace()

def cluster(my_property, comps, amenity_x, k =  5, verbose = False, distance_weight = 1):
    # amenity_x = query['amenity']
    scaler =  StandardScaler()

    # query_df = pd.DataFrame.from_dict(query, orient = 'index').drop('amenity').T

    query_df  = my_property[[ 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude']]
    df  = comps[['rev_pot', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', amenity_x]]
    w_amenity = df[df[amenity_x].astype('bool')].drop(columns = [amenity_x])
    w_out_amenity = df[~df[amenity_x].astype('bool')].drop(columns = [amenity_x])


    y_w = w_amenity.pop('rev_pot')
    w_amenity = w_amenity.append(query_df)
    X_w = scaler.fit_transform(w_amenity)
    X_w[:, 3:] = X_w[:, 3:]*distance_weight
    w_predict =  X_w[-1].reshape(1, -1)
    X_w =  X_w[:-1, :]
    y_w_out = w_out_amenity.pop('rev_pot')
    w_out_amenity = w_out_amenity.append(query_df)
    X_w_out = scaler.fit_transform(w_out_amenity)

    X_w_out[:, 3:] = X_w_out[:, 3:]*distance_weight
    w_out_predict =  X_w_out[-1].reshape(1, -1)
    X_w_out =  X_w_out[:-1, :]

    if (X_w_out.shape[0] < k) or (X_w.shape[0] < k) :
        return 0, 0, 0, 0
    kn_w = KNeighborsRegressor(n_neighbors = k, weights = 'distance', n_jobs =-1)
    kn_w_out = KNeighborsRegressor(n_neighbors = k, weights = 'distance', n_jobs =-1)
    kn_w.fit(X_w, y_w)
    kn_w_out.fit(X_w_out, y_w_out)
    w_distance, w_neighbors = kn_w.kneighbors(w_predict)
    w_neighbors_df = w_amenity.iloc[w_neighbors.flatten()]
    w_out_distance, w_out_neighbors = kn_w_out.kneighbors(w_out_predict)
    w_out_neighbors_df = w_out_amenity.iloc[w_out_neighbors.flatten()]

    w_revenue  = kn_w.predict(w_predict)[0]
    w_out_revenue = kn_w_out.predict(w_out_predict)[0]
    rev_pot = w_revenue -  w_out_revenue
    if verbose:
        print(f'Average yearly revenue with {amenity_x}: $ {w_revenue:.0f} \n Without: $ {w_out_revenue:.0f} \n Yearly revenue potential :  $ { rev_pot:.0f}')
    return w_out_neighbors_df, w_neighbors_df, query_df, rev_pot

def best_amenities(amenities, my_property, comps):
    revenue_potentials = pd.DataFrame(columns =['revenue_potential'])
    for amenity in amenities:
        # query['amenity'] =  amenity
        w_out_neighbors_df, w_neighbors_df, query_df, rev_pot = cluster(my_property, comps, amenity, k = 10, verbose =  True)
        revenue_potentials.loc[amenity] = rev_pot
    # if unique:
    #     return revenue_potentials.sort_values(by = 'revenue_potential').drop(amenities)
    return revenue_potentials.sort_values(by = 'revenue_potential')

import os
id = '13574493'
# id = '15398636'
token = os.environ['AIRDNA_API_TOKEN']
from get_data_from_api import ReadAPI
ReadAPI = ReadAPI(token)
comps, my_property, amenities =  ReadAPI.get_comps_from_id(id)
amenities =  amenities.to_frame().reset_index()[0]
comps = comps.dropna(axis = 1)
my_property =  my_property[comps.columns]

def read_from_pickle():

    comps = pd.read_pickle('comp80.pkl')
    my_property = pd.read_pickle('my_prop.pkl')
    amenities =  pd.read_pickle('amenities80df.pkl')
    return comps, my_property, amenities

rev_df =  best_amenities(amenities, my_property, comps)
to_markdown(rev_df)
import pdb; pdb.set_trace()
