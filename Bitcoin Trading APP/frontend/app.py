import streamlit as st
import plotly.graph_objects as go
import sys
import os
import pandas as pd

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.Trading_Platoform_Bitcoin import get_crypto_data, prepare_features, train_model_and_predict, predict_fiscal_year

# Page config
st.set_page_config(
    page_title="Cryptocurrency Trading Hub",
    page_icon="₿",
    layout="wide"
)

crypto_options = {
    "Bitcoin": {
        "symbol": "BTC-USD",
        "logo": None,  # Ignore images for now
        "description": "Bitcoin is the first decentralized cryptocurrency, created in 2009 by Satoshi Nakamoto."
    },
    "Ethereum": {
        "symbol": "ETH-USD",
        "logo": None,
        "description": "Ethereum is a decentralized platform that enables smart contracts and decentralized applications."
    },
    "Tether": {
        "symbol": "USDT-USD",
        "logo": None,
        "description": "Tether is a stablecoin pegged to the US Dollar, designed to maintain a stable value."
    },
    "XRP": {
        "symbol": "XRP-USD",
        "logo": None,
        "description": "XRP is a digital asset built for payments, enabling fast and low-cost international money transfers."
    }
}

if 'selected_crypto' not in st.session_state:
    st.session_state.selected_crypto = None

def get_price_change(crypto_data):
    if len(crypto_data) >= 2:
        current_price = crypto_data['Close'].iloc[-1]
        previous_price = crypto_data['Close'].iloc[-2]
        change = ((current_price - previous_price) / previous_price) * 100
        return change
    return 0

def show_dashboard():
    st.title("Cryptocurrency Trading Hub")
    st.markdown("Welcome to the Cryptocurrency Trading Hub. Select a cryptocurrency to view detailed analysis and predictions.")
    cols = st.columns(2)
    for idx, (crypto_name, crypto_info) in enumerate(crypto_options.items()):
        with cols[idx % 2]:
            try:
                crypto_data = get_crypto_data(crypto_info['symbol'])
                price_change = get_price_change(crypto_data)
                price = crypto_data['Close'].iloc[-1]
                is_up = price_change >= 0
                arrow = '↑' if is_up else '↓'
                change_color = 'green' if is_up else 'red'
                st.markdown(f"### {crypto_name}")
                st.markdown(f"**Price:** £{price:,.4f}")
                st.markdown(f"<span style='color:{change_color}'>{arrow} {abs(price_change):.2f}%</span>", unsafe_allow_html=True)
                if st.button(f"View Details - {crypto_name}", key=f"details_{crypto_name}"):
                    st.session_state.selected_crypto = crypto_name
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading data for {crypto_name}: {str(e)}")

