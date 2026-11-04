from app.schemas import SensorInput, PredictionResponse

sensor = SensorInput(
    machine_id = "M-101",
    air_temperature=300.5,
    process_temperature=310.2,
    rotational_speed=1450,
    # rotational_speed= -100, # This will raise a validation error because rotational_speed must be greater than 0
    torque=45.3,
    tool_wear=180
)

print(sensor.model_dump())  # This will print the dictionary representation of the SensorInput instance

response = PredictionResponse(
    predicted_class=1,
    failure_probability=0.85,
    # failure_probability=1.5, # This will raise a validation error because failure_probability must be between 0 and 1
    status="failure_risk"
    # status= 'unknown' # this will raise a validation error because status must be either 'failure_risk' or 'normal'
)
print(response.model_dump())  # This will print the dictionary representation of the PredictionResponse instance