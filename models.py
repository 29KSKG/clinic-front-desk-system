"""Database models for users, doctors and appointments."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import relationship
from database import Base

STATUS_BOOKED = "CONFIRMED"
STATUS_CANCELLED = "CANCELLED"


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="frontdesk", nullable=False)


class DoctorDB(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)
    specialty = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    appointments = relationship("AppointmentDB", back_populates="doctor")


class AppointmentDB(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(120), nullable=False, index=True)
    patient_phone = Column(String(30), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default=STATUS_BOOKED, nullable=False, index=True)
    cancellation_fee = Column(Float, default=0.0, nullable=False)
    cancelled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    doctor = relationship("DoctorDB", back_populates="appointments")
    __table_args__ = (Index("ix_live_doctor_start", "doctor_id", "start_time", unique=True, sqlite_where=text("status = 'CONFIRMED'")),)
