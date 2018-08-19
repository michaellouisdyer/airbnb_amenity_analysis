"""Nearest Neighbor Median Regression"""
# edited from SKlearn
from sklearn.neighbors import KNeighborsRegressor

import warnings

import numpy as np
from scipy.sparse import issparse

from sklearn.neighbors.base import _get_weights, _check_weights, NeighborsBase, KNeighborsMixin
from sklearn.neighbors.base import RadiusNeighborsMixin, SupervisedFloatMixin
from sklearn.base import RegressorMixin
from sklearn.utils import check_array
class KNeighborsMedianRegressor(KNeighborsRegressor):

 def predict(self, X):
        """Predict the target for the provided data
        Parameters
        ----------
        X : array-like, shape (n_query, n_features), \
                or (n_query, n_indexed) if metric == 'precomputed'
            Test samples.
        Returns
        -------
        y : array of int, shape = [n_samples] or [n_samples, n_outputs]
            Target values
        """
        if issparse(X) and self.metric == 'precomputed':
            raise ValueError(
                "Sparse matrices not supported for prediction with "
                "precomputed kernels. Densify your matrix."
            )
            X = check_array(X, accept_sparse='csr')

        neigh_dist, neigh_ind = self.kneighbors(X)

        weights = _get_weights(neigh_dist, self.weights)

        _y = self._y
        if _y.ndim == 1:
            _y = _y.reshape((-1, 1))

        if weights is None:
            y_pred = np.median(_y[neigh_ind], axis=1)
        else:
            weights = weights / weights.sum()
            num = _y[neigh_ind.flatten()].T * weights
            cs = list(np.cumsum(num.flatten()))
            ind = np.searchsorted(cs, cs[-1] / 2.0)
            y_pred = _y[ind]

        if self._y.ndim == 1:
            y_pred = y_pred.ravel()
        return y_pred
