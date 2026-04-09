#!/bin/bash

# Evijnar Security-Aware Setup Script
# This script sets up the development environment with proper security practices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Evijnar Development Setup${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"

    local missing=0

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 not found${NC}"
        missing=1
    else
        echo -e "${GREEN}✓ Python 3 found${NC}"
    fi

    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ Node.js not found${NC}"
        missing=1
    else
        echo -e "${GREEN}✓ Node.js found${NC}"
    fi

    if ! command -v pnpm &> /dev/null; then
        echo -e "${RED}✗ pnpm not found (install with: npm install -g pnpm)${NC}"
        missing=1
    else
        echo -e "${GREEN}✓ pnpm found${NC}"
    fi

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker not found${NC}"
        missing=1
    else
        echo -e "${GREEN}✓ Docker found${NC}"
    fi

    if [ $missing -eq 1 ]; then
        echo -e "${RED}Please install missing dependencies and try again.${NC}"
        exit 1
    fi

    echo -e "${GREEN}All prerequisites satisfied!\n${NC}"
}

# Create .env files from templates
create_env_files() {
    echo -e "${BLUE}Creating .env files from templates...${NC}"

    # API .env
    if [ ! -f "apps/api/.env" ]; then
        cp apps/api/.env.example apps/api/.env
        echo -e "${GREEN}✓ Created apps/api/.env${NC}"
    else
        echo -e "${YELLOW}⚠ apps/api/.env already exists (skipping)${NC}"
    fi

    # Web .env.local
    if [ ! -f "apps/web/.env.local" ]; then
        cp apps/web/.env.example apps/web/.env.local
        echo -e "${GREEN}✓ Created apps/web/.env.local${NC}"
    else
        echo -e "${YELLOW}⚠ apps/web/.env.local already exists (skipping)${NC}"
    fi

    # Database .env
    if [ ! -f "packages/database/.env" ]; then
        cp packages/database/.env.example packages/database/.env
        echo -e "${GREEN}✓ Created packages/database/.env${NC}"
    else
        echo -e "${YELLOW}⚠ packages/database/.env already exists (skipping)${NC}"
    fi

    echo ""
}

# Generate encryption keys
generate_encryption_keys() {
    echo -e "${BLUE}Generating encryption keys...${NC}"

    PATIENT_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    PHARMA_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

    echo -e "${GREEN}✓ Generated encryption keys${NC}"
    echo -e "${YELLOW}Note: Update these in apps/api/.env:${NC}"
    echo -e "  ENCRYPTION_KEY_PATIENT_DATA=$PATIENT_KEY"
    echo -e "  ENCRYPTION_KEY_PHARMA_DATA=$PHARMA_KEY\n"
}

# Install pre-commit hooks
setup_precommit() {
    echo -e "${BLUE}Setting up pre-commit hooks...${NC}"

    if command -v pre-commit &> /dev/null; then
        pre-commit install
        echo -e "${GREEN}✓ Pre-commit hooks installed${NC}\n"
    else
        echo -e "${YELLOW}⚠ pre-commit not found. Install with: pip install pre-commit${NC}"
        echo -e "${YELLOW}  Then run: pre-commit install${NC}\n"
    fi
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing dependencies...${NC}"

    echo "Installing Node dependencies..."
    pnpm install
    echo -e "${GREEN}✓ Node dependencies installed${NC}\n"

    echo "Installing Python dependencies..."
    cd apps/api
    pip install -r requirements.txt
    cd ../..
    echo -e "${GREEN}✓ Python dependencies installed${NC}\n"
}

# Start Docker containers
start_docker() {
    echo -e "${BLUE}Starting Docker containers...${NC}"

    docker-compose up -d

    echo "Waiting for services to be ready..."
    sleep 5

    echo -e "${GREEN}✓ Docker containers started${NC}\n"
}

# Run database migrations
setup_database() {
    echo -e "${BLUE}Setting up database...${NC}"

    cd apps/api
    alembic upgrade head
    cd ../..

    echo -e "${GREEN}✓ Database migrations completed${NC}\n"
}

# Verify setup
verify_setup() {
    echo -e "${BLUE}Verifying setup...${NC}"

    # Check API health
    echo "Checking API health..."
    sleep 2
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ API is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ API health check failed (services may still be starting)${NC}"
    fi

    echo -e "${GREEN}✓ Setup verification complete${NC}\n"
}

# Display post-setup instructions
post_setup_instructions() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}Setup Complete!${NC}"
    echo -e "${BLUE}================================${NC}\n"

    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Review and update .env files:"
    echo "   - apps/api/.env"
    echo "   - apps/web/.env.local"
    echo "   - packages/database/.env"
    echo ""
    echo "2. Update encryption keys in apps/api/.env:"
    echo "   - ENCRYPTION_KEY_PATIENT_DATA"
    echo "   - ENCRYPTION_KEY_PHARMA_DATA"
    echo ""
    echo "3. Start development:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - API: http://localhost:8000"
    echo "   - Docs: http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo "  pnpm dev              - Start all services"
    echo "  docker-compose down   - Stop services"
    echo "  pre-commit run --all-files  - Run security checks"
    echo "  pytest apps/api/tests - Run tests"
    echo ""
    echo -e "${YELLOW}Security Reminders:${NC}"
    echo "  ✓ Never commit .env files"
    echo "  ✓ Never commit secrets"
    echo "  ✓ Use pre-commit hooks before committing"
    echo "  ✓ Review SECURITY.md for security policies"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    create_env_files
    generate_encryption_keys
    setup_precommit
    install_dependencies
    start_docker
    setup_database
    verify_setup
    post_setup_instructions
}

# Parse arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --quick        Skip Docker and database setup"
    echo "  --deps-only    Only install dependencies (no Docker)"
    exit 0
elif [ "$1" = "--quick" ]; then
    check_prerequisites
    create_env_files
    generate_encryption_keys
    setup_precommit
    echo -e "${YELLOW}Quick setup complete! Run 'docker-compose up' to start services.${NC}"
    exit 0
elif [ "$1" = "--deps-only" ]; then
    check_prerequisites
    create_env_files
    install_dependencies
    setup_precommit
    echo -e "${GREEN}Dependencies installed! Configure .env files and run 'docker-compose up'.${NC}"
    exit 0
fi

main
