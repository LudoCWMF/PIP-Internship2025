import streamlit as st
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.bitcoin_model import BitcoinPredictor
from utils.trading_platform import main as trading_main

st.set_page_config(
    page_title="Bitcoin Trading Platform",
    page_icon="₿",
    layout="wide"
)

def main():
    st.title("Bitcoin Trading Platform")
    st.write("Welcome to the Bitcoin Trading Platform! This application provides real-time Bitcoin price tracking, predictions, and analysis.")

    predictor = BitcoinPredictor()
    live_data = predictor.get_live_market_data()
    if live_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price (Live)", f"${live_data['current_price']:,.2f}")
        with col2:
            st.metric("24h High (Live)", f"${live_data['high_24h']:,.2f}")
        with col3:
            st.metric("24h Low (Live)", f"${live_data['low_24h']:,.2f}")
        with col4:
            st.metric("24h Volume (Live)", f"${live_data['volume_24h']:,.0f}")
        st.write(f"Market Cap (Live): ${live_data['market_cap']:,.0f}")
        st.write(f"Circulating Supply: {live_data['circulating_supply']:,.0f} BTC")
    else:
        st.warning("Live data unavailable. Showing latest available data.")
        stats = predictor.get_summary_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${stats['current_price']:,.2f}")
        with col2:
            st.metric("24h High", f"${stats['high_24h']:,.2f}")
        with col3:
            st.metric("24h Low", f"${stats['low_24h']:,.2f}")
        with col4:
            st.metric("24h Volume", f"{stats['volume_24h']:,.0f}")
        st.write(f"Market Cap: ${stats['market_cap']:,.0f}")

    # Display price changes
    stats = predictor.get_summary_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("7d Change", f"{stats['change_7d']:.2f}%")
    with col2:
        st.metric("30d Change", f"{stats['change_30d']:.2f}%")
    with col3:
        st.metric("YTD Change", f"{stats['change_ytd']:.2f}%")

    # Get predictions
    predictions = predictor.get_predictions()
    st.subheader("Price Predictions")
    st.write(f"Predicted Price: ${predictions['predicted_price']:,.2f}")
    st.write(f"Confidence Interval: ${predictions['confidence_lower']:,.2f} - ${predictions['confidence_upper']:,.2f}")

    # Get performance metrics
    metrics = predictor.get_performance_metrics()
    st.subheader("Model Performance")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MSE", f"${metrics['mse']:,.2f}")
    with col2:
        st.metric("RMSE", f"${metrics['rmse']:,.2f}")
    with col3:
        st.metric("MAE", f"${metrics['mae']:,.2f}")
    with col4:
        st.metric("R² Score", f"{metrics['r2']:.4f}")

if __name__ == "__main__":
    main() 