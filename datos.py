"""
datos.py – constantes y funciones de progreso compartidas entre páginas.
El progreso se guarda en st.session_state (en memoria por sesión).
"""
import streamlit as st

# ── Lecciones de JUGAR ───────────────────────────────────────────────────────
LECCIONES = [
    {"numero": 1,  "nombre": "Animales",         "palabras": ["GATO", "PERRO", "OSO", "LEON", "PEZ"]},
    {"numero": 2,  "nombre": "Colores",           "palabras": ["ROJO", "AZUL", "VERDE", "NEGRO", "GRIS"]},
    {"numero": 3,  "nombre": "Frutas",            "palabras": ["PERA", "UVA", "MANGO", "LIMON", "KIWI"]},
    {"numero": 4,  "nombre": "Familia",           "palabras": ["MAMA", "PAPA", "HIJO", "TIA", "ABUELO"]},
    {"numero": 5,  "nombre": "Objetos de casa",   "palabras": ["MESA", "SILLA", "CAMA", "PUERTA", "LLAVE"]},
    {"numero": 6,  "nombre": "Números",           "palabras": ["UNO", "DOS", "TRES", "CUATRO", "CINCO"]},
    {"numero": 7,  "nombre": "Cuerpo humano",     "palabras": ["OJO", "MANO", "PIE", "BOCA", "NARIZ"]},
    {"numero": 8,  "nombre": "Ropa",              "palabras": ["GORRA", "CAMISA", "FALDA", "MEDIA", "BOTA"]},
    {"numero": 9,  "nombre": "Escuela",           "palabras": ["LIBRO", "LAPIZ", "MOCHILA", "REGLA", "GOMA"]},
    {"numero": 10, "nombre": "Naturaleza",        "palabras": ["SOL", "LUNA", "RIO", "MAR", "ARBOL"]},
    {"numero": 11, "nombre": "Comida",            "palabras": ["PAN", "SOPA", "ARROZ", "QUESO", "LECHE"]},
    {"numero": 12, "nombre": "Deportes",          "palabras": ["TENIS", "NADAR", "CORRER", "GOL", "EQUIPO"]},
    {"numero": 13, "nombre": "Transporte",        "palabras": ["CARRO", "BUS", "AVION", "MOTO", "BARCO"]},
    {"numero": 14, "nombre": "Lugares",           "palabras": ["CASA", "PARQUE", "CIUDAD", "PLAYA", "TIENDA"]},
    {"numero": 15, "nombre": "Repaso final",      "palabras": ["ELEFANTE", "MARIPOSA", "JIRAFA", "ZAPATO", "AMISTAD"]},
]

# ── Frases del DICCIONARIO ───────────────────────────────────────────────────
FRASES = [
    {"texto": "Hola",                   "archivo": "hola.mp4"},
    {"texto": "Buenos dias",            "archivo": "buenos_dias.mp4"},
    {"texto": "Buenas tardes",          "archivo": "buenas_tardes.mp4"},
    {"texto": "Buenas noches",          "archivo": "buenas_noches.mp4"},
    {"texto": "Mucho gusto",            "archivo": "mucho_gusto.mp4"},
    {"texto": "¿Cómo te llamas?",       "archivo": "como_te_llamas.mp4"},
    {"texto": "Mi nombre es",           "archivo": "mi_nombre_es.mp4"},
    {"texto": "Estoy cansado",          "archivo": "estoy_cansado.mp4"},
    {"texto": "¿Cuántos años tienes?",  "archivo": "cuantos_anios_tienes.mp4"},
    {"texto": "¿Dónde vives?",          "archivo": "donde_vives.mp4"},
    {"texto": "Gracias",                "archivo": "gracias.mp4"},
    {"texto": "De nada",                "archivo": "de_nada.mp4"},
    {"texto": "Lo siento",              "archivo": "lo_siento.mp4"},
    {"texto": "Sí",                     "archivo": "si.mp4"},
    {"texto": "No",                     "archivo": "no.mp4"},
    {"texto": "No entiendo",            "archivo": "no_entiendo.mp4"},
    {"texto": "Yo me llamo Sofía",      "archivo": "yo_me_llamo_sofia.mp4"},
    {"texto": "Yo vivo en Uribia",      "archivo": "yo_vivo_en_uribia.mp4"},
    {"texto": "Yo tengo 18",            "archivo": "yo_tengo_18.mp4"},
    {"texto": "Gusto en conocerte",     "archivo": "gusto_conocerte.mp4"},
    {"texto": "Tal vez",                "archivo": "tal_vez.mp4"},
    {"texto": "Adiós",                  "archivo": "adios.mp4"},
    {"texto": "Nos vemos",              "archivo": "nos_vemos.mp4"},
    {"texto": "Yo estoy feliz",         "archivo": "yo_estoy_feliz.mp4"},
    {"texto": "Yo estoy triste",        "archivo": "yo_estoy_triste.mp4"},
    {"texto": "Por favor",              "archivo": "por_favor.mp4"},
    {"texto": "¿Cómo estás?",           "archivo": "como_estas.mp4"},
    {"texto": "Bien",                   "archivo": "bien.mp4"},
    {"texto": "Mal",                    "archivo": "mal.mp4"},
    {"texto": "Perdón",                 "archivo": "perdon.mp4"},
]

NOMBRES_LECCION_DIC = [
    "Saludos y presentaciones",
    "Emociones y cortesía",
]

def _agrupar_frases(frases, tam=15):
    grupos = []
    for i in range(0, len(frases), tam):
        num = i // tam + 1
        nombre = NOMBRES_LECCION_DIC[num-1] if num-1 < len(NOMBRES_LECCION_DIC) else f"Lección {num}"
        grupos.append({"numero": num, "nombre": nombre, "frases": frases[i:i+tam]})
    return grupos

LECCIONES_DICCIONARIO = _agrupar_frases(FRASES)

# ── Progreso en session_state ────────────────────────────────────────────────
PUNTOS_BARRA = 300
CATEGORIAS   = ["APRENDIZ", "ESTUDIANTE", "MAESTRO"]

def init_progreso():
    if "progreso" not in st.session_state:
        st.session_state.progreso = {
            "categoria": "APRENDIZ",
            "puntos": 0,
            "lecciones_jugadas": 0,
            "historial": {},          # {str(numero): puntaje}
            "historial_dic": {},      # {str(numero): True}
        }

def get_progreso():
    init_progreso()
    return st.session_state.progreso

def leccion_desbloqueada(numero):
    p = get_progreso()
    return numero == 1 or str(numero - 1) in p["historial"]

def dic_desbloqueada(numero):
    p = get_progreso()
    return numero == 1 or str(numero - 1) in p["historial_dic"]

def guardar_puntaje_jugar(numero, puntaje):
    p = get_progreso()
    p["lecciones_jugadas"] += 1
    p["historial"][str(numero)] = puntaje
    # Sumar puntos y subir categoría si corresponde
    if not (p["categoria"] == "MAESTRO" and p["puntos"] >= PUNTOS_BARRA):
        p["puntos"] += puntaje
    if p["puntos"] >= PUNTOS_BARRA:
        idx = CATEGORIAS.index(p["categoria"])
        if idx < len(CATEGORIAS) - 1:
            p["categoria"] = CATEGORIAS[idx + 1]
            p["puntos"] = 0
        else:
            p["puntos"] = PUNTOS_BARRA

def guardar_completado_dic(numero):
    p = get_progreso()
    p["historial_dic"][str(numero)] = True
