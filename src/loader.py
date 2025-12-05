import pandas as pd
from .config import OFFSET_COLUMN_MAP, DEFAULT_OFFSET_COLUMN, SHEET_NAME

class DimensionLoader:
    def __init__(self, excel_path: str):
        # read only the Database sheet, ignore others
        self.df = pd.read_excel(excel_path, sheet_name=SHEET_NAME)
        self._normalize_columns()
        self._validate_columns()

    def _normalize_columns(self):
        # Normalize column names: trim + collapse whitespace
        self.df.columns = [c.strip() for c in self.df.columns]

    def _validate_columns(self):
        # We expect at least a Part (connection type) column and a Size column plus the offset columns
        col_candidates = set(name.lower() for name in self.df.columns)
        # Accept multiple possible names for the 'part' and 'size' columns
        part_names = {"part", "part name", "part_type", "connection_type"}
        size_names = {"size", "size (inches)", "size(inches)", "size_inches", "size (in.)", "size_in"}
        found_part = next((c for c in self.df.columns if c.strip().lower() in part_names), None)
        found_size = next((c for c in self.df.columns if c.strip().lower() in size_names), None)

        if found_part is None or found_size is None:
            raise ValueError(
                "Database sheet must contain a 'Part' column and a 'Size' column (e.g. 'Size (inches)')."
            )

        # store canonical column names for later use
        self.part_col = found_part
        self.size_col = found_size

        # Validate that all offset columns exist in the sheet
        all_offset_cols = set(OFFSET_COLUMN_MAP.values()) | {DEFAULT_OFFSET_COLUMN}
        for offset_col in all_offset_cols:
            if offset_col not in self.df.columns:
                raise ValueError(f"Offset column '{offset_col}' not found in sheet. Available columns: {list(self.df.columns)}")

    def _normalize_size_value(self, val):
        # Normalize size values to a consistent string to match user input.
        # Examples in sheet might be numeric 1.5 or "1-1/2" etc.
        if pd.isna(val):
            return ""
        # If numeric, convert to string with no trailing .0 when integer-like
        try:
            # pandas may return numpy types; cast to float first
            v = float(val)
            if v.is_integer():
                return str(int(v))
            return str(v)
        except Exception:
            # fallback: strip whitespace from original string
            return str(val).strip()

    def get_offset(self, conn_type: str, conn_size: str) -> float:
        """
        Find matching offset for a connection type & size.
        Matching rules:
          - conn_type matches (case-insensitive) any substring of the Part column
          - conn_size matches normalized Size column value starting with the user's size input
          - Uses offset column from OFFSET_COLUMN_MAP if defined for the part type, else DEFAULT_OFFSET_COLUMN
        """
        conn_type = conn_type.strip().lower()
        conn_size = conn_size.strip().lower()

        # Get the offset column for this connection type
        offset_col = OFFSET_COLUMN_MAP.get(conn_type.capitalize(), DEFAULT_OFFSET_COLUMN)

        # Build a mask of rows where Part contains the conn_type (case-insensitive)
        matches = []
        for _, row in self.df.iterrows():
            part_val = str(row[self.part_col]).strip().lower()
            size_val_raw = row[self.size_col]
            size_val = self._normalize_size_value(size_val_raw).lower()

            # Check type match (substring)
            if conn_type not in part_val:
                continue

            # Check size match (start-with match or exact)
            if size_val.startswith(conn_size) or conn_size.startswith(size_val):
                # ensure offset exists and is numeric
                offset = row.get(offset_col)
                if pd.notna(offset):
                    try:
                        return float(offset)
                    except Exception:
                        raise ValueError(f"Found non-numeric offset '{offset}' for row: Part={row[self.part_col]}, Size={row[self.size_col]}")
                # if offset is NaN, keep searching
        # if loop finishes with no return:
        raise ValueError(f"No matching entry found for Type='{conn_type}' and Size='{conn_size}' using column '{offset_col}' in sheet '{SHEET_NAME}'.")
