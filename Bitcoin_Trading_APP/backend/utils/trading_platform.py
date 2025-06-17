import yfinance as yh
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, VotingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from matplotlib.dates import YearLocator, DateFormatter, MonthLocator
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression
import ta
import warnings
import sys
from joblib import Parallel, delayed
import multiprocessing
from functools import lru_cache
import streamlit as st
import requests

warnings.filterwarnings('ignore')

@st.cache_data(ttl=3600)
def get_crypto_data(symbol="BTC-USD"):
    # Get data from the crypto's inception to today
    end_date = datetime.now()
    start_date = datetime(2010, 7, 17)  # Default for BTC, but yfinance will handle shorter histories
    
    try:
        crypto_data = yh.download(symbol, 
                                start=start_date.strftime('%Y-%m-%d'),
                                end=end_date.strftime('%Y-%m-%d'),
                                progress=False)
        
        # Ensure we have enough data
        if len(crypto_data) < 200:
            raise ValueError(f"Not enough historical data for {symbol}. Need at least 200 data points. Current data points: {len(crypto_data)}")
        
        # Flatten MultiIndex columns if they exist
        if isinstance(crypto_data.columns, pd.MultiIndex):
            crypto_data.columns = [col[0] for col in crypto_data.columns]
        
        # Ensure we have the most recent data
        if (end_date - crypto_data.index[-1]).days > 1:
            print(f"Warning: Most recent data is from {crypto_data.index[-1].strftime('%Y-%m-%d')}")
        
        return crypto_data
        
    except Exception as e:
        raise ValueError(f"Error downloading data for {symbol}: {str(e)}")

@lru_cache(maxsize=128)
def calculate_technical_indicators_cached(close, high, low, volume):
    # Convert numpy arrays to pandas Series for ta library
    close_series = pd.Series(close)
    high_series = pd.Series(high)
    low_series = pd.Series(low)
    volume_series = pd.Series(volume)
    
    indicators = {}
    
    # Trend Indicators
    indicators['EMA_9'] = ta.trend.ema_indicator(close_series, window=9)
    indicators['EMA_21'] = ta.trend.ema_indicator(close_series, window=21)
    indicators['EMA_50'] = ta.trend.ema_indicator(close_series, window=50)
    indicators['MACD'] = ta.trend.macd_diff(close_series)
    indicators['ADX'] = ta.trend.adx(high_series, low_series, close_series)
    
    # Momentum Indicators
    indicators['RSI'] = ta.momentum.rsi(close_series)
    indicators['Stoch'] = ta.momentum.stoch(high_series, low_series, close_series)
    indicators['Williams_R'] = ta.momentum.williams_r(high_series, low_series, close_series)
    indicators['ROC'] = ta.momentum.roc(close_series)
    
    # Volatility Indicators
    indicators['BB_high'] = ta.volatility.bollinger_hband(close_series)
    indicators['BB_low'] = ta.volatility.bollinger_lband(close_series)
    indicators['BB_width'] = (indicators['BB_high'] - indicators['BB_low']) / close_series
    indicators['ATR'] = ta.volatility.average_true_range(high_series, low_series, close_series)
    
    # Volume Indicators
    indicators['OBV'] = ta.volume.on_balance_volume(close_series, volume_series)
    indicators['CMF'] = ta.volume.chaikin_money_flow(high_series, low_series, close_series, volume_series)
    indicators['MFI'] = ta.volume.money_flow_index(high_series, low_series, close_series, volume_series)
    
    return indicators

def calculate_technical_indicators(df):
    # Trend Indicators
    df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
    df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['ADX'] = ta.trend.adx(df['High'], df['Low'], df['Close'])

    # Momentum Indicators
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['Stoch'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
    df['Williams_R'] = ta.momentum.williams_r(df['High'], df['Low'], df['Close'])
    df['ROC'] = ta.momentum.roc(df['Close'])

    # Volatility Indicators
    df['BB_high'] = ta.volatility.bollinger_hband(df['Close'])
    df['BB_low'] = ta.volatility.bollinger_lband(df['Close'])
    df['BB_width'] = (df['BB_high'] - df['BB_low']) / df['Close']
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

    # Volume Indicators
    df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
    df['CMF'] = ta.volume.chaikin_money_flow(df['High'], df['Low'], df['Close'], df['Volume'])
    df['MFI'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])

    return df

