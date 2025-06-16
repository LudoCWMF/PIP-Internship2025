import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
from matplotlib.table import Table
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import os

# CloudMundi brand colors
CLOUDMUNDI_TEAL = '#2DD4BF'
CLOUDMUNDI_NAVY = '#1E3A8A' 
CLOUDMUNDI_DARK = '#0F172A'
CLOUDMUNDI_LIGHT = '#F1F5F9'
CLOUDMUNDI_ACCENT = '#06B6D4'

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# Platform fees in basis points
PLATFORM_FEES = {
    'eToro': {'trading': 50, 'spread': 100, 'management': 0},    # 150 bps total
    'Revolut': {'trading': 30, 'spread': 190, 'management': 0},  # 220 bps total  
    'Robinhood': {'trading': 0, 'spread': 50, 'management': 0}   # 50 bps total
}

# Asset class assumptions (annualized) - More realistic
ASSET_PARAMS = {
    'Bitcoin': {'return': 0.15, 'volatility': 0.25},    # 15% return, 25% vol (more conservative)
    'S&P 500': {'return': 0.08, 'volatility': 0.12},    # 8% return, 12% vol
    'Gold': {'return': 0.05, 'volatility': 0.10},       # 5% return, 10% vol
    'Bonds': {'return': 0.03, 'volatility': 0.03}       # 3% return, 3% vol
}

INVESTMENT = 10000  # £10,000

def create_fee_table():
    """Create and save platform fee comparison table"""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('white')
    ax.axis('tight')
    ax.axis('off')
    
    # Table data
    headers = ['Platform', 'Trading Fee (bps)', 'Spread (bps)', 'Total (bps)']
    data = []
    for platform, fees in PLATFORM_FEES.items():
        total = sum(fees.values())
        data.append([platform, fees['trading'], fees['spread'], total])
    
    # Create table
    table = ax.table(cellText=data, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2)
    
    # Style header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor(CLOUDMUNDI_NAVY)
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style cells
    for i in range(1, len(data) + 1):
        for j in range(len(headers)):
            if j == 0:  # Platform names
                table[(i, j)].set_text_props(weight='bold')
            table[(i, j)].set_facecolor('#F8FAFB' if i % 2 == 0 else 'white')
    
    plt.title('Platform Fee Comparison (Basis Points)', fontsize=16, fontweight='bold', 
              color=CLOUDMUNDI_NAVY, pad=20)
    plt.savefig('platform_fee_table.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def simulate_asset_returns(asset, days):
    """Simulate returns for a specific asset"""
    params = ASSET_PARAMS[asset]
    mu = params['return'] / 252  # Daily return
    sigma = params['volatility'] / np.sqrt(252)  # Daily volatility
    
    np.random.seed(hash(asset) % 2**32)
    returns = np.random.normal(mu, sigma, days)
    prices = INVESTMENT * np.cumprod(1 + returns)
    return prices

def create_asset_predictions():
    """Create predicted returns for each asset class"""
    days = 252  # 1 year
    dates = pd.date_range(start='2024-01-01', periods=days)
    
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    
    colors = {'Bitcoin': '#F7931A', 'S&P 500': '#003366', 'Gold': '#FFD700', 'Bonds': '#4B8E4B'}
    
    for asset, color in colors.items():
        values = simulate_asset_returns(asset, days)
        ax.plot(dates, values, label=asset, color=color, linewidth=3, alpha=0.9)
        
        # Add final value annotation
        final_value = values[-1]
        total_return = ((final_value - INVESTMENT) / INVESTMENT) * 100
        
        ax.annotate(f'{asset}\n£{final_value:,.0f}\n+{total_return:.1f}%', 
                   xy=(dates[-1], final_value), 
                   xytext=(20, 0), 
                   textcoords='offset points',
                   fontsize=10, fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, alpha=0.9))
    
    ax.axhline(y=INVESTMENT, color='gray', linestyle='--', alpha=0.5, linewidth=2)
    ax.set_title('Asset Class Performance Prediction (1 Year)', 
                fontsize=20, fontweight='bold', color=CLOUDMUNDI_NAVY, pad=20)
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Portfolio Value (£)', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=12)
    ax.grid(True, axis='y', alpha=0.2, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('asset_predictions.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_platform_adjusted_returns():
    """Create returns adjusted for platform fees"""
    days = 252  # 1 year
    dates = pd.date_range(start='2024-01-01', periods=days)
    
    # Create subplots for each asset
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.patch.set_facecolor('white')
    axes = axes.flatten()
    
    assets = ['Bitcoin', 'S&P 500', 'Gold', 'Bonds']
    asset_colors = {'Bitcoin': '#F7931A', 'S&P 500': '#003366', 'Gold': '#FFD700', 'Bonds': '#4B8E4B'}
    platform_colors = {'eToro': CLOUDMUNDI_TEAL, 'Revolut': CLOUDMUNDI_NAVY, 'Robinhood': CLOUDMUNDI_ACCENT}
    
    for idx, asset in enumerate(assets):
        ax = axes[idx]
        base_values = simulate_asset_returns(asset, days)
        
        # Plot for each platform
        for platform, color in platform_colors.items():
            # Calculate total fee impact
            total_fee_bps = sum(PLATFORM_FEES[platform].values())
            annual_fee = total_fee_bps / 10000  # Convert bps to decimal
            daily_fee = annual_fee / 252
            
            # Apply fees to returns
            fee_adjusted_values = base_values.copy()
            for i in range(1, len(fee_adjusted_values)):
                fee_adjusted_values[i] = fee_adjusted_values[i-1] * (1 - daily_fee) * (base_values[i] / base_values[i-1])
            
            ax.plot(dates, fee_adjusted_values, label=f'{platform} ({total_fee_bps} bps)', 
                   color=color, linewidth=2.5, alpha=0.8)
        
        # Add base performance (no fees)
        ax.plot(dates, base_values, label='No Fees', color=asset_colors[asset], 
               linewidth=2, linestyle='--', alpha=0.6)
        
        ax.axhline(y=INVESTMENT, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax.set_title(f'{asset} Performance by Platform', fontsize=14, fontweight='bold', color=CLOUDMUNDI_NAVY)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Value (£)', fontsize=11)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, axis='y', alpha=0.2, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    plt.suptitle('Platform Fee Impact on Asset Performance (1 Year)', 
                fontsize=20, fontweight='bold', color=CLOUDMUNDI_NAVY, y=0.98)
    plt.tight_layout()
    plt.savefig('platform_fee_impact.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def simulate_portfolio(asset_weights, platform, days):
    """Simulate portfolio with given asset weights and platform fees"""
    # Asset weights: {'Bitcoin': 0.3, 'S&P 500': 0.25, 'Gold': 0.25, 'Bonds': 0.2}
    portfolio_values = np.zeros(days)
    
    for asset, weight in asset_weights.items():
        asset_values = simulate_asset_returns(asset, days) * weight
        portfolio_values += asset_values
    
    # Apply platform fees
    total_fee_bps = sum(PLATFORM_FEES[platform].values())
    annual_fee = total_fee_bps / 10000
    daily_fee = annual_fee / 252
    
    for i in range(1, days):
        portfolio_values[i] = portfolio_values[i] * (1 - daily_fee * i)
    
    return portfolio_values

def plot_portfolio_projection(days, filename, title):
    dates = pd.date_range(start='2024-01-01', periods=days)
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Asset weights
    asset_weights = {'Bitcoin': 0.3, 'S&P 500': 0.25, 'Gold': 0.25, 'Bonds': 0.2}
    
    # Store results for IRR calculation
    results = {}
    
    for platform, color in zip(PLATFORM_FEES.keys(), [CLOUDMUNDI_TEAL, CLOUDMUNDI_NAVY, CLOUDMUNDI_ACCENT]):
        values = simulate_portfolio(asset_weights, platform, days)
        results[platform] = values
        
        # Plot line
        ax.plot(dates, values, label=platform, color=color, linewidth=3, alpha=0.9)
        
        # Calculate returns
        final_value = values[-1]
        total_return = ((final_value - INVESTMENT) / INVESTMENT) * 100
        annual_return = ((final_value / INVESTMENT) ** (252/days) - 1) * 100
        
        # Add final value and return annotation
        y_offset = 0
        if platform == 'Revolut': y_offset = -300
        elif platform == 'Robinhood': y_offset = 300
        
        ax.annotate(f'{platform}\n£{final_value:,.0f}\n+{total_return:.1f}%', 
                   xy=(dates[-1], final_value), 
                   xytext=(20, y_offset), 
                   textcoords='offset points',
                   fontsize=11, fontweight='bold', color=color,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, alpha=0.9),
                   arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # Break-even line
    ax.axhline(y=INVESTMENT, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Initial Investment')
    
    # Styling
    ax.set_title(title, fontsize=20, fontweight='bold', color=CLOUDMUNDI_NAVY, pad=20)
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Portfolio Value (£)', fontsize=14, fontweight='bold')
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:,.0f}'))
    
    # Better legend
    legend = ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=12)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.95)
    
    # Grid
    ax.grid(True, axis='y', alpha=0.2, linestyle='--')
    ax.set_axisbelow(True)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add IRR table
    irr_text = 'Annualized Returns:\n'
    for platform in PLATFORM_FEES.keys():
        final = results[platform][-1]
        irr = ((final / INVESTMENT) ** (252/days) - 1) * 100
        irr_text += f'{platform}: {irr:.1f}%\n'
    
    ax.text(0.02, 0.98, irr_text.strip(), transform=ax.transAxes, 
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=CLOUDMUNDI_LIGHT, alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()

def create_portfolio_simulation():
    """Projected return simulation - Professional version"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # More realistic returns with volatility
    etoro_returns = np.cumsum(np.random.normal(0.08/252, 0.15/np.sqrt(252), len(dates))) - 0.015
    revolut_returns = np.cumsum(np.random.normal(0.08/252, 0.15/np.sqrt(252), len(dates))) - 0.025
    robinhood_returns = np.cumsum(np.random.normal(0.08/252, 0.15/np.sqrt(252), len(dates))) - 0.005
    
    etoro_returns = (etoro_returns + 1) * 100
    revolut_returns = (revolut_returns + 1) * 100
    robinhood_returns = (robinhood_returns + 1) * 100
    
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Plot lines with better styling
    ax.plot(dates, etoro_returns, label='eToro Portfolio', color=CLOUDMUNDI_TEAL, 
            linewidth=3, alpha=0.9)
    ax.plot(dates, revolut_returns, label='Revolut Portfolio', color=CLOUDMUNDI_NAVY, 
            linewidth=3, alpha=0.9)
    ax.plot(dates, robinhood_returns, label='Robinhood Portfolio', color=CLOUDMUNDI_ACCENT, 
            linewidth=3, alpha=0.9)
    
    # Add shaded area for profit/loss zones
    ax.fill_between(dates, 100, etoro_returns, where=(etoro_returns >= 100), 
                    color=CLOUDMUNDI_TEAL, alpha=0.1)
    ax.fill_between(dates, 100, etoro_returns, where=(etoro_returns < 100), 
                    color='red', alpha=0.1)
    
    # Break-even line
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5, linewidth=2, label='Break-even')
    
    # Styling
    ax.set_xlabel('Date (2024)', fontsize=14, fontweight='bold', color=CLOUDMUNDI_DARK)
    ax.set_ylabel('Portfolio Value (%)', fontsize=14, fontweight='bold', color=CLOUDMUNDI_DARK)
    ax.set_title('Portfolio Performance Projection\n', fontsize=20, fontweight='bold', color=CLOUDMUNDI_NAVY)
    ax.text(0.5, 0.98, 'Simulated 1-year returns for diversified portfolio (BTC, S&P 500, Gold, Bonds)', 
            transform=ax.transAxes, ha='center', va='top', fontsize=12, 
            color=CLOUDMUNDI_DARK, alpha=0.8)
    
    # Format x-axis
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    
    # Improve legend
    legend = ax.legend(loc='upper left', frameon=True, fancybox=True, 
                      shadow=True, fontsize=12)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.95)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    
    # Grid
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Add final values annotation
    final_values = {
        'eToro': etoro_returns[-1],
        'Revolut': revolut_returns[-1],
        'Robinhood': robinhood_returns[-1]
    }
    
    y_offset = 0
    for platform, value in final_values.items():
        ax.annotate(f'{platform}: {value:.1f}%', 
                   xy=(dates[-1], value), 
                   xytext=(10, y_offset), 
                   textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        y_offset += 20
    
    # CloudMundi branding
    ax.text(0.99, 0.01, 'CloudMundi', transform=ax.transAxes, 
            ha='right', va='bottom', fontsize=10, color=CLOUDMUNDI_NAVY, 
            alpha=0.7, style='italic')
    
    plt.tight_layout()
    plt.savefig('portfolio_simulation.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

def create_asset_allocation():
    """Asset allocation pie chart - Professional version"""
    assets = ['Bitcoin\n30%', 'S&P 500 ETF\n25%', 'Gold/Commodities\n25%', 'Bonds\n20%']
    sizes = [30, 25, 25, 20]
    colors = [CLOUDMUNDI_TEAL, CLOUDMUNDI_NAVY, CLOUDMUNDI_ACCENT, '#94A3B8']
    
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('white')
    
    # Create pie with better styling
    wedges, texts, autotexts = ax.pie(sizes, labels=assets, colors=colors, autopct='',
                                     startangle=90, textprops={'fontsize': 14, 'fontweight': 'bold'},
                                     wedgeprops=dict(width=0.7, edgecolor='white', linewidth=3))
    
    # Add percentage labels inside
    for i, (wedge, size) in enumerate(zip(wedges, sizes)):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = 0.5 * np.cos(np.radians(angle))
        y = 0.5 * np.sin(np.radians(angle))
        ax.text(x, y, f'{size}%', ha='center', va='center', fontsize=16, 
                fontweight='bold', color='white')
    
    # Center circle for donut effect
    centre_circle = plt.Circle((0, 0), 0.3, fc='white', linewidth=3, edgecolor=CLOUDMUNDI_NAVY)
    fig.gca().add_artist(centre_circle)
    
    # Add center text
    ax.text(0, 0, 'PORTFOLIO\nMIX', ha='center', va='center', 
            fontsize=16, fontweight='bold', color=CLOUDMUNDI_NAVY)
    
    ax.set_title('Recommended Asset Allocation Strategy\n', 
                 fontsize=20, fontweight='bold', color=CLOUDMUNDI_NAVY, pad=20)
    ax.text(0.5, 0.95, 'Diversified investment approach for balanced risk-return profile', 
            transform=ax.transAxes, ha='center', va='top', fontsize=12, 
            color=CLOUDMUNDI_DARK, alpha=0.8)
    
    # Add a legend with brief explanation
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=CLOUDMUNDI_TEAL, markersize=10, label='Bitcoin: High growth, high risk'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=CLOUDMUNDI_NAVY, markersize=10, label='S&P 500: Moderate risk, stable returns'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=CLOUDMUNDI_ACCENT, markersize=10, label='Gold: Defensive hedge, low volatility'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#94A3B8', markersize=10, label='Bonds: Capital preservation, low risk')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=12)
    
    # CloudMundi branding
    ax.text(0.99, 0.01, 'CloudMundi', transform=ax.transAxes, 
            ha='right', va='bottom', fontsize=10, color=CLOUDMUNDI_NAVY, 
            alpha=0.7, style='italic')
    
    ax.axis('equal')
    plt.tight_layout()
    plt.savefig('asset_allocation_pie.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

def calculate_max_drawdown(prices):
    peak = prices[0]
    max_dd = 0
    for price in prices:
        if price > peak:
            peak = price
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    excess_returns = returns - (risk_free_rate / 252)
    if np.std(excess_returns) == 0:
        return 0
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

def create_asset_risk_table():
    """Create a table summarizing risk metrics for each asset class"""
    assets = list(ASSET_PARAMS.keys())
    metrics = []
    days = 252
    for asset in assets:
        prices = simulate_asset_returns(asset, days)
        returns = np.diff(prices) / prices[:-1]
        vol = np.std(returns) * np.sqrt(252)
        max_dd = calculate_max_drawdown(prices)
        sharpe = calculate_sharpe_ratio(returns)
        metrics.append([
            f"{vol*100:.1f}%",
            f"{max_dd*100:.1f}%",
            f"{sharpe:.2f}"
        ])
    # Table data
    columns = ["Volatility (Ann.)", "Max Drawdown", "Sharpe Ratio"]
    fig, ax = plt.subplots(figsize=(10, 2.5))
    ax.axis('off')
    table = ax.table(
        cellText=metrics,
        rowLabels=assets,
        colLabels=columns,
        cellLoc='center',
        loc='center',
        colColours=[CLOUDMUNDI_TEAL, CLOUDMUNDI_NAVY, CLOUDMUNDI_ACCENT],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(13)
    table.scale(1.2, 2)
    fig.patch.set_facecolor('white')
    plt.title('Asset Class Risk Metrics (1 Year Simulation)', fontsize=16, fontweight='bold', color=CLOUDMUNDI_NAVY, pad=15)
    plt.tight_layout()
    plt.savefig('asset_risk_table.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def export_charts_to_excel():
    """Export all generated charts to an Excel file"""
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # List of chart filenames
    charts = [
        'platform_feature_matrix.png',
        'platform_fee_table.png',
        'asset_predictions.png',
        'asset_risk_table.png',
        'platform_fee_impact.png',
        'portfolio_projection_1month.png',
        'portfolio_projection_1year.png',
        'asset_allocation_pie.png'
    ]

    for chart in charts:
        if os.path.exists(chart):
            ws = wb.create_sheet(title=chart.replace('.png', ''))
            img = Image(chart)
            ws.add_image(img, 'A1')

    wb.save('CloudMundi_Charts.xlsx')

if __name__ == "__main__":
    print("🌟 Generating CloudMundi Trading Platform Analysis...")
    # Generate fee table instead of cost comparison chart
    create_fee_table()
    create_asset_predictions()
    create_platform_adjusted_returns()
    create_portfolio_simulation()
    create_asset_allocation()
    create_asset_risk_table()
    # 1-month projection (21 trading days)
    plot_portfolio_projection(21, 'portfolio_projection_1month.png', 'Portfolio Projection: 1 Month (£10,000 Initial Investment)')
    # 1-year projection (252 trading days)
    plot_portfolio_projection(252, 'portfolio_projection_1year.png', 'Portfolio Projection: 1 Year (£10,000 Initial Investment)')
    export_charts_to_excel()
    print("✅ Charts generated successfully!") 
    