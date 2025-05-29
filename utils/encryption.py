import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

# Get the encryption key from the environment
FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise ValueError("FERNET_KEY is not set in the environment variables.")

# Initialize Fernet with the loaded key
fernet = Fernet(FERNET_KEY)

def encrypt_password(password: str) -> str:
    """Encrypt the password using Fernet symmetric encryption."""
    try:
        return fernet.encrypt(password.encode()).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Encryption failed: {str(e)}")

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt the password back to plaintext."""
    try:
        return fernet.decrypt(encrypted_password.encode()).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Invalid Password")
