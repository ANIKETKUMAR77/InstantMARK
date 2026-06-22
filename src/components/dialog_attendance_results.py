import streamlit as st
import time
from src.database.db import create_attendance

def show_attendance_result(df, logs):
    # Professional instructional text
    st.markdown("<p style='color: #64748B; margin-top: -10px; margin-bottom: 15px;'>Please review the AI-generated attendance report before saving it to the database.</p>", unsafe_allow_html=True)
    
    # Modernized dataframe rendering
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.write("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        if st.button('Discard', use_container_width=True):
            # Clear state to cancel the operation
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button('Confirm & Save', use_container_width=True, type='primary'):
            with st.spinner('Syncing to database...'):
                try:
                    create_attendance(logs)
                    st.success("✅ Attendance successfully saved!")
                    # Clear state after successful save
                    st.session_state.attendance_images = []
                    st.session_state.voice_attendance_results = None
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Sync failed: {str(e)}")

@st.dialog("📋 Review Attendance Report")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)