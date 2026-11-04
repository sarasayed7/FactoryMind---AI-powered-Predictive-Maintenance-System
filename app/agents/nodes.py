from app.agents.state import FactoryMindState
from app.schemas import SensorInput
from app.model_service import predict_failure
from app.database import SessionLocal
from app.crud import get_machine_history, save_prediction
from app.rag.rag_service import answer_maintenance_question
from app.models import Machine

# 1. First Validate M_ID present in PostgreSQL or not
def validate_machine_node(state: FactoryMindState) -> dict:
    # 1. Extract machine_id from state
    machine_id = state['machine_id']
    sensor_data_machine_id = state['sensor_data'].get('machine_id')

    if machine_id != sensor_data_machine_id:
        raise ValueError("Machine ID mismatch between state and sensor data")

    # 2. Open a PostgreSQL session
    db = SessionLocal()

    # 3. Check whether the machine exists
    try:
        machine = db.get(Machine, machine_id)

        if machine is None:
            # 4. Raise ValueError if it doesn't exist
            raise ValueError(f"Machine '{machine_id}' does not exist")

    # 5. Close the session safely
    finally:
        db.close()

    # 6. Return {} if validation succeeds
    return {'machine_validated': True}


# 2. Prediction Node
def prediction_node(state: FactoryMindState) -> dict:
    # 1. Extract sensor_data from state
    sensor_data = state['sensor_data']

    # 2. Validate the data using SensorInput
    sensor = SensorInput(**sensor_data)

    # 3. Call run_prediction()
    result = predict_failure(sensor)

    # 4. Save Prediction to PostgreSQL
    db = SessionLocal()
    try:
        save_prediction(db, state['machine_id'], sensor, result)
    finally:
        db.close()

    # 4. Return {"prediction": result}
    return {
        'prediction': result
    }

# 3. History Node
def history_node(state: FactoryMindState) -> dict:
    # 1. Extract machine_id from state
    machine_id = state['machine_id']

    # 2. Create a PostgreSQL session
    db = SessionLocal()

    try:
        # Error handling for invalid machine_id
        machine = db.get(Machine, machine_id)

        if machine is None:
            raise ValueError(f"Machine '{machine_id}' does not exist")
        
        # 3. Call get_machine_history()
        # Retrieve the 5 most recent records
        history = get_machine_history(db, machine_id, limit= 5, offset= 0)

        # 4. Convert ORM records into dictionaries
        readings = []
        for reading in history:
            record = {
                "reading_id": reading.id,
                "recorded_at": reading.recorded_at.isoformat(),
                "predictions": [
                    {
                        "predicted_class": p.predicted_class,
                        "failure_probability": p.failure_probability
                    }
                    for p in reading.predictions
                ]
            }
            readings.append(record)

        # 6. Return {"history": ...}
        return {
            'history': readings
        }
    
    # 5. Close the session safely
    finally:
        db.close()

# 4. Conditional routing
def risk_router(state: FactoryMindState) -> str:
    # 1. Read the prediction from state
    prediction = state['prediction']

    if prediction is None:
        return 'end'

    # 2. Check predicted_class
    predicted_class = prediction['predicted_class']

    # 3. Return "maintenance" if class is 1
    if predicted_class == 1:
        return 'maintenance'

    # 4. Otherwise return "end"
    return 'end'

# 5. Maintenance Node --> conditional routing
def maintenance_node(state: FactoryMindState) -> dict:
    # 1. Extract machine_id
    machine_id = state['machine_id']

    # 2. Extract prediction
    prediction = state['prediction']

    # 3. Construct a maintenance question
    question = "What maintenance inspections and safety precautions are recommended?"

    # 4. Call answer_maintenance_question()
    result = answer_maintenance_question(question)

    # 5. Return {"maintenance_answer": result}
    return{
        'maintenance_answer': result
    }

# 6. Assessment Node
def assessment_node(state: FactoryMindState) -> dict:
    # 1. Extract machine_id
    machine_id = state['machine_id']

    # 2. Extract prediction
    prediction = state['prediction']

    # 3. Extract history
    history = state['history']

    # 4. Extract maintenance_answer
    maintenance_answer = state['maintenance_answer']

    # 5. Construct an assessment dictionary
    assessment = {
        'machine_id': machine_id,
        'risk_status': prediction['status'],
        'failure_probability': prediction['failure_probability'],
        'history_count': len(history),
        'maintenance_guidance': maintenance_answer 

    }
    # 6. Return {"assessment": assessment}
    return{
        'assessment': assessment
    }