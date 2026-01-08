from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    owner_id = Column(Integer, nullable=True)  # Link to user table when available
    risk_profile = Column(String(32), nullable=False, default='moderate')
    initial_capital = Column(Float, nullable=False, default=100000.0)
    current_value = Column(Float, nullable=True)
    strategy_profile_id = Column(Integer, ForeignKey('strategy_profiles.id'), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    positions = relationship('PortfolioPosition', back_populates='portfolio', cascade='all, delete-orphan')
    strategy_profile = relationship('StrategyProfile')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner_id': self.owner_id,
            'risk_profile': self.risk_profile,
            'initial_capital': self.initial_capital,
            'current_value': self.current_value,
            'strategy_profile_id': self.strategy_profile_id,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'positions': [p.to_dict() for p in self.positions]
        }


class PortfolioPosition(Base):
    __tablename__ = 'portfolio_positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    symbol = Column(String(32), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    avg_price = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    portfolio = relationship('Portfolio', back_populates='positions')

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'avg_price': self.avg_price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StrategyProfile(Base):
    __tablename__ = 'strategy_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    archetype = Column(String(64), nullable=True)  # e.g., 'warren', 'quant', 'degen'
    params = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'archetype': self.archetype,
            'params': self.params,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
