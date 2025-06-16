import numpy as np
import pandas as pd
import yfinance as yf

# Get Apple stock data
apple = yf.Ticker("AAPL")

# Get historical data for the last 5 years
hist = apple.history(period="5y")

# Find the maximum and minimum prices
max_price = hist['High'].max()
min_price = hist['Low'].min()

# Find the dates for max and min prices
max_date = hist[hist['High'] == max_price].index[0]
min_date = hist[hist['Low'] == min_price].index[0]

print("\nApple Stock Analysis for Trading:")
print("-" * 50)

# Print the minimum price and date (potential buy point)
print(f"\nLowest Price Point (Potential Buy):")
print(f"Date: {min_date.strftime('%Y-%m-%d')}")
print(f"Price: ${min_price:.2f}")

# Print the maximum price and date (potential sell point)
print(f"\nHighest Price Point (Potential Sell):")
print(f"Date: {max_date.strftime('%Y-%m-%d')}")
print(f"Price: ${max_price:.2f}")

# Check if the dates are in the correct order for trading
if min_date < max_date:
    print("\nTrading Strategy:")
    print("✅ Valid trading opportunity: You could have bought at the low and sold at the high")
    print(f"Potential profit per share: ${(max_price - min_price):.2f}")
else:
    print("\nTrading Strategy:")
    print("❌ Invalid trading opportunity: The high price occurred before the low price")
    print("You would need to look for a different trading window")

# Show the price range
print(f"\nPrice Range:")
print(f"Lowest: ${min_price:.2f}")
print(f"Highest: ${max_price:.2f}")
print(f"Total Range: ${(max_price - min_price):.2f}")

# Display the first few rows of the data
print("\nApple Stock History:")
print(hist.head())

# Basic statistics
print("\nBasic Statistics:")
print(hist.describe())

