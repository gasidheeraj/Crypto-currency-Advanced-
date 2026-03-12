"""
Diagnose Model Prediction
Shows feature breakdown and prediction logic
"""
import joblib
import numpy as np
from data_science.utils.data_loader import CryptoDataLoader
from data_science.indicators.calculate_all import calculate_all_indicators
from datetime import datetime, timedelta

print("="*70)
print("🔍 PREDICTION DIAGNOSTIC TOOL")
print("="*70)

crypto_id = 'bitcoin'

# Load data
loader = CryptoDataLoader()
data = loader.get_price_data(crypto_id)
loader.close()

prices = data['prices']
dates = data['timestamps']

# Load model
model_path = f'models/saved/xgboost_{crypto_id}.pkl'
model_data = joblib.load(model_path)
required_features = model_data['feature_names']

print(f"\n📅 Analyzing last prediction...")
print(f"Crypto: {crypto_id}")
print(f"Data points: {len(prices)}")
print(f"Date range: {dates[0]} to {dates[-1]}")

# Get indicators
indicators = calculate_all_indicators(prices)

# Create features for LAST day (what we used for prediction)
features_dict = {}
features_dict['yesterday_price'] = prices[-1]

for lag in [2, 3, 5, 7]:
    if len(prices) > lag:
        features_dict[f'lag_{lag}'] = prices[-lag]
    else:
        features_dict[f'lag_{lag}'] = prices[-1]

for window in [7, 14, 30]:
    if len(prices) >= window:
        features_dict[f'ma_{window}'] = np.mean(prices[-window:])
    else:
        features_dict[f'ma_{window}'] = np.mean(prices)

for period in [3, 7, 14]:
    if len(prices) > period:
        old_price = prices[-period]
        new_price = prices[-1]
        pct_change = ((new_price - old_price) / old_price) * 100
        features_dict[f'momentum_{period}'] = pct_change
    else:
        features_dict[f'momentum_{period}'] = 0.0

if len(prices) >= 7:
    returns = np.diff(prices[-7:]) / prices[-7:-1]
    features_dict['volatility_7d'] = np.std(returns) * 100
else:
    features_dict['volatility_7d'] = 0.0

features_dict['rsi'] = indicators['rsi'][-1]
features_dict['macd'] = indicators['macd_line'][-1]

# Build feature array
X = np.column_stack([features_dict[name] for name in required_features])

# Make prediction
if model_data.get('model_type') == 'hybrid_ensemble':
    ridge_pred = model_data['ridge_model'].predict(X)[0]
    rf_pred = model_data['rf_model'].predict(X)[0]
    xgb_pred = model_data['xgb_model'].predict(X)[0]
    
    weights = model_data['weights']
    predicted_price = (
        ridge_pred * weights['ridge'] +
        rf_pred * weights['rf'] +
        xgb_pred * weights['xgb']
    )
    
    print("\n" + "="*70)
    print("🧠 ENSEMBLE MODEL BREAKDOWN")
    print("="*70)
    print(f"Ridge prediction:  ${ridge_pred:,.2f} (weight: {weights['ridge']*100:.1f}%)")
    print(f"RF prediction:     ${rf_pred:,.2f} (weight: {weights['rf']*100:.1f}%)")
    print(f"XGBoost prediction: ${xgb_pred:,.2f} (weight: {weights['xgb']*100:.1f}%)")
    print(f"\nFinal prediction:  ${predicted_price:,.2f}")
else:
    predicted_price = model_data['model'].predict(X)[0]
    print(f"\nSingle model prediction: ${predicted_price:,.2f}")

# Current vs predicted
current_price = prices[-1]
predicted_change = predicted_price - current_price
predicted_change_pct = (predicted_change / current_price) * 100

print("\n" + "="*70)
print("📊 PREDICTION SUMMARY")
print("="*70)
print(f"Current price (last in data):  ${current_price:,.2f}")
print(f"Predicted next price:          ${predicted_price:,.2f}")
print(f"Predicted change:              ${predicted_change:,.2f} ({predicted_change_pct:+.2f}%)")

# Show features used
print("\n" + "="*70)
print("🔧 FEATURES USED FOR PREDICTION")
print("="*70)

