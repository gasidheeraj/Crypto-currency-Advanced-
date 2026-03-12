"""
Collect ALL Historical Cryptocurrency Data
Uses CoinGecko's FREE API to get years of data
"""
import requests
import psycopg2
from datetime import datetime
from loguru import logger
import time

# Database connection
DB_CONFIG = {
    'dbname': 'crypto_db',
    'user': 'saidheeraj_postgre',
    'password': 'crypto_password',
    'host': '127.0.0.1',
    'port': 5432
}

# Cryptocurrencies to collect
CRYPTOS = [
    'bitcoin', 'ethereum', 'solana', 'cardano', 
    'dogecoin', 'avalanche-2', 'chainlink', 
    'polkadot', 'ripple'
]

def fetch_historical_data(crypto_id, days='max'):
    """
    Fetch ALL historical data from CoinGecko FREE API
    
    Args:
        crypto_id: Cryptocurrency ID
        days: 'max' for all historical data, or number of days
        
    Returns:
        List of (timestamp, price, volume) tuples
    """
    logger.info(f"📥 Fetching ALL historical data for {crypto_id}...")
    
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    
    # Use 'max' to get ALL historical data!
    params = {
        'vs_currency': 'usd',
        'days': days,  # 'max' = all data available!
        'interval': 'daily'
    }
    
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=60)
        
        # Handle errors
        if response.status_code == 429:
            logger.warning(f"⚠️  Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return fetch_historical_data(crypto_id, days)
        
        response.raise_for_status()
        data = response.json()
        
        # Extract data
        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])
        
        # Process records
        records = []
        for i in range(len(prices)):
            timestamp_ms = prices[i][0]
            price = prices[i][1]
            volume = volumes[i][1] if i < len(volumes) else 0
            
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
            records.append((timestamp, price, volume))
        
        # Calculate time range
        if records:
            first_date = records[0][0]
            last_date = records[-1][0]
            years = (last_date - first_date).days / 365.25
            
            logger.success(f"✅ Fetched {len(records)} records for {crypto_id}")
            logger.info(f"   Date range: {first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}")
            logger.info(f"   Time span: {years:.1f} years")
        
        return records
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP Error for {crypto_id}: {e}")
        logger.info(f"   Status code: {response.status_code}")
        if response.status_code == 404:
            logger.info(f"   This crypto might not exist in CoinGecko")
        return []
    except Exception as e:
        logger.error(f"❌ Error fetching {crypto_id}: {e}")
        return []

def clear_old_data(conn, crypto_id):
    """Delete existing data"""
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM prices 
        WHERE crypto_id = (SELECT id FROM cryptocurrencies WHERE coingecko_id = %s)
    """, (crypto_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    if deleted > 0:
        logger.info(f"🗑️  Deleted {deleted} old records")

def insert_historical_data(conn, crypto_id, records):
    """Insert data into database"""
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM cryptocurrencies WHERE coingecko_id = %s",
        (crypto_id,)
    )
    result = cursor.fetchone()
    
    if not result:
        logger.error(f"❌ {crypto_id} not found in database!")
        cursor.close()
        return
    
    db_crypto_id = result[0]
    
    # Batch insert for speed
    inserted = 0
    batch = []
    batch_size = 100
    
    for timestamp, price, volume in records:
        batch.append((db_crypto_id, price, volume, timestamp))
        
        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT INTO prices (crypto_id, price, volume, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (crypto_id, timestamp) DO UPDATE
                SET price = EXCLUDED.price, volume = EXCLUDED.volume
            """, batch)
            inserted += len(batch)
            batch = []
    
    # Insert remaining
    if batch:
        cursor.executemany("""
            INSERT INTO prices (crypto_id, price, volume, timestamp)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (crypto_id, timestamp) DO UPDATE
            SET price = EXCLUDED.price, volume = EXCLUDED.volume
        """, batch)
        inserted += len(batch)
    
    conn.commit()
    cursor.close()
    logger.success(f"✅ Inserted {inserted} records")

def main():
    """Collect all historical data"""
    logger.info("="*70)
    logger.info("📊 COLLECTING ALL HISTORICAL DATA (FREE API)")
    logger.info("="*70)
    
    print("\n🎯 This will fetch ALL available historical data:")
    print("   - Bitcoin: ~10+ years (since 2013)")
    print("   - Ethereum: ~8+ years (since 2015)")
    print("   - Other cryptos: Since their launch")
    print("   - Completely FREE!")
    print()
    
    confirm = input("Continue? (y/n) [default: y]: ").strip().lower() or 'y'
    
    if confirm != 'y':
        logger.info("❌ Cancelled by user")
        return
    
    # Connect
    logger.info("\n🔌 Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    logger.success("✅ Connected")
    
    # Collect
    success_count = 0
    total_records = 0
    
    for i, crypto_id in enumerate(CRYPTOS, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"[{i}/{len(CRYPTOS)}] {crypto_id.upper()}")
        logger.info(f"{'='*70}")
        
        records = fetch_historical_data(crypto_id, days='max')
        
        if records:
            clear_old_data(conn, crypto_id)
            insert_historical_data(conn, crypto_id, records)
            success_count += 1
            total_records += len(records)
        else:
            logger.warning(f"⚠️  No data collected for {crypto_id}")
        
        # Wait between requests (respect rate limits)
        if i < len(CRYPTOS):
            wait_time = 10
            logger.info(f"⏳ Waiting {wait_time}s before next crypto...")
            time.sleep(wait_time)
    
    conn.close()
    
    # Summary
    logger.info("\n" + "="*70)
    logger.success(f"✅ COLLECTION COMPLETE!")
    logger.info(f"   Success: {success_count}/{len(CRYPTOS)} cryptos")
    logger.info(f"   Total records: {total_records:,}")
    logger.info("="*70)
    
    # Verify
    if success_count > 0:
        logger.info("\n📊 Database Summary:")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.name, 
                COUNT(p.id) as records,
                MIN(p.timestamp) as first_date,
                MAX(p.timestamp) as last_date,
                ROUND(EXTRACT(EPOCH FROM (MAX(p.timestamp) - MIN(p.timestamp))) / 86400 / 365.25, 1) as years
            FROM cryptocurrencies c
            LEFT JOIN prices p ON c.id = p.crypto_id
            GROUP BY c.name
            ORDER BY records DESC
        """)
        
        results = cursor.fetchall()
        
        print("\n" + "="*80)
        print(f"{'Crypto':<15} {'Records':<10} {'From':<12} {'To':<12} {'Years':<8}")
        print("-"*80)
        
        for name, count, first, last, years in results:
            if count > 0:
                first_str = first.strftime('%Y-%m-%d')
                last_str = last.strftime('%Y-%m-%d')
                print(f"{name:<15} {count:<10} {first_str:<12} {last_str:<12} {years or 0:<8.1f}")
        
        print("="*80)
        
        cursor.close()
        conn.close()
    
    logger.info("\n💡 Next Steps:")
    logger.info("   1. Run: python train_xgboost.py")
    logger.info("   2. Refresh dashboard")
    logger.info("   3. Enjoy accurate predictions!")

if __name__ == "__main__":
    main()