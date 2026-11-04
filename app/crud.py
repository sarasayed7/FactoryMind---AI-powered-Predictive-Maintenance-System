from sqlalchemy.orm import Session
from sqlalchemy import select, func 
from sqlalchemy.orm import selectinload

from app.models import Machine, SensorReading, Prediction


def save_prediction(db: Session, machine_id: str, sensor, result):
    try:
        reading = SensorReading(
                machine_id=machine_id,
                air_temperature=sensor.air_temperature,
                process_temperature=sensor.process_temperature,
                rotational_speed=sensor.rotational_speed,
                torque=sensor.torque,
                tool_wear=sensor.tool_wear
        )
        db.add(reading)
        db.flush()
        
        prediction = Prediction(
            reading_id = reading.id,
            predicted_class = result['predicted_class'],
            failure_probability = result['failure_probability'],
            model_version = 'v1.0'
        )
        db.add(prediction)
        db.commit()
        
        return prediction
    except Exception:
        db.rollback()
        raise


def get_machine_history(
    db: Session,
    machine_id: str,
    limit: int = 20,
    offset: int = 0
):
    statement = (
        select(SensorReading)
        .where(SensorReading.machine_id == machine_id)
        .order_by(
            SensorReading.recorded_at.desc(),
            SensorReading.id.desc()
        )
        .options(selectinload(SensorReading.predictions))
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(statement).all()



def get_dashboard_summary(db: Session):
    total_machines = db.scalar(
        select(func.count()).select_from(Machine)
    )
    total_sensor_readings = db.scalar(
        select(func.count()).select_from(SensorReading)
    )

    # Rank readings separately for each machine.
    ranked_readings = (
        select(
            SensorReading.id.label("reading_id"),
            SensorReading.machine_id.label("machine_id"),
            func.row_number().over(
                partition_by=SensorReading.machine_id,
                order_by=[
                    SensorReading.recorded_at.desc(),
                    SensorReading.id.desc()
                ]
            ).label("row_num")
        )
        .subquery()
    )

    # Select the latest reading for each machine
    latest_readings = (
        select(ranked_readings.c.reading_id)
        .where(ranked_readings.c.row_num == 1)
        .subquery()
    )

    # Count machines whose latest reading has a failure prediction.
    machines_at_risk = db.scalar(
        select(func.count(func.distinct(SensorReading.machine_id)))
        .join(
            Prediction,
            Prediction.reading_id == SensorReading.id
        )
        .join(
            latest_readings,
            latest_readings.c.reading_id == SensorReading.id
        )
        .where(Prediction.predicted_class == 1)
    )

    return{
        "total_machines": total_machines,
        "total_sensor_readings": total_sensor_readings,
        "machines_at_risk": machines_at_risk or 0
    }

