from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, BigInteger, ForeignKey, func, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Machine(Base):
    __tablename__ = 'machines'

    id: Mapped[str] = mapped_column(
        String(20),
        primary_key = True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable = False
    )

    machine_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable = True
    )

    location: Mapped[str | None] = mapped_column(
        String(100),
        nullable = True
    )

class SensorReading(Base):
    __tablename__ = 'sensor_readings'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True
    )

    machine_id: Mapped[str] = mapped_column(
        String(20), 
        ForeignKey('machines.id'),
        nullable = False
    )

    air_temperature: Mapped[float] = mapped_column(
        Float,
        nullable = False
    )

    process_temperature: Mapped[float] = mapped_column(
        Float,
        nullable = False
    )

    rotational_speed: Mapped[float] = mapped_column(
        Float,
        nullable = False
    )

    torque: Mapped[float] = mapped_column(
        Float, 
        nullable = False
    )

    tool_wear: Mapped[float] = mapped_column(
        Float,
        nullable = False
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable = False,
        server_default = func.now()
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates='reading'
    )

class Prediction(Base):
    __tablename__ = 'predictions'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True
    )

    reading_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('sensor_readings.id'),
        nullable = False
    )

    predicted_class: Mapped[int] = mapped_column(
        Integer, 
        nullable = False
    )

    failure_probability: Mapped[float] = mapped_column(
        Float(precision = 53),
        nullable = False
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable = False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        nullable = False,
        server_default = func.now()
    )

    reading: Mapped['SensorReading'] = relationship(
        back_populates='predictions'
    )