import json
from flask import Flask, jsonify
from flask_cors import CORS

# --- Initial Setup ---

app = Flask(__name__)
# Allows the frontend to make requests to this backend
CORS(app)

# --- Data Loading ---

def load_cores():
    """Reads the .ndjson file and loads the cores into a list of dictionaries."""
    cores = []
    with open('cores_shapes_params.ndjson', 'r', encoding='utf-8') as f:
        for line in f:
            # Each line is a complete JSON object
            cores.append(json.loads(line))
    return cores

# Load all cores into memory when the server starts
CORE_DB = load_cores()

# --- API Route Definitions ---

@app.route('/api/families')
def get_families():
    """Returns a list of all unique core families."""
    # Using a 'set' ensures each family name appears only once
    unique_families = set(core['family'] for core in CORE_DB)
    return jsonify(sorted(list(unique_families)))

@app.route('/api/models/<string:family>')
def get_models_by_family(family):
    """Returns a list of models for a specific family."""
    models = [
        core['name'] for core in CORE_DB if core['family'] == family
    ]
    return jsonify(sorted(models))

@app.route('/api/core/<path:model_name>')
def get_core_data(model_name):
    """Returns all data for a specific core by its name."""
    for core in CORE_DB:
        if core['name'] == model_name:
            return jsonify(core) # Returns the complete core JSON object
            
    return jsonify({"error": "Core not found"}), 404

# --- Running the Server ---

if __name__ == '__main__':
    # Runs the server in debug mode, which auto-reloads on code changes.
    app.run(debug=True)