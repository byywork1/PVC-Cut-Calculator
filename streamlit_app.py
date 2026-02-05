import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import os
import pandas as pd
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.loader import DimensionLoader
from src.api import get_cut_length, get_lay_in_cuts, get_bushing_cut
from src.config import EXCEL_PATH, SUPPORTED_CONNECTOR_TYPES, CONNECTOR_SIZES
from src.main import decimal_to_fraction_16ths

# ============================================================================
# HELPER FUNCTIONS FOR PERMANENT DATABASE STORAGE
# ============================================================================

def save_connector_to_excel(connector_type: str, sizes_list: list):
    """Save new connector type and sizes to Excel database."""
    try:
        # Read existing Excel file
        df = pd.read_excel(EXCEL_PATH, sheet_name="Database")
        
        # Create new rows for each size
        new_rows = []
        for size_data in sizes_list:
            new_row = {
                'Part': connector_type,
                'Size': size_data['size'],
                'Offset': size_data['offset'],
                'Offset (G1)': size_data['g1_offset'] if size_data['g1_offset'] > 0 else None
            }
            new_rows.append(new_row)
        
        # Append new rows to dataframe
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        
        # Save back to Excel
        with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Database', index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving to Excel: {e}")
        return False

def update_config_py(connector_type: str, sizes_list: list, image_filename: str = None):
    """Update src/config.py with new connector type, sizes, and optionally image mapping."""
    try:
        config_path = Path(__file__).parent / "src" / "config.py"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update SUPPORTED_CONNECTOR_TYPES
        if f'"{connector_type}"' not in content:
            # Find the SUPPORTED_CONNECTOR_TYPES list and add the new type
            old_supported = 'SUPPORTED_CONNECTOR_TYPES = [\n    "Tee (Socket x Socket x Socket)",\n    "Tee (Reducing)",\n    "Bushing (Spigot x Socket)",\n    "Elbow 90(Socket x Socket)",\n    "Union (Socket x Socket)",\n]'
            new_supported = f'SUPPORTED_CONNECTOR_TYPES = [\n    "Tee (Socket x Socket x Socket)",\n    "Tee (Reducing)",\n    "Bushing (Spigot x Socket)",\n    "Elbow 90(Socket x Socket)",\n    "Union (Socket x Socket)",\n    "{connector_type}",\n]'
            content = content.replace(old_supported, new_supported)
        
        # Update CONNECTOR_SIZES
        sizes_str = str([s['size'] for s in sizes_list])
        
        # Find where CONNECTOR_SIZES dict ends and add new entry
        if f'"{connector_type}"' not in content or 'CONNECTOR_SIZES' in content:
            # Add to CONNECTOR_SIZES dict
            old_ending = '    "Union (Socket x Socket)": ["1.5", "2", "2.5", "3", "4"],\n}'
            new_ending = f'    "Union (Socket x Socket)": ["1.5", "2", "2.5", "3", "4"],\n    "{connector_type}": {sizes_str},\n}}'
            content = content.replace(old_ending, new_ending)
        
        # Update CONNECTOR_IMAGE_MAP if image provided
        if image_filename:
            old_image_ending = '    "Union (Socket x Socket)": "union.png",\n}'
            new_image_ending = f'    "Union (Socket x Socket)": "union.png",\n    "{connector_type}": "{image_filename}",\n}}'
            content = content.replace(old_image_ending, new_image_ending)
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        st.error(f"Error updating config.py: {e}")
        return False

def delete_connector_image(connector_type: str):
    """Delete image file associated with a connector type from images/ folder."""
    try:
        from src.config import CONNECTOR_IMAGE_MAP
        
        # Get the image filename from config
        image_filename = CONNECTOR_IMAGE_MAP.get(connector_type)
        
        if image_filename:
            images_dir = Path(__file__).parent / "images"
            image_path = images_dir / image_filename
            
            # Delete the image file if it exists
            if image_path.exists():
                image_path.unlink()
                return True
        
        # If no image mapping or file doesn't exist, still return True (not an error)
        return True
    except Exception as e:
        st.warning(f"Could not delete image file: {e}")
        return True  # Still continue with deletion even if image delete fails

def delete_connector_from_excel(connector_type: str, size: str = None):
    """Delete connector type or specific size from Excel database."""
    try:
        # Read existing Excel file
        df = pd.read_excel(EXCEL_PATH, sheet_name="Database")
        
        if size:
            # Delete specific size from connector type
            df = df[~((df['Part'] == connector_type) & (df['Size'] == size))]
        else:
            # Delete entire connector type
            df = df[df['Part'] != connector_type]
        
        # Save back to Excel
        with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Database', index=False)
        
        return True
    except Exception as e:
        st.error(f"Error deleting from Excel: {e}")
        return False

def delete_connector_from_config(connector_type: str, size: str = None):
    """Delete connector type or specific size from src/config.py."""
    try:
        config_path = Path(__file__).parent / "src" / "config.py"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        if size:
            # Remove specific size from CONNECTOR_SIZES
            # Find the line with this size and remove it
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if f'"{connector_type}"' in line and f'"{size}"' in line:
                    # Skip this line - it's the connector type with this size
                    continue
                new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            # Remove entire connector type from all lists
            # Remove from SUPPORTED_CONNECTOR_TYPES
            content = content.replace(f'    "{connector_type}",\n', '')
            
            # Remove from CONNECTOR_SIZES - remove the entire entry
            import re
            pattern = f'    "{connector_type}": .*?\n'
            content = re.sub(pattern, '', content)
            
            # Remove from CONNECTOR_IMAGE_MAP if it exists
            content = content.replace(f'    "{connector_type}": ".*?",\n', '')
            content = re.sub(f'    "{connector_type}": "[^"]*",\n', '', content)
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        st.error(f"Error updating config.py: {e}")
        return False

def save_image_to_folder(image_obj, filename: str):
    """Save image to images/ folder. Accepts both Streamlit uploaded files and PIL Images."""
    try:
        images_dir = Path(__file__).parent / "images"
        images_dir.mkdir(exist_ok=True)
        
        file_path = images_dir / filename
        
        # Handle PIL Image objects
        if isinstance(image_obj, Image.Image):
            image_obj.save(file_path)
        # Handle Streamlit uploaded file objects
        else:
            with open(file_path, 'wb') as f:
                f.write(image_obj.getvalue())
        
        return True
    except Exception as e:
        st.error(f"Error saving image: {e}")
        return False

