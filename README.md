Variance inflation factors for bookings:


|  Variables         |   VIF          |
|:-------------------|---------------:|
| Unnamed: 0         |    1.058       |
| num_res            |    1.953       |
| airbnb_property_id |    7.785       |
| occ_rate           |   13.804       |
| revenue_potential  |   24.634       |
| days_b             |   84.55        |
| days_a             |  104.978       |
| days_r             |  126.696       |
| city_id            | 1463.55        |
| adr_native         |    1.254e+06   |
| adr                |    1.254e+06   |
| revenue            |    5.608e+06   |
| revenue_native     |    5.608e+06   |


Data imputation MSE:
|   Imputation Method  |    MSE         |
|:---------------------|---------------:|
| SimpleFill (mean)    | 2050.91        |
| 1KNN                 | 3942.8         |
| 2KNN                 | 2963.37        |
| 3KNN                 | 2592.96        |
| 4KNN                 | 2432.66        |
| 5KNN                 | 2332.15        |
| IterativeSVD        |    2.11556e+06 |
| MatrixFactorization | 2104.69        |

Vifs before feature selection (all of Denver)
|                      |         0 |
|:---------------------|----------:|
| breakfast            |     1.04  |
| pets_allowed         |     1.05  |
| longitude            |     1.052 |
| smoking              |     1.081 |
| intercom             |     1.103 |
| indoor_fireplace     |     1.103 |
| suitable_for_events  |     1.107 |
| wireless             |     1.118 |
| free_parking         |     1.125 |
| aircon               |     1.136 |
| handicap_access      |     1.138 |
| doorman              |     1.139 |
| heating              |     1.14  |
| kitchen              |     1.164 |
| internet             |     1.179 |
| family_friendly      |     1.183 |
| tv                   |     1.187 |
| cabletv              |     1.205 |
| hottub               |     1.42  |
| bathrooms            |     1.551 |
| pool                 |     1.888 |
| elevator             |     1.908 |
| gym                  |     2.143 |
| bedrooms             |     3.526 |
| accommodates         |     3.699 |
| dryer                |     7.674 |
| washer               |     7.675 |
| guidebook            |   nan     |


after:
|                      |         0 |
|:---------------------|----------:|
| breakfast            |     1.04  |
| pets_allowed         |     1.05  |
| longitude            |     1.052 |
| smoking              |     1.081 |
| indoor_fireplace     |     1.102 |
| intercom             |     1.103 |
| suitable_for_events  |     1.107 |
| wireless             |     1.116 |
| free_parking         |     1.125 |
| aircon               |     1.134 |
| handicap_access      |     1.138 |
| doorman              |     1.139 |
| heating              |     1.14  |
| kitchen              |     1.163 |
| internet             |     1.179 |
| family_friendly      |     1.183 |
| tv                   |     1.185 |
| washer               |     1.185 |
| cabletv              |     1.205 |
| hottub               |     1.42  |
| c_revenue_native_ltm |     1.515 |
| bathrooms            |     1.55  |
| pool                 |     1.887 |
| elevator             |     1.908 |
| gym                  |     2.143 |
| bedrooms             |     3.524 |
| accommodates         |     3.698 |

ElasticNet (l1 ratio = 1, epsilon = 0.001)
R^2 = 0.2618
|                     |         0 |
|:--------------------|----------:|
| pool                | -1576.91  |
| pets_allowed        | -1017.37  |
| suitable_for_events |  -761.282 |
| doorman             |  -701.459 |
| breakfast           |  -592.936 |
| indoor_fireplace    |  -134.433 |
| washer              |  -127.106 |
| handicap_access     |     0     |
| free_parking        |    -0     |
| kitchen             |    -0     |
| constant            |     0     |
| tv                  |     0     |
| smoking             |    -0     |
| gym                 |    59.6   |
| heating             |   175.392 |
| intercom            |   305.681 |
| wireless            |   591.156 |
| elevator            |   595.671 |
| family_friendly     |   676.562 |
| hottub              |   727.286 |
| aircon              |   757.886 |
| bathrooms           |  1119.92  |
| cabletv             |  2608.05  |
| internet            |  2712.64  |
| accommodates        |  9659.45  |
None

Standard linear regression:
0.2590
|                     |         0 |
|:--------------------|----------:|
| pool                | -1880.88  |
| pets_allowed        | -1110.54  |
| suitable_for_events |  -866.496 |
| doorman             |  -845.254 |
| breakfast           |  -697.207 |
| indoor_fireplace    |  -279.816 |
| washer              |  -266.462 |
| kitchen             |  -109.407 |
| handicap_access     |   -63.143 |
| free_parking        |   -26.873 |
| constant            |     0     |
| tv                  |    14.549 |
| smoking             |    27.328 |
| heating             |   253.956 |
| gym                 |   266.959 |
| intercom            |   405.442 |
| wireless            |   662.696 |
| elevator            |   695.705 |
| family_friendly     |   768.847 |
| aircon              |   838.895 |
| hottub              |   911.675 |
| bathrooms           |  1222.67  |
| cabletv             |  2665.65  |
| internet            |  2804.09  |
| accommodates        |  9729.23  |


Removing bathrooms and accommodates:

ElasticNet (l1 ratio = 1, alpha = 129.33)
r^2 = 0.1331
|                     |         0 |
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


standard linear regressions:
0.1315
|                     |         0 |
|:--------------------|----------:|
| pool                | -3278.2   |
| pets_allowed        | -1262.91  |
| breakfast           | -1171.62  |
| doorman             |  -773.915 |
| smoking             |  -448.95  |
| constant            |     0     |
| gym                 |     5.268 |
| handicap_access     |    56.803 |
| elevator            |   181.741 |
| heating             |   218.822 |
| intercom            |   285.8   |
| wireless            |   489.42  |
| washer              |   515.185 |
| free_parking        |   540.071 |
| kitchen             |   727.196 |
| suitable_for_events |   873.55  |
| tv                  |   912.621 |
| indoor_fireplace    |  1130.24  |
| aircon              |  1489.26  |
| hottub              |  1572.16  |
| internet            |  2226.67  |
| cabletv             |  3668.84  |
| family_friendly     |  3778.69  |
