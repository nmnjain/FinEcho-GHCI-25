from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    voice_embedding = Column(Text, nullable=True)
    accounts = relationship("Account", back_populates="owner")

    # --- ADD THIS CONSTRUCTOR ---
    def __init__(self, username, voice_embedding=None):
        self.username = username
        self.voice_embedding = voice_embedding

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    account_type = Column(String, index=True)
    balance = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="accounts")

    # --- AND ADD THIS CONSTRUCTOR ---
    def __init__(self, account_type, balance, owner_id):
        self.account_type = account_type
        self.balance = balance
        self.owner_id = owner_id