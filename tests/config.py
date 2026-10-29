import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:5173").rstrip("/")

CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "client@eventflow.test")
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD", "client1234")
ORGA_EMAIL = os.getenv("ORGA_EMAIL", "orga@eventflow.test")
ORGA_PASSWORD = os.getenv("ORGA_PASSWORD", "orga1234")
