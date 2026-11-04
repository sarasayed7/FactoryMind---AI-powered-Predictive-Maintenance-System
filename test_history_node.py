from app.agents.nodes import history_node

test_state = {
    "machine_id": "M-101",
    "sensor_data": {},
    "prediction": None,
    "history": [],
    "maintenance_answer": None,
    "errors": []
}

result = history_node(test_state)

print(result)
print(type(result["history"]))
print("History records:", len(result["history"]))

for record in result["history"]:
    print(record)
