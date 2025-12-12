import streamlit as st
import sys
from pathlib import Path
from PIL import Image
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.loader import DimensionLoader
from src.api import get_cut_length, get_lay_in_cuts, get_bushing_cut
from src.config import EXCEL_PATH, SUPPORTED_CONNECTOR_TYPES, CONNECTOR_SIZES
from src.main import decimal_to_fraction_16ths

# Helper function to display connector images
def display_connector_image(connector_type: str, width: int = 150, flip: bool = False):
    """Display image for the selected connector type. Optionally flip the image horizontally."""
    image_map = {
        "Tee (Socket x Socket x Socket)": "images/tee.png",
        "Tee (Reducing)": "images/tee(reducing).png",
        "Bushing (Spigot x Socket)": "images/bushing.png",
        "Elbow 90(Socket x Socket)": "images/elbow.png",
        "Union (Socket x Socket)": "images/union.png",
    }
    
    image_path = image_map.get(connector_type)
    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            # Flip horizontally if requested
            if flip:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            st.image(img, caption=connector_type, width=width)
        except Exception as e:
            st.warning(f"Could not load image for {connector_type}")

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

loader = st.session_state.loader

# Title and description
st.title("🔧 PVC Cut Calculator")
st.markdown("Calculate precise PVC pipe cut lengths for different connector configurations.")

# Tabs for different calculation types
tab1, tab2, tab3 = st.tabs(["Standard Cut", "Lay-in Cut", "Bushing Cut"])

# ============================================================================
# TAB 1: STANDARD CUT (single cut between two connectors)
# ============================================================================
with tab1:
    st.subheader("Standard Cut (Center-to-Center)")
    st.markdown("Calculate a single cut between two connectors.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Connection A**")
        type_a = st.selectbox(
            "Connection Type A",
            SUPPORTED_CONNECTOR_TYPES,
            key="std_type_a",
            label_visibility="collapsed"
        )
        size_a = st.selectbox(
            "Size A (inches)",
            CONNECTOR_SIZES.get(type_a, []),
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
            SUPPORTED_CONNECTOR_TYPES,
            key="std_type_b",
            label_visibility="collapsed"
        )
        size_b = st.selectbox(
            "Size B (inches)",
            CONNECTOR_SIZES.get(type_b, []),
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
with tab2:
    st.subheader("Lay-in Cut (Three Fittings)")
    st.markdown("Calculate two cuts for lay-in connector configuration: Fitting A -> Lay-in Fitting -> Fitting B")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Fitting A**")
        type_a = st.selectbox(
            "Connection Type A",
            SUPPORTED_CONNECTOR_TYPES,
            key="lay_type_a",
            label_visibility="collapsed"
        )
        size_a = st.selectbox(
            "Size A",
            CONNECTOR_SIZES.get(type_a, []),
            key="lay_size_a",
            label_visibility="collapsed"
        )
        # Display image for type_a
        display_connector_image(type_a)
    
    with col2:
        st.markdown("**Lay-in Fitting**")
        type_lay_in = st.selectbox(
            "Lay-in Connection Type",
            SUPPORTED_CONNECTOR_TYPES,
            key="lay_type_lay_in",
            label_visibility="collapsed"
        )
        size_lay_in = st.selectbox(
            "Lay-in Size",
            CONNECTOR_SIZES.get(type_lay_in, []),
            key="lay_size_lay_in",
            label_visibility="collapsed"
        )
        # Display image for type_lay_in
        display_connector_image(type_lay_in)
    
    with col3:
        st.markdown("**Fitting B**")
        type_b = st.selectbox(
            "Connection Type B",
            SUPPORTED_CONNECTOR_TYPES,
            key="lay_type_b",
            label_visibility="collapsed"
        )
        size_b = st.selectbox(
            "Size B",
            CONNECTOR_SIZES.get(type_b, []),
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
with tab3:
    st.subheader("Bushing Cut (Three Fittings)")
    st.markdown("Calculate cut length with bushing: Fitting A -> Bushing -> Fitting B")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Fitting A**")
        type_a = st.selectbox(
            "Connection Type A",
            SUPPORTED_CONNECTOR_TYPES,
            key="bush_type_a",
            label_visibility="collapsed"
        )
        size_a = st.selectbox(
            "Size A",
            CONNECTOR_SIZES.get(type_a, []),
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
            CONNECTOR_SIZES.get(type_bushing, []),
            key="bush_size_bushing",
            label_visibility="collapsed"
        )
        # Display image for bushing
        display_connector_image(type_bushing)
    
    with col3:
        st.markdown("**Fitting B**")
        type_b = st.selectbox(
            "Connection Type B",
            SUPPORTED_CONNECTOR_TYPES,
            key="bush_type_b",
            label_visibility="collapsed"
        )
        size_b = st.selectbox(
            "Size B",
            CONNECTOR_SIZES.get(type_b, []),
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
