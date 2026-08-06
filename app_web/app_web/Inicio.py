import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="Conecta con las Manos",
    page_icon="🤟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Estilos globales ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #08080c !important;
}
[data-testid="stSidebar"] { display: none; }

h1, h2, h3, p, label, span {
    font-family: 'Nunito', sans-serif !important;
    color: #ffffff !important;
}

div[data-testid="stButton"] > button {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 900;
    font-size: 1.1rem;
    border-radius: 14px;
    border: 2px solid #6a3bcc;
    padding: 0.6rem 0;
    width: 100%;
    background: #02c0fc;
    color: #08080c !important;
    transition: background 0.2s;
}
div[data-testid="stButton"] > button:hover {
    background: #6a3bcc;
    color: #fff !important;
}
.card {
    background: #13131a;
    border: 2px solid #6a3bcc;
    border-radius: 18px;
    padding: 2rem 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.titulo-app {
    font-family: 'Nunito', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: #02c0fc !important;
    text-align: center;
    margin-bottom: 0;
}
.sub {
    text-align: center;
    color: #aaaacc !important;
    font-size: 1rem;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Logo ────────────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.image(logo, use_container_width=True)
else:
    st.markdown('<p class="titulo-app">🤟 Conecta con las Manos</p>', unsafe_allow_html=True)

st.markdown('<p class="sub">Aprende lengua de señas jugando</p>', unsafe_allow_html=True)

# ── Botones de navegación ────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("🎮  JUGAR", use_container_width=True):
        st.switch_page("pages/1_Jugar.py")
with col2:
    if st.button("📖  DICCIONARIO", use_container_width=True):
        st.switch_page("pages/2_Diccionario.py")

st.markdown("<br>", unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    if st.button("📊  MI PROGRESO", use_container_width=True):
        st.switch_page("pages/3_Progreso.py")
with col4:
    if st.button("ℹ️  CÓMO JUGAR", use_container_width=True):
        st.switch_page("pages/4_Ayuda.py")
