def calculate_cut_length(c2c: float, offset_a: float, offset_b: float) -> float:
    """
    Simple formula: final cut = C2C - offsetA - offsetB
    Returns the result as a float.
    """
    try:
        c2c_f = float(c2c)
        return c2c_f - float(offset_a) - float(offset_b)
    except Exception as e:
        raise ValueError(f"Invalid numeric input to calculator: {e}")
