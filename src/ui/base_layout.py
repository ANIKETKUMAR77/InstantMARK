import streamlit as st

def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background: #F8FAFC !important;
            }
            .stApp div[data-testid="stColumn"] {
                background-color: transparent !important;
                padding: 1rem !important;
                border-radius: 0 !important;
            }
        </style>  
    """, unsafe_allow_html=True)
    
def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: #F8FAFC !important;
            }
        </style>  
    """, unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        #MainMenu, footer, header {
            visibility: hidden;
        }
            
        .block-container {
            padding-top: 2rem !important;
            max-width: 1200px !important;
        }

        /* Global Typography */
        html, body, [class*="css"], p, span {
            font-family: 'Inter', sans-serif !important;
            color: #475569 !important;
        }

        /* RESTORE STREAMLIT ICONS */
        .material-symbols-rounded, 
        span[class*="material-symbols"], 
        i[class*="material-symbols"] {
            font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        }

        h1, h2, h3, h4 {
            font-family: 'Inter', sans-serif !important;
            color: #0F172A !important;
            letter-spacing: -0.025em !important;
        }

        h1 { font-size: 2.5rem !important; font-weight: 700 !important; line-height: 1.2 !important; margin-bottom: 0.5rem !important; }
        h2 { font-size: 1.75rem !important; font-weight: 600 !important; line-height: 1.2 !important; margin-bottom: 0.5rem !important; }

        button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease-in-out !important;
        }

        /* Primary Button (Dark Slate with WHITE text constraint) */
        button[kind="primary"] {
            background-color: #0F172A !important;
            border: none !important;
        }
        button[kind="primary"] * {
            color: #FFFFFF !important; 
        }
        button[kind="primary"]:hover {
            background-color: #1E293B !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }

        /* Secondary Button (White outline with DARK text constraint) */
        button[kind="secondary"] {
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
        }
        button[kind="secondary"] * {
            color: #0F172A !important; 
        }
        button[kind="secondary"]:hover {
            background-color: #F8FAFC !important;
            border-color: #94A3B8 !important;
            transform: translateY(-1px) !important;
        }

        button[kind="tertiary"] {
            background-color: transparent !important;
            border: none !important;
        }
        button[kind="tertiary"] * {
             color: #64748B !important;
        }
        button[kind="tertiary"]:hover {
            background-color: #F1F5F9 !important;
        }
        button[kind="tertiary"]:hover * {
            color: #0F172A !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1) !important;
            background-color: #FFFFFF !important;
            padding: 1.5rem !important;
        }

        [data-testid="stDataFrame"] {
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
        }
        </style>  
    """, unsafe_allow_html=True)