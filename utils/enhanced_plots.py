# utils/enhanced_plots.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objs as go

# Discord-inspired color palette
DISCORD_COLORS = {
    'primary': '#5865f2',
    'secondary': '#7289da', 
    'success': '#43b581',
    'danger': '#f04747',
    'warning': '#faa61a',
    'info': '#00d4aa',
    'dark': '#2f3136',
    'darker': '#202225',
    'light': '#dcddde',
    'muted': '#72767d'
}

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_empty_chart(message: str) -> go.Figure:
    """Create an empty chart with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        font=dict(size=16, color=DISCORD_COLORS['muted']),
        showarrow=False
    )
    fig.update_layout(
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    return fig

def create_funding_chart(funding_rates: Dict[str, float], coins: List[str]) -> go.Figure:
    """Create a modern funding rates chart with Discord theme"""
    
    # Filter and sort data
    filtered_rates = {coin: funding_rates.get(coin, 0) for coin in coins if coin in funding_rates}
    
    if not filtered_rates:
        return create_empty_chart("No funding rate data available")
    
    # Prepare data
    coins_list = list(filtered_rates.keys())
    rates_list = list(filtered_rates.values())
    
    # Color based on rate direction
    colors = [DISCORD_COLORS['success'] if rate >= 0 else DISCORD_COLORS['danger'] for rate in rates_list]
    
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(go.Bar(
        x=coins_list,
        y=rates_list,
        marker_color=colors,
        text=[f"{rate:.4f}%" for rate in rates_list],
        textposition='outside',
        textfont=dict(color=DISCORD_COLORS['light'], size=12),
        hovertemplate='<b>%{x}</b><br>Funding Rate: %{y:.4f}%<extra></extra>',
        name='Funding Rate'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=DISCORD_COLORS['muted'], opacity=0.5)
    
    # Update layout with Discord theme - FIXED: titlefont -> title with font
    fig.update_layout(
        title=dict(
            text="💰 Funding Rates by Asset",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Assets",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Funding Rate (%)",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5,
            zeroline=True,
            zerolinecolor=DISCORD_COLORS['muted']
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        hovermode='x unified',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_open_interest_chart(open_interest: Dict[str, float], coins: List[str]) -> go.Figure:
    """Create an open interest donut chart with Discord theme"""
    
    # Filter and prepare data
    filtered_oi = {coin: open_interest.get(coin, 0) for coin in coins if coin in open_interest and open_interest.get(coin, 0) > 0}
    
    if not filtered_oi:
        return create_empty_chart("No open interest data available")
    
    # Sort by value for better visualization
    sorted_oi = dict(sorted(filtered_oi.items(), key=lambda x: x[1], reverse=True))
    
    coins_list = list(sorted_oi.keys())
    oi_values = list(sorted_oi.values())
    
    # Generate colors
    colors = px.colors.qualitative.Set3[:len(coins_list)]
    
    fig = go.Figure()
    
    # Add donut chart
    fig.add_trace(go.Pie(
        labels=coins_list,
        values=oi_values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color=DISCORD_COLORS['darker'], width=2)),
        textfont=dict(color=DISCORD_COLORS['light'], size=12),
        hovertemplate='<b>%{label}</b><br>OI: $%{value:,.0f}<br>Share: %{percent}<extra></extra>',
        textinfo='label+percent',
        textposition='outside'
    ))
    
    # Add center text
    total_oi = sum(oi_values)
    fig.add_annotation(
        text=f"<b>Total OI</b><br>${total_oi/1e9:.2f}B",
        x=0.5, y=0.5,
        font=dict(size=16, color=DISCORD_COLORS['light'], family="Whitney"),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(
            text="📊 Open Interest Distribution",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01,
            font=dict(color=DISCORD_COLORS['light'])
        ),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_whale_activity_chart(whale_data: List[Dict]) -> go.Figure:
    """Create whale activity timeline chart"""
    
    if not whale_data:
        return create_empty_chart("No whale activity data available")
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(whale_data)
    
    # Ensure we have required columns
    required_cols = ['timestamp', 'symbol', 'activity', 'position_size']
    if not all(col in df.columns for col in required_cols):
        return create_empty_chart("Incomplete whale activity data")
    
    # Convert timestamp and sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Create color mapping
    df['color'] = df['activity'].apply(lambda x: 
        DISCORD_COLORS['success'] if 'buy' in x.lower() else 
        DISCORD_COLORS['danger'] if 'sell' in x.lower() else 
        DISCORD_COLORS['warning']
    )
    
    fig = go.Figure()
    
    # Add scatter plot for whale activities
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['position_size'],
        mode='markers',
        marker=dict(
            size=df['position_size'].apply(lambda x: min(max(x/1e6, 8), 25)),  # Scale marker size
            color=df['color'],
            line=dict(width=2, color=DISCORD_COLORS['light']),
            opacity=0.8
        ),
        text=df.apply(lambda row: f"{row['symbol']}<br>{row['activity']}<br>${row['position_size']:,.0f}", axis=1),
        hovertemplate='<b>%{text}</b><br>Time: %{x}<extra></extra>',
        name='Whale Activity'
    ))
    
    fig.update_layout(
        title=dict(
            text="🐋 Whale Activity Timeline",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Time",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Position Size ($)",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5,
            type='log'  # Log scale for better visualization
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        hovermode='closest',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_funding_history_chart(df: pd.DataFrame, coin: str) -> go.Figure:
    """Create funding rate history chart"""
    
    if df.empty:
        return create_empty_chart(f"No funding history available for {coin}")
    
    fig = go.Figure()
    
    # Add line chart
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['fundingRate'],
        mode='lines+markers',
        line=dict(color=DISCORD_COLORS['primary'], width=2),
        marker=dict(size=4, color=DISCORD_COLORS['primary']),
        fill='tonexty' if df['fundingRate'].min() < 0 else 'tozeroy',
        fillcolor=f"rgba{(*hex_to_rgb(DISCORD_COLORS['primary']), 0.1)}",
        hovertemplate='<b>%{x}</b><br>Funding Rate: %{y:.4f}%<extra></extra>',
        name=f'{coin} Funding Rate'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=DISCORD_COLORS['muted'], opacity=0.5)
    
    fig.update_layout(
        title=dict(
            text=f"📈 {coin} Funding Rate History",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Time",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Funding Rate (%)",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        hovermode='x unified',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_basis_comparison_chart(basis_data: Dict[str, float], coins: List[str]) -> go.Figure:
    """Create basis comparison chart"""
    
    filtered_basis = {coin: basis_data.get(coin, 0) for coin in coins if coin in basis_data}
    
    if not filtered_basis:
        return create_empty_chart("No basis data available")
    
    coins_list = list(filtered_basis.keys())
    basis_values = list(filtered_basis.values())
    
    # Color based on basis value
    colors = [
        DISCORD_COLORS['success'] if basis > 0.1 else 
        DISCORD_COLORS['danger'] if basis < -0.1 else 
        DISCORD_COLORS['warning'] 
        for basis in basis_values
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=coins_list,
        y=basis_values,
        marker_color=colors,
        text=[f"{basis:.3f}%" for basis in basis_values],
        textposition='outside',
        textfont=dict(color=DISCORD_COLORS['light'], size=12),
        hovertemplate='<b>%{x}</b><br>Basis: %{y:.3f}%<extra></extra>',
        name='Basis'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=DISCORD_COLORS['muted'], opacity=0.5)
    
    fig.update_layout(
        title=dict(
            text="📊 Futures vs Spot Basis",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Assets",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Basis (%)",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        hovermode='x unified',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_multi_metric_chart(data: Dict, coins: List[str]) -> go.Figure:
    """Create a comprehensive multi-metric chart with subplots"""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "💰 Funding Rates", 
            "📊 Open Interest", 
            "📈 24h Volume", 
            "⚖️ Basis"
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Extract data
    funding_rates = data.get('funding_rates', {})
    open_interest = data.get('open_interest', {})
    volume_data = data.get('perpetual_data', {}).get('volume_24h', {})
    basis_data = data.get('basis_data', {})
    
    # Filter coins that have data
    active_coins = [coin for coin in coins if any([
        coin in funding_rates,
        coin in open_interest,
        coin in volume_data,
        coin in basis_data
    ])]
    
    if not active_coins:
        return create_empty_chart("No data available for selected coins")
    
    # Funding Rates (top-left)
    if funding_rates:
        funding_values = [funding_rates.get(coin, 0) for coin in active_coins]
        funding_colors = [DISCORD_COLORS['success'] if rate >= 0 else DISCORD_COLORS['danger'] for rate in funding_values]
        
        fig.add_trace(
            go.Bar(
                x=active_coins,
                y=funding_values,
                marker_color=funding_colors,
                name="Funding Rate",
                showlegend=False,
                text=[f"{rate:.3f}%" for rate in funding_values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Funding: %{y:.4f}%<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Open Interest (top-right)
    if open_interest:
        oi_values = [open_interest.get(coin, 0) for coin in active_coins]
        
        fig.add_trace(
            go.Bar(
                x=active_coins,
                y=oi_values,
                marker_color=DISCORD_COLORS['info'],
                name="Open Interest",
                showlegend=False,
                text=[f"${val/1e6:.1f}M" if val > 1e6 else f"${val:,.0f}" for val in oi_values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>OI: $%{y:,.0f}<extra></extra>'
            ),
            row=1, col=2
        )
    
    # Volume 24h (bottom-left)
    if volume_data:
        volume_values = [volume_data.get(coin, 0) for coin in active_coins]
        
        fig.add_trace(
            go.Bar(
                x=active_coins,
                y=volume_values,
                marker_color=DISCORD_COLORS['secondary'],
                name="24h Volume",
                showlegend=False,
                text=[f"${val/1e6:.1f}M" if val > 1e6 else f"${val:,.0f}" for val in volume_values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Volume: $%{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Basis (bottom-right)
    if basis_data:
        basis_values = [basis_data.get(coin, 0) for coin in active_coins]
        basis_colors = [
            DISCORD_COLORS['success'] if basis > 0.1 else 
            DISCORD_COLORS['danger'] if basis < -0.1 else 
            DISCORD_COLORS['warning'] 
            for basis in basis_values
        ]
        
        fig.add_trace(
            go.Bar(
                x=active_coins,
                y=basis_values,
                marker_color=basis_colors,
                name="Basis",
                showlegend=False,
                text=[f"{basis:.3f}%" for basis in basis_values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Basis: %{y:.3f}%<extra></extra>'
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="📊 Multi-Metric Dashboard",
            font=dict(size=20, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        height=700,
        margin=dict(t=80, b=50, l=50, r=50)
    )
    
    # Update all axes
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(
                tickfont=dict(color=DISCORD_COLORS['light'], size=10),
                gridcolor=DISCORD_COLORS['muted'],
                gridwidth=0.5,
                row=i, col=j
            )
            fig.update_yaxes(
                tickfont=dict(color=DISCORD_COLORS['light'], size=10),
                gridcolor=DISCORD_COLORS['muted'],
                gridwidth=0.5,
                row=i, col=j
            )
    
    return fig

def create_anomaly_detection_chart(anomalies: List[Dict]) -> go.Figure:
    """Create chart for funding rate anomalies"""
    
    if not anomalies:
        return create_empty_chart("No anomalies detected")
    
    # Convert to DataFrame
    df = pd.DataFrame(anomalies)
    
    # Sort by absolute funding rate
    df = df.sort_values('funding_rate', key=abs, ascending=False)
    
    # Color mapping
    color_map = {
        'HIGH': DISCORD_COLORS['danger'],
        'MEDIUM': DISCORD_COLORS['warning'],
        'LOW': DISCORD_COLORS['info']
    }
    
    colors = [color_map.get(severity, DISCORD_COLORS['muted']) for severity in df['severity']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['coin'],
        y=df['funding_rate'],
        marker_color=colors,
        text=[f"{rate:.4f}%<br>{severity}" for rate, severity in zip(df['funding_rate'], df['severity'])],
        textposition='outside',
        textfont=dict(color=DISCORD_COLORS['light'], size=11),
        hovertemplate='<b>%{x}</b><br>%{customdata}<br>Rate: %{y:.4f}%<extra></extra>',
        customdata=df['description'],
        name='Anomalies'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color=DISCORD_COLORS['muted'], opacity=0.5)
    
    fig.update_layout(
        title=dict(
            text="🚨 Funding Rate Anomalies",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Assets",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Funding Rate (%)",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        hovermode='x unified',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_correlation_heatmap(correlation_data: pd.DataFrame) -> go.Figure:
    """Create correlation heatmap for funding rates"""
    
    if correlation_data.empty:
        return create_empty_chart("No correlation data available")
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_data.values,
        x=correlation_data.columns,
        y=correlation_data.index,
        colorscale='RdBu',
        zmid=0,
        text=correlation_data.round(3).values,
        texttemplate="%{text}",
        textfont={"size": 10, "color": "white"},
        hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="🔄 Funding Rate Correlations",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            tickfont=dict(color=DISCORD_COLORS['light']),
            side='bottom'
        ),
        yaxis=dict(
            tickfont=dict(color=DISCORD_COLORS['light'])
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        margin=dict(t=50, b=50, l=80, r=50)
    )
    
    return fig

def create_market_sentiment_gauge(sentiment_score: float) -> go.Figure:
    """Create a gauge chart for market sentiment based on funding rates"""
    
    # Normalize sentiment score to 0-100 scale
    normalized_score = max(0, min(100, (sentiment_score + 1) * 50))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=normalized_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Market Sentiment", 'font': {'color': DISCORD_COLORS['light'], 'size': 18}},
        delta={'reference': 50, 'increasing': {'color': DISCORD_COLORS['success']}, 'decreasing': {'color': DISCORD_COLORS['danger']}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': DISCORD_COLORS['light']},
            'bar': {'color': DISCORD_COLORS['primary']},
            'steps': [
                {'range': [0, 25], 'color': DISCORD_COLORS['danger']},
                {'range': [25, 50], 'color': DISCORD_COLORS['warning']},
                {'range': [50, 75], 'color': DISCORD_COLORS['info']},
                {'range': [75, 100], 'color': DISCORD_COLORS['success']}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': normalized_score
            }
        }
    ))
    
    fig.update_layout(
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_volume_analysis_chart(volume_data: Dict[str, List], timeframe: str = '24h') -> go.Figure:
    """Create volume analysis chart with trend indicators"""
    
    if not volume_data:
        return create_empty_chart("No volume data available")
    
    fig = go.Figure()
    
    coins = list(volume_data.keys())
    
    for i, coin in enumerate(coins[:10]):  # Limit to top 10 for readability
        volumes = volume_data[coin]
        if not volumes:
            continue
            
        x_values = list(range(len(volumes)))
        
        fig.add_trace(go.Scatter(
            x=x_values,
            y=volumes,
            mode='lines',
            name=coin,
            line=dict(width=2),
            hovertemplate=f'<b>{coin}</b><br>Volume: $%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=f"📈 Volume Analysis ({timeframe})",
            font=dict(size=18, color=DISCORD_COLORS['light'], family="Whitney"),
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Time",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        yaxis=dict(
            title=dict(
                text="Volume ($)",
                font=dict(color=DISCORD_COLORS['light'])
            ),
            tickfont=dict(color=DISCORD_COLORS['light']),
            gridcolor=DISCORD_COLORS['muted'],
            gridwidth=0.5
        ),
        plot_bgcolor=DISCORD_COLORS['dark'],
        paper_bgcolor=DISCORD_COLORS['darker'],
        font=dict(family="Whitney", color=DISCORD_COLORS['light']),
        hovermode='x unified',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig