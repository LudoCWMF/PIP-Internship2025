import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.patches as mpatches

# Set professional financial style
sns.set_theme(style="whitegrid", context="notebook", font_scale=1.2)

# Custom styling for financial charts
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.2
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.color'] = '#333333'
plt.rcParams['ytick.color'] = '#333333'
plt.rcParams['axes.labelcolor'] = '#333333'
plt.rcParams['axes.titlecolor'] = '#333333'

# Professional color palette for financial charts
colors = {
    'gross': '#1f77b4',    # Blue for Gross
    'net': '#ff7f0e',      # Orange for Net
    'target': '#2ca02c',   # Green for Target
    'grid': '#e0e0e0',     # Light gray for grid
    'background': '#ffffff' # White background
}

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# --- Fee Model ---
mgmt_fee_drag = 0.135  # 13.5% of Gross IRR
carry_drag = 0.0375    # 3.75% of Gross IRR

# Simulating extracted key data from Agathos Fund III documents for .csv export
data = {
    "Fund": ["Fund I", "Fund II", "Fund III (Target)"],
    "Vintage Year": [2016, 2020, 2025],
    "Committed Capital (£m)": [30, 50, 100],
    "Deployed Capital (£m)": [30, 47, 0],
    "Gross IRR (%)": [28.0, 24.5, 25.0],
    # Net IRR: calculated for Fund I & II, Fund III uses target 18%
    "Net IRR (%)": [
        round(28.0 - (28.0 * mgmt_fee_drag) - (28.0 * carry_drag), 2),
        round(24.5 - (24.5 * mgmt_fee_drag) - (24.5 * carry_drag), 2),
        18.0
    ],
    "Gross MOIC (x)": [2.5, 2.2, 2.5],
    # Net MOIC: estimate similar drag as IRR for illustration, or use 1.8x for Fund III as per your doc
    "Net MOIC (x)": [
        round(2.5 * (1 - mgmt_fee_drag - carry_drag), 2),
        round(2.2 * (1 - mgmt_fee_drag - carry_drag), 2),
        1.8
    ],
    "No. of Platform Investments": [6, 8, 8],
    "Sectors": ["Business Services, Healthcare", "Education, Healthcare", "Education, ESG, Healthcare"]
}

fund_data_df = pd.DataFrame(data)

# Save as CSV in the current directory
csv_path = os.path.join(current_dir, "Agathos_Fund_Performance_and_Strategy.csv")
fund_data_df.to_csv(csv_path, index=False)

def set_ymax(ax, values, buffer=0.10):
    ymax = max(values) * (1 + buffer)
    ax.set_ylim(top=ymax)

def save_png_only(fig, filename_base):
    fig.savefig(f"{filename_base}.png", dpi=300, bbox_inches='tight', facecolor=colors['background'])

def create_irr_comparison():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    width = 0.35
    bars1 = ax.bar(x - width/2, fund_data_df['Gross IRR (%)'], width, 
                   label='Gross IRR', color=colors['gross'], alpha=0.9,
                   edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, fund_data_df['Net IRR (%)'], width, 
                   label='Net IRR', color=colors['net'], alpha=0.9,
                   edgecolor='black', linewidth=1)
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 8),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    add_labels(bars1)
    add_labels(bars2)
    set_ymax(ax, list(fund_data_df['Gross IRR (%)']) + list(fund_data_df['Net IRR (%)']))
    ax.axhline(y=18.0, color=colors['target'], linestyle='--', alpha=0.8,
               linewidth=2, label='Fund III Target Net IRR')
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('IRR (%)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Gross vs. Net IRR', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    legend = ax.legend(loc='upper right', frameon=True, framealpha=0.95,
                      edgecolor='black', fancybox=False)
    fig.text(0.02, 0.01, 
             'Note: Gross IRR represents portfolio performance before fees and carry.\n'
             'Net IRR represents actual returns to Limited Partners.',
             fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'irr_comparison'))
    plt.close(fig)

def create_moic_comparison():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    width = 0.35
    bars1 = ax.bar(x - width/2, fund_data_df['Gross MOIC (x)'], width,
                   label='Gross MOIC', color=colors['gross'], alpha=0.9,
                   edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, fund_data_df['Net MOIC (x)'], width,
                   label='Net MOIC', color=colors['net'], alpha=0.9,
                   edgecolor='black', linewidth=1)
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}x',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 8),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    add_labels(bars1)
    add_labels(bars2)
    set_ymax(ax, list(fund_data_df['Gross MOIC (x)']) + list(fund_data_df['Net MOIC (x)']))
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('MOIC (x)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Gross vs. Net MOIC', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    legend = ax.legend(loc='upper right', frameon=True, framealpha=0.95,
                      edgecolor='black', fancybox=False)
    fig.text(0.02, 0.01, 
             'Note: MOIC (Multiple on Invested Capital) shows total return multiple.\n'
             'Gross MOIC represents portfolio performance, Net MOIC represents LP returns.',
             fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'moic_comparison'))
    plt.close(fig)

