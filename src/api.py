from .loader import DimensionLoader
from .calculator import calculate_cut_length
from .models import Connection, CutRequest

def get_cut_length(loader: DimensionLoader, type_a: str, size_a: str, type_b: str, size_b: str, c2c: float):
    """
    Returns (CutRequest, cut_length)
    """
    offset_a = loader.get_offset(type_a, size_a)
    offset_b = loader.get_offset(type_b, size_b)

    conn_a = Connection(type_a, size_a, offset_a)
    conn_b = Connection(type_b, size_b, offset_b)
    request = CutRequest(conn_a, conn_b, c2c)

    cut_length = calculate_cut_length(c2c, offset_a, offset_b)
    return request, cut_length
