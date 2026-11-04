from langgraph.graph import StateGraph, START, END

from app.agents.state import FactoryMindState
from app.agents.nodes import risk_router, assessment_node

builder = StateGraph(FactoryMindState)

def fake_prediction(state):
    return {
        "prediction": {
            "predicted_class": 1,
            "failure_probability": 0.85,
            "status": "failure_risk"
        }
    }

def fake_history(state):
    return {"history": []}

def fake_maintenance(state):
    return {
        "maintenance_answer": {
            "answer": "Simulated maintenance guidance",
            "sources": []
        }
    }

builder.add_node("prediction", fake_prediction)
builder.add_node("history", fake_history)
builder.add_node("maintenance", fake_maintenance)
builder.add_node("assessment", assessment_node)

builder.add_edge(START, "prediction")
builder.add_edge("prediction", "history")
builder.add_conditional_edges("history", risk_router,
    {
    "maintenance": "maintenance",
    "end": "assessment"
    }
)
builder.add_edge("maintenance","assessment")
builder.add_edge("assessment", END)

test_graph = builder.compile()

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

result = test_graph.invoke(initial_state)

assert result["prediction"]["predicted_class"] == 1
assert result["maintenance_answer"] is not None
assert result["assessment"]["risk_status"] == "failure_risk"
assert result["assessment"]["maintenance_guidance"] is not None

print("Full failure-risk workflow test passed!")
