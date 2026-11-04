from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime

# Machine Learning Model
class SensorInput(BaseModel):
    machine_id: str = Field(min_length = 1, max_length = 20)
    air_temperature: float = Field(ge=0)
    process_temperature: float = Field(ge=0)
    rotational_speed: float = Field(gt=0)
    torque: float = Field(ge=0)
    tool_wear: float = Field(ge=0)

class PredictionResponse(BaseModel):
    predicted_class: int = Field(ge=0, le=1)
    failure_probability: float = Field(ge=0, le=1)
    status: Literal['failure_risk', 'normal']

# PostgreSQL
class PredictionHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    predicted_class: int = Field(ge=0, le=1)
    failure_probability: float = Field(ge=0, le=1)
    model_version: str
    created_at: datetime
    
class SensorReadingHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: str = Field(min_length = 1, max_length = 20)
    air_temperature: float = Field(ge=0)
    process_temperature: float = Field(ge=0)
    rotational_speed: float = Field(gt=0)
    torque: float = Field(ge=0)
    tool_wear: float = Field(ge=0)
    recorded_at: datetime
    predictions: list[PredictionHistory] #--> Nested Schema

# RAG
class MaintenanceQuestion(BaseModel):
    question: str = Field(min_length=3)

class MaintenanceSource(BaseModel):
    source: str
    page_number: int
    similarity_score: float

class MaintenanceAnswer(BaseModel):
    answer: str
    sources: list[MaintenanceSource]

# FastAPI assessment response
class MachineAssessmentResponse(BaseModel):
    machine_id: str
    risk_status: Literal['normal', 'failure_risk']
    failure_probability: float
    history_count: int
    maintenance_guidance: MaintenanceAnswer | None

# Machine response
class MachineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str 
    name: str
    machine_type: str | None
    location: str | None