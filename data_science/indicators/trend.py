"""
Trend Indicators
Calculate MACD, Moving Averages, and trend indicators
"""
import numpy as np
from loguru import logger

def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        prices: numpy array of prices
        period: lookback period
    
    Returns:
        numpy array: EMA values
    """
    ema = np.zeros(len(prices))
    
    # Start with SMA for first value
    if len(prices) < period:
        return ema
    
    # First EMA is simple average
    sma = np.mean(prices[:period])
    ema[period-1] = sma
    
    # Multiplier for weighting
    multiplier = 2.0 / (period + 1.0)
    
    # Calculate EMA for remaining values
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i-1]) * multiplier + ema[i-1]
    
    return ema

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: numpy array of prices
        fast: fast EMA period (default 12)
        slow: slow EMA period (default 26)
        signal: signal line period (default 9)
    
    Returns:
        tuple: (macd_line, signal_line, histogram)
    """
    # Need at least slow + signal periods
    min_periods = slow + signal
    
    if len(prices) < min_periods:
        logger.warning(f"Not enough data for MACD (need {min_periods}, have {len(prices)})")
        # Return arrays of zeros instead of None
        zeros = np.zeros(len(prices))
        return zeros, zeros, zeros
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    # MACD line = fast EMA - slow EMA
    macd_line = ema_fast - ema_slow
    
    # Signal line = EMA of MACD line (only non-zero part)
    signal_line = calculate_ema(macd_line[slow-1:], signal)
    
    # Pad signal line with zeros at beginning
    signal_padded = np.zeros(len(prices))
    signal_padded[slow-1:] = signal_line
    
    # Histogram = MACD - Signal
    histogram = macd_line - signal_padded
    
    logger.info(f"✅ Calculated MACD for {len(prices)} prices")
    return macd_line, signal_padded, histogram