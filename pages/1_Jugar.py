import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import joblib, os, time
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datos import LECCIONES, leccion_desbloqueada, guardar_puntaje_jugar, get_progreso

st.set_page_config(page_title="Jugar – Conecta con las Manos", page_icon="🎮", layout="centered")

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
.palabra-display{font-size:2rem;font-weight:900;letter-spacing:6px;
    text-align:center;padding:1rem;background:#13131a;
    border:2px solid #6a3bcc;border-radius:14px;margin:1rem 0}
.letra-ok{color:#00dc64!important}
.letra-actual{color:#02c0fc!important;text-decoration:underline}
.letra-pending{color:#555!important}
</style>
""", unsafe_allow_html=True)

# ── Cargar modelo ────────────────────────────────────────────────────────────
@st.cache_resource
def cargar_modelo():
    ruta = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modelo_senas.pkl")
    if os.path.exists(ruta):
        return joblib.load(ruta)
    return None

@st.cache_resource
def cargar_imagen_letra(letra):
    base = os.path.dirname(os.path.dirname(__file__))
    for nombre in [f"{letra}.png", f"{letra.lower()}.png"]:
        ruta = os.path.join(base, "letras", nombre)
        if os.path.exists(ruta):
            return Image.open(ruta).resize((180, 180))
    return None

modelo = cargar_modelo()

# ── Estado de la sesión ──────────────────────────────────────────────────────
def init_estado():
    defaults = {
        "jugar_pantalla": "seleccion",   # seleccion | jugando | resultado
        "jugar_leccion":  None,
        "jugar_palabra_idx": 0,
        "jugar_letra_idx": 0,
        "jugar_letras_ok": 0,
        "jugar_letras_total": 0,
        "jugar_frames_ok": 0,
        "jugar_ultima_pred": "-",
        "jugar_confianza": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_estado()

# ── Procesador de video (streamlit-webrtc) ───────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
FRAMES_CONFIRMAR = 20
CONFIANZA_MIN    = 0.55

class ProcesadorManos(VideoProcessorBase):
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False, max_num_hands=1,
            min_detection_confidence=0.6, min_tracking_confidence=0.6)
        self.letra_objetivo = ""
        self.frames_ok = 0
        self.ultima_pred = "-"
        self.confianza   = 0.0
        self.acertada    = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)

        self.ultima_pred = "-"
        self.confianza   = 0.0

        if res.multi_hand_landmarks and self.letra_objetivo:
            pm = res.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(img, pm, mp_hands.HAND_CONNECTIONS)

            base = pm.landmark[0]
            fila = []
            for lm in pm.landmark:
                fila += [lm.x - base.x, lm.y - base.y, lm.z - base.z]
            entrada = np.array(fila).reshape(1, -1)

            if modelo and hasattr(modelo, "predict_proba"):
                probs = modelo.predict_proba(entrada)[0]
                idx   = int(np.argmax(probs))
                self.ultima_pred = modelo.classes_[idx]
                self.confianza   = float(probs[idx])
            elif modelo:
                self.ultima_pred = modelo.predict(entrada)[0]
                self.confianza   = 1.0

            if self.ultima_pred == self.letra_objetivo and self.confianza >= CONFIANZA_MIN:
                self.frames_ok += 1
            else:
                self.frames_ok = 0

            if self.frames_ok >= FRAMES_CONFIRMAR:
                self.acertada = True
                self.frames_ok = 0
        else:
            self.frames_ok = 0

        # Barra de progreso en el frame
        pct = min(self.frames_ok / FRAMES_CONFIRMAR, 1.0)
        bw  = int(img.shape[1] * 0.4 * pct)
        cv2.rectangle(img, (10, 10), (int(img.shape[1]*0.4)+10, 28), (40,40,40), -1)
        cv2.rectangle(img, (10, 10), (10+bw, 28), (0,220,100), -1)
        cv2.putText(img, f"{self.ultima_pred} ({self.confianza:.2f})",
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

# ════════════════════════════════════════════════════════════════════════════
# PANTALLA: SELECCIÓN DE LECCIÓN
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.jugar_pantalla == "seleccion":
    st.markdown("## 🎮 Jugar — elige una lección")
    if st.button("← Inicio"):
        st.switch_page("Inicio.py")
    st.markdown("---")

    if modelo is None:
        st.error("⚠️ No se encontró el archivo `modelo_senas.pkl`. Ponlo en la carpeta raíz de la app.")

    cols = st.columns(3)
    for i, lec in enumerate(LECCIONES):
        desbloqueada = leccion_desbloqueada(lec["numero"])
        with cols[i % 3]:
            label = f"{'🔓' if desbloqueada else '🔒'} {lec['numero']}. {lec['nombre']}"
            if st.button(label, disabled=not desbloqueada, key=f"lec_{lec['numero']}"):
                st.session_state.jugar_leccion      = lec
                st.session_state.jugar_palabra_idx  = 0
                st.session_state.jugar_letra_idx    = 0
                st.session_state.jugar_letras_ok    = 0
                st.session_state.jugar_letras_total = sum(len(p) for p in lec["palabras"])
                st.session_state.jugar_frames_ok    = 0
                st.session_state.jugar_pantalla     = "jugando"
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PANTALLA: JUGANDO
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.jugar_pantalla == "jugando":
    lec         = st.session_state.jugar_leccion
    palabras    = lec["palabras"]
    p_idx       = st.session_state.jugar_palabra_idx
    l_idx       = st.session_state.jugar_letra_idx

    if p_idx >= len(palabras):
        st.session_state.jugar_pantalla = "resultado"
        st.rerun()

    palabra        = palabras[p_idx]
    letra_objetivo = palabra[l_idx] if l_idx < len(palabra) else ""

    st.markdown(f"### Lección {lec['numero']}: {lec['nombre']}")
    prog_total = f"{p_idx + 1}/{len(palabras)} palabras"
    st.caption(prog_total)

    # Mostrar palabra con colores
    partes = ""
    for i, c in enumerate(palabra):
        if i < l_idx:
            partes += f'<span class="letra-ok">{c}</span>'
        elif i == l_idx:
            partes += f'<span class="letra-actual">{c}</span>'
        else:
            partes += f'<span class="letra-pending">{c}</span>'
    st.markdown(f'<div class="palabra-display">{partes}</div>', unsafe_allow_html=True)

    col_cam, col_ref = st.columns([3, 1])

    with col_ref:
        st.markdown(f"**Forma la letra:**")
        st.markdown(f"<h1 style='color:#02c0fc;text-align:center;font-size:4rem'>{letra_objetivo}</h1>",
                    unsafe_allow_html=True)
        img_ref = cargar_imagen_letra(letra_objetivo)
        if img_ref:
            st.image(img_ref, caption="Referencia", use_container_width=True)
        else:
            st.info("Pon imágenes en la carpeta `letras/`")

    with col_cam:
        ctx = webrtc_streamer(
            key=f"cam_{p_idx}_{l_idx}",
            video_processor_factory=ProcesadorManos,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        if ctx.video_processor:
            ctx.video_processor.letra_objetivo = letra_objetivo

            # Revisar si acertó
            if ctx.video_processor.acertada:
                ctx.video_processor.acertada = False
                st.session_state.jugar_letras_ok += 1
                # Avanzar letra / palabra
                if l_idx + 1 < len(palabra):
                    st.session_state.jugar_letra_idx += 1
                else:
                    st.session_state.jugar_palabra_idx += 1
                    st.session_state.jugar_letra_idx   = 0
                time.sleep(0.3)
                st.rerun()

    col_s, col_v = st.columns(2)
    with col_s:
        if st.button("⏭ Saltar letra"):
            if l_idx + 1 < len(palabra):
                st.session_state.jugar_letra_idx += 1
            else:
                st.session_state.jugar_palabra_idx += 1
                st.session_state.jugar_letra_idx   = 0
            st.rerun()
    with col_v:
        if st.button("🚪 Salir sin guardar"):
            st.session_state.jugar_pantalla = "seleccion"
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PANTALLA: RESULTADO
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.jugar_pantalla == "resultado":
    lec    = st.session_state.jugar_leccion
    ok     = st.session_state.jugar_letras_ok
    total  = st.session_state.jugar_letras_total
    puntaje = round((ok / total) * 100) if total else 0

    guardar_puntaje_jugar(lec["numero"], puntaje)

    st.markdown("## ✅ ¡Lección completada!")
    st.markdown(f"### {lec['nombre']}")
    st.metric("Puntaje", f"{puntaje} / 100")
    st.progress(puntaje / 100)

    if puntaje >= 80:
        st.success("🌟 ¡Excelente! Dominas estas señas.")
    elif puntaje >= 50:
        st.warning("👍 Buen intento, sigue practicando.")
    else:
        st.error("💪 Puedes mejorar, ¡vuelve a intentarlo!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Repetir lección"):
            st.session_state.jugar_palabra_idx  = 0
            st.session_state.jugar_letra_idx    = 0
            st.session_state.jugar_letras_ok    = 0
            st.session_state.jugar_frames_ok    = 0
            st.session_state.jugar_letras_total = sum(len(p) for p in lec["palabras"])
            st.session_state.jugar_pantalla     = "jugando"
            st.rerun()
    with col2:
        if st.button("📋 Ver lecciones"):
            st.session_state.jugar_pantalla = "seleccion"
            st.rerun()