@st.cache_data
def prepare_features(df):
    # Make a copy to avoid modifying the original dataframe
    df = df.copy()
    
    # Forward fill missing values for price data
    price_columns = ['Open', 'High', 'Low', 'Close']
    df[price_columns] = df[price_columns].fillna(method='ffill')
    
    # Fill volume with 0 if missing
    df['Volume'] = df['Volume'].fillna(0)
    
    # Calculate returns using vectorized operations
    df['Returns'] = df['Close'].pct_change()
    df['Returns_5d'] = df['Close'].pct_change(periods=5)
    df['Returns_30d'] = df['Close'].pct_change(periods=30)
    df['Returns_90d'] = df['Close'].pct_change(periods=90)
    
    # Calculate moving averages using vectorized operations with forward fill
    df['SMA_5'] = df['Close'].rolling(window=5, min_periods=1).mean()
    df['SMA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
    df['SMA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
    
    # Calculate price momentum using vectorized operations
    df['Momentum_5'] = df['Close'] / df['Close'].shift(5).fillna(method='ffill') - 1
    df['Momentum_30'] = df['Close'] / df['Close'].shift(30).fillna(method='ffill') - 1
    
    # Calculate volatility using vectorized operations
    df['Volatility_5'] = df['Returns'].rolling(window=5, min_periods=1).std()
    df['Volatility_30'] = df['Returns'].rolling(window=30, min_periods=1).std()
    
    # Add technical indicators
    df = calculate_technical_indicators(df)
    
    # Add recent price levels using vectorized operations
    for i in range(1, 6):
        df[f'lag_{i}'] = df['Close'].shift(i).fillna(method='ffill')
    
    # Add price ranges using vectorized operations
    df['High_Low_Range'] = (df['High'] - df['Low']) / df['Close']
    
    # Add trend indicators using vectorized operations
    df['Trend_30d'] = df['Close'].rolling(window=30, min_periods=1).mean() / df['Close'].rolling(window=30, min_periods=1).mean().shift(30).fillna(method='ffill')
    df['Trend_90d'] = df['Close'].rolling(window=90, min_periods=1).mean() / df['Close'].rolling(window=90, min_periods=1).mean().shift(90).fillna(method='ffill')
    
    # Add cyclical features
    df['Day_of_Week'] = df.index.dayofweek
    df['Month'] = df.index.month
    df['Quarter'] = df.index.quarter
    
    # Add interaction features using vectorized operations
    df['Price_Volume_Interaction'] = df['Close'] * df['Volume']
    df['Volatility_Volume_Interaction'] = df['Volatility_30'] * df['Volume']
    
    # Fill remaining NaN values with appropriate methods
    # For technical indicators, use forward fill
    technical_columns = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Day_of_Week', 'Month', 'Quarter']]
    df[technical_columns] = df[technical_columns].fillna(method='ffill')
    
    # For any remaining NaN values, use backward fill
    df = df.fillna(method='bfill')
    
    # If there are still any NaN values, fill with 0
    df = df.fillna(0)
    
    # Ensure we have enough data
    if len(df) < 200:  # Minimum required data points
        raise ValueError(f"Not enough data points after feature preparation. Need at least 200 data points. Current data points: {len(df)}")
    
    return df

def select_features(X, y, k=20):
    # Select top k features using f_regression
    selector = SelectKBest(f_regression, k=k)
    X_selected = selector.fit_transform(X, y)
    selected_features = X.columns[selector.get_support()].tolist()
    return X_selected, selected_features

def optimize_hyperparameters(model, X_train, y_train):
    # Define parameter grid based on model type with reduced search space
    if isinstance(model, RandomForestRegressor):
        param_grid = {
            'n_estimators': [200, 300],
            'max_depth': [10, 15],
            'min_samples_leaf': [2, 4]
        }
    elif isinstance(model, XGBRegressor):
        param_grid = {
            'n_estimators': [200, 300],
            'max_depth': [4, 6],
            'learning_rate': [0.1, 0.2]
        }
    elif isinstance(model, GradientBoostingRegressor):
        param_grid = {
            'n_estimators': [200, 300],
            'max_depth': [4, 6],
            'learning_rate': [0.1, 0.2]
        }
    else:
        return model  # Return original model if no optimization needed
    
    # Use TimeSeriesSplit with fewer splits
    tscv = TimeSeriesSplit(n_splits=3)
    grid_search = GridSearchCV(model, param_grid, cv=tscv, scoring='neg_mean_squared_error', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    return grid_search.best_estimator_

def predict_fiscal_year(df, model, scaler, features):
    # Use the last 180 days of returns to simulate future returns
    lookback = 180
    last_returns = df['Returns'].dropna().iloc[-lookback:]
    mean_return = last_returns.mean()
    std_return = last_returns.std()
    
    # Start from the last known price
    last_price = df['Close'].iloc[-1]
    future_prices = [last_price]
    np.random.seed(42)
    
    # Optionally, add a small trend based on the last year's average return
    annual_trend = df['Close'].iloc[-365] / df['Close'].iloc[-365] if len(df) > 365 else 1.0
    daily_trend = annual_trend ** (1/365) - 1
    
    for day in range(365):
        # Simulate a daily return
        simulated_return = np.random.normal(mean_return + daily_trend, std_return)
        # Limit extreme returns to +/- 2 std
        simulated_return = np.clip(simulated_return, mean_return - 2*std_return, mean_return + 2*std_return)
        # Calculate next price
        next_price = future_prices[-1] * (1 + simulated_return)
        # Prevent negative or zero prices
        next_price = max(next_price, 1)
        future_prices.append(next_price)
    
    # Remove the initial last_price to return only future predictions
    return future_prices[1:]

def train_single_model(model_name, model, X_train, y_train, X_test, y_test, df):
    print(f"\nTraining {model_name}...")
    
    # Optimize hyperparameters
    optimized_model = optimize_hyperparameters(model, X_train, y_train)
    
    # Train model
    optimized_model.fit(X_train, y_train)
    y_pred = optimized_model.predict(X_test)
    
    # Ensure predictions are positive and within reasonable bounds
    y_pred = np.maximum(y_pred, df['Close'].min() * 0.5)
    y_pred = np.minimum(y_pred, df['Close'].max() * 1.5)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    metrics = {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'R2': r2,
        'MAPE': mape
    }
    
    print(f"{model_name} Performance:")
    print(f"MSE: ${mse:,.2f}")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"MAE: ${mae:,.2f}")
    print(f"R² Score: {r2:.4f}")
    print(f"MAPE: {mape:.2f}%")
    
    return {
        'model': optimized_model,
        'predictions': y_pred,
        'metrics': metrics
    }

@st.cache_data
def train_model_and_predict(df):
    # Prepare features
    features = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
    target = 'Close'
    
    # Ensure we have features
    if not features:
        raise ValueError("No features available for training")
    
    X = df[features].values
    y = df[target].values
    
    # Ensure we have data
    if len(X) == 0 or len(y) == 0:
        raise ValueError("No data available for training")
    
    # Train-test split (no shuffle for time series)
    test_size = 0.2
    split_idx = int(len(df) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Ensure we have training data
    if len(X_train) == 0 or len(y_train) == 0:
        raise ValueError("No training data available after split")
    
    # Scale features using RobustScaler for better handling of outliers
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Feature selection
    X_train_selected, selected_features = select_features(pd.DataFrame(X_train_scaled, columns=features), y_train)
    X_test_selected = pd.DataFrame(X_test_scaled, columns=features)[selected_features].values
    
    # Ensure we have selected features
    if len(selected_features) == 0:
        raise ValueError("No features selected after feature selection")
    
    # Initialize models
    models = {
        'Linear Regression': LinearRegression(positive=True),
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=0.1),
        'SVR': SVR(kernel='rbf', C=1.0, epsilon=0.1),
        'KNN': KNeighborsRegressor(n_neighbors=5, weights='distance'),
        'Random Forest': RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=300, max_depth=6, learning_rate=0.1, random_state=42),
        'Extra Trees': ExtraTreesRegressor(n_estimators=300, max_depth=15, random_state=42)
    }
    
    # Train models in parallel
    n_jobs = max(1, multiprocessing.cpu_count() - 1)  # Leave one CPU free
    model_results = Parallel(n_jobs=n_jobs)(
        delayed(train_single_model)(
            name, model, X_train_selected, y_train, X_test_selected, y_test, df
        ) for name, model in models.items()
    )
    
    # Convert results to dictionary
    model_results = dict(zip(models.keys(), model_results))
    
    # Create ensemble prediction using weighted average based on R² scores
    r2_scores = {name: results['metrics']['R2'] for name, results in model_results.items()}
    positive_r2_scores = {name: max(score, 0) for name, score in r2_scores.items()}
    total_positive_r2 = sum(positive_r2_scores.values())
    weights = {name: score/total_positive_r2 for name, score in positive_r2_scores.items()}
    
    ensemble_pred = np.zeros_like(y_test)
    for name, results in model_results.items():
        ensemble_pred += weights[name] * results['predictions']
    
    # Ensure ensemble predictions are positive and within bounds
    ensemble_pred = np.maximum(ensemble_pred, df['Close'].min() * 0.5)
    ensemble_pred = np.minimum(ensemble_pred, df['Close'].max() * 1.5)
    
    # Calculate ensemble metrics
    ensemble_metrics = {
        'MSE': mean_squared_error(y_test, ensemble_pred),
        'RMSE': np.sqrt(mean_squared_error(y_test, ensemble_pred)),
        'MAE': mean_absolute_error(y_test, ensemble_pred),
        'R2': r2_score(y_test, ensemble_pred),
        'MAPE': np.mean(np.abs((y_test - ensemble_pred) / y_test)) * 100
    }
    
    print("\nEnsemble Model Performance:")
    print(f"MSE: ${ensemble_metrics['MSE']:,.2f}")
    print(f"RMSE: ${ensemble_metrics['RMSE']:,.2f}")
    print(f"MAE: ${ensemble_metrics['MAE']:,.2f}")
    print(f"R² Score: {ensemble_metrics['R2']:.4f}")
    print(f"MAPE: {ensemble_metrics['MAPE']:.2f}%")
    
    # Predict tomorrow's price using weighted average of individual models
    tomorrow_features = df[features].iloc[[-1]].values
    tomorrow_features_scaled = scaler.transform(tomorrow_features)
    tomorrow_features_selected = pd.DataFrame(tomorrow_features_scaled, columns=features)[selected_features].values
    
    tomorrow_pred = 0
    for name, results in model_results.items():
        tomorrow_pred += weights[name] * results['model'].predict(tomorrow_features_selected)[0]
    
    # Ensure tomorrow's prediction is positive and within bounds
    tomorrow_pred = np.maximum(tomorrow_pred, df['Close'].min() * 0.5)
    tomorrow_pred = np.minimum(tomorrow_pred, df['Close'].max() * 1.5)
    
    # Add some noise based on recent volatility
    recent_vol = abs(df['Returns'].iloc[-180:].std())
    noise = np.random.normal(0, recent_vol * abs(tomorrow_pred))
    tomorrow_pred += noise
    
    # Final bounds check for tomorrow's prediction
    lower = df['Close'].iloc[-1] * 0.98
    upper = df['Close'].iloc[-1] * 1.02
    tomorrow_pred = np.clip(tomorrow_pred, lower, upper)
    
    return model_results, scaler, selected_features, tomorrow_pred, y_test, ensemble_pred, ensemble_metrics

def plot_bitcoin_history(df, tomorrow_pred, y_test, y_pred, fiscal_year_preds):
    # Set style and parameters for professional look
    plt.style.use('default')  # Use default style as base
    sns.set_theme(style="whitegrid")  # Apply seaborn theme
    
    # Set custom parameters for professional look
    plt.rcParams.update({
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.linewidth': 1.5,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'grid.linewidth': 0.8,
        'grid.alpha': 0.3,
        'figure.facecolor': '#f8f9fa',
        'axes.facecolor': '#ffffff',
        'axes.grid': True,
        'grid.color': '#cccccc',
        'grid.linestyle': '--',
        'axes.edgecolor': '#333333'
    })
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 15))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.2)
    
    # Define professional color scheme
    colors = {
        'historical': '#1f77b4',  # Deep blue
        'prediction': '#ff7f0e',  # Orange
        'future': '#2ca02c',      # Green
        'tomorrow': '#d62728',    # Red
        'volume': '#9467bd',      # Purple
        'volatility': '#e377c2'   # Pink
    }
    
    # Main price plot
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(df.index, df['Close'], label='Historical Price', color=colors['historical'], 
             linewidth=2, alpha=0.9)
    test_dates = df.index[-len(y_test):]
    ax1.plot(test_dates, y_pred, label='Test Predictions', color=colors['prediction'], 
             linewidth=2, alpha=0.9)
    tomorrow_date = df.index[-1] + timedelta(days=1)
    ax1.scatter(tomorrow_date, tomorrow_pred, color=colors['tomorrow'], s=150, 
                label="Tomorrow's Prediction", zorder=5, marker='*', edgecolor='black', linewidth=1)
    
    ax1.set_title('Bitcoin Price History and Predictions', fontsize=16, pad=15, fontweight='bold')
    ax1.set_ylabel('Price per Bitcoin (USD)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax1.xaxis.set_major_locator(YearLocator())
    ax1.xaxis.set_major_formatter(DateFormatter('%Y'))
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.legend(loc='upper left', frameon=True, fancybox=True, framealpha=0.9, 
              edgecolor='black', shadow=True)
    
    # Last year and future predictions
    ax2 = fig.add_subplot(gs[1, :])
    last_year = df.iloc[-365:]
    last_year_dates = last_year.index
    future_dates = pd.date_range(start=df.index[-1] + timedelta(days=1), periods=365, freq='D')
    ax2.plot(last_year_dates, last_year['Close'], label='Historical Price', color=colors['historical'], 
             linewidth=2, alpha=0.9)
    test_dates_year = test_dates[-365:]
    test_pred_year = y_pred[-365:]
    ax2.plot(test_dates_year, test_pred_year, label='Test Predictions', color=colors['prediction'], 
             linewidth=2, alpha=0.9)
    ax2.plot(future_dates, fiscal_year_preds, label='Future Predictions', color=colors['future'], 
             linewidth=2, alpha=0.9)
    ax2.scatter(tomorrow_date, tomorrow_pred, color=colors['tomorrow'], s=150, 
                label="Tomorrow's Prediction", zorder=5, marker='*', edgecolor='black', linewidth=1)
    
    ax2.set_title('Bitcoin Price - Last Fiscal Year and Future Prediction', fontsize=16, pad=15, fontweight='bold')
    ax2.set_ylabel('Price per Bitcoin (USD)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax2.xaxis.set_major_locator(MonthLocator(interval=2))
    ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.legend(loc='upper left', frameon=True, fancybox=True, framealpha=0.9, 
              edgecolor='black', shadow=True)
    
    # Volume plot
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.bar(df.index, df['Volume'], color=colors['volume'], alpha=0.7, edgecolor='black', linewidth=0.5)
    ax3.set_title('Trading Volume', fontsize=16, pad=15, fontweight='bold')
    ax3.set_ylabel('Volume', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
    
    # Volatility plot
    ax4 = fig.add_subplot(gs[2, 1])
    volatility = df['Returns'].rolling(window=30).std() * np.sqrt(252) * 100
    ax4.plot(df.index, volatility, color=colors['volatility'], linewidth=2)
    ax4.set_title('30-Day Rolling Volatility (Annualized)', fontsize=16, pad=15, fontweight='bold')
    ax4.set_ylabel('Volatility (%)', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')
    
    # Add footer with timestamp
    fig.text(0.99, 0.01, f'Data Source: Yahoo Finance | Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
             fontsize=10, ha='right', va='bottom', alpha=0.7)
    
    # Add a subtle background color to the figure
    fig.patch.set_facecolor('#f8f9fa')
    
    # Ensure everything fits with proper spacing
    fig.tight_layout(rect=[0, 0.03, 1, 0.98])
    
    try:
        plt.show()
    except Exception as e:
        print(f"Warning: Could not display plot: {str(e)}")
        # Save the plot instead
        plt.savefig('bitcoin_prediction.png', dpi=300, bbox_inches='tight')
        print("Plot has been saved as 'bitcoin_prediction.png'")

def get_live_btc_price():
    """Fetch the current Bitcoin price in USD from CoinGecko (real-time)."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["bitcoin"]["usd"])
    except Exception as e:
        print(f"Error fetching live BTC price from CoinGecko: {e}")
        return None

def main(symbol="BTC-USD"):
    try:
        # Get crypto data
        crypto_data = get_crypto_data(symbol)
        
        # Calculate total market value (use BTC supply as default, or fetch dynamically for other coins)
        circulating_supply = 19_500_000 if symbol == "BTC-USD" else 1  # Placeholder for other coins
        total_market_value = crypto_data['Close'].iloc[-1] * circulating_supply
        
        print(f"\n{symbol} Statistics:")
        print(f"Current Price: ${crypto_data['Close'].iloc[-1]:,.2f}")
        print(f"Total Market Value: ${total_market_value:,.2f}")
        print(f"24h High: ${crypto_data['High'].iloc[-1]:,.2f}")
        print(f"24h Low: ${crypto_data['Low'].iloc[-1]:,.2f}")
        print(f"24h Volume: {crypto_data['Volume'].iloc[-1]:,.0f}")
        print(f"Total Data Points: {len(crypto_data)}")
        
        # Prepare features for the model
        prepared_data = prepare_features(crypto_data)
        print(f"Data Points After Feature Preparation: {len(prepared_data)}")
        
        # Train models and get predictions
        model_results, scaler, features, tomorrow_pred, y_test, ensemble_pred, metrics = train_model_and_predict(prepared_data)
        
        print("\nModel Weights in Ensemble:")
        r2_scores = {name: results['metrics']['R2'] for name, results in model_results.items()}
        weights = {name: score/sum(r2_scores.values()) for name, score in r2_scores.items()}
        for name, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            print(f"{name}: {weight:.2%}")
        
        print(f"\nTomorrow's Predicted Price: ${tomorrow_pred:,.2f}")
        print(f"Prediction Range: ${tomorrow_pred * (1 - 2*metrics['RMSE']/tomorrow_pred):,.2f} - ${tomorrow_pred * (1 + 2*metrics['RMSE']/tomorrow_pred):,.2f}")
        print(f"Predicted Market Value: ${tomorrow_pred * circulating_supply:,.2f}")
        
        best_model_name = max(weights.items(), key=lambda x: x[1])[0]
        fiscal_year_preds = predict_fiscal_year(prepared_data, model_results[best_model_name]['model'], scaler, features)
        plot_bitcoin_history(prepared_data, tomorrow_pred, y_test, ensemble_pred, fiscal_year_preds)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC-USD"
    main(symbol) 
    