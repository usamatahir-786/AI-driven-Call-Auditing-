# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class Agent(Base):
    __tablename__ = "Agent"
    
    agent_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_name = Column(String(100))
    email = Column(String(100), unique=True)
    agent_code = Column(String(50))
