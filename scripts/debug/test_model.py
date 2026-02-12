from app.database import SessionLocal
from app.models.face import Face
# Ensure env loaded (done in database.py)

db = SessionLocal()
try:
    print("Querying faces...")
    faces = db.query(Face).all()
    print(f"Faces: {len(faces)}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
