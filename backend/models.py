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
    positions = relationship(
        'PortfolioPosition',
        primaryjoin=lambda: Memecoin.symbol == foreign(PortfolioPosition.symbol),
        backref='memecoin',
    )

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


# -------------------- Trade History (Outcome Tracking) --------------------
class TradeHistory(Base):
    """Complete trade history with outcome attribution."""
    __tablename__ = 'trade_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(String(64), nullable=False, index=True)
    outcome_id = Column(String(64), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    symbol = Column(String(32), nullable=False)
    action = Column(String(16), nullable=False)  # BUY, SELL, HOLD
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    commission = Column(Float, nullable=True, default=0.0)
    slippage = Column(Float, nullable=True, default=0.0)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    meta = Column(JSON, nullable=True)  # Full attribution data

    order = relationship('Order')

    __table_args__ = (
        Index('idx_trade_decision', 'decision_id'),
        Index('idx_trade_outcome', 'outcome_id'),
        Index('idx_trade_symbol', 'symbol'),
        Index('idx_trade_timestamp', 'timestamp'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'decision_id': self.decision_id,
            'outcome_id': self.outcome_id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'pnl': self.pnl,
            'commission': self.commission,
            'slippage': self.slippage,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'meta': self.meta or {},
        }


# -------------------- Paper Position Model ---------------------
class PaperPosition(Base):
    """Paper trading position with explicit entry/exit lifecycle."""
    __tablename__ = 'paper_positions'

    id = Column(String(64), primary_key=True)  # e.g., 'pos_abc123'
    decision_id = Column(String(64), nullable=False, index=True)  # Canonical decision_id
    symbol = Column(String(32), nullable=False)
    side = Column(String(16), nullable=False)  # BUY (long), SELL (short)
    quantity = Column(Float, nullable=False)

    # Entry
    entry_order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    entry_fill_id = Column(String(64), nullable=True)
    entry_price = Column(Float, nullable=False)
    entry_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Exit
    exit_order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    exit_fill_id = Column(String(64), nullable=True)
    exit_price = Column(Float, nullable=True)  # NULL until closed
    exit_timestamp = Column(DateTime, nullable=True)  # NULL until closed

    # P&L
    realized_pnl = Column(Float, nullable=True)  # NULL until closed
    commission = Column(Float, nullable=True, default=0.0)
    slippage = Column(Float, nullable=True, default=0.0)
    spread_cost = Column(Float, nullable=True, default=0.0)

    # Status
    status = Column(String(16), nullable=False, default='OPEN')  # OPEN, CLOSED

    # Strategy context
    strategy_id = Column(String(64), nullable=True)
    regime = Column(String(32), nullable=True)
    meta = Column(JSON, nullable=True)

    # Relationships
    entry_order = relationship('Order', foreign_keys=[entry_order_id])
    exit_order = relationship('Order', foreign_keys=[exit_order_id])

    __table_args__ = (
        Index('idx_paper_position_symbol', 'symbol'),
        Index('idx_paper_position_status', 'status'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'decision_id': self.decision_id,
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'entry_order_id': self.entry_order_id,
            'entry_fill_id': self.entry_fill_id,
            'entry_price': self.entry_price,
            'entry_timestamp': self.entry_timestamp.isoformat() if self.entry_timestamp is not None else None,
            'exit_order_id': self.exit_order_id,
            'exit_fill_id': self.exit_fill_id,
            'exit_price': self.exit_price,
            'exit_timestamp': self.exit_timestamp.isoformat() if self.exit_timestamp is not None else None,
            'realized_pnl': self.realized_pnl,
            'commission': self.commission,
            'slippage': self.slippage,
            'spread_cost': self.spread_cost,
            'status': self.status,
            'strategy_id': self.strategy_id,
            'regime': self.regime,
            'meta': self.meta or {},
        }


# -------------------- Outcome Model ---------------------
class Outcome(Base):
    __tablename__ = 'outcomes'

    id = Column(String(64), primary_key=True)  # e.g., 'out_abc123'
    decision_id = Column(String(64), nullable=False, index=True)  # Canonical decision_id
    position_id = Column(String(64), ForeignKey('paper_positions.id'), nullable=True, index=True)
    symbol = Column(String(32), nullable=False)
    action = Column(String(16), nullable=False)  # BUY, SELL
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    commission = Column(Float, nullable=True, default=0.0)
    slippage = Column(Float, nullable=True, default=0.0)
    spread_cost = Column(Float, nullable=True, default=0.0)
    pnl = Column(Float, nullable=False)  # Realized P&L
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)  # close timestamp

    # Relationship to position
    position = relationship('PaperPosition')
    # Relationship to attributions
    attributions = relationship('Attribution', back_populates='outcome')
    # Relationship to learning events
    learning_events = relationship('LearningEvent', back_populates='outcome')

    @property
    def attribution_ids(self):
        return [attr.id for attr in self.attributions]

    @property
    def learning_event_ids(self):
        return [event.id for event in self.learning_events]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'decision_id': self.decision_id,
            'position_id': self.position_id,
            'symbol': self.symbol,
            'action': self.action,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'commission': self.commission,
            'slippage': self.slippage,
            'spread_cost': self.spread_cost,
            'pnl': self.pnl,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


# -------------------- Attribution Model -----------------
class Attribution(Base):
    __tablename__ = 'attributions'

    id = Column(String(64), primary_key=True)  # e.g., 'attr_abc123'
    outcome_id = Column(String(64), ForeignKey('outcomes.id'), nullable=False, index=True)
    component = Column(String(32), nullable=False)  # e.g., 'strategy', 'agent_warren'
    value = Column(Float, nullable=False)  # attributed P&L
    percentage = Column(Float, nullable=False)  # percentage of total P&L
    confidence = Column(Float, nullable=False)  # confidence in attribution
    details = Column(JSON, nullable=True)  # attribution metadata
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to outcome
    outcome = relationship('Outcome')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'outcome_id': self.outcome_id,
            'component': self.component,
            'value': self.value,
            'percentage': self.percentage,
            'confidence': self.confidence,
            'details': self.details or {},
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


# -------------------- LearningEvent Model ---------------
class LearningEvent(Base):
    __tablename__ = 'learning_events'

    id = Column(String(64), primary_key=True)  # e.g., 'learn_abc123'
    outcome_id = Column(String(64), ForeignKey('outcomes.id'), nullable=False, index=True)
    event_type = Column(String(32), nullable=False)  # e.g., 'confidence_update'
    target_type = Column(String(32), nullable=True)  # e.g., 'agent', 'strategy', 'market_regime'
    target_id = Column(String(64), nullable=True)  # e.g., 'warren', 'institutional', 'bull_market'
    old_value = Column(String(256), nullable=True)  # stored as string for flexibility
    new_value = Column(String(256), nullable=True)  # stored as string for flexibility
    event_metadata = Column(JSON, nullable=True)  # additional metadata (renamed from metadata to avoid SQLAlchemy reserved name)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to outcome
    outcome = relationship('Outcome')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'outcome_id': self.outcome_id,
            'event_type': self.event_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'metadata': self.event_metadata or {},
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
