# Calculate Baseline (No Fees) in USD, then convert
if use_capital_calls:
    baseline_initial = total_commitment / selected_rate
else:
    baseline_initial = initial_investment / selected_rate

baseline_model = FinancialModel(
    initial_investment=baseline_initial,
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