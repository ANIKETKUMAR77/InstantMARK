import streamlit as st
import time
from src.database.db import create_subject

@st.dialog("📚 Create New Subject")
def create_subject_dialog(teacher_id):
    # Professional, subtle instructional text
    st.markdown("<p style='color: #64748B; margin-top: -10px; margin-bottom: 15px;'>Enter the details to create a new class and generate an invite code for your students.</p>", unsafe_allow_html=True)
    
    sub_id = st.text_input("Subject Code", placeholder="e.g. CS101")
    sub_name = st.text_input("Subject Name", placeholder="e.g. Machine Learning")
    sub_section = st.text_input("Section", placeholder="e.g. A, B, or Online")

    st.write("<br>", unsafe_allow_html=True)

    if st.button("Create Subject", type='primary', use_container_width=True):
        if sub_id and sub_name and sub_section:
            with st.spinner("Creating subject..."):
                try:
                    create_subject(sub_id, sub_name, sub_section, teacher_id)
                    st.success(f"Successfully created **{sub_id} - {sub_name}**!")
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    # Make SQL duplicate key errors more readable for the user
                    error_msg = str(e).lower()
                    if "duplicate key" in error_msg or "unique constraint" in error_msg:
                        st.error(f"A subject with the code '{sub_id}' already exists. Please use a unique code.")
                    else:
                        st.error(f"An unexpected error occurred: {str(e)}")
        else:
            st.warning("Please fill out all fields before creating.")