import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file in your project/data folder (adjust filename if needed)
EXCEL_PATH = os.path.join(BASE_DIR, "..", "data", "PVC Cut Database .xlsx")

# Connection types you support
SUPPORTED_TYPES = ["Elbow", "Tee", "Union", "Flange", "Bushing"]

# Offset columns by part type. If a part isn't listed, falls back to DEFAULT_OFFSET_COLUMN
OFFSET_COLUMN_MAP = {
    "Elbow": "G",
    "Tee": "H",
    "Union": "G1",
    "Flange": "H1",
    "Bushing": "L",
}

# Default offset column if part type not found in map
DEFAULT_OFFSET_COLUMN = "G"

# Sheet name to read (explicit per your instruction)
SHEET_NAME = "Database"