# Helper function to display connector images
def display_connector_image(connector_type: str, width: int = 150, flip: bool = False):
    """Display image for the selected connector type. Optionally flip the image horizontally."""
    from src.config import CONNECTOR_IMAGE_MAP
    
    # First check if it's in the config map (which includes both standard and custom mappings)
    image_filename = CONNECTOR_IMAGE_MAP.get(connector_type)
    image_path = None
    
    if image_filename:
        image_path = Path(__file__).parent / "images" / image_filename
    
    # If not found in map, try to find it dynamically in images/ folder by connector name
    if not image_path or not image_path.exists():
        images_dir = Path(__file__).parent / "images"
        if images_dir.exists():
            for file in images_dir.iterdir():
                if file.is_file() and connector_type.lower() in file.stem.lower():
                    image_path = file
                    break
    
    if image_path and image_path.exists():
        try:
            img = Image.open(image_path)
            # Flip horizontally if requested
            if flip:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            st.image(img, caption=connector_type, width=width)
        except Exception as e:
            st.warning(f"Could not load image for {connector_type}")
    else:
        # Silently skip if no image found (don't show warning for custom connectors without images)
        pass

# Page config
st.set_page_config(
    page_title="PVC Cut Calculator",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .result-box {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin: 20px 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'loader' not in st.session_state:
    try:
        st.session_state.loader = DimensionLoader(EXCEL_PATH)
    except Exception as e:
        st.error(f"Error loading database: {e}")
        st.stop()

# Initialize connector/size session state for cross-tab synchronization
if 'connector_types_modified' not in st.session_state:
    st.session_state.connector_types_modified = list(SUPPORTED_CONNECTOR_TYPES)

if 'connector_sizes_modified' not in st.session_state:
    st.session_state.connector_sizes_modified = dict(CONNECTOR_SIZES)

if 'connector_offsets' not in st.session_state:
    st.session_state.connector_offsets = {}

# Update loader with session offsets
loader = st.session_state.loader
loader.session_offsets = st.session_state.connector_offsets

# Title and description
st.title("🔧 PVC Cut Calculator")
st.markdown("Calculate precise PVC pipe cut lengths for different connector configurations.")

# Tabs for different calculation types
jobs_tab, standard_tab, layin_tab, bushing_tab, manage_tab = st.tabs(["Jobs", "Standard Cut", "Lay-in Cut", "Bushing Cut", "Manage Fittings"])

# ============================================================================
# TAB 1: STANDARD CUT (single cut between two connectors)
# ============================================================================
with standard_tab:
    st.subheader("Standard Cut (Center-to-Center)")
    st.markdown("Calculate a single cut between two connectors.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Connection A**")
        type_a = st.selectbox(
            "Connection Type A",
            st.session_state.connector_types_modified,
            key="std_type_a",
            label_visibility="collapsed"
        )
        size_a = st.selectbox(
            "Size A (inches)",
            st.session_state.connector_sizes_modified.get(type_a, []),
            key="std_size_a",
            label_visibility="collapsed",
            help="Select the connector size"
        )
        # Display image for type_a
        display_connector_image(type_a)
    
    with col2:
        st.markdown("**Connection B**")
        type_b = st.selectbox(
            "Connection Type B",
            st.session_state.connector_types_modified,
            key="std_type_b",
            label_visibility="collapsed"
        )
        size_b = st.selectbox(
            "Size B (inches)",
            st.session_state.connector_sizes_modified.get(type_b, []),
            key="std_size_b",
            label_visibility="collapsed",
            help="Select the connector size"
        )
        # Display image for type_b (flip if Elbow 90)
        display_connector_image(type_b, flip=(type_b == "Elbow 90(Socket x Socket)"))
    
    # Measurement inputs
    st.markdown("**Measurement**")
    col1, col2 = st.columns(2)
    with col1:
        c2c = st.number_input(
            "Center-to-Center (inches)",
            min_value=0.0,
            value=12.0,
            step=0.25,
            key="std_c2c"
        )
    
    with col2:
        include_shave = st.checkbox(
            "Include Shave (-1/16\")",
            value=False,
            key="std_shave"
        )
    
    # Calculate button
    if st.button("Calculate Cut Length", key="std_calc", type="primary"):
        try:
            request, cut_length = get_cut_length(
                loader,
                type_a,
                size_a,
                type_b,
                size_b,
                c2c
            )
            
            if include_shave:
                cut_length -= 1/16
            
            # Display result
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Result")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Decimal:** {cut_length:.5f}\"")
            with col2:
                st.markdown(f"**Fraction (1/16ths):** {decimal_to_fraction_16ths(cut_length)}")
            
            st.markdown("---")
            st.markdown("**Calculation Details:**")
            st.text(str(request))
            st.markdown('</div>', unsafe_allow_html=True)
            
        except ValueError as e:
            st.markdown(f'<div class="error-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Unexpected error: {e}</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: LAY-IN CUT (three fittings: A -> Lay-in -> B)
# ============================================================================
with layin_tab:
    st.subheader("Lay-in Cut (Three Fittings)")
    st.markdown("Calculate two cuts for lay-in connector configuration: Fitting A -> Lay-in Fitting -> Fitting B")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Fitting A**")
        type_a = st.selectbox(
            "Connection Type A",
            st.session_state.connector_types_modified,
            key="lay_type_a",
            label_visibility="collapsed"
        )
        size_a = st.selectbox(
            "Size A",
            st.session_state.connector_sizes_modified.get(type_a, []),
            key="lay_size_a",
            label_visibility="collapsed"
        )
        # Display image for type_a
        display_connector_image(type_a)
    
    with col2:
        st.markdown("**Lay-in Fitting**")
        type_lay_in = st.selectbox(
            "Lay-in Connection Type",
            st.session_state.connector_types_modified,
            key="lay_type_lay_in",
            label_visibility="collapsed"
        )
        size_lay_in = st.selectbox(
            "Lay-in Size",
            st.session_state.connector_sizes_modified.get(type_lay_in, []),
            key="lay_size_lay_in",
            label_visibility="collapsed"
        )
        # Display image for type_lay_in
        display_connector_image(type_lay_in)
    
    with col3:
        st.markdown("**Fitting B**")
        type_b = st.selectbox(
            "Connection Type B",
            st.session_state.connector_types_modified,
            key="lay_type_b",
            label_visibility="collapsed"
        )
        size_b = st.selectbox(
            "Size B",
            st.session_state.connector_sizes_modified.get(type_b, []),
            key="lay_size_b",
            label_visibility="collapsed"
        )
        # Display image for type_b (flip if Elbow 90)
        display_connector_image(type_b, flip=(type_b == "Elbow 90(Socket x Socket)"))
    
    # Lay-in specific measurements
    st.markdown("**Measurements**")
    col1, col2 = st.columns(2)
    
    with col1:
        c2c_overall = st.number_input(
            "Overall C2C (inches)",
            min_value=0.0,
            value=12.0,
            step=0.25,
            key="lay_c2c_overall"
        )
    
    with col2:
        c2c_lay_in = st.number_input(
            "C2C: Fitting A to Lay-in (inches)",
            min_value=0.0,
            value=6.0,
            step=0.25,
            key="lay_c2c_lay_in"
        )
    
    include_shave = st.checkbox(
        "Include Shave (-1/16\") on both cuts",
        value=False,
        key="lay_shave"
    )
    
    # Calculate button
    if st.button("Calculate Lay-in Cuts", key="lay_calc", type="primary"):
        try:
            request, (cut1, cut2) = get_lay_in_cuts(
                loader,
                type_a,
                size_a,
                type_lay_in,
                size_lay_in,
                type_b,
                size_b,
                c2c_overall,
                c2c_lay_in
            )
            
            if include_shave:
                cut1 -= 1/16
                cut2 -= 1/16
            
            # Display result
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Result")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Cut 1 (A → Lay-in):**")
                st.markdown(f"- Decimal: {cut1:.5f}\"")
                st.markdown(f"- Fraction: {decimal_to_fraction_16ths(cut1)}")
            
            with col2:
                st.markdown("**Cut 2 (Lay-in → B):**")
                st.markdown(f"- Decimal: {cut2:.5f}\"")
                st.markdown(f"- Fraction: {decimal_to_fraction_16ths(cut2)}")
            
            st.markdown("---")
            st.markdown("**Calculation Details:**")
            st.text(str(request))
            st.markdown('</div>', unsafe_allow_html=True)
            
        except ValueError as e:
            st.markdown(f'<div class="error-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Unexpected error: {e}</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: BUSHING CUT (three fittings: A -> Bushing -> B)
# ============================================================================
with bushing_tab:
    st.subheader("Bushing Cut (Three Fittings)")
    st.markdown("Calculate cut length with bushing: Fitting A -> Bushing -> Fitting B")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Fitting A**")
        type_a = st.selectbox(
            "Connection Type A",
            st.session_state.connector_types_modified,
            key="bush_type_a",
            label_visibility="collapsed"
        )
        size_a = st.selectbox(
            "Size A",
            st.session_state.connector_sizes_modified.get(type_a, []),
            key="bush_size_a",
            label_visibility="collapsed"
        )
        # Display image for type_a
        display_connector_image(type_a)
    
    with col2:
        st.markdown("**Bushing**")
        # Bushing is always "Bushing (Spigot x Socket)"
        type_bushing = "Bushing (Spigot x Socket)"
        st.markdown("Type: Bushing (Spigot x Socket)")
        size_bushing = st.selectbox(
            "Bushing Size",
            st.session_state.connector_sizes_modified.get(type_bushing, []),
            key="bush_size_bushing",
            label_visibility="collapsed"
        )
        # Display image for bushing
        display_connector_image(type_bushing)
    
    with col3:
        st.markdown("**Fitting B**")
        type_b = st.selectbox(
            "Connection Type B",
            st.session_state.connector_types_modified,
            key="bush_type_b",
            label_visibility="collapsed"
        )
        size_b = st.selectbox(
            "Size B",
            st.session_state.connector_sizes_modified.get(type_b, []),
            key="bush_size_b",
            label_visibility="collapsed"
        )
        # Display image for type_b (flip if Elbow 90)
        display_connector_image(type_b, flip=(type_b == "Elbow 90(Socket x Socket)"))
    
    # Bushing specific measurements
    st.markdown("**Measurements**")
    c2c = st.number_input(
        "Center-to-Center (inches)",
        min_value=0.0,
        value=12.0,
        step=0.25,
        key="bush_c2c"
    )
    
    include_shave = st.checkbox(
        "Include Shave (-1/16\")",
        value=False,
        key="bush_shave"
    )
    
    # Calculate button
    if st.button("Calculate Bushing Cut", key="bush_calc", type="primary"):
        try:
            request, cut_length = get_bushing_cut(
                loader,
                type_a,
                size_a,
                type_bushing,
                size_bushing,
                type_b,
                size_b,
                c2c
            )
            
            if include_shave:
                cut_length -= 1/16
            
            # Display result
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("### ✅ Result")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Decimal:** {cut_length:.5f}\"")
            with col2:
                st.markdown(f"**Fraction (1/16ths):** {decimal_to_fraction_16ths(cut_length)}")
            
            st.markdown("---")
            st.markdown("**Calculation Details:**")
            st.text(str(request))
            st.markdown('</div>', unsafe_allow_html=True)
            
        except ValueError as e:
            st.markdown(f'<div class="error-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Unexpected error: {e}</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 4: JOBS - Create and manage job checklists
# ============================================================================
with jobs_tab:
    st.subheader("Job Management")
    st.markdown("Create a job, add cuts to a checklist, and export for printing.")
    
    # Initialize job session state
    if 'jobs' not in st.session_state:
        st.session_state.jobs = {}
    if 'current_job' not in st.session_state:
        st.session_state.current_job = None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_job_name = st.text_input("New Job Name", placeholder="Enter job name (e.g., Kitchen Renovation)")
        if st.button("Create Job", key="create_job"):
            if new_job_name.strip():
                if new_job_name in st.session_state.jobs:
                    st.error("Job already exists!")
                else:
                    st.session_state.jobs[new_job_name] = {
                        'cuts': [],
                        'created_at': str(st.session_state.get('current_timestamp', ''))
                    }
                    st.session_state.current_job = new_job_name
                    st.success(f"Job '{new_job_name}' created!")
                    st.rerun()
            else:
                st.error("Please enter a job name")
    
    with col2:
        if st.session_state.jobs:
            selected_job = st.selectbox(
                "Select Job",
                list(st.session_state.jobs.keys()),
                key="job_selector"
            )
            if selected_job:
                st.session_state.current_job = selected_job
        else:
            st.info("No jobs created yet. Create one above.")
    
    with col3:
        if st.session_state.current_job and st.session_state.current_job in st.session_state.jobs:
            if st.button("Delete Job", key="delete_job"):
                del st.session_state.jobs[st.session_state.current_job]
                st.session_state.current_job = None
                st.success("Job deleted!")
                st.rerun()
    
    # Current job operations
    if st.session_state.current_job and st.session_state.current_job in st.session_state.jobs:
        st.markdown(f"### Job: **{st.session_state.current_job}**")
        
        # Add cuts section
        st.markdown("#### Add Cuts to Job")
        
        cut_type = st.radio(
            "Cut Type",
            ["Standard Cut", "Bushing Cut"],  # "Lay-in Cut" - disabled for now
            key="job_cut_type"
        )
        
        if cut_type == "Standard Cut":
            col1, col2 = st.columns(2)
            with col1:
                job_type_a = st.selectbox(
                    "Connection Type A",
                    st.session_state.connector_types_modified,
                    key="job_std_type_a"
                )
                job_size_a = st.selectbox(
                    "Size A",
                    st.session_state.connector_sizes_modified.get(job_type_a, []),
                    key="job_std_size_a"
                )
                # Display image for job_type_a
                display_connector_image(job_type_a, width=120)
            
            with col2:
                job_type_b = st.selectbox(
                    "Connection Type B",
                    st.session_state.connector_types_modified,
                    key="job_std_type_b"
                )
                job_size_b = st.selectbox(
                    "Size B",
                    st.session_state.connector_sizes_modified.get(job_type_b, []),
                    key="job_std_size_b"
                )
                # Display image for job_type_b (flip if Elbow 90)
                display_connector_image(job_type_b, width=120, flip=(job_type_b == "Elbow 90(Socket x Socket)"))
            
            job_c2c = st.number_input(
                "Center-to-Center (inches)",
                min_value=0.0,
                value=12.0,
                step=0.25,
                key="job_std_c2c"
            )
            
            job_shave = st.checkbox("Include Shave (-1/16\")", key="job_std_shave")
            job_notes = st.text_input("Notes (optional)", key="job_std_notes", placeholder="e.g., kitchen sink drain")
            
            if st.button("Add Cut to Job", key="add_std_cut"):
                try:
                    request, cut_length = get_cut_length(
                        loader,
                        job_type_a,
                        job_size_a,
                        job_type_b,
                        job_size_b,
                        job_c2c
                    )
                    
                    if job_shave:
                        cut_length -= 1/16
                    
                    cut_num = len(st.session_state.jobs[st.session_state.current_job]['cuts']) + 1
                    cut_data = {
                        'number': cut_num,
                        'type': 'Standard',
                        'connection_a': f"{job_type_a} ({job_size_a}\")",
                        'connection_b': f"{job_type_b} ({job_size_b}\")",
                        'c2c': job_c2c,
                        'length_decimal': cut_length,
                        'length_fraction': decimal_to_fraction_16ths(cut_length),
                        'shave': job_shave,
                        'notes': job_notes
                    }
                    
                    st.session_state.jobs[st.session_state.current_job]['cuts'].append(cut_data)
                    st.success(f"Cut {cut_num} added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # elif cut_type == "Lay-in Cut":
        #     col1, col2, col3 = st.columns(3)
        #     
        #     with col1:
        #         job_type_a = st.selectbox(
        #             "Fitting A Type",
        #             SUPPORTED_CONNECTOR_TYPES,
        #             key="job_lay_type_a"
        #         )
        #         job_size_a = st.selectbox(
        #             "Size A",
        #             CONNECTOR_SIZES.get(job_type_a, []),
        #             key="job_lay_size_a"
        #         )
        #     
        #     with col2:
        #         job_type_lay_in = st.selectbox(
        #             "Lay-in Type",
        #             SUPPORTED_CONNECTOR_TYPES,
        #             key="job_lay_type_lay_in"
        #         )
        #         job_size_lay_in = st.selectbox(
        #             "Size Lay-in",
        #             CONNECTOR_SIZES.get(job_type_lay_in, []),
        #             key="job_lay_size_lay_in"
        #         )
        #     
        #     with col3:
        #         job_type_b = st.selectbox(
        #             "Fitting B Type",
        #             SUPPORTED_CONNECTOR_TYPES,
        #             key="job_lay_type_b"
        #         )
        #         job_size_b = st.selectbox(
        #             "Size B",
        #             CONNECTOR_SIZES.get(job_type_b, []),
        #             key="job_lay_size_b"
        #         )
        #     
        #     job_c2c_overall = st.number_input(
        #         "Overall C2C",
        #         min_value=0.0,
        #         value=12.0,
        #         step=0.25,
        #         key="job_lay_c2c_overall"
        #     )
        #     
        #     job_c2c_lay_in = st.number_input(
        #         "C2C: A to Lay-in",
        #         min_value=0.0,
        #         value=6.0,
        #         step=0.25,
        #         key="job_lay_c2c_lay_in"
        #     )
        #     
        #     job_shave = st.checkbox("Include Shave on both cuts", key="job_lay_shave")
        #     job_notes = st.text_input("Notes (optional)", key="job_lay_notes")
        #     
        #     if st.button("Add Cut to Job", key="add_lay_cut"):
        #         try:
        #             request, (cut1, cut2) = get_lay_in_cuts(
        #                 loader,
        #                 job_type_a,
        #                 job_size_a,
        #                 job_type_lay_in,
        #                 job_size_lay_in,
        #                 job_type_b,
        #                 job_size_b,
        #                 job_c2c_overall,
        #                 job_c2c_lay_in
        #             )
        #             
        #             if job_shave:
        #                 cut1 -= 1/16
        #                 cut2 -= 1/16
        #             
        #             cut_num = len(st.session_state.jobs[st.session_state.current_job]['cuts']) + 1
        #             cut_data = {
        #                 'number': cut_num,
        #                 'type': 'Lay-in',
        #                 'connection_a': f"{job_type_a} ({job_size_a}\")",
        #                 'connection_lay_in': f"{job_type_lay_in} ({job_size_lay_in}\")",
        #                 'connection_b': f"{job_type_b} ({job_size_b}\")",
        #                 'c2c_overall': job_c2c_overall,
        #                 'c2c_lay_in': job_c2c_lay_in,
        #                 'cut1_decimal': cut1,
        #                 'cut1_fraction': decimal_to_fraction_16ths(cut1),
        #                 'cut2_decimal': cut2,
        #                 'cut2_fraction': decimal_to_fraction_16ths(cut2),
        #                 'shave': job_shave,
        #                 'notes': job_notes
        #             }
        #             
        #             st.session_state.jobs[st.session_state.current_job]['cuts'].append(cut_data)
        #             st.success(f"Cut {cut_num} added!")
        #             st.rerun()
        #         except Exception as e:
        #             st.error(f"Error: {e}")
        
        elif cut_type == "Bushing Cut":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                job_type_a = st.selectbox(
                    "Fitting A Type",
                    st.session_state.connector_types_modified,
                    key="job_bush_type_a"
                )
                job_size_a = st.selectbox(
                    "Size A",
                    st.session_state.connector_sizes_modified.get(job_type_a, []),
                    key="job_bush_size_a"
                )
                # Display image for job_type_a
                display_connector_image(job_type_a, width=100)
            
            with col2:
                st.markdown("**Bushing**")
                st.markdown("Type: Bushing (Spigot x Socket)")
                job_size_bushing = st.selectbox(
                    "Bushing Size",
                    st.session_state.connector_sizes_modified.get("Bushing (Spigot x Socket)", []),
                    key="job_bush_size_bushing"
                )
                # Display image for bushing
                display_connector_image("Bushing (Spigot x Socket)", width=100)
            
            with col3:
                job_type_b = st.selectbox(
                    "Fitting B Type",
                    st.session_state.connector_types_modified,
                    key="job_bush_type_b"
                )
                job_size_b = st.selectbox(
                    "Size B",
                    st.session_state.connector_sizes_modified.get(job_type_b, []),
                    key="job_bush_size_b"
                )
                # Display image for job_type_b (flip if Elbow 90)
                display_connector_image(job_type_b, width=100, flip=(job_type_b == "Elbow 90(Socket x Socket)"))
            
            job_c2c = st.number_input(
                "Center-to-Center",
                min_value=0.0,
                value=12.0,
                step=0.25,
                key="job_bush_c2c"
            )
            
            job_shave = st.checkbox("Include Shave (-1/16\")", key="job_bush_shave")
            job_notes = st.text_input("Notes (optional)", key="job_bush_notes")
            
            if st.button("Add Cut to Job", key="add_bush_cut"):
                try:
                    request, cut_length = get_bushing_cut(
                        loader,
                        job_type_a,
                        job_size_a,
                        "Bushing (Spigot x Socket)",
                        job_size_bushing,
                        job_type_b,
                        job_size_b,
                        job_c2c
                    )
                    
                    if job_shave:
                        cut_length -= 1/16
                    
                    cut_num = len(st.session_state.jobs[st.session_state.current_job]['cuts']) + 1
                    cut_data = {
                        'number': cut_num,
                        'type': 'Bushing',
                        'connection_a': f"{job_type_a} ({job_size_a}\")",
                        'connection_bushing': f"Bushing ({job_size_bushing}\")",
                        'connection_b': f"{job_type_b} ({job_size_b}\")",
                        'c2c': job_c2c,
                        'length_decimal': cut_length,
                        'length_fraction': decimal_to_fraction_16ths(cut_length),
                        'shave': job_shave,
                        'notes': job_notes
                    }
                    
                    st.session_state.jobs[st.session_state.current_job]['cuts'].append(cut_data)
                    st.success(f"Cut {cut_num} added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Display checklist
        st.markdown("#### Checklist")
        
        if st.session_state.jobs[st.session_state.current_job]['cuts']:
            # Create checklist with columns for checkbox, cut info, and delete
            for cut in st.session_state.jobs[st.session_state.current_job]['cuts']:
                col1, col2, col3 = st.columns([0.5, 5, 0.5])
                
                with col1:
                    checked = st.checkbox(
                        "Done",
                        key=f"cut_{cut['number']}_check",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    if cut['type'] == 'Standard':
                        st.markdown(f"""
                        **Cut {cut['number']}** | {cut['type']} Cut  
                        {cut['connection_a']} → {cut['connection_b']}  
                        C2C: {cut['c2c']}" | Length: **{cut['length_fraction']}** ({cut['length_decimal']:.4f}")  
                        {f"✓ Shave applied" if cut['shave'] else ""}  
                        {f"_Note: {cut['notes']}_" if cut['notes'] else ""}
                        """)
                    # elif cut['type'] == 'Lay-in':
                    #     st.markdown(f"""
                    #     **Cut {cut['number']}** | {cut['type']} Cut  
                    #     {cut['connection_a']} → {cut['connection_lay_in']} → {cut['connection_b']}  
                    #     Cut 1 (A→Lay-in): **{cut['cut1_fraction']}** ({cut['cut1_decimal']:.4f}")  
                    #     Cut 2 (Lay-in→B): **{cut['cut2_fraction']}** ({cut['cut2_decimal']:.4f}")  
                    #     {f"✓ Shave applied" if cut['shave'] else ""}  
                    #     {f"_Note: {cut['notes']}_" if cut['notes'] else ""}
                    #     """)
                    elif cut['type'] == 'Bushing':
                        st.markdown(f"""
                        **Cut {cut['number']}** | {cut['type']} Cut  
                        {cut['connection_a']} → {cut['connection_bushing']} → {cut['connection_b']}  
                        C2C: {cut['c2c']}" | Length: **{cut['length_fraction']}** ({cut['length_decimal']:.4f}")  
                        {f"✓ Shave applied" if cut['shave'] else ""}  
                        {f"_Note: {cut['notes']}_" if cut['notes'] else ""}
                        """)
                
                with col3:
                    if st.button("🗑️", key=f"delete_cut_{cut['number']}", help="Delete this cut"):
                        st.session_state.jobs[st.session_state.current_job]['cuts'].remove(cut)
                        st.success("Cut removed!")
                        st.rerun()
                
                st.divider()
            
            # Export section
            st.markdown("#### Export Checklist")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate text version for printing
                export_text = f"PVC CUT CALCULATOR - JOB CHECKLIST\n"
                export_text += f"Job: {st.session_state.current_job}\n"
                export_text += f"{'='*60}\n\n"
                
                for cut in st.session_state.jobs[st.session_state.current_job]['cuts']:
                    export_text += f"[ ] CUT {cut['number']}\n"
                    if cut['type'] == 'Standard':
                        export_text += f"    Type: Standard Cut\n"
                        export_text += f"    {cut['connection_a']} → {cut['connection_b']}\n"
                        export_text += f"    C2C: {cut['c2c']}\"\n"
                        export_text += f"    Length: {cut['length_fraction']} ({cut['length_decimal']:.4f}\")\n"
                    # elif cut['type'] == 'Lay-in':
                    #     export_text += f"    Type: Lay-in Cut\n"
                    #     export_text += f"    {cut['connection_a']} → {cut['connection_lay_in']} → {cut['connection_b']}\n"
                    #     export_text += f"    Cut 1: {cut['cut1_fraction']} ({cut['cut1_decimal']:.4f}\")\n"
                    #     export_text += f"    Cut 2: {cut['cut2_fraction']} ({cut['cut2_decimal']:.4f}\")\n"
                    elif cut['type'] == 'Bushing':
                        export_text += f"    Type: Bushing Cut\n"
                        export_text += f"    {cut['connection_a']} → {cut['connection_bushing']} → {cut['connection_b']}\n"
                        export_text += f"    C2C: {cut['c2c']}\"\n"
                        export_text += f"    Length: {cut['length_fraction']} ({cut['length_decimal']:.4f}\")\n"
                    
                    if cut['shave']:
                        export_text += f"    ✓ Shave applied\n"
                    if cut['notes']:
                        export_text += f"    Note: {cut['notes']}\n"
                    export_text += "\n"
                
                st.download_button(
                    label="📥 Download Checklist (TXT)",
                    data=export_text,
                    file_name=f"{st.session_state.current_job}_checklist.txt",
                    mime="text/plain"
                )
            
            with col2:
                st.info("💡 Tip: Use your browser's Print function (Cmd+P) to print this checklist or save as PDF")
        
        else:
            st.info("No cuts added yet. Add your first cut above!")

# ============================================================================
# TAB 5: MANAGE FITTINGS - Add new connector types and sizes
# ============================================================================
with manage_tab:
    st.subheader("Manage Fittings")
    st.markdown("Add new connector types and sizes to your database.")
    
    tab_view, tab_add = st.tabs(["View Current Fittings", "Add New Fitting"])
    
    # ========================
    # View Current Fittings
    # ========================
    with tab_view:
        st.markdown("### Current Connector Types")
        
        for conn_type in st.session_state.connector_types_modified:
            with st.expander(f"📦 {conn_type}", expanded=False):
                sizes = st.session_state.connector_sizes_modified.get(conn_type, [])
                
                # Delete entire connector type button
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("🗑️ Delete Type", key=f"delete_type_{conn_type}", type="secondary", help="Delete entire connector type"):
                        # Delete from Excel, config, and images folder
                        if delete_connector_from_excel(conn_type):
                            if delete_connector_from_config(conn_type):
                                # Delete associated image
                                delete_connector_image(conn_type)
                                
                                st.session_state.connector_types_modified.remove(conn_type)
                                del st.session_state.connector_sizes_modified[conn_type]
                                st.success(f"✅ Removed '{conn_type}' from database, config, and images folder!")
                                st.rerun()
                            else:
                                st.error("Deleted from Excel but failed to update config.py")
                        else:
                            st.error("Failed to delete from Excel database")
                
                if sizes:
                    st.markdown(f"**Available Sizes ({len(sizes)}):**")
                    # Display sizes with delete buttons
                    for size in sizes:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.code(size, language="text")
                        with col3:
                            if st.button("✕", key=f"delete_size_{conn_type}_{size}", help="Delete this size"):
                                # Delete from Excel and config
                                if delete_connector_from_excel(conn_type, size):
                                    if delete_connector_from_config(conn_type, size):
                                        updated_sizes = [s for s in st.session_state.connector_sizes_modified[conn_type] if s != size]
                                        st.session_state.connector_sizes_modified[conn_type] = updated_sizes
                                        st.success(f"✅ Removed '{size}' from database and config!")
                                        st.rerun()
                                    else:
                                        st.error("Deleted from Excel but failed to update config.py")
                                else:
                                    st.error("Failed to delete from Excel database")
                                st.rerun()
                else:
                    st.warning("No sizes defined for this connector type")
    
    # ========================
    # Add New Fitting
    # ========================
    with tab_add:
        st.markdown("### Add New Connector Type or Size")
        
        option = st.radio(
            "What would you like to add?",
            ["Add New Connector Type", "Add Size to Existing Type"],
            key="fitting_option"
        )
        
        if option == "Add New Connector Type":
            st.markdown("#### New Connector Type")
            
            new_type_name = st.text_input(
                "Connector Type Name",
                placeholder="e.g., Wye (Socket x Socket x Socket)",
                key="new_connector_type"
            )
            
            st.markdown("**Upload Image (Optional)**")
            uploaded_image = st.file_uploader(
                "Upload an image for this connector type",
                type=["png", "jpg", "jpeg", "gif"],
                key="new_connector_image",
                help="Recommended: 150x150 pixels. Supported formats: PNG, JPG, JPEG, GIF"
            )
            
            if uploaded_image is not None:
                # Initialize image editing state
                if 'image_rotation' not in st.session_state:
                    st.session_state.image_rotation = 0
                if 'image_flip_horizontal' not in st.session_state:
                    st.session_state.image_flip_horizontal = False
                if 'image_flip_vertical' not in st.session_state:
                    st.session_state.image_flip_vertical = False
                
                # Load and display image with edits
                image_pil = Image.open(uploaded_image)
                edited_image = image_pil.copy()
                
                # Apply rotations
                if st.session_state.image_rotation != 0:
                    edited_image = edited_image.rotate(st.session_state.image_rotation, expand=True)
                
                # Apply flips
                if st.session_state.image_flip_horizontal:
                    edited_image = edited_image.transpose(Image.FLIP_LEFT_RIGHT)
                if st.session_state.image_flip_vertical:
                    edited_image = edited_image.transpose(Image.FLIP_TOP_BOTTOM)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("**Preview:**")
                    st.image(edited_image, width=120)
                with col2:
                    st.success(f"✅ Image selected: {uploaded_image.name}")
                    st.info("This image will be displayed when users select this connector type.")
                
                # Image editing controls
                st.markdown("**Edit Image**")
                col_rot1, col_rot2, col_rot3, col_rot4 = st.columns(4)
                
                with col_rot1:
                    if st.button("🔄 Rotate 90°", key="rotate_90"):
                        st.session_state.image_rotation = (st.session_state.image_rotation + 90) % 360
                        st.rerun()
                
                with col_rot2:
                    if st.button("↩️ Rotate -90°", key="rotate_minus_90"):
                        st.session_state.image_rotation = (st.session_state.image_rotation - 90) % 360
                        st.rerun()
                
                with col_rot3:
                    st.session_state.image_flip_horizontal = st.checkbox(
                        "🔀 Flip Horizontal",
                        value=st.session_state.image_flip_horizontal,
                        key="flip_horizontal"
                    )
                
                with col_rot4:
                    st.session_state.image_flip_vertical = st.checkbox(
                        "⬌ Flip Vertical",
                        value=st.session_state.image_flip_vertical,
                        key="flip_vertical"
                    )
                
                if st.button("🔄 Reset Image", key="reset_image"):
                    st.session_state.image_rotation = 0
                    st.session_state.image_flip_horizontal = False
                    st.session_state.image_flip_vertical = False
                    st.rerun()
                
                # Get file extension
                file_ext = Path(uploaded_image.name).suffix
                
                st.markdown("**Image Filename (in images/ folder)**")
                default_filename = f"{new_type_name.lower().replace(' ', '_')}{file_ext}"
                image_filename = st.text_input(
                    "Custom filename (leave blank to use default)",
                    value="",
                    placeholder=default_filename,
                    key="image_filename",
                    help="The filename that will be used to save this image"
                )
                
                # Use custom filename if provided, otherwise use default
                if image_filename.strip():
                    final_filename = image_filename.strip()
                else:
                    final_filename = default_filename
                
                st.info(f"✓ Image will be saved as: `{final_filename}`")
            else:
                final_filename = None
            
            st.markdown("**Sizes with Offsets**")
            st.info("Add each size with its corresponding offset values. You can add multiple sizes.")
            
            # Initialize session state for new connector sizes input
            if 'new_conn_sizes_list' not in st.session_state:
                st.session_state.new_conn_sizes_list = []
            
            # Display existing sizes being added
            if st.session_state.new_conn_sizes_list:
                st.markdown("##### Sizes to Add:")
                for idx, size_data in enumerate(st.session_state.new_conn_sizes_list):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    with col1:
                        st.text(f"Size: {size_data['size']}")
                    with col2:
                        st.text(f"Offset: {size_data['offset']:.4f}\"")
                    with col3:
                        g1_text = f"G1: {size_data['g1_offset']:.4f}\"" if size_data['g1_offset'] > 0 else "G1: N/A"
                        st.text(g1_text)
                    with col4:
                        if st.button("🗑️", key=f"remove_size_{idx}", help="Remove this size"):
                            st.session_state.new_conn_sizes_list.pop(idx)
                            st.rerun()
            
            # Add new size input
            st.markdown("##### Add Size:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                size_input = st.text_input(
                    "Size",
                    placeholder="e.g., 1.5 or 2x2x1",
                    key="new_size_input",
                    help="Enter a single size"
                )
            
            with col2:
                offset_input = st.number_input(
                    "Offset",
                    min_value=0.0,
                    step=0.0625,
                    key="new_offset_input",
                    help="Enter the offset value in inches",
                    format="%.4f"
                )
            
            with col3:
                g1_offset_input = st.number_input(
                    "G1 Offset (optional)",
                    min_value=0.0,
                    step=0.0625,
                    key="new_g1_offset_input",
                    help="Enter the G1 offset value (leave as 0 if not needed)",
                    format="%.4f"
                )
            
            if st.button("Add Size to List", key="add_size_to_list"):
                if not size_input.strip():
                    st.error("Please enter a size")
                elif offset_input == 0.0:
                    st.error("Please enter a valid offset value")
                else:
                    # Check if size already exists in the list
                    if any(s['size'] == size_input.strip() for s in st.session_state.new_conn_sizes_list):
                        st.error("This size already exists in the list")
                    else:
                        st.session_state.new_conn_sizes_list.append({
                            'size': size_input.strip(),
                            'offset': offset_input,
                            'g1_offset': g1_offset_input
                        })
                        st.success(f"Added size '{size_input.strip()}' with offset {offset_input:.4f}\"")
                        st.rerun()
            
            # Add connector type button
            if st.button("✅ Create Connector Type", key="add_new_type", type="primary"):
                if not new_type_name.strip():
                    st.error("Please enter a connector type name")
                elif new_type_name in st.session_state.connector_types_modified:
                    st.error(f"Connector type '{new_type_name}' already exists!")
                elif not st.session_state.new_conn_sizes_list:
                    st.error("Please add at least one size with offset")
                else:
                    # Extract sizes and offsets
                    sizes_list = [s['size'] for s in st.session_state.new_conn_sizes_list]
                    
                    # Save to Excel database
                    if save_connector_to_excel(new_type_name, st.session_state.new_conn_sizes_list):
                        # Update config.py with image filename
                        if update_config_py(new_type_name, st.session_state.new_conn_sizes_list, final_filename):
                            # Add to session state
                            st.session_state.connector_types_modified.append(new_type_name)
                            st.session_state.connector_sizes_modified[new_type_name] = sizes_list
                            
                            # Store offset data
                            if 'connector_offsets' not in st.session_state:
                                st.session_state.connector_offsets = {}
                            
                            for size_data in st.session_state.new_conn_sizes_list:
                                offset_key = f"{new_type_name}|{size_data['size']}"
                                st.session_state.connector_offsets[offset_key] = {
                                    'offset': size_data['offset'],
                                    'g1_offset': size_data['g1_offset'] if size_data['g1_offset'] > 0 else None
                                }
                            
                            # Store image if uploaded
                            if uploaded_image is not None and final_filename:
                                # Get the edited image
                                image_pil = Image.open(uploaded_image)
                                edited_image = image_pil.copy()
                                
                                # Apply rotations
                                if st.session_state.image_rotation != 0:
                                    edited_image = edited_image.rotate(st.session_state.image_rotation, expand=True)
                                
                                # Apply flips
                                if st.session_state.image_flip_horizontal:
                                    edited_image = edited_image.transpose(Image.FLIP_LEFT_RIGHT)
                                if st.session_state.image_flip_vertical:
                                    edited_image = edited_image.transpose(Image.FLIP_TOP_BOTTOM)
                                
                                if save_image_to_folder(edited_image, final_filename):
                                    if 'connector_images' not in st.session_state:
                                        st.session_state.connector_images = {}
                                    
                                    # Store image metadata in session
                                    st.session_state.connector_images[new_type_name] = {
                                        'filename': final_filename,
                                        'rotation': st.session_state.image_rotation,
                                        'flip_horizontal': st.session_state.image_flip_horizontal,
                                        'flip_vertical': st.session_state.image_flip_vertical
                                    }
                                    st.success(f"✅ Created '{new_type_name}' with {len(sizes_list)} sizes!")
                                    st.success(f"✅ Saved to Excel database and config.py!")
                                    st.success(f"📸 Image saved to images/ as '{final_filename}'!")
                                else:
                                    st.error("Failed to save image to images/ folder")
                            else:
                                st.success(f"✅ Created '{new_type_name}' with {len(sizes_list)} sizes!")
                                st.success(f"✅ Saved to Excel database and config.py!")
                            
                            st.info(f"""
                            ℹ️ **Changes have been saved permanently to:**
                            - Excel database: `data/PVC Cut Database .xlsx`
                            - Configuration: `src/config.py`
                            
                            **Note:** You may need to restart the app to fully load the changes in all modules.
                            """)
                            
                            # Clear the form
                            st.session_state.new_conn_sizes_list = []
                            st.rerun()
                        else:
                            st.error("Failed to update config.py. Changes saved to Excel only.")
                    else:
                        st.error("Failed to save to Excel database.")
        
        else:  # Add Size to Existing Type
            st.markdown("#### Add Size to Existing Type")
            
            existing_type = st.selectbox(
                "Select Connector Type",
                st.session_state.connector_types_modified,
                key="select_existing_type"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_size_input = st.text_input(
                    "New Size",
                    placeholder="e.g., 2.5 or 2x2x1",
                    key="new_size_single",
                    help="Enter a single size"
                )
            
            with col2:
                offset_value = st.number_input(
                    "Offset",
                    min_value=0.0,
                    step=0.0625,
                    key="new_offset_value",
                    help="Enter the offset value in inches",
                    format="%.4f"
                )
            
            with col3:
                g1_offset_value = st.number_input(
                    "G1 Offset (optional)",
                    min_value=0.0,
                    step=0.0625,
                    key="new_g1_offset_value",
                    help="Enter the G1 offset value (leave as 0 if not needed)",
                    format="%.4f"
                )
            
            if st.button("Add Size with Offset", key="add_single_size", type="primary"):
                if not new_size_input.strip():
                    st.error("Please enter a size")
                elif offset_value == 0.0:
                    st.error("Please enter a valid offset value")
                else:
                    new_size = new_size_input.strip()
                    current_sizes = st.session_state.connector_sizes_modified.get(existing_type, [])
                    
                    if new_size in current_sizes:
                        st.error(f"Size '{new_size}' already exists in '{existing_type}'")
                    else:
                        # Save to Excel
                        size_data = {
                            'size': new_size,
                            'offset': offset_value,
                            'g1_offset': g1_offset_value
                        }
                        
                        if save_connector_to_excel(existing_type, [size_data]):
                            # Update config.py
                            if update_config_py(existing_type, [size_data]):
                                # Add new size to session state
                                updated_sizes = current_sizes + [new_size]
                                st.session_state.connector_sizes_modified[existing_type] = updated_sizes
                                
                                # Store offset data in session state
                                if 'connector_offsets' not in st.session_state:
                                    st.session_state.connector_offsets = {}
                                
                                offset_key = f"{existing_type}|{new_size}"
                                st.session_state.connector_offsets[offset_key] = {
                                    'offset': offset_value,
                                    'g1_offset': g1_offset_value if g1_offset_value > 0 else None
                                }
                                
                                st.success(f"✅ Added size '{new_size}' to '{existing_type}'!")
                                st.success(f"✅ Saved to Excel database and config.py!")
                                st.info(f"""
                                ℹ️ **Changes have been saved permanently to:**
                                - Excel database: `data/PVC Cut Database .xlsx`
                                - Configuration: `src/config.py`
                                
                                **Note:** You may need to restart the app to fully load the changes in all modules.
                                """)
                                st.rerun()
                            else:
                                st.error("Failed to update config.py. Changes saved to Excel only.")
                        else:
                            st.error("Failed to save to Excel database.")
    
    # Display current session state
    st.markdown("---")
    st.markdown("### Session Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Connector Types", len(st.session_state.connector_types_modified))
    
    with col2:
        total_sizes = sum(len(sizes) for sizes in st.session_state.connector_sizes_modified.values())
        st.metric("Total Sizes", total_sizes)
    
    if st.checkbox("Show detailed session data", key="show_session_data"):
        st.json({
            "types": st.session_state.connector_types_modified,
            "sizes": st.session_state.connector_sizes_modified
        })

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>PVC Cut Calculator MVP | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
