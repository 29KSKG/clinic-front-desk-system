"""Pydantic request and response schemas."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)


class UserLogin(BaseModel):
    username: str
    password: str


class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: str
    is_active: bool = True
    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    patient_phone: str = Field(min_length=6, max_length=30)
    doctor_id: int
    start_time: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)


class AppointmentOut(BaseModel):
    id: int
    patient_name: str
    patient_phone: str
    doctor_id: int
    doctor_name: str
    start_time: datetime
    end_time: datetime
    status: str
    cancellation_fee: float
    class Config:
        from_attributes = True


class PaginatedAppointments(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[AppointmentOut]
