import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from model.output import FinancialModel, Currency, FeeStructure, PerformanceMetrics, CapitalCallSchedule

st.set_page_config(
    page_title="PE/VC Investment Calculator",
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
st.title("📈 PE/VC Investment Calculator")
st.markdown("""
    This app models private equity or venture capital investment performance over time.
    Adjust the parameters in the sidebar to see how they affect your investment returns.
""")

# Sidebar inputs
st.sidebar.header("Investment Parameters")

# Currency selection
currency = st.sidebar.selectbox(
    "Currency",
    options=[c.value for c in Currency],
    index=2  # Default to USD
)

# --- Currency conversion rates ---
currency_rates = {
    'USD': 1.0,
    'GBP': 0.85,
    'EUR': 0.93
}
selected_rate = currency_rates[currency]

# Capital call parameters
st.sidebar.subheader("Capital Call Schedule")
use_capital_calls = st.sidebar.checkbox("Use Capital Calls", value=False)

# Initialize investment variables
initial_investment = 0
total_commitment = 0
investment_period = 3
call_frequency = 'quarterly'

if use_capital_calls:
    total_commitment = st.sidebar.number_input(
        "Total Commitment",
        min_value=1000,
        max_value=10000000,
        value=10000,
        step=1000
    )
    
    investment_period = st.sidebar.number_input(
        "Investment Period (Years)",
        min_value=1,
        max_value=5,
        value=3,
        step=1
    )
    
    call_frequency = st.sidebar.selectbox(
        "Call Frequency",
        options=['quarterly', 'semi-annual', 'annual'],
        index=0
    )
else:
    # Initial investment (single upfront)
    initial_investment = st.sidebar.number_input(
        "Initial Investment",
        min_value=100,
        max_value=1000000,
        value=1000,
        step=100
    )

# Fee structure
st.sidebar.subheader("Fee Structure")
management_fee = st.sidebar.slider(
    "Management Fee (% per year)",
    min_value=0.0,
    max_value=5.0,
    value=2.0,
    step=0.1
) / 100

performance_fee = st.sidebar.slider(
    "Performance Fee / Carry (% of profits above hurdle)",
    min_value=0.0,
    max_value=30.0,
    value=20.0,
    step=0.5
) / 100

hurdle_rate = st.sidebar.slider(
    "Hurdle Rate (%)",
    min_value=0.0,
    max_value=30.0,
    value=8.0,
    step=0.5
) / 100

# Performance metrics
st.sidebar.subheader("Performance Assumptions")
target_irr = st.sidebar.slider(
    "Target IRR (%)",
    min_value=-20.0,
    max_value=50.0,
    value=15.0,
    step=0.5
) / 100

moic = st.sidebar.slider(
    "MOIC (x)",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.1
)

mm = st.sidebar.slider(
    "Money Multiple (MM)",
    min_value=0.5,
    max_value=5.0,
    value=2.5,
    step=0.1
)

tvpi = st.sidebar.slider(
    "TVPI (x)",
    min_value=0.5,
    max_value=5.0,
    value=2.5,
    step=0.1
)

# Create model instance (in USD)
if use_capital_calls:
    capital_call_schedule = CapitalCallSchedule(
        total_commitment=total_commitment / selected_rate,
        investment_period_years=investment_period,
        call_frequency=call_frequency
    )
    model = FinancialModel(
        initial_investment=total_commitment / selected_rate,  # Use total commitment as initial investment
        currency=Currency(currency),
        fee_structure=FeeStructure(
            management_fee=management_fee,
            performance_fee=performance_fee,
            hurdle_rate=hurdle_rate
        ),
        performance_metrics=PerformanceMetrics(
            target_irr=target_irr,
            moic=moic,
            mm=mm,
            tvpi=tvpi
        ),
        capital_call_schedule=capital_call_schedule
    )
else:
    model = FinancialModel(
        initial_investment=initial_investment / selected_rate,
        currency=Currency(currency),
        fee_structure=FeeStructure(
            management_fee=management_fee,
            performance_fee=performance_fee,
            hurdle_rate=hurdle_rate
        ),
        performance_metrics=PerformanceMetrics(
            target_irr=target_irr,
            moic=moic,
            mm=mm,
            tvpi=tvpi
        )
    )

# Get results and convert all monetary columns to selected currency
results = model.results.copy()
for col in ['Gross_Return', 'Net_Return', 'Cumulative_Gross', 'Cumulative_Net']:
    results[col] = results[col] * selected_rate

summary = model.get_summary_metrics()

# Calculate Baseline (No Fees) in USD, then convert
if use_capital_calls:
    baseline_model = FinancialModel(
        initial_investment=total_commitment / selected_rate,
        currency=Currency(currency),
        fee_structure=FeeStructure(
            management_fee=0.0,
            performance_fee=0.0,
            hurdle_rate=hurdle_rate
        ),
        performance_metrics=PerformanceMetrics(
            target_irr=target_irr,
            moic=moic,
            mm=mm,
            tvpi=tvpi
        ),
        capital_call_schedule=CapitalCallSchedule(
            total_commitment=total_commitment / selected_rate,
            investment_period_years=investment_period,
            call_frequency=call_frequency
        )
    )
else:
    baseline_model = FinancialModel(
        initial_investment=initial_investment / selected_rate,
        currency=Currency(currency),
        fee_structure=FeeStructure(
            management_fee=0.0,
            performance_fee=0.0,
            hurdle_rate=hurdle_rate
        ),
        performance_metrics=PerformanceMetrics(
            target_irr=target_irr,
            moic=moic,
            mm=mm,
            tvpi=tvpi
        )
    )
baseline_results = baseline_model.results
baseline_final = baseline_results['Cumulative_Gross'].iloc[-1] * selected_rate

# Live scenario (with fees)
live_final = results['Cumulative_Net'].iloc[-1]

# Difference and impact
difference = live_final - baseline_final
impact_pct = (difference / baseline_final) * 100 if baseline_final != 0 else 0

# Display summary
st.subheader("Live Scenario Projections")
colA, colB, colC = st.columns(3)
colA.metric("Baseline Value (No Fees)", f"{baseline_final:,.2f} {currency}")
colB.metric("Live Scenario Value (With Fees)", f"{live_final:,.2f} {currency}", f"{difference:,.2f} {currency}")
colC.metric("Total Fees Impact (vs. Baseline)", f"{abs(impact_pct):.2f}%")

# Main chart: Performance & Growth Trajectories
st.subheader("Performance & Growth Trajectories Over Time")
fig_growth = go.Figure()
fig_growth.add_trace(go.Scatter(
    x=results['Year'],
    y=results['Cumulative_Gross'],
    name='Gross Return',
    line=dict(color='blue')
))
fig_growth.add_trace(go.Scatter(
    x=results['Year'],
    y=results['Cumulative_Net'],
    name='Net Return',
    line=dict(color='orange')
))
fig_growth.update_layout(
    title='Investment Value Growth Over Time',
    xaxis_title='Year',
    yaxis_title=f'Value ({currency})',
    hovermode='x unified',
    showlegend=True
)

# --- Always show Growth Trajectories chart at the top ---
st.plotly_chart(fig_growth, use_container_width=True)

# --- Tabbed interface for metrics and data ---
tab_irr, tab_moic, tab_mm, tab_tvpi, tab_dpi, tab_data = st.tabs(["IRR", "MOIC", "MM", "TVPI", "DPI", "Detailed Data"])

with tab_irr:
    st.subheader("IRR Over Time")
    fig_irr = go.Figure()
    fig_irr.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Gross_IRR'],
        name='Gross IRR',
        line=dict(color='blue')
    ))
    fig_irr.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Net_IRR'],
        name='Net IRR',
        line=dict(color='orange')
    ))
    fig_irr.update_layout(
        title='IRR Over Time',
        xaxis_title='Year',
        yaxis_title='IRR',
        hovermode='x unified',
        showlegend=True
    )
    st.plotly_chart(fig_irr, use_container_width=True)
    st.markdown("**IRR (Internal Rate of Return):** The annualized effective compounded return rate that makes the net present value of all cash flows (both positive and negative) from an investment equal to zero. It is a common measure of investment performance over time.")

