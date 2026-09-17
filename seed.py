"""Create the demo account and doctors."""
from database import Base, SessionLocal, engine
from models import DoctorDB, UserDB
from security import hash_password


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(UserDB).filter(UserDB.username == "admin").first():
            db.add(UserDB(username="admin", full_name="Front Desk Admin", password_hash=hash_password("admin123")))
        if db.query(DoctorDB).count() == 0:
            db.add_all([
                DoctorDB(name="Dr. Sarah Jenkins", specialty="General Practice"),
                DoctorDB(name="Dr. Rajiv Sharma", specialty="Cardiology"),
                DoctorDB(name="Dr. Elena Rostova", specialty="Pediatrics"),
                DoctorDB(name="Dr. Marcus Vance", specialty="Orthopedics"),
            ])
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
