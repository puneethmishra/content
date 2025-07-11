#!/bin/bash

# WhatsApp MCP Dashboard Setup Script
# This script helps you set up the WhatsApp MCP Dashboard quickly

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: $NPM_VERSION"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    elif command_exists python; then
        PYTHON_VERSION=$(python --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python is not installed. Please install Python 3.8+ from https://python.org/"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
    print_success "pip found"
    
    # Check Git
    if command_exists git; then
        GIT_VERSION=$(git --version)
        print_success "Git found: $GIT_VERSION"
    else
        print_error "Git is not installed. Please install Git from https://git-scm.com/"
        exit 1
    fi
    
    # Check Go (optional)
    if command_exists go; then
        GO_VERSION=$(go version)
        print_success "Go found: $GO_VERSION"
    else
        print_warning "Go is not installed. You'll need to install it to run the WhatsApp MCP Server."
        print_warning "Download from: https://go.dev/dl/"
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    $PIP_CMD install --upgrade pip
    print_success "pip upgraded"
}

# Install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    
    cd backend
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Backend dependencies installed"
    else
        print_error "requirements.txt not found in backend directory"
        exit 1
    fi
    
    cd ..
}

# Install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    cd frontend
    
    if [ -f "package.json" ]; then
        npm install
        print_success "Frontend dependencies installed"
    else
        print_error "package.json not found in frontend directory"
        exit 1
    fi
    
    cd ..
}

# Setup environment file
setup_env_file() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.template" ]; then
            cp backend/.env.template backend/.env
            print_success "Environment file created from template"
            print_warning "Please edit backend/.env with your configuration"
        else
            print_error ".env.template not found"
            exit 1
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Backend startup script
    cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "Starting WhatsApp MCP Dashboard Backend..."
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x start_backend.sh
    
    # Frontend startup script
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "Starting WhatsApp MCP Dashboard Frontend..."
cd frontend
npm start
EOF
    chmod +x start_frontend.sh
    
    # Combined startup script
    cat > start_dashboard.sh << 'EOF'
#!/bin/bash
echo "Starting WhatsApp MCP Dashboard..."
echo "Starting backend in background..."
./start_backend.sh &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 10

echo "Starting frontend..."
./start_frontend.sh &
FRONTEND_PID=$!

echo "Dashboard starting..."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access the dashboard at: http://localhost:3000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF
    chmod +x start_dashboard.sh
    
    print_success "Startup scripts created"
}

# Setup WhatsApp MCP Server
setup_whatsapp_mcp() {
    print_status "Setting up WhatsApp MCP Server..."
    
    if [ ! -d "whatsapp-mcp" ]; then
        print_status "Cloning WhatsApp MCP Server..."
        git clone https://github.com/lharries/whatsapp-mcp.git
        print_success "WhatsApp MCP Server cloned"
    else
        print_warning "WhatsApp MCP Server directory already exists"
    fi
    
    if command_exists go; then
        print_status "Building WhatsApp MCP Server..."
        cd whatsapp-mcp/whatsapp-bridge
        go mod tidy
        print_success "WhatsApp MCP Server dependencies installed"
        cd ../..
    else
        print_warning "Go not found. Please install Go to build the WhatsApp MCP Server"
    fi
}

# Create WhatsApp MCP startup script
create_whatsapp_script() {
    print_status "Creating WhatsApp MCP startup script..."
    
    cat > start_whatsapp_mcp.sh << 'EOF'
#!/bin/bash
echo "Starting WhatsApp MCP Server..."
echo "You will need to scan the QR code with your WhatsApp mobile app"
echo ""
cd whatsapp-mcp/whatsapp-bridge
go run main.go
EOF
    chmod +x start_whatsapp_mcp.sh
    
    print_success "WhatsApp MCP startup script created"
}

# Display final instructions
show_final_instructions() {
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Edit backend/.env with your configuration (API keys, business info, etc.)"
    echo "2. Start the WhatsApp MCP Server: ./start_whatsapp_mcp.sh"
    echo "3. Scan the QR code with your WhatsApp mobile app"
    echo "4. Start the dashboard: ./start_dashboard.sh"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo "• Dashboard: http://localhost:3000"
    echo "• API Documentation: http://localhost:8000/docs"
    echo "• Backend API: http://localhost:8000"
    echo ""
    echo -e "${BLUE}Startup Scripts Created:${NC}"
    echo "• ./start_whatsapp_mcp.sh - Start WhatsApp MCP Server"
    echo "• ./start_backend.sh - Start backend only"
    echo "• ./start_frontend.sh - Start frontend only"
    echo "• ./start_dashboard.sh - Start both backend and frontend"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo "• Make sure to configure your .env file before starting"
    echo "• The WhatsApp MCP Server must be running for the dashboard to work"
    echo "• For AI features, add your OpenAI/Anthropic API keys to .env"
    echo ""
}

# Main setup function
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                WhatsApp MCP Dashboard Setup                  ║"
    echo "║              Automated Installation Script                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    check_requirements
    setup_python_env
    install_backend_deps
    install_frontend_deps
    setup_env_file
    create_startup_scripts
    setup_whatsapp_mcp
    create_whatsapp_script
    show_final_instructions
}

# Run main function
main "$@"