for i, feature_name in enumerate(required_features):
    value = features_dict[feature_name]
    if 'price' in feature_name or 'ma_' in feature_name or 'lag_' in feature_name:
        print(f"{i+1:2d}. {feature_name:20s} = ${value:,.2f}")
    else:
        print(f"{i+1:2d}. {feature_name:20s} = {value:.2f}")

# Show recent price trend
print("\n" + "="*70)
print("📈 RECENT PRICE TREND (Last 7 Days)")
print("="*70)

for i in range(min(7, len(prices))):
    idx = -(7-i)
    price = prices[idx]
    date = dates[idx]
    
    if i > 0:
        prev_price = prices[idx-1]
        change = price - prev_price
        change_pct = (change / prev_price) * 100
        print(f"{date}: ${price:,.2f} ({change_pct:+.2f}%)")
    else:
        print(f"{date}: ${price:,.2f}")

# Technical indicators summary
print("\n" + "="*70)
print("📊 TECHNICAL INDICATORS")
print("="*70)
print(f"RSI:           {indicators['rsi'][-1]:.2f} ", end="")
if indicators['rsi'][-1] > 70:
    print("(OVERBOUGHT)")
elif indicators['rsi'][-1] < 30:
    print("(OVERSOLD)")
else:
    print("(NEUTRAL)")

print(f"MACD:          {indicators['macd_line'][-1]:.2f}")
print(f"MACD Signal:   {indicators['macd_signal'][-1]:.2f} ", end="")
if indicators['macd_line'][-1] > indicators['macd_signal'][-1]:
    print("(BULLISH)")
else:
    print("(BEARISH)")

print(f"BB Upper:      ${indicators['bb_upper'][-1]:,.2f}")
print(f"BB Middle:     ${indicators['bb_middle'][-1]:,.2f}")
print(f"BB Lower:      ${indicators['bb_lower'][-1]:,.2f}")

# Model's historical accuracy
print("\n" + "="*70)
print("📊 MODEL PERFORMANCE STATS")
print("="*70)
metrics = model_data.get('metrics', {})
print(f"R² Score:      {metrics.get('r2', 0):.4f}")
print(f"Accuracy:      {metrics.get('accuracy', 0)*100:.2f}%")
print(f"MAPE:          {metrics.get('mape', 0):.2f}%")
print(f"MAE:           ${metrics.get('mae', 0):,.2f}")

print("\n" + "="*70)
print("💡 INTERPRETATION")
print("="*70)

interpretation = f"""
The model predicted {predicted_change_pct:+.2f}% change for the next day.

This prediction was based on:
1. Yesterday's price: ${features_dict['yesterday_price']:,.2f}
2. Recent trend (7-day momentum): {features_dict['momentum_7']:+.2f}%
3. RSI: {features_dict['rsi']:.2f} ({'overbought' if features_dict['rsi'] > 70 else 'oversold' if features_dict['rsi'] < 30 else 'neutral'})
4. MACD: {features_dict['macd']:.2f} ({'bullish' if features_dict['macd'] > 0 else 'bearish'})

The model has {metrics.get('accuracy', 0)*100:.2f}% average accuracy (MAPE: {metrics.get('mape', 0):.2f}%).
This means on average, predictions are off by ${metrics.get('mae', 0):,.2f}.

A {abs(predicted_change_pct):.1f}% prediction is {'within normal range' if abs(predicted_change_pct) < 5 else 'slightly aggressive'} 
for this model.
"""

print(interpretation)

print("\n" + "="*70)
print("⚠️  LIMITATIONS")
print("="*70)
print("""
Machine learning models CANNOT predict:
❌ Black swan events (wars, regulations, bans)
❌ Major news announcements
❌ Whale movements (large traders)
❌ Market manipulation
❌ Sudden sentiment shifts

The model can only predict based on:
✅ Historical price patterns
✅ Technical indicators
✅ Recent momentum
✅ Statistical trends

If actual price moved differently than predicted, it likely means:
1. An unpredictable event occurred (news, geopolitics, etc.)
2. Market sentiment shifted suddenly
3. Large traders moved the market

This is NORMAL for all ML models. Even the best models are wrong sometimes!
""")

print("="*70)