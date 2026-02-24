from .loader import DimensionLoader
from .calculator import calculate_cut_length, lay_in_cut_length, bushing_cut_length
from .models import Connection, CutRequest

def get_cut_length(loader: DimensionLoader, type_a: str, size_a: str, type_b: str, size_b: str, c2c: float, use_g1_for_type_a: bool = False, use_g1_for_type_b: bool = False):
    """
    Returns (CutRequest, cut_length)
    
    Args:
        loader: DimensionLoader instance
        type_a: Connector type A
        size_a: Size of connector A
        type_b: Connector type B
        size_b: Size of connector B
        c2c: Center-to-center distance
        use_g1_for_type_a: If True, use G1 offset for type_a instead of normal offset
        use_g1_for_type_b: If True, use G1 offset for type_b instead of normal offset
    """
    # Get normal offsets
    offset_a = loader.get_offset(type_a, size_a)
    offset_b = loader.get_offset(type_b, size_b)
    
    # Override with G1 offsets if requested and available
    if use_g1_for_type_a:
        g1_offset_a = loader.get_offset_g1(type_a, size_a)
        if g1_offset_a is not None:
            offset_a = g1_offset_a
    
    if use_g1_for_type_b:
        g1_offset_b = loader.get_offset_g1(type_b, size_b)
        if g1_offset_b is not None:
            offset_b = g1_offset_b

    conn_a = Connection(type_a, size_a, offset_a)
    conn_b = Connection(type_b, size_b, offset_b)
    request = CutRequest(conn_a, conn_b, c2c)

    cut_length = calculate_cut_length(c2c, offset_a, offset_b)
    return request, cut_length


def get_lay_in_cuts(loader: DimensionLoader, type_a: str, size_a: str, type_lay_in: str, size_lay_in: str, 
                    type_b: str, size_b: str, c2c_overall: float, c2c_lay_in: float):
    """
    Returns (CutRequest, (cut1, cut2)) for lay-in style with 3 fittings: A -> Lay-in -> B
    Cut 1: from A to Lay-in
    Cut 2: from Lay-in to B
    """
    offset_a = loader.get_offset(type_a, size_a)
    offset_lay_in = loader.get_offset(type_lay_in, size_lay_in)
    offset_b = loader.get_offset(type_b, size_b)

    conn_a = Connection(type_a, size_a, offset_a)
    conn_lay_in = Connection(type_lay_in, size_lay_in, offset_lay_in)
    conn_b = Connection(type_b, size_b, offset_b)
    request = CutRequest(conn_a, conn_b, c2c_overall)

    cut1, cut2 = lay_in_cut_length(c2c_overall, c2c_lay_in, offset_a, offset_lay_in, offset_b)
    return request, (cut1, cut2)


def get_bushing_cut(loader: DimensionLoader, type_a: str, size_a: str, type_bushing: str, size_bushing: str, 
                    type_b: str, size_b: str, c2c: float):
    """
    Returns (CutRequest, cut_length) for a bushing-included calculation with 3 fittings: A -> Bushing -> B
    """
    offset_a = loader.get_offset(type_a, size_a)
    offset_bushing = loader.get_offset(type_bushing, size_bushing)
    offset_b = loader.get_offset(type_b, size_b)

    conn_a = Connection(type_a, size_a, offset_a)
    conn_bushing = Connection(type_bushing, size_bushing, offset_bushing)
    conn_b = Connection(type_b, size_b, offset_b)
    request = CutRequest(conn_a, conn_b, c2c)

    cut_length = bushing_cut_length(c2c, offset_a, offset_bushing, offset_b)
    return request, cut_length

