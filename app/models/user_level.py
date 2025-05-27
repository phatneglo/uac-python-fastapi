from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class UserLevel(Base):
    __tablename__ = "user_levels"
    
    user_level_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    system_id = Column(Integer)  # References systems table 