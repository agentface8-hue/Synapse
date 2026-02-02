from passlib.context import CryptContext
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("Hashing...")
    h = pwd_context.hash("test")
    print(f"Hash: {h[:10]}...")
except Exception as e:
    print(f"Error: {e}")
