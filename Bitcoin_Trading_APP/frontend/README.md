# Bitcoin Trading App

A Streamlit-based cryptocurrency trading application that provides real-time data analysis and predictions.

## Deployment Instructions

### Local Development
1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment
1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and main file (app.py)
6. Click "Deploy"

## Project Structure
```
frontend/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .streamlit/        # Streamlit configuration
│   └── config.toml    # Theme and server settings
└── images/           # Application images and icons
```

## Features
- Real-time cryptocurrency price tracking
- Technical analysis and predictions
- Interactive charts and visualizations
- Multiple cryptocurrency support
- Machine learning-based price predictions

## Dependencies
All required packages are listed in `requirements.txt`. The main dependencies include:
- streamlit
- pandas
- numpy
- yfinance
- scikit-learn
- xgboost
- plotly
- matplotlib 