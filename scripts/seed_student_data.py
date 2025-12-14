from configs.database import SessionLocal
from models.student import Student

def seed_students():
    db = SessionLocal()
    try:
        if db.query(Student).count() == 0:
            db.add_all([
                Student(full_name="Nguyen Van A", age=20, email="nva@test.com"),
                Student(full_name="Nguyen Thi B", age=22, email="ntb@test.com"),
            ])
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_students()
