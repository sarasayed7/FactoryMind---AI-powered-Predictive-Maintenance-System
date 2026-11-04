from langgraph.graph import StateGraph, START, END

from app.agents.state import FactoryMindState
from app.agents.nodes import prediction_node, history_node, maintenance_node, risk_router, assessment_node, validate_machine_node

builder = StateGraph(FactoryMindState)

# NODES
# 13. Register validate_machine_node as validate_machine
builder.add_node('validate_machine', validate_machine_node)

# 1. Register prediction_node as "prediction"
builder.add_node('prediction', prediction_node)

# 2. Register history_node as "history"
builder.add_node('history', history_node)

# 8. Register maintenance_node as "maintenance"
builder.add_node('maintenance', maintenance_node)

# 11. Register assessment_node as "assessment"
builder.add_node('assessment', assessment_node)


# EDGES
#14. connct START to validate_machine
builder.add_edge(START, 'validate_machine')

# 3. Connect validate_machine to prediction
builder.add_edge('validate_machine', 'prediction')

# 4. Connect prediction to history
builder.add_edge('prediction', 'history')

# 9. Connect history to risk_router
builder.add_conditional_edges('history', risk_router, {
    'maintenance': 'maintenance',
    'end': "assessment"
})

#10. Connect maintenance_node to assessment_node
builder.add_edge('maintenance', 'assessment')

# 12. Connect assessment to END
builder.add_edge('assessment', END)


# 6. Compile the graph
graph = builder.compile()


#  testing error handling
# initial_state = {
#     "machine_id": "M-999",
#     "sensor_data": {
#         "machine_id": "M-777",
#         "air_temperature": 300.0,
#         "process_temperature": 310.0,
#         "rotational_speed": 1500,
#         "torque": 40.0,
#         "tool_wear": 100
#     },
#     "prediction": None,
#     "history": [],
#     "maintenance_answer": None,
#     "assessment": None,
#     "machine_validated": False,
#     "errors": []
# }

# 7. invoke

if __name__ == "__main__":
    # Test graph here
    initial_state = {
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
    "assessment": None,
    "machine_validated": False,
    "errors": []
    }
    result = graph.invoke(initial_state)

    # print("Prediction:", result["prediction"])
    # print("History:", result["history"])
    # print("Maintenance:", result["maintenance_answer"])
    # print("Errors:", result["errors"])

    print("FINAL ASSESSMENT:")
    print(result["assessment"])
