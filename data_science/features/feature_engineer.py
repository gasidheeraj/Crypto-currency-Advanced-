"""
Feature Engineering
Create features for machine learning models
"""
import numpy as np
from loguru import logger

class FeatureEngineer:
    """Create features from price data"""
    
    def __init__(self):
        logger.info("✅ Feature Engineer initialized")
    
    def create_lag_features(self, prices, lags=[1, 2, 3, 6, 12, 24]):
        """
        Create lag features (previous prices)
        
        Args:
            prices: numpy array of prices
            lags: list of lag periods (default: [1,2,3,6,12,24])
        
        Returns:
            dict: Dictionary of lag features
        """
        lag_features = {}
        
        for lag in lags:
            lagged = np.zeros(len(prices))
            lagged[lag:] = prices[:-lag]
            lag_features[f'price_lag_{lag}'] = lagged
        
        logger.info(f"✅ Created {len(lags)} lag features")
        return lag_features
    
    def create_rolling_features(self, prices, windows=[3, 7, 14, 30]):
        """
        Create rolling statistics (moving averages, max, min)
        
        Args:
            prices: numpy array of prices
            windows: list of window sizes (default: [3,7,14,30])
        
        Returns:
            dict: Dictionary of rolling features
        """
        rolling_features = {}
        
        for window in windows:
            # Rolling mean (average)
            rolling_mean = np.zeros(len(prices))
            for i in range(window - 1, len(prices)):
                rolling_mean[i] = np.mean(prices[i - window + 1:i + 1])
            rolling_features[f'rolling_mean_{window}'] = rolling_mean
            
            # Rolling max
            rolling_max = np.zeros(len(prices))
            for i in range(window - 1, len(prices)):
                rolling_max[i] = np.max(prices[i - window + 1:i + 1])
            rolling_features[f'rolling_max_{window}'] = rolling_max
            
            # Rolling min
            rolling_min = np.zeros(len(prices))
            for i in range(window - 1, len(prices)):
                rolling_min[i] = np.min(prices[i - window + 1:i + 1])
            rolling_features[f'rolling_min_{window}'] = rolling_min
            
            # Rolling std (volatility)
            rolling_std = np.zeros(len(prices))
            for i in range(window - 1, len(prices)):
                rolling_std[i] = np.std(prices[i - window + 1:i + 1])
            rolling_features[f'rolling_std_{window}'] = rolling_std
        
        logger.info(f"✅ Created rolling features for {len(windows)} windows")
        return rolling_features
    def create_all_features(self, prices, timestamps, indicators=None):
        """
        Create complete feature set combining all feature types
        
        Args:
            prices: numpy array of prices
            timestamps: numpy array of datetime objects
            indicators: dict of technical indicators (optional)
        
        Returns:
            dict: Complete feature set
        """
        logger.info("Creating complete feature set...")
        
        # Create all feature types
        features = {}
        
        # 1. Original data
        features['price'] = prices
        
        # 2. Lag features
        lag_features = self.create_lag_features(prices, lags=[1, 2, 3, 6, 12])
        features.update(lag_features)
        
        # 3. Rolling features
        rolling_features = self.create_rolling_features(prices, windows=[3, 7, 14])
        features.update(rolling_features)
        
        # 4. Time features
        time_features = self.create_time_features(timestamps)
        features.update(time_features)
        
        # 5. Add technical indicators if provided
        if indicators:
            features['rsi'] = indicators.get('rsi', np.zeros(len(prices)))
            features['macd_line'] = indicators.get('macd_line', np.zeros(len(prices)))
            features['macd_signal'] = indicators.get('macd_signal', np.zeros(len(prices)))
            features['bb_upper'] = indicators.get('bb_upper', np.zeros(len(prices)))
            features['bb_middle'] = indicators.get('bb_middle', np.zeros(len(prices)))
            features['bb_lower'] = indicators.get('bb_lower', np.zeros(len(prices)))
        
        # Count total features
        num_features = len(features)
        logger.info(f"✅ Created {num_features} total features!")
        
        return features