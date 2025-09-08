import numpy as np

class WindingMaker:
    """
    This class performs a fit check of the defined windings in the core window considering the defined bobbin parameters
    It also calculates the coordinates of each turn, as well as the position and dimensions of the equivalent winding blocks.
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
            print("ERROR: The windings dont fit!")

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
            
            winding_dims['primary'] = {'x': BobbinThickness + InsulationThickness_1, 'y': BobbinThickness + InsulationThickness_1, 'width': (NumberOfTurns_1 / turns_per_layer_1) * pitch_1 - 2*InsulationThickness_1, 'height': turns_per_layer_1 * pitch_1 - 2*InsulationThickness_1}
            winding_dims['secondary'] = {'x': x_start_2 + InsulationThickness_2, 'y': y_start_2 + InsulationThickness_2, 'width': (NumberOfTurns_2 / turns_per_layer_2) * pitch_2 - 2*InsulationThickness_2, 'height': turns_per_layer_2 * pitch_2 - 2*InsulationThickness_2}

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
                
            winding_dims['primary'] = {'x': BobbinThickness + InsulationThickness_1, 'y': y_start_p + InsulationThickness_1, 'width': (NumberOfTurns_1 / turns_per_layer_p) * pitch_1 - 2*InsulationThickness_1, 'height': height_occupied_p - 2*InsulationThickness_1}
            winding_dims['secondary'] = {'x': BobbinThickness + InsulationThickness_2, 'y': y_start_s + InsulationThickness_2, 'width': (NumberOfTurns_2 / turns_per_layer_s) * pitch_2 - 2*InsulationThickness_2, 'height': height_occupied_s - 2*InsulationThickness_2}

        return coordinates, winding_dims
    