from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from tabulate import tabulate
import numpy as np
import pandas as pd

from fancyimpute import SimpleFill, KNN,  IterativeSVD, MatrixFactorization

def to_markdown(df, round_places=3):
    """Returns a markdown, rounded representation of a dataframe"""
    print(tabulate(df.round(round_places), headers='keys', tablefmt='pipe'))

def return_markdown(df, round_places = 3):
    return tabulate(df.round(round_places), headers='keys', tablefmt='pipe')

class XyScaler(BaseEstimator, TransformerMixin):
    """Standardize a training set of data along with a vector of targets."""

    def __init__(self):
        self.X_scaler = StandardScaler()
        self.y_scaler = StandardScaler()

    def fit(self, X, y, *args, **kwargs):
        """Fit the scaler to data and a target vector."""
        self.X_scaler.fit(X)
        self.y_scaler.fit(y.reshape(-1, 1))
        return self

    def transform(self, X, y, *args, **kwargs):
        """Transform a new set of data and target vector."""
        return (self.X_scaler.transform(X, copy=True),
                self.y_scaler.transform(y.reshape(-1, 1), copy=True).flatten())

    def inverse_transform(self, X, y, *args, **kwargs):
        """Tranform from a scaled representation back to the original scale."""
        return (self.X_scaler.inverse_transform(X),
                self.y_scaler.inverse_transform(y.reshape(-1, 1)).flatten())

def impute_df(df, algorithm):
    """Returns completed dataframe given an imputation algorithm"""
    return pd.DataFrame(data=algorithm.complete(df), columns=df.columns, index=df.index)


def create_test_df(df, p, cols_to_replace):
    """Creates a DF with p ratio of values replaced with None in the specificed columns"""
    x_complete = df[cols_to_replace]
    N = df.shape[0]
    M = len(cols_to_replace)
    missing_mask = np.random.choice(a=[True, False], size=(N, M), p=[p, 1-p])
    x_incomplete = x_complete.mask(missing_mask, other=None)
    df_incomplete = df.copy()
    df_incomplete[cols_to_replace] = x_incomplete
    return df_incomplete


def determine_impute(df):
    """Iterates various imputation methods to find lower MSE"""
    algorithms = [SimpleFill(), KNN(1), KNN(2), KNN(3), KNN(
        4), KNN(5), IterativeSVD(),  MatrixFactorization()]
    MSE = {}
    df_incomplete = create_test_df(df, 0.7, list(df.keys()))
    for i, alg in enumerate(algorithms):
        print(alg)
        X_complete = impute_df(df_incomplete, alg)
        alg_mse = ((df-X_complete) ** 2).sum().mean()
        print(str(i) + alg.__class__.__name__, alg_mse)
        MSE[str(i)+alg.__class__.__name__] = alg_mse
    return MSE
