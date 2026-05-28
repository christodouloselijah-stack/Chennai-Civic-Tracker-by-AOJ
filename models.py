from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Constituency(Base):
    __tablename__ = "constituencies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    district = Column(String, index=True)
    
    updates = relationship("CivicUpdate", back_populates="constituency")

class CivicUpdate(Base):
    __tablename__ = "civic_updates"
    id = Column(Integer, primary_key=True, index=True)
    constituency_id = Column(Integer, ForeignKey("constituencies.id"))
    title = Column(String)
    description = Column(String)
    status = Column(String)
    image_url = Column(String)
    date = Column(Date)
    source = Column(String)
    article_url = Column(String)

    constituency = relationship("Constituency", back_populates="updates")

class Feedback(Base):
    __tablename__ = "feedback_submissions"
    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String, index=True)
    title = Column(String)
    area = Column(String)
    description = Column(String)
    source_url = Column(String)
    submitter = Column(String)
    date = Column(Date)
