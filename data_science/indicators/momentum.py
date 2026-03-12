"""
Momentum Indicators
Calculate RSI and other momentum indicators
"""
import numpy as np
from loguru import logger

def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    RSI measures momentum - whether asset is overbought or oversold
    - RSI > 70 = Overbought (might go down)
    - RSI < 30 = Oversold (might go up)
    - RSI = 50 = Neutral
    
    Args:
        prices: numpy array of prices
        period: lookback period (default 14)
    
    Returns:
        numpy array: RSI values
    """
    if len(prices) < period:
        logger.warning(f"Not enough data for RSI (need {period}, have {len(prices)})")
        return None
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gains = np.zeros(len(prices))
    avg_losses = np.zeros(len(prices))
    
    # First average is simple mean
    avg_gains[period] = np.mean(gains[:period])
    avg_losses[period] = np.mean(losses[:period])
    
    # Subsequent values use smoothing
    for i in range(period + 1, len(prices)):
        avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
        avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
    
    # Calculate RS (Relative Strength)
    rs = np.divide(avg_gains, avg_losses, 
                   out=np.zeros_like(avg_gains), 
                   where=avg_losses!=0)
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    logger.info(f"✅ Calculated RSI for {len(prices)} prices")
    return rsi