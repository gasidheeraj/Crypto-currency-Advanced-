"""
Data Preparation for ML Models
Prepare features and target for training
"""
import numpy as np
from loguru import logger

class DataPreparation:
    """Prepare data for machine learning"""
    
    def __init__(self):
        logger.info("✅ Data Preparation initialized")
    
    def create_target(self, prices, horizon=1):
        """
        Create target variable (future price)
        
        Args:
            prices: numpy array of prices
            horizon: how many periods ahead to predict (default: 1)
        
        Returns:
            numpy array: target prices (shifted forward)
        """
        # Shift prices backward to get future prices
        target = np.zeros(len(prices))
        target[:-horizon] = prices[horizon:]
        
        # Last values have no future data (set to NaN)
        target[-horizon:] = np.nan
        
        logger.info(f"✅ Created target variable (predicting {horizon} periods ahead)")
        return target
    
    def prepare_features_array(self, features, exclude_keys=['price']):
        """
        Convert feature dictionary to numpy array
        
        Args:
            features: dict of features
            exclude_keys: keys to exclude from features
        
        Returns:
            tuple: (feature_array, feature_names)
        """
        # Get feature names (exclude certain keys)
        feature_names = [k for k in features.keys() if k not in exclude_keys]
        
        # Stack features into 2D array
        # Shape: (num_samples, num_features)
        feature_list = [features[name] for name in feature_names]
        X = np.column_stack(feature_list)
        
        logger.info(f"✅ Prepared feature array: {X.shape} (samples, features)")
        return X, feature_names
    
    def remove_invalid_rows(self, X, y):
        """
        Remove rows with NaN or zero values
        
        Args:
            X: feature array
            y: target array
        
        Returns:
            tuple: (X_clean, y_clean)
        """
        # Find valid rows (no NaN, no zeros in important columns)
        valid_mask = ~np.isnan(y)  # Target not NaN
        valid_mask &= ~np.any(np.isnan(X), axis=1)  # No NaN in features
        valid_mask &= ~np.all(X == 0, axis=1)  # Not all zeros
        
        X_clean = X[valid_mask]
        y_clean = y[valid_mask]
        
        removed = len(X) - len(X_clean)
        logger.info(f"✅ Removed {removed} invalid rows, kept {len(X_clean)} rows")
        
        return X_clean, y_clean
    
    def split_train_test(self, X, y, test_size=0.2):
        """
        Split data into training and test sets
        
        Time series: Use first 80% for training, last 20% for testing
        (Don't shuffle! Order matters for time series)
        
        Args:
            X: feature array
            y: target array
            test_size: fraction for test set (default: 0.2)
        
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        # Calculate split point
        split_idx = int(len(X) * (1 - test_size))
        
        # Split (don't shuffle - time series!)
        X_train = X[:split_idx]
        X_test = X[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        logger.info(f"✅ Train set: {len(X_train)} samples")
        logger.info(f"✅ Test set:  {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test