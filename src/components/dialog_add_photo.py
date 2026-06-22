import streamlit as st
from PIL import Image
import time

@st.dialog("📸 Add Classroom Photos")
def add_photos_dialog():
    # Professional, subtle instructional text
    st.markdown("<p style='color: #64748B; margin-top: -10px; margin-bottom: 15px;'>Capture live photos or upload existing images of your classroom to run AI attendance.</p>", unsafe_allow_html=True)

    # Ensure the image queue exists in state
    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    # Use native Streamlit tabs instead of manual state buttons for a cleaner UI
    tab1, tab2 = st.tabs(["📸 Camera Capture", "📂 Upload Files"])

    with tab1:
        cam_photo = st.camera_input('Take Snapshot', label_visibility="collapsed")
        if cam_photo:
            # Explicit confirmation button prevents Streamlit auto-rerun loops
            if st.button("Add Snapshot to Batch", type="primary", use_container_width=True, key="add_cam"):
                st.session_state.attendance_images.append(Image.open(cam_photo))
                st.success("Photo added to batch!")
                time.sleep(1)
                st.rerun()

    with tab2:
        uploaded_files = st.file_uploader('Choose image files', type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, label_visibility="collapsed")
        
        if uploaded_files:
            if st.button(f"Add {len(uploaded_files)} Photos to Batch", type="primary", use_container_width=True, key="add_up"):
                for f in uploaded_files:
                    st.session_state.attendance_images.append(Image.open(f))
                
                st.success(f"{len(uploaded_files)} photos added to batch!")
                time.sleep(1)
                st.rerun()

    st.divider()
    
    # Display current queue status
    current_count = len(st.session_state.attendance_images)
    st.markdown(f"<p style='text-align: center; color: #0F172A; font-weight: 600; font-size: 0.95rem; margin-bottom: 15px;'>Currently queued: {current_count} photos</p>", unsafe_allow_html=True)
    
    # Secondary button to close dialog
    if st.button('Done', use_container_width=True):
        st.rerun()