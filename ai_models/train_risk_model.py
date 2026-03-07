import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# load dataset
data = pd.read_csv("dataset.csv")

# features and label
X = data[['temperature','rainfall','aqi']]
y = data['risk']

# create model
model = RandomForestClassifier()

# train model
model.fit(X, y)

# save model
joblib.dump(model, "risk_model.pkl")

print("Risk model trained and saved")