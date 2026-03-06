from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean, Index
from sqlalchemy.orm import declarative_base, relationship, foreign

Base = declarative_base()


# -------------------- User Model --------------------
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, unique=True)
    email = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None
        }


class JournalEntry(Base):
    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Link to user
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=True)  # Link to portfolio
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String(32), nullable=False)
    reward = Column(Float, nullable=True)
    balance = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    
    user = relationship('User', backref='journal_entries')
    portfolio = relationship('Portfolio', backref='journal_entries')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp is not None else None,
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'archetype': self.archetype,
            'params': self.params,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'archetype': self.archetype,
            'params': self.params,
            'published': bool(self.published),
            'metrics': self.metrics or {},
            'created_at': self.created_at.isoformat() if self.created_at is not None else None
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'owner_id': self.owner_id,
            'risk_profile': self.risk_profile,
            'initial_capital': self.initial_capital,
            'current_value': self.current_value,
            'strategy_profile_id': self.strategy_profile_id,
            'meta': self.meta,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
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
    
    # Relationships
    positions = relationship('PortfolioPosition', primaryjoin="foreign(PortfolioPosition.symbol) == Memecoin.symbol", backref='memecoin')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'score': self.score,
            'meta': self.meta or {},
            'created_at': self.created_at.isoformat() if self.created_at is not None else None
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
    
    __table_args__ = (
        Index('idx_position_portfolio', 'portfolio_id'),
        Index('idx_position_symbol', 'symbol'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'avg_price': self.avg_price,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None
        }


# -------------------- Order Manager (Paper) --------------------
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)  # Link to portfolio
    symbol = Column(String(32), nullable=False)
    usd = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default='pending')  # pending, filled, cancelled
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    
    portfolio = relationship('Portfolio', backref='orders')
    
    __table_args__ = (
        Index('idx_order_portfolio', 'portfolio_id'),
        Index('idx_order_symbol', 'symbol'),
        Index('idx_order_status', 'status'),
        Index('idx_order_created', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'usd': self.usd,
            'quantity': self.quantity,
            'price': self.price,
            'status': self.status,
            'meta': self.meta or {},
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at is not None else None
        }

# -------------------- Market Data & Audit (Institutional) --------------------
class RawMarketData(Base):
    __tablename__ = 'raw_market_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False)
    instrument = Column(String(64), nullable=False)
    metric = Column(String(64), nullable=False)
    value = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    retrieved_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    meta = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_rmd_instrument', 'instrument'),
        Index('idx_rmd_metric', 'metric'),
        Index('idx_rmd_timestamp', 'timestamp'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source,
            'instrument': self.instrument,
            'metric': self.metric,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'retrieved_at': self.retrieved_at.isoformat() if self.retrieved_at else None,
            'meta': self.meta or {}
        }


class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    section = Column(String(128), nullable=False)
    datapoint_ref = Column(Integer, ForeignKey('raw_market_data.id'), nullable=True)
    data_age_seconds = Column(Integer, nullable=True)
    sources = Column(JSON, nullable=True)  # List of checked sources & timestamps
    verification_status = Column(String(64), nullable=True)  # 'ok', 'variance_flag', 'missing'
    fallback_level = Column(Integer, default=0)
    trust_contrib = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    datapoint = relationship('RawMarketData', backref='audit_logs')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'section': self.section,
            'datapoint_ref': self.datapoint_ref,
            'data_age_seconds': self.data_age_seconds,
            'sources': self.sources or {},
            'verification_status': self.verification_status,
            'fallback_level': self.fallback_level,
            'trust_contrib': self.trust_contrib,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
