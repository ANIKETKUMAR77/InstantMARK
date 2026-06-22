import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card

from src.database.db import (
    check_teacher_exists, 
    create_teacher, 
    teacher_login, 
    get_teacher_subjects, 
    get_attendance_for_teacher,
    get_teacher_dashboard_stats,
    get_datewise_attendance,
    get_all_students
)

from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.database.config import supabase

# ==========================================
# AUTHENTICATION SCREENS
# ==========================================
def teacher_auth_screen():
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if st.button("← Back Home", use_container_width=False, type="tertiary"):
            st.session_state['login_type'] = None
            st.rerun()
            
        st.write("<br>", unsafe_allow_html=True)
        
        login_mode = st.session_state.get('teacher_login_mode', 'login')
        
        if login_mode == 'login':
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center;'>👨‍🏫 Teacher Portal Login</h2>", unsafe_allow_html=True)
                st.write("<br>", unsafe_allow_html=True)
                
                username = st.text_input("Username", key="t_log_user")
                password = st.text_input("Password", type="password", key="t_log_pass")
                st.divider()
                
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button('Login', type="primary", use_container_width=True):
                        teacher = teacher_login(username, password)
                        if teacher:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'teacher'
                            st.session_state.teacher_data = teacher
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                with bc2:
                    if st.button('Register Instead', use_container_width=True):
                        st.session_state['teacher_login_mode'] = 'register'
                        st.rerun()
                        
        else:
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center;'>📝 Teacher Registration</h2>", unsafe_allow_html=True)
                
                name = st.text_input("Full Name", placeholder="e.g. Dr. Sarah Smith", key="t_reg_name")
                username = st.text_input("Username", key="t_reg_user")
                password = st.text_input("Password", type="password", key="t_reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password", key="t_reg_pass_conf")
                st.divider()
                
                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button('Create Account', type="primary", use_container_width=True):
                        if not all([name, username, password, confirm_password]):
                            st.warning("All fields are required.")
                        elif password != confirm_password:
                            st.error("Passwords do not match.")
                        elif check_teacher_exists(username):
                            st.error("Username is already taken.")
                        else:
                            create_teacher(username, password, name)
                            st.success("Account created! Please log in.")
                            st.session_state['teacher_login_mode'] = 'login'
                            import time
                            time.sleep(1)
                            st.rerun()
                with bc2:
                    if st.button('Login Instead', use_container_width=True):
                        st.session_state['teacher_login_mode'] = 'login'
                        st.rerun()


# ==========================================
# DASHBOARD TABS
# ==========================================
def render_analytics_tab(teacher_id):
    st.markdown("### Enterprise Analytics")
    stats = get_teacher_dashboard_stats(teacher_id)
    
    # 1. Top Metrics
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Subjects", stats['total_subjects'])
    mc2.metric("Enrolled Students", stats['total_students_enrolled'])
    mc3.metric("Classes Conducted", stats['total_classes_conducted'])
    mc4.metric("Avg. Attendance", f"{stats['average_attendance']}%")
    
    st.divider()
    
    # 2. Student Analytics Engine
    st.markdown("#### Comprehensive Student Performance")
    logs = get_attendance_for_teacher(teacher_id)
    all_students = get_all_students()
    student_map = {s['student_id']: s['name'] for s in all_students}
    
    if logs:
        student_stats = {}
        for log in logs:
            sid = log['student_id']
            sub_name = log['subjects']['name']
            
            if sid not in student_stats:
                student_stats[sid] = {"Name": student_map.get(sid, f"ID: {sid}"), "Total Classes": 0, "Attended": 0, "Subjects": set()}
            
            student_stats[sid]["Total Classes"] += 1
            student_stats[sid]["Subjects"].add(sub_name)
            if log.get('is_present'):
                student_stats[sid]["Attended"] += 1
                
        # Build Dataframe
        data = []
        for sid, d in student_stats.items():
            pct = (d["Attended"] / d["Total Classes"] * 100) if d["Total Classes"] > 0 else 0
            status = "🔴 At Risk" if pct < 75 else "🟢 Good"
            data.append({
                "Student Name": d["Name"],
                "Enrolled Subjects": ", ".join(list(d["Subjects"])),
                "Classes Attended": d["Attended"],
                "Total Classes": d["Total Classes"],
                "Attendance %": f"{pct:.1f}%",
                "Status": status
            })
            
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No attendance data available yet to generate analytics.")

def render_take_attendance_tab(teacher_id):
    st.markdown("### Take AI Attendance")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You haven\'t created any subjects yet. Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))
    with col2:
        if st.button('📸 Add Photos', type='primary', use_container_width=True):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]
    st.divider()

    if st.session_state.attendance_images:
        st.markdown("#### Added Photos")
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, use_container_width=True, caption=f'Photo {idx+1}')
                
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', use_container_width=True, type='tertiary', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', use_container_width=True, type='secondary', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    # Safely indented inside the 'else' block!
                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('🎙️ Use Voice Attendance', type='primary', use_container_width=True):
            voice_attendance_dialog(selected_subject_id)


