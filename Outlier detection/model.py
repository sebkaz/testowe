
from joblib import dump
import numpy as np
from sklearn.ensemble import IsolationForest

ran_gen = np.random.RandomState(44) 

X = 0.4 * ran_gen.randn(500,2)
X = np.round(X, 3)
X_train = np.r_[X+2, X-2]

clf = IsolationForest(n_estimators=50, max_samples=500, random_state=ran_gen, contamination=0.01)
clf.fit(X_train)

dump(clf, './isolation_forest.joblib')
