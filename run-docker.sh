#!/bin/bash

# Crypto Dashboard Docker Runner
# This script helps you run the crypto dashboard using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="crypto-dashboard"
IMAGE_NAME="crypto-dashboard_dashboard"
DEFAULT_PORT="8502"
ENV_FILE=".env"

# Function to print colored output
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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found. Creating a template..."
        cat > "$ENV_FILE" << EOF
# Crypto Dashboard Environment Variables
# Copy this file and update with your actual API keys

# CoinGecko API (free tier available)
COINGECKO_API_KEY=your_coingecko_api_key_here

# CoinMarketCap API
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# News API
NEWS_API_KEY=your_news_api_key_here

# Twitter API (optional)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Reddit API (optional)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Database settings (optional)
DATABASE_URL=sqlite:///crypto_dashboard.db

# Dashboard settings
DASHBOARD_PORT=8502
EOF
        print_warning "Please edit the .env file with your actual API keys before running the dashboard."
    fi
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    if docker-compose build dashboard; then
        print_success "Docker image built successfully!"
    else
        print_error "Failed to build Docker image."
        exit 1
    fi
}

# Function to stop existing container
stop_container() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_status "Stopping existing container..."
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
    fi
}

# Function to run the container
run_container() {
    local port=${1:-$DEFAULT_PORT}
    
    print_status "Starting crypto dashboard on port $port..."
    
    if docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$port:8501" \
        --env-file "$ENV_FILE" \
        --restart unless-stopped \
        "$IMAGE_NAME:latest"; then
        
        print_success "Container started successfully!"
        print_success "Dashboard is available at: http://localhost:$port"
        
        # Wait a moment for the container to start
        sleep 3
        
        # Check if container is healthy
        if docker ps -f name="$CONTAINER_NAME" --format "table {{.Status}}" | grep -q "healthy\|Up"; then
            print_success "Container is running and healthy!"
        else
            print_warning "Container started but health status unknown. Check logs with: docker logs $CONTAINER_NAME"
        fi
    else
        print_error "Failed to start container."
        exit 1
    fi
}

# Function to show logs
show_logs() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_status "Showing container logs (press Ctrl+C to exit)..."
        docker logs -f "$CONTAINER_NAME"
    else
        print_error "Container '$CONTAINER_NAME' is not running."
        exit 1
    fi
}

# Function to show status
show_status() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_success "Container is running:"
        docker ps -f name="$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # Get the port
        local port=$(docker port "$CONTAINER_NAME" 8501 | cut -d: -f2)
        if [ -n "$port" ]; then
            print_success "Dashboard URL: http://localhost:$port"
        fi
    else
        print_warning "Container '$CONTAINER_NAME' is not running."
    fi
}

# Function to stop the container
stop_dashboard() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_status "Stopping crypto dashboard..."
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        print_success "Dashboard stopped successfully!"
    else
        print_warning "Container '$CONTAINER_NAME' is not running."
    fi
}

# Main script logic
case "${1:-run}" in
    "build")
        check_docker
        build_image
        ;;
    "run")
        check_docker
        check_env_file
        stop_container
        run_container "${2:-$DEFAULT_PORT}"
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "stop")
        stop_dashboard
        ;;
    "restart")
        check_docker
        stop_container
        run_container "${2:-$DEFAULT_PORT}"
        ;;
    "help"|"-h"|"--help")
        echo "Crypto Dashboard Docker Runner"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  run [port]    Start the dashboard (default port: $DEFAULT_PORT)"
        echo "  build         Build the Docker image"
        echo "  stop          Stop the dashboard"
        echo "  restart [port] Restart the dashboard"
        echo "  logs          Show container logs"
        echo "  status        Show container status"
        echo "  help          Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 run        # Start on default port ($DEFAULT_PORT)"
        echo "  $0 run 8080   # Start on port 8080"
        echo "  $0 logs       # View logs"
        echo "  $0 stop       # Stop the dashboard"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac
