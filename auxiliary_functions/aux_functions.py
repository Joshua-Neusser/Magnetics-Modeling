
import numpy as np

class WindingMaker:
    """
    Pilar 1: O CALCULISTA.
    Versão completa e corrigida. Calcula coordenadas e dimensões para AMBOS os modos.
    """
    def __init__(self, WindowWidth, WindowHeight, BobbinType, BobbinThickness,
                 NumberOfTurns_1, NumberOfTurns_2,
                 ConductorDiameter_1, InsulationThickness_1,
                 ConductorDiameter_2, InsulationThickness_2,
                 WindingsSpacing=0, PrimaryHeight=0, InterSectionSpacing=0, SecondaryHeight=0,
                 SecondaryYAlign='bottom', PrimaryYAlignSplit='bottom', SecondaryYAlignSplit='bottom'):
        
        self.coordinates, self.winding_dims = self._calculate_geometry(
            WindowWidth, WindowHeight, BobbinType, BobbinThickness,
            NumberOfTurns_1, NumberOfTurns_2, ConductorDiameter_1, InsulationThickness_1,
            ConductorDiameter_2, InsulationThickness_2, WindingsSpacing, PrimaryHeight, 
            InterSectionSpacing, SecondaryHeight, SecondaryYAlign, 
            PrimaryYAlignSplit, SecondaryYAlignSplit
        )
        if not self.coordinates:
            print("WARNING: The Windings Didnt Fit!")

    def get_all_coordinates(self):
        return self.coordinates

    def get_equivalent_dims(self):
        return self.winding_dims

    def _calculate_geometry(self, WindowWidth, WindowHeight, BobbinType, BobbinThickness,
                            NumberOfTurns_1, NumberOfTurns_2, ConductorDiameter_1, InsulationThickness_1,
                            ConductorDiameter_2, InsulationThickness_2, WindingsSpacing, PrimaryHeight, 
                            InterSectionSpacing, SecondaryHeight, SecondaryYAlign, 
                            PrimaryYAlignSplit, SecondaryYAlignSplit):
        
        pitch_1 = ConductorDiameter_1 + 2 * InsulationThickness_1
        pitch_2 = ConductorDiameter_2 + 2 * InsulationThickness_2
        bobbin_inner_width = WindowWidth - BobbinThickness
        bobbin_inner_height = WindowHeight - 2 * BobbinThickness
        coordinates = []
        winding_dims = {}

        if BobbinType == 'Normal':
            turns_per_layer_1 = int(bobbin_inner_height / pitch_1)
            if turns_per_layer_1 == 0: return [], {}
            num_layers_1 = np.ceil(NumberOfTurns_1 / turns_per_layer_1)
            width_1 = num_layers_1 * pitch_1
            turns_per_layer_2 = int(bobbin_inner_height / pitch_2)
            if turns_per_layer_2 == 0: return [], {}
            num_layers_2 = np.ceil(NumberOfTurns_2 / turns_per_layer_2)
            width_2 = num_layers_2 * pitch_2
            total_width_needed = width_1 + WindingsSpacing + width_2
            if total_width_needed > bobbin_inner_width: return [], {}
            
            for i in range(NumberOfTurns_1):
                layer, turn_in_layer = divmod(i, turns_per_layer_1)
                x_pos = BobbinThickness + (layer * pitch_1) + pitch_1 / 2
                y_pos = BobbinThickness + (turn_in_layer * pitch_1) + pitch_1 / 2
                coordinates.append({'x': x_pos, 'y': y_pos, 'winding': 'primary', 'turn': i + 1})
            
            y_start_2 = BobbinThickness
            if SecondaryYAlign == 'center':
                actual_turns = min(NumberOfTurns_2, turns_per_layer_2)
                height_occupied = actual_turns * pitch_2
                y_start_2 = BobbinThickness + (bobbin_inner_height - height_occupied) / 2
            x_start_2 = BobbinThickness + (num_layers_1 * pitch_1) + WindingsSpacing
            for i in range(NumberOfTurns_2):
                layer, turn_in_layer = divmod(i, turns_per_layer_2)
                x_pos = x_start_2 + (layer * pitch_2) + pitch_2 / 2
                y_pos = y_start_2 + (turn_in_layer * pitch_2) + pitch_2 / 2
                coordinates.append({'x': x_pos, 'y': y_pos, 'winding': 'secondary', 'turn': i + 1})
            
            winding_dims['primary'] = {'x': BobbinThickness, 'y': BobbinThickness, 'width': (NumberOfTurns_1 / turns_per_layer_1) * pitch_1, 'height': turns_per_layer_1 * pitch_1}
            winding_dims['secondary'] = {'x': x_start_2, 'y': y_start_2, 'width': (NumberOfTurns_2 / turns_per_layer_2) * pitch_2, 'height': turns_per_layer_2 * pitch_2}

        elif BobbinType == 'Split':
            if PrimaryHeight + InterSectionSpacing + SecondaryHeight > bobbin_inner_height: return [], {}
            
            turns_per_layer_p = int(PrimaryHeight / pitch_1)
            if turns_per_layer_p == 0: return [], {}
            num_layers_1 = np.ceil(NumberOfTurns_1 / turns_per_layer_p)
            width_1 = num_layers_1 * pitch_1
            if width_1 > bobbin_inner_width: return [], {}

            turns_per_layer_s = int(SecondaryHeight / pitch_2)
            if turns_per_layer_s == 0: return [], {}
            num_layers_2 = np.ceil(NumberOfTurns_2 / turns_per_layer_s)
            width_2 = num_layers_2 * pitch_2
            if width_2 > bobbin_inner_width: return [], {}

            v_turns_p = min(NumberOfTurns_1, turns_per_layer_p) if NumberOfTurns_1 <= turns_per_layer_p else turns_per_layer_p
            height_occupied_p = v_turns_p * pitch_1
            empty_space_p = PrimaryHeight - height_occupied_p
            y_start_p = BobbinThickness
            if PrimaryYAlignSplit == 'center': y_start_p = BobbinThickness + empty_space_p / 2
            elif PrimaryYAlignSplit == 'top': y_start_p = BobbinThickness + empty_space_p
            for i in range(NumberOfTurns_1):
                layer, turn_in_layer = divmod(i, turns_per_layer_p)
                x_pos = BobbinThickness + (layer * pitch_1) + pitch_1 / 2
                y_pos = y_start_p + (turn_in_layer * pitch_1) + pitch_1 / 2
                coordinates.append({'x': x_pos, 'y': y_pos, 'winding': 'primary', 'turn': i + 1})

            v_turns_s = min(NumberOfTurns_2, turns_per_layer_s) if NumberOfTurns_2 <= turns_per_layer_s else turns_per_layer_s
            height_occupied_s = v_turns_s * pitch_2
            empty_space_s = SecondaryHeight - height_occupied_s
            y_start_s = BobbinThickness + PrimaryHeight + InterSectionSpacing
            if SecondaryYAlignSplit == 'center': y_start_s += empty_space_s / 2
            elif SecondaryYAlignSplit == 'top': y_start_s += empty_space_s
            for i in range(NumberOfTurns_2):
                layer, turn_in_layer = divmod(i, turns_per_layer_s)
                x_pos = BobbinThickness + (layer * pitch_2) + pitch_2 / 2
                y_pos = y_start_s + (turn_in_layer * pitch_2) + pitch_2 / 2
                coordinates.append({'x': x_pos, 'y': y_pos, 'winding': 'secondary', 'turn': i + 1})
                
            winding_dims['primary'] = {'x': BobbinThickness, 'y': y_start_p, 'width': (NumberOfTurns_1 / turns_per_layer_p) * pitch_1, 'height': height_occupied_p}
            winding_dims['secondary'] = {'x': BobbinThickness, 'y': y_start_s, 'width': (NumberOfTurns_2 / turns_per_layer_s) * pitch_2, 'height': height_occupied_s}

        return coordinates, winding_dims
    






