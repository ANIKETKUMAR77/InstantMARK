import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
import tempfile
import time

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.pipelines.face_pipeline import get_face_embeddings, train_classifier
from src.database.db import (
    student_login, 
    create_student, 
    get_student_dashboard_stats, 
    get_student_attendance,
    update_student_face_data,
    unenroll_student_to_subject
)
from src.components.dialog_enroll import enroll_dialog

# ==========================================
# HELPER: IMAGE TO BASE64
# ==========================================
def img_to_base64(img_array):
    """Compresses and converts an image array to a Base64 string for database storage."""
    img = Image.fromarray(img_array)
    img.thumbnail((200, 200)) # Compress for profile photo
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()

# ==========================================
# AUTHENTICATION SCREENS
# ==========================================
def student_auth_screen():
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if st.button("← Back Home", use_container_width=False, type="tertiary"):
            st.session_state['login_type'] = None
            st.rerun()
            
        st.write("<br>", unsafe_allow_html=True)
        
        login_mode = st.session_state.get('student_login_mode', 'login')
        
        if login_mode == 'login':
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center;'>🎓 Student Portal Login</h2>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                
                username = st.text_input("Username", key="s_log_user")
                password = st.text_input("Password", type="password", key="s_log_pass")
                st.divider()
                
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button('Login', type="primary", use_container_width=True):
                        student = student_login(username, password)
                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = student
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                with bc2:
                    if st.button('Register Instead', use_container_width=True):
                        st.session_state['student_login_mode'] = 'register'
                        st.rerun()
                        
        else:
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center;'>📝 Student Registration</h2>", unsafe_allow_html=True)
                
                name = st.text_input("Full Name", placeholder="e.g. John Doe", key="s_reg_name")
                username = st.text_input("Username", key="s_reg_user")
                password = st.text_input("Password", type="password", key="s_reg_pass")
                st.info("You will register your FaceID and Voice Profile from the dashboard after creating your account.")
                st.divider()
                
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button('Create Account', type="primary", use_container_width=True):
                        if name and username and password:
                            student_data = create_student(name, username, password)
                            if student_data:
                                st.success("Account created! Please log in.")
                                st.session_state['student_login_mode'] = 'login'
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Username might be taken.")
                        else:
                            st.warning("Please fill all fields.")
                with bc2:
                    if st.button('Login Instead', use_container_width=True):
                        st.session_state['student_login_mode'] = 'login'
                        st.rerun()

