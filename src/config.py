import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the Excel file in your project/data folder (adjust filename if needed)
EXCEL_PATH = os.path.join(BASE_DIR, "..", "data", "PVC Cut Database .xlsx")

# Exact connector types for dropdown menu - these will be matched exactly in the database
SUPPORTED_CONNECTOR_TYPES = [
    "Tee (Socket x Socket x Socket)",
    "Tee (Reducing)",
    "Bushing (Spigot x Socket)",
    "Elbow 90(Socket x Socket)",
    "Union (Socket x Socket)",
]

# Available sizes for each connector type (from database)
CONNECTOR_SIZES = {
    "Tee (Socket x Socket x Socket)": ["1.5", "2", "2.5", "3", "4", "5", "6", "8"],
    "Tee (Reducing)": [
        "1.5x1.5x0.5", "1.5x1.5x0.75", "1.5x1.5x1", "1.5x1.5x1.25",
        "2x2x0.5", "2x2x0.75", "2x2x1", "2x2x1.25", "2x2x1.5", "2x2x4",
        "2.5x2.5x0.5", "2.5x2.5x0.75", "2.5x2.5x1", "2.5x2.5x1.25", "2.5x2.5x1.5", "2.5x2.5x2",
        "3x3x0.5", "3x3x0.75", "3x3x1", "3x3x1.25", "3x3x1.5", "3x3x2", "3x3x2.5",
        "4x4x0.5", "4x4x0.75", "4x4x1", "4x4x1.25", "4x4x1.5", "4x4x2", "4x4x2.5", "4x4x3",
        "6x6x0.5", "6x6x0.75", "6x6x1", "6x6x1.25", "6x6x1.5", "6x6x2", "6x6x2.5", "6x6x3", "6x6x4",
        "8x8x0.5", "8x8x1", "8x8x2", "8x8x2.5", "8x8x3", "8x8x4", "8x8x6",
    ],
    "Bushing (Spigot x Socket)": [
        "1.5x0.5", "1.5x0.75", "1.5x1", "1.5x1.25",
        "2x0.5", "2x0.75", "2x1", "2x1.25", "2x1.5",
        "2.5x0.5", "2.5x0.75", "2.5x1", "2.5x1.25", "2.5x1.5", "2.5x2",
        "3x0.5", "3x0.75", "3x1", "3x1.25", "3x1.5", "3x2", "3x2.5",
        "4x0.5", "4x0.75", "4x1", "4x1.25", "4x1.5", "4x2", "4x2.5", "4x3",
        "5x2", "5x3", "5x4",
        "6x0.75", "6x1", "6x1.25", "6x1.5", "6x2", "6x2.5", "6x3", "6x4", "6x5",
        "8x1.5", "8x2", "8x3", "8x4", "8x6",
    ],
    "Elbow 90(Socket x Socket)": ["1.5", "2", "2.5", "3", "4", "5", "6", "8"],
    "Union (Socket x Socket)": ["1.5", "2", "2.5", "3", "4"],
}

# Offset columns by connector type
OFFSET_COLUMN_MAP = {
    "Tee (Socket x Socket x Socket)": "Offset",
    "Tee (Reducing)": "Offset",
    "Bushing (Spigot x Socket)": "Offset",
    "Elbow 90(Socket x Socket)": "Offset",
    "Union (Socket x Socket)": "Offset",
}

# Alternative offset column (G1) - used for secondary offset when available
OFFSET_COLUMN_G1 = "Offset (G1)"

# Default offset column if part type not found in map
DEFAULT_OFFSET_COLUMN = "Offset"

# Sheet name to read (explicit per your instruction)
SHEET_NAME = "Database"
