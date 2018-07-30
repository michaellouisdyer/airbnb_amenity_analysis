# regression
from utils import to_markdown
import pandas as pd
import numpy as np
from data_prep import get_data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNetCV, LinearRegression, LassoCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

amenity_df = get_data()
# amenity_df = amenity_df.query('neighborhood == "cherry_creek"')
y = amenity_df.pop('c_revenue_native_ltm')
# X = amenity_df.drop(columns = ['neighborhood', 'latitude', 'longitude','bedrooms'])
X = amenity_df.drop(columns = ['neighborhood', 'latitude', 'longitude', 'accommodates', 'bedrooms', 'bathrooms'])
X['constant'] = 1

scaler = StandardScaler()
X_scale =  scaler.fit_transform(X)
X_train, X_test, y_train,y_test = train_test_split(X_scale, y, test_size =  0.25, random_state = 5)
en = ElasticNetCV(l1_ratio = [.1, .5, .7, .9, .95, .99, 1], eps=1e-3, n_jobs = -1)
en.fit(X_train, y_train)
score  = en.score(X_test, y_test)
coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, en.coef_)), orient='index').sort_values(by=0)

print(score.round(4))
print( to_markdown(coefficients_df) )

lm = LinearRegression()
lm.fit(X_train, y_train)
score  = lm.score(X_test, y_test)
coefficients_df = pd.DataFrame.from_dict(dict(zip(X.columns, lm.coef_)), orient='index').sort_values(by=0)

print(score.round(4))
print( to_markdown(coefficients_df) )
import pdb; pdb.set_trace()
