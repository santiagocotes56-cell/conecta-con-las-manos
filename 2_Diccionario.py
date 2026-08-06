import streamlit as st
import os, random, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datos import (LECCIONES_DICCIONARIO, FRASES,
                   dic_desbloqueada, guardar_completado_dic)

st.set_page_config(page_title="Diccionario – Conecta con las Manos", page_icon="📖", layout="centered")

st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{background:#08080c!important}
[data-testid="stSidebar"]{display:none}
h1,h2,h3,p,label,span{color:#fff!important}
div[data-testid="stButton"]>button{
    font-weight:900;border-radius:14px;border:2px solid #6a3bcc;
    width:100%;background:#02c0fc;color:#08080c!important}
div[data-testid="stButton"]>button:hover{background:#6a3bcc;color:#fff!important}
div[data-testid="stButton"]>button:disabled{background:#2a2a35!important;color:#666!important;border-color:#444!important}
.significado{font-size:1.8rem;font-weight:900;text-align:center;
    color:#02c0fc!important;padding:0.5rem 0 1rem 0}
.opcion-ok{background:#00dc64!important;color:#000!important}
.opcion-mal{background:#dc3232!important;color:#fff!important}
</style>
""", unsafe_allow_html=True)

VIDEOS_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "videos")
RONDAS_POR_LECCION = 5

# ── Estado ───────────────────────────────────────────────────────────────────
def init():
    defaults = {
        "dic_pantalla":   "seleccion",   # seleccion|aprendizaje|desafio|resultado
        "dic_leccion":    None,
        "dic_ronda":      0,             # 0-4
        "dic_grupo":      [],            # 3 frases de la ronda actual
        "dic_vid_idx":    0,             # índice dentro del grupo (aprendizaje)
        "dic_desafio_q":  0,             # pregunta dentro del desafío (0-2)
        "dic_desafio_ord":[],            # orden aleatorio de las 3 frases para el desafío
        "dic_opciones":   [],
        "dic_correcta":   "",
        "dic_respuesta":  None,          # None | "ok" | "mal"
        "dic_rondas_ok":  0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

def video_url(archivo):
    """Ruta local del video (Streamlit sirve archivos estáticos de la carpeta del proyecto)."""
    return os.path.join(VIDEOS_BASE, archivo)

def preparar_ronda(leccion, num_ronda):
    """Saca el grupo de 3 frases correspondiente a la ronda."""
    todas = leccion["frases"]
    grupos = [todas[i:i+3] for i in range(0, len(todas), 3)]
    if num_ronda < len(grupos):
        return grupos[num_ronda]
    return []

def generar_opciones(correcta, frases_todas, grupo_actual):
    textos_grupo = {f["texto"] for f in grupo_actual}
    pool = [f for f in frases_todas if f["texto"] not in textos_grupo]
    if len(pool) < 2:
        pool = [f for f in frases_todas if f["texto"] != correcta["texto"]]
    distractoras = random.sample(pool, min(2, len(pool)))
    ops = [correcta["texto"]] + [d["texto"] for d in distractoras]
    random.shuffle(ops)
    return ops

# ════════════════════════════════════════════════════════════════════════════
# SELECCIÓN DE LECCIÓN
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.dic_pantalla == "seleccion":
    st.markdown("## 📖 Diccionario — elige una lección")
    if st.button("← Inicio"):
        st.switch_page("Inicio.py")
    st.markdown("---")

    cols = st.columns(2)
    for i, lec in enumerate(LECCIONES_DICCIONARIO):
        desbloqueada = dic_desbloqueada(lec["numero"])
        with cols[i % 2]:
            label = f"{'🔓' if desbloqueada else '🔒'} {lec['numero']}. {lec['nombre']}"
            if st.button(label, disabled=not desbloqueada, key=f"dic_{lec['numero']}"):
                st.session_state.dic_leccion   = lec
                st.session_state.dic_ronda     = 0
                st.session_state.dic_vid_idx   = 0
                st.session_state.dic_rondas_ok = 0
                st.session_state.dic_grupo     = preparar_ronda(lec, 0)
                st.session_state.dic_pantalla  = "aprendizaje"
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# APRENDIZAJE: ver los 3 videos uno a uno
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.dic_pantalla == "aprendizaje":
    lec    = st.session_state.dic_leccion
    ronda  = st.session_state.dic_ronda
    grupo  = st.session_state.dic_grupo
    vidx   = st.session_state.dic_vid_idx

    total_rondas = RONDAS_POR_LECCION

    st.markdown(f"### 📖 {lec['nombre']} — Ronda {ronda+1} de {total_rondas}")
    st.progress((ronda) / total_rondas)
    st.markdown(f"**Aprende estas señas** · Video {vidx+1} de {len(grupo)}")
    st.markdown("---")

    if vidx < len(grupo):
        frase = grupo[vidx]
        st.markdown(f'<p class="significado">✋ {frase["texto"]}</p>', unsafe_allow_html=True)

        ruta_video = video_url(frase["archivo"])
        if os.path.exists(ruta_video):
            st.video(ruta_video, loop=True, autoplay=True, muted=True)
        else:
            st.warning(f"Video `{frase['archivo']}` no encontrado en la carpeta `videos/`.")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("SIGUIENTE ›", use_container_width=True):
                if vidx + 1 < len(grupo):
                    st.session_state.dic_vid_idx += 1
                else:
                    # Preparar desafío
                    orden = grupo[:]
                    random.shuffle(orden)
                    st.session_state.dic_desafio_ord = orden
                    st.session_state.dic_desafio_q   = 0
                    frase_c = orden[0]
                    st.session_state.dic_correcta  = frase_c["texto"]
                    st.session_state.dic_opciones  = generar_opciones(frase_c, FRASES, grupo)
                    st.session_state.dic_respuesta = None
                    st.session_state.dic_pantalla  = "desafio"
                st.rerun()
        with col1:
            if st.button("🚪 Salir"):
                st.session_state.dic_pantalla = "seleccion"
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# DESAFÍO: 3 preguntas (una por cada video del grupo)
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.dic_pantalla == "desafio":
    lec    = st.session_state.dic_leccion
    ronda  = st.session_state.dic_ronda
    grupo  = st.session_state.dic_grupo
    orden  = st.session_state.dic_desafio_ord
    q_idx  = st.session_state.dic_desafio_q
    total_rondas = RONDAS_POR_LECCION

    st.markdown(f"### 🎯 Desafío — Ronda {ronda+1} de {total_rondas}")
    st.progress((ronda) / total_rondas)
    st.markdown(f"**Pregunta {q_idx+1} de {len(orden)}** · ¿Qué significa esta seña?")
    st.markdown("---")

    frase_actual = orden[q_idx]
    correcta     = st.session_state.dic_correcta
    opciones     = st.session_state.dic_opciones
    respuesta    = st.session_state.dic_respuesta

    ruta_video = video_url(frase_actual["archivo"])
    if os.path.exists(ruta_video):
        st.video(ruta_video, loop=True, autoplay=True, muted=True)
    else:
        st.warning(f"Video `{frase_actual['archivo']}` no encontrado.")

    st.markdown("<br>", unsafe_allow_html=True)

    if respuesta is None:
        cols = st.columns(3)
        for i, op in enumerate(opciones):
            with cols[i]:
                if st.button(op, key=f"op_{q_idx}_{i}", use_container_width=True):
                    if op == correcta:
                        st.session_state.dic_respuesta = "ok"
                    else:
                        st.session_state.dic_respuesta = "mal"
                    st.rerun()
    else:
        if respuesta == "ok":
            st.success(f"✅ ¡Correcto! Es: **{correcta}**")
            if st.button("Siguiente pregunta ›"):
                siguiente_q = q_idx + 1
                if siguiente_q < len(orden):
                    # Siguiente pregunta del desafío
                    frase_c = orden[siguiente_q]
                    st.session_state.dic_desafio_q  = siguiente_q
                    st.session_state.dic_correcta   = frase_c["texto"]
                    st.session_state.dic_opciones   = generar_opciones(frase_c, FRASES, grupo)
                    st.session_state.dic_respuesta  = None
                else:
                    # Desafío completado → siguiente ronda o fin
                    st.session_state.dic_rondas_ok += 1
                    siguiente_ronda = ronda + 1
                    if siguiente_ronda < total_rondas:
                        st.session_state.dic_ronda    = siguiente_ronda
                        st.session_state.dic_vid_idx  = 0
                        st.session_state.dic_grupo    = preparar_ronda(lec, siguiente_ronda)
                        st.session_state.dic_pantalla = "aprendizaje"
                    else:
                        guardar_completado_dic(lec["numero"])
                        st.session_state.dic_pantalla = "resultado"
                st.rerun()
        else:
            st.error("❌ Incorrecto, intenta de nuevo.")
            cols = st.columns(3)
            for i, op in enumerate(opciones):
                with cols[i]:
                    if st.button(op, key=f"retry_{q_idx}_{i}", use_container_width=True):
                        if op == correcta:
                            st.session_state.dic_respuesta = "ok"
                        else:
                            st.session_state.dic_respuesta = "mal"
                        st.rerun()

    st.markdown("---")
    if st.button("🚪 Salir sin guardar"):
        st.session_state.dic_pantalla = "seleccion"
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.dic_pantalla == "resultado":
    lec = st.session_state.dic_leccion
    st.markdown("## 🏆 ¡Lección del diccionario completada!")
    st.markdown(f"### {lec['nombre']}")
    st.success("✅ ¡Superaste las 5 rondas! La siguiente lección está desbloqueada.")
    st.balloons()

    if st.button("📋 Ver lecciones"):
        st.session_state.dic_pantalla = "seleccion"
        st.rerun()
    if st.button("← Inicio"):
        st.switch_page("Inicio.py")
