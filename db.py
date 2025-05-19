from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import Base

engine = create_engine("sqlite:///db.sqlite", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def get_session():
    return session
