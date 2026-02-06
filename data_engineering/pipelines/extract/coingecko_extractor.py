"""
CoinGecko API Data Extractor
"""
import requests
from datetime import datetime
from loguru import logger
from data_engineering.config.settings import settings
from data_engineering.utils.helpers import retry, timing_decorator, rate_limit

class CoinGeckoExtractor:
    """Extract cryptocurrency data from CoinGecko API"""
    
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({'x-cg-pro-api-key': self.api_key})
    
    @retry(max_attempts=3, delay=2)
    @rate_limit(min_interval=1.2)
    @timing_decorator
    def fetch_market_data(self, crypto_ids):
        """Fetch current market data for multiple cryptocurrencies"""
        url = f"{self.base_url}/coins/markets"
        
        params = {
            'vs_currency': 'usd',
            'ids': ','.join(crypto_ids),
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h,7d,30d'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Fetched market data for {len(data)} cryptocurrencies")
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ CoinGecko API error: {e}")
            raise
    
    @retry(max_attempts=3, delay=2)
    @rate_limit(min_interval=1.2)
    def fetch_ohlc_data(self, crypto_id, days=1):
        """Fetch OHLC data for a single cryptocurrency"""
        url = f"{self.base_url}/coins/{crypto_id}/ohlc"
        
        params = {
            'vs_currency': 'usd',
            'days': days
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Fetched OHLC data for {crypto_id}: {len(data)} records")
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ OHLC fetch error for {crypto_id}: {e}")
            return []
    
    def close(self):
        """Close session"""
        self.session.close()
        logger.info("🔒 CoinGecko extractor session closed")