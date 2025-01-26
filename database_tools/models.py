from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    description = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
