import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# CloudMundi brand colors
CLOUDMUNDI_TEAL = '#2DD4BF'
CLOUDMUNDI_NAVY = '#1E3A8A' 
CLOUDMUNDI_DARK = '#0F172A'
CLOUDMUNDI_LIGHT = '#F1F5F9'
CLOUDMUNDI_ACCENT = '#06B6D4'

def create_feature_comparison_matrix():
    """Create a professional feature comparison matrix"""
    
    # Data setup
    platforms = ['eToro', 'Revolut', 'Robinhood']
    features = [
        'Bitcoin Trading', 'Crypto Wallet', 'Commodities', 
        'S&P 500 Access', 'Bond ETFs', 'Social Trading',
        'Educational Tools', 'Mobile Experience', 'Global Access'
    ]
    
    # Scoring matrix (0-3: None, Limited, Good, Excellent)
    scores = np.array([
        [3, 3, 3, 3, 2, 3, 3, 2, 3],  # eToro
        [2, 1, 1, 3, 0, 0, 1, 3, 2],  # Revolut
        [2, 1, 0, 3, 2, 0, 3, 3, 1]   # Robinhood
    ])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('white')
    
    # Create custom colormap
    colors = ['#EF4444', '#F59E0B', '#10B981', '#059669']
    n_bins = 4
    cmap = sns.blend_palette(colors, n_colors=n_bins, as_cmap=True)
    
    # Create heatmap
    im = ax.imshow(scores, cmap=cmap, aspect='auto', vmin=0, vmax=3)
    
    # Set ticks
    ax.set_xticks(np.arange(len(features)))
    ax.set_yticks(np.arange(len(platforms)))
    ax.set_xticklabels(features, rotation=45, ha='right', fontsize=12)
    ax.set_yticklabels(platforms, fontsize=14, fontweight='bold')
    
    # Add text annotations
    status_text = ['Not Available', 'Limited', 'Good', 'Excellent']
    for i in range(len(platforms)):
        for j in range(len(features)):
            text = ax.text(j, i, status_text[scores[i, j]], 
                          ha="center", va="center", 
                          color="white" if scores[i, j] < 2 else "black",
                          fontsize=10, fontweight='bold')
    
    # Styling
    ax.set_title('Platform Feature Comparison Matrix\n', 
                fontsize=22, fontweight='bold', color=CLOUDMUNDI_NAVY, pad=20)
    ax.text(0.5, 0.98, 'Comprehensive capability assessment across key trading features', 
            transform=ax.transAxes, ha='center', va='top', fontsize=12, 
            color=CLOUDMUNDI_DARK, alpha=0.8)
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add grid
    ax.set_xticks(np.arange(len(features))-.5, minor=True)
    ax.set_yticks(np.arange(len(platforms))-.5, minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Feature Availability', rotation=270, labelpad=20, 
                   fontsize=12, fontweight='bold')
    cbar.set_ticks([0, 1, 2, 3])
    cbar.set_ticklabels(status_text)
    
    # CloudMundi branding
    ax.text(0.99, -0.15, 'CloudMundi', transform=ax.transAxes, 
            ha='right', va='bottom', fontsize=10, color=CLOUDMUNDI_NAVY, 
            alpha=0.7, style='italic')
    
    plt.tight_layout()
    plt.savefig('platform_feature_matrix.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

if __name__ == "__main__":
    print("🎨 Creating platform comparison matrix...")
    create_feature_comparison_matrix()
    print("✅ Feature matrix created successfully!") 