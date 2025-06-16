import numpy as np
import pandas as pd
import yfinance as yh 
import matplotlib.pyplot as plt

# Define the ticker symbols
sp500_ticker = "^GSPC"  # S&P 500
ftse_ticker = "^FTSE"   # FTSE 100

# Download data for both indices
sp500_data = yh.download(sp500_ticker, start="2020-01-01", end="2024-03-01")
ftse_data = yh.download(ftse_ticker, start="2020-01-01", end="2024-03-01")

# Calculate normalized prices (starting from 100)
sp500_normalized = sp500_data['Close'] / sp500_data['Close'].iloc[0] * 100
ftse_normalized = ftse_data['Close'] / ftse_data['Close'].iloc[0] * 100

# Create the comparison plot
plt.figure(figsize=(12, 6))
plt.plot(sp500_normalized.index, sp500_normalized, label='S&P 500', linewidth=2)
plt.plot(ftse_normalized.index, ftse_normalized, label='FTSE 100', linewidth=2)

plt.title('S&P 500 vs FTSE 100 Performance Comparison (Normalized)')
plt.xlabel('Date')
plt.ylabel('Normalized Price (Starting at 100)')
plt.legend()
plt.grid(True)
plt.show()

# Print some basic statistics
print("\nPerformance Statistics:")
print("\nS&P 500:")
print(f"Total Return: {((sp500_normalized.iloc[-1]/100 - 1) * 100):.2f}%")
print(f"Current Value: {sp500_data['Close'].iloc[-1]:.2f}")

print("\nFTSE 100:")
print(f"Total Return: {((ftse_normalized.iloc[-1]/100 - 1) * 100):.2f}%")
print(f"Current Value: {ftse_data['Close'].iloc[-1]:.2f}")

