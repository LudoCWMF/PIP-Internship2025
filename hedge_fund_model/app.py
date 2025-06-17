import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import threading
import time
import os
import numpy_financial as npf

# Set page config FIRST
st.set_page_config(
    page_title="Hedge Fund Performance Model",
    page_icon="📈",
    layout="wide"
)

# Set black background using custom CSS
st.markdown(
    """
    <style>
    body, .stApp, .st-cq, .st-cx, .st-cy, .st-cz, .st-da, .st-db, .st-dc, .st-dd, .st-de, .st-df, .st-dg, .st-dh, .st-di, .st-dj, .st-dk, .st-dl, .st-dm, .st-dn, .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt, .st-du, .st-dv, .st-dw, .st-dx, .st-dy, .st-dz {
        background-color: #000000 !important;
    }
    .stApp {
        background-color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def open_browser():
    """Open the browser after a short delay to ensure Streamlit has started."""
    if not os.environ.get('BROWSER_OPENED'):
        time.sleep(1.5)  # Wait for Streamlit to start
        webbrowser.open('http://localhost:8501')
        os.environ['BROWSER_OPENED'] = '1'

# Start the browser in a separate thread only if it hasn't been opened yet
if not os.environ.get('BROWSER_OPENED'):
    threading.Thread(target=open_browser, daemon=True).start()

# Add a clean, professional divider function
def section_divider():
    st.markdown(
        """
        <hr style="border: none; height: 2px; background: linear-gradient(90deg, rgba(0,212,255,0.7) 0%, rgba(255,255,255,0.3) 100%); box-shadow: 0 0 6px #00c3ff55; margin: 32px 0 32px 0;" />
        """,
        unsafe_allow_html=True
    )

# Title and description
st.title("Hedge Fund Performance Model")
st.markdown("""
This app models and compares hedge fund investment performance over time, 
showing the impact of various fees on returns.
""")

# Divider below the heading
section_divider()

# Sidebar inputs
st.sidebar.header("Investment Parameters")

# Currency selection
currency = st.sidebar.selectbox(
    "Currency",
    ["USD", "EUR", "GBP"],
    index=0
)

# Initial investment
initial_investment = st.sidebar.number_input(
    f"Initial Investment ({currency})",
    min_value=100,
    value=1000,
    step=100
)

# Annual return rate
annual_return = st.sidebar.number_input(
    "Annual Return Rate (%)",
    min_value=-50.0,
    max_value=100.0,
    value=10.0,
    step=0.1
)

# Volatility
use_volatility = st.sidebar.checkbox("Include Volatility", value=False)
volatility = 0
if use_volatility:
    volatility = st.sidebar.number_input(
        "Volatility (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=0.1
    )

# Investment period
years = st.sidebar.number_input(
    "Investment Period (years)",
    min_value=1,
    max_value=50,
    value=10,
    step=1
)

# High-Water Mark (shared by both fee structures)
high_water_mark = st.sidebar.checkbox("Apply High-Water Mark", value=False)

# Hurdle Rate (shared by both fee structures)
hurdle_rate = st.sidebar.number_input(
    "Hurdle Rate (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=0.1
)

# --- Sidebar inputs for fee structure comparison ---
st.sidebar.markdown("---")
st.sidebar.header("Fee Structure Comparison")

st.sidebar.markdown("**Fee Structure 1**")
user1_mgmt = st.sidebar.number_input("Management Fee 1 (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1, key='mgmt1')
user1_perf = st.sidebar.number_input("Performance Fee 1 (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key='perf1')

st.sidebar.markdown("**Fee Structure 2**")
user2_mgmt = st.sidebar.number_input("Management Fee 2 (%)", min_value=0.0, max_value=10.0, value=1.5, step=0.1, key='mgmt2')
user2_perf = st.sidebar.number_input("Performance Fee 2 (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0, key='perf2')

def calculate_portfolio_values(initial_investment, annual_return, volatility, years,
                             management_fee, performance_fee, hurdle_rate, high_water_mark):
    # Initialize arrays
    years_array = np.arange(years + 1)
    gross_values = np.zeros(years + 1)
    net_values = np.zeros(years + 1)
    management_fees = np.zeros(years + 1)
    performance_fees = np.zeros(years + 1)
    
    # Set initial values
    gross_values[0] = initial_investment
    net_values[0] = initial_investment
    high_water = initial_investment
    
    # Calculate values for each year
    for year in range(1, years + 1):
        # Calculate gross return with volatility if enabled
        if use_volatility:
            random_return = np.random.normal(annual_return, volatility)
            gross_return = 1 + (random_return / 100)
        else:
            gross_return = 1 + (annual_return / 100)
        
        # Calculate gross value
        gross_values[year] = gross_values[year-1] * gross_return
        
        # Calculate management fee
        management_fee_amount = net_values[year-1] * (management_fee / 100)
        management_fees[year] = management_fee_amount
        
        # Calculate net value before performance fee
        net_before_perf = gross_values[year] - management_fee_amount
        
        # Calculate performance fee
        if high_water_mark:
            performance_fee_base = max(0, net_before_perf - high_water)
        else:
            performance_fee_base = max(0, net_before_perf - net_values[year-1])
        
        if performance_fee_base > 0 and (net_before_perf - net_values[year-1]) > (hurdle_rate / 100 * net_values[year-1]):
            performance_fee_amount = performance_fee_base * (performance_fee / 100)
        else:
            performance_fee_amount = 0
            
        performance_fees[year] = performance_fee_amount
        
        # Calculate final net value
        net_values[year] = net_before_perf - performance_fee_amount
        
        # Update high water mark
        if high_water_mark:
            high_water = max(high_water, net_values[year])
    
    return years_array, gross_values, net_values, management_fees, performance_fees

def calculate_scenario(initial_investment, return_rate, volatility, years,
                      management_fee, performance_fee, hurdle_rate, high_water_mark):
    """Calculate a single scenario with given parameters."""
    _, _, net_values, _, _ = calculate_portfolio_values(
        initial_investment, return_rate, volatility, years,
        management_fee, performance_fee, hurdle_rate, high_water_mark
    )
    return net_values[-1]

# Calculate portfolio values for main outputs using Fee Structure 1
# Gross (no fees)
years_array, gross_values, _, _, _ = calculate_portfolio_values(
    initial_investment, annual_return, volatility, years,
    0, 0, hurdle_rate, high_water_mark
)
# Net (Fee Structure 1)
_, _, net_values, management_fees, performance_fees = calculate_portfolio_values(
    initial_investment, annual_return, volatility, years,
    user1_mgmt, user1_perf, hurdle_rate, high_water_mark
)

# Create DataFrame for results
results_df = pd.DataFrame({
    'Year': years_array,
    'Gross Value': gross_values,
    'Net Value': net_values,
    'Management Fees': management_fees,
    'Performance Fees': performance_fees
})

# Calculate metrics for summary (Fee Structure 1)
gross_irr = (gross_values[-1] / initial_investment) ** (1/years) - 1
net_irr = (net_values[-1] / initial_investment) ** (1/years) - 1
total_management_fees = sum(management_fees)
total_performance_fees = sum(performance_fees)
total_fees = total_management_fees + total_performance_fees

gross_mm = gross_values[-1] / initial_investment
net_mm = net_values[-1] / initial_investment

# Calculate Baseline (No Fees) scenario
_, gross_values_baseline, _, _, _ = calculate_portfolio_values(
    initial_investment, annual_return, volatility, years,
    management_fee=0, performance_fee=0, hurdle_rate=0, high_water_mark=False
)
baseline_final = gross_values_baseline[-1]
live_final = net_values[-1]
fees_impact_pct = (baseline_final - live_final) / baseline_final * 100 if baseline_final > 0 else 0

# --- Create all figures before using them in the layout ---

# Performance & Growth Trajectories (fig1)
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=years_array,
    y=gross_values,
    name='Gross Portfolio Value',
    line=dict(color='#0066FF', width=2)  # Blue
))
fig1.add_trace(go.Scatter(
    x=years_array,
    y=net_values,
    name='Net Portfolio Value',
    line=dict(color='#FF2222', width=2)  # Red
))

fig1.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title='Growth of Investment Over Time',
    xaxis_title='Year',
    yaxis_title=f'Portfolio Value ({currency})',
    hovermode='x unified',
    showlegend=True
)

# Fee Breakdown Chart (fig2)
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=years_array[1:],
    y=management_fees[1:],
    name='Management Fees',
    marker_color='blue'
))
fig2.add_trace(go.Bar(
    x=years_array[1:],
    y=performance_fees[1:],
    name='Performance Fees',
    marker_color='red'
))

fig2.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title='Fee Breakdown by Year',
    xaxis_title='Year',
    yaxis_title=f'Fees ({currency})',
    barmode='stack',
    hovermode='x unified',
    showlegend=True
)

# IRR and MOIC Over Time Figures
irr_gross = []
irr_net = []
moic_gross = []
moic_net = []
for i in range(1, years + 1):
    irr_gross.append((gross_values[i] / initial_investment) ** (1/i) - 1)
    irr_net.append((net_values[i] / initial_investment) ** (1/i) - 1)
    moic_gross.append(gross_values[i] / initial_investment)
    moic_net.append(net_values[i] / initial_investment)

fig_irr = go.Figure()
fig_irr.add_trace(go.Scatter(x=years_array[1:], y=irr_gross, name="Gross IRR", line=dict(color='#0066FF', width=2)))
fig_irr.add_trace(go.Scatter(x=years_array[1:], y=irr_net, name="Net IRR", line=dict(color='#FF2222', width=2)))

fig_irr.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title="Annualized Return Over Time",
    xaxis_title="Year",
    yaxis_title="Annualized Return (decimal)",
    hovermode='x unified',
    showlegend=True
)

fig_moic = go.Figure()
fig_moic.add_trace(go.Scatter(x=years_array[1:], y=moic_gross, name="Gross MOIC", line=dict(color='#0066FF', width=2)))
fig_moic.add_trace(go.Scatter(x=years_array[1:], y=moic_net, name="Net MOIC", line=dict(color='#FF2222', width=2)))

fig_moic.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title="MOIC Over Time",
    xaxis_title="Year",
    yaxis_title="MOIC (x)",
    hovermode='x unified',
    showlegend=True
)

# --- True IRR (Cash Flow IRR) Over Time ---
true_irr_gross = []
true_irr_net = []
for i in range(1, years + 1):
    # Gross IRR: cash flows are -initial_investment at t=0, 0 for years 1..i-1, gross_values[i] at year i
    gross_cf = [-initial_investment] + [0]*(i-1) + [gross_values[i]]
    net_cf = [-initial_investment] + [0]*(i-1) + [net_values[i]]
    try:
        gross_irr_val = npf.irr(gross_cf)
    except Exception:
        gross_irr_val = np.nan
    try:
        net_irr_val = npf.irr(net_cf)
    except Exception:
        net_irr_val = np.nan
    true_irr_gross.append(gross_irr_val)
    true_irr_net.append(net_irr_val)

fig_true_irr = go.Figure()
fig_true_irr.add_trace(go.Scatter(x=years_array[1:], y=true_irr_gross, name="Gross IRR (True)", line=dict(color='#0066FF', width=2)))
fig_true_irr.add_trace(go.Scatter(x=years_array[1:], y=true_irr_net, name="Net IRR (True)", line=dict(color='#FF2222', width=2)))

fig_true_irr.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title="True IRR (Cash Flow IRR) Over Time",
    xaxis_title="Year",
    yaxis_title="IRR (decimal)",
    hovermode='x unified',
    showlegend=True
)

# --- Live Scenario Projections Section (TOP) ---
st.markdown("## Live Scenario Projections")
colA, colB, colC = st.columns(3)

with colA:
    st.metric("Baseline Value (No Fees)", f"{baseline_final:,.2f} {currency}")
with colB:
    st.metric(
        "Live Scenario Value (With Fees)",
        f"{live_final:,.2f} {currency}",
        delta=f"{live_final-baseline_final:,.2f} {currency}",
        delta_color="inverse"
    )
with colC:
    st.metric(
        "Total Fees Impact (vs. Baseline)",
        f"{fees_impact_pct:.2f}%",
        delta=None
    )

st.caption("""
These projections show your investment's final value with and without fees, and the total impact of fees as a percentage of the baseline (no-fee) scenario. Adjust parameters in the sidebar to see live updates.
""")

# Divider below Live Scenario Projections
section_divider()

# --- Performance & Growth Trajectories Section ---
st.markdown("## Performance & Growth Trajectories Over Time")
st.plotly_chart(fig1, use_container_width=True, key='growth_chart')
st.markdown("This chart compares how the investment grows with and without hedge fund fees over time. Net returns reflect the deduction of annual management and performance fees.")

section_divider()

# --- Tabbed Metrics Section (IRR, MOIC, Detailed Data) ---
st.markdown("## Key Performance Metrics")
tabs = st.tabs(["IRR", "MOIC", "Detailed Data"])

tab_names = ["IRR", "MOIC", "Detailed Data"]
for i, tab in enumerate(tabs):
    with tab:
        if tab_names[i] == "IRR":
            st.subheader("True IRR (Cash Flow IRR) Over Time")
            st.plotly_chart(fig_true_irr, use_container_width=True, key='true_irr_chart_tab')
            st.info("This is the true IRR (Internal Rate of Return) calculated from cash flows, as used in hedge fund and private equity reporting. For a single lump-sum investment, this matches CAGR, but for more complex cash flows, it will differ.")
        elif tab_names[i] == "MOIC":
            st.subheader("MOIC Over Time")
            st.plotly_chart(fig_moic, use_container_width=True, key='moic_chart_tab')
            st.info("Gross and Net MOIC (Multiple of Money) over time. MOIC is the ratio of current value to initial investment.")
        elif tab_names[i] == "Detailed Data":
            st.subheader("Detailed Year-by-Year Data")
            st.dataframe(results_df.style.format({
                'Gross Value': '{:,.2f}',
                'Net Value': '{:,.2f}',
                'Management Fees': '{:,.2f}',
                'Performance Fees': '{:,.2f}'
            }))
            st.info("This table shows the detailed results for each year, including gross/net values and fees paid.")

section_divider()

# --- Returns Comparison Calculation ---
def calc_net_curve(mgmt_fee, perf_fee):
    _, _, net_curve, _, _ = calculate_portfolio_values(
        initial_investment, annual_return, volatility, years,
        mgmt_fee, perf_fee, hurdle_rate, high_water_mark
    )
    return net_curve

net_no_fee = calc_net_curve(0, 0)
net_user1 = calc_net_curve(user1_mgmt, user1_perf)
net_user2 = calc_net_curve(user2_mgmt, user2_perf)

# --- Returns Comparison Chart ---
section_divider()
st.markdown("## Net Returns Comparison: Different Fee Structures")
fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(
    x=years_array,
    y=net_no_fee,
    name="No Fees",
    line=dict(color="#0066FF", width=2)
))
fig_compare.add_trace(go.Scatter(
    x=years_array,
    y=net_user1,
    name=f"{user1_mgmt:.2f}% / {user1_perf:.2f}%",
    line=dict(color="#FF2222", width=2)
))
fig_compare.add_trace(go.Scatter(
    x=years_array,
    y=net_user2,
    name=f"{user2_mgmt:.2f}% / {user2_perf:.2f}%",
    line=dict(color="#00CC44", width=2)
))
fig_compare.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title="Net Portfolio Value Over Time: Fee Structure Comparison",
    xaxis_title="Year",
    yaxis_title=f"Net Portfolio Value ({currency})",
    hovermode='x unified',
    showlegend=True
)
st.plotly_chart(fig_compare, use_container_width=True, key='compare_chart')
st.markdown("""
This chart compares the net portfolio value over time for three fee structures: No Fees, and two user-defined fee structures. Adjust the sidebar to see the impact of different fee levels on your investment returns.
""")
section_divider()

# --- Calculate annual fees for both user-defined fee structures ---
_, _, _, mgmt_fees_1, perf_fees_1 = calculate_portfolio_values(
    initial_investment, annual_return, volatility, years,
    user1_mgmt, user1_perf, hurdle_rate, high_water_mark
)
_, _, _, mgmt_fees_2, perf_fees_2 = calculate_portfolio_values(
    initial_investment, annual_return, volatility, years,
    user2_mgmt, user2_perf, hurdle_rate, high_water_mark
)

# --- Fees Section ---
st.markdown("## Fee Breakdown (Comparison)")
fig_fees_compare = go.Figure()
fig_fees_compare.add_trace(go.Bar(
    x=years_array[1:],
    y=mgmt_fees_1[1:],
    name=f"Mgmt Fee 1 ({user1_mgmt:.2f}%)",
    marker_color="#0066FF",
    offsetgroup=0
))
fig_fees_compare.add_trace(go.Bar(
    x=years_array[1:],
    y=perf_fees_1[1:],
    name=f"Perf Fee 1 ({user1_perf:.2f}%)",
    marker_color="#FF2222",
    offsetgroup=1
))
fig_fees_compare.add_trace(go.Bar(
    x=years_array[1:],
    y=mgmt_fees_2[1:],
    name=f"Mgmt Fee 2 ({user2_mgmt:.2f}%)",
    marker_color="#00CC44",
    offsetgroup=2
))
fig_fees_compare.add_trace(go.Bar(
    x=years_array[1:],
    y=perf_fees_2[1:],
    name=f"Perf Fee 2 ({user2_perf:.2f}%)",
    marker_color="#FFA500",
    offsetgroup=3
))
fig_fees_compare.update_layout(
    plot_bgcolor="#000000",
    paper_bgcolor="#000000",
    font_color="#FFFFFF",
    title="Annual Fees by Year: Fee Structure Comparison",
    xaxis_title="Year",
    yaxis_title=f"Fee Amount ({currency})",
    barmode='group',
    hovermode='x unified',
    showlegend=True
)
st.plotly_chart(fig_fees_compare, use_container_width=True, key='fees_chart_unique')
st.markdown("""
This chart compares annual management and performance fees for both user-defined fee structures. Adjust the sidebar to see how different fee levels impact the fee drag on your investment.
""")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Total Mgmt Fee 1", f"{currency} {sum(mgmt_fees_1):,.2f}")
    st.metric(f"Total Perf Fee 1", f"{currency} {sum(perf_fees_1):,.2f}")
with col2:
    st.metric(f"Total Mgmt Fee 2", f"{currency} {sum(mgmt_fees_2):,.2f}")
    st.metric(f"Total Perf Fee 2", f"{currency} {sum(perf_fees_2):,.2f}")
with col3:
    st.metric(f"Total Fees 1", f"{currency} {sum(mgmt_fees_1)+sum(perf_fees_1):,.2f}")
    st.metric(f"Total Fees 2", f"{currency} {sum(mgmt_fees_2)+sum(perf_fees_2):,.2f}")
section_divider()

# --- Summary Metrics Section ---
st.markdown("## Summary Metrics")
col_returns, col_fees, col_multiples = st.columns(3)

with col_returns:
    st.metric("Final Gross Return", f"{gross_values[-1]:,.2f} {currency}")
    st.metric("Final Net Return", f"{net_values[-1]:,.2f} {currency}")

with col_fees:
    st.metric("Total Fees Paid", f"{total_fees:,.2f} {currency}")
    st.metric("Management Fee (Total)", f"{total_management_fees:,.2f} {currency}")
    st.metric("Performance Fee (Total)", f"{total_performance_fees:,.2f} {currency}")
    st.metric("Management Fee Rate", f"{user1_mgmt:.1f}%")
    st.metric("Performance Fee Rate", f"{user1_perf:.1f}%")

with col_multiples:
    st.metric("Final MOIC", f"{gross_values[-1]/initial_investment:.2f}")
    st.metric("Final IRR", f"{gross_irr:.2%}")

st.markdown("""
**Conclusion:**

This summary provides a comprehensive overview of your investment scenario, including final returns, total fees, and key performance metrics. Adjust the parameters in the sidebar to see how different fee structures and assumptions impact your net returns and overall fund performance.
""") 