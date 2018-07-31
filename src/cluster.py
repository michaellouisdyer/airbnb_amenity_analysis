import pandas as pd
import numpy as np
from data_prep import get_data
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from gmplot import gmplot
from utils import to_markdown

def get_query(best =  False, id = False):
    ### TODO: clean inputs
    unique_amenities =  list(pd.read_pickle('common_amenities.pkl')[0])

    # longitude  = -104.996133
    # latitude = 39.716561
    # bedrooms = 1.0
    # bathrooms = 1.0
    # accommodates = 2.0
    # amenity = 'pool'
    property_amenities = []

    if id:
        amenity_df = get_data(id = True)
        id_property = amenity_df.query('airbnb_property_id == @id')
        property_amenities = [x for x in id_property.columns[(id_property == True).all()]]
        property_amenities.remove('bedrooms')
        property_amenities.remove('bathrooms')

        try:
            longitude = id_property['longitude'].iloc[0]
            latitude = id_property['latitude'].iloc[0]
            bedrooms = id_property['bedrooms'].iloc[0]
            bathrooms = id_property['bathrooms'].iloc[0]
            accommodates = id_property['accommodates'].iloc[0]
        except IndexError:
            print(f'ID # {id} not found')
            quit()
    else:
        latitude = float(input("Latitude: "))
        longitude = float(input("Longitude: "))
        accommodates = float(input("Accommodates: "))
        bedrooms = float(input("Beds: "))
        bathrooms = float(input("Baths: "))

    if best:
        return { 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'accommodates': accommodates, 'latitude': latitude, 'longitude': longitude}, property_amenities

    else:
        print("Available amenities", unique_amenities)
        amenity = input("Amenity: ").strip().lower()
        return { 'bedrooms': bedrooms, 'bathrooms': bathrooms, 'accommodates': accommodates, 'latitude': latitude, 'longitude': longitude,'amenity': amenity}

def cluster(query, amenity_df, k =  5, verbose = False, distance_weight = 1):
    amenity_x = query['amenity']
    scaler =  StandardScaler()

    query_df = pd.DataFrame.from_dict(query, orient = 'index').drop('amenity').T

    df  = amenity_df[['c_revenue_native_ltm', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', amenity_x]]
    w_amenity = df[df[amenity_x]].drop(columns = [amenity_x])
    w_out_amenity = df[~df[amenity_x]].drop(columns = [amenity_x])


    y_w = w_amenity.pop('c_revenue_native_ltm')
    w_amenity = w_amenity.append(query_df)
    X_w = scaler.fit_transform(w_amenity)
    X_w[:, 3:] = X_w[:, 3:]*distance_weight
    w_predict =  X_w[-1].reshape(1, -1)
    X_w =  X_w[:-1, :]
    y_w_out = w_out_amenity.pop('c_revenue_native_ltm')
    w_out_amenity = w_out_amenity.append(query_df)
    X_w_out = scaler.fit_transform(w_out_amenity)

    X_w_out[:, 3:] = X_w_out[:, 3:]*distance_weight
    w_out_predict =  X_w_out[-1].reshape(1, -1)
    X_w_out =  X_w_out[:-1, :]

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


def plot_neighbors(w_out_neighbors_df, w_neighbors_df, query_df, name):
    gmap = gmplot.GoogleMapPlotter(query_df['latitude'], query_df['longitude'], 13)
    gmap.scatter(w_out_neighbors_df['latitude'], w_out_neighbors_df['longitude'], 'red', size=40, marker=True, title = 'No' + name)
    gmap.scatter(w_neighbors_df['latitude'], w_neighbors_df['longitude'], 'blue', size=40, marker=True, title ='With' + name)
    gmap.marker(query_df['latitude'], query_df['longitude'], 'green', title="Query Location")
    filename = name + '.html'
    gmap.draw(filename)
    print("You can view a map of nearby properties by opening " + filename)

def best_amenities(id = None, unique = False):
    amenity_df = get_data()
    query, property_amenities = get_query(best = True, id = id)
    unique_amenities =  list(pd.read_pickle('common_amenities.pkl')[0])
    revenue_potentials = pd.DataFrame(columns =['revenue_potential'])
    for amenity in unique_amenities:
        query['amenity'] =  amenity
        w_out_neighbors_df, w_neighbors_df, query_df, rev_pot = cluster(query, amenity_df, k=20)
        revenue_potentials.loc[amenity] = rev_pot
    if unique:
        return revenue_potentials.sort_values(by = 'revenue_potential').drop(property_amenities)
    return revenue_potentials.sort_values(by = 'revenue_potential')

def one_amenity(id = False):
    amenity_df = get_data()
    query = get_query(id = id)
    amenity_x = query['amenity']
    w_out_neighbors_df, w_neighbors_df, query_df, rev_pot = cluster(query, amenity_df, k=10, verbose = True)
    plot_neighbors(w_out_neighbors_df, w_neighbors_df, query_df, amenity_x)


# rev_potentials = best_amenities(id = '6333040', unique = False)
# to_markdown(rev_potentials)

def test_weights():
    amenity_df = get_data()
    query = get_query()
    amenity_x = query['amenity']
    for weight in [1,1.5,2]:
        w_out_neighbors_df, w_neighbors_df, query_df, rev_pot = cluster(query, amenity_df, k=10, distance_weight = weight)
        plot_name = amenity_x + f"distance: {weight}"
        plot_neighbors(w_out_neighbors_df, w_neighbors_df, query_df, plot_name)


def main():
    id = False
    program = int(input('Select Program: \n 1. Find best amenities \n 2. Select amenity \n'))
    input_method = int(input('Input information mode: \n 1. Airbnb property ID \n 2. Manual entry\n'))
    if input_method == 1:
        id = input("ID: ").strip()
    if program == 1:
        rev_potentials = best_amenities(id = id, unique = False)
        to_markdown(rev_potentials)

    if program ==2:
            one_amenity(id = id)
    if input_method == 2:
        if program ==1:
            pass
        if program ==2:
            pass
if __name__ == main():
    main()