def show_details():
    selected_crypto = st.session_state.selected_crypto
    if selected_crypto not in crypto_options:
        st.error("Invalid cryptocurrency selected")
        st.session_state.selected_crypto = None
        st.rerun()
        return

    crypto_info = crypto_options[selected_crypto]
    if st.button("← Back to Home", key="back_to_home"):
        st.session_state.selected_crypto = None
        st.rerun()
        return

    st.header(selected_crypto)
    st.markdown(f"**Symbol:** {crypto_info['symbol']}")
    st.markdown(f"{crypto_info['description']}")

    try:
        crypto_data = get_crypto_data(crypto_info['symbol'])
        prepared_data = prepare_features(crypto_data)
        model_results, scaler, features, tomorrow_pred, y_test, ensemble_pred, metrics = train_model_and_predict(prepared_data)

        # --- Price Chart ---
        price_ranges = {
            "Last Week": 7,
            "Last Month": 30,
            "6 Months": 182,
            "1 Year": 365,
            "5 Years": 1825,
            "All Time": None
        }
        st.markdown("---")
        st.header(f"Live {selected_crypto} Market Data")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"£{crypto_data['Close'].iloc[-1]:,.4f}")
        with col2:
            st.metric("24h High", f"£{crypto_data['High'].iloc[-1]:,.4f}")
        with col3:
            st.metric("24h Low", f"£{crypto_data['Low'].iloc[-1]:,.4f}")
        with col4:
            st.metric("24h Volume", f"{crypto_data['Volume'].iloc[-1]:,.0f}")

        st.markdown("---")
        st.header(f"{selected_crypto} Price Prediction")
        st.metric("Tomorrow's Predicted Price", f"£{tomorrow_pred:,.4f}")

        st.subheader("Model Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("MSE", f"{metrics['MSE']:,.2f}")
        with col2:
            st.metric("RMSE", f"{metrics['RMSE']:,.2f}")
        with col3:
            st.metric("MAE", f"{metrics['MAE']:,.2f}")
        with col4:
            st.metric("R² Score", f"{metrics['R2']:.3f}")

        st.markdown("---")
        st.header(f"{selected_crypto} Historical Price Chart")
        price_range = st.selectbox("Price Chart Time Range", list(price_ranges.keys()), index=4, key="price_range")
        n_price = price_ranges[price_range]
        price_data = prepared_data.tail(n_price) if n_price is not None else prepared_data
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=price_data.index,
            y=price_data['Close'],
            mode='lines',
            name='Historical Price',
            line=dict(color='royalblue', width=2)
        ))
        fig_hist.update_layout(
            xaxis_title='Date',
            yaxis_title='Price (£)',
            template='plotly_dark',
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # --- Next Year Prediction Chart ---
        st.markdown("---")
        st.header(f"{selected_crypto} Next Year Price Prediction")
        best_model_name = max(model_results.items(), key=lambda x: x[1]['metrics']['R2'])[0]
        fiscal_year_preds = predict_fiscal_year(prepared_data, model_results[best_model_name]['model'], scaler, features)
        future_dates = pd.date_range(start=prepared_data.index[-1] + pd.Timedelta(days=1), periods=365, freq='D')
        fig_future = go.Figure()
        fig_future.add_trace(go.Scatter(
            x=future_dates,
            y=fiscal_year_preds,
            mode='lines',
            name='Next Year Prediction',
            line=dict(color='orange', width=2)
        ))
        fig_future.update_layout(
            xaxis_title='Date',
            yaxis_title='Predicted Price (£)',
            template='plotly_dark',
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_future, use_container_width=True)

        # --- Detailed Table of Next Year Predictions ---
        detailed_pred_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Price (£)': fiscal_year_preds
        })
        detailed_pred_df['Percentage Change (%)'] = detailed_pred_df['Predicted Price (£)'].pct_change() * 100
        st.markdown('#### Detailed Table of Next Year Predicted Prices')
        st.dataframe(detailed_pred_df, use_container_width=True)

        st.markdown("---")
        st.header("Technical Indicators")
        rsi_ranges = {
            "Last Week": 7,
            "Last Month": 30,
            "6 Months": 182,
            "1 Year": 365,
            "5 Years": 1825,
            "All Time": None
        }
        macd_ranges = rsi_ranges.copy()
        tabs = st.tabs(["RSI", "MACD"])
        with tabs[0]:
            rsi_range = st.selectbox("RSI Time Range", list(rsi_ranges.keys()), index=4, key="rsi_range")
            n_rsi = rsi_ranges[rsi_range]
            rsi_data = prepared_data.tail(n_rsi) if n_rsi is not None else prepared_data
            if 'RSI' not in rsi_data.columns:
                st.error("RSI column is missing from the data. Please check backend feature calculation.")
            elif rsi_data['RSI'].isna().all():
                st.warning("RSI column exists but all values are NaN. This may be due to insufficient data for calculation. Showing debug info below:")
                st.write(rsi_data['RSI'].head(20))
                st.write(rsi_data['RSI'].tail(20))
            elif rsi_data['RSI'].notna().sum() > 10:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=rsi_data.index,
                    y=rsi_data['RSI'],
                    mode='lines',
                    line=dict(color='purple', width=1),
                    name='RSI'
                ))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(
                    yaxis_title='RSI',
                    template='plotly_dark',
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_rsi, use_container_width=True)
                st.markdown(
                    """
                    **RSI (Relative Strength Index):**  
                    - RSI above 70: *Overbought* (price may be too high, possible reversal down)  
                    - RSI below 30: *Oversold* (price may be too low, possible reversal up)  
                    - 30–70: Neutral zone  
                    """
                )
            else:
                st.info("Not enough data to display RSI for this range.")
        with tabs[1]:
            macd_range = st.selectbox("MACD Time Range", list(macd_ranges.keys()), index=4, key="macd_range")
            n_macd = macd_ranges[macd_range]
            macd_data = prepared_data.tail(n_macd) if n_macd is not None else prepared_data
            if 'MACD' not in macd_data.columns or 'MACD_signal' not in macd_data.columns:
                st.error("MACD or MACD_signal column is missing from the data. Please check backend feature calculation.")
            elif macd_data['MACD'].isna().all() or macd_data['MACD_signal'].isna().all():
                st.warning("MACD or MACD_signal column exists but all values are NaN. This may be due to insufficient data for calculation. Showing debug info below:")
                st.write(macd_data[['MACD', 'MACD_signal']].head(20))
                st.write(macd_data[['MACD', 'MACD_signal']].tail(20))
            elif macd_data['MACD'].notna().sum() > 10 and macd_data['MACD_signal'].notna().sum() > 10:
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(
                    x=macd_data.index,
                    y=macd_data['MACD'],
                    mode='lines',
                    line=dict(color='blue', width=1),
                    name='MACD'
                ))
                fig_macd.add_trace(go.Scatter(
                    x=macd_data.index,
                    y=macd_data['MACD_signal'],
                    mode='lines',
                    line=dict(color='orange', width=1),
                    name='Signal'
                ))
                fig_macd.update_layout(
                    yaxis_title='MACD',
                    template='plotly_dark',
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_macd, use_container_width=True)
                st.markdown(
                    """
                    **MACD (Moving Average Convergence Divergence):**  
                    - When MACD crosses above the Signal line: *Bullish* (potential buy signal)  
                    - When MACD crosses below the Signal line: *Bearish* (potential sell signal)  
                    - The further MACD is from zero, the stronger the trend  
                    """
                )
            else:
                st.info("Not enough data to display MACD for this range.")

        st.markdown("---")
        st.header("Statistical Summary")
        summary_ranges = {
            "Last Week": 7,
            "Last Month": 30,
            "6 Months": 182,
            "1 Year": 365,
            "5 Years": 1825,
            "All Time": None
        }
        summary_range = st.selectbox("Summary Time Range", list(summary_ranges.keys()), index=4, key="summary_range")
        n_summary = summary_ranges[summary_range]
        summary_data = prepared_data.tail(n_summary) if n_summary is not None else prepared_data
        st.markdown(f"#### {summary_range} Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"£{summary_data['Close'].mean():,.4f}")
            st.metric("Median Price", f"£{summary_data['Close'].median():,.4f}")
        with col2:
            if 'Volatility_30' in summary_data.columns:
                st.metric("Volatility", f"{summary_data['Volatility_30'].mean():.2f}")
            st.metric(f"High", f"£{summary_data['Close'].max():,.4f}")
        with col3:
            st.metric(f"Low", f"£{summary_data['Close'].min():,.4f}")
            st.metric("Recent Volume", f"{crypto_data['Volume'].iloc[-1]:,.0f}")

    except Exception as e:
        st.error(f"An error occurred while loading the details: {str(e)}")
        if st.button("Return to Dashboard", key="return_dashboard"):
            st.session_state.selected_crypto = None
            st.rerun()

# --- MAIN LOGIC ---
if st.session_state.selected_crypto is None:
    show_dashboard()
else:
    show_details()