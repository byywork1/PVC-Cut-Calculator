import pandas as pd
from .config import OFFSET_COLUMN, SHEET_NAME, OFFSET_COLUMN_G1, SUPPORTED_CONNECTOR_TYPES
from fractions import Fraction

class DimensionLoader:
    def __init__(self, excel_path: str, session_offsets: dict = None):
        # read only the Database sheet, ignore others
        self.df = pd.read_excel(excel_path, sheet_name=SHEET_NAME)
        self._normalize_columns()
        self._validate_columns()
        self._load_connector_map()
        # Store session offsets for newly added connectors (from session state)
        self.session_offsets = session_offsets or {}

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

        # Validate that offset columns exist in the sheet
        if OFFSET_COLUMN not in self.df.columns:
            raise ValueError(f"Offset column '{OFFSET_COLUMN}' not found in sheet. Available columns: {list(self.df.columns)}")

    def _load_connector_map(self):
        """
        Build a mapping of exact connector type names to database rows.
        Creates a dict: {"Tee (SocketxSocketxSocket)": [row_data, ...], ...}
        """
        self.connector_map = {}
        for conn_type in SUPPORTED_CONNECTOR_TYPES:
            matching_rows = []
            for idx, row in self.df.iterrows():
                part_val = str(row[self.part_col]).strip()
                if part_val == conn_type:
                    matching_rows.append(row)
            self.connector_map[conn_type] = matching_rows

    def _normalize_size_value(self, val):
        # Normalize size values to match user input.
        # Can be numeric (1.5, 2, etc.) or text format (1.5x1.5x0.5, 2x2x1, etc.)
        if pd.isna(val):
            return ""
        val_str = str(val).strip()
        
        # For text formats like "1.5x1.5x0.5", return as-is
        if 'x' in val_str.lower():
            return val_str.lower()
        
        # For numeric values, convert with no trailing .0 when integer-like
        try:
            v = float(val_str)
            if v.is_integer():
                return str(int(v))
            return str(v)
        except ValueError:
            return val_str.lower()

    def _parse_offset_value(self, val):
        """
        Parse offset value which may be a float, int, or fraction string like '15/32'.
        Returns float or raises ValueError.
        """
        if pd.isna(val):
            return None
        try:
            # Try direct float conversion first
            return float(val)
        except (ValueError, TypeError):
            # Try parsing as fraction string
            try:
                frac = Fraction(str(val).strip())
                return float(frac)
            except (ValueError, ZeroDivisionError):
                raise ValueError(f"Cannot convert '{val}' to numeric offset")

    def get_offset(self, conn_type: str, conn_size: str) -> float:
        """
        Find matching offset for an exact connector type and size.
        
        Args:
            conn_type: Exact connector type from SUPPORTED_CONNECTOR_TYPES or session
            conn_size: Numeric or text size to match exactly
            
        Returns:
            float: The offset value from the database or session
            
        Raises:
            ValueError: If connector type is not supported or no matching size found
        """
        # First, check session offsets for newly added connectors
        offset_key = f"{conn_type}|{conn_size}"
        if offset_key in self.session_offsets:
            offset_data = self.session_offsets[offset_key]
            if offset_data and 'offset' in offset_data:
                return offset_data['offset']
        
        # Validate connector type exists in our supported list OR in connector_map
        if conn_type not in SUPPORTED_CONNECTOR_TYPES and conn_type not in self.connector_map:
            raise ValueError(
                f"Unsupported connector type: '{conn_type}'. "
                f"Supported types: {SUPPORTED_CONNECTOR_TYPES}"
            )

        # Get the offset column for this connection type
        offset_col = OFFSET_COLUMN

        # Normalize the size input for comparison
        normalized_input_size = self._normalize_size_value(conn_size)

        # Get rows that match this exact connector type
        matching_rows = self.connector_map.get(conn_type, [])
        if not matching_rows:
            raise ValueError(
                f"No database entries found for connector type '{conn_type}'"
            )

        # Find exact size match within the matching rows
        for row in matching_rows:
            size_val_raw = row[self.size_col]
            normalized_db_size = self._normalize_size_value(size_val_raw)

            if normalized_db_size == normalized_input_size:
                offset = row.get(offset_col)
                if pd.notna(offset):
                    try:
                        return self._parse_offset_value(offset)
                    except ValueError:
                        raise ValueError(
                            f"Invalid offset value '{offset}' for {conn_type} Size={row[self.size_col]}"
                        )

        # No exact size match found
        available_sizes = [
            self._normalize_size_value(row[self.size_col]) 
            for row in matching_rows
        ]
        raise ValueError(
            f"No matching size '{conn_size}' for connector '{conn_type}'. "
            f"Available sizes: {available_sizes}"
        )

    def get_offset_g1(self, conn_type: str, conn_size: str) -> float:
        """
        Find matching G1 offset for an exact connector type and size.
        
        Args:
            conn_type: Exact connector type from SUPPORTED_CONNECTOR_TYPES or session
            conn_size: Numeric or text size to match exactly
            
        Returns:
            float: The G1 offset value from the database or session, or None if not available
            
        Raises:
            ValueError: If connector type is not supported or no matching size found
        """
        # First, check session offsets for newly added connectors
        offset_key = f"{conn_type}|{conn_size}"
        if offset_key in self.session_offsets:
            offset_data = self.session_offsets[offset_key]
            if offset_data and 'g1_offset' in offset_data:
                g1_value = offset_data['g1_offset']
                if g1_value and g1_value > 0:
                    return g1_value
        
        # Validate connector type exists in our supported list OR in connector_map
        if conn_type not in SUPPORTED_CONNECTOR_TYPES and conn_type not in self.connector_map:
            raise ValueError(
                f"Unsupported connector type: '{conn_type}'. "
                f"Supported types: {SUPPORTED_CONNECTOR_TYPES}"
            )

        # Normalize the size input for comparison
        normalized_input_size = self._normalize_size_value(conn_size)

        # Get rows that match this exact connector type
        matching_rows = self.connector_map.get(conn_type, [])
        if not matching_rows:
            raise ValueError(
                f"No database entries found for connector type '{conn_type}'"
            )

        # Find exact size match within the matching rows
        for row in matching_rows:
            size_val_raw = row[self.size_col]
            normalized_db_size = self._normalize_size_value(size_val_raw)

            if normalized_db_size == normalized_input_size:
                # Try to get G1 offset column if it exists
                if OFFSET_COLUMN_G1 in self.df.columns:
                    g1_offset = row.get(OFFSET_COLUMN_G1)
                    if pd.notna(g1_offset):
                        try:
                            return self._parse_offset_value(g1_offset)
                        except ValueError:
                            return None
                return None

        # No exact size match found
        return None
