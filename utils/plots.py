# utils/enhanced_plots.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List

def create_funding_chart(funding_data: Dict[str, float], coins: List[str]) -> go.Figure:
    """Create funding rate chart similar to screenshot"""
    # Generate historical data for the chart
    dates = pd.date_range(end=datetime.now(), periods=24, freq='H')
    
    fig = go.Figure()
    
    colors = ['#00D4AA', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    for i, coin in enumerate(coins):
        # Simulate historical funding rates
        base_rate = funding_data.get(coin, 0) / 100
        historical_rates = []
        
        for j in range(24):
            # Add some realistic variation
            noise = np.random.normal(0, 0.001)
            trend = np.sin(j * 0.3) * 0.002
            rate = base_rate + noise + trend
            historical_rates.append(rate * 100)  # Convert back to percentage
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=historical_rates,
            mode='lines+markers',
            name=f'{coin}/USDT',
            line=dict(width=2, color=colors[i % len(colors)]),
            marker=dict(size=4),
            hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Funding Rate: %{y:.4f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': 'Funding Rates - 24H History',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        },
        xaxis_title='Time',
        yaxis_title='Funding Rate (%)',
        plot_bgcolor='rgba(17, 24, 39, 1)',  # Dark background
        paper_bgcolor='rgba(17, 24, 39, 1)',
        font=dict(color='white'),
        xaxis=dict(
            gridcolor='rgba(55, 65, 81, 0.5)',
            zerolinecolor='rgba(55, 65, 81, 0.8)',
        ),
        yaxis=dict(
            gridcolor='rgba(55, 65, 81, 0.5)',
            zerolinecolor='rgba(55, 65, 81, 0.8)',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400
    )
    
    # Add horizontal line at 0%
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255, 255, 255, 0.5)")
    
    return fig

def create_liquidation_heatmap(liquidation_data: Dict, coins: List[str]) -> go.Figure:
    """Create liquidation heatmap"""
    # Prepare data for heatmap
    z_data = []
    y_labels = []
    
    for coin in coins:
        if coin in liquidation_data:
            long_liq = liquidation_data[coin]['long_liquidations'] / 1000000  # Convert to millions
            short_liq = liquidation_data[coin]['short_liquidations'] / 1000000
            z_data.append([long_liq, short_liq])
            y_labels.append(coin)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=['Long Liquidations', 'Short Liquidations'],
        y=y_labels,
        colorscale='RdYlBu_r',
        text=[[f'${z:.1f}M' for z in row] for row in z_data],
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='<b>%{y}</b><br>%{x}: $%{z:.1f}M<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '24h Liquidations Heatmap',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'white'}
        },
        plot_bgcolor='rgba(17, 24, 39, 1)',
        paper_bgcolor='rgba(17, 24, 39, 1)',
        font=dict(color='white'),
        height=300
    )
    
    return fig

def create_whale_activity_chart(whale_activity: List[Dict]) -> go.Figure:
    """Create whale activity visualization"""
    df = pd.DataFrame(whale_activity)
    
    # Create bubble chart
    fig = go.Figure()
    
    # Separate by activity type
    colors = {
        'Open Long': '#00D4AA',
        'Open Short': '#FF6B6B', 
        'Close Long': '#FFE066',
        'Close Short': '#FF9F43',
        'Add to Long': '#00D4AA',
        'Add to Short': '#FF6B6B',
        'Reduce Long': '#FFE066',
        'Reduce Short': '#FF9F43'
    }
    
    for activity_type in df['activity'].unique():
        activity_df = df[df['activity'] == activity_type]
        
        fig.add_trace(go.Scatter(
            x=activity_df['timestamp'],
            y=activity_df['symbol'],
            mode='markers',
            marker=dict(
                size=activity_df['position_size'] / 100000,  # Scale bubble size
                color=colors.get(activity_type, '#74B9FF'),
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            name=activity_type,
            text=activity_df['address'],
            hovertemplate='<b>%{text}</b><br>%{fullData.name}<br>%{y}<br>Size: $%{marker.size:.1f}M<br>Time: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': 'Whale Activity Timeline',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'white'}
        },
        xaxis_title='Time',
        yaxis_title='Asset',
        plot_bgcolor='rgba(17, 24, 39, 1)',
        paper_bgcolor='rgba(17, 24, 39, 1)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(55, 65, 81, 0.5)'),
        yaxis=dict(gridcolor='rgba(55, 65, 81, 0.5)'),
        height=400,
        showlegend=True
    )
    
    return fig

