-- ============================================================================
-- CRYPTO PREDICTION PROJECT - DATABASE SCHEMA
-- ============================================================================

-- ============================================================================
-- TABLE 1: Crypto Metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS crypto_metadata (
    id SERIAL PRIMARY KEY,
    crypto_id VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE 2: Price Data (OHLCV)
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_data (
    id SERIAL PRIMARY KEY,
    crypto_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20, 8),
    high DECIMAL(20, 8),
    low DECIMAL(20, 8),
    close DECIMAL(20, 8),
    volume DECIMAL(30, 8),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_price_record UNIQUE(crypto_id, timestamp)
);

-- ============================================================================
-- TABLE 3: Market Data
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    crypto_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    market_cap BIGINT,
    total_volume BIGINT,
    circulating_supply DECIMAL(30, 8),
    max_supply DECIMAL(30, 8),
    price_change_24h DECIMAL(10, 2),
    price_change_percentage_24h DECIMAL(10, 4),
    price_change_percentage_7d DECIMAL(10, 4),
    price_change_percentage_30d DECIMAL(10, 4),
    market_cap_rank INTEGER,
    ath DECIMAL(20, 8),
    ath_date TIMESTAMP,
    atl DECIMAL(20, 8),
    atl_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_market_record UNIQUE(crypto_id, timestamp)
);

-- ============================================================================
-- TABLE 4: Technical Indicators
-- ============================================================================
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    crypto_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Momentum Indicators
    rsi_14 DECIMAL(10, 4),
    rsi_7 DECIMAL(10, 4),
    rsi_21 DECIMAL(10, 4),
    
    -- MACD
    macd DECIMAL(20, 8),
    macd_signal DECIMAL(20, 8),
    macd_histogram DECIMAL(20, 8),
    
    -- Bollinger Bands
    bollinger_upper DECIMAL(20, 8),
    bollinger_middle DECIMAL(20, 8),
    bollinger_lower DECIMAL(20, 8),
    bollinger_bandwidth DECIMAL(10, 4),
    
    -- Moving Averages
    sma_7 DECIMAL(20, 8),
    sma_20 DECIMAL(20, 8),
    sma_50 DECIMAL(20, 8),
    sma_100 DECIMAL(20, 8),
    sma_200 DECIMAL(20, 8),
    ema_12 DECIMAL(20, 8),
    ema_26 DECIMAL(20, 8),
    ema_50 DECIMAL(20, 8),
    
    -- Volatility
    volatility_7d DECIMAL(10, 4),
    volatility_30d DECIMAL(10, 4),
    
    -- Volume Indicators
    volume_sma_20 DECIMAL(30, 8),
    volume_ratio DECIMAL(10, 4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_indicator_record UNIQUE(crypto_id, timestamp)
);

-- ============================================================================
-- TABLE 5: Pipeline Logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    execution_time_seconds DECIMAL(10, 2),
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE 6: Data Quality Metrics
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id SERIAL PRIMARY KEY,
    crypto_id VARCHAR(100) NOT NULL,
    metric_date DATE NOT NULL,
    completeness_score DECIMAL(5, 2),
    accuracy_score DECIMAL(5, 2),
    timeliness_score DECIMAL(5, 2),
    missing_records_count INTEGER,
    duplicate_records_count INTEGER,
    outlier_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_quality_metric UNIQUE(crypto_id, metric_date)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- =====