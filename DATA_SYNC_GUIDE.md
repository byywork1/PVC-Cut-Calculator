# Data Synchronization Guide: Updating Connectors & Sizes Across Tabs

## Current Architecture

Your PVC Cut Calculator has a **centralized configuration system** that ensures all tabs automatically stay synchronized. Here's how it works:

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  data/PVC Cut Database.xlsx (Source of Truth)           │
│  - Database sheet: Part, Size, Offset, Offset (G1)      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  src/config.py (Configuration Constants)                │
│  - SUPPORTED_CONNECTOR_TYPES (list)                     │
│  - CONNECTOR_SIZES (dictionary)                         │
│  - OFFSET_COLUMN_MAP (mapping)                          │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ↓           ↓           ↓
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │Standard │ │Lay-in   │ │Bushing  │
    │Cut Tab  │ │Cut Tab  │ │Cut Tab  │
    └─────────┘ └─────────┘ └─────────┘
         │           │           │
         └───────────┼───────────┘
                     ↓
          Jobs Tab (Uses all data)
```

## How Each Tab References the Data

### 1. **Standard Cut Tab** (Line 99-169)
```python
type_a = st.selectbox(
    "Connection Type A",
    SUPPORTED_CONNECTOR_TYPES,  # ← From config.py
    key="type_a"
)

size_a = st.selectbox(
    "Size A",
    CONNECTOR_SIZES.get(type_a, []),  # ← Dynamically populated based on type
    key="size_a"
)
```

### 2. **Lay-in Cut Tab** (Line 198-279)
```python
type_lay_in = st.selectbox(
    "Connector Type",
    SUPPORTED_CONNECTOR_TYPES,  # ← Same reference
    key="type_layin"
)

size_lay_in = st.selectbox(
    "Size",
    CONNECTOR_SIZES.get(type_lay_in, []),  # ← Same reference
    key="size_layin"
)
```

### 3. **Bushing Cut Tab** (Line 281-362)
```python
type_a = st.selectbox(
    "Bushing Type",
    SUPPORTED_CONNECTOR_TYPES,  # ← Same reference
    key="type_a_bushing"
)

size_a = st.selectbox(
    "Size",
    CONNECTOR_SIZES.get(type_a, []),  # ← Same reference
    key="size_a_bushing"
)
```

## How to Add New Connectors or Sizes

### ✅ The Right Way (Permanent)

All tabs will automatically update when you follow this process:

#### Step 1: Update Excel Database
1. Open `data/PVC Cut Database.xlsx`
2. Go to the **Database** sheet
3. Add new row(s):
   - **Part**: Connector type name (must match `SUPPORTED_CONNECTOR_TYPES`)
   - **Size**: The size value (1.5, 2, 2.5, etc. or 2x2x1 format)
   - **Offset**: Offset distance in inches (e.g., 0.5625)
   - **Offset (G1)**: Secondary offset if applicable (optional)

#### Step 2: Update `src/config.py`

**If adding a NEW connector type:**

```python
SUPPORTED_CONNECTOR_TYPES = [
    "Tee (Socket x Socket x Socket)",
    "Tee (Reducing)",
    "Bushing (Spigot x Socket)",
    "Elbow 90(Socket x Socket)",
    "Union (Socket x Socket)",
    "Wye (Socket x Socket x Socket)",  # ← NEW
]

CONNECTOR_SIZES = {
    # ... existing types ...
    "Wye (Socket x Socket x Socket)": ["1.5", "2", "2.5", "3", "4"],  # ← NEW
}
```

**If adding a size to an existing type:**

```python
CONNECTOR_SIZES = {
    "Tee (Socket x Socket x Socket)": ["1.5", "2", "2.5", "3", "4", "5", "6", "8", "10"],  # ← Added "10"
    # ... rest unchanged ...
}
```

#### Step 3: Restart the App
- Save all changes
- Restart the Streamlit app (`streamlit run streamlit_app.py`)
- **All tabs will now have access to the new connector/size** ✅

### ⚠️ What NOT to Do

❌ **Don't** hardcode sizes in individual tabs
❌ **Don't** add sizes only in `streamlit_app.py` without updating `config.py`
❌ **Don't** assume the Excel database will auto-sync without updating `config.py`

## Why This Architecture Ensures Synchronization

### Single Source of Truth
- `src/config.py` is imported in `streamlit_app.py` at line 12
- All tabs reference the **same** `SUPPORTED_CONNECTOR_TYPES` and `CONNECTOR_SIZES` objects
- When you update `config.py` and restart, all tabs get the new data

### Example: Adding Size "5" to Tee (Socket x Socket x Socket)

**Before:**
```python
"Tee (Socket x Socket x Socket)": ["1.5", "2", "2.5", "3", "4", "6", "8"]
```

**After:**
```python
"Tee (Socket x Socket x Socket)": ["1.5", "2", "2.5", "3", "4", "5", "6", "8"]
```

**Result:**
- ✅ Standard Cut Tab - Size A dropdown shows "5"
- ✅ Standard Cut Tab - Size B dropdown shows "5"
- ✅ Lay-in Cut Tab - Shows "5"
- ✅ Bushing Cut Tab - Shows "5"
- ✅ Jobs Tab - Can use connectors with size "5"

**Instant update across ALL tabs!** 🎯

## Session State vs. Permanent Changes

### Session State (Temporary - Current Session Only)
The "Manage Fittings" tab stores changes in session state:
```python
if 'connector_types_modified' not in st.session_state:
    st.session_state.connector_types_modified = list(SUPPORTED_CONNECTOR_TYPES)
```

**This is only for testing.** Changes disappear when you:
- Close the browser
- Restart the app
- Refresh the page

### Permanent Changes
To make changes stick across app restarts:
1. Update `data/PVC Cut Database.xlsx` (Excel file)
2. Update `src/config.py` (Python configuration)
3. Restart the app

## Troubleshooting

### "Size option doesn't appear in all tabs"
**Solution:** 
- Check that the size is in `CONNECTOR_SIZES` in `src/config.py` ✓
- Verify the connector type name matches exactly (case-sensitive) ✓
- Restart the Streamlit app ✓

### "New connector type only works in one tab"
**Solution:**
- Ensure you added it to `SUPPORTED_CONNECTOR_TYPES` ✓
- Added the connector to `CONNECTOR_SIZES` dict ✓
- Both files saved ✓
- App restarted ✓

### "Excel database updated but app doesn't show new data"
**Solution:**
- Did you update `config.py` to match? ✓
- Did you restart the app? ✓
- Try clearing browser cache ✓

## File References

| File | Purpose | Edit When |
|------|---------|-----------|
| `data/PVC Cut Database.xlsx` | Database of all connectors & offsets | Adding new data |
| `src/config.py` | Python constants for dropdowns | Adding new connectors or sizes |
| `src/loader.py` | Loads Excel into memory | Rarely - don't edit |
| `streamlit_app.py` | UI layer | Adding UI elements, not data |

## Summary

✅ **All tabs stay synchronized automatically** by referencing the same `config.py` constants
✅ **Update `src/config.py`** when adding new connectors or sizes
✅ **Update Excel database** to store the actual offset values
✅ **Restart the app** to load the changes
✅ **All tabs instantly show the new options** without code duplication
