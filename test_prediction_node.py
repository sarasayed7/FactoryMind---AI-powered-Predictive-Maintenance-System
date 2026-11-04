from app.agents.nodes import prediction_node

test_state = {
    "machine_id": "M-101",
    "sensor_data": {
        "machine_id": "M-101",
        "air_temperature": 300.0,
        "process_temperature": 310.0,
        "rotational_speed": 1500,
        "torque": 40.0,
        "tool_wear": 100
    },
    "prediction": None,
    "history": [],
    "maintenance_answer": None,
    "errors": []
}

result = prediction_node(test_state)

print(result)