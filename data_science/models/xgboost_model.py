"""
XGBoost Model for Price Prediction
"""
import numpy as np
import xgboost as xgb
from loguru import logger
import joblib

class XGBoostPredictor:
    """XGBoost model for cryptocurrency price prediction"""
    
    def __init__(self):
        """Initialize XGBoost model"""
        self.model = None
        self.feature_names = None
        logger.info("✅ XGBoost Predictor initialized")
    
    def create_model(self):
        """
        Create XGBoost model with optimized parameters
        
        Returns:
            XGBoost model
        """
        model = xgb.XGBRegressor(
            n_estimators=100,        # Number of trees
            max_depth=5,             # How deep each tree can go
            learning_rate=0.1,       # How fast it learns
            objective='reg:squarederror',  # Minimize error
            random_state=42          # For reproducibility
        )
        
        logger.info("✅ XGBoost model created")
        return model
    
    def train(self, X_train, y_train, feature_names=None):
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training targets
            feature_names: List of feature names
        """
        logger.info(f"Training XGBoost on {len(X_train)} samples...")
        
        # Create model
        self.model = self.create_model()
        self.feature_names = feature_names
        
        # Train
        self.model.fit(X_train, y_train, verbose=False)
        
        logger.info("✅ Training complete!")
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X: Features to predict on
        
        Returns:
            numpy array: Predictions
        """
        if self.model is None:
            raise ValueError("Model not trained yet! Call train() first.")
        
        predictions = self.model.predict(X)
        logger.info(f"✅ Generated {len(predictions)} predictions")
        return predictions
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test targets
        
        Returns:
            dict: Evaluation metrics
        """
        # Make predictions
        y_pred = self.predict(X_test)
        
        # Calculate metrics
        mae = np.mean(np.abs(y_test - y_pred))  # Mean Absolute Error
        rmse = np.sqrt(np.mean((y_test - y_pred)**2))  # Root Mean Square Error
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100  # Mean Absolute % Error
        
        # R² score (how much variance explained)
        ss_res = np.sum((y_test - y_pred)**2)
        ss_tot = np.sum((y_test - np.mean(y_test))**2)
        r2 = 1 - (ss_res / ss_tot)
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2': r2
        }
        
        logger.info(f"✅ Evaluation complete - MAE: ${mae:.2f}, MAPE: {mape:.2f}%")
        return metrics
    
    def save_model(self, filepath):
        """Save trained model to file"""
        if self.model is None:
            raise ValueError("No model to save!")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model from file"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        logger.info(f"✅ Model loaded from {filepath}")