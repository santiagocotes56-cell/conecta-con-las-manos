import streamlit as st
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datos import get_progreso, LECCIONES, LECCIONES_DICCIONARIO, PUNTOS_BARRA, CATEGORIAS

st.set_page_config(page_title="Mi Progreso", page_icon="📊", layout="centered")
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{background:#08080c!important}
[data-testid="stSidebar"]{display:none}
h1,h2,h3,p,label,span{color:#fff!important}
div[data-testid="stButton"]>button{
    font-weight:900;border-radius:14px;border:2px solid #6a3bcc;
    width:100%;background:#02c0fc;color:#08080c!important}
.cat-badge{font-size:2rem;font-weight:900;color:#02c0fc!important;text-align:center}
</style>
""", unsafe_allow_html=True)

if st.button("← Inicio"):
    st.switch_page("Inicio.py")

st.markdown("## 📊 Mi Progreso")

p = get_progreso()

# ── Categoría y barra ────────────────────────────────────────────────────────
st.markdown(f'<p class="cat-badge">🏅 {p["categoria"]}</p>', unsafe_allow_html=True)
st.progress(min(p["puntos"] / PUNTOS_BARRA, 1.0),
            text=f'{p["puntos"]} / {PUNTOS_BARRA} puntos para subir de categoría')

st.metric("Lecciones jugadas", p["lecciones_jugadas"])
st.markdown("---")

# ── Lecciones JUGAR ──────────────────────────────────────────────────────────
st.markdown("### 🎮 Jugar")
cols = st.columns(3)
for i, lec in enumerate(LECCIONES):
    puntaje = p["historial"].get(str(lec["numero"]))
    with cols[i % 3]:
        if puntaje is not None:
            st.markdown(f"**{lec['numero']}. {lec['nombre']}**")
            st.progress(puntaje / 100, text=f"{puntaje}/100")
        else:
            st.markdown(f"🔒 {lec['numero']}. {lec['nombre']}")

st.markdown("---")

# ── Lecciones DICCIONARIO ────────────────────────────────────────────────────
st.markdown("### 📖 Diccionario")
for lec in LECCIONES_DICCIONARIO:
    completada = str(lec["numero"]) in p["historial_dic"]
    icono = "✅" if completada else "🔒"
    st.markdown(f"{icono} **{lec['numero']}. {lec['nombre']}**")
