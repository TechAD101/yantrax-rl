#!/bin/bash

# YantraX RL Deployment Script
# Author: TechAD101
# Created: August 28, 2025
# Description: Automated deployment script for YantraX RL backend and frontend services

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging setup
LOG_DIR="logs"
DEPLOY_LOG="${LOG_DIR}/deployment_$(date +%Y%m%d_%H%M%S).log"
SERVICE_LOG_DIR="${LOG_DIR}/services"

# Create log directories
mkdir -p "$LOG_DIR" "$SERVICE_LOG_DIR"

# Logging function
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

# Cleanup function for graceful shutdown
cleanup() {
    log_warning "Cleaning up deployment processes..."
    # Kill background processes if they exist
    jobs -p | xargs -r kill 2>/dev/null || true
    log_info "Cleanup completed"
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Main deployment function
main() {
    log_info "=== YantraX RL Deployment Started ==="
    log_info "Deployment log: $DEPLOY_LOG"
    
    # Step 1: Make script executable
    log_info "Making deployment script executable..."
    chmod +x "$0"
    log_success "Script is now executable"
    
    # Step 2: Check system requirements
    log_info "Checking system requirements..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | cut -d" " -f2)
    log_info "Python version: $python_version"
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed. Please install pip and try again."
        exit 1
    fi
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found in project root"
        exit 1
    fi
    
    log_success "System requirements check passed"
    
    # Step 3: Set up Python virtual environment
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
    
    # Step 4: Upgrade pip and install dependencies
    log_info "Upgrading pip..."
    pip install --upgrade pip >> "$DEPLOY_LOG" 2>&1
    log_success "pip upgraded successfully"
    
    log_info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt >> "$DEPLOY_LOG" 2>&1
    log_success "Dependencies installed successfully"
    
    # Step 5: Check backend and frontend directories
    log_info "Checking project structure..."
    
    if [ ! -d "backend" ]; then
        log_error "backend directory not found"
        exit 1
    fi
    
    if [ ! -d "frontend" ]; then
        log_error "frontend directory not found"
        exit 1
    fi
    
    log_success "Project structure validated"
    
    # Step 6: Set up environment variables
    log_info "Setting up environment variables..."
    
    # Load .env file if it exists
    if [ -f ".env" ]; then
        log_info "Loading environment variables from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
        log_success "Environment variables loaded"
    else
        log_warning ".env file not found, using default settings"
    fi
    
    # Step 7: Start backend services
    log_info "Starting backend services..."
    
    # Backend service on port 5000
    if [ -f "backend/app.py" ]; then
        log_info "Starting main backend service on port 5000..."
        cd backend
        nohup python app.py > "../$SERVICE_LOG_DIR/backend_5000.log" 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > "../$SERVICE_LOG_DIR/backend_5000.pid"
        cd ..
        log_success "Backend service started on port 5000 (PID: $BACKEND_PID)"
    else
        log_warning "backend/app.py not found, skipping port 5000 service"
    fi
    
    # Additional backend service on port 5001
    if [ -f "backend/api_service.py" ]; then
        log_info "Starting API service on port 5001..."
        cd backend
        nohup python api_service.py > "../$SERVICE_LOG_DIR/backend_5001.log" 2>&1 &
        API_PID=$!
        echo $API_PID > "../$SERVICE_LOG_DIR/backend_5001.pid"
        cd ..
        log_success "API service started on port 5001 (PID: $API_PID)"
    else
        log_warning "backend/api_service.py not found, skipping port 5001 service"
    fi
    
    # Step 8: Start frontend service
    log_info "Starting frontend service..."
    
    # Frontend service on port 5002
    if [ -f "frontend/app.py" ]; then
        log_info "Starting frontend service on port 5002..."
        cd frontend
        nohup python app.py > "../$SERVICE_LOG_DIR/frontend_5002.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "../$SERVICE_LOG_DIR/frontend_5002.pid"
        cd ..
        log_success "Frontend service started on port 5002 (PID: $FRONTEND_PID)"
    elif [ -f "frontend/server.py" ]; then
        log_info "Starting frontend server on port 5002..."
        cd frontend
        nohup python server.py > "../$SERVICE_LOG_DIR/frontend_5002.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "../$SERVICE_LOG_DIR/frontend_5002.pid"
        cd ..
        log_success "Frontend server started on port 5002 (PID: $FRONTEND_PID)"
    else
        log_warning "frontend/app.py or frontend/server.py not found, skipping frontend service"
    fi
    
    # Step 9: Wait for services to start and verify
    log_info "Waiting for services to initialize..."
    sleep 5
    
    # Check if services are running
    log_info "Verifying service status..."
    
    services_running=0
    
    # Check port 5000
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":5000 "; then
            log_success "Service on port 5000 is running"
            services_running=$((services_running + 1))
        else
            log_warning "Port 5000 service may not be running"
        fi
        
        # Check port 5001
        if netstat -tuln | grep -q ":5001 "; then
            log_success "Service on port 5001 is running"
            services_running=$((services_running + 1))
        else
            log_warning "Port 5001 service may not be running"
        fi
        
        # Check port 5002
        if netstat -tuln | grep -q ":5002 "; then
            log_success "Service on port 5002 is running"
            services_running=$((services_running + 1))
        else
            log_warning "Port 5002 service may not be running"
        fi
    else
        log_warning "netstat not available, skipping port verification"
    fi
    
    # Step 10: Create service management scripts
    log_info "Creating service management scripts..."
    
    # Create stop script
    cat > stop_services.sh << 'EOF'
#!/bin/bash
# Stop all YantraX RL services

echo "Stopping YantraX RL services..."

# Stop services using PID files
for pidfile in logs/services/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service_name=$(basename "$pidfile" .pid)
        echo "Stopping $service_name (PID: $pid)..."
        kill "$pid" 2>/dev/null || echo "Process $pid not found"
        rm -f "$pidfile"
    fi
done

echo "All services stopped"
EOF
    
    chmod +x stop_services.sh
    log_success "Created stop_services.sh"
    
    # Create status script
    cat > status_services.sh << 'EOF'
#!/bin/bash
# Check status of YantraX RL services

echo "YantraX RL Service Status:"
echo "========================="

# Check each service
for pidfile in logs/services/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service_name=$(basename "$pidfile" .pid)
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "✓ $service_name (PID: $pid) - RUNNING"
        else
            echo "✗ $service_name (PID: $pid) - NOT RUNNING"
        fi
    fi
done

# Check ports
echo "
Port Status:"
echo "============"
for port in 5000 5001 5002; do
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            echo "✓ Port $port - LISTENING"
        else
            echo "✗ Port $port - NOT LISTENING"
        fi
    else
        echo "? Port $port - Cannot check (netstat not available)"
    fi
done
EOF
    
    chmod +x status_services.sh
    log_success "Created status_services.sh"
    
    # Step 11: Final deployment summary
    log_success "=== YantraX RL Deployment Completed ==="
    echo ""
    echo -e "${GREEN}🚀 Deployment Summary:${NC}"
    echo -e "${BLUE}├── Services started: $services_running${NC}"
    echo -e "${BLUE}├── Logs directory: $LOG_DIR${NC}"
    echo -e "${BLUE}├── Service logs: $SERVICE_LOG_DIR${NC}"
    echo -e "${BLUE}├── Deployment log: $DEPLOY_LOG${NC}"
    echo ""
    echo -e "${YELLOW}📋 Available commands:${NC}"
    echo -e "${BLUE}├── Check status: ./status_services.sh${NC}"
    echo -e "${BLUE}├── Stop services: ./stop_services.sh${NC}"
    echo -e "${BLUE}└── View logs: tail -f $SERVICE_LOG_DIR/*.log${NC}"
    echo ""
    echo -e "${GREEN}✅ YantraX RL is now running!${NC}"
    echo -e "${BLUE}Access the services at:${NC}"
    echo -e "${BLUE}├── Backend (Port 5000): http://https://symmetrical-zebra-x5xjjpjr79q5fp4g6-5000.app.github.dev${NC}"
    echo -e "${BLUE}├── API Service (Port 5001): http://localhost:5001${NC}"
    echo -e "${BLUE}└── Frontend (Port 5002): http://localhost:5002${NC}"
    
    log_info "Deployment completed successfully. Services are running in background."
}

# Run main function
main "$@"
