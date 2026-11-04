from fastapi import FastAPI
from app.schemas import SensorInput, PredictionResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import select
from contextlib import asynccontextmanager


from app.model_service import predict_failure as run_prediction
from app.database import get_db, engine, SessionLocal
from app.crud import save_prediction, get_machine_history, get_dashboard_summary
from app.models import Machine, Base
from app.schemas import SensorReadingHistory, PredictionHistory, MaintenanceAnswer,MaintenanceSource, MaintenanceQuestion, MachineAssessmentResponse, MachineResponse
from app.rag.rag_service import answer_maintenance_question

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't already exist
    Base.metadata.create_all(bind=engine)

    # Seed the initial machine records if missing
    with SessionLocal() as db:
        for machine_id in ["M-101", "M-102"]:
            if db.get(Machine, machine_id) is None:
                db.add(
                    Machine(
                        id=machine_id,
                        name=f"Machine {machine_id}"
                    )
                )

        db.commit()

    yield

app = FastAPI(title="FactoryMind API", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Machine failure classification
@app.post('/predict', response_model=PredictionResponse)
def predict_failure(sensor: SensorInput, db: Session = Depends(get_db)):
    machine = db.get(Machine, sensor.machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )
    
    result = run_prediction(sensor)
    save_prediction(db, sensor.machine_id, sensor, result)
    return result

# Historical sensor readings and predictions
@app.get('/machines/{machine_id}/history', response_model=list[SensorReadingHistory])
def machine_history(machine_id: str, 
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db), ):

    machine = db.get(Machine, machine_id)
    
    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )
    readings = get_machine_history(db, machine_id, limit = limit, offset=offset)
    return readings

# - Maintenance-document RAG assistant
@app.post("/maintenance/ask", response_model=MaintenanceAnswer)
def ask_maintenance(request: MaintenanceQuestion):
    # 1. Extract question from request
    question = request.question

    # 2. Call answer_maintenance_question()
    result = answer_maintenance_question(question)

    # 3. Return the service result
    return result

from fastapi import HTTPException
from pydantic import ValidationError

from app.agents.graph import graph


@app.post("/machines/{machine_id}/assess", response_model=MachineAssessmentResponse)
def assess_machine(machine_id: str, sensor: SensorInput):

    # 1. Build initial LangGraph state
    sensor_data = sensor.model_dump()

    initial_state = {
    "machine_id": machine_id,
    "sensor_data": sensor_data,
    "prediction": None,
    "history": [],
    "maintenance_answer": None,
    "assessment": None,
    "errors": [],
    "machine_validated": False
    }

    # 2. Invoke the graph inside try/except
    try:
        result = graph.invoke(initial_state)
    except ValueError as error:
        # 3. Convert known errors into HTTPException

        message = str(error)

        print("DEBUG - Machine ID:", machine_id)
        print("DEBUG - Sensor Machine ID:", sensor.machine_id)
        print("DEBUG - Exception:", repr(error))

        if message == f"Machine '{machine_id}' does not exist":
            raise HTTPException(
                status_code=404,
                detail=message
            ) from error

        if message == "Machine ID mismatch between state and sensor data":
            raise HTTPException(
                status_code=400,
                detail=message
            ) from error

        raise HTTPException(
            status_code=400,
            detail=message
        ) from error
    
    # 4. Return the final assessment
    return result["assessment"]

@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    summary = get_dashboard_summary(db)
    return summary

@app.get("/machines", response_model=list[MachineResponse])
def list_machines(db: Session = Depends(get_db)):
    machines = db.scalars(select(Machine)).all()
    return machines

# NOTE: run the FastAPI server using the command: uvicorn app.main:app --reload
# /health for health check and /docs for /predict sensor data validation.