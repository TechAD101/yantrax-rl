# YantraX API Documentation

## Overview
YantraX is an AI-driven trading platform with institutional-grade analytics, multi-persona reasoning, and paper trading capabilities.

---

## Authentication

### Register User
**POST** `/api/auth/register`

**Request:**
```json
{
  "username": "trader123",
  "email": "trader@example.com",
  "password": "secure_password"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "trader123",
    "email": "trader@example.com",
    "created_at": "2026-02-01T00:00:00"
  },
  "message": "User registered"
}
```

### Login User
**POST** `/api/auth/login`

**Request:**
```json
{
  "username": "trader123",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "trader123",
    "email": "trader@example.com",
    "created_at": "2026-02-01T00:00:00"
  },
  "message": "Logged in"
}
```

### Get User Info
**GET** `/api/auth/user/<user_id>`

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "trader123",
    "email": "trader@example.com"
  }
}
```

---

## Portfolio Management

### Create Portfolio
**POST** `/api/portfolio`

**Request:**
```json
{
  "name": "Momentum Portfolio",
  "owner_id": 1,
  "risk_profile": "moderate",
  "initial_capital": 100000.0,
  "strategy": {
    "name": "Momentum Strategy",
    "archetype": "quant",
    "params": {"window": 20}
  }
}
```

**Response (201):**
```json
{
  "portfolio": {
    "id": 1,
    "name": "Momentum Portfolio",
    "owner_id": 1,
    "risk_profile": "moderate",
    "initial_capital": 100000.0,
    "current_value": 100000.0,
    "created_at": "2026-02-01T00:00:00",
    "positions": []
  }
}
```

### Get Portfolio by ID
**GET** `/api/portfolio/<portfolio_id>`

**Response (200):**
```json
{
  "portfolio": {
    "id": 1,
    "name": "Momentum Portfolio",
    "positions": [
      {"symbol": "AAPL", "quantity": 100, "avg_price": 175.50}
    ]
  }
}
```

---

## Strategy Management

### Publish Strategy
**POST** `/api/strategy/publish`

**Request:**
```json
{
  "name": "Momentum v0.1",
  "description": "High-frequency momentum capture",
  "archetype": "quant",
  "params": {"window": 20, "threshold": 0.02},
  "metrics": {"win_rate": 0.65, "sharpe": 1.25}
}
```

**Response (201):**
```json
{
  "strategy": {
    "id": 1,
    "name": "Momentum v0.1",
    "published": true,
    "metrics": {"win_rate": 0.65, "sharpe": 1.25}
  }
}
```

### List Strategies
**GET** `/api/strategy/list`

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 10)
- `archetype` (string): Filter by archetype (quant, warren, degen)
- `q` (string): Search by name/description
- `min_sharpe` (float): Minimum Sharpe ratio
- `min_win_rate` (float): Minimum win rate
- `sort_by` (string): Sort field (sharpe, win_rate, name)
- `order` (string): Sort order (asc, desc)

**Response (200):**
```json
{
  "strategies": [...],
  "page": 1,
  "per_page": 10,
  "total": 50,
  "total_pages": 5
}
```

### Get Top Strategies
**GET** `/api/strategy/top?limit=10&metric=sharpe&order=desc`

**Response (200):**
```json
{
  "strategies": [
    {
      "id": 1,
      "name": "Momentum v0.1",
      "metrics": {"sharpe": 1.8, "win_rate": 0.72}
    }
  ]
}
```

### Get Strategy by ID
**GET** `/api/strategy/<strategy_id>`

**Response (200):**
```json
{
  "strategy": {
    "id": 1,
    "name": "Momentum v0.1",
    "description": "High-frequency momentum capture",
    "archetype": "quant",
    "published": true,
    "metrics": {"win_rate": 0.65, "sharpe": 1.25}
  }
}
```

---

## Backtesting

### Run Backtest
**POST** `/api/backtest`

**Request:**
```json
{
  "strategy_id": 1,
  "symbol": "AAPL",
  "days": 30,
  "initial_capital": 100000
}
```

**Response (200):**
```json
{
  "backtest": {
    "strategy_id": 1,
    "symbol": "AAPL",
    "initial_capital": 100000,
    "final_value": 115432.50,
    "total_return": 15.43,
    "win_rate": 68.5,
    "total_trades": 13,
    "trades": [
      {"action": "BUY", "price": 175.50, "qty": 455.17, "date": "2026-01-02T00:00:00"},
      {"action": "SELL", "price": 182.30, "qty": 455.17, "pnl": 3101.23, "date": "2026-01-10T00:00:00"}
    ]
  }
}
```

### Get Backtest Results
**GET** `/api/backtest/results?limit=10`

**Response (200):**
```json
{
  "results": [...]
}
```

---

## Order Manager (Paper Trading)

### Create Order
**POST** `/api/orders`

**Request:**
```json
{
  "symbol": "AAPL",
  "usd": 5000
}
```

**Response (201):**
```json
{
  "order": {
    "id": 1,
    "symbol": "AAPL",
    "usd": 5000,
    "quantity": 28.57,
    "price": 174.90,
    "status": "filled",
    "created_at": "2026-02-01T00:00:00",
    "executed_at": "2026-02-01T00:00:00"
  }
}
```

### List Orders
**GET** `/api/orders?limit=100`

**Response (200):**
```json
{
  "orders": [
    {
      "id": 1,
      "symbol": "AAPL",
      "usd": 5000,
      "quantity": 28.57,
      "status": "filled"
    }
  ]
}
```

### Get Order by ID
**GET** `/api/orders/<order_id>`

**Response (200):**
```json
{
  "order": {
    "id": 1,
    "symbol": "AAPL",
    "usd": 5000,
    "quantity": 28.57,
    "status": "filled"
  }
}
```

---

## Memecoin Engine (Prototype)

### Scan Market
**POST** `/api/memecoin/scan`

**Request:**
```json
{
  "symbols": ["DOGE", "SHIB", "PEPE"]
}
```

**Response (200):**
```json
{
  "results": [
    {
      "symbol": "DOGE",
      "social": 850.5,
      "mentions": 234,
      "price": 0.0847,
      "momentum": 0.123,
      "degen_score": 45.67,
      "scanned_at": 1706779200
    }
  ]
}
```

### Get Top Memecoins
**GET** `/api/memecoin/top?limit=10`

**Response (200):**
```json
{
  "memecoins": [
    {
      "id": 1,
      "symbol": "DOGE",
      "score": 45.67,
      "metadata": {
        "social": 850.5,
        "mentions": 234,
        "price": 0.0847,
        "momentum": 0.123
      }
    }
  ]
}
```

### Simulate Memecoin Trade
**POST** `/api/memecoin/simulate`

**Request:**
```json
{
  "symbol": "DOGE",
  "usd": 500
}
```

**Response (200):**
```json
{
  "result": {
    "symbol": "DOGE",
    "price": 0.0847,
    "usd": 500,
    "quantity": 5900.47
  }
}
```

---

## Market Data & Analysis

### Get Verified Price
**GET** `/api/data/price-verified?symbol=AAPL`

**Response (200):**
```json
{
  "symbol": "AAPL",
  "price": 175.50,
  "source": "multi-provider",
  "confidence": 0.95
}
```

### Get Verification Stats
**GET** `/api/data/verification-stats`

**Response (200):**
```json
{
  "statistics": {
    "total_checks": 1000,
    "consensus_rate": 0.98,
    "active_providers": 3
  }
}
```

---

## Trade Validation

### Validate Trade
**POST** `/api/trade/validate`

**Request:**
```json
{
  "trade": {
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 100,
    "price": 175.50
  },
  "market_context": {
    "volatility": 0.18,
    "trend": "bullish"
  }
}
```

**Response (200):**
```json
{
  "symbol": "AAPL",
  "valid": true,
  "confidence": 0.88,
  "checks": {
    "market_hours": true,
    "volatility_check": true,
    "position_size": true
  }
}
```

### Get Validation Stats
**GET** `/api/trade/validation-stats`

**Response (200):**
```json
{
  "statistics": {
    "total_validations": 5000,
    "approved_rate": 0.92,
    "avg_confidence": 0.85
  }
}
```

---

## AI Firm & Personas

### Get Warren Persona Analysis
**POST** `/api/ai-firm/personas/warren`

**Request:**
```json
{
  "symbol": "AAPL"
}
```

**Response (200):**
```json
{
  "warren_analysis": {
    "recommendation": "BUY",
    "confidence": 0.88,
    "reasoning": "Based on fundamental screening of AAPL..."
  },
  "philosophy": "Rule No. 1: Never lose money..."
}
```

### Get Cathie Persona Analysis
**POST** `/api/ai-firm/personas/cathie`

**Request:**
```json
{
  "symbol": "NVDA"
}
```

**Response (200):**
```json
{
  "cathie_analysis": {
    "recommendation": "BUY",
    "confidence": 0.91,
    "reasoning": "Disruption potential for NVDA is accelerating..."
  }
}
```

---

## Error Responses

**400 Bad Request:**
```json
{"error": "Missing required fields"}
```

**401 Unauthorized:**
```json
{"error": "Invalid credentials"}
```

**404 Not Found:**
```json
{"error": "Resource not found"}
```

**500 Server Error:**
```json
{"error": "Internal server error"}
```

---

## Status Codes

- `200` OK
- `201` Created
- `400` Bad Request
- `401` Unauthorized
- `404` Not Found
- `500` Internal Server Error

---

## Base URL
- Development: `http://localhost:5000`
- Production: `https://yantrax-backend.onrender.com`

---

## Pagination

Most list endpoints support pagination:
- `page` (int): Page number (1-indexed)
- `per_page` (int): Items per page (default: 10)
- `total_pages` (int): Total number of pages

Example: `GET /api/strategy/list?page=2&per_page=20`

---

## Rate Limiting

No rate limiting currently enforced. Recommended: 100 requests/minute per user.

---

## Versioning

Current API Version: `v1` (no prefix, implied)

Future versions will use `/api/v2/...` format.
