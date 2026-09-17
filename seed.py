"""Create or upgrade the demo database and seed its initial records."""
from database import Base, SessionLocal, engine, upgrade_schema
from models import DoctorDB, UserDB
from security import hash_password


def run():
    # create_all is not a migration tool; upgrade existing tables first.
    Base.metadata.create_all(bind=engine)
    upgrade_schema()

    db = SessionLocal()
    try:
        if not db.query(UserDB).filter(UserDB.username == "admin").first():
            db.add(
                UserDB(
                    username="admin",
                    full_name="Front Desk Admin",
                    hashed_password=hash_password("admin123"),
                    role="admin",
                )
            )

        if db.query(DoctorDB).count() == 0:
            db.add_all([
                DoctorDB(name="Dr. Sarah Jenkins", specialty="General Practice"),
                DoctorDB(name="Dr. Rajiv Sharma", specialty="Cardiology"),
                DoctorDB(name="Dr. Elena Rostova", specialty="Pediatrics"),
                DoctorDB(name="Dr. Marcus Vance", specialty="Orthopedics"),
            ])
        db.commit()
        print("Database ready. Demo login: admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
