import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env variables from backend/.env
# Assuming we run this from root
load_dotenv("backend/.env")

DATABASE_URL = os.getenv("DATABASE_URL")

def cleanup():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in backend/.env")
        return

    # Log host only for safety
    try:
        host = DATABASE_URL.split('@')[1]
        print(f"Connecting to DB: {host}")
    except:
        print("Connecting to DB...")

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("Checking for spam posts...")
            
            # Check count
            result = conn.execute(text("SELECT count(*) FROM posts WHERE title LIKE '%Moltbook%'"))
            count = result.scalar()
            print(f"Found {count} spam posts.")

            if count > 0:
                print("Deleting...")
                conn.execute(text("DELETE FROM posts WHERE title LIKE '%Moltbook%'"))
                conn.commit()
                print(f"✅ Deleted {count} posts.")
            else:
                print("No cleanup needed.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    cleanup()
