import joblib

# load the trained model
model = joblib.load("risk_model.pkl")

def predict_risk(temp, rain, aqi):
    prediction = model.predict([[temp, rain, aqi]])
    
    if prediction[0] == 1:
        return "High Risk"
    else:
        return "Low Risk"


# test example
result = predict_risk(42, 60, 350)
print("Prediction:", result)