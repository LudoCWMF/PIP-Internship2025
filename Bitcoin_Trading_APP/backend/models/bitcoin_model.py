import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import datetime
import requests

class BitcoinPredictor:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.data = None
        
    def fetch_data(self):
        """Fetch Bitcoin data from Yahoo Finance"""
        btc = yf.Ticker("BTC-USD")
        self.data = btc.history(period="max")
        return self.data
    
    def prepare_features(self, df):
        """Prepare features for prediction"""
        df['Returns'] = df['Close'].pct_change()
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        # --- RSI ---
        delta = df['Close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        rs = roll_up / roll_down
        df['RSI'] = 100.0 - (100.0 / (1.0 + rs))
        # --- MACD ---
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df = df.dropna()
        return df
    
    def get_summary_stats(self):
        """Get summary statistics for Bitcoin"""
        if self.data is None:
            self.fetch_data()
            
        current_price = self.data['Close'].iloc[-1]
        high_24h = self.data['High'].iloc[-1]
        low_24h = self.data['Low'].iloc[-1]
        volume_24h = self.data['Volume'].iloc[-1]
        
        # Calculate percentage changes
        change_7d = ((current_price / self.data['Close'].iloc[-7]) - 1) * 100
        change_30d = ((current_price / self.data['Close'].iloc[-30]) - 1) * 100
        ytd = self.data[self.data.index.year == datetime.datetime.now().year]
        change_ytd = ((current_price / ytd['Close'].iloc[0]) - 1) * 100
        
        return {
            'current_price': current_price,
            'high_24h': high_24h,
            'low_24h': low_24h,
            'volume_24h': volume_24h,
            'change_7d': change_7d,
            'change_30d': change_30d,
            'change_ytd': change_ytd,
            'market_cap': current_price * 19_000_000  # Approximate circulating supply
        }
    
    def get_predictions(self):
        """Get price predictions for the next day"""
        if self.data is None:
            self.fetch_data()
            
        # Simple prediction using moving average
        ma5 = self.data['Close'].rolling(window=5).mean().iloc[-1]
        ma20 = self.data['Close'].rolling(window=20).mean().iloc[-1]
        
        # Calculate confidence interval
        std = self.data['Close'].rolling(window=20).std().iloc[-1]
        
        return {
            'predicted_price': ma5,
            'confidence_lower': ma5 - 2*std,
            'confidence_upper': ma5 + 2*std,
            'predicted_market_cap': ma5 * 19_000_000
        }
    
    def get_chart_data(self):
        """Get data for charting"""
        if self.data is None:
            self.fetch_data()
            
        df = self.data.copy()
        df = self.prepare_features(df)
        
        # Convert timezone-aware timestamps to timezone-naive
        df.index = df.index.tz_localize(None)
        
        # Return all necessary columns for the frontend
        return df[['Close', 'MA5', 'MA20', 'Volume', 'Returns', 'Volatility', 'RSI', 'MACD', 'MACD_signal', 'Open', 'High', 'Low']].reset_index()
    
    def get_performance_metrics(self):
        """Calculate model performance metrics"""
        if self.data is None:
            self.fetch_data()
            
        df = self.data.copy()
        df = self.prepare_features(df)
        
        # Simple train-test split
        train_size = int(len(df) * 0.8)
        train_data = df[:train_size]
        test_data = df[train_size:]
        
        # Calculate metrics
        mse = mean_squared_error(test_data['Close'], test_data['MA5'])
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(test_data['Close'], test_data['MA5'])
        r2 = r2_score(test_data['Close'], test_data['MA5'])
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'train_size': len(train_data),
            'test_size': len(test_data)
        }
    
    def get_detailed_predictions(self):
        """Return detailed predictions for test set and future forecast."""
        if self.data is None:
            self.fetch_data()
        df = self.data.copy()
        df = self.prepare_features(df)
        df = df.reset_index()
        # Simple train-test split
        train_size = int(len(df) * 0.8)
        test_data = df.iloc[train_size:].copy()
        # Use MA5 as prediction (for now, matches get_performance_metrics)
        test_data['Predicted'] = test_data['MA5']
        test_data['Absolute Error'] = (test_data['Close'] - test_data['Predicted']).abs()
        test_data['Percentage Error'] = 100 * test_data['Absolute Error'] / test_data['Close']
        detailed = test_data[['Date', 'Close', 'Predicted', 'Absolute Error', 'Percentage Error']].rename(columns={
            'Close': 'Actual Price',
            'Predicted': 'Predicted Price'
        })
        # Future forecast: use last close as base, simulate next 365 days using mean/std of last 180 returns
        lookback = 180
        last_returns = df['Returns'].dropna().iloc[-lookback:]
        mean_return = last_returns.mean()
        std_return = last_returns.std()
        last_price = df['Close'].iloc[-1]
        future_prices = [last_price]
        np.random.seed(42)
        for _ in range(365):
            simulated_return = np.random.normal(mean_return, std_return)
            simulated_return = np.clip(simulated_return, mean_return - 2*std_return, mean_return + 2*std_return)
            next_price = max(future_prices[-1] * (1 + simulated_return), 1)
            future_prices.append(next_price)
        future_dates = pd.date_range(start=df['Date'].iloc[-1] + pd.Timedelta(days=1), periods=365, freq='D')
        future_df = pd.DataFrame({
            'Date': future_dates,
            'Future Price': future_prices[1:]
        })
        return detailed, future_df 
    
    def get_live_market_data(self):
        """Fetch live Bitcoin price, market cap, and volume from CoinGecko API"""
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            market_data = data["market_data"]
            return {
                "current_price": market_data["current_price"]["usd"],
                "market_cap": market_data["market_cap"]["usd"],
                "volume_24h": market_data["total_volume"]["usd"],
                "high_24h": market_data["high_24h"]["usd"],
                "low_24h": market_data["low_24h"]["usd"],
                "circulating_supply": market_data["circulating_supply"],
                "total_supply": market_data["total_supply"]
            }
        except Exception as e:
            print(f"Error fetching live market data: {e}")
            return None 