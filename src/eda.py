# eda
from utils import to_markdown
import pandas as pd
import numpy as np
from data_prep import get_data
import matplotlib.pyplot as plt
import seaborn as sns
def plot_amenities(amenity_df):
    df =  amenity_df.select_dtypes(include = ['bool'])#.dropna()
    fig, axes =  plt.subplots(5,5, sharey =  'row')
    fig.suptitle("Yearly revenue comparison for Airbnb amenities in Denver")
    fig.delaxes(axes[4, 2])
    fig.delaxes(axes[4, 3])
    fig.delaxes(axes[4, 4])
    for i, col in enumerate(df.columns):
            ax  = axes[i // 5, i % 5]
            amenities = amenity_df[['c_revenue_native_ltm',col]]
            sns.violinplot(x= col, y =  'c_revenue_native_ltm', data =  amenities, split =  True, ax =  ax)
            ax.set_ylabel('Yearly Revenue')
            ax.set_xlabel('')
            if i % 5 != 0:
                ax.yaxis.set_visible(False)
            if i // 5 != 5:
                # ax.xaxis.set_visible(False)
                pass
            ax.set_title(col)

def amenity_IQR(amenity_df):
    df =  amenity_df.select_dtypes(include = ['bool'])#.dropna()
    stats =  pd.DataFrame(columns = ['Mean_dif', 'standard_deviation'])
    for i, col in enumerate(df.columns):
            amenities = amenity_df[['c_revenue_native_ltm',col]].groupby(col)
            amenity_stats = amenities.describe()['c_revenue_native_ltm']
            # amenity_stats['IQR'] = amenity_stats['75%'] -  amenity_stats['25%']
            mean = amenity_stats['mean'].iloc[0] -  amenity_stats['mean'].iloc[1],
            std_dev =             np.sqrt(amenity_stats['std'].iloc[0]**2 +  amenity_stats['std'].iloc[1]**2 )
            stats.loc[col] = {'Mean_dif': mean[0], 'standard_deviation':std_dev }
    return stats


amenity_df = get_data()
# amenity_analysis(amenity_df)

stats = amenity_IQR(amenity_df)
import pdb; pdb.set_trace()
# plt.show()
