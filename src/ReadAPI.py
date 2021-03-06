import os
import time

import numpy as np
import pandas as pd
import requests


class ReadAPI(object):
    """Read from the AirDNA API"""

    def __init__(self, token, verbose=False, num_comps=20):
        self.token = token
        self.verbose = verbose
        self.num_comps = num_comps

    def get_single_property(self, property_id):
        """Returns property details from one property from market minder"""
        time.sleep(0.2) # timer to avoid overloading servers
        r = requests.get('https://api.airdna.co/client/v1/market/property?access_token={}&property_id={}&show_amenities=True&show_images=False&show_location=True&currency=usd'.format(self.token, property_id))

        if r.status_code != 200:
            if self.verbose:
                print(f'HTTP code: {r.status_code}')
            time.sleep(5)
        return pd.Series(r.json()['property_details'])

    def get_comps(self, info):
        """Returns a dataframe of comparable properties"""

        comp_df = pd.DataFrame()
        lat, long, beds, bath, acc = info

        # API only returns 10 properties at once, so this 'walks' around the area to get more
        i = 0
        num_rows = 0
        new_lat = lat
        new_long = long
        step = 0.000
        weights = np.array([[1, 1], [-1, -1], [1, -1], [-1, 1]])
        while num_rows < self.num_comps:
            i += 1
            r = requests.get("https://api.airdna.co//client/v1/rentalizer/estimate?access_token={}&lat={}&lng={}&bedrooms={}&bathrooms={}&accommodates={}&show_amenities=True".format(
                self.token, new_lat, new_long, beds, bath, acc)) # returns list of comps from rentalizer
            time.sleep(0.1)

            if r.status_code != 200:
                print(f'HTTP code: {r.status_code}')
                time.sleep(5)

            comp_df = comp_df.append(pd.DataFrame.from_dict(r.json()['comps']))
            comp_df.drop_duplicates('airbnb_property_id', inplace=True)
            new_lat = lat+step * weights[i % 4, 0]
            new_long = long+step * weights[i % 4, 1]
            num_rows = comp_df.shape[0]

            if self.verbose:
                print(f'HTTP code: {r.status_code}, request #: {i}, # comps: {num_rows}')
            if i % 4 == 0:
                step += 0.07
            if i > 50: #avoids overloading the servers
                continue

        comp_df[['latitude', 'longitude']] = comp_df['location'].apply(pd.Series)
        comp_df['rev_pot'] = comp_df['stats'].apply(
            pd.Series)['revenue_potential'].apply(pd.Series)['ltm']
        return comp_df

    def get_comps_from_id(self, property_id):
        """Uses airbnb id to get information about the property in order to find comps"""

        prop = self.get_single_property(property_id).to_frame().T
        info = prop[['latitude', 'longitude', 'bedrooms', 'bathrooms', 'accommodates']]
        info = tuple(*[*info.values])
        comp_df = self.get_comps(info)
        comp_df = self.get_extra_info(comp_df)
        comp_df = comp_df.append(prop, ignore_index=True)
        comp_df2, amenities = self.create_amenity_matrix(comp_df)
        id_int = int(property_id)
        return comp_df2.query('airbnb_property_id != @id_int'), comp_df2.query('airbnb_property_id == @id_int').iloc[-1], amenities

    def extra_single_property(self, property_id):
        """A function to return columns for a single property"""
        prop = self.get_single_property(property_id)
        return prop[['amenities', 'title']]

    def get_extra_info(self, comp_df):
        """Adds extra information for the comps"""
        comp_df[['amenities', 'title']] = comp_df['airbnb_property_id'].apply(
            self.extra_single_property)
        return comp_df

    def create_amenity_matrix(self, comp_df):
        """Convert list to binary matrix"""
        amenities = []
        for i, x in comp_df.iterrows():
            amenities.append(pd.get_dummies(comp_df['amenities'][i]).sum())
        amenity_matrix = pd.concat(amenities, axis=1).T.fillna(0)
        return comp_df.join(amenity_matrix), amenity_matrix.columns
