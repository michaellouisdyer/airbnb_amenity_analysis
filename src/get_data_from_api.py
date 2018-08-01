import requests
import os
import numpy as np
import pandas as pd
import time
class ReadAPI(object):
    def __init__(self, token):
        self.token = token

    def get_single_property(self, property_id):
        time.sleep(0.3)
        r = requests.get('https://api.airdna.co/client/v1/market/property?access_token={}&property_id={}&show_amenities=True&show_images=False&show_location=True&currency=usd'.format(self.token, property_id))
        # print(r.status_code)
        if r.status_code != 200:
            time.sleep(5)
        return pd.Series(r.json()['property_details'])

    def get_comps(self, info, num_comps = 40):
        comp_df = pd.DataFrame()
        lat, long, beds, bath, acc = info
        i = 0
        num_rows = 0
        new_lat = lat
        new_long = long
        step = 0.000
        weights = np.array([[1,1], [-1,-1], [1,-1], [-1,1]])
        while num_rows < num_comps:
            i+=1
            print(i)
            r= requests.get("https://api.airdna.co//client/v1/rentalizer/estimate?access_token={}&lat={}&lng={}&bedrooms={}&bathrooms={}&accommodates={}&show_amenities=True".format(self.token, new_lat, new_long, beds, bath, acc))
            print(r.status_code)
            print(r)
            time.sleep(0.3)
            if r.status_code != 200:
                time.sleep(5)
            comp_df = comp_df.append(pd.DataFrame.from_dict(r.json()['comps']))
            comp_df.drop_duplicates('airbnb_property_id', inplace = True)
            new_lat = lat+step *weights[i%4,0]
            new_long = long+step *weights[i%4,1]
            num_rows = comp_df.shape[0]
            print(f'rows =  {num_rows}')
            if i%4 == 0:
                step += 0.015
            if i > 20:
                break

        comp_df[['latitude', 'longitude']] = comp_df['location'].apply(pd.Series)
        comp_df['rev_pot'] = comp_df['stats'].apply(pd.Series)['revenue_potential'].apply(pd.Series)['ltm']
        return comp_df

    def get_comps_from_id(self, property_id):
        prop = self.get_single_property(property_id).to_frame().T
        info = prop[['latitude', 'longitude', 'bedrooms', 'bathrooms', 'accommodates']]
        info = tuple(*[*info.values])
        comp_df = self.get_comps(info)
        comp_df = self.get_amenities(comp_df)
        comp_df =  comp_df.append(prop, ignore_index=True)
        comp_df2 = self.create_amenity_matrix(comp_df)
        id_int = int(property_id)
        return comp_df2.query('airbnb_property_id != @id_int'), comp_df2.query('airbnb_property_id == @id_int').iloc[-1]

    def amenity_single_property(self, property_id):
        prop = self.get_single_property(property_id)
        return prop['amenities']


    def get_amenities(self, comp_df):
        comp_df['amenities'] = comp_df['airbnb_property_id'].apply(self.amenity_single_property)
        return comp_df

    def create_amenity_matrix(self, comp_df):
        amenities = []
        for i, x in comp_df.iterrows():
            amenities.append(pd.get_dummies(comp_df['amenities'][i]).sum())
        amenity_matrix = pd.concat(amenities, axis = 1).T.fillna(0)
        import pdb; pdb.set_trace()
        return comp_df.join(amenity_matrix)


# r.headers
# r.json()['property_details']['amenities']
# info = ( 39.716561,-104.996133, 2, 2, 4)

id = '6333040'
token = os.environ['AIRDNA_API_TOKEN']
ReadAPI = ReadAPI(token)
comps, my_property =  ReadAPI.get_comps_from_id(id)
import pdb; pdb.set_trace()
