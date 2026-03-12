"""
RSI (Relative Strength Index) Indicator
Measures momentum and overbought/oversold conditions
"""
import numpy as np
from loguru import logger

def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: Array of price data
        period: RSI period (default 14)
    
    Returns:
        Array of RSI values (0-100)
    """
    if len(prices) < period + 1:
        logger.warning(f"Not enough data for RSI. Need {period + 1} points, have {len(prices)}")
        return np.full(len(prices), np.nan)
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    rsi = np.zeros(len(prices))
    rsi[:period] = np.nan
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        rsi[period] = 100
    else:
        rs = avg_gain / avg_loss
        rsi[period] = 100 - (100 / (1 + rs))
    
    for i in range(period + 1, len(prices)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        
        if avg_loss == 0:
            rsi[i] = 100
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100 - (100 / (1 + rs))
    
    logger.debug(f"Calculated RSI (period={period})")
    return rsi

def get_rsi_signal(rsi_value):
    """Get trading signal from RSI value"""
    if rsi_value < 30:
        return 'oversold'
    elif rsi_value > 70:
        return 'overbought'
    else:
        return 'neutral'

