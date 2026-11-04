from pathlib import Path
import joblib
import pandas as pd

# Loading model
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    /'artifacts'
    /'factorymind_model.joblib'

)

model = joblib.load(MODEL_PATH)

# Building prediction function
def predict_failure(sensor):
    # 1. Convert sensor into a dictionary
    sensor = sensor.model_dump()  # Convert Pydantic model to dictionary

    # 2. Map API field names to training column names
    data = {
        'Air temperature [K]' : sensor['air_temperature'],
        'Process temperature [K]': sensor['process_temperature'],
        'Rotational speed [rpm]': sensor['rotational_speed'],
        'Torque [Nm]': sensor['torque'],
        'Tool wear [min]': sensor['tool_wear']
    }

    # 3. Create a one-row DataFrame in the correct column order
    df = pd.DataFrame([data])

    # 4. Call model.predict()
    prediction = model.predict(df)
    predicted_class = int(prediction[0])  # Convert numpy array to int

    # 5. Call model.predict_proba()
    probability = model.predict_proba(df)
    failured_probability = float(probability[0][1])  # Probability of class 1 (failure)

    status = "failure_risk" if predicted_class == 1 else "normal"

    # 6. Return predicted class and failure probability
    return{
        'predicted_class': predicted_class,
        'failure_probability': failured_probability,
        'status': status
    }