def create_open_interest_chart(oi_data: Dict[str, float], coins: List[str]) -> go.Figure:
    """Create open interest comparison chart"""
    values = [oi_data.get(coin, 0) / 1000000 for coin in coins]  # Convert to millions
    
    fig = go.Figure(data=[
        go.Bar(
            x=coins,
            y=values,
            text=[f'${v:.1f}M' for v in values],
            textposition='auto',
            marker_color='#00D4AA',
            hovertemplate='<b>%{x}</b><br>Open Interest: $%{y:.1f}M<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Open Interest Comparison',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': 'white'}
        },
        xaxis_title='Asset',
        yaxis_title='Open Interest (Millions USD)',
        plot_bgcolor='rgba(17, 24, 39, 1)',
        paper_bgcolor='rgba(17, 24, 39, 1)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(55, 65, 81, 0.5)'),
        yaxis=dict(gridcolor='rgba(55, 65, 81, 0.5)'),
        height=350
    )
    
    return fig

def create_portfolio_overview(data: Dict) -> go.Figure:
    """Create portfolio overview similar to screenshot"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Position Distribution', 'PnL Breakdown', 'Risk Metrics', 'Performance'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "indicator"}, {"type": "scatter"}]]
    )
    
    # Position distribution (pie chart)
    position_labels = ['Long Positions', 'Short Positions', 'Cash']
    position_values = [65, 25, 10]
    
    fig.add_trace(go.Pie(
        labels=position_labels,
        values=position_values,
        hole=0.4,
        marker_colors=['#00D4AA', '#FF6B6B', '#74B9FF']
    ), row=1, col=1)
    
    # PnL breakdown (bar chart)
    assets = ['BTC', 'ETH', 'SOL', 'Others']
    pnl_values = [25.5, 12.3, -5.2, 8.1]
    colors = ['#00D4AA' if x > 0 else '#FF6B6B' for x in pnl_values]
    
    fig.add_trace(go.Bar(
        x=assets,
        y=pnl_values,
        marker_color=colors,
        text=[f'{x:+.1f}%' for x in pnl_values],
        textposition='auto'
    ), row=1, col=2)
    
    # Risk indicator
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=27.91,
        title={'text': "Total PnL ($M)"},
        gauge={'axis': {'range': [None, 50]},
               'bar': {'color': "#00D4AA"},
               'steps': [{'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 40}}
    ), row=2, col=1)
    
    # Performance timeline
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    performance = np.cumsum(np.random.randn(30) * 0.02) + 1
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=performance,
        mode='lines',
        line=dict(color='#00D4AA', width=2),
        fill='tonexty'
    ), row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(17, 24, 39, 1)',
        paper_bgcolor='rgba(17, 24, 39, 1)',
        font=dict(color='white'),
        title={
            'text': 'Portfolio Overview',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'white'}
        }
    )
    
    return fig

def create_market_sentiment_gauge(sentiment_score: float) -> go.Figure:
    """Create market sentiment gauge"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sentiment_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Market Sentiment"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#00D4AA"},
            'steps': [
                {'range': [0, 30], 'color': "#FF6B6B"},
                {'range': [30, 70], 'color': "#FFE066"},
                {'range': [70, 100], 'color': "#00D4AA"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(17, 24, 39, 1)',
        paper_bgcolor='rgba(17, 24, 39, 1)',
        font=dict(color='white', size=16)
    )
    
    return fig