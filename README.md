## Should I Buy a Hot Tub?
#### An personalized neighborhood analysis for Airbnb owners, based on data from AirDNA

### Exploring the data
The purpose of this project is to provide Airbnb owners with personalized recommendations for which amenities (from the Airbnb amenities list) can provide the most additional revenue for them. AirDNA analyzes many other valuable factors, but I wanted to see what impact amenities had revenue. My revenue measure was projected lifetime revenue, which is the total revenue that AirDNA predicts a property would have made since 2017 if it had been completely available (not blocked off by the owner) the whole time, accounting for booking rates and nightly rates.

I first started by exploring the data for interactions between features, and I found that washers and dryers were highly correlated with each other (makes sense).

I then looked at the distribution of various amenities for all of Denver:
<img src = "img/amenity_comparison.png" width =1200>

 I then ran an elastic net regression on all of the properties in Denver to see if there were any overall trends.

ElasticNet (l1_ratio = 1, alpha = 129.33)
R**2 = 0.1331

|  Amenity            |Coefficient|
|:--------------------|----------:|
| pool                | -2936.92  |
| pets_allowed        | -1096.61  |
| breakfast           | -1011.22  |
| doorman             |  -618.584 |
| smoking             |  -314.398 |
| gym                 |     0     |
| handicap_access     |     0     |
| elevator            |     0     |
| constant            |     0     |
| heating             |   172.856 |
| intercom            |   190.666 |
| free_parking        |   423.045 |
| wireless            |   432.563 |
| washer              |   460.173 |
| kitchen             |   652.922 |
| suitable_for_events |   695.309 |
| tv                  |   878.608 |
| indoor_fireplace    |  1035.44  |
| hottub              |  1336.98  |
| aircon              |  1422.26  |
| internet            |  2169.43  |
| cabletv             |  3624.64  |
| family_friendly     |  3691.5   |

I found that some being family friendly, as well as having cable were slightly correlated with higher revenue potential. Pools, pets, and breakfast were correlated with less. This does not indicate that the amenity causes a change in potential, only that higher revenue properties are more likely to have these things. Similarly, adding a pool would not decrease the value of a home; however, lower revenue homes were more likely to have a pool. This model, because it does not include important factors such as the number of beds and the location, has very little predictive power with an R**2 of 0.13.



There are a number of factors that affect these outcomes, as it is likely that properties that have certain amenities have different revenue potential because of underlying differences. In order to address this, I made a script to give personalized recommendations based on similar properties to a particular Airbnb.

### Revenue Prediction:
To determine the most important features for an area, I created a program that takes the URL of an Airbnb property, uses an algorithm to find comparable properties, and then uses KNeighbors Regression to predict revenue with and without a particular amenity based on information about those properties. The with-amenity prediction minus the without-amenity prediction is the revenue potential. I evaluated this for the most common amenities and put them in order of most potential.

#### Example map for properties with and without breakfast in Denver
<img src = "img/breakfast_map.png", width = 900>




#### Making the app
To make the app, I first used the AirDNA API to access property information based on URL and return a list of comparable properties. Since the API only returns ten comps at a time, I created a function to 'walk' around the area and return more comps in a wider radius. I then ran another call to the API to get detailed amenity information for each of the comps. I then parsed the json and created a binary matrix of the features.  
Then, for each amenity in the amenity matrix, I split the comps into two groups: one that has that amenity, and another that doesn't, and use KNeighbors regression to predict the revenue for each of those groups. The difference between the groups is the revenue potential for a particular amenity. I created a lightweight dashboard with Dash and Flask to display this information.

#### Doing some NLP
I also decided to explore the language of the Airbnb listings, using LASSO regression and NLP to predict potential revenue of a property based on a TF-IDF matrix of various listing text fields.
Words with higher coefficients indicate that they are more commonly associated with rentals that have a higher value and vice versa for lower values. The app generates a list of the most important words in the area based on the title.

 These models have low predictive value as they are meant to identify hidden trends.



I also decided to explore the language of the Airbnb listings, using LASSO regression and NLP to predict potential revenue of a property based on a TF-IDF matrix of various listing text fields. These models have low predictive value as they are meant to identify hidden trends.

Description  
LASSO R^2 =  0.155  
Alpha:  7.002  

| Word     | Coefficient     |
| :------------- | :------------- |
|coors|      11170 |
|fully|      11273 |
|downtown|   12282 |
|home|       12412 |
|5|          12510 |
|3|          13055 |
|large|      13196 |
|modern|     19092 |
|high|       19632 |
|family|     21560 |
|spacious|   22518 |


Title  
LASSO R^2 =  0.154  
Alpha:  10.519  

| Word    | Coefficient     |
| :------------- | :------------- |
|historic   |10650|
|modern     |10792|
|3          |11809|
|loft       |11961|
|large      |12391|
|oasis      |12591|
|remodel    |13360|
|deck       |15890|
|rooftop    |16228|
|luxury     |20769|
|sleep      |44856|



#### Future Work:
I'd like to verify the results of the amenity comparison to make sure that the distances are being calculated correctly. Many real estate companies, instead of calculating vector similarities, calculate similarities for each feature iteratively and then average the results.

Working with linear regression on a property by property bases did not yield good results because of the curse of dimensionality. I need to dig in deeper to see how to improve their performance; possibly by getting more comps or limiting the feature subset to a very small number.

I also find the NLP work very promising -- there is a lot of hidden data in the text of these places and I'd like to look at the body of the description as well as the reviews to determine underlying trends among high revenue properties.

The goal is to create an API endpoint that seamlessly integrates with the upcoming AirDNA personalized dashboard.
