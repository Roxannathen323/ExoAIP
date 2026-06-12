import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import os

class VACGenerator:
    """
    Procedural generator for Visual Approach Charts (VAC) using topography or atmospheric data.
    """

    @staticmethod
    def generate_map(planet_name, archetype, output_path):
        """
        Generates a 2D contour map based on planet archetype.
        """
        # Ensure static/maps directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        plt.switch_backend('Agg')  # Use non-interactive backend
        fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
        
        # Dashboard UI style (Dark)
        # We use a neutral background that looks good in UI but prints decently
        bg_color = '#0a0a0c'
        ax.set_facecolor(bg_color)
        fig.patch.set_facecolor(bg_color)
        
        size = 100
        np.random.seed(sum(map(ord, planet_name))) # Deterministic noise for same planet
        raw_data = np.random.rand(size, size)
        
        is_giant = archetype in ['gas-giant', 'hot-jupiter', 'ice-giant']
        accent_color = '#00f2ff' if is_giant else '#ff9d00'
        
        if is_giant:
            # Atmospheric bands / Storms
            x = np.linspace(0, 10, size)
            y = np.linspace(0, 10, size)
            X, Y = np.meshgrid(x, y)
            # Create wavy horizontal bands
            data = np.sin(Y + gaussian_filter(raw_data, sigma=3) * 2)
            ax.contour(data, levels=15, colors=accent_color, alpha=0.6, linewidths=1.2)
            ax.set_title(f"ATMOSPHERIC ISOBARIC CHART // {planet_name.upper()}", color=accent_color, fontsize=12, pad=20, fontweight='bold')
        else:
            # Topographic contours
            data = gaussian_filter(raw_data, sigma=5)
            ax.contour(data, levels=12, colors=accent_color, alpha=0.8, linewidths=1.5)
            ax.set_title(f"TOPOGRAPHIC APPROACH CHART // {planet_name.upper()}", color=accent_color, fontsize=12, pad=20, fontweight='bold')

        # Decorations: Grid and Scale
        ax.grid(color='white', linestyle='--', alpha=0.1, linewidth=0.5)
        ax.set_xticks(np.linspace(0, size, 5))
        ax.set_yticks(np.linspace(0, size, 5))
        ax.set_xticklabels(['10°W', '5°W', '0°', '5°E', '10°E'], color='#808080', fontsize=8)
        ax.set_yticklabels(['10°S', '5°S', '0°', '5°N', '10°N'], color='#808080', fontsize=8)
        
        # Pseudo Scale Bar
        ax.plot([10, 30], [5, 5], color='white', lw=2)
        ax.text(20, 7, "500 NM", color='white', ha='center', fontsize=8, family='monospace')
        
        # North Arrow
        ax.annotate('N', xy=(90, 95), xytext=(90, 85),
                    arrowprops=dict(facecolor='white', width=1, headwidth=5),
                    color='white', ha='center', fontsize=10, fontweight='bold')

        # Border
        for spine in ax.spines.values():
            spine.set_color(accent_color)
            spine.set_alpha(0.3)

        plt.tight_layout()
        plt.savefig(output_path, facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)
        return output_path

    @staticmethod
    def generate_heightmap(planet_name, archetype):
        """
        Generates a numeric heightmap array for 3D wireframe rendering.
        """
        size = 50 # Lower resolution for wireframe performance
        np.random.seed(sum(map(ord, planet_name)))
        raw_data = np.random.rand(size, size)
        
        is_giant = archetype in ['gas-giant', 'hot-jupiter', 'ice-giant']
        
        if is_giant:
            # Wavy atmospheric bands
            x = np.linspace(0, 10, size)
            y = np.linspace(0, 10, size)
            X, Y = np.meshgrid(x, y)
            data = np.sin(Y + gaussian_filter(raw_data, sigma=2) * 2) * 2.0
        else:
            # Topographic features
            data = gaussian_filter(raw_data, sigma=3) * 15.0
            
        return data.tolist()