with tab_moic:
    st.subheader("MOIC Over Time")
    fig_moic = go.Figure()
    fig_moic.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Gross_MOIC'],
        name='Gross MOIC',
        line=dict(color='blue')
    ))
    fig_moic.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Net_MOIC'],
        name='Net MOIC',
        line=dict(color='orange')
    ))
    fig_moic.update_layout(
        title='MOIC Over Time',
        xaxis_title='Year',
        yaxis_title='MOIC',
        hovermode='x unified',
        showlegend=True
    )
    st.plotly_chart(fig_moic, use_container_width=True)
    st.markdown("**MOIC (Multiple on Invested Capital):** The ratio of total value (realized and unrealized) to the total amount of capital invested. It shows how many times the original investment has been returned.")

with tab_mm:
    st.subheader("Money Multiple (MM) Over Time")
    fig_mm = go.Figure()
    fig_mm.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Gross_MM'],
        name='Gross MM',
        line=dict(color='blue')
    ))
    fig_mm.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Net_MM'],
        name='Net MM',
        line=dict(color='orange')
    ))
    fig_mm.update_layout(
        title='Money Multiple (MM) Over Time',
        xaxis_title='Year',
        yaxis_title='MM',
        hovermode='x unified',
        showlegend=True
    )
    st.plotly_chart(fig_mm, use_container_width=True)
    st.markdown("**MM (Money Multiple):** The ratio of total distributions plus residual value to the total capital invested. It is a simple measure of how much money has been made on an investment relative to the amount invested.")

