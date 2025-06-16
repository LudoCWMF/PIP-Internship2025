import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Fetch Apple's historical data
apple = yf.Ticker("AAPL")
hist = apple.history(period="10y")  # Get 10 years of daily data

# Calculate daily returns
daily_returns = hist['Close'].pct_change().dropna()

# Calculate volatility (standard deviation of returns)
volatility = daily_returns.std()

# Annualize the volatility (multiply by square root of trading days)
annualized_volatility = volatility * np.sqrt(252)  # 252 trading days in a year

# Fetch S&P 500 data for market comparison
sp500 = yf.Ticker("^GSPC")
sp500_hist = sp500.history(period="10y")
sp500_returns = sp500_hist['Close'].pct_change().dropna()
sp500_volatility = sp500_returns.std() * np.sqrt(252)

def interpret_volatility(vol):
    if vol < 0.15:  # Less than 15% annualized volatility
        return "Low"
    elif vol < 0.25:  # Between 15% and 25% annualized volatility
        return "Moderate"
    else:  # Greater than 25% annualized volatility
        return "High"

volatility_level = interpret_volatility(annualized_volatility)

print(f"Apple's Daily Volatility: {volatility:.4f}")
print(f"Apple's Annualized Volatility: {annualized_volatility:.4f}")
print(f"\nVolatility Level: {volatility_level}")
print(f"Context: This indicates {volatility_level.lower()} volatility for Apple's stock.")

print(f"\nMarket Comparison:")
print(f"S&P 500 Annualized Volatility: {sp500_volatility:.4f}")
print(f"Volatility Difference (Apple vs S&P 500): {annualized_volatility - sp500_volatility:.4f}")

if annualized_volatility > sp500_volatility:
    print("Apple's stock is more volatile than the market average")
else:
    print("Apple's stock is less volatile than the market average")

# Calculate cumulative returns
apple_cumulative = (1 + daily_returns).cumprod() - 1
sp500_cumulative = (1 + sp500_returns).cumprod() - 1

# Create separate figures for each plot
plt.figure(figsize=(15, 6))
plt.plot(daily_returns.index, daily_returns, label='Apple Daily Returns', alpha=0.7)
plt.plot(sp500_returns.index, sp500_returns, label='S&P 500 Daily Returns', alpha=0.7)
plt.title('Daily Returns: Apple vs S&P 500 (10 Years)', pad=20)
plt.xlabel('Date', labelpad=10)
plt.ylabel('Daily Returns', labelpad=10)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

plt.figure(figsize=(15, 6))
plt.plot(apple_cumulative.index, apple_cumulative * 100, label='Apple Cumulative Returns', linewidth=2)
plt.plot(sp500_cumulative.index, sp500_cumulative * 100, label='S&P 500 Cumulative Returns', linewidth=2)
plt.title('Cumulative Returns Over Time (10 Years)', pad=20)
plt.xlabel('Date', labelpad=10)
plt.ylabel('Cumulative Returns (%)', labelpad=10)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print final returns
print(f"\nTotal Return Analysis (10 Years):")
print(f"Apple Total Return: {apple_cumulative.iloc[-1]*100:.2f}%")
print(f"S&P 500 Total Return: {sp500_cumulative.iloc[-1]*100:.2f}%")

# Calculate annualized returns
years = 10
apple_annualized = (1 + apple_cumulative.iloc[-1]) ** (1/years) - 1
sp500_annualized = (1 + sp500_cumulative.iloc[-1]) ** (1/years) - 1

print(f"\nAnnualized Returns:")
print(f"Apple Annualized Return: {apple_annualized*100:.2f}%")
print(f"S&P 500 Annualized Return: {sp500_annualized*100:.2f}%")

