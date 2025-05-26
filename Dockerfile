# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
# API Keys for crypto data providers
ENV COINGECKO_API_KEY=""
ENV COINMARKETCAP_API_KEY=""
ENV ALPHA_VANTAGE_API_KEY=""
ENV NEWS_API_KEY=""
ENV COVALENT_API_KEY=""

# Social media API keys (optional)
ENV TWITTER_BEARER_TOKEN=""
ENV REDDIT_CLIENT_ID=""
ENV REDDIT_CLIENT_SECRET=""

# Exchange API keys (optional for trading features)
ENV BINANCE_API_KEY=""
ENV BINANCE_SECRET=""
ENV BYBIT_API_KEY=""
ENV BYBIT_SECRET=""
ENV OKX_API_KEY=""
ENV OKX_SECRET=""
ENV OKX_PASSPHRASE=""

# Notification settings (optional)
ENV TELEGRAM_TOKEN=""
ENV TELEGRAM_CHAT_ID=""
ENV EMAIL_USER=""
ENV EMAIL_PASSWORD=""
ENV RECIPIENT_EMAIL=""
ENV SMTP_SERVER="smtp.gmail.com"
ENV SMTP_PORT="587"

# Application settings
ENV DEFAULT_COINS="BTC,ETH,SOL"
ENV AUTO_REFRESH_INTERVAL="60"
ENV DATABASE_URL="sqlite:///crypto_dashboard.db"
ENV DASHBOARD_PORT="8501"
ENV PYTHONUNBUFFERED="1"

# Create non-root user for security
RUN useradd -m -u 1000 streamlit && \
    chown -R streamlit:streamlit /app
USER streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false"]
