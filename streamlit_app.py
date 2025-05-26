# Discord-themed streamlit_app.py with modern UI

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
    api_key = os.getenv("CRYPTOPANIC_API_KEY")
    if not api_key:
        return []
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&public=true"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("results", [])
    except:
        pass
    return []

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

async def render_dashboard():
    if not selected_coins:
        st.warning("⚠️ Please select at least one cryptocurrency from the sidebar")
        return
    
    with st.spinner("🔄 Loading market data..."):
        # Fetch all data
        funding = await deriv_service.get_multi_coin_funding_rates(selected_coins)
        oi = await deriv_service.get_multi_coin_open_interest(selected_coins)
        whale_data = await whale_tracker.get_recent_whale_activity(selected_coins)
        perp_data = await deriv_service.get_perpetual_data(selected_coins)
        basis_data = await deriv_service.get_basis_data(selected_coins)
        news = await fetch_news()

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
                whale_count = len(whale_data) if whale_data is not None and not (isinstance(whale_data, pd.DataFrame) and whale_data.empty) and len(whale_data) > 0 else 0
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
                    '24h Volume': f"${perp_data.get('volume_24h', {}).get(coin, 0)/1e6:.1f}M",
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
        
        # Check if whale_data exists and has content
        has_whale_data = (whale_data is not None and 
                         not (isinstance(whale_data, pd.DataFrame) and whale_data.empty) and 
                         len(whale_data) > 0)
        
        if has_whale_data:
            st.markdown(f"**Recent Activities:** {len(whale_data)} transactions detected")
            
            # Whale activity cards
            for activity in whale_data[:10]:
                # Handle both dict and string formats
                if isinstance(activity, dict):
                    activity_type = activity.get('activity', 'unknown').lower()
                    card_class = 'buy' if 'buy' in activity_type else 'sell'
                    
                    symbol = activity.get('symbol', 'N/A')
                    activity_name = activity.get('activity', 'Unknown')
                    position_size = activity.get('position_size', 0)
                    exchange = activity.get('exchange', 'Unknown')
                    timestamp = activity.get('timestamp', '')
                    time_str = pd.to_datetime(timestamp).strftime('%H:%M:%S') if timestamp else 'N/A'
                    
                    st.markdown(f"""
                    <div class="whale-activity {card_class}">
                        <strong>{symbol}</strong> • 
                        {activity_name} • 
                        ${position_size:,.0f} • 
                        {exchange} • 
                        {time_str}
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif isinstance(activity, str):
                    # Handle string format
                    st.markdown(f"""
                    <div class="whale-activity">
                        {activity}
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    # Handle other formats
                    st.markdown(f"""
                    <div class="whale-activity">
                        Unknown activity format: {str(activity)[:100]}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Whale activity chart - only if we have dict format data
            dict_activities = [a for a in whale_data if isinstance(a, dict)]
            if len(dict_activities) > 1:
                st.plotly_chart(create_whale_activity_chart(dict_activities), use_container_width=True)
        else:
            st.info("📊 No recent whale activity detected")

    with tabs[4]:
        st.markdown("### 📈 Whale Accumulation Analysis")
        
        with st.spinner("🔍 Analyzing whale positions..."):
            summary = await whale_tracker.get_whale_positions_summary(selected_coins)
        
        if summary and len(summary) > 0:
            acc_data = []
            for coin, data in summary.items():
                acc_data.append({
                    'Asset': coin,
                    'Long Positions': f"${data.get('total_long_positions', 0)/1e6:.1f}M",
                    'Short Positions': f"${data.get('total_short_positions', 0)/1e6:.1f}M",
                    'Net Position': f"${data.get('net_position', 0)/1e6:.1f}M",
                    'L/S Ratio': f"{data.get('long_short_ratio', 0):.2f}",
                    'Active Whales': data.get('whale_count', 0)
                })
            
            df = pd.DataFrame(acc_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📊 No accumulation data available")

    with tabs[5]:
        st.markdown("### 📰 Crypto News Feed")
        
        if news and len(news) > 0:
            for article in news[:15]:
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{article.get('title', 'No title')}</div>
                    <div class="news-meta">
                        {article.get('published_at', '')[:16] if article.get('published_at') else 'Unknown time'} • 
                        <a href="{article.get('url', '#')}" target="_blank" class="news-link">Read More</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📡 No news data available. Check your API configuration.")

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