def render_manage_subjects_tab(teacher_id):
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        st.markdown("### Manage Subjects")
    with col2:
        if st.button('➕ Create Subject', use_container_width=True, type='primary'):
            create_subject_dialog(teacher_id)

    st.write("<br>", unsafe_allow_html=True)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students Enrolled", sub['total_students']),
                ("🕰️", "Classes Held", sub['total_classes']),
            ]
            def share_btn():
                # Key is restored, icon is removed, emoji is added!
                if st.button("🔗 Share Invite Code", key=f"share_{sub['subject_code']}", use_container_width=True):
                    share_subject_dialog(sub['name'], sub['subject_code'])

            with st.container(border=True):
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=stats,
                    footer_callback=share_btn
                )
    else:
        st.info("No subjects found. Create one to get started.")


def render_attendance_records_tab(teacher_id):
    st.markdown("### Session Logs & Reports")
    records = get_datewise_attendance(teacher_id)

    if not records:
        st.info("No attendance records found.")
        return
    
    # Pre-process mapping
    all_students = get_all_students()
    student_map = {s['student_id']: s['name'] for s in all_students}

    # Group records by Session (Timestamp + Subject)
    sessions = {}
    for r in records:
        ts_raw = r.get('timestamp')
        if not ts_raw: continue
        
        # Group by exact minute to bundle a single class session
        session_key = ts_raw[:16] 
        sub_name = r['subjects']['name']
        sub_code = r['subjects']['subject_code']
        uid = f"{session_key} | {sub_code}"
        
        if uid not in sessions:
            sessions[uid] = {
                "Date": datetime.fromisoformat(ts_raw).strftime("%b %d, %Y - %I:%M %p"),
                "Subject": f"{sub_code} - {sub_name}",
                "Total": 0,
                "Present": 0,
                "Records": []
            }
            
        sessions[uid]["Total"] += 1
        is_pres = bool(r.get('is_present', False))
        if is_pres: sessions[uid]["Present"] += 1
        
        # Save specific student record for the drill-down
        sessions[uid]["Records"].append({
            "Student Name": student_map.get(r['student_id'], f"ID: {r['student_id']}"),
            "Status": "✅ Present" if is_pres else "❌ Absent"
        })

    # 1. Summary Table
    st.markdown("#### Session Summary")
    summary_data = []
    for uid, data in sessions.items():
        pct = (data["Present"] / data["Total"] * 100) if data["Total"] > 0 else 0
        summary_data.append({
            "Session ID": uid,
            "Date & Time": data["Date"],
            "Subject": data["Subject"],
            "Present": f"{data['Present']} / {data['Total']}",
            "Attendance %": f"{pct:.1f}%"
        })
        
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary.drop(columns=["Session ID"]), use_container_width=True, hide_index=True)
    
    st.divider()

    # 2. Drill-down Specifics
    st.markdown("#### Detailed Roll Call")
    selected_session = st.selectbox("Select a session to view roll call:", options=list(sessions.keys()), format_func=lambda x: sessions[x]["Date"] + " | " + sessions[x]["Subject"])
    
    if selected_session:
        detail_df = pd.DataFrame(sessions[selected_session]["Records"])
        detail_df = detail_df.sort_values(by="Student Name")
        st.dataframe(detail_df, use_container_width=True, hide_index=True)


# ==========================================
# MAIN ROUTER
# ==========================================
def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    teacher_id = teacher_data['teacher_id']
    
    # --- Top Navigation Bar ---
    c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment='center')
    with c1:
        header_dashboard()
    with c2:
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; align-items: center; gap: 10px;'>
                <span style='font-weight: 500; color: #0F172A;'>{teacher_data['name']}</span>
                <div style='width: 40px; height: 40px; border-radius: 50%; background-color: #2563EB; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;'>
                    {teacher_data['name'][0].upper()}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        if st.button("Logout", type='secondary', use_container_width=True):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()

    st.write("<br>", unsafe_allow_html=True)

    # --- Modern Tab Navigation ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview & Analytics", "📸 Take Attendance", "📚 Manage Subjects", "📋 Session Logs"])
    
    with tab1:
        render_analytics_tab(teacher_id)
    with tab2:
        render_take_attendance_tab(teacher_id)
    with tab3:
        render_manage_subjects_tab(teacher_id)
    with tab4:
        render_attendance_records_tab(teacher_id)

    footer_dashboard()


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if st.session_state.get("is_logged_in") and st.session_state.get("user_role") == 'teacher':
        teacher_dashboard()
    else:
        teacher_auth_screen()