# ==========================================
# DASHBOARD TABS
# ==========================================
def render_overview_tab(stats):
    if stats['overall_percentage'] < 75 and stats['overall_percentage'] > 0:
        st.markdown(f"""
        <div style='background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 1rem; border-radius: 4px; margin-bottom: 2rem;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 1.5rem; margin-right: 10px;'>⚠️</span>
                <div>
                    <h4 style='color: #991B1B; margin: 0;'>Attendance Warning</h4>
                    <p style='color: #B91C1C; margin: 0;'>Your overall attendance is <strong>{stats['overall_percentage']}%</strong>. Please improve your attendance to avoid academic penalties.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Analytics Overview")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Overall Attendance", f"{stats['overall_percentage']}%")
    mc2.metric("Enrolled Subjects", len(stats['subject_stats']))
    
    total_classes = sum(s['total_classes'] for s in stats['subject_stats'])
    mc3.metric("Total Classes Conducted", total_classes)
    
    st.divider()
    
    st.markdown("### Subject Breakdown")
    for sub in stats['subject_stats']:
        pct = sub['percentage']
        color = "#10B981" if pct >= 75 else "#EF4444" 
        
        with st.container(border=True):
            st.markdown(f"""
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='font-weight: 600; color: #0F172A;'>{sub['subject_code']} - {sub['subject_name']}</span>
                    <span style='font-weight: 600; color: {color};'>{pct}%</span>
                </div>
                <div style="background-color: #E2E8F0; border-radius: 4px; width: 100%; height: 8px;">
                    <div style="background-color: {color}; width: {pct}%; height: 100%; border-radius: 4px; transition: width 0.5s ease;"></div>
                </div>
                <p style='font-size: 0.85rem; color: #64748B; margin-top: 8px; margin-bottom: 0;'>Total Classes: {sub['total_classes']}</p>
            """, unsafe_allow_html=True)

def render_history_tab(student_id):
    st.markdown("### Attendance History")
    logs = get_student_attendance(student_id)
    
    if not logs:
        st.info("No attendance records found.")
        return
        
    table_data = []
    for log in logs:
        sub = log.get('subjects', {})
        table_data.append({
            "Date": str(log.get('timestamp', ''))[:10],
            "Subject Code": sub.get('subject_code', 'N/A'),
            "Subject Name": sub.get('name', 'N/A'),
            "Status": "Present" if log.get('is_present') else "Absent"
        })
        
    df = pd.DataFrame(table_data)
    df = df.sort_values(by="Date", ascending=False)
    
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", help="Present or Absent")
        }
    )

def render_settings_tab(student_id):
    st.markdown("### Profile Settings")
    st.write("Ensure your FaceID and Voice Profile are registered for automated attendance.")
    
    st.write("<br>", unsafe_allow_html=True)
    
    # 1. Face Registration Card
    with st.container(border=True):
        st.markdown("<h4 style='color: #0F172A; margin-bottom: 10px;'>Update FaceID Profile</h4>", unsafe_allow_html=True)
        
        camera_input = st.camera_input("Capture New Face Profile", label_visibility="collapsed")
        
        if camera_input:
            if st.button("Save & Update Face Data", type="primary", use_container_width=True):
                with st.spinner("Analyzing facial features..."):
                    img_array = np.array(Image.open(camera_input))
                    encodings = get_face_embeddings(img_array)
                    
                    if encodings:
                        face_emb = encodings[0].tolist()
                        b64_photo = img_to_base64(img_array)
                        
                        update_student_face_data(student_id, face_embedding=face_emb, photo_url=b64_photo)
                        train_classifier() 
                        
                        st.session_state.student_data['profile_photo_url'] = b64_photo
                        st.success("Face data successfully updated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not detect a clear face. Please try again with better lighting.")

    st.write("<br>", unsafe_allow_html=True)

    # 2. Voice Registration Card
    with st.container(border=True):
        st.markdown("<h4 style='color: #0F172A; margin-bottom: 10px;'>Update Voice Profile</h4>", unsafe_allow_html=True)
        st.info("Record a short phrase like: 'My name is [Your Name] and I am present.'")
        
        audio_data = st.audio_input("Record Voice Sample", label_visibility="collapsed")
        
        if audio_data:
            if st.button("Save Voice Data", type="primary", use_container_width=True):
                with st.spinner("Processing voice..."):
                    from src.pipelines.voice_pipeline import get_voice_embedding
                    
                    voice_emb = get_voice_embedding(audio_data.read())
                    if voice_emb is not None:
                        # Update the database
                        from src.database.db import update_student_voice_data
                        update_student_voice_data(student_id, voice_embedding=voice_emb.tolist())
                        st.success("Voice profile updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not extract voice features. Try speaking clearly without background noise.")

# ==========================================
# MAIN DASHBOARD ENTRY
# ==========================================
def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    photo_url = student_data.get('profile_photo_url')
    
    c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        img_src = photo_url if photo_url else "https://i.ibb.co/qy0gZJg/default-avatar.png"
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; align-items: center; gap: 10px;'>
                <span style='font-weight: 500; color: #0F172A;'>{student_data['name']}</span>
                <img src='{img_src}' style='width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #E2E8F0;'/>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        if st.button("Logout", type='secondary', use_container_width=True):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data 
            st.rerun()

    hc1, hc2 = st.columns([3, 1], vertical_alignment="bottom")
    with hc1:
        st.markdown(f"<h1 style='font-size: 2rem;'>Welcome back, {student_data['name'].split()[0]}!</h1>", unsafe_allow_html=True)
    with hc2:
        if st.button('➕ Join New Class', type='primary', use_container_width=True):
            enroll_dialog()

    st.write("<br>", unsafe_allow_html=True)

    stats = get_student_dashboard_stats(student_id)
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🕒 Attendance History", "⚙️ FaceID & Profile"])
    
    with tab1:
        render_overview_tab(stats)
    with tab2:
        render_history_tab(student_id)
    with tab3:
        render_settings_tab(student_id)

# ==========================================
# SCREEN ROUTER
# ==========================================
def student_screen():
    style_background_dashboard()
    style_base_layout()

    if st.session_state.get("is_logged_in") and st.session_state.get("user_role") == 'student':
        student_dashboard()
    else:
        student_auth_screen()