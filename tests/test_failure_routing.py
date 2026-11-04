from app.agents.nodes import risk_router

failure_state = {
    "prediction": {
        "predicted_class": 1,
        "failure_probability": 0.85,
        "status": "failure_risk"
    }
}

route = risk_router(failure_state)

assert route == "maintenance"

print("Failure-risk routing test passed!")