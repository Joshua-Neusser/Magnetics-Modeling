import json
from flask import Flask, jsonify, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
import math

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# --- NOVA CLASSE PARA O NÚCLEO SELECIONADO ---
class SelectedCore:
    def __init__(self, core_data_dict):
        """
        Inicializa o objeto do núcleo a partir de um dicionário vindo do frontend.
        """
        self.data = core_data_dict if core_data_dict else {}
        self.name = self.data.get('name', 'N/A')
        self.family = self.data.get('family', 'N/A')
        self.parameters = self.data.get('parameters', {})
        self.dimensions = self.data.get('dimensions', {})

    def get(self, param_name):
        """
        Método unificado para obter qualquer parâmetro ou dimensão do núcleo.
        Retorna o valor numérico ou None se não for encontrado.
        """
        # 1. Procura primeiro nos parâmetros efetivos (ex: 'Ae', 'le', 'Ve')
        if param_name in self.parameters:
            return self.parameters[param_name]
        
        # 2. Se não encontrar, procura nas dimensões (ex: 'A', 'B', 'C')
        if param_name in self.dimensions:
            dim_data = self.dimensions[param_name]
            
            # Se for um dicionário, extrai o melhor valor (nominal ou médio)
            if isinstance(dim_data, dict):
                if 'nominal' in dim_data and dim_data['nominal'] is not None:
                    return dim_data['nominal']
                elif 'minimum' in dim_data and 'maximum' in dim_data:
                    return (dim_data.get('minimum', 0) + dim_data.get('maximum', 0)) / 2
            
            # Se for apenas um número
            elif isinstance(dim_data, (int, float)):
                return dim_data
        
        # 3. Se não encontrar em lugar nenhum
        return None

# --- Funções de Carregamento de Dados e Rotas (Inalteradas) ---
def load_cores():
    cores = []
    with open('cores_shapes_params.ndjson', 'r', encoding='utf-8') as f:
        for line in f:
            cores.append(json.loads(line))
    return cores

CORE_DB = load_cores()

@app.route('/api/families')
def get_families():
    # ... (código inalterado) ...
    unique_families = set(core['family'] for core in CORE_DB)
    return jsonify(sorted(list(unique_families)))

@app.route('/api/models/<string:family>')
def get_models_by_family(family):
    # ... (código inalterado) ...
    models = [core['name'] for core in CORE_DB if core['family'] == family]
    return jsonify(sorted(models))

@app.route('/api/core/<path:model_name>')
def get_core_data(model_name):
    # ... (código inalterado) ...
    for core in CORE_DB:
        if core['name'] == model_name:
            return jsonify(core)
    return jsonify({"error": "Core not found"}), 404

# --- Função Auxiliar (Inalterada) ---
def send_figure_as_json(fig):
    # ... (código inalterado) ...
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    image_data_url = f"data:image/png;base64,{img_base64}"
    return jsonify({'image_src': image_data_url})

# --- Função de Plotagem Refatorada para Usar a Nova Classe ---
def create_winding_plot(inputs):
    # CRIA UMA INSTÂNCIA DA NOVA CLASSE
    core = SelectedCore(inputs.get('currentCore'))
    core_family = core.family

    bobbin = inputs.get('bobbin', {})
    component_type = inputs.get('componentType', 'inductor')
    primary_winding_data = inputs.get('primaryWinding') if component_type == 'transformer' else inputs.get('inductorWinding')
    secondary_winding_data = inputs.get('secondaryWinding') if component_type == 'transformer' else {}
    

