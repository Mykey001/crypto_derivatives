# streamlit_app.py
import streamlit as st
import pandas as pd
import time
import asyncio
from datetime import datetime, timedelta
from services.Enhanced_derivatives import EnhancedDerivativesService
from services.whale_tracker import WhaleTrackerService
from services.liquidation_tracker import LiquidationTracker
from services.enhanced_alerts import EnhancedAlertsService
from utils.plots import create_funding_chart, create_liquidation_heatmap, create_whale_activity_chart
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from services.Enhanced_derivatives import EnhancedDerivativesService
from services.Enhanced_derivatives import EnhancedDerivativesService
import asyncio

alerts_service = EnhancedAlertsService()


load_dotenv()

# Enhanced Streamlit Configuration
st.set_page_config(
    page_title="Hyperliquid Whale Tracker (Real-Time)", 
    layout="wide", 
    page_icon="🐋",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme matching the screenshot
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1f2937;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #374151;
    }
    .whale-activity {
        background: #111827;
        border-radius: 8px;
        padding: 1rem;
    }
    .stMetric {
        background: #1f2937;
        padding: 0.5rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    derivatives_service = EnhancedDerivativesService()
    whale_service = WhaleTrackerService()
    liquidation_service = LiquidationTracker()
    return derivatives_service, whale_service, liquidation_service

derivatives_service, whale_service, liquidation_service = init_services()

# Sidebar Configuration
st.sidebar.header("🎛️ Dashboard Settings")
selected_coins = st.sidebar.multiselect(
    "Select Cryptocurrencies",
    ["BTC", "ETH", "SOL", "AVAX", "MATIC", "ARB", "OP", "DOGE", "ADA", "DOT", "LINK", "UNI"],
    default=["BTC", "ETH", "SOL"]
)

alert_threshold = st.sidebar.slider("Funding Rate Alert Threshold (%)", 0.1, 2.0, 0.5, 0.1)
whale_threshold = st.sidebar.number_input("Whale Position Threshold ($M)", min_value=0.1, value=1.0, step=0.1)
auto_refresh = st.sidebar.checkbox("Auto Refresh (60s)", value=True)

# Main Dashboard Header
st.markdown("""
<div class="main-header">
    <h1>🐋 Hyperliquid Whale Tracker (Real-Time)</h1>
    <p>Professional-grade cryptocurrency market monitoring and whale activity tracking</p>
</div>
""", unsafe_allow_html=True)

# Create main containers
main_placeholder = st.empty()

def format_large_number(num):
    """Format large numbers with appropriate suffixes"""
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.1f}K"
    else:
        return f"${num:.2f}"

def get_color_for_value(value, threshold=0):
    """Return appropriate color based on value"""
    if value > threshold:
        return "🟢"
    elif value < -threshold:
        return "🔴"
    else:
        return "⚪"

