"""
Bollinger Bands Indicator
Volatility indicator showing price range
"""
import numpy as np
from loguru import logger

def calculate_bollinger_bands(prices, window=20, num_std=2):
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Array of price data
        window: Moving average window (default 20)
        num_std: Number of standard deviations (default 2)
    
    Returns:
        dict with bb_upper, bb_middle, bb_lower, bb_bandwidth
    """
    if len(prices) < window:
        logger.warning(f"Not enough data for Bollinger Bands")
        return {
            'bb_upper': np.full(len(prices), np.nan),
            'bb_middle': np.full(len(prices), np.nan),
            'bb_lower': np.full(len(prices), np.nan),
            'bb_bandwidth': np.full(len(prices), np.nan)
        }
    
    bb_middle = np.zeros(len(prices))
    bb_middle[:window - 1] = np.nan
    
    for i in range(window - 1, len(prices)):
        bb_middle[i] = np.mean(prices[i - window + 1:i + 1])
    
    bb_std = np.zeros(len(prices))
    bb_std[:window - 1] = np.nan
    
    for i in range(window - 1, len(prices)):
        bb_std[i] = np.std(prices[i - window + 1:i + 1])
    
    bb_upper = bb_middle + (bb_std * num_std)
    bb_lower = bb_middle - (bb_std * num_std)
    bb_bandwidth = bb_upper - bb_lower
    
    logger.debug(f"Calculated Bollinger Bands")
    
    return {
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'bb_bandwidth': bb_bandwidth
    }

def get_bollinger_signal(price, upper_band, lower_band):
    """Get trading signal from Bollinger Bands position"""
    if np.isnan(upper_band) or np.isnan(lower_band):
        return 'neutral'
    
    if price >= upper_band:
        return 'overbought'
    elif price <= lower_band:
        return 'oversold'
    else:
        return 'neutral'

def calculate_percent_b(price, upper_band, lower_band):
    """Calculate %B indicator"""
    if np.isnan(upper_band) or np.isnan(lower_band):
        return np.nan
    
    if upper_band == lower_band:
        return 0.5
    
    percent_b = (price - lower_band) / (upper_band - lower_band)
    return percent_b