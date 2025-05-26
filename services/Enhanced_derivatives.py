# services/Enhanced_derivatives.py
import ccxt
import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import os

class EnhancedDerivativesService:
    def __init__(self):
        # Initialize multiple exchanges for broader coverage
        self.exchanges = {
            'binance': ccxt.binance({
                'apiKey': os.getenv('BINANCE_API_KEY'),
                'secret': os.getenv('BINANCE_SECRET'),
                'enableRateLimit': True, 
                'options': {'defaultType': 'future'},
                'timeout': 10000,
                'sandbox': False
            }),
            'bybit': ccxt.bybit({
                'apiKey': os.getenv('BYBIT_API_KEY'),
                'secret': os.getenv('BYBIT_SECRET'),
                'enableRateLimit': True,
                'options': {'defaultType': 'linear'},
                'timeout': 10000,
                'sandbox': False
            }),
            'okx': ccxt.okx({
                'apiKey': os.getenv('OKX_API_KEY'),
                'secret': os.getenv('OKX_SECRET'),
                'password': os.getenv('OKX_PASSPHRASE'),
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'},
                'timeout': 10000,
                'sandbox': False
            })
        }
        
        # Extended coin list matching your app's expectations
        self.supported_coins = [
            'BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'ARB', 'OP', 'DOGE', 
            'ADA', 'DOT', 'LINK', 'UNI', 'AAVE', 'COMP', 'MKR', 'SNX',
            'CRV', 'SUSHI', 'YFI', 'BAL', 'REN', 'KNC', 'ZRX', 'BAND',
            'ALGO', 'ATOM', 'NEAR', 'FTM', 'LUNA', 'ICP', 'VET', 'TRX',
            'EOS', 'XTZ', 'THETA', 'FIL', 'EGLD', 'HBAR', 'FLOW', 'MANA',
            'XRP', 'LTC', 'BCH', 'ETC', 'XLM', 'DASH', 'ZEC', 'XMR'
        ]
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Cache for reducing API calls
        self._cache = {}
        self._cache_ttl = 60  # seconds
        
    def _get_cache_key(self, method: str, *args) -> str:
        """Generate cache key for method and arguments"""
        return f"{method}:{':'.join(map(str, args))}"
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        return (datetime.now() - self._cache[key]['timestamp']).seconds < self._cache_ttl
    
    def _get_cached_data(self, key: str):
        """Get cached data if valid"""
        if self._is_cache_valid(key):
            return self._cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data):
        """Set data in cache"""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_multi_coin_funding_rates(self, coins: List[str]) -> Dict[str, float]:
        """Get funding rates for multiple coins across exchanges with caching"""
        cache_key = self._get_cache_key('funding_rates', *sorted(coins))
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        funding_rates = {}
        
        # Process coins in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i + batch_size]
            
            for coin in batch:
                if coin not in self.supported_coins:
                    continue
                    
                funding_rate = await self._get_funding_rate_for_coin(coin)
                funding_rates[coin] = funding_rate
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.1)
        
        self._set_cache(cache_key, funding_rates)
        return funding_rates
    
    async def _get_funding_rate_for_coin(self, coin: str) -> float:
        """Get funding rate for a single coin with fallback exchanges"""
        for exchange_name, exchange in self.exchanges.items():
            try:
                symbol = f"{coin}/USDT:USDT"
                
                # Special handling for different exchanges
                if exchange_name == 'okx':
                    symbol = f"{coin}-USDT-SWAP"
                elif exchange_name == 'bybit' and coin in ['BTC', 'ETH']:
                    symbol = f"{coin}USDT"
                
                rate = exchange.fetch_funding_rate(symbol)
                if rate and rate.get('fundingRate'):
                    return rate['fundingRate'] * 100
                    
            except Exception as e:
                self.logger.debug(f"Failed to fetch funding rate for {coin} on {exchange_name}: {e}")
                continue
        
        self.logger.warning(f"Could not fetch funding rate for {coin} from any exchange")
        return 0.0
    
    async def get_multi_coin_open_interest(self, coins: List[str]) -> Dict[str, float]:
        """Get open interest for multiple coins with caching"""
        cache_key = self._get_cache_key('open_interest', *sorted(coins))
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        open_interest = {}
        
        for coin in coins:
            if coin not in self.supported_coins:
                continue
                
            oi_value = await self._get_open_interest_for_coin(coin)
            open_interest[coin] = oi_value
            await asyncio.sleep(0.1)
        
        self._set_cache(cache_key, open_interest)
        return open_interest
    
    async def _get_open_interest_for_coin(self, coin: str) -> float:
        """Get open interest for a single coin with fallback exchanges"""
        for exchange_name, exchange in self.exchanges.items():
            try:
                symbol = f"{coin}/USDT:USDT"
                
                if exchange_name == 'okx':
                    symbol = f"{coin}-USDT-SWAP"
                elif exchange_name == 'bybit' and coin in ['BTC', 'ETH']:
                    symbol = f"{coin}USDT"
                
                oi = exchange.fetch_open_interest(symbol)
                if oi and oi.get('openInterestValue'):
                    return float(oi['openInterestValue'])
                    
            except Exception as e:
                self.logger.debug(f"Failed to fetch OI for {coin} on {exchange_name}: {e}")
                continue
        
        self.logger.warning(f"Could not fetch open interest for {coin} from any exchange")
        return 0.0
    
    async def get_funding_history(self, coin: str, days: int = 7) -> pd.DataFrame:
        """Get historical funding rates for analysis"""
        try:
            symbol = f"{coin}/USDT:USDT"
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Try Binance first as it has good historical data
            funding_history = self.exchanges['binance'].fetch_funding_rate_history(
                symbol, since=since, limit=1000
            )
            
            if not funding_history:
                return pd.DataFrame()
            
            df = pd.DataFrame(funding_history)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['fundingRate'] = df['fundingRate'] * 100
            
            return df[['datetime', 'fundingRate']].sort_values('datetime')
            
        except Exception as e:
            self.logger.error(f"Error fetching funding history for {coin}: {e}")
            return pd.DataFrame()
    
    async def get_perpetual_data(self, coins: List[str]) -> Dict:
        """Get comprehensive perpetual futures data with improved error handling"""
        cache_key = self._get_cache_key('perpetual_data', *sorted(coins))
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        data = {
            'funding_rates': {},
            'open_interest': {},
            'volume_24h': {},
            'mark_prices': {},
            'next_funding_time': {}
        }
        
        # Get funding rates and OI using existing methods
        funding_rates = await self.get_multi_coin_funding_rates(coins)
        open_interest = await self.get_multi_coin_open_interest(coins)
        
        data['funding_rates'] = funding_rates
        data['open_interest'] = open_interest
        
        # Get additional data
        for coin in coins:
            if coin not in self.supported_coins:
                continue
                
            ticker_data = await self._get_ticker_data_for_coin(coin)
            data['volume_24h'][coin] = ticker_data.get('volume', 0)
            data['mark_prices'][coin] = ticker_data.get('mark_price', 0)
            data['next_funding_time'][coin] = ticker_data.get('funding_time')
        
        self._set_cache(cache_key, data)
        return data
    
    async def _get_ticker_data_for_coin(self, coin: str) -> Dict:
        """Get ticker data for a single coin"""
        for exchange_name, exchange in self.exchanges.items():
            try:
                symbol = f"{coin}/USDT:USDT"
                
                if exchange_name == 'okx':
                    symbol = f"{coin}-USDT-SWAP"
                elif exchange_name == 'bybit' and coin in ['BTC', 'ETH']:
                    symbol = f"{coin}USDT"
                
                ticker = exchange.fetch_ticker(symbol)
                if ticker:
                    return {
                        'volume': ticker.get('quoteVolume', 0),
                        'mark_price': ticker.get('mark', ticker.get('last', 0)),
                        'funding_time': None  # Would need separate call for this
                    }
                    
            except Exception as e:
                self.logger.debug(f"Failed to fetch ticker for {coin} on {exchange_name}: {e}")
                continue
        
        return {'volume': 0, 'mark_price': 0, 'funding_time': None}
    
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
                    'timestamp': datetime.now(),
                    'description': f'{coin} funding rate at {rate:.4f}% ({"bullish" if rate > 0 else "bearish"} pressure)'
                }
                anomalies.append(anomaly)
        
        return sorted(anomalies, key=lambda x: abs(x['funding_rate']), reverse=True)
    
    def get_supported_coins(self) -> List[str]:
        """Return list of supported coins"""
        return self.supported_coins.copy()
    
    async def get_basis_data(self, coins: List[str]) -> Dict[str, float]:
        """Calculate basis (futures vs spot premium) with caching"""
        cache_key = self._get_cache_key('basis_data', *sorted(coins))
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        basis_data = {}
        
        for coin in coins:
            if coin not in self.supported_coins:
                continue
                
            basis = await self._calculate_basis_for_coin(coin)
            basis_data[coin] = basis
            await asyncio.sleep(0.1)
        
        self._set_cache(cache_key, basis_data)
        return basis_data
    
    async def _calculate_basis_for_coin(self, coin: str) -> float:
        """Calculate basis for a single coin"""
        try:
            # Get futures and spot prices from the same exchange
            exchange = self.exchanges['binance']
            
            # Get futures price
            futures_symbol = f"{coin}/USDT:USDT"
            futures_ticker = exchange.fetch_ticker(futures_symbol)
            futures_price = futures_ticker['last']
            
            # Get spot price
            spot_symbol = f"{coin}/USDT"
            spot_ticker = exchange.fetch_ticker(spot_symbol)
            spot_price = spot_ticker['last']
            
            if futures_price and spot_price and spot_price > 0:
                # Calculate basis as percentage
                basis = ((futures_price - spot_price) / spot_price) * 100
                return basis
            
        except Exception as e:
            self.logger.debug(f"Could not calculate basis for {coin}: {e}")
        
        return 0.0
    
    async def get_market_summary(self, coins: List[str]) -> Dict:
        """Get comprehensive market summary for dashboard"""
        try:
            # Get all data concurrently
            funding_task = self.get_multi_coin_funding_rates(coins)
            oi_task = self.get_multi_coin_open_interest(coins)
            perp_task = self.get_perpetual_data(coins)
            basis_task = self.get_basis_data(coins)
            
            funding_rates, open_interest, perp_data, basis_data = await asyncio.gather(
                funding_task, oi_task, perp_task, basis_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(funding_rates, Exception):
                funding_rates = {}
            if isinstance(open_interest, Exception):
                open_interest = {}
            if isinstance(perp_data, Exception):
                perp_data = {'funding_rates': {}, 'open_interest': {}, 'volume_24h': {}, 'mark_prices': {}}
            if isinstance(basis_data, Exception):
                basis_data = {}
            
            return {
                'funding_rates': funding_rates,
                'open_interest': open_interest,
                'perpetual_data': perp_data,
                'basis_data': basis_data,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market summary: {e}")
            return {
                'funding_rates': {},
                'open_interest': {},
                'perpetual_data': {'funding_rates': {}, 'open_interest': {}, 'volume_24h': {}, 'mark_prices': {}},
                'basis_data': {},
                'timestamp': datetime.now()
            }
    
    def clear_cache(self):
        """Clear the cache manually"""
        self._cache.clear()
        self.logger.info("Cache cleared")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all exchanges"""
        health = {}
        
        for name, exchange in self.exchanges.items():
            try:
                # Try to fetch BTC ticker as health check
                ticker = exchange.fetch_ticker('BTC/USDT')
                health[name] = bool(ticker and ticker.get('last'))
            except:
                health[name] = False
        
        return health