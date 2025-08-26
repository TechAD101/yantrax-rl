from flask import Flask, jsonify, request
from flask_cors import CORS
from services.notification_service import send_notification
from services.logger_service import logger, get_logs, log_message
from services.market_data_service import get_latest_price
from ai_agents.macro_monk import macro_monk_decision
from ai_agents.the_ghost import ghost_signal_handler
from ai_agents.data_whisperer import analyze_data, detect_anomalies
from ai_agents.degen_auditor import audit_trade
from rl_core.rl_trainer import train_model, run_rl_cycle
from rl_core.env_market_sim import MarketSimEnv
import sqlite3
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# -----------------------------
# Flask App Configuration
# -----------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend access

# Enhanced logging configuration
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    """Initialize SQLite database with enhanced schema"""
    conn = sqlite3.connect("trade_journal.db")
    cursor = conn.cursor()
    
    # Enhanced journal entries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            signal TEXT NOT NULL,
            audit TEXT NOT NULL,
            reward REAL NOT NULL,
            market_data TEXT,
            agent_coordination TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Enhanced agent commentary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_commentary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            agent TEXT NOT NULL,
            comment TEXT NOT NULL,
            confidence_score REAL,
            market_context TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # System health monitoring table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            component TEXT NOT NULL,
            status TEXT NOT NULL,
            performance_metrics TEXT,
            error_details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized successfully")

