import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Set up the database connection and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
