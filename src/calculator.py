def calculate_cut_length(c2c: float, offset_a: float, offset_b: float) -> float:
    """
    formula: final cut = C2C - offsetA - offsetB
    Returns the result as a float.
    """
    try:
        c2c_f = float(c2c)
        return c2c_f - float(offset_a) - float(offset_b) 
    except Exception as e:
        raise ValueError(f"Invalid numeric input to calculator: {e}")
    

def lay_in_cut_length(c2c_overall: float, c2c_lay_in: float, offset_a: float, offset_b: float, lay_in_offset: float) -> float:
    """
    formula: Cut 1 = C2C_overall - C2C_lay_in - offsetB 
    formula: Cut 2 = C2C_lay_in - lay_in_offset - offsetA 
    Returns Cut 1 and Cut 2 as floats 
    """
    try:
        c2c_overall_f = float(c2c_overall)
        c2c_lay_in_f = float(c2c_lay_in)

        return c2c_overall_f - c2c_lay_in_f - float(offset_b), c2c_lay_in_f - float(offset_a) - float(lay_in_offset)
    except Exception as e:
        raise ValueError(f"Invalid numeric input to calculator: {e}")
    

def bushing_cut_length(c2c: float, offset_a: float, offset_b: float, bushing: float) -> float:
    """
    formula: final cut = C2C - offsetA - offsetB - bushing
    Returns the result as a float.
    """
    try:
        c2c_f = float(c2c)
        return c2c_f - float(offset_a) - float(offset_b) - bushing 
    except Exception as e:
        raise ValueError(f"Invalid numeric input to calculator: {e}")