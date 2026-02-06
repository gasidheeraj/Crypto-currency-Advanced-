"""
Main ETL Pipeline Orchestrator
"""
import time
from datetime import datetime
from loguru import logger

from data_engineering.utils.logger import setup_logger
from data_engineering.config.database import DatabaseConfig
from data_engineering.config.settings import settings
from data_engineering.pipelines.extract.coingecko_extractor import CoinGeckoExtractor
from data_engineering.pipelines.transform.data_transformer import DataTransformer
from data_engineering.pipelines.load.data_loader import DataLoader

# Setup logger
setup_logger()

class CryptoPipeline:
    """Main ETL Pipeline Orchestrator"""
    
    def __init__(self):
        self.extractor = CoinGeckoExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
        self.crypto_list = settings.CRYPTOS_TO_TRACK
    
    def setup_database(self):
        """Initialize database schema"""
        logger.info("=" * 70)
        logger.info("🔧 Setting up database...")
        logger.info("=" * 70)
        
        db = DatabaseConfig()
        db.connect()
        
        try:
            db.execute_script('database/schemas/create_tables.sql')
            db.execute_script('database/schemas/initial_data.sql')
            
            logger.info("=" * 70)
            logger.info("✅ Database setup completed successfully!")
            logger.info("=" * 70)
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
        finally:
            db.close()
    
    def run_pipeline(self):
        """Execute complete ETL pipeline"""
        start_time = time.time()
        started_at = datetime.now()
        pipeline_name = "crypto_market_data_pipeline"
        
        logger.info("\n" + "=" * 70)
        logger.info(f"🚀 Starting {pipeline_name}")
        logger.info(f"📅 Timestamp: {started_at}")
        logger.info(f"🔢 Cryptocurrencies: {len(self.crypto_list)}")
        logger.info("=" * 70 + "\n")
        
        total_records = 0
        status = 'SUCCESS'
        error_message = None
        
        try:
            # EXTRACT
            logger.info("📥 [1/3] EXTRACT PHASE: Fetching data from CoinGecko API...")
            raw_data = self.extractor.fetch_market_data(self.crypto_list)
            
            if not raw_data:
                logger.warning("⚠️  No data fetched, skipping pipeline")
                return
            
            logger.info(f"    ✓ Successfully fetched {len(raw_data)} records")
            
            # TRANSFORM
            logger.info("\n🔄 [2/3] TRANSFORM PHASE: Processing and validating data...")
            market_data = self.transformer.transform_market_data(raw_data)
            logger.info(f"    ✓ Transformed {len(market_data)} market data records")
            
            price_data = self.transformer.transform_price_data(raw_data)
            logger.info(f"    ✓ Transformed {len(price_data)} price data records")
            
            # LOAD
            logger.info("\n💾 [3/3] LOAD PHASE: Inserting into PostgreSQL database...")
            market_records = self.loader.load_market_data(market_data)
            logger.info(f"    ✓ Loaded {market_records} market data records")
            
            price_records = self.loader.load_price_data(price_data)
            logger.info(f"    ✓ Loaded {price_records} price data records")
            
            total_records = market_records + price_records
            
            # Log execution
            execution_time = time.time() - start_time
            self.loader.log_pipeline_execution(
                pipeline_name=pipeline_name,
                status=status,
                records_processed=total_records,
                execution_time=execution_time,
                started_at=started_at
            )
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            logger.info(f"📊 Total records processed: {total_records}")
            logger.info(f"⏱️  Execution time: {execution_time:.2f} seconds")
            logger.info("=" * 70 + "\n")
        
        except Exception as e:
            execution_time = time.time() - start_time
            status = 'FAILED'
            error_message = str(e)
            
            logger.error("\n" + "=" * 70)
            logger.error("❌ PIPELINE FAILED!")
            logger.error("=" * 70)
            logger.error(f"Error: {e}")
            logger.error("=" * 70 + "\n")
            
            try:
                self.loader.log_pipeline_execution(
                    pipeline_name=pipeline_name,
                    status=status,
                    records_processed=total_records,
                    execution_time=execution_time,
                    error_message=error_message,
                    started_at=started_at
                )
            except:
                pass
            
            raise
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        self.extractor.close()
        self.loader.close()

if __name__ == "__main__":
    pipeline = CryptoPipeline()
    
    try:
        # First-time setup
        pipeline.setup_database()
        
        # Run pipeline
        pipeline.run_pipeline()
    
    except KeyboardInterrupt:
        logger.info("\n⛔ Application stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Application error: {e}")
    finally:
        pipeline.cleanup()
        logger.info("👋 Goodbye!\n")