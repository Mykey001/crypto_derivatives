# Crypto Dashboard - Docker Setup

This guide will help you run the Crypto Dashboard using Docker, which provides a consistent and isolated environment for the application.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)
- At least 4GB of available RAM
- Internet connection for downloading dependencies and fetching crypto data

## Quick Start

### Option 1: Using the Helper Script (Recommended)

1. **Make the script executable** (if not already done):
   ```bash
   chmod +x run-docker.sh
   ```

2. **Run the dashboard**:
   ```bash
   ./run-docker.sh run
   ```

3. **Access the dashboard**:
   Open your browser and go to `http://localhost:8502`

### Option 2: Using Docker Compose

1. **Build and run**:
   ```bash
   docker-compose up --build
   ```

2. **Access the dashboard**:
   Open your browser and go to `http://localhost:8501`

### Option 3: Using Docker directly

1. **Build the image**:
   ```bash
   docker build -t crypto-dashboard .
   ```

2. **Run the container**:
   ```bash
   docker run -d --name crypto-dashboard -p 8502:8501 --env-file .env crypto-dashboard
   ```

## Configuration

### Environment Variables

The application uses environment variables for configuration. Edit the `.env` file with your API keys:

```env
# Required for full functionality
COINGECKO_API_KEY=your_coingecko_api_key_here
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here

# Optional but recommended
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Optional for social sentiment
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
```

## Helper Script Commands

The `run-docker.sh` script provides several useful commands:

```bash
# Start the dashboard (default port 8502)
./run-docker.sh run

# Start on a specific port
./run-docker.sh run 8080

# Build the Docker image
./run-docker.sh build

# Stop the dashboard
./run-docker.sh stop

# Restart the dashboard
./run-docker.sh restart

# View logs
./run-docker.sh logs

# Check status
./run-docker.sh status

# Show help
./run-docker.sh help
```

## Troubleshooting

### Port Already in Use

If you get a "port already allocated" error:

1. **Use a different port**:
   ```bash
   ./run-docker.sh run 8503
   ```

2. **Stop existing containers**:
   ```bash
   docker stop $(docker ps -q --filter "publish=8501")
   ```

### Container Won't Start

1. **Check the logs**:
   ```bash
   ./run-docker.sh logs
   ```

2. **Rebuild the image**:
   ```bash
   ./run-docker.sh build
   ```

## Current Status

✅ **Your crypto dashboard is now running successfully in Docker!**

- **Container**: crypto-dashboard-new
- **Port**: 8502
- **URL**: http://localhost:8502
- **Status**: Running and healthy

You can access your dashboard by opening http://localhost:8502 in your web browser.
