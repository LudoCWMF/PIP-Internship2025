    def _calculate_results(self) -> pd.DataFrame:
        """Calculate gross and net returns over time with realistic PE/VC cash flows."""
        # Create time series
        years = np.arange(0, 11)  # 10-year projection
        n_years = len(years)

        # Initialize arrays
        investment_value = np.zeros(n_years)
        management_fees = np.zeros(n_years)
        performance_fees = np.zeros(n_years)
        net_value = np.zeros(n_years)
        called_capital = np.zeros(n_years)
        committed_capital = np.zeros(n_years)

        # Handle capital calls if schedule exists
        if self.capital_call_schedule:
            call_schedule = self.capital_call_schedule.get_call_schedule()
            for year, amount in call_schedule:
                year_idx = int(year)
                if year_idx < n_years:
                    called_capital[year_idx] = amount
            # Set committed capital to total commitment for investment period, then zero (or could be cumulative called for post-investment period)
            investment_period = self.capital_call_schedule.investment_period_years
            committed_capital[:investment_period+1] = self.capital_call_schedule.total_commitment
            committed_capital[investment_period+1:] = 0
        else:
            # Single upfront investment
            called_capital[0] = self.initial_investment
            committed_capital[:] = self.initial_investment  # Charge management fee on initial investment every year

        # Calculate cumulative called capital
        cumulative_called = np.cumsum(called_capital)

        # Initial investment value
        investment_value[0] = called_capital[0]
        net_value[0] = called_capital[0]

        # Calculate final value based on target IRR
        final_value = cumulative_called[-1] * (1 + self.performance_metrics.target_irr) ** (n_years - 1)

        # Simulate realistic PE/VC cash flows
        investment_period = 3
        harvest_period = n_years - investment_period

        # Calculate intermediate values
        harvest_start = 4  # Define outside the loop to avoid redeclaration
        for year in range(1, n_years):
            if year <= investment_period:
                # Investment period: gradual value increase
                investment_value[year] = cumulative_called[year] * (1 + self.performance_metrics.target_irr) ** year
            else:
                # Harvest period: distribute returns
                remaining_years = n_years - year
                if remaining_years > 0:
                    # Distribute remaining value over remaining years
                    distribution = (final_value - investment_value[year-1]) / remaining_years
                    investment_value[year] = investment_value[year-1] + distribution
            
            # Calculate management fees
            if self.capital_call_schedule:
                if year <= self.capital_call_schedule.investment_period_years:
                    # During investment period: fee on committed capital
                    management_fees[year] = self.capital_call_schedule.total_commitment * self.fee_structure.management_fee
                else:
                    # After investment period: fee on invested capital (cumulative called), ensure nonzero for chart visibility
                    management_fees[year] = max(cumulative_called[year], 1e-8) * self.fee_structure.management_fee
            else:
                management_fees[year] = committed_capital[year] * self.fee_structure.management_fee
            
            # --- FIX: Spread performance fees over harvest years ---
            if self.capital_call_schedule:
                hurdle_base = cumulative_called[year]
            else:
                hurdle_base = self.initial_investment

            if year > 0:
                # Calculate distributed profit this year (only during harvest period)
                if year >= harvest_start:
                    distributed = investment_value[year] - investment_value[year-1]
                    hurdle = hurdle_base * (self.fee_structure.hurdle_rate)  # annual hurdle
                    profit_above_hurdle = max(0, distributed - hurdle)
                    performance_fees[year] = profit_above_hurdle * self.fee_structure.performance_fee
                else:
                    performance_fees[year] = 0
            
            # Calculate net value
            net_value[year] = investment_value[year] - management_fees[year] - performance_fees[year] 

        # Create DataFrame with all metrics
        df = pd.DataFrame({
            'Year': years,
            'Called_Capital': called_capital,
            'Committed_Capital': committed_capital,
            'Cumulative_Called': cumulative_called,
            'Gross_Return': investment_value,
            'Management_Fee': management_fees,
            'Performance_Fee': performance_fees,
            'Net_Return': net_value
        })

        # ... rest of existing calculation code ...

        return df 