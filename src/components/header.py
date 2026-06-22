import streamlit as st
import base64
import os

def get_image_base64(image_path):
    """Safely reads a local image file and converts it to a base64 string."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def header_home():
    """Large, centered hero header for the main login/landing page."""
    logo_b64 = get_image_base64("logo.png")
    
    # Increased height to 120px to accommodate the text inside the logo image
    img_tag = f"<img src='data:image/png;base64,{logo_b64}' style='height: 120px; margin-bottom: 5px;' />" if logo_b64 else ""
    
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 40px; margin-bottom: 40px;">
            {img_tag}
            <p style='color: #64748B; font-size: 1.1rem; margin-top: 10px; font-weight: 400;'>Enterprise Attendance System</p>
        </div>   
    """, unsafe_allow_html=True)

def header_dashboard():
    """Compact, horizontal header for the Teacher and Student dashboards."""
    logo_b64 = get_image_base64("logo.png")
    
    # Clean, logo-only top bar
    img_tag = f"<img src='data:image/png;base64,{logo_b64}' style='height: 45px;' />" if logo_b64 else ""
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #E2E8F0;">
            {img_tag}
        </div>   
    """, unsafe_allow_html=True)