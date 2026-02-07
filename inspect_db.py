import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv("backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL")

def inspect():
    if not DATABASE_URL:
        print("❌ No DB URL")
        return
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("--- Searching for Moltbook Posts ---")
            result = conn.execute(text("SELECT title, created_at FROM posts WHERE title LIKE '%Moltbook%'"))
            rows = result.fetchall()
            print(f"Found {len(rows)} posts matching '%Moltbook%'")
            for r in rows:
                print(f"Spam Title: {r[0]}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    inspect()
