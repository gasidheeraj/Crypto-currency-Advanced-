"""
Feature Engineer Optimized for DAILY Data
"""
import numpy as np
from datetime import datetime
from loguru import logger

class DailyFeatureEngineer:
    """Create features optimized for daily cryptocurrency data"""
    
    def __init__(self):
        logger.info("✅ Daily Feature Engineer initialized")
    
    def create_lag_features(self, prices, lags=[1, 2, 3, 5, 7]):
        """
        Lag features for DAILY data
        lag_1 = yesterday
        lag_7 = 1 week ago
        """
        features = {}
        
        for lag in lags:
            feature_name = f'price_lag_{lag}'
            lagged = np.zeros(len(prices))
            lagged[lag:] = prices[:-lag]
            lagged[:lag] = np.nan
            features[feature_name] = lagged
        
        return features
    
    def create_rolling_features(self, prices, windows=[3, 7, 14, 30, 90]):
        """
        Rolling features for DAILY data
        3-day, 1-week, 2-week, 1-month, 3-month
        """
        features = {}
        
        for window in windows:
            # Moving average
            rolling_mean = np.convolve(prices, np.ones(window)/window, mode='same')
            rolling_mean[:window-1] = np.nan
            features[f'rolling_mean_{window}'] = rolling_mean
            
            # Max
            rolling_max = np.array([
                prices[max(0, i-window+1):i+1].max() if i >= window-1 else np.nan
                for i in range(len(prices))
            ])
            features[f'rolling_max_{window}'] = rolling_max
            
            # Min
            rolling_min = np.array([
                prices[max(0, i-window+1):i+1].min() if i >= window-1 else np.nan
                for i in range(len(prices))
            ])
            features[f'rolling_min_{window}'] = rolling_min
            
            # Std (volatility)
            rolling_std = np.array([
                prices[max(0, i-window+1):i+1].std() if i >= window-1 else np.nan
                for i in range(len(prices))
            ])
            features[f'rolling_std_{window}'] = rolling_std
        
        return features
    
    def create_momentum_features(self, prices):
        """Price momentum and rate of change"""
        features = {}
        
        # Daily returns (% change)
        returns = np.zeros(len(prices))
        returns[1:] = (prices[1:] - prices[:-1]) / prices[:-1] * 100
        returns[0] = np.nan
        features['daily_return'] = returns
        
        # Rate of change over different periods
        for period in [3, 7, 14, 30]:
            roc = np.zeros(len(prices))
            roc[period:] = (prices[period:] - prices[:-period]) / prices[:-period] * 100
            roc[:period] = np.nan
            features[f'roc_{period}'] = roc
        
        return features
    
    def create_time_features(self, timestamps):
        """Time-based features for daily data"""
        features = {}
        
        day_of_week = np.array([ts.weekday() for ts in timestamps])
        day_of_month = np.array([ts.day for ts in timestamps])
        month = np.array([ts.month for ts in timestamps])
        quarter = np.array([(ts.month - 1) // 3 + 1 for ts in timestamps])
        
        features['day_of_week'] = day_of_week
        features['day_of_month'] = day_of_month
        features['month'] = month
        features['quarter'] = quarter
        features['is_weekend'] = (day_of_week >= 5).astype(float)
        features['is_month_start'] = (day_of_month <= 3).astype(float)
        features['is_month_end'] = (day_of_month >= 28).astype(float)
        
        return features
    
    def create_all_features(self, prices, timestamps, indicators=None):
        """Create all features optimized for daily data"""
        features = {}
        
        # Price itself
        features['price'] = prices
        
        # Lag features (1, 2, 3, 5, 7 days ago)
        lag_features = self.create_lag_features(prices)
        features.update(lag_features)
        
        # Rolling features (3d, 7d, 14d, 30d, 90d)
        rolling_features = self.create_rolling_features(prices)
        features.update(rolling_features)
        
        # Momentum features
        momentum_features = self.create_momentum_features(prices)
        features.update(momentum_features)
        
        # Time features
        time_features = self.create_time_features(timestamps)
        features.update(time_features)
        
        # Add technical indicators if provided
        if indicators:
            features['rsi'] = indicators['rsi']
            features['macd_line'] = indicators['macd_line']
            features['macd_signal'] = indicators['macd_signal']
            features['macd_histogram'] = indicators['macd_histogram']
            features['bb_upper'] = indicators['bb_upper']
            features['bb_middle'] = indicators['bb_middle']
            features['bb_lower'] = indicators['bb_lower']
        
        logger.info(f"✅ Created {len(features)} daily-optimized features")
        return features