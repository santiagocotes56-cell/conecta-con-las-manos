import streamlit as st, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="Cómo jugar", page_icon="ℹ️", layout="centered")
st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{background:#08080c!important}
[data-testid="stSidebar"]{display:none}
h1,h2,h3,p,label,span,li{color:#fff!important}
div[data-testid="stButton"]>button{
    font-weight:900;border-radius:14px;border:2px solid #6a3bcc;
    width:100%;background:#02c0fc;color:#08080c!important}
</style>
""", unsafe_allow_html=True)

if st.button("← Inicio"):
    st.switch_page("Inicio.py")

st.markdown("## ℹ️ Cómo jugar")

st.markdown("""
### 🎮 JUGAR
1. Elige una lección (las primeras están desbloqueadas, las demás se van abriendo al completar).
2. Se te muestra una **palabra** letra por letra.
3. Forma cada letra con tu mano frente a la cámara.
4. Cuando la IA detecte la letra correcta varios segundos, avanza automáticamente.
5. La imagen de referencia en la pantalla te muestra cómo hacer cada seña.
6. Al terminar todas las palabras recibes un puntaje de 0 a 100.

### 📖 DICCIONARIO
1. Elige una lección.
2. Se te muestran **3 videos** con su significado uno a uno — pulsa **SIGUIENTE** para avanzar.
3. Luego viene el **desafío**: se reproduce uno de esos videos y tienes que elegir qué significa entre 3 opciones.
4. Se te pregunta por los 3 videos del grupo antes de pasar a la siguiente ronda.
5. Cada lección tiene **5 rondas** de 3 videos + 3 preguntas cada una.
6. Completa las 5 rondas para desbloquear la siguiente lección.

### 📊 PROGRESO
- Cada lección completada suma puntos.
- Al llenar la barra subes de categoría: **APRENDIZ → ESTUDIANTE → MAESTRO**.
- Tu progreso se guarda mientras dure la sesión.

### 💡 Consejos
- Usa buena iluminación para que la cámara vea bien tu mano.
- Pon la mano en el centro de la pantalla.
- Si la IA no reconoce la letra, ajusta el ángulo de tu mano.
""")
