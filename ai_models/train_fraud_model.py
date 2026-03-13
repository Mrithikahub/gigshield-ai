import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

data = {
    "claim_amount":[200,5000,300,1000,150,7000],
    "risk_score":[0.7,0.0,0.6,0.2,0.5,0.1],
    "disruption_count":[1,0,1,0,1,0],
    "past_claims":[2,7,1,3,0,10],
    "avg_claim":[400,300,350,500,200,250],
    "days_since":[30,3,60,10,100,2],
    "fraud":[0,1,0,0,0,1]
}

df = pd.DataFrame(data)

X = df.drop("fraud",axis=1)
y = df["fraud"]

model = RandomForestClassifier()
model.fit(X,y)

joblib.dump(model,"fraud_model.pkl")

print("Fraud model trained")