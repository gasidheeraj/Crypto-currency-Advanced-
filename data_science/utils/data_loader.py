"""
Data Loader - Load cryptocurrency data from PostgreSQL
"""
import numpy as np
from data_engineering.config.database import DatabaseConfig
from loguru import logger

class CryptoDataLoader:
    """Load cryptocurrency data from database"""
    
    def __init__(self):
        """Initialize database connection"""
        self.db = DatabaseConfig()
        self.db.connect()
        logger.info("✅ Database connected")
    
    def get_all_cryptos(self):
        """
        Get list of all cryptocurrencies
        
        Returns:
            list: List of dictionaries with crypto info
        """
        query = """
            SELECT crypto_id, symbol, name
            FROM crypto_metadata
            ORDER BY name
        """
        
        result = self.db.execute_query(query, fetch=True)
        logger.info(f"✅ Found {len(result)} cryptocurrencies")
        return result
    
    def get_price_data(self, crypto_id, days=None):
        """
        Get price data for one cryptocurrency
        
        Args:
            crypto_id: e.g., 'bitcoin'
            days: Number of days (None = all data)
        
        Returns:
            dict: Contains timestamps, prices, volumes as numpy arrays
        """
        if days:
            query = """
                SELECT timestamp, close, volume
                FROM price_data
                WHERE crypto_id = %s
                AND timestamp >= NOW() - INTERVAL '%s days'
                ORDER BY timestamp ASC
            """
            params = (crypto_id, days)
        else:
            query = """
                SELECT timestamp, close, volume
                FROM price_data
                WHERE crypto_id = %s
                ORDER BY timestamp ASC
            """
            params = (crypto_id,)
        
        result = self.db.execute_query(query, params=params, fetch=True)
        
        if not result:
            logger.warning(f"⚠️ No data for {crypto_id}")
            return None
        
        # Convert to numpy arrays
        data = {
            'timestamps': np.array([r['timestamp'] for r in result]),
            'prices': np.array([float(r['close']) for r in result]),
            'volumes': np.array([float(r['volume']) if r['volume'] else 0 for r in result])
        }
        
        logger.info(f"✅ Loaded {len(result)} records for {crypto_id}")
        return data
    
    def close(self):
        """Close database connection"""
        self.db.close()
        logger.info("🔒 Connection closed")