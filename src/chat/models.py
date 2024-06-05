from sqlalchemy import Column, Integer, BigInteger, String

from src.database import Base

class Message(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    message = Column(String)
    client_id = Column(BigInteger)