def create_timeline_chart():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    ax.plot(fund_data_df['Vintage Year'], fund_data_df['Net IRR (%)'], 
            marker='o', linewidth=2.5, color=colors['net'], label='Net IRR',
            markersize=10, markerfacecolor='white', markeredgecolor=colors['net'],
            markeredgewidth=2)
    for x, y in zip(fund_data_df['Vintage Year'], fund_data_df['Net IRR (%)']):
        ax.annotate(f'{y:.1f}%', (x, y), textcoords="offset points", xytext=(0, 8),
                    ha='center', fontsize=11, fontweight='bold', color='black')
    ax.axhline(y=18.0, color=colors['target'], linestyle='--', alpha=0.8,
               linewidth=2, label='Fund III Target')
    ax.set_xlabel('Vintage Year', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Net IRR (%)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Net IRR by Vintage Year', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(fund_data_df['Vintage Year'])
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    legend = ax.legend(loc='upper right', frameon=True, framealpha=0.95,
                      edgecolor='black', fancybox=False)
    fig.text(0.02, 0.01, 
             'Note: Shows the evolution of Net IRR across fund vintages.\n'
             'Fund III (2025) represents target performance.',
             fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'irr_timeline'))
    plt.close(fig)

def create_capital_comparison():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    width = 0.35
    bars1 = ax.bar(x - width/2, fund_data_df['Committed Capital (£m)'], width, 
                   label='Committed Capital', color=colors['gross'], alpha=0.9,
                   edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, fund_data_df['Deployed Capital (£m)'], width, 
                   label='Deployed Capital', color=colors['net'], alpha=0.9,
                   edgecolor='black', linewidth=1)
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'£{height:.0f}m',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 8),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    add_labels(bars1)
    add_labels(bars2)
    set_ymax(ax, list(fund_data_df['Committed Capital (£m)']) + list(fund_data_df['Deployed Capital (£m)']))
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Capital (£m)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Committed vs. Deployed Capital', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    legend = ax.legend(loc='upper right', frameon=True, framealpha=0.95,
                      edgecolor='black', fancybox=False)
    fig.text(0.02, 0.01, 
             'Note: Committed Capital is the total capital raised. Deployed Capital is the amount invested to date.',
             fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'capital_comparison'))
    plt.close(fig)

def create_gross_irr_chart():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    bars = ax.bar(x, fund_data_df['Gross IRR (%)'], color=colors['gross'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    set_ymax(ax, fund_data_df['Gross IRR (%)'])
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Gross IRR (%)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Gross IRR (Before Fees)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    fig.text(0.02, 0.01, 'Gross IRR is the annualized return before any fees or carry.', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'gross_irr_only'))
    plt.close(fig)

def create_net_irr_chart():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    bars = ax.bar(x, fund_data_df['Net IRR (%)'], color=colors['net'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    set_ymax(ax, fund_data_df['Net IRR (%)'])
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Net IRR (%)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Net IRR (After Fees)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    fig.text(0.02, 0.01, 'Net IRR is your actual annualized return after all fees and carry.', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'net_irr_only'))
    plt.close(fig)

def create_gross_moic_chart():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    bars = ax.bar(x, fund_data_df['Gross MOIC (x)'], color=colors['gross'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}x',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    set_ymax(ax, fund_data_df['Gross MOIC (x)'])
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Gross MOIC (x)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Gross MOIC (Before Fees)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    fig.text(0.02, 0.01, 'Gross MOIC is the total multiple on invested capital before any fees or carry.', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'gross_moic_only'))
    plt.close(fig)

def create_net_moic_single_chart():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    bars = ax.bar(x, fund_data_df['Net MOIC (x)'], color=colors['net'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}x',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    set_ymax(ax, fund_data_df['Net MOIC (x)'])
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Net MOIC (x)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – Net MOIC (After Fees)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    fig.text(0.02, 0.01, 'Net MOIC is your total multiple on invested capital after all fees and carry.', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'net_moic_single_only'))
    plt.close(fig)

def create_net_moic_chart():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    bars = ax.bar(x, fund_data_df['Net MOIC (x)'], color=colors['net'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}x',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    set_ymax(ax, fund_data_df['Net MOIC (x)'])
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Net MOIC (x)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Net MOIC by Fund (After Fees)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    fig.text(0.02, 0.01, 'Net MOIC reflects your total multiple on invested capital after all fees and carry.', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'net_moic_only'))
    plt.close(fig)

def create_fund3_deployment_timeline():
    years = list(range(2025, 2035))
    committed = 100  # £m
    drawdown = [committed * 0.2 if y < 2030 else 0 for y in years]  # 20% per year for 5 years
    cumulative_drawn = [sum(drawdown[:i+1]) for i in range(len(drawdown))]
    # Simulate distributions: return 25% of committed per year from 2030-2034
    distributions = [0 if y < 2030 else committed * 0.25 for y in years]
    cumulative_returned = [sum(distributions[:i+1]) for i in range(len(distributions))]
    net_cash = [draw - ret for draw, ret in zip(cumulative_drawn, cumulative_returned)]
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    ax.step(years, cumulative_drawn, where='mid', label='Cumulative Deployed', color=colors['gross'], linewidth=2)
    ax.step(years, cumulative_returned, where='mid', label='Cumulative Returned', color=colors['net'], linewidth=2)
    ax.plot(years, net_cash, label='Net Cash Out', color='#888888', linestyle='--', linewidth=2)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('£m', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Fund III – Simulated Capital Deployment & Return Timeline', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='center right', frameon=True, framealpha=0.95, edgecolor='black', fancybox=False)
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'fund3_deployment_timeline'))
    plt.close(fig)

def create_irr_comparison_with_fee_drag():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    width = 0.25
    gross = fund_data_df['Gross IRR (%)']
    net = fund_data_df['Net IRR (%)']
    fee_drag = gross - net
    bars_gross = ax.bar(x - width, gross, width, label='Gross IRR', color=colors['gross'], alpha=0.9, edgecolor='black', linewidth=1)
    bars_drag = ax.bar(x, fee_drag, width, bottom=net, label='Fee Drag', color='#888888', alpha=0.8, edgecolor='black', linewidth=1, hatch='//')
    bars_net = ax.bar(x + width, net, width, label='Net IRR', color=colors['net'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars_gross:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 12), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    for bar in bars_net:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 12), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    # Add extra y-axis buffer for annotation and labels
    set_ymax(ax, list(gross) + list(net), buffer=0.18)
    # Green, dashed, clearly labeled target line for Fund III
    ax.axhline(y=18.0, color='green', linestyle='--', alpha=0.9, linewidth=2)
    ax.annotate('Fund III Target Net IRR', xy=(2, 18.0), xytext=(1.7, 21.5), color='green', fontsize=12, fontweight='bold', arrowprops=dict(arrowstyle='->', color='green', lw=2), bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='green', lw=1, alpha=0.7))
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('IRR (%)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – IRR: Gross, Fee Drag, and Net', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    legend = ax.legend(loc='upper right', frameon=True, framealpha=0.95, edgecolor='black', fancybox=False)
    fig.text(0.02, 0.01, 'Fee drag = difference between Gross and Net IRR (management fees + carry).', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.08, 1, 1])
    fig.subplots_adjust(bottom=0.15, top=0.92, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'irr_comparison_fee_drag'))
    plt.close(fig)

def create_moic_comparison_with_fee_drag():
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=colors['background'])
    x = np.arange(len(fund_data_df['Fund']))
    width = 0.25
    gross = fund_data_df['Gross MOIC (x)']
    net = fund_data_df['Net MOIC (x)']
    fee_drag = gross - net
    bars_gross = ax.bar(x - width, gross, width, label='Gross MOIC', color=colors['gross'], alpha=0.9, edgecolor='black', linewidth=1)
    bars_drag = ax.bar(x, fee_drag, width, bottom=net, label='Fee Drag', color='#888888', alpha=0.8, edgecolor='black', linewidth=1, hatch='//')
    bars_net = ax.bar(x + width, net, width, label='Net MOIC', color=colors['net'], alpha=0.9, edgecolor='black', linewidth=1)
    for bar in bars_gross:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}x', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 8), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    for bar in bars_net:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}x', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 8), textcoords="offset points", ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    set_ymax(ax, list(gross) + list(net))
    # Green, dashed, clearly labeled target line for Fund III
    ax.axhline(y=1.8, color='green', linestyle='--', alpha=0.9, linewidth=2)
    ax.annotate('Fund III Target Net MOIC', xy=(2, 1.8), xytext=(2.1, 2.0), color='green', fontsize=12, fontweight='bold', arrowprops=dict(arrowstyle='->', color='green'))
    ax.set_xlabel('Fund', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('MOIC (x)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Agathos Funds – MOIC: Gross, Fee Drag, and Net', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(fund_data_df['Fund'], fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    legend = ax.legend(loc='upper right', frameon=True, framealpha=0.95, edgecolor='black', fancybox=False)
    fig.text(0.02, 0.01, 'Fee drag = difference between Gross and Net MOIC (management fees + carry).', fontsize=10, style='italic', color='#333333')
    ax.grid(True, alpha=0.2, linestyle='--')
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.subplots_adjust(bottom=0.13, top=0.93, left=0.08, right=0.98)
    save_png_only(fig, os.path.join(current_dir, 'moic_comparison_fee_drag'))
    plt.close(fig)

# Generate all visualizations
create_irr_comparison()
create_moic_comparison()
create_timeline_chart()
create_capital_comparison()
create_gross_irr_chart()
create_net_irr_chart()
create_gross_moic_chart()
create_net_moic_single_chart()
create_net_moic_chart()
create_fund3_deployment_timeline()
create_irr_comparison_with_fee_drag()
create_moic_comparison_with_fee_drag()
