# class calculate:




#     def calculate_lif_cut_length(c2c: float, offset_a: float, offset_b: float, offset_c: float) -> float:
#         try:
#             c2c_f = float(c2c)
#             return c2c_f - float(offset_a) - float(offset_b) - float(offset_c)
#         except Exception as e:
#             raise ValueError(f"Invalid numeric input to calculator: {e}")


    #def calculate_bushing_cut_length(c2c: float, offset_a: float, offset_b: float, offset_c) -> float: 




def calculate_cut_length(c2c: float, offset_a: float, offset_b: float) -> float:
    """
    Simple formula: final cut = C2C - offsetA - offsetB
    Returns the result as a float.
    """
    try:
        c2c_f = float(c2c)
        result = c2c_f - float(offset_a) - float(offset_b)
        rounded = round(result * 16)/ 16.0
        return decimal_to_fraction_16(rounded)
    except Exception as e:
        raise ValueError(f"Invalid numeric input to calculator: {e}")



def decimal_to_fraction_16(decimal: float) -> str:
    """
    Convert a decimal to a fraction with denominator 16.
    Example: 2.3125 returns "2 5/16"
    """
    whole = int(decimal)
    remainder = round((decimal - whole) * 16)
    
    if remainder == 0:
        return str(whole)
    elif remainder == 16:
        return str(whole + 1)
    else:
        return f"{whole} {remainder}/16"
