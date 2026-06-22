import streamlit as st
import pandas as pd
from datetime import datetime

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result

@st.dialog('🎙️ Voice Roll Call')
def voice_attendance_dialog(selected_subject_id):
    # Professional instructional text
    st.markdown("<p style='color: #64748B; margin-top: -10px; margin-bottom: 15px;'>Record the classroom audio as students say 'Present'. The AI will analyze voice biometrics to mark attendance.</p>", unsafe_allow_html=True)

    audio_data = st.audio_input("Record classroom audio", label_visibility="collapsed")
    
    st.write("<br>", unsafe_allow_html=True)

    if st.button('Analyze Audio', type='primary', use_container_width=True):
        if not audio_data:
            st.warning("Please record audio before analyzing.")
            return
            
        with st.spinner('Processing voice biometrics...'):
            enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No students are enrolled in this course.')
                return
                
            candidates_dict = {
                s['students']['student_id']: s['students']['voice_embedding'] 
                for s in enrolled_students if s['students'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('No enrolled students have voice profiles registered.')
                return
            
            audio_bytes = audio_data.read()
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Confidence Score": f"{score:.2f}" if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present)
                })
                
            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)