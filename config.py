# config.py
import os

try:
    # Optional: if python-dotenv is installed, this will load .env automatically
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If python-dotenv is not installed, environment variables must be set manually
    pass

# ==========================
#   DB CONFIG
# ==========================
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    # Default to your real local password so it works even without .env
    "password": os.getenv("DB_PASSWORD", "calladoctor1234"),
    "database": os.getenv("DB_NAME", "calladoctor"),
}

# ==========================
#   EMAIL CONFIG
# ==========================
# You can override these via .env later if you want
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "linkeshjpr.25@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "gdnmwsbcljegppkp")
