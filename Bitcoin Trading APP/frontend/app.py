import streamlit as st
import plotly.graph_objects as go
import sys
import os
import pandas as pd
import base64
from PIL import Image
import io

# Configure Streamlit page
st.set_page_config(
    page_title="Cryptocurrency Trading Hub",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.Trading_Platoform_Bitcoin import get_crypto_data, prepare_features, train_model_and_predict, predict_fiscal_year

def get_image_as_base64(image_path):
    """Convert a PNG image to base64 string, fallback to placeholder if missing."""
    if os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            # Resize large images to prevent performance issues
            if img.width > 500 or img.height > 500:
                img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            # Convert to RGB if necessary (for RGBA images)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            img.save(buffered, format="PNG", optimize=True)
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Error converting image {image_path} to base64: {e}")
    
    # Fallback to placeholder
    placeholder_path = os.path.join(os.path.dirname(__file__), "images", "placeholder.png")
    if os.path.exists(placeholder_path):
        try:
            img = Image.open(placeholder_path)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            print(f"Error converting placeholder image to base64: {e}")
    return ""

APP_DIR = os.path.dirname(__file__)
crypto_options = {
    "Bitcoin": {
        "symbol": "BTC-USD",
        "logo": os.path.join(APP_DIR, "images", "bitcoin.svg.png"),
        "description": "Bitcoin is the first decentralized cryptocurrency, created in 2009 by Satoshi Nakamoto.",
        "tagline": "The original digital gold."
    },
    "Ethereum": {
        "symbol": "ETH-USD",
        "logo": os.path.join(APP_DIR, "images", "ethereum.png"),
        "description": "Ethereum is a decentralized platform for smart contracts and dApps.",
        "tagline": "Programmable blockchain for the world."
    },
    "Tether": {
        "symbol": "USDT-USD",
        "logo": os.path.join(APP_DIR, "images", "tether-logo.png"),
        "description": "Tether is a stablecoin pegged to the US Dollar.",
        "tagline": "Stability in a volatile world."
    },
    "BNB": {
        "symbol": "BNB-USD",
        "logo": os.path.join(APP_DIR, "images", "bnb-bnb-logo-png_seeklogo-476074.png"),
        "description": "BNB is the native token of the Binance ecosystem.",
        "tagline": "Fueling the Binance ecosystem."
    },
    "Solana": {
        "symbol": "SOL-USD",
        "logo": os.path.join(APP_DIR, "images", "solana_logo.png"),
        "description": "Solana is a high-performance blockchain supporting builders around the world.",
        "tagline": "Fast, scalable, and decentralized."
    },
    "XRP": {
        "symbol": "XRP-USD",
        "logo": os.path.join(APP_DIR, "images", "ripple-brandlogo.net_.png"),
        "description": "XRP is a digital asset built for global payments.",
        "tagline": "Global payments, instant and cheap."
    },
    "USD Coin": {
        "symbol": "USDC-USD",
        "logo": os.path.join(APP_DIR, "images", "blue-usdc-icon-symbol-logo.png"),
        "description": "USD Coin is a fully-backed US Dollar stablecoin.",
        "tagline": "Digital dollar for the digital age."
    },
    "Cardano": {
        "symbol": "ADA-USD",
        "logo": os.path.join(APP_DIR, "images", "what-is-cardano-ada_cryptocurrency_800x480-compressor.png"),
        "description": "Cardano is a proof-of-stake blockchain platform.",
        "tagline": "Secure and sustainable blockchain."
    },
    "Dogecoin": {
        "symbol": "DOGE-USD",
        "logo": os.path.join(APP_DIR, "images", "dogecoin_logo.png"),
        "description": "Dogecoin is a meme-inspired cryptocurrency.",
        "tagline": "The fun and friendly internet currency."
    },
    "Toncoin": {
        "symbol": "TON11419-USD",
        "logo": os.path.join(APP_DIR, "images", "ton_symbol.png"),
        "description": "Toncoin is the native token of The Open Network (TON).",
        "tagline": "Powering the Open Network."
    },
    "TRON": {
        "symbol": "TRX-USD",
        "logo": os.path.join(APP_DIR, "images", "2fb1bc84c1494178beef0822179d137d.png"),
        "description": "TRON is a blockchain-based decentralized platform.",
        "tagline": "Decentralizing the web."
    },
    "Avalanche": {
        "symbol": "AVAX-USD",
        "logo": os.path.join(APP_DIR, "images", "avalanche_logo_without_text.png"),
        "description": "Avalanche is a high-speed, low-cost blockchain platform.",
        "tagline": "Blazingly fast, low cost, eco-friendly."
    },
    "Shiba Inu": {
        "symbol": "SHIB-USD",
        "logo": os.path.join(APP_DIR, "images", "shiba-inu-logo-512x512.png"),
        "description": "Shiba Inu is a meme coin and decentralized community project.",
        "tagline": "A decentralized meme token."
    },
    "Polkadot": {
        "symbol": "DOT-USD",
        "logo": os.path.join(APP_DIR, "images", "polkadot-logo.png"),
        "description": "Polkadot enables cross-blockchain transfers of any type of data or asset.",
        "tagline": "Connecting the dots of blockchain."
    },
    "Chainlink": {
        "symbol": "LINK-USD",
        "logo": os.path.join(APP_DIR, "images", "chainlink (link)-01.png"),
        "description": "Chainlink is a decentralized oracle network.",
        "tagline": "Bridging smart contracts with real world data."
    },
    "Polygon": {
        "symbol": "MATIC-USD",
        "logo": os.path.join(APP_DIR, "images", "polygon_icon.svg.png"),
        "description": "Polygon is a protocol and framework for building and connecting Ethereum-compatible blockchain networks.",
        "tagline": "Ethereum's internet of blockchains."
    },
    "Litecoin": {
        "symbol": "LTC-USD",
        "logo": os.path.join(APP_DIR, "images", "6825152.png"),
        "description": "Litecoin is a peer-to-peer cryptocurrency and open-source project.",
        "tagline": "Silver to Bitcoin's gold."
    },
    "Bitcoin Cash": {
        "symbol": "BCH-USD",
        "logo": os.path.join(APP_DIR, "images", "bitcoincash.svg.png"),
        "description": "Bitcoin Cash is a peer-to-peer electronic cash system.",
        "tagline": "Fast, reliable, low fees."
    },
    "Internet Computer": {
        "symbol": "ICP-USD",
        "logo": os.path.join(APP_DIR, "images", "630c5fcaf8184351dc5c6ee5.png"),
        "description": "Internet Computer is a blockchain that runs at web speed.",
        "tagline": "The world's first web-speed blockchain."
    },
    "Uniswap": {
        "symbol": "UNI7083-USD",
        "logo": os.path.join(APP_DIR, "images", "uniswap-logo-black.png"),
        "description": "Uniswap is a leading decentralized crypto exchange protocol.",
        "tagline": "Swap, earn, and build on the leading DEX."
    },
    "Dai": {
        "symbol": "DAI-USD",
        "logo": os.path.join(APP_DIR, "images", "1958.png"),
        "description": "Dai is a stablecoin soft-pegged to the US Dollar.",
        "tagline": "A decentralized stablecoin."
    },
    "Ethereum Classic": {
        "symbol": "ETC-USD",
        "logo": os.path.join(APP_DIR, "images", "ethereum_classic-logo.wine.png"),
        "description": "Ethereum Classic is the original Ethereum blockchain.",
        "tagline": "The immutable Ethereum."
    },
    "Stellar": {
        "symbol": "XLM-USD",
        "logo": os.path.join(APP_DIR, "images", "stellar_symbol.png"),
        "description": "Stellar is an open network for storing and moving money.",
        "tagline": "Money that moves like email."
    },
    "Aptos": {
        "symbol": "APT-USD",
        "logo": os.path.join(APP_DIR, "images", "aptos_mark_blk.png"),
        "description": "Aptos is a scalable Layer 1 blockchain.",
        "tagline": "Move fast, stay secure."
    },
    "Cosmos": {
        "symbol": "ATOM-USD",
        "logo": os.path.join(APP_DIR, "images", "cosmos-cryptocurrency-icon-2048x2048-k2k2lftp.png"),
        "description": "Cosmos is an ever-expanding ecosystem of interconnected apps and services.",
        "tagline": "The internet of blockchains."
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
    # Apply global black theme styling
    st.markdown("""
    <style>
    /* Global black background */
    .stApp {
        background-color: #000000;
    }
    
    /* Fix screen fitting */
    .main .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-right: 3rem;
        padding-left: 3rem;
        padding-bottom: 2rem;
    }
    
    /* Remove default Streamlit padding and margins */
    .css-1d391kg, .css-1lcbmhc, .css-1avcm0n {
        padding-top: 0rem;
    }
    
    /* Make full width */
    .css-12oz5g7, .css-12w0qpk {
        max-width: 100%;
    }
    
    /* Ensure responsive layout */
    @media (max-width: 768px) {
        .main .block-container {
            padding-right: 1rem;
            padding-left: 1rem;
        }
    }
    
    /* Style all text elements */
    .stMarkdown, .stText {
        color: #ffffff;
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Main title */
    .main-title {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #b8b8b8;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    
    /* Button styling */
    .stButton > button {
        background: #0052ff;
        color: #ffffff;
        border: none;
        font-weight: 500;
        border-radius: 4px;
        padding: 8px 16px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #0040cc;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Input field styling */
    input[type="text"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(255, 153, 0, 0.1);
    }
    
    [data-testid="metric-container"] > div > div > div > div {
        color: #ffffff !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #b8b8b8;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ff9900;
        background-color: #2a2a2a;
    }
    
    /* Plotly chart dark theme override */
    .js-plotly-plot .plotly .modebar {
        background-color: transparent !important;
    }
    
    /* Section dividers */
    hr {
        border-color: #333333;
        margin: 30px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Professional header with decorative elements
    st.markdown("""
    <div style='width: 100%; margin-bottom: 50px;'>
        <div style='height: 2px; background: linear-gradient(90deg, transparent 0%, #0052ff 50%, transparent 100%); margin-bottom: 30px;'></div>
        <div style='text-align: center; position: relative;'>
            <h1 class="main-title">Cryptocurrency Trading Hub</h1>
            <p class="subtitle">Welcome to the professional cryptocurrency analysis platform</p>
        </div>
        <div style='display: flex; align-items: center; justify-content: center; margin-top: 30px;'>
            <div style='width: 100px; height: 1px; background: #333333;'></div>
            <div style='width: 8px; height: 8px; background: #0052ff; border-radius: 50%; margin: 0 20px;'></div>
            <div style='width: 100px; height: 1px; background: #333333;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Calculate 24h change for all cryptos ---
    crypto_data_list = []
    for crypto_name, crypto_info in crypto_options.items():
        try:
            data = get_crypto_data(crypto_info['symbol'])
            price = data['Close'].iloc[-1]
            price_change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) > 1 else 0
            market_cap = price * 1e9  # Placeholder, you can use your supply dict if you want
            logo_path = crypto_info['logo'] if os.path.exists(crypto_info['logo']) else os.path.join(APP_DIR, "images", "placeholder.png")
            logo_b64 = get_image_as_base64(logo_path)
            crypto_data_list.append({
                'name': crypto_name,
                'symbol': crypto_info['symbol'],
                'logo_b64': logo_b64,
                'price': price,
                'price_change': price_change,
                'market_cap': market_cap,
                'tagline': crypto_info.get('tagline', ''),
            })
        except Exception as e:
            continue

    # --- Top Movers (24h) ---
    top_movers = sorted(crypto_data_list, key=lambda x: abs(x['price_change']), reverse=True)[:5]
    st.markdown('<h2 style="color: #ffffff; font-size: 2.5rem; font-weight: 800; margin-bottom: 30px;">Top movers (24h)</h2>', unsafe_allow_html=True)
    mover_cols = st.columns(5)
    for idx, mover in enumerate(top_movers):
        with mover_cols[idx]:
            color = '#16c784' if mover['price_change'] >= 0 else '#ea3943'
            arrow = '↑' if mover['price_change'] >= 0 else '↓'
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                        border-radius:20px;
                        padding:25px 15px;
                        text-align:center;
                        border: 2px solid {color};
                        box-shadow: 0 0 20px rgba({22 if mover['price_change'] >= 0 else 234}, {199 if mover['price_change'] >= 0 else 57}, {132 if mover['price_change'] >= 0 else 67}, 0.3);
                        transition: all 0.3s;'>
                <img src='data:image/png;base64,{mover['logo_b64']}' style='width:60px;height:60px;border-radius:50%;margin-bottom:12px;
                     object-fit: contain;
                     box-shadow: 0 0 15px rgba(0, 82, 255, 0.3);'>
                <div style='font-weight:800;font-size:1.2rem;color:#ffffff;margin-bottom:5px;'>{mover['name'].upper()}</div>
                <div style='font-size:1.3rem;color:#ffffff;font-weight:700;margin-bottom:5px;'>£{mover['price']:,.2f}</div>
                <div style='color:{color};font-weight:800;font-size:1.3rem;text-shadow: 0 0 10px {color};'>
                    {arrow} {abs(mover['price_change']):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)  # vertical space
            btn_key = f"top_details_{mover['name']}"
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            if st.button("View Details", key=btn_key):
                st.session_state.selected_crypto = mover['name']
                st.session_state.details_loading = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Searchable Table of All Cryptos ---
    st.markdown('<h2 style="color: #ffffff; font-size: 2.5rem; font-weight: 800; margin-top: 50px; margin-bottom: 30px;">Prices (24h)</h2>', unsafe_allow_html=True)
    # Enhanced search bar with modern styling
    st.markdown('''
    <style>
    .search-container {
        background: transparent;
        padding: 0px;
        margin-bottom: 20px;
    }
    .search-bar-flex {
        display: flex;
        align-items: center;
        gap: 15px;
        width: 100%;
    }
    .search-icon {
        width: 20px;
        height: 20px;
        color: #666666;
        flex-shrink: 0;
    }
    .search-bar-flex input[type="text"] {
        width: 100%;
        padding: 12px 15px 12px 40px;
        border-radius: 8px;
        background: #1a1a1a;
        border: 1px solid #333333;
        color: #ffffff;
        font-size: 1rem;
        outline: none;
        transition: all 0.2s;
    }
    .search-bar-flex input[type="text"]:focus {
        border: 1px solid #666666;
    }
    .search-bar-flex input[type="text"]::placeholder {
        color: #666666;
        opacity: 1;
        font-size: 1rem;
    }
    
    /* Table row styling */
    .crypto-row {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border-radius: 15px;
        margin-bottom: 10px;
        padding: 15px;
        border: 1px solid #333333;
        transition: all 0.3s;
    }
    .crypto-row:hover {
        border: 1px solid #ff9900;
        box-shadow: 0 0 15px rgba(255, 153, 0, 0.2);
        transform: translateX(5px);
    }
    </style>
    <div class="search-container">
        <div class="search-bar-flex">
            <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
    ''', unsafe_allow_html=True)
    search = st.text_input("", "", key="crypto_search", placeholder="Filter by name or symbol")
    st.markdown('</div></div>', unsafe_allow_html=True)
    filtered_cryptos = [c for c in crypto_data_list if search.lower() in c['name'].lower() or search.lower() in c['symbol'].lower()]
    # Professional table header
    header_cols = st.columns([0.5, 2.5, 1.5, 1.5, 1.5, 1.5])
    with header_cols[1]:
        st.markdown("<span style='color: #666666; font-size: 0.9rem; font-weight: 500;'>Name</span>", unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown("<span style='color: #666666; font-size: 0.9rem; font-weight: 500;'>Price</span>", unsafe_allow_html=True)
    with header_cols[3]:
        st.markdown("<span style='color: #666666; font-size: 0.9rem; font-weight: 500;'>Change</span>", unsafe_allow_html=True)
    with header_cols[4]:
        st.markdown("<span style='color: #666666; font-size: 0.9rem; font-weight: 500;'>Market cap ↓</span>", unsafe_allow_html=True)
    for c in filtered_cryptos:
        change_color = '#00ff88' if c['price_change'] >= 0 else '#ff3366'
        arrow = '↑' if c['price_change'] >= 0 else '↓'
        
        # Create a container for each row
        cols = st.columns([0.5, 2.5, 1.5, 1.5, 1.5, 1.5])
        with cols[0]:
            st.markdown(f"""
            <div style='text-align:center;'>
                <img src='data:image/png;base64,{c['logo_b64']}' 
                     style='width:45px;height:45px;border-radius:50%;
                            object-fit: contain;
                            box-shadow: 0 0 10px rgba(0, 82, 255, 0.2);'>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""
            <div>
                <span style='font-weight:800;color:#ffffff;font-size:1.1rem;'>{c['name']}</span>
                <span style='font-weight:400;color:#666666;font-size:0.9rem;margin-left:10px;'>{c['symbol']}</span>
            </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<div style='color:#ffffff;font-weight:700;font-size:1.1rem;'>£{c['price']:,.2f}</div>", unsafe_allow_html=True)
        with cols[3]:
            color = '#16c784' if c['price_change'] >= 0 else '#ea3943'
            arrow = '' if abs(c['price_change']) < 0.01 else '↑' if c['price_change'] >= 0 else '↓'
            st.markdown(f"""
            <div style='font-weight:800;color:{color};font-size:1.1rem;
                        text-shadow: 0 0 5px {color}33;'>
                {arrow} {abs(c['price_change']):.2f}%
            </div>
            """, unsafe_allow_html=True)
        with cols[4]:
            st.markdown(f"<div style='color:#ffffff;font-weight:600;font-size:1.1rem;'>£{c['market_cap']/1e9:.1f}B</div>", unsafe_allow_html=True)
        with cols[5]:
            if st.button('View Details', key=f'details_{c["name"]}_row', 
                       help=f"View detailed analysis for {c['name']}"):
                st.session_state.selected_crypto = c['name']
                st.session_state.details_loading = True
                st.rerun()

def show_details():
    # Apply the same black theme styling
    st.markdown("""
    <style>
    /* Global black background */
    .stApp {
        background-color: #000000;
    }
    
    /* Enhanced metric cards for details page */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        border: 2px solid #0052ff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0, 82, 255, 0.2);
    }
    
    /* Back button styling */
    .back-button {
        background: linear-gradient(90deg, #333333, #444444);
        color: #ff9900;
        padding: 12px 24px;
        border-radius: 30px;
        border: 2px solid #ff9900;
        font-weight: 700;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s;
        margin-bottom: 30px;
    }
    
    .back-button:hover {
        background: linear-gradient(90deg, #ff9900, #ff7700);
        color: #000000;
        transform: translateX(-5px);
        box-shadow: 0 5px 15px rgba(255, 153, 0, 0.4);
    }
    
    /* Crypto headers */
    .crypto-header {
        color: #ffffff;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 20px;
    }
    
    /* Section headers */
    .section-header {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 40px 0 20px 0;
    }
    
    /* Plotly charts background */
    .js-plotly-plot .plotly .bg {
        fill: #000000 !important;
    }
    
    /* Enhanced dividers */
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #0052ff, transparent);
        margin: 40px 0;
        border-radius: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    selected_crypto = st.session_state.selected_crypto
    if selected_crypto not in crypto_options:
        st.error("Invalid cryptocurrency selected")
        st.session_state.selected_crypto = None
        st.session_state.details_loading = False
        st.rerun()
        return

    crypto_info = crypto_options[selected_crypto]
    
    # Enhanced back button
    if st.button("← Return to Dashboard", key="back_to_home", help="Go back to the main dashboard"):
        st.session_state.selected_crypto = None
        st.session_state.details_loading = False
        # Clear stored data
        if 'crypto_data' in st.session_state:
            del st.session_state.crypto_data
        if 'prepared_data' in st.session_state:
            del st.session_state.prepared_data
        if 'model_results' in st.session_state:
            del st.session_state.model_results
        st.rerun()
        return

    # Load data if needed
    if st.session_state.get('details_loading', False):
        with st.spinner('Loading data and predictions...'):
            try:
                crypto_data = get_crypto_data(crypto_info['symbol'])
                if crypto_data is None or crypto_data.empty:
                    st.warning("No data returned for this cryptocurrency.")
                    st.session_state.details_loading = False
                    return
                prepared_data = prepare_features(crypto_data)
                if prepared_data is None or prepared_data.empty:
                    st.warning("No prepared data available for this cryptocurrency.")
                    st.session_state.details_loading = False
                    return
                model_results, scaler, features, tomorrow_pred, y_test, ensemble_pred, metrics = train_model_and_predict(prepared_data)
                if model_results is None or scaler is None or features is None or tomorrow_pred is None or y_test is None or ensemble_pred is None or metrics is None:
                    st.warning("Model or prediction results are missing.")
                    st.session_state.details_loading = False
                    return
                
                # Store data in session state
                st.session_state.crypto_data = crypto_data
                st.session_state.prepared_data = prepared_data
                st.session_state.model_results = {
                    'model_results': model_results,
                    'scaler': scaler,
                    'features': features,
                    'tomorrow_pred': tomorrow_pred,
                    'y_test': y_test,
                    'ensemble_pred': ensemble_pred,
                    'metrics': metrics
                }
                st.session_state.details_loading = False
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred while loading the details: {str(e)}")
                st.session_state.details_loading = False
                if st.button("Return to Dashboard", key="return_dashboard_error"):
                    st.session_state.selected_crypto = None
                    st.rerun()
        return

    # Check if data is available
    if 'crypto_data' not in st.session_state or 'prepared_data' not in st.session_state or 'model_results' not in st.session_state:
        st.error("Data not loaded properly. Please try again.")
        if st.button("Return to Dashboard", key="return_dashboard_no_data"):
            st.session_state.selected_crypto = None
            st.rerun()
        return

    # Retrieve data from session state
    crypto_data = st.session_state.crypto_data
    prepared_data = st.session_state.prepared_data
    model_results = st.session_state.model_results['model_results']
    scaler = st.session_state.model_results['scaler']
    features = st.session_state.model_results['features']
    tomorrow_pred = st.session_state.model_results['tomorrow_pred']
    y_test = st.session_state.model_results['y_test']
    ensemble_pred = st.session_state.model_results['ensemble_pred']
    metrics = st.session_state.model_results['metrics']

    # Only render details after loading is done
    # Enhanced crypto header with logo
    logo_b64 = get_image_as_base64(crypto_info['logo'])
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 40px;'>
        <img src='data:image/png;base64,{logo_b64}' 
             style='width: 120px; height: 120px; border-radius: 50%; 
                    object-fit: contain;
                    box-shadow: 0 0 30px rgba(0, 82, 255, 0.5);
                    margin-bottom: 20px;'>
        <h1 class='crypto-header'>{selected_crypto}</h1>
        <div style='display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 15px;'>
            <span style='background: #1a1a1a; padding: 8px 20px; border-radius: 20px; 
                         border: 2px solid #0052ff; color: #ffffff; font-weight: 700;'>
                {crypto_info['symbol']}
            </span>
        </div>
        <p style='color: #b8b8b8; font-size: 1.1rem; max-width: 800px; margin: 0 auto;'>
            {crypto_info['description']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Price Chart ---
    price_ranges = {
        "Last Week": 7,
        "Last Month": 30,
        "6 Months": 182,
        "1 Year": 365,
        "5 Years": 1825,
        "All Time": None
    }
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-header">Live {selected_crypto} Market Data</h2>', unsafe_allow_html=True)
    # Calculate 24h change and market cap
    current_price = crypto_data['Close'].iloc[-1]
    price_change = ((crypto_data['Close'].iloc[-1] - crypto_data['Close'].iloc[-2]) / crypto_data['Close'].iloc[-2]) * 100 if len(crypto_data) > 1 else 0
    # Use realistic supply for each crypto if available, else fallback
    supply_dict = {'BTC-USD': 19500000, 'ETH-USD': 120000000, 'USDT-USD': 110000000000, 'XRP-USD': 55000000000}
    supply = supply_dict.get(crypto_info['symbol'], 100000000)
    market_cap = current_price * supply
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Current Price", f"${current_price:,.4f}")
    with col2:
        st.metric("24h High", f"${crypto_data['High'].iloc[-1]:,.4f}")
    with col3:
        st.metric("24h Low", f"${crypto_data['Low'].iloc[-1]:,.4f}")
    with col4:
        st.metric("24h % Change", f"{price_change:+.2f}%", delta_color="inverse")
    with col5:
        st.metric("Market Cap", f"${market_cap:,.0f}")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-header">{selected_crypto} Price Prediction</h2>', unsafe_allow_html=True)
    st.metric("Tomorrow's Predicted Price", f"${tomorrow_pred:,.4f}")

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

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-header">{selected_crypto} Historical Price Chart</h2>', unsafe_allow_html=True)
    price_range = st.selectbox("Price Chart Time Range", list(price_ranges.keys()), index=4, key="price_range")
    n_price = price_ranges[price_range]
    price_data = prepared_data.tail(n_price) if n_price is not None else prepared_data
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(
        x=price_data.index,
        y=price_data['Close'],
        mode='lines',
        name='Historical Price',
        line=dict(color='#0052ff', width=2)
    ))
    fig_hist.update_layout(
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_dark',
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff', size=14),
        xaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
        yaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1a1a1a', font_size=14, font_family="Arial")
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- Next Year Prediction Chart ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="section-header">{selected_crypto} Next Year Price Prediction</h2>', unsafe_allow_html=True)
    best_model_name = max(model_results.items(), key=lambda x: x[1]['metrics']['R2'])[0]
    fiscal_year_preds = predict_fiscal_year(prepared_data, model_results[best_model_name]['model'], scaler, features)
    future_dates = pd.date_range(start=prepared_data.index[-1] + pd.Timedelta(days=1), periods=365, freq='D')
    fig_future = go.Figure()
    fig_future.add_trace(go.Scatter(
        x=future_dates,
        y=fiscal_year_preds,
        mode='lines',
        name='Next Year Prediction',
        line=dict(color='#16c784', width=2)
    ))
    fig_future.update_layout(
        xaxis_title='Date',
        yaxis_title='Predicted Price ($)',
        template='plotly_dark',
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff', size=14),
        xaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
        yaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1a1a1a', font_size=14, font_family="Arial")
    )
    st.plotly_chart(fig_future, use_container_width=True)

    # --- Detailed Table of Next Year Predictions ---
    detailed_pred_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted Price ($)': fiscal_year_preds
    })
    detailed_pred_df['Percentage Change (%)'] = detailed_pred_df['Predicted Price ($)'].pct_change() * 100
    st.markdown('#### Detailed Table of Next Year Predicted Prices')
    st.dataframe(detailed_pred_df, use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">Technical Indicators</h2>', unsafe_allow_html=True)
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
                line=dict(color='#9f7aea', width=2),
                name='RSI'
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(
                yaxis_title='RSI',
                template='plotly_dark',
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='#000000',
                paper_bgcolor='#000000',
                font=dict(color='#ffffff', size=14),
                xaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
                yaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
                hovermode='x unified',
                hoverlabel=dict(bgcolor='#1a1a1a', font_size=14, font_family="Arial")
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
                line=dict(color='#0052ff', width=2),
                name='MACD'
            ))
            fig_macd.add_trace(go.Scatter(
                x=macd_data.index,
                y=macd_data['MACD_signal'],
                mode='lines',
                line=dict(color='#ea3943', width=2),
                name='Signal'
            ))
            fig_macd.update_layout(
                yaxis_title='MACD',
                template='plotly_dark',
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='#000000',
                paper_bgcolor='#000000',
                font=dict(color='#ffffff', size=14),
                xaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
                yaxis=dict(gridcolor='#333333', showgrid=True, gridwidth=1),
                hovermode='x unified',
                hoverlabel=dict(bgcolor='#1a1a1a', font_size=14, font_family="Arial")
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

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">Statistical Summary</h2>', unsafe_allow_html=True)
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
        st.metric("Average Price", f"${summary_data['Close'].mean():,.4f}")
        st.metric("Median Price", f"${summary_data['Close'].median():,.4f}")
    with col2:
        if 'Volatility_30' in summary_data.columns:
            st.metric("Volatility", f"{summary_data['Volatility_30'].mean():.2f}")
        st.metric(f"High", f"${summary_data['Close'].max():,.4f}")
    with col3:
        st.metric(f"Low", f"${summary_data['Close'].min():,.4f}")
        st.metric("Recent Volume", f"{crypto_data['Volume'].iloc[-1]:,.0f}")

# --- MAIN LOGIC ---
if 'details_loading' not in st.session_state:
    st.session_state.details_loading = False

if st.session_state.selected_crypto is None:
    show_dashboard()
else:
    show_details()
    