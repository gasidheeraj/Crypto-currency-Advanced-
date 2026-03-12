"""
Volatility Indicators
Calculate Bollinger Bands and volatility indicators
"""
import numpy as np
from loguru import logger

def calculate_sma(prices, period):
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: numpy array of prices
        period: lookback period
    
    Returns:
        numpy array: SMA values
    """
    sma = np.zeros(len(prices))
    
    for i in range(period - 1, len(prices)):
        sma[i] = np.mean(prices[i - period + 1:i + 1])
    
    return sma

def calculate_bollinger_bands(prices, period=20, num_std=2):
    """
    Calculate Bollinger Bands
    
    Bollinger Bands show price volatility:
    - Upper Band = SMA + (2 × std dev)
    - Middle Band = SMA
    - Lower Band = SMA - (2 × std dev)
    
    Price touching upper band = might be overbought
    Price touching lower band = might be oversold
    
    Args:
        prices: numpy array of prices
        period: lookback period (default 20)
        num_std: number of standard deviations (default 2)
    
    Returns:
        tuple: (upper_band, middle_band, lower_band)
    """
    if len(prices) < period:
        logger.warning(f"Not enough data for Bollinger Bands (need {period}, have {len(prices)})")
        zeros = np.zeros(len(prices))
        return zeros, zeros, zeros
    
    # Calculate middle band (SMA)
    middle_band = calculate_sma(prices, period)
    
    # Calculate standard deviation
    std_dev = np.zeros(len(prices))
    for i in range(period - 1, len(prices)):
        std_dev[i] = np.std(prices[i - period + 1:i + 1])
    
    # Calculate upper and lower bands
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)
    
    logger.info(f"✅ Calculated Bollinger Bands for {len(prices)} prices")
    return upper_band, middle_band, lower_band