from app.agents.nodes import risk_router
from app.agents.state import FactoryMindState

test_cases = [
    {"prediction": {"predicted_class": 1}},
    {"prediction": {"predicted_class": 0}},
    {"prediction": None}
]

for state in test_cases:
    print(risk_router(state))