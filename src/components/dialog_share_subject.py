import streamlit as st
import segno
import io

@st.dialog("🔗 Share Class Invite")
def share_subject_dialog(subject_name, subject_code):
    # Update this domain when you deploy InstantMARK to your new Streamlit URL!
    app_domain = "https://instantmark.streamlit.app" 
    join_url = f"{app_domain}/?join-code={subject_code}"

    # Professional, dynamic instructional text
    st.markdown(f"<p style='color: #64748B; margin-top: -10px; margin-bottom: 20px;'>Invite students to <strong>{subject_name}</strong> using the code, direct link, or QR code below.</p>", unsafe_allow_html=True)

    # Generate QR Code
    qr = segno.make(join_url)
    out = io.BytesIO()
    # Light parameter set to white to ensure it scans perfectly against our gray dashboard background
    qr.save(out, kind='png', scale=8, border=2, light="#FFFFFF")

    # Clean 2-column layout
    col1, col2 = st.columns([1, 1], gap="large", vertical_alignment="center")

    with col1:
        st.markdown("<h4 style='color: #0F172A; font-size: 1rem; margin-bottom: 5px;'>Invite Code</h4>", unsafe_allow_html=True)
        st.code(subject_code, language="text")
        
        st.markdown("<h4 style='color: #0F172A; font-size: 1rem; margin-bottom: 5px; margin-top: 15px;'>Direct Link</h4>", unsafe_allow_html=True)
        st.code(join_url, language="text")
        
        st.caption("Copy to share via WhatsApp, Teams, or Email.")

    with col2:
        # Wrap QR code in a clean styling box
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; border: 1px solid #E2E8F0; padding: 10px; border-radius: 12px; background: white;'>
        """, unsafe_allow_html=True)
        st.image(out.getvalue(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 10px; margin-bottom: 0;'>Scan with mobile camera to join</p>", unsafe_allow_html=True)