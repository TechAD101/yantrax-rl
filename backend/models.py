from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class JournalEntry(Base):
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String(32), nullable=False)
    reward = Column(Float, nullable=True)
    balance = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action': self.action,
            'reward': self.reward,
            'balance': self.balance,
            'notes': self.notes,
            'confidence': self.confidence
        }