#    if not all([E, F, D]):
#        raise ValueError("Dimensões E, F, ou D não encontradas para o núcleo ETD.")



    match core_family:
        case 'etd':
            E = core.get('E') * 1000 if core.get('E') else 0
            F = core.get('F') * 1000 if core.get('F') else 0
            D = core.get('D') * 1000 if core.get('D') else 0
            window_width = (E - F) / 2
            window_height = 2 * D



    # O restante da função continua igual, mas poderia ser ainda mais simplificada
    # usando a classe Core, se necessário.
    fig, ax = plt.subplots(figsize=(3, 4), dpi=300)
    # ... (resto do código de plotagem inalterado) ...
    ax.set_aspect('equal', adjustable='box')
    colors = {"core": "#A9A9A9", "bobbin": "#000080", "primary": "#00BFFF", "secondary": "#FFA500", "inductor": "#90ee90", "background": "#2a475e"}
    fig.patch.set_facecolor(colors['background'])
    ax.set_facecolor(colors['background'])

    core_leg_thickness = 2
    ax.add_patch(patches.Rectangle((-core_leg_thickness, -bobbin.get('thickness', 0)), window_width + 2*core_leg_thickness, window_height + 2*bobbin.get('thickness', 0), facecolor=colors['core'], zorder=1))
    ax.add_patch(patches.Rectangle((0, 0), window_width, window_height, facecolor=colors['background'], zorder=2))
    ax.add_patch(patches.Rectangle((0, 0), window_width, window_height, facecolor=colors['bobbin'], zorder=3))
    
    def _draw_circles(start_x, usable_width, usable_height, winding_data, color_key):
        bobbin_thickness = bobbin.get('thickness', 0)
        wire_diam = winding_data.get('diameter', 0)
        insulation = winding_data.get('insulation', 0)
        total_wire_diam = wire_diam + (2 * insulation)
        turns = winding_data.get('turns', 0)
        if total_wire_diam <= 0 or turns <= 0: return 0
        turns_per_column = math.floor(usable_height / total_wire_diam) if total_wire_diam > 0 else 0
        if turns_per_column == 0: return 0
        num_columns = math.ceil(turns / turns_per_column)
        for i in range(turns):
            column = i // turns_per_column
            row = i % turns_per_column
            center_x = start_x + (total_wire_diam / 2) + (column * total_wire_diam)
            center_y = bobbin_thickness + (total_wire_diam / 2) + (row * total_wire_diam)
            if (center_x + wire_diam / 2) > (start_x + usable_width): break
            ax.add_patch(patches.Circle((center_x, center_y), radius=wire_diam / 2, facecolor=colors[color_key], zorder=4))
        return num_columns * total_wire_diam

    bobbin_thickness = bobbin.get('thickness', 0)
    usable_height = window_height - (2 * bobbin_thickness)
    if component_type == 'inductor':
        usable_width = window_width - (2 * bobbin_thickness)
        _draw_circles(bobbin_thickness, usable_width, usable_height, primary_winding_data, 'inductor')
    elif component_type == 'transformer':
        if bobbin.get('type') == 'normal':
            usable_width = window_width - (2 * bobbin_thickness)
            # Armazenando temporariamente os dados do primário para o cálculo do secundário
            app.config['primary_winding_data_temp'] = primary_winding_data
            primary_width_used = _draw_circles(bobbin_thickness, usable_width, usable_height, primary_winding_data, 'primary')
            secondary_start_x = bobbin_thickness + primary_width_used + bobbin.get('interWindingSpacing', 0)
            secondary_usable_width = usable_width - primary_width_used - bobbin.get('interWindingSpacing', 0)
            _draw_circles(secondary_start_x, secondary_usable_width, usable_height, secondary_winding_data, 'secondary')
        elif bobbin.get('type') == 'split':
            primary_usable_width = bobbin.get('primarySectionSize', 0)
            _draw_circles(bobbin_thickness, primary_usable_width, usable_height, primary_winding_data, 'primary')
            secondary_start_x = bobbin_thickness + primary_usable_width + bobbin.get('interSectionSpacing', 0)
            secondary_usable_width = bobbin.get('secondarySectionSize', 0)
            _draw_circles(secondary_start_x, secondary_usable_width, usable_height, secondary_winding_data, 'secondary')
    
    ax.set_xlim(-window_width * 0.5, window_width * 1.5)
    ax.set_ylim(-window_height * 0.2, window_height * 1.2)
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
    return fig

# --- Rota do Flask (Inalterada) ---
@app.route('/api/generate_plot', methods=['POST'])
def generate_plot():
    # ... (código inalterado) ...
    inputs = request.get_json()
    if not inputs:
        return jsonify({"error": "No input data"}), 400
    component_type = inputs.get('componentType')
    primary = inputs.get('primaryWinding') if component_type == 'transformer' else inputs.get('inductorWinding')
    secondary = inputs.get('secondaryWinding') if component_type == 'transformer' else {}
    if primary.get('wireType') == 'litz' or secondary.get('wireType') == 'litz':
        fig, ax = plt.subplots(figsize=(4, 3), dpi=300)
        ax.text(0.5, 0.5, 'Plot para fio Litz\nainda não implementado.', ha='center', va='center', fontsize=12, color='white')
        ax.set_facecolor('#2a475e')
        fig.patch.set_facecolor('#2a475e')
        ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
        return send_figure_as_json(fig)
    if inputs.get('currentCore', {}).get('family') != 'etd':
        fig, ax = plt.subplots(figsize=(4, 3), dpi=300)
        ax.text(0.5, 0.5, 'Plot disponível\napenas para núcleos ETD.', ha='center', va='center', fontsize=12, color='white')
        ax.set_facecolor('#2a475e')
        fig.patch.set_facecolor('#2a475e')
        ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
        return send_figure_as_json(fig)
    try:
        fig = create_winding_plot(inputs)
        return send_figure_as_json(fig)
    except Exception as e:
        print(f"Error during plot creation: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)