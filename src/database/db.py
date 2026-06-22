from src.database.config import supabase
import bcrypt
from datetime import datetime

# ==========================================
# AUTHENTICATION & SECURITY
# ==========================================
def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    # Fallback to False if hashed password is empty or invalid
    if not hashed: return False
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

# ==========================================
# TEACHER OPERATIONS
# ==========================================
def check_teacher_exists(username):
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0 

def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher.get('password', '')):
            return teacher
    return None

def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'][:10] for log in attendance)) # Group by YYYY-MM-DD
        sub['total_classes'] = unique_sessions

        sub.pop('subject_students', None)
        sub.pop('attendance_logs', None)
    return subjects

# --- NEW: Teacher Analytics Engine ---
def get_teacher_dashboard_stats(teacher_id):
    """Calculates enterprise-grade metrics for the teacher dashboard."""
    subjects = get_teacher_subjects(teacher_id)
    logs = get_attendance_for_teacher(teacher_id)
    
    total_students = sum(sub['total_students'] for sub in subjects)
    total_classes = sum(sub['total_classes'] for sub in subjects)
    
    # Calculate average attendance
    total_logs = len(logs)
    present_logs = sum(1 for log in logs if log.get('is_present', False))
    avg_attendance = (present_logs / total_logs * 100) if total_logs > 0 else 0

    return {
        "total_subjects": len(subjects),
        "total_students_enrolled": total_students,
        "total_classes_conducted": total_classes,
        "average_attendance": round(avg_attendance, 2)
    }

def get_datewise_attendance(teacher_id):
    """Fetches attendance grouped by Date and Subject for the Advanced Data Table"""
    response = supabase.table('attendance_logs').select("*, subjects!inner(name, subject_code, teacher_id)").eq('subjects.teacher_id', teacher_id).order('timestamp', desc=True).execute()
    return response.data

# ==========================================
# STUDENT OPERATIONS
# ==========================================
def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

# --- UPDATED: Student Creation now supports Username/Password/Profile Photo ---
def create_student(new_name, username, password, face_embedding=None, voice_embedding=None, photo_url=None):
    data = {
        'name': new_name, 
        'username': username,
        'password': hash_pass(password) if password else None,
        'face_embedding': face_embedding, 
        'voice_embedding': voice_embedding,
        'profile_photo_url': photo_url
    }
    response = supabase.table('students').insert(data).execute()
    return response.data

# --- NEW: Student Login ---
def student_login(username, password):
    response = supabase.table("students").select("*").eq("username", username).execute()
    if response.data:
        student = response.data[0]
        if check_pass(password, student.get('password', '')):
            return student
    return None

# --- NEW: Face Re-registration & Profile Photo Update ---
def update_student_face_data(student_id, face_embedding=None, photo_url=None):
    data = {}
    if face_embedding is not None:
        data['face_embedding'] = face_embedding
    if photo_url is not None:
        data['profile_photo_url'] = photo_url
        
    if not data: return None
    
    response = supabase.table('students').update(data).eq('student_id', student_id).execute()
    return response.data

def enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response = supabase.table('subject_students').insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id, subject_id):
    response = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data

def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data

def get_student_attendance(student_id):
    response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data

# --- NEW: Student Analytics Engine ---
def get_student_dashboard_stats(student_id):
    """Calculates overall and subject-wise percentages for the Student Dashboard warnings."""
    logs = get_student_attendance(student_id)
    subjects = get_student_subjects(student_id)
    
    total_logs = len(logs)
    present_logs = sum(1 for log in logs if log.get('is_present', False))
    overall_percentage = (present_logs / total_logs * 100) if total_logs > 0 else 0
    
    subject_stats = []
    for sub in subjects:
        sub_info = sub.get('subjects', {})
        sub_id = sub_info.get('subject_id')
        sub_logs = [log for log in logs if log.get('subject_id') == sub_id]
        
        s_total = len(sub_logs)
        s_present = sum(1 for log in sub_logs if log.get('is_present', False))
        s_pct = (s_present / s_total * 100) if s_total > 0 else 0
        
        subject_stats.append({
            "subject_name": sub_info.get('name', 'Unknown'),
            "subject_code": sub_info.get('subject_code', ''),
            "percentage": round(s_pct, 2),
            "total_classes": s_total
        })
        
    return {
        "overall_percentage": round(overall_percentage, 2),
        "subject_stats": subject_stats
    }

# ==========================================
# ATTENDANCE CORE
# ==========================================
def create_attendance(logs):
    response = supabase.table('attendance_logs').insert(logs).execute()
    return response.data

def get_attendance_for_teacher(teacher_id):
    response = supabase.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
    return response.data

def update_student_voice_data(student_id, voice_embedding):
    """Updates a student's voice embedding in the database."""
    try:
        data = {"voice_embedding": voice_embedding}
        response = supabase.table('students').update(data).eq('student_id', student_id).execute()
        return response.data
    except Exception as e:
        print(f"Error updating voice data: {e}")
        return None