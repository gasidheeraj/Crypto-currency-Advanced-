"""
Cryptocurrency Price Prediction Dashboard
Built with Streamlit
"""
import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path
import joblib
import numpy as np
import os
from datetime import datetime, timedelta

# Add project root to Python path (IMPORTANT!)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from data_science.utils.data_loader import CryptoDataLoader
from data_science.indicators.calculate_all import calculate_all_indicators
from data_science.features.feature_engineer import FeatureEngineer
from data_science.models.data_preparation import DataPreparation
from data_science.models.xgboost_model import XGBoostPredictor

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Crypto Price Predictor",
    page_icon="🚀",
    layout="wide"
)

# ============================================================================
# HEADER
# ============================================================================

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size: 50px !important;
        font-weight: bold;
        background: linear-gradient(90deg, #00D9FF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-size: 18px;
        color: #888;
        margin-top: -20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">🚀 Crypto Price Predictor</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by Machine Learning & Technical Analysis</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.header("⚙️ Settings")

selected_crypto = st.sidebar.selectbox(
    "Select Cryptocurrency",
    ["bitcoin", "ethereum", "solana", "cardano", "dogecoin", "avalanche-2", "chainlink", "polkadot", "ripple"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Select a cryptocurrency to view predictions and analysis")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Refresh Data")

if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("Click to reload latest data from database")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    """
    **Crypto Price Predictor**
    
    This dashboard uses:
    - 📊 Technical indicators (RSI, MACD, BB)
    - 🤖 XGBoost ML model
    - 📈 31 engineered features
    - 💾 Real-time PostgreSQL data
    
    **Model Accuracy:** ~95%
    """
)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_crypto_data(crypto_id):
    """Load cryptocurrency data from database"""
    loader = CryptoDataLoader()
    data = loader.get_price_data(crypto_id)
    loader.close()
    return data

# Load data with spinner
with st.spinner(f"📥 Loading {selected_crypto} data..."):
    data = load_crypto_data(selected_crypto)

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

if data and len(data['prices']) > 0:
    prices = data['prices']
    timestamps = data['timestamps']
    
    # ========================================================================
    # CALCULATE INDICATORS EARLY (needed for chart)
    # ========================================================================
    with st.spinner("Calculating technical indicators..."):
        indicators = calculate_all_indicators(prices)
    
    # ========================================================================
    # METRICS ROW
    # ========================================================================
    
    st.subheader("📊 Current Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Current Price
    with col1:
        current_price = prices[-1]
        price_change = prices[-1] - prices[-2] if len(prices) > 1 else 0
        st.metric(
            label="💰 Current Price",
            value=f"${current_price:,.2f}",
            delta=f"${price_change:,.2f}"
        )
        
    
    # Total Change
    with col2:
        if len(prices) > 1:
            total_change = prices[-1] - prices[0]
            change_pct = (total_change / prices[0]) * 100
            st.metric(
                label="📈 Total Change",
                value=f"{change_pct:+.2f}%",
                delta=f"${total_change:,.2f}"
            )
        else:
            st.metric(label="📈 Total Change", value="N/A")
    
    # Highest Price
    with col3:
        high_price = prices.max()
        st.metric(
            label="⬆️ Highest",
            value=f"${high_price:,.2f}"
        )
    
    # Lowest Price
    with col4:
        low_price = prices.min()
        st.metric(
            label="⬇️ Lowest",
            value=f"${low_price:,.2f}"
        )
    
    st.markdown("---")
    
    # ========================================================================
    # STATISTICS SUMMARY
    # ========================================================================
    
    st.subheader("📊 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📈 Average", f"${prices.mean():,.2f}")
    
    with col2:
        volatility = prices.std()
        st.metric("📊 Volatility", f"${volatility:,.2f}")
    
    with col3:
        price_range = prices.max() - prices.min()
        st.metric("📏 Range", f"${price_range:,.2f}")
    
    with col4:
        st.metric("📦 Records", f"{len(prices)}")
    
    with col5:
        # Calculate trend
        if len(prices) > 1:
            trend = "📈 Up" if prices[-1] > prices[0] else "📉 Down"
        else:
            trend = "➡️ Flat"
        st.metric("🎯 Trend", trend)
    
    st.markdown("---")
    
    # ========================================================================
    # SUCCESS MESSAGE
    # ========================================================================
    
    st.success(f"✅ Successfully loaded {len(prices)} price records for {selected_crypto.upper()}")
    
    # ========================================================================
    # PRICE CHART
    # ========================================================================
    
    st.subheader("📈 Price History")
    
    # Create Plotly chart
    fig = go.Figure()
    
    # Add actual price line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=prices,
        mode='lines',
        name='Actual Price',
        line=dict(color='#00D9FF', width=2),
        hovertemplate='<b>%{x}</b><br>Price: $%{y:,.2f}<extra></extra>'
    ))
    
    # Add Bollinger Bands to chart
    if 'bb_upper' in indicators:
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=indicators['bb_upper'],
            mode='lines',
            name='BB Upper',
            line=dict(color='rgba(255,255,255,0.2)', width=1, dash='dash'),
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=indicators['bb_lower'],
            mode='lines',
            name='BB Lower',
            line=dict(color='rgba(255,255,255,0.2)', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(68,138,255,0.1)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=indicators['bb_middle'],
            mode='lines',
            name='BB Middle (MA)',
            line=dict(color='rgba(255,165,0,0.5)', width=1, dash='dot'),
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{selected_crypto.upper()} Price Chart",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        hovermode='x unified',
        height=500,
        template='plotly_dark',
        showlegend=True
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # TECHNICAL INDICATORS
    # ========================================================================
    
    st.subheader("📊 Technical Indicators")
    
    # Create 3 columns for indicators
    col1, col2, col3 = st.columns(3)
    
    # RSI
    with col1:
        latest_rsi = indicators['rsi'][-1]
        
        st.markdown("### RSI (14)")
        st.metric(
            label="Relative Strength Index",
            value=f"{latest_rsi:.2f}"
        )
        
        # RSI interpretation
        if latest_rsi > 70:
            st.error("🔴 OVERBOUGHT - Might drop soon")
        elif latest_rsi < 30:
            st.success("🟢 OVERSOLD - Might rise soon")
        else:
            st.info("🟡 NEUTRAL - Normal range")
        
        # Progress bar
        st.progress(latest_rsi / 100)
        st.caption(f"Range: 0 (Oversold) → 100 (Overbought)")
    
    # MACD
    with col2:
        latest_macd = indicators['macd_line'][-1]
        latest_signal = indicators['macd_signal'][-1]
        latest_hist = indicators['macd_histogram'][-1]
        
        st.markdown("### MACD")
        st.metric(
            label="Moving Average Convergence Divergence",
            value=f"{latest_macd:,.2f}"
        )
        
        # MACD interpretation
        if latest_macd > latest_signal:
            st.success("🟢 BULLISH - MACD above signal")
        else:
            st.error("🔴 BEARISH - MACD below signal")
        
        st.caption(f"Signal: {latest_signal:,.2f}")
        st.caption(f"Histogram: {latest_hist:,.2f}")
    
    # Bollinger Bands
    with col3:
        latest_upper = indicators['bb_upper'][-1]
        latest_middle = indicators['bb_middle'][-1]
        latest_lower = indicators['bb_lower'][-1]
        current_price = prices[-1]
        
        st.markdown("### Bollinger Bands")
        
        # Calculate position within bands
        band_width = latest_upper - latest_lower
        if band_width > 0:
            position = ((current_price - latest_lower) / band_width) * 100
        else:
            position = 50
        
        st.metric(
            label="Position in Bands",
            value=f"{position:.1f}%"
        )
        
        # Bollinger interpretation
        if position > 80:
            st.error("🔴 Near Upper Band - Might be overbought")
        elif position < 20:
            st.success("🟢 Near Lower Band - Might be oversold")
        else:
            st.info("🟡 Within Normal Range")
        
        st.caption(f"Upper: ${latest_upper:,.2f}")
        st.caption(f"Middle: ${latest_middle:,.2f}")
        st.caption(f"Lower: ${latest_lower:,.2f}")
    
    st.markdown("---")
    
    # ========================================================================
# ML PREDICTIONS
# ========================================================================
    st.header("🤖 Machine Learning Prediction")

    model_path = f"models/saved/xgboost_{selected_crypto}.pkl"

    if os.path.exists(model_path):
        try:
            # STEP 1: Load model FIRST to get feature order
            model_data = joblib.load(model_path)
            required_features = model_data['feature_names']
            
            # STEP 2: Get latest prices and indicators (already calculated above!)
            latest_prices = prices  # Use existing prices variable
            # indicators already calculated above, reuse it
            
            # STEP 3: Create features dict (order doesn't matter here)
            features_dict = {}
            
            # Yesterday's price (most important!)
            features_dict['yesterday_price'] = latest_prices[-1]
            
            # Lag features
            for lag in [2, 3, 5, 7]:
                if len(latest_prices) > lag:
                    features_dict[f'lag_{lag}'] = latest_prices[-lag]
                else:
                    features_dict[f'lag_{lag}'] = latest_prices[-1]
            
            # Moving averages
            for window in [7, 14, 30]:
                if len(latest_prices) >= window:
                    features_dict[f'ma_{window}'] = np.mean(latest_prices[-window:])
                else:
                    features_dict[f'ma_{window}'] = np.mean(latest_prices)
            
            # Momentum (percentage change)
            for period in [3, 7, 14]:
                if len(latest_prices) > period:
                    old_price = latest_prices[-period]
                    new_price = latest_prices[-1]
                    pct_change = ((new_price - old_price) / old_price) * 100
                    features_dict[f'momentum_{period}'] = pct_change
                else:
                    features_dict[f'momentum_{period}'] = 0.0
            
            # Volatility (7-day)
            if len(latest_prices) >= 7:
                returns = np.diff(latest_prices[-7:]) / latest_prices[-7:-1]
                features_dict['volatility_7d'] = np.std(returns) * 100
            else:
                features_dict['volatility_7d'] = 0.0
            
            # Technical indicators (already calculated!)
            features_dict['rsi'] = indicators['rsi'][-1]
            features_dict['macd'] = indicators['macd_line'][-1]
            
            # STEP 4: Build feature array in MODEL's order
            X = np.column_stack([features_dict[name] for name in required_features])
            
            # STEP 5: Make prediction
            if model_data.get('model_type') == 'hybrid_ensemble':
                # Hybrid ensemble prediction
                ridge_pred = model_data['ridge_model'].predict(X)[0]
                rf_pred = model_data['rf_model'].predict(X)[0]
                xgb_pred = model_data['xgb_model'].predict(X)[0]
                
                weights = model_data['weights']
                predicted_price = (
                    ridge_pred * weights['ridge'] +
                    rf_pred * weights['rf'] +
                    xgb_pred * weights['xgb']
                )
                
                # Show ensemble info
                st.info(f"🧠 **Ensemble:** Ridge ({weights['ridge']*100:.1f}%) + RF ({weights['rf']*100:.1f}%) + XGB ({weights['xgb']*100:.1f}%)")
            else:
                # Regular XGBoost
                predicted_price = model_data['model'].predict(X)[0]
                st.info("🤖 **Model Type:** Single XGBoost")
            
            # STEP 6: Sanity check
            current_price = latest_prices[-1]
            predicted_change_pct = ((predicted_price - current_price) / current_price) * 100
            
            # If prediction is >10% change, use conservative estimate
            if abs(predicted_change_pct) > 10:
                st.warning("⚠️ Model prediction seems extreme. Using conservative 2% estimate.")
                predicted_price = current_price * 1.02 if predicted_change_pct > 0 else current_price * 0.98
                predicted_change_pct = ((predicted_price - current_price) / current_price) * 100
            
            # STEP 7: Display prediction
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="💰 Current Price",
                    value=f"${current_price:,.2f}"
                )
                
            
            with col2:
                st.metric(
                    label="🔮 Predicted Next Price",
                    value=f"${predicted_price:,.2f}",
                    delta=f"{predicted_change_pct:.2f}%"
                )
            
            with col3:
                predicted_change = predicted_price - current_price
                st.metric(
                    label="📊 Predicted Change",
                    value=f"${predicted_change:,.2f}",
                    delta=f"{predicted_change_pct:.2f}%"
                )
            
            # Show feature order for debugging
            with st.expander("🔍 Debug: Feature Order"):
                st.write("**Model expects features in this order:**")
                st.write(required_features)
            
        except Exception as e:
            st.error(f"❌ Error making prediction: {e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.warning(f"⚠️ No trained model found for {selected_crypto}")
        st.info(f"💡 Train a model using: `python train_hybrid_model.py {selected_crypto}`")

    # ========================================================================
    # MODEL PERFORMANCE METRICS
    # ========================================================================
    
    st.markdown("---")
    st.subheader("📊 Model Performance")
    
    # Load model and get metrics on test data
    with st.spinner("📈 Calculating model performance..."):
        try:
            # Prepare same features as prediction
            features_dict = {}
            features_dict['yesterday_price'] = prices
            
            for lag in [2, 3, 5, 7]:
                lagged = np.zeros(len(prices))
                lagged[lag:] = prices[:-lag]
                lagged[:lag] = np.nan
                features_dict[f'lag_{lag}'] = lagged
            
            for window in [7, 14, 30]:
                ma = np.convolve(prices, np.ones(window)/window, mode='same')
                ma[:window-1] = np.nan
                features_dict[f'ma_{window}'] = ma
            
            for period in [3, 7, 14]:
                pct = np.zeros(len(prices))
                pct[period:] = (prices[period:] - prices[:-period]) / prices[:-period] * 100
                pct[:period] = np.nan
                features_dict[f'momentum_{period}'] = pct
            
            vol_7 = np.array([
                prices[max(0, i-6):i+1].std() if i >= 6 else np.nan
                for i in range(len(prices))
            ])
            features_dict['volatility_7d'] = vol_7
            features_dict['rsi'] = indicators['rsi']
            features_dict['macd'] = indicators['macd_line']
            
            # Convert to array
            feature_names = list(features_dict.keys())
            X = np.column_stack([features_dict[name] for name in feature_names])
            
            # Target
            target = np.zeros(len(prices))
            target[:-1] = prices[1:]
            target[-1] = np.nan
            
            # Remove NaN rows
            valid_mask = ~np.isnan(X).any(axis=1) & ~np.isnan(target)
            X_clean = X[valid_mask]
            y_clean = target[valid_mask]
            
            # Split
            split_idx = int(len(X_clean) * 0.8)
            X_test = X_clean[split_idx:]
            y_test = y_clean[split_idx:]
            
            # Load model
            model_path = f'models/saved/xgboost_{selected_crypto}.pkl'
            model_data = joblib.load(model_path)
            
            # Check if metrics are stored in model
            if 'metrics' in model_data:
                # Use stored metrics (faster!)
                metrics = model_data['metrics']
                mae = metrics['mae']
                mape = metrics['mape']
                r2 = metrics['r2']
                accuracy = metrics['accuracy']
                
            else:
                # Calculate metrics (slower)
                if model_data.get('model_type') == 'hybrid_ensemble':
                    ridge_pred = model_data['ridge_model'].predict(X_test)
                    rf_pred = model_data['rf_model'].predict(X_test)
                    xgb_pred = model_data['xgb_model'].predict(X_test)
                    
                    weights = model_data['weights']
                    predictions = (
                        ridge_pred * weights['ridge'] +
                        rf_pred * weights['rf'] +
                        xgb_pred * weights['xgb']
                    )
                else:
                    model = XGBoostPredictor()
                    model.model = model_data['model']
                    predictions = model.predict(X_test)
                
                mae = np.mean(np.abs(y_test - predictions))
                mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
                r2 = 1 - (np.sum((y_test - predictions)**2) / np.sum((y_test - np.mean(y_test))**2))
                accuracy = 100 - mape
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🎯 Model Accuracy",
                    value=f"{accuracy:.2f}%",
                    help="100% - MAPE (higher is better)"
                )
                if accuracy >= 99:
                    st.success("⭐⭐⭐⭐⭐ EXCELLENT")
                elif accuracy >= 97:
                    st.success("⭐⭐⭐⭐ VERY GOOD")
                elif accuracy >= 95:
                    st.info("⭐⭐⭐ GOOD")
                elif accuracy >= 92:
                    st.warning("⭐⭐ ACCEPTABLE")
                else:
                    st.error("⭐ NEEDS IMPROVEMENT")
            
            with col2:
                st.metric(
                    label="📊 MAPE",
                    value=f"{mape:.2f}%",
                    help="Mean Absolute Percentage Error (lower is better)"
                )
                if mape < 1:
                    st.success("Excellent (<1%)")
                elif mape < 3:
                    st.success("Very Good (<3%)")
                elif mape < 5:
                    st.info("Good (<5%)")
                elif mape < 10:
                    st.warning("Acceptable (<10%)")
                else:
                    st.error("Poor (>10%)")
            
            with col3:
                st.metric(
                    label="💰 MAE",
                    value=f"${mae:,.2f}",
                    help="Mean Absolute Error in dollars (lower is better)"
                )
                mae_percent = (mae / prices[-1]) * 100
                st.caption(f"{mae_percent:.2f}% of current price")
            
            with col4:
                st.metric(
                    label="📈 R² Score",
                    value=f"{r2:.4f}",
                    help="Variance explained by model (higher is better, max 1.0)"
                )
                if r2 >= 0.90:
                    st.success("Excellent (>0.90)")
                elif r2 >= 0.85:
                    st.success("Very Good (>0.85)")
                elif r2 >= 0.80:
                    st.info("Good (>0.80)")
                elif r2 >= 0.70:
                    st.warning("Acceptable (>0.70)")
                else:
                    st.error("Poor (<0.70)")
            
            # Show model type
            if model_data.get('model_type') == 'hybrid_ensemble':
                st.info("🔮 **Model Type:** Hybrid Ensemble (Ridge + Random Forest + XGBoost)")
            else:
                st.info("🤖 **Model Type:** Single XGBoost")
            
            # Interpretation
            st.markdown("### 📝 Model Interpretation")
            
            interpretation = f"""
            This model achieves **{accuracy:.2f}% accuracy** on {selected_crypto.upper()} price predictions.
            
            **What this means:**
            - On average, predictions are off by **${mae:,.2f}** ({mape:.2f}%)
            - The model explains **{r2*100:.1f}%** of price movements
            - R² Score of **{r2:.4f}** indicates {'excellent' if r2 >= 0.85 else 'good' if r2 >= 0.80 else 'acceptable'} predictive power
            """
            
            if accuracy >= 97:
                interpretation += "\n\n✅ **This is a high-quality model** suitable for price predictions."
            elif accuracy >= 95:
                interpretation += "\n\n✅ **This is a good model** with reliable predictions."
            elif accuracy >= 92:
                interpretation += "\n\n⚠️ **This model is acceptable** but could be improved."
            else:
                interpretation += "\n\n⚠️ **This model needs improvement.**"
            
            st.info(interpretation)
        
        except Exception as e:
            st.error(f"❌ Could not calculate model performance: {e}")
            st.info("💡 Make sure you've trained the hybrid model for this cryptocurrency")
    # ========================================================================
    # DATA PREVIEW
    # ========================================================================
    
    with st.expander("📋 View Raw Data"):
        st.write(f"**Price Range:** ${prices.min():,.2f} - ${prices.max():,.2f}")
        st.write(f"**Average Price:** ${prices.mean():,.2f}")
        st.write(f"**Data Points:** {len(prices)}")
        st.write(f"**Time Range:** {timestamps[0]} to {timestamps[-1]}")

else:
    # ========================================================================
    # ERROR MESSAGE
    # ========================================================================
    
    st.error(f"❌ No data found for {selected_crypto}")
    st.info("💡 Try selecting a different cryptocurrency from the sidebar")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 20px;'>
        <p style='color: gray; margin: 5px;'>
            Built by <b>Sai Dheeraj G</b>
        </p>
        <p style='color: gray; margin: 5px; font-size: 14px;'>
            🤖 Model: XGBoost | 📊 Features: 31 | 💾 Database: PostgreSQL | 🎯 Accuracy: ~95%
        </p>
        <p style='color: gray; margin: 5px; font-size: 12px;'>
            Data Source: CoinGecko API | Updated every 5 minutes
        </p>
    </div>
    """,
    unsafe_allow_html=True
)