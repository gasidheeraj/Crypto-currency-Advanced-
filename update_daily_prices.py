"""
Update Daily Prices for All Cryptocurrencies
Fetches latest day's data and adds to database
"""
from data_science.utils.data_loader import CryptoDataLoader
import yfinance as yf
import psycopg2
from datetime import datetime, timedelta
from loguru import logger

# Configure logger
logger.add("logs/daily_update_{time}.log", rotation="1 week")

print("="*70)
print(f"🔄 DAILY PRICE UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Yahoo Finance ticker mapping
TICKER_MAP = {
    'bitcoin': 'BTC-USD',
    'ethereum': 'ETH-USD',
    'cardano': 'ADA-USD',
    'solana': 'SOL-USD',
    'polkadot': 'DOT-USD',
    'ripple': 'XRP-USD',
    'dogecoin': 'DOGE-USD',
    'avalanche-2': 'AVAX-USD',
    'chainlink': 'LINK-USD'
}

# Database connection
conn = psycopg2.connect(
    dbname='crypto_db',
    user='saidheeraj_postgre',
    password='crypto_password',
    host='127.0.0.1',
    port=5432
)

# Get all cryptocurrencies
loader = CryptoDataLoader()
cryptos = loader.get_all_cryptos()
loader.close()

print(f"\n📊 Updating {len(cryptos)} cryptocurrencies...")

success_count = 0
failed = []

for crypto in cryptos:
    crypto_id = crypto['crypto_id']
    name = crypto['name']
    
    try:
        # Get Yahoo Finance ticker
        ticker = TICKER_MAP.get(crypto_id)
        
        if not ticker:
            print(f"⚠️  {name}: No ticker mapping")
            failed.append((name, "No ticker"))
            continue
        
        print(f"\n📥 {name} ({ticker})...")
        
        # Fetch last 2 days (to ensure we get today's data)
        df = yf.download(
            ticker,
            period="2d",
            interval="1d",
            progress=False
        )
        
        if df.empty:
            print(f"   ⚠️  No data available")
            failed.append((name, "No data"))
            continue
        
        # Get the latest day
        latest_date = df.index[-1]
        latest_data = df.iloc[-1]
        
        # Extract OHLCV
        open_price = float(latest_data['Open'])
        high_price = float(latest_data['High'])
        low_price = float(latest_data['Low'])
        close_price = float(latest_data['Close'])
        volume = float(latest_data['Volume'])
        
        # Insert or update in database
        cursor = conn.cursor()
        
        # Check if this date already exists
        cursor.execute("""
            SELECT COUNT(*) FROM price_data 
            WHERE crypto_id = %s AND timestamp::date = %s::date
        """, (crypto_id, latest_date))
        
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            # Update existing record
            cursor.execute("""
                UPDATE price_data
                SET open = %s, high = %s, low = %s, close = %s, volume = %s
                WHERE crypto_id = %s AND timestamp::date = %s::date
            """, (open_price, high_price, low_price, close_price, volume, 
                  crypto_id, latest_date))
            
            print(f"   ✅ Updated: {latest_date.strftime('%Y-%m-%d')} | ${close_price:,.2f}")
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO price_data 
                (crypto_id, timestamp, open, high, low, close, volume, market_cap)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
            """, (crypto_id, latest_date, open_price, high_price, 
                  low_price, close_price, volume))
            
            print(f"   ✅ Inserted: {latest_date.strftime('%Y-%m-%d')} | ${close_price:,.2f}")
        
        conn.commit()
        cursor.close()
        
        success_count += 1
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        logger.error(f"Error updating {name}: {e}")
        failed.append((name, str(e)))

conn.close()

# Summary
print("\n" + "="*70)
print("📊 UPDATE SUMMARY")
print("="*70)
print(f"✅ Success: {success_count}/{len(cryptos)}")
print(f"❌ Failed:  {len(failed)}/{len(cryptos)}")

if failed:
    print("\n❌ Failed cryptocurrencies:")
    for name, reason in failed:
        print(f"   - {name}: {reason}")

print("\n" + "="*70)
print(f"✅ Update complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# Log completion
logger.info(f"Daily update complete: {success_count} success, {len(failed)} failed")