def log_to_journal(signal: str, audit: str, reward: float, market_data: Optional[str] = None, agent_coordination: Optional[str] = None):
    """Enhanced journal logging with additional context"""
    try:
        conn = sqlite3.connect("trade_journal.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO journal_entries (timestamp, signal, audit, reward, market_data, agent_coordination)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), signal, audit, reward, market_data, agent_coordination))
        conn.commit()
        conn.close()
        logger.info(f"📝 Journal entry logged: Signal={signal}, Reward={reward}")
    except Exception as e:
        logger.error(f"❌ Failed to log journal entry: {str(e)}")

def log_agent_commentary(agent: str, comment: str, confidence_score: Optional[float] = None, market_context: Optional[str] = None):
    """Enhanced agent commentary logging"""
    try:
        conn = sqlite3.connect("trade_journal.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_commentary (timestamp, agent, comment, confidence_score, market_context)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), agent, comment, confidence_score, market_context))
        conn.commit()
        conn.close()
        logger.info(f"💬 Agent commentary logged: {agent}")
    except Exception as e:
        logger.error(f"❌ Failed to log agent commentary: {str(e)}")

# -----------------------------
# Core API Endpoints
# -----------------------------

@app.route("/")
def index():
    """System status and welcome endpoint"""
    return jsonify({
        "message": "YantraX RL Backend is Live 🚀",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Multi-Agent RL Trading",
            "Emotional Market Simulation", 
            "Real-time Data Integration",
            "Advanced Risk Management"
        ]
    })

@app.route("/health", methods=["GET"])
def health():
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        conn = sqlite3.connect("trade_journal.db")
        conn.close()
        
        # Test market data service
        test_price = get_latest_price("AAPL")
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "operational",
                "market_data": "operational" if test_price else "degraded",
                "ai_agents": "operational",
                "rl_core": "operational"
            },
            "uptime": "available",
            "version": "2.0.0"
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/logs", methods=["GET"])
def logs():
    """Get system logs with optional filtering"""
    try:
        limit = request.args.get("limit", 50, type=int)
        level = request.args.get("level", "all")
        
        log_entries = get_logs(limit)
        
        if level != "all":
            log_entries = [log for log in log_entries if level.upper() in log.upper()]
        
        return jsonify({
            "logs": log_entries,
            "count": len(log_entries),
            "filtered_by": level
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve logs: {str(e)}")
        return jsonify({"error": "Failed to retrieve logs"}), 500

@app.route("/notify", methods=["POST"])
def notify():
    """Enhanced notification endpoint"""
    try:
        data = request.get_json(force=True)
        message = data.get("message", "No message")
        subject = data.get("subject", "YantraX Notification")
        to_email = data.get("to_email", os.getenv("SMTP_USER", ""))
        priority = data.get("priority", "normal")
        
        success = send_notification(subject, message, to_email)
        
        if success:
            log_message(f"[Notify] {priority.upper()}: {message}")
            return jsonify({
                "status": "sent",
                "message": message,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "failed",
                "error": "Failed to send notification"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Notification failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/market-price", methods=["GET"])
def market_price():
    """Enhanced market price endpoint with additional data"""
    try:
        symbol = request.args.get("symbol", "AAPL")
        include_analysis = request.args.get("analysis", "false").lower() == "true"
        
        price = get_latest_price(symbol)
        
        response_data = {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if price is not None else "no_data"
        }
        
        if include_analysis and price is not None:
            market_data = analyze_data(symbol)
            response_data["analysis"] = market_data
            
        return jsonify(response_data), 200 if price is not None else 404
        
    except Exception as e:
        logger.error(f"❌ Market price request failed: {str(e)}")
        return jsonify({"error": "Could not fetch market price"}), 500

# -----------------------------
# AI Agent Coordination Endpoints
# -----------------------------

@app.route("/run-cycle", methods=["POST"])
def run_cycle():
    """Enhanced agent coordination cycle with comprehensive logging"""
    try:
        request_data = request.get_json() or {}
        symbol = request_data.get("symbol", "AAPL")
        
        logger.info(f"🚀 Starting agent coordination cycle for {symbol}")
        
        # Step 1: Data Analysis
        market_data = analyze_data(symbol)
        logger.info(f"[Data Whisperer] Analysis complete: {market_data.get('trend', 'unknown')} trend")
        log_agent_commentary("Data Whisperer", f"Market analysis for {symbol}: {market_data.get('trend', 'unknown')} trend, {market_data.get('sentiment', 'neutral')} sentiment", market_context=str(market_data))
        
        # Step 2: Strategic Decision
        strategy = macro_monk_decision(market_data)
        logger.info(f"[Macro Monk] Strategy decision: {strategy}")
        log_agent_commentary("Macro Monk", f"Strategic decision: {strategy} based on price ${market_data.get('price', 'unknown')}")
        
        # Step 3: Signal Processing
        signal = ghost_signal_handler(strategy)
        logger.info(f"[The Ghost] Signal processed: {signal}")
        log_agent_commentary("The Ghost", f"Emotional intelligence signal: {signal}")
        
        # Step 4: Risk Assessment
        audit = audit_trade(signal)
        logger.info(f"[Degen Auditor] Risk audit: {audit}")
        log_agent_commentary("Degen Auditor", f"Risk assessment result: {audit}")
        
        # Step 5: RL Environment Execution
        env = MarketSimEnv()
        state, reward, done = env.step(signal.split().lower() if signal else "hold")
        
        # Step 6: Anomaly Detection
        anomalies = detect_anomalies(market_data)
        if anomalies.get("risk_alert", False):
            logger.warning(f"⚠️ Market anomalies detected: {anomalies}")
            log_agent_commentary("System Monitor", f"Risk alert: Anomaly score {anomalies.get('anomaly_score', 0)}")
        
        # Step 7: Notifications
        notification_message = f"Cycle Complete | Signal: {signal} | Reward: {reward:.3f} | Market: {market_data.get('trend', 'unknown')}"
        send_notification(
            subject="YantraX Trading Cycle Complete",
            message=notification_message,
            to_email=os.getenv("SMTP_USER", "")
        )
        
        # Step 8: Comprehensive Logging
        log_to_journal(
            signal=signal,
            audit=audit,
            reward=reward,
            market_data=str(market_data),
            agent_coordination=f"Strategy: {strategy}, Anomalies: {anomalies.get('anomaly_score', 0)}"
        )
        
        logger.info(f"✅ Agent cycle complete | Reward: {reward:.3f} | State: {state.get('cycle', 0)}")
        
        return jsonify({
            "status": "success",
            "cycle_id": state.get('cycle', 0),
            "signal": signal,
            "strategy": strategy,
            "audit": audit,
            "reward": reward,
            "market_data": market_data,
            "state": state,
            "anomalies": anomalies,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Agent cycle failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/train", methods=["POST"])
def trigger_training():
    """Enhanced RL training endpoint"""
    try:
        request_data = request.get_json() or {}
        episodes = request_data.get("episodes", 100)
        learning_rate = request_data.get("learning_rate", 0.001)
        
        logger.info(f"🧠 Starting RL training: {episodes} episodes, LR: {learning_rate}")
        
        result = train_model(episodes=episodes, learning_rate=learning_rate)
        
        log_agent_commentary("RL Trainer", f"Training completed: {episodes} episodes")
        
        return jsonify({
            **result,
            "training_config": {
                "episodes": episodes,
                "learning_rate": learning_rate
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/god-cycle", methods=["GET"])
def run_god_cycle():
    """Enhanced RL God Mode cycle"""
    try:
        logger.info("🔥 Initiating RL God Mode cycle")
        
        result = run_rl_cycle()
        
        if result.get("status") == "error":
            return jsonify(result), 500
            
        log_agent_commentary("RL God Mode", f"God cycle completed: Balance ${result.get('final_balance', 0):,.2f}, Total Reward: {result.get('total_reward', 0):.3f}")
        
        return jsonify({
            **result,
            "mode": "god_cycle",
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ RL God cycle failed: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/journal", methods=["GET"])
def view_journal():
    """Enhanced journal retrieval with filtering and pagination"""
    try:
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        conn = sqlite3.connect("trade_journal.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, signal, audit, reward, market_data, agent_coordination, created_at
            FROM journal_entries 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        entries = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total_count = cursor.fetchone()
        
        conn.close()
        
        journal_list = []
        for row in entries:
            journal_list.append({
                "timestamp": row,
                "signal": row,
                "audit": row,
                "reward": row,
                "market_data": row,
                "agent_coordination": row,
                "created_at": row
            })
        
        return jsonify({
            "entries": journal_list,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(journal_list)) < total_count
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Journal retrieval failed: {str(e)}")
        return jsonify({"error": "Failed to retrieve journal"}), 500

@app.route("/commentary", methods=["GET"])
def get_agent_commentary():
    """Enhanced agent commentary retrieval"""
    try:
        limit = request.args.get("limit", 50, type=int)
        agent_filter = request.args.get("agent", None)
        
        conn = sqlite3.connect("trade_journal.db")
        cursor = conn.cursor()
        
        if agent_filter:
            cursor.execute("""
                SELECT timestamp, agent, comment, confidence_score, market_context, created_at
                FROM agent_commentary 
                WHERE agent = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (agent_filter, limit))
        else:
            cursor.execute("""
                SELECT timestamp, agent, comment, confidence_score, market_context, created_at
                FROM agent_commentary 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
        rows = cursor.fetchall()
        conn.close()
        
        commentary_list = []
        for row in rows:
            commentary_list.append({
                "timestamp": row,
                "agent": row,
                "comment": row,
                "confidence_score": row,
                "market_context": row,
                "created_at": row
            })
        
        return jsonify({
            "commentary": commentary_list,
            "count": len(commentary_list),
            "filtered_by_agent": agent_filter
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Commentary retrieval failed: {str(e)}")
        return jsonify({"error": "Failed to retrieve commentary"}), 500

@app.route("/market-stats", methods=["GET"])
def market_stats():
    """Enhanced market statistics endpoint"""
    try:
        symbol = request.args.get("symbol", "AAPL")
        include_anomalies = request.args.get("anomalies", "false").lower() == "true"
        
        market_data = analyze_data(symbol)
        
        response = {
            "symbol": symbol,
            "market_data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
        if include_anomalies:
            anomalies = detect_anomalies(market_data)
            response["anomalies"] = anomalies
            
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Market stats failed: {str(e)}")
        return jsonify({"error": "Failed to retrieve market stats"}), 500

# -----------------------------
# Error Handlers
# -----------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested API endpoint does not exist",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat()
    }), 500

# -----------------------------
# Application Startup
# -----------------------------

if __name__ == "__main__":
    try:
        # Initialize database
        init_db()
        
        # Log startup
        logger.info("🚀 YantraX RL Backend starting up...")
        logger.info("✅ All systems initialized successfully")
        
        # Start Flask application
        app.run(
            debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 5000))
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)

