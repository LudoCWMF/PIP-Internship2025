import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from model.output import FinancialModel, Currency, FeeStructure, PerformanceMetrics

# Set page config
st.set_page_config(
    page_title="Investment Returns Calculator",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stSlider {
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📈 Investment Returns Calculator")
st.markdown("""
    This app calculates investment returns and fee impact based on your inputs.
    Adjust the parameters in the sidebar to see how they affect your investment returns.
""")

# Sidebar inputs
st.sidebar.header("Investment Parameters")

# Initial investment
initial_investment = st.sidebar.number_input(
    "Initial Investment",
    min_value=100,
    max_value=1000000,
    value=1000,
    step=100
)

# Currency selection
currency = st.sidebar.selectbox(
    "Currency",
    options=[c.value for c in Currency],
    index=2  # Default to USD
)

# Fee structure
st.sidebar.subheader("Fee Structure")
management_fee = st.sidebar.slider(
    "Management Fee (%)",
    min_value=0.0,
    max_value=5.0,
    value=2.0,
    step=0.1
) / 100

performance_fee = st.sidebar.slider(
    "Performance Fee (%)",
    min_value=0.0,
    max_value=30.0,
    value=20.0,
    step=0.5
) / 100

# Performance metrics
st.sidebar.subheader("Performance Assumptions")
irr = st.sidebar.slider(
    "IRR (%)",
    min_value=-20.0,
    max_value=50.0,
    value=15.0,
    step=0.5
) / 100

mm = st.sidebar.slider(
    "Money Multiple (x)",
    min_value=0.5,
    max_value=5.0,
    value=2.5,
    step=0.1
)

dpi = st.sidebar.slider(
    "DPI (%)",
    min_value=0.0,
    max_value=100.0,
    value=80.0,
    step=5.0
) / 100

moic = st.sidebar.slider(
    "MOIC (x)",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.1
)

tvpi = st.sidebar.slider(
    "TVPI (x)",
    min_value=0.5,
    max_value=5.0,
    value=2.5,
    step=0.1
)

# Create model instance
model = FinancialModel(
    initial_investment=initial_investment,
    currency=Currency(currency),
    fee_structure=FeeStructure(
        management_fee=management_fee,
        performance_fee=performance_fee
    ),
    performance_metrics=PerformanceMetrics(
        irr=irr,
        mm=mm,
        dpi=dpi,
        moic=moic,
        tvpi=tvpi
    )
)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Investment Growth Over Time")
    
    # Create Plotly figure for investment growth
    fig = go.Figure()
    
    # Add gross and net return lines
    fig.add_trace(go.Scatter(
        x=model.results['Year'],
        y=model.results['Gross_Return'],
        name='Gross Return',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=model.results['Year'],
        y=model.results['Net_Return'],
        name='Net Return',
        line=dict(color='green')
    ))
    
    fig.update_layout(
        title='Investment Growth Over Time',
        xaxis_title='Year',
        yaxis_title=f'Value ({currency})',
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Fee Impact Over Time")
    
    # Create Plotly figure for fees
    fig = go.Figure()
    
    # Add stacked bar chart for fees
    fig.add_trace(go.Bar(
        x=model.results['Year'],
        y=model.results['Management_Fee'],
        name='Management Fee',
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        x=model.results['Year'],
        y=model.results['Performance_Fee'],
        name='Performance Fee',
        marker_color='lightgreen'
    ))
    
    fig.update_layout(
        title='Fee Impact Over Time',
        xaxis_title='Year',
        yaxis_title=f'Fees ({currency})',
        barmode='stack',
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Key metrics display
st.subheader("Key Performance Metrics")

# Create three columns for metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Final Gross Return",
        f"{model.results['Gross_Return'].iloc[-1]:,.2f} {currency}"
    )
    st.metric(
        "Final Net Return",
        f"{model.results['Net_Return'].iloc[-1]:,.2f} {currency}"
    )

with col2:
    st.metric(
        "Total Fees Paid",
        f"{model.results['Management_Fee'].sum() + model.results['Performance_Fee'].sum():,.2f} {currency}"
    )
    st.metric(
        "Net Multiple",
        f"{model.results['Net_Return'].iloc[-1]/initial_investment:.2f}x"
    )

with col3:
    st.metric(
        "Management Fee Impact",
        f"{(model.results['Management_Fee'].sum() / model.results['Gross_Return'].iloc[-1] * 100):.1f}%"
    )
    st.metric(
        "Performance Fee Impact",
        f"{(model.results['Performance_Fee'].sum() / model.results['Gross_Return'].iloc[-1] * 100):.1f}%"
    )

# Comparison chart
st.subheader("Gross vs Net Returns Comparison")

# Create comparison chart
fig = go.Figure()

# Add bars for gross and net metrics
metrics = ['TVPI', 'MOIC', 'MM']
gross_values = [model.performance_metrics.tvpi, model.performance_metrics.moic, model.performance_metrics.mm]
net_values = [
    model.results['Net_Return'].iloc[-1]/initial_investment,
    model.results['Net_Return'].iloc[-1]/initial_investment,
    model.results['Net_Return'].iloc[-1]/initial_investment
]

fig.add_trace(go.Bar(
    name='Gross',
    x=metrics,
    y=gross_values,
    marker_color='blue'
))

fig.add_trace(go.Bar(
    name='Net',
    x=metrics,
    y=net_values,
    marker_color='green'
))

fig.update_layout(
    title='Gross vs Net Returns Comparison',
    xaxis_title='Metric',
    yaxis_title='Multiple',
    barmode='group',
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True) 