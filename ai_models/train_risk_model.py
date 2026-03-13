import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

data = {
    "temperature":[30,45,25,42,28,35,40],
    "rainfall":[0,80,0,60,10,0,70],
    "wind":[3,10,2,8,4,5,9],
    "humidity":[60,90,50,80,70,65,85],
    "aqi":[80,150,60,200,90,120,180],
    "disruption_count":[0,1,0,1,0,0,1],
    "risk_score":[0.0,0.7,0.0,0.6,0.1,0.2,0.8],
    "is_disrupted":[0,1,0,1,0,0,1],
    "risk_level":[0,3,0,2,0,1,3]
}

df = pd.DataFrame(data)

X = df.drop("risk_level",axis=1)
y = df["risk_level"]

model = RandomForestClassifier()
model.fit(X,y)

joblib.dump(model,"risk_model.pkl")

print("Risk model trained")