async def update_dashboard():
    """Main dashboard update function"""
    try:
        # Fetch all data concurrently
        funding_data = await derivatives_service.get_multi_coin_funding_rates(selected_coins)
        oi_data = await derivatives_service.get_multi_coin_open_interest(selected_coins)
        whale_activity = await whale_service.get_recent_whale_activity(selected_coins, whale_threshold)
        liquidation_data = await liquidation_service.get_liquidation_data(selected_coins)
        
        with main_placeholder.container():
            # Top-level metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            total_oi = sum([oi_data.get(coin, 0) for coin in selected_coins])
            avg_funding = sum([funding_data.get(coin, 0) for coin in selected_coins]) / len(selected_coins)
            total_liquidations = sum([liquidation_data.get(coin, {}).get('total', 0) for coin in selected_coins])
            active_whales = len(whale_activity)
            
            with col1:
                st.metric(
                    "Total Open Interest", 
                    format_large_number(total_oi),
                    delta=f"{get_color_for_value(avg_funding, 0.1)} Avg Funding: {avg_funding:.3f}%"
                )
            
            with col2:
                st.metric(
                    "24h Liquidations", 
                    format_large_number(total_liquidations),
                    delta="🔥 High volatility" if total_liquidations > 100000000 else "📊 Normal"
                )
            
            with col3:
                st.metric(
                    "Active Whale Positions", 
                    f"{active_whales}",
                    delta="🐋 High activity" if active_whales > 10 else "📈 Moderate"
                )
            
            with col4:
                market_sentiment = "🚀 Bullish" if avg_funding > 0.2 else "🐻 Bearish" if avg_funding < -0.2 else "⚖️ Neutral"
                st.metric("Market Sentiment", market_sentiment)
            
            st.divider()
            
            # Main content area with tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "🐋 Whale Activity", "💥 Liquidations", "📈 Charts"])
            
            with tab1:
                # Funding rates and OI table
                st.subheader("📊 Real-Time Market Data")
                
                market_df = pd.DataFrame({
                    'Symbol': [f"{coin}/USDT" for coin in selected_coins],
                    'Funding Rate (%)': [f"{funding_data.get(coin, 0):.4f}" for coin in selected_coins],
                    'Open Interest': [format_large_number(oi_data.get(coin, 0)) for coin in selected_coins],
                    'Status': [get_color_for_value(funding_data.get(coin, 0), alert_threshold/100) for coin in selected_coins],
                    '24h Liquidations': [format_large_number(liquidation_data.get(coin, {}).get('total', 0)) for coin in selected_coins]
                })
                
                st.dataframe(
                    market_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Alert generation
                for coin in selected_coins:
                    funding_rate = funding_data.get(coin, 0)
                    if abs(funding_rate) > alert_threshold:
                        alert_msg = f"⚠️ {coin} funding rate alert: {funding_rate:.4f}% (Threshold: ±{alert_threshold}%)"
                        st.warning(alert_msg)
                        if st.sidebar.checkbox("Send Telegram Alerts", value=False):
                            EnhancedAlertsService.send_telegram_alert(alert_msg)
            
            with tab2:
                st.subheader("🐋 Latest Whale Activity")
                
                if whale_activity:
                    whale_df = pd.DataFrame(whale_activity)
                    whale_df['Time'] = pd.to_datetime(whale_df['timestamp']).dt.strftime('%H:%M')
                    whale_df['Position'] = whale_df['position_size'].apply(format_large_number)
                    whale_df['Price'] = whale_df['price'].apply(lambda x: f"${x:,.2f}")
                    
                    # Color-code activities
                    def get_activity_color(activity):
                        if 'Open Long' in activity:
                            return '🟢'
                        elif 'Open Short' in activity:
                            return '🔴'
                        elif 'Close Long' in activity:
                            return '🟡'
                        else:
                            return '🟠'
                    
                    whale_df['Activity'] = whale_df['activity'].apply(lambda x: f"{get_activity_color(x)} {x}")
                    
                    display_columns = ['Address', 'Symbol', 'Activity', 'Position', 'Price', 'Time']
                    st.dataframe(
                        whale_df[display_columns],
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                else:
                    st.info("No significant whale activity detected in the selected timeframe.")
            
            with tab3:
                st.subheader("💥 Liquidation Tracker")
                
                # Liquidation summary
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Long Liquidations**")
                    long_liq_total = sum([liquidation_data.get(coin, {}).get('long_liquidations', 0) for coin in selected_coins])
                    st.metric("24h Long Liquidations", format_large_number(long_liq_total))
                
                with col2:
                    st.markdown("**Short Liquidations**")
                    short_liq_total = sum([liquidation_data.get(coin, {}).get('short_liquidations', 0) for coin in selected_coins])
                    st.metric("24h Short Liquidations", format_large_number(short_liq_total))
                
                # Liquidation heatmap
                if liquidation_data:
                    liq_chart = create_liquidation_heatmap(liquidation_data, selected_coins)
                    st.plotly_chart(liq_chart, use_container_width=True)
            
            with tab4:
                st.subheader("📈 Market Analysis Charts")
                
                # Funding rate chart
                funding_chart = create_funding_chart(funding_data, selected_coins)
                st.plotly_chart(funding_chart, use_container_width=True)
                
                # Whale activity chart
                if whale_activity:
                    whale_chart = create_whale_activity_chart(whale_activity)
                    st.plotly_chart(whale_chart, use_container_width=True)
            
            # Footer with last update time
            st.divider()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            st.caption(f"🕒 Last updated: {current_time} | 🔄 Auto-refresh: {'ON' if auto_refresh else 'OFF'}")
            
    except Exception as e:
        st.error(f"Error updating dashboard: {str(e)}")
        st.info("Retrying in 60 seconds...")

# Main execution loop
if __name__ == "__main__":
    if auto_refresh:
        # Auto-refresh mode
        while True:
            asyncio.run(update_dashboard())
            time.sleep(60)
    else:
        # Manual refresh mode
        if st.button("🔄 Refresh Data"):
            asyncio.run(update_dashboard())
        else:
            # Initial load
            asyncio.run(update_dashboard())

            # At the bottom of services/enhanced_derivatives.py
_service_instance = EnhancedDerivativesService()

async def get_funding_rates(coins):
    return await _service_instance.get_multi_coin_funding_rates(coins)
