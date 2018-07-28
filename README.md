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
