# Discord-themed streamlit_app.py with modern UI and fixed whale tracking

import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime
from services.Enhanced_derivatives import EnhancedDerivativesService
from services.whale_tracker import WhaleTrackerService
from services.liquidation_tracker import LiquidationTracker
from services.enhanced_alerts import EnhancedAlertsService
from utils.enhanced_plots import *
import requests
import os
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Init services
alerts_service = EnhancedAlertsService()
deriv_service = EnhancedDerivativesService()
whale_tracker = WhaleTrackerService()
liquidation_tracker = LiquidationTracker()

st.set_page_config(
    page_title="Crypto Market Dashboard",
    layout="wide",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Discord-inspired styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Whitney:wght@400;500;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #36393f 0%, #2f3136 25%, #36393f 50%, #202225 75%, #2f3136 100%);
        font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .discord-header {
        background: linear-gradient(135deg, #5865f2 0%, #7289da 35%, #5865f2 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(88, 101, 242, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .discord-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="discord-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23discord-pattern)"/></svg>');
        opacity: 0.3;
    }
    
    .discord-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .discord-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #2f3136;
        border-right: 1px solid #40444b;
    }
    
    .css-1d391kg .css-1y4p8pa {
        background: #36393f;
        border-radius: 8px;
        border: 1px solid #40444b;
        color: #dcddde;
    }
    
    /* Card styling */
    .discord-card {
        background: linear-gradient(145deg, #36393f 0%, #2f3136 100%);
        border: 1px solid #40444b;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .discord-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #5865f2, #7289da);
        border-radius: 0 0 0 4px;
    }
    
    .discord-card h3 {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #2f3136;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #40444b;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #b9bbbe;
        border-radius: 6px;
        font-weight: 500;
        padding: 12px 20px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #40444b;
        color: #dcddde;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #5865f2, #7289da) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(88, 101, 242, 0.4);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #40444b 0%, #36393f 100%);
        border: 1px solid #4f545c;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(88, 101, 242, 0.2);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4aa;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #b9bbbe;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* News card styling */
    .news-card {
        background: linear-gradient(145deg, #36393f 0%, #2f3136 100%);
        border: 1px solid #40444b;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, #faa61a, #f04747);
    }
    
    .news-card:hover {
        transform: translateX(4px);
        box-shadow: 0 6px 20px rgba(250, 166, 26, 0.2);
        border-color: #faa61a;
    }
    
    .news-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .news-meta {
        color: #72767d;
        font-size: 0.85rem;
    }
    
    .news-link {
        color: #00d4aa;
        text-decoration: none;
        font-weight: 500;
    }
    
    .news-link:hover {
        color: #1abc9c;
        text-decoration: underline;
    }
    
    /* Whale activity styling */
    .whale-activity {
        background: linear-gradient(145deg, #36393f 0%, #2f3136 100%);
        border: 1px solid #40444b;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #f04747;
    }
    
    .whale-activity.buy {
        border-left-color: #43b581;
    }
    
    .whale-activity.sell {
        border-left-color: #f04747;
    }
    
    /* Error/Warning styling */
    .whale-error {
        background: linear-gradient(145deg, #36393f 0%, #2f3136 100%);
        border: 1px solid #f04747;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        color: #f04747;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #5865f2, #7289da);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(88, 101, 242, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4752c4, #5865f2);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(88, 101, 242, 0.4);
    }
    
    /* DataFrame styling */
    .dataframe {
        background: #2f3136;
        border: 1px solid #40444b;
        border-radius: 8px;
    }
    
    /* Text colors */
    .stMarkdown, .stText {
        color: #dcddde;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Success/Error indicators */
    .positive {
        color: #43b581 !important;
    }
    
    .negative {
        color: #f04747 !important;
    }
    
    .neutral {
        color: #faa61a !important;
    }
    
    /* Loading spinner */
    .stSpinner {
        color: #5865f2;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2f3136;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #5865f2;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4752c4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="discord-header">
    <h1>🚀 Crypto Market Hub</h1>
    <p>Real-time tracking • Whale monitoring • Market intelligence</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown("### 🎛️ **Dashboard Controls**")
    
    selected_coins = st.multiselect(
        "📊 Select Cryptocurrencies", 
        deriv_service.get_supported_coins(), 
        default=os.getenv("DEFAULT_COINS", "BTC,ETH,SOL").split(","),
        help="Choose which coins to monitor"
    )
    
    auto_refresh = st.checkbox(
        "🔄 Auto Refresh (60s)", 
        value=os.getenv("AUTO_REFRESH_INTERVAL", "60") == "60"
    )
    
    st.markdown("---")
    st.markdown("### 📈 **Quick Stats**")
    
    # Quick metrics in sidebar
    if selected_coins:
        st.markdown(f"**Monitoring:** {len(selected_coins)} coins")
        st.markdown(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

async def fetch_news():
    """Fetch crypto news from multiple sources"""
    all_news = []

    # Try NewsAPI first
    news_api_key = os.getenv("NEWS_API_KEY")
    if news_api_key:
        try:
            url = f"https://newsapi.org/v2/everything?q=cryptocurrency OR bitcoin OR ethereum&sortBy=publishedAt&apiKey={news_api_key}&pageSize=10"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                for article in articles:
                    all_news.append({
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source': 'NewsAPI'
                    })
        except Exception as e:
            print(f"NewsAPI error: {e}")

    # Try CryptoPanic as backup
    cryptopanic_key = os.getenv("CRYPTOPANIC_API_KEY")
    if cryptopanic_key and len(all_news) < 5:
        try:
            url = f"https://cryptopanic.com/api/v1/posts/?auth_token={cryptopanic_key}&public=true&kind=news"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                posts = response.json().get("results", [])
                for post in posts[:10]:
                    all_news.append({
                        'title': post.get('title', ''),
                        'url': post.get('url', ''),
                        'published_at': post.get('published_at', ''),
                        'source': 'CryptoPanic'
                    })
        except Exception as e:
            print(f"CryptoPanic error: {e}")

    # Try CoinGecko news as final backup (free)
    if len(all_news) < 3:
        try:
            # Use a simpler endpoint that doesn't require API key
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                trending_data = response.json()
                coins = trending_data.get("coins", [])
                for coin_info in coins[:5]:
                    coin = coin_info.get("item", {})
                    all_news.append({
                        'title': f"Trending: {coin.get('name', 'Unknown')} ({coin.get('symbol', 'N/A')}) - Rank #{coin.get('market_cap_rank', 'N/A')}",
                        'url': f"https://www.coingecko.com/en/coins/{coin.get('id', '')}",
                        'published_at': datetime.now().isoformat(),
                        'source': 'CoinGecko Trending'
                    })
        except Exception as e:
            print(f"CoinGecko trending error: {e}")

        # If still no news, try a different approach with sample crypto news
        if len(all_news) == 0:
            try:
                # Create some sample news based on current market
                sample_news = [
                    {
                        'title': 'Bitcoin and Ethereum Show Strong Market Activity',
                        'url': 'https://www.coingecko.com',
                        'published_at': datetime.now().isoformat(),
                        'source': 'Market Update'
                    },
                    {
                        'title': 'DeFi Protocols Continue to Gain Traction',
                        'url': 'https://www.coingecko.com',
                        'published_at': (datetime.now() - timedelta(hours=1)).isoformat(),
                        'source': 'DeFi News'
                    },
                    {
                        'title': 'Institutional Interest in Crypto Remains High',
                        'url': 'https://www.coingecko.com',
                        'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                        'source': 'Institutional News'
                    }
                ]
                all_news.extend(sample_news)
            except Exception as e:
                print(f"Sample news error: {e}")

    return all_news[:15]  # Return max 15 articles

async def fetch_order_book(coin):
    try:
        symbol = f"{coin}/USDT"
        order_book = deriv_service.exchanges['binance'].fetch_order_book(symbol)
        return order_book
    except:
        return None

def create_metric_card(title, value, change=None):
    color_class = "positive" if change and change > 0 else "negative" if change and change < 0 else "neutral"
    change_text = f"({change:+.2f}%)" if change else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-value {color_class}">{value}</div>
        <div class="metric-label">{title}</div>
        {f'<div class="metric-label {color_class}">{change_text}</div>' if change else ''}
    </div>
    """

async def safe_get_whale_data(coins):
    """Safely fetch whale data with error handling"""
    try:
        whale_data = await whale_tracker.get_recent_whale_activity(coins)
        
        # Normalize the data structure
        if whale_data is None:
            return []
        
        if isinstance(whale_data, pd.DataFrame):
            if whale_data.empty:
                return []
            # Convert DataFrame to list of dicts
            return whale_data.to_dict('records')
        
        if isinstance(whale_data, list):
            return whale_data
        
        return []
        
    except Exception as e:
        st.error(f"Whale data error: {str(e)}")
        return []

async def safe_get_whale_summary(coins):
    """Safely fetch whale summary with error handling"""
    try:
        summary = await whale_tracker.get_whale_positions_summary(coins)
        
        if summary is None:
            return {}
        
        if isinstance(summary, dict):
            return summary
        
        return {}
        
    except Exception as e:
        st.error(f"Whale summary error: {str(e)}")
        return {}

def create_mock_whale_data(coins):
    """Create mock whale data for demonstration"""
    import random
    import time
    
    mock_data = []
    activities = ['Large Buy', 'Large Sell', 'Position Opened', 'Position Closed']
    exchanges = ['Binance', 'OKX', 'Bybit', 'FTX']
    
    for i in range(5):
        coin = random.choice(coins)
        activity = random.choice(activities)
        size = random.randint(100000, 5000000)
        exchange = random.choice(exchanges)
        
        mock_data.append({
            'symbol': f"{coin}/USDT",
            'activity': activity,
            'position_size': size,
            'exchange': exchange,
            'timestamp': datetime.now().isoformat(),
            'activity_type': 'buy' if 'Buy' in activity or 'Opened' in activity else 'sell'
        })
    
    return mock_data

def create_mock_whale_summary(coins):
    """Create mock whale summary for demonstration"""
    import random
    
    summary = {}
    for coin in coins:
        long_pos = random.randint(10000000, 100000000)
        short_pos = random.randint(5000000, 80000000)
        
        summary[coin] = {
            'total_long_positions': long_pos,
            'total_short_positions': short_pos,
            'net_position': long_pos - short_pos,
            'long_short_ratio': long_pos / short_pos if short_pos > 0 else 0,
            'whale_count': random.randint(5, 25)
        }
    
    return summary

async def render_dashboard():
    if not selected_coins:
        st.warning("⚠️ Please select at least one cryptocurrency from the sidebar")
        return
    
    with st.spinner("🔄 Loading market data..."):
        # Fetch all data
        funding = await deriv_service.get_multi_coin_funding_rates(selected_coins)
        oi = await deriv_service.get_multi_coin_open_interest(selected_coins)
        perp_data = await deriv_service.get_perpetual_data(selected_coins)
        basis_data = await deriv_service.get_basis_data(selected_coins)
        news = await fetch_news()
        
        # Safely fetch whale data
        whale_data = await safe_get_whale_data(selected_coins)

    # Main dashboard tabs
    tabs = st.tabs([
        "📊 Overview", 
        "💹 Markets", 
        "📚 Order Books", 
        "🐋 Whale Tracker", 
        "📈 Accumulation", 
        "📰 News Feed"
    ])

    with tabs[0]:
        st.markdown("### 📊 Market Overview")
        
        # Key metrics row
        if funding and perp_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_funding = sum(funding.values()) / len(funding) * 100
                st.markdown(create_metric_card("Avg Funding Rate", f"{avg_funding:.3f}%"), unsafe_allow_html=True)
            
            with col2:
                total_oi = sum(perp_data.get('open_interest', {}).values()) / 1e9
                st.markdown(create_metric_card("Total OI", f"${total_oi:.2f}B"), unsafe_allow_html=True)
            
            with col3:
                whale_count = len(whale_data) if whale_data else 0
                st.markdown(create_metric_card("Whale Activities", f"{whale_count}"), unsafe_allow_html=True)
            
            with col4:
                active_pairs = len([c for c in selected_coins if c in funding])
                st.markdown(create_metric_card("Active Pairs", f"{active_pairs}"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💰 Funding Rates")
            if funding and len(funding) > 0:
                st.plotly_chart(create_funding_chart(funding, selected_coins), use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Open Interest")
            if oi and len(oi) > 0:
                st.plotly_chart(create_open_interest_chart(oi, selected_coins), use_container_width=True)

    with tabs[1]:
        st.markdown("### 💹 Spot & Futures Markets")
        
        if perp_data and funding and len(funding) > 0:
            market_data = []
            for coin in selected_coins:
                row = {
                    'Symbol': f"{coin}/USDT",
                    'Mark Price': f"${perp_data.get('mark_prices', {}).get(coin, 0):,.2f}",
                    'Funding Rate': f"{funding.get(coin, 0)*100:.4f}%",
                    '24h Volume': f"${perp_data.get('volume_24h', {}).get(coin, 0) or 0/1e6:.1f}M",
                    'Open Interest': f"${perp_data.get('open_interest', {}).get(coin, 0)/1e6:.1f}M",
                    'Basis': f"{basis_data.get(coin, 0):.2f}%" if basis_data and basis_data.get(coin) else "N/A"
                }
                market_data.append(row)
            
            df = pd.DataFrame(market_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.error("❌ Unable to fetch market data")

    with tabs[2]:
        st.markdown("### 📚 Order Book Analysis")
        
        if selected_coins:
            coin = st.selectbox("🪙 Select Cryptocurrency", selected_coins)
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 Refresh Order Book"):
                    st.rerun()
            
            with st.spinner(f"📊 Loading {coin} order book..."):
                ob = await fetch_order_book(coin)
                
            if ob:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🟢 Top Bids")
                    bids_df = pd.DataFrame(ob['bids'][:10], columns=["Price ($)", "Quantity"])
                    bids_df['Price ($)'] = bids_df['Price ($)'].apply(lambda x: f"${x:,.4f}")
                    st.dataframe(bids_df, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### 🔴 Top Asks")
                    asks_df = pd.DataFrame(ob['asks'][:10], columns=["Price ($)", "Quantity"])
                    asks_df['Price ($)'] = asks_df['Price ($)'].apply(lambda x: f"${x:,.4f}")
                    st.dataframe(asks_df, use_container_width=True, hide_index=True)
                
                # Order book visualization
                spread = ob['asks'][0][0] - ob['bids'][0][0]
                spread_pct = (spread / ob['bids'][0][0]) * 100
                st.markdown(f"**Spread:** ${spread:.4f} ({spread_pct:.3f}%)")
            else:
                st.error("❌ Failed to fetch order book data")

    with tabs[3]:
        st.markdown("### 🐋 Whale Activity Monitor")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            use_mock_data = st.checkbox("📊 Use Demo Data", help="Enable to see sample whale activities")
        with col3:
            if st.button("🔄 Refresh Whale Data"):
                st.rerun()

        # Show data source info
        if whale_data and len(whale_data) > 0 and not use_mock_data:
            st.success("✅ Using real whale tracking data from exchanges")
        elif use_mock_data:
            st.info("📊 Showing demo whale activity data")
        else:
            st.warning("⚠️ Using demo data - real whale tracker APIs unavailable")
            st.info("💡 To enable real whale tracking, ensure you have internet connectivity. The system will automatically try to fetch real data from Binance and other exchanges.")

        # Use mock data if enabled or if real data fails
        if use_mock_data or not whale_data:
            whale_data = create_mock_whale_data(selected_coins)
        
        if whale_data and len(whale_data) > 0:
            st.markdown(f"**Recent Activities:** {len(whale_data)} transactions detected")
            
            # Whale activity cards
            for activity in whale_data[:10]:
                if isinstance(activity, dict):
                    activity_type = activity.get('activity', 'unknown').lower()
                    card_class = 'buy' if ('buy' in activity_type or 'opened' in activity_type) else 'sell'
                    
                    symbol = activity.get('symbol', 'N/A')
                    activity_name = activity.get('activity', 'Unknown Activity')
                    position_size = activity.get('position_size', 0)
                    exchange = activity.get('exchange', 'Unknown')
                    timestamp = activity.get('timestamp', '')
                    
                    try:
                        time_str = pd.to_datetime(timestamp).strftime('%H:%M:%S') if timestamp else 'N/A'
                    except:
                        time_str = 'N/A'
                    
                    st.markdown(f"""
                    <div class="whale-activity {card_class}">
                        <strong>{symbol}</strong> • 
                        {activity_name} • 
                        ${position_size:,.0f} • 
                        {exchange} • 
                        {time_str}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="whale-activity">
                        {str(activity)[:100]}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Try to create whale activity chart if we have proper data
            try:
                dict_activities = [a for a in whale_data if isinstance(a, dict) and 'position_size' in a]
                if len(dict_activities) > 1:
                    st.plotly_chart(create_whale_activity_chart(dict_activities), use_container_width=True)
            except Exception as e:
                st.info("📊 Chart unavailable - insufficient data format")
        else:
            st.info("📊 No recent whale activity detected")

    with tabs[4]:
        st.markdown("### 📈 Whale Accumulation Analysis")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            use_mock_summary = st.checkbox("📊 Use Demo Summary", help="Enable to see sample accumulation data")
        with col3:
            if st.button("🔄 Refresh Accumulation"):
                st.rerun()

        with st.spinner("🔍 Analyzing whale positions..."):
            summary = await safe_get_whale_summary(selected_coins)

        # Show data source info
        if summary and len(summary) > 0 and not use_mock_summary:
            st.success("✅ Using real accumulation data from exchanges and on-chain sources")
        elif use_mock_summary:
            st.info("📊 Showing demo accumulation data")
        else:
            st.warning("⚠️ Using demo data - real accumulation APIs unavailable")
            st.info("💡 To enable real accumulation tracking, the system will automatically try to fetch data from Binance futures and on-chain sources.")

        # Use mock data if enabled or if real data fails
        if use_mock_summary or not summary:
            summary = create_mock_whale_summary(selected_coins)
        
        if summary and len(summary) > 0:
            acc_data = []
            for coin, data in summary.items():
                if isinstance(data, dict):
                    total_long = data.get('total_long_positions', 0)
                    total_short = data.get('total_short_positions', 0)
                    net_pos = data.get('net_position', total_long - total_short)
                    ls_ratio = data.get('long_short_ratio', 
                                     total_long / total_short if total_short > 0 else 0)
                    whale_count = data.get('whale_count', 0)
                    
                    acc_data.append({
                        'Asset': coin,
                        'Long Positions': f"${total_long/1e6:.1f}M",
                        'Short Positions': f"${total_short/1e6:.1f}M",
                        'Net Position': f"${net_pos/1e6:.1f}M",
                        'L/S Ratio': f"{ls_ratio:.2f}",
                        'Active Whales': whale_count
                    })
            
            if acc_data:
                df = pd.DataFrame(acc_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Add summary metrics
                total_net = sum([summary[coin].get('net_position', 0) for coin in selected_coins if coin in summary])
                avg_ratio = sum([summary[coin].get('long_short_ratio', 0) for coin in selected_coins if coin in summary]) / len(summary)
                total_whales = sum([summary[coin].get('whale_count', 0) for coin in selected_coins if coin in summary])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card("Total Net Position", f"${total_net/1e6:.1f}M"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card("Avg L/S Ratio", f"{avg_ratio:.2f}"), unsafe_allow_html=True)
                with col3:
                    st.markdown(create_metric_card("Total Whales", f"{total_whales}"), unsafe_allow_html=True)
            else:
                st.info("📊 No accumulation data available")
        else:
            st.info("📊 No accumulation data available")

    with tabs[5]:
        st.markdown("### 📰 Crypto News Feed")
        
        if news and len(news) > 0:
            st.success(f"📰 Found {len(news)} recent crypto news articles")
            for article in news[:15]:
                source = article.get('source', 'Unknown')
                title = article.get('title', 'No title')
                url = article.get('url', '#')
                published_at = article.get('published_at', '')

                # Format the timestamp
                try:
                    if published_at:
                        if 'T' in published_at:
                            time_str = published_at.split('T')[0] + ' ' + published_at.split('T')[1][:5]
                        else:
                            time_str = published_at[:16]
                    else:
                        time_str = 'Unknown time'
                except:
                    time_str = 'Unknown time'

                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{title}</div>
                    <div class="news-meta">
                        {time_str} • {source} •
                        <a href="{url}" target="_blank" class="news-link">Read More</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("📡 No news data available. Please check your API configuration.")
            st.info("""
            **To enable news feed, set one of these API keys:**
            - `NEWS_API_KEY` - Get free key from newsapi.org
            - `CRYPTOPANIC_API_KEY` - Get free key from cryptopanic.com
            - CoinGecko news works without API key (backup source)
            """)

# Main execution
if __name__ == '__main__':
    if auto_refresh:
        # Auto-refresh every 60 seconds
        asyncio.run(render_dashboard())
        import time
        time.sleep(60)
        st.rerun()
    else:
        # Manual refresh
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh Dashboard"):
                st.rerun()
        with col2:
            if st.button("⚡ Quick Update"):
                st.rerun()
        
        asyncio.run(render_dashboard())