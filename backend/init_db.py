from app.database import Base, engine
from app.models import agent, post, comment, face, vote

try:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Error: {e}")
