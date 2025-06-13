import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np

def get_bitcoin_data():
    # No longer needed for opening/closing, but kept for possible future use
    btc = yf.Ticker("BTC-USD")
    data = btc.history(period="1d")
    return data

def get_predictions():
    # Use the user guesses as the predictions, in the order given
    predictions = [
        ('George', 108430),
        ('Ludo', 106512),
        ('Amber', 110443),
        ('Issy', 108846),
        ('Pip', 107842),
        ('Charles', 107995)
    ]
    return predictions

def plot_comparison():
    # Use the provided opening and closing prices for yesterday
    actual_open = 107529
    actual_close = 105161
    
    # Get predictions (now user guesses)
    predictions = get_predictions()
    names = [name for name, _ in predictions]
    values = [value for _, value in predictions]
    x = range(1, len(predictions) + 1)
    
    # Create the plot
    plt.style.use('default')  # Use default style
    sns.set_theme(style="whitegrid")  # Apply seaborn theme
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot actual prices
    ax.axhline(y=actual_open, color='blue', linestyle='--', label='Opening Price')
    ax.axhline(y=actual_close, color='green', linestyle='--', label='Closing Price')
    
    # Plot predictions (user guesses)
    ax.plot(x, values, 'ro-', label='Predicted Prices (Guesses)')
    
    # Add value labels for predictions with names
    for i, (name, value) in enumerate(predictions):
        ax.annotate(f'{name}: ${value:,.0f}',
                    (i+1, value),
                    textcoords="offset points",
                    xytext=(0,10),
                    ha='center',
                    fontsize=10,
                    color='red',
                    fontweight='bold')
    
    # Customize the plot
    ax.set_title('Bitcoin Price Comparison: Actual vs Predictions (Guesses)', fontsize=14, pad=15)
    ax.set_xlabel('Prediction Number', fontsize=12)
    ax.set_ylabel('Price (USD)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis to show dollar values
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.2f}'))
    
    # Add legend
    ax.legend(loc='upper right')
    
    # Add value labels for actual prices
    ax.annotate(f'Opening: ${actual_open:,.2f}',
                (0.5, actual_open),
                textcoords="offset points",
                xytext=(0,10),
                ha='center')
    ax.annotate(f'Closing: ${actual_close:,.2f}',
                (0.5, actual_close),
                textcoords="offset points",
                xytext=(0,10),
                ha='center')
    
    # Adjust layout and display
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_comparison()
