from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    middle_name = Column(String(50))
    last_name = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    user_level_id = Column(String(255))
    reports_to_user_id = Column(Integer, ForeignKey("users.user_id"))
    photo = Column(String(255))
    mobile_number = Column(String(20))
    department_id = Column(Integer)  # ForeignKey to departments table
    profile = Column(Text) 