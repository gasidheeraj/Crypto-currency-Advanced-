"""
Calculate All Technical Indicators
Combines RSI, MACD, and Bollinger Bands
"""
import numpy as np
from loguru import logger
from data_science.indicators.momentum import calculate_rsi
from data_science.indicators.trend import calculate_macd
from data_science.indicators.volatility import calculate_bollinger_bands

def calculate_all_indicators(prices):
    """
    Calculate all technical indicators for given prices
    
    Args:
        prices: numpy array of prices
    
    Returns:
        dict: All indicator values
    """
    logger.info(f"Calculating all indicators for {len(prices)} prices...")
    
    # Calculate each indicator
    rsi = calculate_rsi(prices, period=14)
    macd_line, signal_line, histogram = calculate_macd(prices)
    upper_band, middle_band, lower_band = calculate_bollinger_bands(prices, period=20)
    
    # Package results
    indicators = {
        'rsi': rsi,
        'macd_line': macd_line,
        'macd_signal': signal_line,
        'macd_histogram': histogram,
        'bb_upper': upper_band,
        'bb_middle': middle_band,
        'bb_lower': lower_band,
        'prices': prices
    }
    
    logger.info("✅ All indicators calculated successfully!")
    return indicators