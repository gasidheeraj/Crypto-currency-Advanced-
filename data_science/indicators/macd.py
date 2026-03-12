"""
MACD (Moving Average Convergence Divergence) Indicator
Trend-following momentum indicator
"""
import numpy as np
from loguru import logger

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    ema = np.zeros(len(prices))
    ema[:period - 1] = np.nan
    ema[period - 1] = np.mean(prices[:period])
    multiplier = 2 / (period + 1)
    
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
    
    return ema

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate MACD
    
    Args:
        prices: Array of price data
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)
    
    Returns:
        dict with macd_line, signal_line, macd_histogram
    """
    if len(prices) < slow_period + signal_period:
        logger.warning(f"Not enough data for MACD")
        return {
            'macd_line': np.full(len(prices), np.nan),
            'signal_line': np.full(len(prices), np.nan),
            'macd_histogram': np.full(len(prices), np.nan)
        }
    
    fast_ema = calculate_ema(prices, fast_period)
    slow_ema = calculate_ema(prices, slow_period)
    macd_line = fast_ema - slow_ema
    
    valid_start = slow_period - 1
    macd_valid = macd_line[valid_start:]
    
    signal_line = np.full(len(prices), np.nan)
    signal_ema = calculate_ema(macd_valid, signal_period)
    signal_line[valid_start:] = signal_ema
    
    macd_histogram = macd_line - signal_line
    
    logger.debug(f"Calculated MACD")
    
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'macd_histogram': macd_histogram
    }

def get_macd_signal(macd_line, signal_line, histogram):
    """Get trading signal from MACD"""
    if np.isnan(macd_line) or np.isnan(signal_line):
        return 'neutral'
    
    if macd_line > signal_line and histogram > 0:
        return 'bullish'
    elif macd_line < signal_line and histogram < 0:
        return 'bearish'
    else:
        return 'neutral'