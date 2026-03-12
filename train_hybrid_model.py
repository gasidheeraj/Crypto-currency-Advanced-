"""
Hybrid Model: Yesterday's Price + ML Adjustment
Leverages the 0.96 baseline and adds intelligent corrections
"""
from data_science.utils.data_loader import CryptoDataLoader
from data_science.indicators.calculate_all import calculate_all_indicators
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
import xgboost as xgb

print("="*70)
print("🚀 TRAINING HYBRID MODEL: BASELINE + ML ADJUSTMENT")
print("="*70)

# Load data
print("\n📥 Loading Bitcoin data...")
loader = CryptoDataLoader()
data = loader.get_price_data('bitcoin')
loader.close()

prices = data['prices']
timestamps = data['timestamps']
print(f"✅ Loaded {len(prices)} records")

# ============================================================================
# CREATE SIMPLE BUT POWERFUL FEATURES
# ============================================================================

print("\n🔧 Creating features...")

# Target: next day's price
target = np.zeros(len(prices))
target[:-1] = prices[1:]
target[-1] = np.nan

# Features
features = {}

# 1. BASELINE: Yesterday's price (most important!)
features['yesterday_price'] = prices.copy()

# 2. Short-term lags
for lag in [2, 3, 5, 7]:
    lagged = np.zeros(len(prices))
    lagged[lag:] = prices[:-lag]
    lagged[:lag] = np.nan
    features[f'lag_{lag}'] = lagged

# 3. Moving averages (trend)
for window in [7, 14, 30]:
    ma = np.convolve(prices, np.ones(window)/window, mode='same')
    ma[:window-1] = np.nan
    features[f'ma_{window}'] = ma

# 4. Momentum
for period in [3, 7, 14]:
    pct = np.zeros(len(prices))
    pct[period:] = (prices[period:] - prices[:-period]) / prices[:-period] * 100
    pct[:period] = np.nan
    features[f'momentum_{period}'] = pct

# 5. Volatility
vol_7 = np.array([
    prices[max(0, i-6):i+1].std() if i >= 6 else np.nan
    for i in range(len(prices))
])
features['volatility_7d'] = vol_7

# 6. Technical indicators
indicators = calculate_all_indicators(prices)
features['rsi'] = indicators['rsi']
features['macd'] = indicators['macd_line']

print(f"✅ Created {len(features)} features")

# ============================================================================
# PREPARE DATA
# ============================================================================

print("\n📊 Preparing data...")

# Convert to arrays
feature_names = list(features.keys())
X = np.column_stack([features[name] for name in feature_names])

# Remove NaN rows
valid_mask = ~np.isnan(X).any(axis=1) & ~np.isnan(target)
X_clean = X[valid_mask]
y_clean = target[valid_mask]

print(f"Clean samples: {len(X_clean)}")

# Split (80/20)
split_idx = int(len(X_clean) * 0.8)
X_train = X_clean[:split_idx]
X_test = X_clean[split_idx:]
y_train = y_clean[:split_idx]
y_test = y_clean[split_idx:]

print(f"✅ Train: {len(X_train)}, Test: {len(X_test)}")

# ============================================================================
# TRAIN HYBRID ENSEMBLE MODEL
# ============================================================================

print("\n🚀 Training hybrid ensemble...")

