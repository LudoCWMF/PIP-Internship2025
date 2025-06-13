import streamlit as st

st.set_page_config(page_title="Test App", page_icon="🧪", layout="wide")

st.title("Streamlit Test App")
st.write("If you can see this, Streamlit is working correctly!")

# Simple test widgets
st.header("Testing Basic Widgets")
name = st.text_input("Enter your name", "Test User")
st.write(f"Hello, {name}!")

# Test metric
st.metric("Test Metric", "123.45", "+10%")

# Success message
st.success("✅ Streamlit is running successfully!")

# Check if we can import the backend
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    
    from backend.Trading_Platoform_Bitcoin import get_crypto_data
    st.success("✅ Backend module imported successfully!")
    
    # Try to fetch a small amount of data
    with st.spinner("Testing data fetch for Bitcoin..."):
        data = get_crypto_data("BTC-USD")
        if data is not None and not data.empty:
            st.success(f"✅ Successfully fetched {len(data)} days of Bitcoin data!")
            st.write(f"Latest price: ${data['Close'].iloc[-1]:,.2f}")
        else:
            st.error("❌ No data returned")
except Exception as e:
    st.error(f"❌ Error importing backend or fetching data: {str(e)}")

st.info("If all checks pass, the main app should work. The issue might be with loading data for 25 cryptocurrencies at once.") 