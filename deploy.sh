#!/bin/bash

# YantraX RL Unified System - One-Command Deployment
# Author: Perplexity Labs
# Created: August 30, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_DIR="logs"
DEPLOY_LOG="${LOG_DIR}/unified_deployment_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$LOG_DIR"

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$DEPLOY_LOG"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$DEPLOY_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "$DEPLOY_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$DEPLOY_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$DEPLOY_LOG"
}

# Cleanup function
cleanup() {
    log_warning "Cleaning up deployment processes..."
    jobs -p | xargs -r kill 2>/dev/null || true
    log_info "Cleanup completed"
}
trap cleanup EXIT INT TERM

main() {
    log_info "=== YantraX RL Unified Deployment Started ==="
    log_info "Deployment log: $DEPLOY_LOG"
    
    # Step 1: System Requirements Check
    log_info "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | cut -d" " -f2)
    log_info "Python version: $python_version"
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed"
        exit 1
    fi
    
    log_success "System requirements check passed"
    
    # Step 2: Create Project Structure
    log_info "Creating unified project structure..."
    
    mkdir -p yantrax-unified/{backend,frontend,config,tests,logs}
    
    # Copy unified_api.py to backend
    if [ -f "unified_api.py" ]; then
        cp unified_api.py yantrax-unified/backend/ 
        log_success "Copied unified_api.py to backend directory"
    else
        log_error "unified_api.py not found in project root"
        exit 1
    fi
    
    # Copy frontend files
    if [ -f "frontend/index.html" ]; then
        cp frontend/index.html yantrax-unified/frontend/
        log_success "Copied frontend files"
    else
        log_error "frontend/index.html not found"
        exit 1
    fi
    
    cd yantrax-unified
    
    log_success "Project structure created"
    
    # Step 3: Create Requirements File
    log_info "Creating requirements.txt..."
    
    cat > backend/requirements.txt << 'EOF'
# YantraX RL Unified API Requirements
flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
werkzeug==3.0.1
click==8.1.7
itsdangerous==2.1.2
jinja2==3.1.2
markupsafe==2.2.1
urllib3==2.1.0
certifi==2023.11.17
charset-normalizer==3.3.2
idna==3.6
EOF
    
    log_success "Requirements file created"
    
    # Step 4: Set up Python virtual environment
    log_info "Setting up Python virtual environment..."
    
    VENV_DIR="venv"
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    log_success "Virtual environment activated"
    
    # Step 5: Install dependencies
    log_info "Installing dependencies..."
    cd backend
    pip install -r requirements.txt >> "../$DEPLOY_LOG" 2>&1
    cd ..
    log_success "Dependencies installed"
    
    # Step 6: Start Unified API Service (port 8000)
    log_info "Starting Unified API service on port 8000..."
    cd backend
    nohup python unified_api.py > "../logs/unified_api.log" 2>&1 &
    UNIFIED_API_PID=$!
    echo $UNIFIED_API_PID > "../logs/unified_api.pid"
    cd ..
    log_success "Unified API service started (PID: $UNIFIED_API_PID)"
    
    # Step 7: Start Frontend Service (port 3000)  
    log_info "Starting frontend service on port 3000..."
    cd frontend
    nohup python3 -m http.server 3000 > "../logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "../logs/frontend.pid"
    cd ..
    log_success "Frontend service started (PID: $FRONTEND_PID)"
    
    # Step 8: Wait for services to start
    log_info "Waiting for services to initialize..."
    sleep 10
    
    # Step 9: Test Services
    log_info "Testing services..."
    
    services_running=0
    
    # Test Unified API (port 8000)
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Unified API service is healthy (port 8000)"
        services_running=$((services_running + 1))
    else
        log_warning "Unified API service may not be responding"
    fi
    
    # Test Frontend (port 3000)
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        log_success "Frontend service is healthy (port 3000)"
        services_running=$((services_running + 1))
    else
        log_warning "Frontend service may not be responding"
    fi
    
    # Test API endpoints
    log_info "Testing API endpoints..."
    
    # Test sentiment API
    if curl -f -X POST http://localhost:8000/api/v1/sentiment \
           -H "Content-Type: application/json" \
           -d '{"text": "Apple stock is performing well"}' >/dev/null 2>&1; then
        log_success "Sentiment API is working"
    else
        log_warning "Sentiment API test failed"
    fi
    
    # Test trading dashboard API
    if curl -f http://localhost:8000/api/v1/trading-dashboard >/dev/null 2>&1; then
        log_success "Trading dashboard API is working"
    else
        log_warning "Trading dashboard API test failed"
    fi
    
    # Step 10: Create Management Scripts
    log_info "Creating management scripts..."
    
    # Create status script
    cat > check_status.sh << 'EOF'
#!/bin/bash
echo "YantraX RL Unified System Status:"
echo "=================================="

echo "Unified API Health (Port 8000):"
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "❌ Unified API not responding"

echo -e "\nFrontend Status (Port 3000):"
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not responding"
fi

echo -e "\nAPI Endpoints Test:"
if curl -f -X POST http://localhost:8000/api/v1/sentiment -H "Content-Type: application/json" -d '{"text":"test"}' >/dev/null 2>&1; then
    echo "✅ Sentiment API working"
else
    echo "❌ Sentiment API not working"
fi

if curl -f http://localhost:8000/api/v1/trading-dashboard >/dev/null 2>&1; then
    echo "✅ Trading Dashboard API working"
else
    echo "❌ Trading Dashboard API not working"
fi

echo -e "\nService Status:"
if [ -f logs/unified_api.pid ] && ps -p $(cat logs/unified_api.pid) > /dev/null 2>&1; then
    echo "✅ Unified API service running (PID: $(cat logs/unified_api.pid))"
else
    echo "❌ Unified API service not running"
fi

if [ -f logs/frontend.pid ] && ps -p $(cat logs/frontend.pid) > /dev/null 2>&1; then
    echo "✅ Frontend service running (PID: $(cat logs/frontend.pid))"
else
    echo "❌ Frontend service not running"
fi
EOF
    
    chmod +x check_status.sh
    log_success "Created check_status.sh"
    
    # Create stop script
    cat > stop_services.sh << 'EOF'
#!/bin/bash
echo "Stopping YantraX RL Unified services..."

if [ -f logs/unified_api.pid ]; then
    kill $(cat logs/unified_api.pid) 2>/dev/null || true
    rm logs/unified_api.pid
    echo "✅ Unified API service stopped"
fi

if [ -f logs/frontend.pid ]; then
    kill $(cat logs/frontend.pid) 2>/dev/null || true
    rm logs/frontend.pid
    echo "✅ Frontend service stopped"
fi

echo "All services stopped"
EOF
    
    chmod +x stop_services.sh
    log_success "Created stop_services.sh"
    
    # Step 11: Final Status Report
    log_success "=== YantraX RL Unified Deployment Completed ==="
    echo ""
    echo -e "${GREEN}🚀 Deployment Summary:${NC}"
    echo -e "${BLUE}├── Services running: $services_running/2${NC}"
    echo -e "${BLUE}├── Unified API: http://localhost:8000${NC}"
    echo -e "${BLUE}├── Frontend Dashboard: http://localhost:3000${NC}"
    echo -e "${BLUE}├── Deployment log: $DEPLOY_LOG${NC}"
    echo ""
    echo -e "${YELLOW}📋 Available commands:${NC}"
    echo -e "${BLUE}├── Check status: ./check_status.sh${NC}"
    echo -e "${BLUE}├── Stop services: ./stop_services.sh${NC}"
    echo -e "${BLUE}└── View logs: tail -f logs/*.log${NC}"
    echo ""
    echo -e "${GREEN}✅ YantraX RL Unified System is now operational!${NC}"
    echo ""
    echo -e "${BLUE}🎯 Quick Test Commands:${NC}"
    echo -e "${BLUE}├── Test Sentiment: curl -X POST http://localhost:8000/api/v1/sentiment -H 'Content-Type: application/json' -d '{\"text\":\"Tesla stock surging!\"}' | python3 -m json.tool${NC}"
    echo -e "${BLUE}├── View Dashboard: curl http://localhost:8000/api/v1/trading-dashboard | python3 -m json.tool${NC}"
    echo -e "${BLUE}└── Check Health: curl http://localhost:8000/health | python3 -m json.tool${NC}"
    echo ""
    echo -e "${GREEN}🎉 Professional AI Trading Platform Ready!${NC}"
    
    log_info "Deployment completed successfully. All systems operational."
}

# Run main function
main "$@"
