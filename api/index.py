import sys
import os

# Add the python-backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))

from main import app

# Export the FastAPI app for Vercel
handler = app 