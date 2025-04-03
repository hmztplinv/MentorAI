
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the database initialization
from app.db.init_db import init_db

if __name__ == "__main__":
    init_db()
