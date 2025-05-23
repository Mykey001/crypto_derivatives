# services/liquidation_tracker.py
import asyncio
import aiohttp
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random
import logging

class LiquidationTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://fapi.binance.com"  # Binance Futures API
        
    async def get_liquidation_data(self, coins: List[str]) -> Dict:
        """Get liquidation data for specified coins"""
        liquidation_data = {}
        
        for coin in coins:
            try:
                # Simulate realistic liquidation data
                # In production, this would fetch from liquidation APIs
                long_liquidations = random.uniform(1, 50) * 1000000
                short_liquidations = random.uniform(1, 30) * 1000000
                
                liquidation_data[coin] = {
                    'total': long_liquidations + short_liquidations,
                    'long_liquidations': long_liquidations,
                    'short_liquidations': short_liquidations,
                    'liquidation_ratio': long_liquidations / (long_liquidations + short_liquidations) if (long_liquidations + short_liquidations) > 0 else 0.5,
                    'avg_liquidation_size': random.uniform(10000, 500000),
                    'liquidation_count': random.randint(50, 500)
                }
                
            except Exception as e:
                self.logger.warning(f"Error fetching liquidation data for {coin}: {e}")
                liquidation_data[coin] = {
                    'total': 0,
                    'long_liquidations': 0,
                    'short_liquidations': 0,
                    'liquidation_ratio': 0.5,
                    'avg_liquidation_size': 0,
                    'liquidation_count': 0
                }
        
        return liquidation_data
    
    async def get_liquidation_heatmap_data(self, coins: List[str]) -> Dict:
        """Get liquidation concentration data for heatmap"""
        heatmap_data = {}
        
        price_levels = ['Support 1', 'Support 2', 'Current', 'Resistance 1', 'Resistance 2']
        
        for coin in coins:
            coin_data = {}
            for level in price_levels:
                # Simulate liquidation concentration at different price levels
                long_liq = random.uniform(0, 100) * 1000000
                short_liq = random.uniform(0, 80) * 1000000
                
                coin_data[level] = {
                    'long_liquidations': long_liq,
                    'short_liquidations': short_liq,
                    'total_liquidations': long_liq + short_liq,
                    'price_distance': random.uniform(-10, 10)  # % from current price
                }
            
            heatmap_data[coin] = coin_data
        
        return heatmap_data
    
    async def get_recent_liquidations(self, coins: List[str], limit: int = 20) -> List[Dict]:
        """Get recent liquidation events"""
        liquidations = []
        current_time = datetime.now()
        
        for i in range(limit):
            coin = random.choice(coins)
            side = random.choice(['Long', 'Short'])
            
            # Generate realistic liquidation sizes
            if coin in ['BTC', 'ETH']:
                size = random.uniform(50000, 2000000)  # $50K to $2M
            else:
                size = random.uniform(10000, 500000)   # $10K to $500K
            
            # Base prices for realistic liquidation prices
            base_prices = {
                'BTC': 67000, 'ETH': 2650, 'SOL': 178, 'AVAX': 35,
                'MATIC': 0.85, 'ARB': 1.2, 'OP': 2.1, 'DOGE': 0.16,
                'ADA': 0.45, 'DOT': 7.2, 'LINK': 14.5, 'UNI': 8.9
            }
            
            base_price = base_prices.get(coin, random.uniform(1, 100))
            price_variation = random.uniform(-0.02, 0.02)  # ±2% variation
            liquidation_price = base_price * (1 + price_variation)
            
            liquidation = {
                'timestamp': current_time - timedelta(minutes=random.randint(1, 60)),
                'symbol': f"{coin}/USDT",
                'side': side,
                'size': size,
                'price': liquidation_price,
                'exchange': random.choice(['Binance', 'Bybit', 'OKX']),
                'leverage': random.randint(5, 50)
            }
            liquidations.append(liquidation)
        
        # Sort by timestamp (most recent first)
        liquidations.sort(key=lambda x: x['timestamp'], reverse=True)
        return liquidations
    
    async def get_liquidation_stats(self, coins: List[str], timeframe: str = '24h') -> Dict:
        """Get liquidation statistics"""
        stats = {
            'total_liquidations': 0,
            'long_percentage': 0,
            'short_percentage': 0,
            'largest_liquidation': 0,
            'most_liquidated_coin': '',
            'liquidation_trend': 'NEUTRAL'
        }
        
        liquidation_data = await self.get_liquidation_data(coins)
        
        total_liq = sum([data['total'] for data in liquidation_data.values()])
        total_long_liq = sum([data['long_liquidations'] for data in liquidation_data.values()])
        total_short_liq = sum([data['short_liquidations'] for data in liquidation_data.values()])
        
        stats['total_liquidations'] = total_liq
        stats['long_percentage'] = (total_long_liq / total_liq * 100) if total_liq > 0 else 0
        stats['short_percentage'] = (total_short_liq / total_liq * 100) if total_liq > 0 else 0
        
        # Find most liquidated coin
        if liquidation_data:
            most_liquidated = max(liquidation_data.items(), key=lambda x: x[1]['total'])
            stats['most_liquidated_coin'] = most_liquidated[0]
            stats['largest_liquidation'] = max([data['avg_liquidation_size'] for data in liquidation_data.values()])
        
        # Determine trend
        if stats['long_percentage'] > 60:
            stats['liquidation_trend'] = 'BEARISH'  # More longs liquidated = bearish
        elif stats['short_percentage'] > 60:
            stats['liquidation_trend'] = 'BULLISH'  # More shorts liquidated = bullish
        else:
            stats['liquidation_trend'] = 'NEUTRAL'
        
        return stats
    
    async def predict_liquidation_zones(self, coin: str) -> Dict:
        """Predict potential liquidation zones"""
        # In production, this would analyze order book and position data
        current_price = random.uniform(50, 70000)  # Simulate current price
        
        zones = {
            'support_zones': [
                {
                    'price': current_price * 0.95,
                    'liquidation_amount': random.uniform(10, 100) * 1000000,
                    'side': 'Long',
                    'strength': 'Strong'
                },
                {
                    'price': current_price * 0.90,
                    'liquidation_amount': random.uniform(20, 150) * 1000000,
                    'side': 'Long',
                    'strength': 'Very Strong'
                }
            ],
            'resistance_zones': [
                {
                    'price': current_price * 1.05,
                    'liquidation_amount': random.uniform(15, 80) * 1000000,
                    'side': 'Short',
                    'strength': 'Moderate'
                },
                {
                    'price': current_price * 1.10,
                    'liquidation_amount': random.uniform(25, 120) * 1000000,
                    'side': 'Short',
                    'strength': 'Strong'
                }
            ]
        }
        
        return zones