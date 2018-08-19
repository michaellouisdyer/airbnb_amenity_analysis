# EDA
from utils import to_markdown
import pandas as pd
import numpy as np
from data_prep import get_data
import matplotlib.pyplot as plt
import seaborn as sns


def plot_amenities(amenity_df):
    """Create violin plots of various amenities"""

    df = amenity_df.select_dtypes(include=['bool']).dropna()
    fig, axes = plt.subplots(5, 5, sharey='row')
    fig.suptitle("Yearly revenue comparison for Airbnb amenities in Denver")

    # delete unused axes
    fig.delaxes(axes[4, 2])
    fig.delaxes(axes[4, 3])
    fig.delaxes(axes[4, 4])

    for i, col in enumerate(df.columns):
            ax = axes[i // 5, i % 5]
            amenities = amenity_df[['c_revenue_native_ltm', col]]
            sns.violinplot(x=col, y='c_revenue_native_ltm', data=amenities, split=True, ax=ax)
            ax.set_ylabel('Yearly Revenue')
            ax.set_xlabel('')
            if i % 5 != 0:
                ax.yaxis.set_visible(False)
            ax.set_title(col)


def amenity_stats(amenity_df):
    """Calculate the mean difference and standard deviation for various amenities"""

    df = amenity_df.select_dtypes(include=['bool']).dropna()

    stats = pd.DataFrame(columns=['Mean_dif', 'standard_deviation_of_dif'])

    for i, col in enumerate(df.columns):
            amenities = amenity_df[['c_revenue_native_ltm', col]].groupby(col)
            amenity_stats = amenities.describe()['c_revenue_native_ltm']

            mean = amenity_stats['mean'].iloc[0] - amenity_stats['mean'].iloc[1],

            std_dev = np.sqrt(amenity_stats['std'].iloc[0]**2 + amenity_stats['std'].iloc[1]**2)

            stats.loc[col] = {'Mean_dif': mean[0], 'standard_deviation_of_dif': std_dev}
    return stats


def main():
    amenity_df = get_data()
    plot_amenities(amenity_df)
    plt.show())

    stats=amenity_IQR(amenity_df)
    to_markdown(stats)  # tabulated form of stats table


if __name__ == '__main__':
    main()
