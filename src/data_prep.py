import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
import numpy as np
from utils import to_markdown, impute_df, create_test_df, determine_impute
import matplotlib.pyplot as plt
from itertools import chain
pd.options.display.max_columns =  110
import ast



def VIFS(df):
    # vif_df = pd.DataFrame(orient = 'index')
    vif_dict = {}
    df =  df.select_dtypes(include = [np.number, 'bool'])#.dropna()
    for i, col in enumerate(df.columns):
        if df[col].dtype in['float64', 'int64', 'bool']:
            vif_dict[col] = variance_inflation_factor(df.values.astype('int64'), i)
            # print(col)
    return pd.DataFrame.from_dict(vif_dict, orient='index').sort_values(by=0)

def get_unique_amenities(prop):

    unq = prop['amenities'].dropna().unique()
    flatten = [ast.literal_eval(ppty) for ppty in unq]
    flt = pd.Series(list(chain(*flatten)))
    return flt.unique()

# def main():
def get_data(extra_column =  False):
    bookings = pd.read_csv('../data/denver_booking_data.csv')
    prop = pd.read_csv('../data/denver_properties.csv')

    # prop['clean_rate'] =  prop['cleaning_fee'] / (prop['price_nightly']  +prop['cleaning_fee'])
    # plt.scatter(prop['accommodates'], prop['clean_rate'])
    # amenities =  get_unique_amenities(prop)
    # pd.to_pickle(amenities, 'amenities.pkl')
    prop['neighborhood'] = prop['neighborhood'].str.replace(' ','_').str.lower()
    if extra_column:
        w_id = prop[[extra_column, 'c_revenue_potential_ltm', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', 'neighborhood', 'smoking', 'pets_allowed', 'tv', 'internet', 'cabletv', 'wireless', 'aircon', 'heating', 'elevator', 'pool', 'handicap_access', 'kitchen', 'doorman', 'free_parking', 'gym', 'hottub', 'indoor_fireplace', 'intercom', 'breakfast', 'suitable_for_events', 'family_friendly', 'washer']]
        return w_id.fillna(w_id.mean())


    amenity_df  = prop[['c_revenue_potential_ltm', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', 'neighborhood', 'smoking', 'pets_allowed', 'tv', 'internet', 'cabletv', 'wireless', 'aircon', 'heating', 'elevator', 'pool', 'handicap_access', 'kitchen', 'doorman', 'free_parking', 'gym', 'hottub', 'indoor_fireplace', 'intercom', 'breakfast', 'suitable_for_events', 'family_friendly', 'washer']]
    amenity_df = amenity_df.fillna(amenity_df.mean())
    return amenity_df

def imputation_method():
    amenity_df = get_data()
    y = amenity_df.pop('c_revenue_native_ltm')
    X = amenity_df.drop(columns = ['neighborhood'])

    impute_df = pd.DataFrame.from_dict(determine_impute(X), orient = 'index')
    return impute_df
# import pdb; pdb.set_trace()
# plt.show()
# vif_df = VIFS(bookings)
# amenity_df = get_data()
# vif_df = VIFS(amenity_df)
# to_markdown(vif_df)
# import pdb; pdb.set_trace()
# main()
# import pdb; pdb.set_trace()