import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import FuncFormatter
import matplotlib.colors as mcolors
from matplotlib.collections import PatchCollection


class TransformerPlotter:
    """
    Pilar 2: O ARTISTA. Versão com a correção de enquadramento (zoom).
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
        
        # --- AJUSTE 1: Guardar as dimensões da janela ---
        self.WindowWidth = WindowWidth
        self.WindowHeight = WindowHeight
        
        # Desenha os elementos estáticos do fundo
        bobbin_inner_width = WindowWidth - BobbinThickness
        bobbin_inner_height = WindowHeight - 2 * BobbinThickness
        
        self.ax.add_patch(patches.Rectangle((0, 0), WindowWidth, WindowHeight, lw=2, ec='black', fc='none', label='Janela do Núcleo'))
        self.ax.add_patch(patches.Rectangle((BobbinThickness, BobbinThickness), bobbin_inner_width, bobbin_inner_height, lw=1.5, ls='--', ec='gray', fc='lightgray', alpha=0.3, label='Área Útil'))
        
        if BobbinType == 'Split':
            spacer_rect = patches.Rectangle(xy=(BobbinThickness, BobbinThickness + PrimaryHeight), width=bobbin_inner_width, height=InterSectionSpacing,
                                          linewidth=1, linestyle='--', edgecolor='gray', facecolor='lightgray', alpha=0.5, label='Divisória')
            self.ax.add_patch(spacer_rect)

    def plot_geometry(self, coordinates, winding_dims,
                      ConductorDiameter_1, InsulationThickness_1,
                      ConductorDiameter_2, InsulationThickness_2):
        
        # ... (Este método inteiro permanece o mesmo, está correto) ...
        if not coordinates:
            print("Nenhuma geometria para plotar.")
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
        
        primary_color, secondary_color = 'royalblue', 'darkorange'
        self.ax.add_collection(PatchCollection(primary_ins_patches, facecolor=self.darken_color(primary_color, 0.4), edgecolor='none', label='Isolação Primária'))
        self.ax.add_collection(PatchCollection(primary_cop_patches, facecolor=primary_color, edgecolor='none', label='Cobre Primário'))
        self.ax.add_collection(PatchCollection(secondary_ins_patches, facecolor=self.darken_color(secondary_color, 0.4), edgecolor='none', label='Isolação Secundária'))
        self.ax.add_collection(PatchCollection(secondary_cop_patches, facecolor=secondary_color, edgecolor='none', label='Cobre Secundário'))
        
        rect_style = {'linestyle': ':', 'linewidth': 1.5, 'facecolor': 'none', 'alpha': 0.8}
        if 'primary' in winding_dims:
            p_dims = winding_dims['primary']
            self.ax.add_patch(patches.Rectangle((p_dims['x'], p_dims['y']), p_dims['width'], p_dims['height'],
                                  edgecolor=self.darken_color(primary_color), **rect_style, label='Área Eq. Primário'))
        if 'secondary' in winding_dims:
            s_dims = winding_dims['secondary']
            self.ax.add_patch(patches.Rectangle((s_dims['x'], s_dims['y']), s_dims['width'], s_dims['height'],
                                  edgecolor=self.darken_color(secondary_color), **rect_style, label='Área Eq. Secundário'))

    def finalize_and_show(self, title="2D Core Window Plot", instance_name="transformer_plot"):
        self.ax.set_title(title)
        self.ax.set_xlabel('Largura da Janela (mm)')
        self.ax.set_ylabel('Altura da Janela (mm)')
        formatter = FuncFormatter(lambda x, pos: f'{x * 1000:.0f}')
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.yaxis.set_major_formatter(formatter)
        
        # --- AJUSTE 2: Usar os valores guardados para definir o zoom corretamente ---
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

