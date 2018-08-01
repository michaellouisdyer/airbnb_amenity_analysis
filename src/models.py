# regression
from utils import to_markdown
import pandas as pd
import numpy as np
from data_prep import get_data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNetCV, LinearRegression, LassoCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def run_regressions(df):
    # amenity_df = amenity_df.query('neighborhood == "cherry_creek"')
    # y = amenity_df.pop('c_revenue_native_ltm')
    y = amenity_df.pop('c_revenue_potential_ltm')
    # X = amenity_df.drop(columns = ['neighborhood', 'latitude', 'longitude','bedrooms'])
    X = amenity_df.drop(columns = ['neighborhood', 'latitude', 'longitude', 'accommodates', 'bedrooms', 'bathrooms'])
    X['constant'] = 1

    scaler = StandardScaler()
    X_scale =  scaler.fit_transform(X)
    X_train, X_test, y_train,y_test = train_test_split(X_scale, y, test_size =  0.25, random_state = 5)
    en = ElasticNetCV(l1_ratio = [.1, .5, .7, .9, .95, .99, 1], eps=1e-3, n_jobs = -1)
    en.fit(X_train, y_train)
    score  = en.score(X_test, y_test)
    print(f"ElasticNet R^2: {score: .3f} \n Alpha: {en.alpha_ : .3f} \n l1_ratio: {en.l1_ratio_}")
    coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, en.coef_)), orient='index').sort_values(by=0)

    to_markdown(coefficients_df)

    lm = LinearRegression()
    lm.fit(X_train, y_train)
    score  = lm.score(X_test, y_test)
    coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, lm.coef_)), orient='index').sort_values(by=0)

    print(score.round(4))
    print(f"Standard Linear R^2: {score: .3f}")
    to_markdown(coefficients_df)

# amenity_df = get_data(extra_column = 'rating_overall')
prop = pd.read_csv('../data/denver_properties.csv')
prop['neighborhood'] = prop['neighborhood'].str.replace(' ','_').str.lower()
# amenity_df  = prop[['c_revenue_native_ltm', 'neighborhood','bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', 'smoking', 'pets_allowed', 'tv', 'internet', 'cabletv', 'wireless', 'aircon', 'heating', 'elevator', 'pool', 'handicap_access', 'kitchen', 'doorman', 'free_parking', 'gym', 'hottub', 'indoor_fireplace', 'intercom', 'breakfast', 'suitable_for_events', 'family_friendly', 'washer',  'views_week', 'img_count', 'reviews_count', 'instant_book', 'response_rate', 'minimum_stay', 'cleaning_fee', 'price_weekly', 'price_monthly', 'price_nightly', 'rating_overall', 'rating_communication', 'rating_accuracy', 'rating_cleanliness', 'rating_checkin', 'rating_location','rating_value','response_time', 'weekly_discount', 'monthly_discount', 'business_ready']]
amenity_df  = prop[['c_revenue_native_ltm','neighborhood', 'accommodates', 'longitude', 'latitude', 'bedrooms', 'bathrooms',  'smoking', 'pets_allowed', 'tv', 'internet', 'cabletv', 'wireless', 'aircon', 'heating', 'elevator', 'pool', 'handicap_access', 'kitchen', 'doorman', 'free_parking', 'gym', 'hottub', 'indoor_fireplace', 'intercom', 'breakfast', 'suitable_for_events', 'family_friendly', 'washer',  'views_week', 'img_count', 'reviews_count', 'instant_book', 'response_rate', 'minimum_stay', 'cleaning_fee',  'price_nightly', 'rating_overall','response_time', 'weekly_discount',  'business_ready']]
amenity_df = amenity_df.fillna(amenity_df.mean())
# from data_prep import VIFS
# to_markdown(VIFS(amenity_df))
run_regressions(amenity_df)
