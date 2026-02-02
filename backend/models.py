from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# -------------------- User Model --------------------
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, unique=True)
    email = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


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


# ------------------------ Portfolio Models ------------------------
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


class Strategy(Base):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    archetype = Column(String(64), nullable=True)
    params = Column(JSON, nullable=True)
    published = Column(Integer, nullable=False, default=0)  # 0=internal/draft, 1=published
    metrics = Column(JSON, nullable=True)  # {win_rate, sharpe, aum}
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'archetype': self.archetype,
            'params': self.params,
            'published': bool(self.published),
            'metrics': self.metrics or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    owner_id = Column(Integer, nullable=True)  # Link to user table when available
    risk_profile = Column(String(32), nullable=False, default='moderate')
    initial_capital = Column(Float, nullable=False, default=100000.0)
    current_value = Column(Float, nullable=True)
    strategy_profile_id = Column(Integer, ForeignKey('strategy_profiles.id'), nullable=True)
    meta = Column(JSON, nullable=True)
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
            'meta': self.meta,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'positions': [p.to_dict() for p in self.positions]
        }


# -------------------- Memecoin Model --------------------
class Memecoin(Base):
    __tablename__ = 'memecoins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), nullable=False, unique=True)
    score = Column(Float, nullable=False, default=0.0)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'score': self.score,
            'metadata': self.meta or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
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


# -------------------- Order Manager (Paper) --------------------
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), nullable=False)
    usd = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default='pending')  # pending, filled, cancelled
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'usd': self.usd,
            'quantity': self.quantity,
            'price': self.price,
            'status': self.status,
            'meta': self.meta or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }
