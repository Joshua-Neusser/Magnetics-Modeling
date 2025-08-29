def core_window_dimensions(SelectedCore):

    match SelectedCore["family"]:
        case 'ETD':
            WindowWidth  = (SelectedCore["E"] - SelectedCore["F"])/2
            WindowHeight = SelectedCore["D"]*2
    
    return WindowWidth, WindowHeight