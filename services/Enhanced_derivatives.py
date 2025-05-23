# services/enhanced_derivatives.py
import ccxt
import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

class EnhancedDerivativesService:
    def __init__(self):
        # Initialize multiple exchanges for broader coverage
        self.exchanges = {
            'binance': ccxt.binance({
                'enableRateLimit': True, 
                'options': {'defaultType': 'future'},
                'timeout': 10000
            }),
            'bybit': ccxt.bybit({
                'enableRateLimit': True,
                'options': {'defaultType': 'linear'},
                'timeout': 10000
            }),
            'okx': ccxt.okx({
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'},
                'timeout': 10000
            })
        }
        
        # Extended coin list with more altcoins
        self.supported_coins = [
            'BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'ARB', 'OP', 'DOGE', 
            'ADA', 'DOT', 'LINK', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX',
            'CRV', 'SUSHI', 'YFI', 'BAL', 'REN', 'KNC', 'ZRX', 'BAND',
            'ALGO', 'ATOM', 'NEAR', 'FTM', 'LUNA', 'ICP', 'VET', 'TRX',
            'EOS', 'XTZ', 'THETA', 'FIL', 'EGLD', 'HBAR', 'FLOW', 'MANA'
        ]
        
        self.logger = logging.getLogger(__name__)
        
    async def get_multi_coin_funding_rates(self, coins: List[str]) -> Dict[str, float]:
        """Get funding rates for multiple coins across exchanges"""
        funding_rates = {}
        
        for coin in coins:
            if coin not in self.supported_coins:
                continue
                
            try:
                # Try Binance first
                symbol = f"{coin}/USDT:USDT"
                rate = self.exchanges['binance'].fetch_funding_rate(symbol)
                funding_rates[coin] = rate['fundingRate'] * 100 if rate['fundingRate'] else 0
                
            except Exception as e:
                try:
                    # Fallback to Bybit
                    symbol = f"{coin}/USDT:USDT"
                    rate = self.exchanges['bybit'].fetch_funding_rate(symbol)
                    funding_rates[coin] = rate['fundingRate'] * 100 if rate['fundingRate'] else 0
                    
                except Exception as e2:
                    self.logger.warning(f"Could not fetch funding rate for {coin}: {e2}")
                    funding_rates[coin] = 0
                    
        return funding_rates
    
    async def get_multi_coin_open_interest(self, coins: List[str]) -> Dict[str, float]:
        """Get open interest for multiple coins"""
        open_interest = {}
        
        for coin in coins:
            if coin not in self.supported_coins:
                continue
                
            try:
                symbol = f"{coin}/USDT:USDT"
                oi = self.exchanges['binance'].fetch_open_interest(symbol)
                open_interest[coin] = oi['openInterestValue'] if oi['openInterestValue'] else 0
                
            except Exception as e:
                try:
                    # Fallback to Bybit
                    oi = self.exchanges['bybit'].fetch_open_interest(symbol)
                    open_interest[coin] = oi['openInterestValue'] if oi['openInterestValue'] else 0
                    
                except Exception as e2:
                    self.logger.warning(f"Could not fetch OI for {coin}: {e2}")
                    open_interest[coin] = 0
                    
        return open_interest
    
    async def get_funding_history(self, coin: str, days: int = 7) -> pd.DataFrame:
        """Get historical funding rates for analysis"""
        try:
            symbol = f"{coin}/USDT:USDT"
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            funding_history = self.exchanges['binance'].fetch_funding_rate_history(
                symbol, since=since, limit=1000
            )
            
            df = pd.DataFrame(funding_history)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['fundingRate'] = df['fundingRate'] * 100
            
            return df[['datetime', 'fundingRate']]
            
        except Exception as e:
            self.logger.error(f"Error fetching funding history for {coin}: {e}")
            return pd.DataFrame()
    
    async def get_perpetual_data(self, coins: List[str]) -> Dict:
        """Get comprehensive perpetual futures data"""
        data = {
            'funding_rates': {},
            'open_interest': {},
            'volume_24h': {},
            'mark_prices': {},
            'next_funding_time': {}
        }
        
        for coin in coins:
            try:
                symbol = f"{coin}/USDT:USDT"
                
                # Get ticker data
                ticker = self.exchanges['binance'].fetch_ticker(symbol)
                data['volume_24h'][coin] = ticker['quoteVolume'] if ticker['quoteVolume'] else 0
                data['mark_prices'][coin] = ticker['mark'] if ticker['mark'] else ticker['last']
                
                # Get funding rate
                funding = self.exchanges['binance'].fetch_funding_rate(symbol)
                data['funding_rates'][coin] = funding['fundingRate'] * 100 if funding['fundingRate'] else 0
                data['next_funding_time'][coin] = funding['fundingDatetime'] if funding['fundingDatetime'] else None
                
                # Get open interest
                oi = self.exchanges['binance'].fetch_open_interest(symbol)
                data['open_interest'][coin] = oi['openInterestValue'] if oi['openInterestValue'] else 0
                
            except Exception as e:
                self.logger.warning(f"Error fetching data for {coin}: {e}")
                # Set default values
                data['funding_rates'][coin] = 0
                data['open_interest'][coin] = 0
                data['volume_24h'][coin] = 0
                data['mark_prices'][coin] = 0
                data['next_funding_time'][coin] = None
        
        return data
    
    async def detect_funding_anomalies(self, coins: List[str], threshold: float = 0.5) -> List[Dict]:
        """Detect unusual funding rate patterns"""
        anomalies = []
        funding_rates = await self.get_multi_coin_funding_rates(coins)
        
        for coin, rate in funding_rates.items():
            if abs(rate) > threshold:
                anomaly = {
                    'coin': coin,
                    'funding_rate': rate,
                    'severity': 'HIGH' if abs(rate) > 1.0 else 'MEDIUM',
                    'direction': 'BULLISH' if rate > 0 else 'BEARISH',
                    'timestamp': datetime.now()
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def get_supported_coins(self) -> List[str]:
        """Return list of supported coins"""
        return self.supported_coins.copy()
    
    async def get_basis_data(self, coins: List[str]) -> Dict[str, float]:
        """Calculate basis (futures vs spot premium)"""
        basis_data = {}
        
        for coin in coins:
            try:
                # Get futures price
                futures_symbol = f"{coin}/USDT:USDT"
                futures_ticker = self.exchanges['binance'].fetch_ticker(futures_symbol)
                futures_price = futures_ticker['last']
                
                # Get spot price
                spot_symbol = f"{coin}/USDT"
                spot_ticker = self.exchanges['binance'].fetch_ticker(spot_symbol)
                spot_price = spot_ticker['last']
                
                # Calculate basis as percentage
                basis = ((futures_price - spot_price) / spot_price) * 100
                basis_data[coin] = basis
                
            except Exception as e:
                self.logger.warning(f"Could not calculate basis for {coin}: {e}")
                basis_data[coin] = 0
        
        return basis_data