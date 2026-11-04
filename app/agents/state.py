from typing import TypedDict, Any

class FactoryMindState(TypedDict):
    machine_id: str
    sensor_data: dict[str, Any]
    prediction: dict | None
    history: list[dict]
    maintenance_answer: dict | None
    assessment: dict | None
    machine_validated: bool
    errors: list[str]

