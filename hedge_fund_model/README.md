# Hedge Fund Performance Model

This Streamlit application models and compares hedge fund investment performance over time, showing the impact of various fees on returns.

## Features

- Model investment growth with and without hedge fund fees
- Compare gross vs. net returns
- Analyze fee impact (management and performance fees)
- Support for high-water mark and hurdle rate
- Optional volatility simulation
- Multiple currency support (USD, EUR, GBP)
- Interactive charts and metrics
- Detailed fee breakdown by year
- Automatic browser launch

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

You can run the application in two ways:

1. Using the launcher script (recommended):
```bash
python launch.py
```

2. Directly with Streamlit:
```bash
streamlit run app.py
```

Both methods will automatically open the application in your default web browser.

## Usage

1. Use the sidebar to configure your investment parameters:
   - Initial investment amount
   - Currency selection
   - Expected annual return
   - Optional volatility
   - Fee structure (management and performance fees)
   - Hurdle rate and high-water mark settings
   - Investment period

2. View the interactive charts and metrics:
   - Growth of investment over time
   - Fee breakdown by year
   - Key performance metrics (IRR, total fees, etc.)

3. Toggle the "Show raw data table" checkbox to view detailed year-by-year results.

## Notes

- The model assumes annual compounding
- Management fees are calculated on the net asset value
- Performance fees are calculated on gains above the hurdle rate (if set)
- High-water mark ensures performance fees are only paid on new gains above the previous peak
- Volatility simulation uses a normal distribution of returns 