
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import FuncFormatter
import matplotlib.colors as mcolors
from matplotlib.collections import PatchCollection


class TransformerPlotter:
    """
    This class plots the core window.
    """
    @staticmethod
    def darken_color(color, amount=0.5):
        try:
            c = mcolors.cnames[color]
        except:
            c = color
        c = mcolors.to_rgb(c)
        c = mcolors.rgb_to_hsv(c)
        c[2] = c[2] * (1 - amount)
        return mcolors.hsv_to_rgb(c)
    
    def __init__(self, WindowWidth, WindowHeight, BobbinThickness, BobbinType, 
                 PrimaryHeight=0, InterSectionSpacing=0):
        
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_aspect('equal', adjustable='box')
        
        self.WindowWidth = WindowWidth
        self.WindowHeight = WindowHeight
        
        # Desenha os elementos estáticos do fundo
        bobbin_inner_width = WindowWidth - BobbinThickness
        bobbin_inner_height = WindowHeight - 2 * BobbinThickness
        
        self.ax.add_patch(patches.Rectangle((0, 0), WindowWidth, WindowHeight, lw=2, ec='black', fc='none', label='Core Window'))
        self.ax.add_patch(patches.Rectangle((BobbinThickness, BobbinThickness), bobbin_inner_width, bobbin_inner_height, lw=1.5, ls='--', ec='gray', fc='lightgray', alpha=0.3, label='Bobbin Window'))
        
        if BobbinType == 'Split':
            spacer_rect = patches.Rectangle(xy=(BobbinThickness, BobbinThickness + PrimaryHeight), width=bobbin_inner_width, height=InterSectionSpacing,
                                          linewidth=1, linestyle='--', edgecolor='gray', facecolor='lightgray', alpha=0.3, label='Spacing')
            self.ax.add_patch(spacer_rect)

    def plot_geometry(self, coordinates, winding_dims,
                      ConductorDiameter_1, InsulationThickness_1,
                      ConductorDiameter_2, InsulationThickness_2):
        
        if not coordinates:
            print("ERROR: No Geometry Assigned!")
            return

        primary_ins_patches, primary_cop_patches = [], []
        secondary_ins_patches, secondary_cop_patches = [], []

        pitch_1 = ConductorDiameter_1 + 2 * InsulationThickness_1
        pitch_2 = ConductorDiameter_2 + 2 * InsulationThickness_2
        
        for turn in coordinates:
            x, y = turn['x'], turn['y']
            if turn['winding'] == 'primary':
                primary_ins_patches.append(patches.Circle((x, y), pitch_1 / 2))
                primary_cop_patches.append(patches.Circle((x, y), ConductorDiameter_1 / 2))
            else:
                secondary_ins_patches.append(patches.Circle((x, y), pitch_2 / 2))
                secondary_cop_patches.append(patches.Circle((x, y), ConductorDiameter_2 / 2))
        
        primary_color, secondary_color = 'darkorange', 'royalblue' 
        self.ax.add_collection(PatchCollection(primary_ins_patches, facecolor=self.darken_color(primary_color, 0.4), edgecolor='none'))
        self.ax.add_collection(PatchCollection(primary_cop_patches, facecolor=primary_color, edgecolor='none'))
        self.ax.add_collection(PatchCollection(secondary_ins_patches, facecolor=self.darken_color(secondary_color, 0.4), edgecolor='none'))
        self.ax.add_collection(PatchCollection(secondary_cop_patches, facecolor=secondary_color, edgecolor='none'))
        
        rect_style = {'linestyle': ':', 'linewidth': 1.5, 'facecolor': 'none', 'alpha': 0.8}
        if 'primary' in winding_dims:
            p_dims = winding_dims['primary']
            self.ax.add_patch(patches.Rectangle((p_dims['x'], p_dims['y']), p_dims['width'], p_dims['height'],
                                  edgecolor=self.darken_color(primary_color), **rect_style, label='Primary Equivalent Block'))
        if 'secondary' in winding_dims:
            s_dims = winding_dims['secondary']
            self.ax.add_patch(patches.Rectangle((s_dims['x'], s_dims['y']), s_dims['width'], s_dims['height'],
                                  edgecolor=self.darken_color(secondary_color), **rect_style, label='Secondary Equivalent Block'))

    def finalize_and_show(self, title="2D Core Window Plot", instance_name="transformer_plot"):
        self.ax.set_title(title)
        self.ax.set_xlabel('Window Width (mm)')
        self.ax.set_ylabel('Window Height (mm)')
        formatter = FuncFormatter(lambda x, pos: f'{x * 1000:.0f}')
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.yaxis.set_major_formatter(formatter)
        
        x_margin = self.WindowWidth * 0.05
        y_margin = self.WindowHeight * 0.05
        self.ax.set_xlim(-x_margin, self.WindowWidth + x_margin)
        self.ax.set_ylim(-y_margin, self.WindowHeight + y_margin)
        
        self.ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5))
        self.ax.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        #plt.savefig(f'{instance_name}.png', dpi=300, bbox_inches='tight')
        plt.show()
        #print(f"Gráfico salvo como '{instance_name}.png'")

