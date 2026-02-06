"""
Data Transformation Module
"""
from datetime import datetime
from loguru import logger

class DataTransformer:
    """Transform raw API data into database-ready format"""
    
    @staticmethod
    def transform_market_data(raw_data):
        """Transform market data from CoinGecko format"""
        transformed = []
        
        for item in raw_data:
            try:
                transformed_item = {
                    'crypto_id': item.get('id'),
                    'timestamp': datetime.now(),
                    'market_cap': item.get('market_cap'),
                    'total_volume': item.get('total_volume'),
                    'circulating_supply': item.get('circulating_supply'),
                    'max_supply': item.get('max_supply'),
                    'price_change_24h': item.get('price_change_24h'),
                    'price_change_percentage_24h': item.get('price_change_percentage_24h'),
                    'price_change_percentage_7d': item.get('price_change_percentage_7d_in_currency'),
                    'price_change_percentage_30d': item.get('price_change_percentage_30d_in_currency'),
                    'market_cap_rank': item.get('market_cap_rank'),
                    'ath': item.get('ath'),
                    'ath_date': datetime.fromisoformat(item['ath_date'].replace('Z', '+00:00')) if item.get('ath_date') else None,
                    'atl': item.get('atl'),
                    'atl_date': datetime.fromisoformat(item['atl_date'].replace('Z', '+00:00')) if item.get('atl_date') else None
                }
                transformed.append(transformed_item)
            
            except Exception as e:
                logger.warning(f"⚠️  Error transforming market data for {item.get('id')}: {e}")
                continue
        
        logger.info(f"✅ Transformed {len(transformed)} market data records")
        return transformed
    
    @staticmethod
    def transform_price_data(raw_data):
        """Transform price data from CoinGecko format"""
        transformed = []
        
        for item in raw_data:
            try:
                transformed_item = {
                    'crypto_id': item.get('id'),
                    'timestamp': datetime.now(),
                    'close': item.get('current_price'),
                    'high': item.get('high_24h'),
                    'low': item.get('low_24h'),
                    'volume': item.get('total_volume'),
                    'market_cap': item.get('market_cap')
                }
                transformed.append(transformed_item)
            
            except Exception as e:
                logger.warning(f"⚠️  Error transforming price for {item.get('id')}: {e}")
                continue
        
        logger.info(f"✅ Transformed {len(transformed)} price data records")
        return transformed
    
    @staticmethod
    def transform_ohlc_data(crypto_id, raw_ohlc):
        """Transform OHLC data from CoinGecko format"""
        transformed = []
        
        for ohlc in raw_ohlc:
            try:
                transformed_item = {
                    'crypto_id': crypto_id,
                    'timestamp': datetime.fromtimestamp(ohlc[0] / 1000),
                    'open': ohlc[1],
                    'high': ohlc[2],
                    'low': ohlc[3],
                    'close': ohlc[4],
                    'volume': None,
                    'market_cap': None
                }
                transformed.append(transformed_item)
            
            except Exception as e:
                logger.warning(f"⚠️  Error transforming OHLC for {crypto_id}: {e}")
                continue
        
        logger.info(f"✅ Transformed {len(transformed)} OHLC records for {crypto_id}")
        return transformed