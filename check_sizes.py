import pandas as pd
from src.config import SUPPORTED_CONNECTOR_TYPES

df = pd.read_excel('data/PVC Cut Database .xlsx', sheet_name='Database')

for conn_type in SUPPORTED_CONNECTOR_TYPES:
    sizes = df[df['Part'] == conn_type]['Size'].unique()
    sizes_list = sorted([str(s) for s in sizes if pd.notna(s)])
    print(f"{conn_type}: {sizes_list}")
