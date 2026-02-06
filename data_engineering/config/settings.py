"""
Application Settings and Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'crypto_db')
    DB_USER = os.getenv('DB_USER', 'crypto_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Cryptocurrencies to track
    CRYPTOS_TO_TRACK = os.getenv(
        'CRYPTOS_TO_TRACK',
        'bitcoin,ethereum,cardano,solana,polkadot'
    ).split(',')
    
    # Pipeline settings
    FETCH_INTERVAL_MINUTES = int(os.getenv('FETCH_INTERVAL_MINUTES', 5))
    
    # API Settings
    COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
    BINANCE_BASE_URL = 'https://api.binance.com/api/v3'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/pipeline.log')
    
    # Data paths
    RAW_DATA_PATH = 'data/raw'
    PROCESSED_DATA_PATH = 'data/processed'
    ARCHIVE_DATA_PATH = 'data/archive'
    
    # Rate limiting
    API_RATE_LIMIT_SECONDS = 1.2
    MAX_RETRIES = 3
    RETRY_DELAY = 2

settings = Settings()