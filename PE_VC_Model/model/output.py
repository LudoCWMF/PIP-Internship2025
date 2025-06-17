import pandas as pd
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Currency(Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"

@dataclass
class FeeStructure:
    management_fee: float = 0.02  # 2%
    performance_fee: float = 0.20  # 20%
    hurdle_rate: float = 0.08  # 8%

@dataclass
class PerformanceMetrics:
    target_irr: float
    moic: float
    mm: float
    tvpi: float

@dataclass
class CapitalCallSchedule:
    total_commitment: float
    investment_period_years: int = 3
    call_frequency: str = 'quarterly'  # 'quarterly', 'semi-annual', 'annual'
    
    def get_call_schedule(self) -> List[Tuple[int, float]]:
        """Generate capital call schedule based on parameters."""
        if self.call_frequency == 'quarterly':
            periods_per_year = 4
        elif self.call_frequency == 'semi-annual':
            periods_per_year = 2
        else:  # annual
            periods_per_year = 1
            
        total_periods = self.investment_period_years * periods_per_year
        call_amount = self.total_commitment / total_periods
        
        schedule = []
        for period in range(total_periods):
            year = period / periods_per_year
            schedule.append((year, call_amount))
            
        return schedule

class FinancialModel:
    def __init__(
        self,
        initial_investment: float = 1000,
        currency: Currency = Currency.USD,
        fee_structure: Optional[FeeStructure] = None,
        performance_metrics: Optional[PerformanceMetrics] = None,
        capital_call_schedule: Optional[CapitalCallSchedule] = None
    ):
        self.initial_investment = initial_investment
        self.currency = currency
        self.fee_structure = fee_structure or FeeStructure()
        self.performance_metrics = performance_metrics or PerformanceMetrics(
            target_irr=0.15,  # 15% IRR
            moic=2.0,    # 2.0x MOIC
            mm=2.5,      # 2.5x MM
            tvpi=2.5     # 2.5x TVPI
        )
        self.capital_call_schedule = capital_call_schedule
        
        # Validate inputs
        self._validate_inputs()
        
        # Initialize results DataFrame
        self.results = self._calculate_results()

    def _validate_inputs(self):
        """Validate all input parameters."""
        if self.capital_call_schedule:
            if self.capital_call_schedule.total_commitment <= 0:
                raise ValueError("Total commitment must be positive")
            if self.capital_call_schedule.investment_period_years <= 0:
                raise ValueError("Investment period must be positive")
        else:
            if self.initial_investment <= 0:
                raise ValueError("Initial investment must be positive")
        
        if not 0 <= self.fee_structure.management_fee <= 1:
            raise ValueError("Management fee must be between 0 and 1")
        
        if not 0 <= self.fee_structure.performance_fee <= 1:
            raise ValueError("Performance fee must be between 0 and 1")
        
        if not 0 <= self.fee_structure.hurdle_rate <= 1:
            raise ValueError("Hurdle rate must be between 0 and 1")
        
        if self.performance_metrics.target_irr <= -1:
            raise ValueError("Target IRR must be greater than -100%")
        
        if self.performance_metrics.moic <= 0:
            raise ValueError("MOIC must be positive")
        
        if self.performance_metrics.mm <= 0:
            raise ValueError("Money Multiple must be positive")
        
        if self.performance_metrics.tvpi <= 0:
            raise ValueError("TVPI must be positive")

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
            
            # Calculate performance fees (only on profits above hurdle, at the end)
            if year == n_years - 1:
                profit_above_hurdle = max(0, investment_value[year] - cumulative_called[year] * (1 + self.fee_structure.hurdle_rate) ** year)
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
        
        # Calculate cumulative returns
        df['Cumulative_Gross'] = df['Gross_Return']
        df['Cumulative_Net'] = df['Net_Return']
        
        # --- Simulate realistic cash flows for IRR calculation ---
        gross_cash_flows = np.zeros(n_years)
        net_cash_flows = np.zeros(n_years)
        gross_cash_flows[0] = -cumulative_called[0]
        net_cash_flows[0] = -cumulative_called[0]
        # Distribute final value over harvest years (years 4-10)
        harvest_start = 4
        harvest_years = n_years - harvest_start
        if harvest_years > 0:
            gross_dist = (investment_value[-1] - cumulative_called[0]) / harvest_years
            net_dist = (net_value[-1] - cumulative_called[0]) / harvest_years
            for i in range(harvest_start, n_years):
                gross_cash_flows[i] = gross_dist
                net_cash_flows[i] = net_dist
        # Calculate IRR for each year using cash flows up to that year
        gross_irr = []
        net_irr = []
        for year in range(n_years):
            try:
                gross_irr.append(npf.irr(gross_cash_flows[:year+1]))
            except:
                gross_irr.append(np.nan)
            try:
                net_irr.append(npf.irr(net_cash_flows[:year+1]))
            except:
                net_irr.append(np.nan)
        df['Gross_IRR'] = gross_irr
        df['Net_IRR'] = net_irr
        
        # Calculate MOIC
        df['Gross_MOIC'] = df['Cumulative_Gross'] / cumulative_called[0]
        df['Net_MOIC'] = df['Cumulative_Net'] / cumulative_called[0]
        
        # Calculate Money Multiple
        df['Gross_MM'] = df['Cumulative_Gross'] / cumulative_called[0]
        df['Net_MM'] = df['Cumulative_Net'] / cumulative_called[0]
        
        # Calculate TVPI
        df['Gross_TVPI'] = df['Cumulative_Gross'] / cumulative_called[0]
        df['Net_TVPI'] = df['Cumulative_Net'] / cumulative_called[0]
        
        # Calculate DPI (Distributed to Paid-In)
        df['Gross_DPI'] = (df['Cumulative_Gross'] - cumulative_called[0]) / cumulative_called[0]
        df['Net_DPI'] = (df['Cumulative_Net'] - cumulative_called[0]) / cumulative_called[0]
        
        return df

    def get_summary_metrics(self) -> Dict[str, float]:
        """Get summary metrics for the investment."""
        final_row = self.results.iloc[-1]
        return {
            'Final_Gross_Return': final_row['Cumulative_Gross'],
            'Final_Net_Return': final_row['Cumulative_Net'],
            'Total_Fees': self.results['Management_Fee'].sum() + self.results['Performance_Fee'].sum(),
            'Final_Gross_IRR': final_row['Gross_IRR'],
            'Final_Net_IRR': final_row['Net_IRR'],
            'Final_Gross_MOIC': final_row['Gross_MOIC'],
            'Final_Net_MOIC': final_row['Net_MOIC'],
            'Final_Gross_MM': final_row['Gross_MM'],
            'Final_Net_MM': final_row['Net_MM'],
            'Final_Gross_TVPI': final_row['Gross_TVPI'],
            'Final_Net_TVPI': final_row['Net_TVPI']
        }

    def display_metrics(self):
        """Display key financial metrics."""
        print(f"\nFinancial Model Results ({self.currency.value})")
        print("-" * 50)
        print(f"Initial Investment: {self.initial_investment:,.2f}")
        print(f"Management Fee: {self.fee_structure.management_fee*100:.1f}%")
        print(f"Performance Fee: {self.fee_structure.performance_fee*100:.1f}%")
        print("\nPerformance Metrics:")
        print(f"Target IRR: {self.performance_metrics.target_irr*100:.1f}%")
        print(f"MOIC: {self.performance_metrics.moic:.2f}x")
        print(f"Money Multiple: {self.performance_metrics.mm:.2f}x")
        print(f"TVPI: {self.performance_metrics.tvpi:.2f}x")
        
        final_gross = self.results['Cumulative_Gross'].iloc[-1]
        final_net = self.results['Cumulative_Net'].iloc[-1]
        total_fees = self.results['Management_Fee'].sum() + self.results['Performance_Fee'].sum()
        
        print("\nFinal Results:")
        print(f"Final Gross Return: {final_gross:,.2f}")
        print(f"Final Net Return: {final_net:,.2f}")
        print(f"Total Fees Paid: {total_fees:,.2f}")
        print(f"Net Multiple: {final_net/self.initial_investment:.2f}x")

    def plot_results(self):
        """Create visualization of returns and fees."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Returns over time
        ax1.plot(self.results['Year'], self.results['Cumulative_Gross'], label='Cumulative Gross Return', marker='o')
        ax1.plot(self.results['Year'], self.results['Cumulative_Net'], label='Cumulative Net Return', marker='s')
        ax1.set_title('Investment Returns Over Time')
        ax1.set_xlabel('Year')
        ax1.set_ylabel(f'Value ({self.currency.value})')
        ax1.grid(True)
        ax1.legend()
        
        # Plot 2: Fees over time
        ax2.bar(self.results['Year'], self.results['Management_Fee'], 
                label='Management Fee', alpha=0.6)
        ax2.bar(self.results['Year'], self.results['Performance_Fee'],
                bottom=self.results['Management_Fee'], label='Performance Fee', alpha=0.6)
        ax2.set_title('Fees Over Time')
        ax2.set_xlabel('Year')
        ax2.set_ylabel(f'Fees ({self.currency.value})')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()

def main():
    # Example usage
    model = FinancialModel(
        initial_investment=1000,
        currency=Currency.USD,
        fee_structure=FeeStructure(
            management_fee=0.02,
            performance_fee=0.20,
            hurdle_rate=0.08
        ),
        performance_metrics=PerformanceMetrics(
            target_irr=0.15,
            moic=2.0,
            mm=2.5,
            tvpi=2.5
        )
    )
    
    print(model.get_summary_metrics())
    model.display_metrics()
    model.plot_results()

if __name__ == "__main__":
    main()