with tab_tvpi:
    st.subheader("TVPI Over Time")
    fig_tvpi = go.Figure()
    fig_tvpi.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Gross_TVPI'],
        name='Gross TVPI',
        line=dict(color='blue')
    ))
    fig_tvpi.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Net_TVPI'],
        name='Net TVPI',
        line=dict(color='orange')
    ))
    fig_tvpi.update_layout(
        title='TVPI Over Time',
        xaxis_title='Year',
        yaxis_title='TVPI',
        hovermode='x unified',
        showlegend=True
    )
    st.plotly_chart(fig_tvpi, use_container_width=True)
    st.markdown("**TVPI (Total Value to Paid-In):** The ratio of the current value of remaining holdings plus total distributions to the total capital paid in by investors. It measures the total value generated by an investment relative to the amount invested.")

with tab_dpi:
    st.subheader("DPI Over Time")
    fig_dpi = go.Figure()
    fig_dpi.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Gross_DPI'],
        name='Gross DPI',
        line=dict(color='blue')
    ))
    fig_dpi.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Net_DPI'],
        name='Net DPI',
        line=dict(color='orange')
    ))
    fig_dpi.update_layout(
        title='DPI Over Time',
        xaxis_title='Year',
        yaxis_title='DPI',
        hovermode='x unified',
        showlegend=True
    )
    st.plotly_chart(fig_dpi, use_container_width=True)
    st.markdown("**DPI (Distributed to Paid-In):** The ratio of total distributions to total capital paid in by investors. It measures how much cash or stock has been returned to investors relative to what they invested.")

with tab_data:
    st.subheader("Detailed Data")
    st.dataframe(results)

# Fee Impact Chart
st.subheader("Fee Impact Over Time")
fig_fees = go.Figure()
fig_fees.add_trace(go.Bar(
    x=results['Year'],
    y=results['Management_Fee'],
    name='Management Fee',
    marker_color='lightblue'
))
fig_fees.add_trace(go.Bar(
    x=results['Year'],
    y=results['Performance_Fee'],
    name='Performance Fee',
    marker_color='orange'
))
fig_fees.update_layout(
    title='Fee Impact Over Time',
    xaxis_title='Year',
    yaxis_title=f'Fees ({currency})',
    barmode='stack',
    hovermode='x unified',
    showlegend=True
)
st.plotly_chart(fig_fees, use_container_width=True)

# Summary metrics
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Final Gross Return",
        f"{summary['Final_Gross_Return']:,.2f} {currency}"
    )
    st.metric(
        "Final Net Return",
        f"{summary['Final_Net_Return']:,.2f} {currency}"
    )

with col2:
    st.metric(
        "Total Fees Paid",
        f"{summary['Total_Fees']:,.2f} {currency}"
    )
    st.metric(
        "Management Fee (Total)",
        f"{results['Management_Fee'].sum():,.2f} {currency}"
    )
    st.metric(
        "Performance Fee (Total)",
        f"{results['Performance_Fee'].sum():,.2f} {currency}"
    )
    st.metric(
        "Management Fee Rate",
        f"{management_fee*100:.1f}%"
    )
    st.metric(
        "Performance Fee Rate",
        f"{performance_fee*100:.1f}%"
    )
    st.metric(
        "Hurdle Rate",
        f"{hurdle_rate*100:.1f}%"
    )

with col3:
    st.metric(
        f"Final MOIC",
        f"{summary['Final_Gross_MOIC']:.2f}"
    )
    st.metric(
        f"Final MM",
        f"{summary['Final_Gross_MM']:.2f}"
    )
    st.metric(
        f"Final TVPI",
        f"{summary['Final_Gross_TVPI']:.2f}"
    )
    st.metric(
        f"Final IRR",
        f"{summary['Final_Gross_IRR']*100:.2f}%"
    )
    st.metric(
        f"Final DPI",
        f"{results['Gross_DPI'].iloc[-1]:.2f}"
    )

# Optional: Show raw cash flows
if st.checkbox("Show Raw Cash Flows"):
    st.dataframe(results)

# Add capital call visualization if using capital calls
if use_capital_calls:
    st.subheader("Capital Call Schedule")
    fig_calls = go.Figure()
    
    # Plot called capital
    fig_calls.add_trace(go.Bar(
        x=results['Year'],
        y=results['Called_Capital'],
        name='Called Capital',
        marker_color='lightblue'
    ))
    
    # Plot committed capital
    fig_calls.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Committed_Capital'],
        name='Committed Capital',
        line=dict(color='blue', dash='dash')
    ))
    
    fig_calls.update_layout(
        title='Capital Call Schedule',
        xaxis_title='Year',
        yaxis_title=f'Amount ({currency})',
        barmode='stack',
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig_calls, use_container_width=True) 