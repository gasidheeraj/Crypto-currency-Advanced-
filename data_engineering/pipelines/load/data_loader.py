"""
Data Loading Module
"""
from loguru import logger
from data_engineering.config.database import DatabaseConfig

class DataLoader:
    """Load transformed data into PostgreSQL database"""
    
    def __init__(self):
        self.db = DatabaseConfig()
        self.db.connect()
    
    def load_market_data(self, data):
        """Load market data into database"""
        if not data:
            logger.warning("⚠️  No market data to load")
            return 0
        
        cursor = self.db.get_cursor(dict_cursor=False)
        
        insert_query = """
            INSERT INTO market_data 
            (crypto_id, timestamp, market_cap, total_volume, circulating_supply, 
             max_supply, price_change_24h, price_change_percentage_24h,
             price_change_percentage_7d, price_change_percentage_30d,
             market_cap_rank, ath, ath_date, atl, atl_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (crypto_id, timestamp) DO UPDATE SET
                market_cap = EXCLUDED.market_cap,
                total_volume = EXCLUDED.total_volume,
                circulating_supply = EXCLUDED.circulating_supply,
                max_supply = EXCLUDED.max_supply,
                price_change_24h = EXCLUDED.price_change_24h,
                price_change_percentage_24h = EXCLUDED.price_change_percentage_24h,
                price_change_percentage_7d = EXCLUDED.price_change_percentage_7d,
                price_change_percentage_30d = EXCLUDED.price_change_percentage_30d,
                market_cap_rank = EXCLUDED.market_cap_rank,
                ath = EXCLUDED.ath,
                ath_date = EXCLUDED.ath_date,
                atl = EXCLUDED.atl,
                atl_date = EXCLUDED.atl_date
        """
        
        records_loaded = 0
        for item in data:
            try:
                cursor.execute(insert_query, (
                    item['crypto_id'],
                    item['timestamp'],
                    item['market_cap'],
                    item['total_volume'],
                    item['circulating_supply'],
                    item['max_supply'],
                    item['price_change_24h'],
                    item['price_change_percentage_24h'],
                    item.get('price_change_percentage_7d'),
                    item.get('price_change_percentage_30d'),
                    item['market_cap_rank'],
                    item.get('ath'),
                    item.get('ath_date'),
                    item.get('atl'),
                    item.get('atl_date')
                ))
                records_loaded += 1
            except Exception as e:
                logger.error(f"❌ Error loading market data for {item['crypto_id']}: {e}")
        
        self.db.conn.commit()
        logger.info(f"✅ Loaded {records_loaded} market data records")
        return records_loaded
    
    def load_price_data(self, data):
        """Load price data into database"""
        if not data:
            logger.warning("⚠️  No price data to load")
            return 0
        
        cursor = self.db.get_cursor(dict_cursor=False)
        
        insert_query = """
            INSERT INTO price_data 
            (crypto_id, timestamp, open, high, low, close, volume, market_cap)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (crypto_id, timestamp) DO UPDATE SET
                open = COALESCE(EXCLUDED.open, price_data.open),
                high = COALESCE(EXCLUDED.high, price_data.high),
                low = COALESCE(EXCLUDED.low, price_data.low),
                close = EXCLUDED.close,
                volume = COALESCE(EXCLUDED.volume, price_data.volume),
                market_cap = COALESCE(EXCLUDED.market_cap, price_data.market_cap)
        """
        
        records_loaded = 0
        for item in data:
            try:
                cursor.execute(insert_query, (
                    item['crypto_id'],
                    item['timestamp'],
                    item.get('open'),
                    item.get('high'),
                    item.get('low'),
                    item.get('close'),
                    item.get('volume'),
                    item.get('market_cap')
                ))
                records_loaded += 1
            except Exception as e:
                logger.error(f"❌ Error loading price data for {item['crypto_id']}: {e}")
        
        self.db.conn.commit()
        logger.info(f"✅ Loaded {records_loaded} price data records")
        return records_loaded
    
    def log_pipeline_execution(self, pipeline_name, status, records_processed, 
                               execution_time, error_message=None, started_at=None):
        """Log pipeline execution to database"""
        cursor = self.db.get_cursor(dict_cursor=False)
        
        insert_query = """
            INSERT INTO pipeline_logs 
            (pipeline_name, status, records_processed, execution_time_seconds, 
             error_message, started_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            pipeline_name,
            status,
            records_processed,
            execution_time,
            error_message,
            started_at
        ))
        
        self.db.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.db.close()