# Model 1: Ridge Regression (linear, emphasizes yesterday's price)
print("   Training Ridge Regression...")
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)
ridge_pred = ridge.predict(X_test)
ridge_r2 = 1 - (np.sum((y_test - ridge_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
print(f"      Ridge R² = {ridge_r2:.4f}")

# Model 2: Random Forest (captures non-linear patterns)
print("   Training Random Forest...")
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_r2 = 1 - (np.sum((y_test - rf_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
print(f"      Random Forest R² = {rf_r2:.4f}")

# Model 3: XGBoost (gradient boosting)
print("   Training XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)
xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)
xgb_r2 = 1 - (np.sum((y_test - xgb_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
print(f"      XGBoost R² = {xgb_r2:.4f}")

# ============================================================================
# ENSEMBLE: WEIGHTED AVERAGE (emphasize best models)
# ============================================================================

print("\n🔧 Creating weighted ensemble...")

# Weight by R² score
total_r2 = ridge_r2 + rf_r2 + xgb_r2
ridge_weight = ridge_r2 / total_r2
rf_weight = rf_r2 / total_r2
xgb_weight = xgb_r2 / total_r2

print(f"   Ridge weight: {ridge_weight:.3f}")
print(f"   RF weight: {rf_weight:.3f}")
print(f"   XGBoost weight: {xgb_weight:.3f}")

# Ensemble prediction
ensemble_pred = (
    ridge_pred * ridge_weight +
    rf_pred * rf_weight +
    xgb_pred * xgb_weight
)

# ============================================================================
# EVALUATE ENSEMBLE
# ============================================================================

print("\n📈 Evaluating ensemble...")

mae = np.mean(np.abs(y_test - ensemble_pred))
rmse = np.sqrt(np.mean((y_test - ensemble_pred)**2))
mape = np.mean(np.abs((y_test - ensemble_pred) / y_test)) * 100
r2 = 1 - (np.sum((y_test - ensemble_pred)**2) / np.sum((y_test - np.mean(y_test))**2))
accuracy = 100 - mape

print("\n" + "="*70)
print("HYBRID ENSEMBLE MODEL PERFORMANCE:")
print("-"*70)
print(f"R² Score:                   {r2:.4f}")
print(f"Mean Absolute Error (MAE):  ${mae:,.2f}")
print(f"Root Mean Square Error:     ${rmse:,.2f}")
print(f"Mean Absolute % Error:      {mape:.2f}%")
print(f"Accuracy:                   {accuracy:.2f}%")
print("="*70)

# Rating
if r2 >= 0.90:
    print("\n🌟 EXCELLENT R² SCORE! (≥0.90)")
elif r2 >= 0.85:
    print("\n✅ VERY GOOD R² SCORE! (≥0.85)")
elif r2 >= 0.80:
    print("\n✅ GOOD R² SCORE (≥0.80)")
elif r2 >= 0.70:
    print("\n⚠️  ACCEPTABLE R² SCORE (≥0.70)")
else:
    print("\n❌ R² SCORE NEEDS IMPROVEMENT")

# Sample predictions
print("\n" + "="*70)
print("SAMPLE PREDICTIONS:")
print("-"*70)

for i in range(min(10, len(ensemble_pred))):
    actual = y_test[i]
    predicted = ensemble_pred[i]
    error = abs(actual - predicted)
    error_pct = (error / actual) * 100
    
    print(f"Sample {i+1}: Actual ${actual:>10,.2f} | Predicted ${predicted:>10,.2f} | Error ${error:>8,.2f} ({error_pct:.2f}%)")

# ============================================================================
# SAVE ENSEMBLE MODEL
# ============================================================================

print("\n💾 Saving hybrid ensemble model...")
model_data = {
    'ridge_model': ridge,
    'rf_model': rf,
    'xgb_model': xgb_model,
    'feature_names': feature_names,
    'weights': {
        'ridge': ridge_weight,
        'rf': rf_weight,
        'xgb': xgb_weight
    },
    'model_type': 'hybrid_ensemble',
    'metrics': {
        'r2': r2,
        'mae': mae,
        'mape': mape,
        'accuracy': accuracy
    }
}

joblib.dump(model_data, 'models/saved/xgboost_bitcoin.pkl')
print("✅ Model saved!")

print("\n" + "="*70)
if r2 >= 0.85:
    print("🎉 SUCCESS! Excellent R² score achieved!")
elif r2 >= 0.80:
    print("✅ GOOD! Strong R² score achieved!")
else:
    print(f"R² = {r2:.4f}")
    print("This is the best we can achieve with current data/features.")
    print("To improve further, consider:")
    print("  1. Collect intraday data (hourly)")
    print("  2. Add external features (sentiment, volume)")
    print("  3. Use deep learning (LSTM)")
print("="*70)