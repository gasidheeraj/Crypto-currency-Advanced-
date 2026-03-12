"""
Train Hybrid Ensemble Models for ALL Cryptocurrencies
"""
from data_science.utils.data_loader import CryptoDataLoader
from data_science.indicators.calculate_all import calculate_all_indicators
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
import xgboost as xgb
import os

print("="*70)
print("🚀 TRAINING HYBRID MODELS FOR ALL CRYPTOCURRENCIES")
print("="*70)

# Get all cryptos
loader = CryptoDataLoader()
cryptos = loader.get_all_cryptos()
loader.close()

print(f"\n📊 Found {len(cryptos)} cryptocurrencies")

success_count = 0
results = []

for i, crypto in enumerate(cryptos, 1):
    crypto_id = crypto['crypto_id']
    name = crypto['name']
    
    print(f"\n{'='*70}")
    print(f"[{i}/{len(cryptos)}] {name.upper()}")
    print(f"{'='*70}")
    
    try:
        # Load data
        loader = CryptoDataLoader()
        data = loader.get_price_data(crypto_id)
        loader.close()
        
        if not data or len(data['prices']) < 100:
            print(f"⚠️  Skipping - not enough data")
            continue
        
        prices = data['prices']
        timestamps = data['timestamps']
        print(f"✅ Loaded {len(prices)} records")
        
        # Create features
        print(f"🔧 Creating features...")
        features = {}
        features['yesterday_price'] = prices.copy()
        
        for lag in [2, 3, 5, 7]:
            lagged = np.zeros(len(prices))
            lagged[lag:] = prices[:-lag]
            lagged[:lag] = np.nan
            features[f'lag_{lag}'] = lagged
        
        for window in [7, 14, 30]:
            ma = np.convolve(prices, np.ones(window)/window, mode='same')
            ma[:window-1] = np.nan
            features[f'ma_{window}'] = ma
        
        for period in [3, 7, 14]:
            pct = np.zeros(len(prices))
            pct[period:] = (prices[period:] - prices[:-period]) / prices[:-period] * 100
            pct[:period] = np.nan
            features[f'momentum_{period}'] = pct
        
        vol_7 = np.array([
            prices[max(0, i-6):i+1].std() if i >= 6 else np.nan
            for i in range(len(prices))
        ])
        features['volatility_7d'] = vol_7
        
        indicators = calculate_all_indicators(prices)
        features['rsi'] = indicators['rsi']
        features['macd'] = indicators['macd_line']
        
        # Prepare data
        target = np.zeros(len(prices))
        target[:-1] = prices[1:]
        target[-1] = np.nan
        
        feature_names = list(features.keys())
        X = np.column_stack([features[name] for name in feature_names])
        
        valid_mask = ~np.isnan(X).any(axis=1) & ~np.isnan(target)
        X_clean = X[valid_mask]
        y_clean = target[valid_mask]
        
        split_idx = int(len(X_clean) * 0.8)
        X_train = X_clean[:split_idx]
        X_test = X_clean[split_idx:]
        y_train = y_clean[:split_idx]
        y_test = y_clean[split_idx:]
        
        print(f"✅ Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Train ensemble
        print(f"🚀 Training ensemble...")
        
        ridge = Ridge(alpha=1.0)
        ridge.fit(X_train, y_train)
        ridge_pred = ridge.predict(X_test)
        ridge_r2 = 1 - (np.sum((y_test - ridge_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
        
        rf = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)
        rf_r2 = 1 - (np.sum((y_test - rf_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
        
        xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1)
        xgb_model.fit(X_train, y_train)
        xgb_pred = xgb_model.predict(X_test)
        xgb_r2 = 1 - (np.sum((y_test - xgb_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
        
        # Weighted ensemble
        total_r2 = ridge_r2 + rf_r2 + xgb_r2
        ridge_weight = ridge_r2 / total_r2
        rf_weight = rf_r2 / total_r2
        xgb_weight = xgb_r2 / total_r2
        
        ensemble_pred = ridge_pred * ridge_weight + rf_pred * rf_weight + xgb_pred * xgb_weight
        
        # Metrics
        mae = np.mean(np.abs(y_test - ensemble_pred))
        mape = np.mean(np.abs((y_test - ensemble_pred) / y_test)) * 100
        r2 = 1 - (np.sum((y_test - ensemble_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
        accuracy = 100 - mape
        
        print(f"\n📊 Performance:")
        print(f"   Accuracy: {accuracy:.2f}%")
        print(f"   R² Score: {r2:.4f}")
        print(f"   MAPE: {mape:.2f}%")
        
        # Save
        model_data = {
            'ridge_model': ridge,
            'rf_model': rf,
            'xgb_model': xgb_model,
            'feature_names': feature_names,
            'weights': {'ridge': ridge_weight, 'rf': rf_weight, 'xgb': xgb_weight},
            'model_type': 'hybrid_ensemble',
            'metrics': {'r2': r2, 'mae': mae, 'mape': mape, 'accuracy': accuracy}
        }
        
        model_path = f'models/saved/xgboost_{crypto_id}.pkl'
        joblib.dump(model_data, model_path)
        print(f"✅ Saved: {model_path}")
        
        success_count += 1
        results.append((name, r2, accuracy))
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Summary
print(f"\n{'='*70}")
print(f"📊 TRAINING SUMMARY")
print(f"{'='*70}")
print(f"✅ Success: {success_count}/{len(cryptos)}")
print(f"\n📁 Model Performance:")
for name, r2, acc in results:
    print(f"   {name:<15s}: R²={r2:.4f}, Accuracy={acc:.2f}%")
print(f"{'='*70}")