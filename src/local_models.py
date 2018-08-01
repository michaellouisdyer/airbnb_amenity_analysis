from utils import to_markdown
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNetCV, LinearRegression, LassoCV

from sklearn.preprocessing import StandardScaler

def run_local_regression(comps, my_property):
    not_included_in_property = my_property.loc[my_property == 0].index
    y = comps.pop('rev_pot')
    X = comps[not_included_in_property]
    # X = comps.drop(columns = [ 'latitude', 'longitude', 'accommodates', 'bedrooms', 'bathrooms', 'cover_img', 'airbnb_property_id', 'cover_img', 'distance_meters', 'listing_url', 'location', 'property_type', 'room_type', 'stats', 'title', 'amenities', 'extra_person_charge'])

    # scaler = StandardScaler()
    # X_scale =  scaler.fit_transform(X)
    X_train, X_test, y_train,y_test = train_test_split(X, y, test_size =  0.66, random_state = 5)
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




comps =pd.read_pickle('comps_df.pkl').dropna(axis = 1)
my_property =pd.read_pickle('my_propertydf.pkl')[comps.columns]
run_local_regression(comps, my_property)
import pdb; pdb.set_trace()
