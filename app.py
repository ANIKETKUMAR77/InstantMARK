import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

from src.components.dialog_auto_enroll import auto_enroll_dialog

def inject_enterprise_styles():
    """
    Injects global CSS to override Streamlit defaults and enforce 
    a modern, clean, enterprise SaaS aesthetic (e.g., Notion, Google Workspace).
    """
    st.markdown("""
        <style>
        /* Import Inter Font for a modern SaaS look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Font and Background */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Clean Light Theme Background */
        .stApp {
            background-color: #F8FAFC; 
        }
        
        /* Hide Streamlit Default UI Elements for a white-label feel */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {
            background: transparent;
        }
        
        /* Standardize Container Cards (Soft shadows, rounded corners) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            background-color: #FFFFFF !important;
            padding: 1.5rem !important;
        }
        
        /* Modern Premium Buttons */
        .stButton button[type="primary"] {
            background-color: #0F172A !important; /* Slate 900 */
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[type="primary"]:hover {
            background-color: #1E293B !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stButton button[type="secondary"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[kind="secondary"]:hover {
            border-color: #94A3B8 !important;
            background-color: #F1F5F9 !important;
        }
        
        /* Smooth text inputs */
        div[data-baseweb="input"] {
            border-radius: 6px !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #0F172A !important;
            box-shadow: 0 0 0 1px #0F172A !important;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    # 1. Global Page Configuration
    st.set_page_config(
        page_title='InstantMARK | Enterprise Attendance',
        page_icon="icon.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 2. Inject SaaS UI Styles
    inject_enterprise_styles()

    # 3. State Management
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    # 4. Routing
    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()

    # 5. Join Code / Auto-Enroll Logic
    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type = 'student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            auto_enroll_dialog(join_code)

if __name__ == "__main__":
    main()