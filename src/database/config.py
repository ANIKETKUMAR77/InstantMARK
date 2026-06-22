import streamlit as st
from supabase import create_client, Client

@st.cache_resource(show_spinner=False)
def init_connection() -> Client:
    """
    Initialize the Supabase client as a cached resource.
    This prevents creating a new connection on every Streamlit rerun,
    drastically improving performance and reducing database load.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("🚨 Configuration Error: Missing Supabase credentials. Please check your secrets.toml file.")
        st.stop()
    except Exception as e:
        st.error(f"🚨 Database Connection Failed: {str(e)}")
        st.stop()

# Export the singleton instance to be imported by db.py and other modules
supabase: Client = init_connection()