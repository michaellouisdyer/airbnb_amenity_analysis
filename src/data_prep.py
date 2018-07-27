import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
import numpy as np
from utils import to_markdown
import matplotlib.pyplot as plt
from itertools import chain
pd.options.display.max_columns =  110
import ast

unique_amenities = {'smoke_detector', 'patio_or_balcony', 'elevator', 'paid_parking_on_premises', 'kitchen', 'hair-dryer', 'home_wide_doorway', 'ev_charger', 'extra_pillows_and_blankets', 'high_chair', 'wide_hallway_clearance', 'waterfront', 'cable', 'stove', 'grab_rails_in_toilet', 'accessible_height_bed', 'dishwasher', 'iron', 'wheelchair_accessible', 'bed_linens', 'babysitter_recommendations', 'wide_clearance_to_bed', 'first_aid_kit', 'doorman_entry', 'shower_chair', 'refrigerator', 'pool', 'bedroom_step_free_access', 'game_console', 'grab_rails_in_shower_and_toilet', 'baby_bath', 'host_checkin', 'pocket_wifi', 'baby_monitor', 'essentials', 'electric_profiling_bed', 'hot_water', 'doorman', 'long_term_stays_allowed', 'buzzer', 'carbon_monoxide_detector', 'wireless_internet', 'disabled_parking_spot', 'free_parking', 'ethernet_connection', 'oven', 'washer', 'internet', 'beachfront', 'table_corner_guards', 'cleaning_before_checkout', 'dryer', 'street_parking', 'dishes_and_silverware', 'microwave', 'wide_clearance_to_shower_and_toilet', 'keypad', 'cooking_basics', 'lockbox', 'private-living-room', 'event_friendly', 'has_pets', 'garden_or_backyard', 'lake_access', 'lock_on_bedroom_door', 'window_guards', 'crib', 'fireplace', 'family_friendly', 'breakfast', 'coffee_maker', 'pack_n_play_travel_crib', 'room_darkening_shades', 'changing_table', 'beach_essentials', 'tub_with_shower_bench', 'bbq_area', 'bathroom_step_free_access', 'safety_card', 'flat_smooth_pathway_to_front_door', 'bathtub', 'allows_smoking', 'handheld_shower_head', 'bedroom_wide_doorway', 'home_step_free_access', 'single_level_home', 'jacuzzi', 'heating', 'common_space_step_free_access', 'gym', 'stair_gates', 'outlet_covers', 'allows_pets', 'accessible_height_toilet', 'common_space_wide_doorway', '24hr-checkin', 'hangers', 'childrens_books_and_toys', 'private-entrance', 'fire_extinguisher', 'rollin_shower', 'grab_rails_in_shower', 'other_checkin', 'smartlock', 'fireplace_guards', 'bathroom_wide_doorway', 'paid_parking', 'shampoo', 'childrens_dinnerware', 'tv', 'ac', 'path_to_entrance_lit_at_night', 'laptop-friendly', 'luggage_dropoff_allowed'}


def VIFS(df):
    vif_df = pd.Series()
    df =  df.select_dtypes(include = [np.number])#.dropna()
    for i, col in enumerate(df.columns):
        if df[col].dtype in['float64', 'int64']:
            vif_df[col] = variance_inflation_factor(df.values, i)
    return vif_df

def get_unique_amenities(prop):

    # amen = chain.from_iterable(prop['amenities'].unique())
    # flatten = [amenity for sublst in prop['amenities'].unique() for amenity in sublst]
    unq = prop['amenities'].dropna().unique()
    flatten = [ast.literal_eval(ppty) for ppty in unq]
    flt = pd.Series(list(chain(*flatten)))
    return flt.unique()






# def main():
bookings = pd.read_csv('../data/denver_booking_data.csv')
prop = pd.read_csv('../data/denver_properties.csv')

prop['clean_rate'] =  prop['cleaning_fee'] / (prop['price_nightly']  +prop['cleaning_fee'])
plt.scatter(prop['accommodates'], prop['clean_rate'])
amenities =  get_unique_amenities(prop)
pd.to_pickle(amenities, 'amenities.pkl')
amenity_df  = prop[['c_revenue_native_ltm', 'bedrooms', 'bathrooms', 'accommodates', 'latitude', 'longitude', 'nieghborhood','guidebook', 'smoking', 'pets_allowed', 'tv', 'internet', 'cabletv', 'wireless', 'aircon', 'heating', 'elevator', 'pool', 'handicap_access', 'kitchen', 'doorman', 'free_parking', 'gym', 'hottub', 'indoor_fireplace', 'intercom', 'breakfast', 'suitable_for_events', 'family_friendly', 'washer', 'dryer']]

# import pdb; pdb.set_trace()
# plt.show()
# vif_df = VIFS(bookings)
# vif_df = VIFS(properties)
# import pdb; pdb.set_trace()
# main()
# import pdb; pdb.set_trace()
