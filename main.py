from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib

# Standard SHA-256 Hashing helper
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# ==========================================
# 1. DATABASE SETUP
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./clinic.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="frontdesk")

class DoctorDB(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    appointments = relationship("AppointmentDB", back_populates="doctor")

class AppointmentDB(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True, nullable=False)
    patient_phone = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="CONFIRMED")
    cancellation_fee = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor = relationship("DoctorDB", back_populates="appointments")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_data():
    db = SessionLocal()
    if not db.query(UserDB).filter(UserDB.username == "admin").first():
        hashed_pw = hash_password("admin123")
        db.add(UserDB(username="admin", full_name="Front Desk Admin", hashed_password=hashed_pw, role="admin"))
    
    if db.query(DoctorDB).count() == 0:
        docs = [
            DoctorDB(name="Dr. Sarah Jenkins", specialty="General Practice"),
            DoctorDB(name="Dr. Rajiv Sharma", specialty="Cardiology"),
            DoctorDB(name="Dr. Elena Rostova", specialty="Pediatrics"),
            DoctorDB(name="Dr. Marcus Vance", specialty="Orthopedics")
        ]
        db.add_all(docs)
    db.commit()
    db.close()

seed_data()

# ==========================================
# 2. SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: str
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_name: str
    patient_phone: str
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
    items: List[AppointmentOut]

# ==========================================
# 3. FASTAPI APP & ENDPOINTS
# ==========================================
app = FastAPI(title="CareSync Front Desk Clinic API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/register", tags=["Auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserDB).filter(UserDB.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hash_password(user.password)
    db_user = UserDB(username=user.username, full_name=user.full_name, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/api/auth/login", tags=["Auth"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "username": db_user.username, "full_name": db_user.full_name}

@app.get("/api/doctors", response_model=List[DoctorOut], tags=["Doctors"])
def get_doctors(db: Session = Depends(get_db)):
    return db.query(DoctorDB).all()

@app.post("/api/appointments", response_model=AppointmentOut, tags=["Appointments"])
def book_appointment(appt: AppointmentCreate, db: Session = Depends(get_db)):
    start = appt.start_time
    end = start + timedelta(minutes=appt.duration_minutes)

    if start < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot book appointments in the past.")

    overlapping = db.query(AppointmentDB).filter(
        AppointmentDB.doctor_id == appt.doctor_id,
        AppointmentDB.status == "CONFIRMED",
        AppointmentDB.start_time < end,
        AppointmentDB.end_time > start
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=409,
            detail=f"Conflict: Doctor is already booked between {overlapping.start_time.strftime('%H:%M')} and {overlapping.end_time.strftime('%H:%M')}."
        )

    doc = db.query(DoctorDB).filter(DoctorDB.id == appt.doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    new_appt = AppointmentDB(
        patient_name=appt.patient_name,
        patient_phone=appt.patient_phone,
        doctor_id=appt.doctor_id,
        start_time=start,
        end_time=end,
        status="CONFIRMED"
    )
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)

    return AppointmentOut(
        id=new_appt.id,
        patient_name=new_appt.patient_name,
        patient_phone=new_appt.patient_phone,
        doctor_id=new_appt.doctor_id,
        doctor_name=doc.name,
        start_time=new_appt.start_time,
        end_time=new_appt.end_time,
        status=new_appt.status,
        cancellation_fee=new_appt.cancellation_fee
    )

@app.put("/api/appointments/{appt_id}/cancel", tags=["Appointments"])
def cancel_appointment(appt_id: int, db: Session = Depends(get_db)):
    appt = db.query(AppointmentDB).filter(AppointmentDB.id == appt_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Appointment is already cancelled")

    now = datetime.utcnow()
    hours_until_appt = (appt.start_time - now).total_seconds() / 3600.0

    fee = 0.0
    if hours_until_appt < 24.0:
        fee = 25.0

    appt.status = "CANCELLED"
    appt.cancellation_fee = fee
    db.commit()

    return {
        "message": "Appointment cancelled successfully",
        "cancellation_fee": fee,
        "is_late": fee > 0
    }

@app.get("/api/appointments/search", response_model=PaginatedAppointments, tags=["Appointments"])
def search_appointments(
    search: Optional[str] = Query(None),
    doctor_id: Optional[int] = Query(None),
    date_str: Optional[str] = Query(None),
    sort_by: str = Query("start_time", enum=["start_time", "patient_name", "created_at"]),
    sort_order: str = Query("asc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    query = db.query(AppointmentDB)

    if search:
        query = query.filter(AppointmentDB.patient_name.ilike(f"%{search}%"))
    if doctor_id:
        query = query.filter(AppointmentDB.doctor_id == doctor_id)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_of_day = datetime.combine(target_date, datetime.min.time())
            end_of_day = datetime.combine(target_date, datetime.max.time())
            query = query.filter(AppointmentDB.start_time >= start_of_day, AppointmentDB.start_time <= end_of_day)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    order_col = getattr(AppointmentDB, sort_by)
    if sort_order == "desc":
        order_col = order_col.desc()
    query = query.order_by(order_col)

    total = query.count()
    items_db = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for appt in items_db:
        items.append(
            AppointmentOut(
                id=appt.id,
                patient_name=appt.patient_name,
                patient_phone=appt.patient_phone,
                doctor_id=appt.doctor_id,
                doctor_name=appt.doctor.name if appt.doctor else "Unknown",
                start_time=appt.start_time,
                end_time=appt.end_time,
                status=appt.status,
                cancellation_fee=appt.cancellation_fee
            )
        )

    return PaginatedAppointments(total=total, page=page, page_size=page_size, items=items)
