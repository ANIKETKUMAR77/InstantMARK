import streamlit as st
from src.ui.base_layout import style_background_home, style_base_layout
from src.components.header import header_home

def home_screen():
    # Inject global styles
    style_background_home()
    style_base_layout()
    
    # Render the newly fixed logo
    header_home()
    
    # Use columns to perfectly center the login cards on the screen
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1], gap="large")
    
    with c2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>🎓 Student Portal</h3>", unsafe_allow_html=True)
            st.write("<p style='text-align: center; color: #64748B; font-size: 0.95rem;'>View your attendance records and register your FaceID.</p>", unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)
            
            if st.button("Login as Student", type="primary", use_container_width=True):
                st.session_state['login_type'] = 'student'
                st.rerun()

    with c3:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'>👨‍🏫 Teacher Portal</h3>", unsafe_allow_html=True)
            st.write("<p style='text-align: center; color: #64748B; font-size: 0.95rem;'>Manage classes, generate reports, and run AI roll call.</p>", unsafe_allow_html=True)
            st.write("<br>", unsafe_allow_html=True)
            
            if st.button("Login as Teacher", type="secondary", use_container_width=True):
                st.session_state['login_type'] = 'teacher'
                st.rerun()