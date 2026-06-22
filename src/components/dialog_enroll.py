import streamlit as st
import time
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

@st.dialog("➕ Join New Class")
def enroll_dialog():
    # Professional, subtle instructional text
    st.markdown("<p style='color: #64748B; margin-top: -10px; margin-bottom: 15px;'>Enter the invite code provided by your teacher to enroll in their class.</p>", unsafe_allow_html=True)
    
    join_code = st.text_input('Invite Code', placeholder='e.g. CS101', label_visibility="collapsed")
    
    st.write("<br>", unsafe_allow_html=True)

    if st.button('Enroll Now', type='primary', use_container_width=True):
        if join_code:
            with st.spinner('Verifying invite code...'):
                # 1. Verify the subject exists
                res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()
                
                if res.data:
                    subject = res.data[0]
                    student_id = st.session_state.student_data['student_id']

                    # 2. Check if the student is already enrolled
                    check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                    
                    if check.data:
                        st.warning(f"You are already enrolled in **{subject['name']}**.")
                    else:
                        # 3. Enroll the student
                        enroll_student_to_subject(student_id, subject['subject_id'])
                        st.success(f"Successfully enrolled in **{subject['name']}**!")
                        time.sleep(1.5)
                        st.rerun()
                else:
                    st.error("Invalid invite code. Please check and try again.")
        else:
            st.warning('Please enter an invite code.')