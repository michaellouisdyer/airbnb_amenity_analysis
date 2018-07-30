import pandas as pd
import numpy as np
from data_prep import get_data
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from gmplot import gmplot

def get_query():
    ### TODO: clean inputs
    # latitude = float(input("Latitude: "))
    # longitude = float(input("Longitude: "))
    # accommodates = float(input("Accommodates: "))
    # bedrooms = float(input("Beds: "))
    # bathrooms = float(input("Baths: "))
    # amenity = input("Amenity: ")
    accommodates = 4.0
    longitude  = -104.897614
    latitude = 39.669066
    bedrooms = 2.0
    bathrooms = 1.0
    amenity = 'pool'
    return { 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'accommodates': accommodates, 'latitude': latitude, 'longitude': longitude,'amenity': amenity}


def cluster(query, amenity_df):
    amenity_x = query['amenity']
    scaler =  StandardScaler()

    query_df = pd.DataFrame.from_dict(query, orient = 'index').drop('amenity').T


    df  = amenity_df[['c_revenue_native_ltm', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', amenity_x]]
    w_amenity = df[df[amenity_x]].drop(columns = [amenity_x])
    w_out_amenity = df[~df[amenity_x]].drop(columns = [amenity_x])


    y_w = w_amenity.pop('c_revenue_native_ltm')
    w_amenity = w_amenity.append(query_df)
    X_w = scaler.fit_transform(w_amenity)
    w_predict =  X_w[-1].reshape(1, -1)
    X_w =  X_w[:-1, :]
    y_w_out = w_out_amenity.pop('c_revenue_native_ltm')
    w_out_amenity = w_out_amenity.append(query_df)
    X_w_out = scaler.fit_transform(w_out_amenity)

    w_out_predict =  X_w_out[-1].reshape(1, -1)
    X_w_out =  X_w_out[:-1, :]
    kn = KNeighborsRegressor(weights = 'distance', n_jobs =-1)
    kn_w = KNeighborsRegressor(weights = 'distance', n_jobs =-1)
    kn_w_out = KNeighborsRegressor(weights = 'distance', n_jobs =-1)
    kn_w.fit(X_w, y_w)
    kn_w_out.fit(X_w_out, y_w_out)
    w_distance, w_neighbors = kn_w.kneighbors(w_predict)
    w_neighbors_df = w_amenity.iloc[w_neighbors.flatten()]
    w_out_distance, w_out_neighbors = kn_w_out.kneighbors(w_out_predict)
    import pdb; pdb.set_trace()
    w_out_neighbors_df = w_out_amenity.iloc[w_out_neighbors.flatten()]



    w_revenue  = kn_w.predict(w_predict)[0]
    w_out_revenue = kn_w_out.predict(w_out_predict)[0]
    print(f'Average yearly revenue with {amenity_x}: $ {w_revenue:.0f} \n Without: $ {w_out_revenue:.0f} \n Yearly revenue potential :  $ {w_revenue -  w_out_revenue :.0f}')

    return w_out_neighbors_df, w_neighbors_df, query_df



def plot_neighbors(w_out_neighbors_df, w_neighbors_df, query_df):
    gmap = gmplot.GoogleMapPlotter.from_geocode("Denver")
    gmap.scatter(w_out_neighbors_df['latitude'], w_out_neighbors_df['longitude'], 'red', size=40, marker=True)
    gmap.scatter(w_neighbors_df['latitude'], w_neighbors_df['longitude'], 'blue', size=40, marker=True)
    gmap.marker(query_df['latitude'], query_df['longitude'], 'green', title="Query Location")
    gmap.draw("pool1.html")

amenity_df = get_data()
query = get_query()
w_out_neighbors_df, w_neighbors_df, query_df = cluster(query, amenity_df)
plot_neighbors(w_out_neighbors_df, w_neighbors_df, query_df)
