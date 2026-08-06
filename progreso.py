import json
import os

ARCHIVO_PROGRESO = "progreso.json"
PUNTOS_PARA_LLENAR_BARRA = 300  # Puntos necesarios para llenar la barra una vez (ajustable)
CATEGORIAS = ["APRENDIZ", "ESTUDIANTE", "MAESTRO"]


def cargar_progreso():
    """Lee el progreso guardado, o crea uno nuevo si no existe todavia."""
    if os.path.exists(ARCHIVO_PROGRESO):
        try:
            with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"categoria": "APRENDIZ", "puntos_actuales": 0, "lecciones_jugadas": 0, "historial": {}}


def guardar_progreso(progreso):
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
        json.dump(progreso, f, indent=2, ensure_ascii=False)


def registrar_resultado_leccion(numero_leccion, puntaje):
    """
    Llamar a esta funcion cada vez que el jugador termine una leccion
    (esto lo hara el juego de la Fase 5, conectado a la camara).

    numero_leccion: el numero de la leccion jugada (1-15)
    puntaje: el desempeno obtenido en esa leccion, de 0 a 100
    """
    progreso = cargar_progreso()
    progreso["lecciones_jugadas"] = progreso.get("lecciones_jugadas", 0) + 1
    progreso.setdefault("historial", {})[str(numero_leccion)] = puntaje

    # Si ya esta en MAESTRO y con la barra llena, se queda llena (no sigue acumulando)
    barra_llena_en_maestro = (
        progreso["categoria"] == "MAESTRO"
        and progreso["puntos_actuales"] >= PUNTOS_PARA_LLENAR_BARRA
    )
    if not barra_llena_en_maestro:
        progreso["puntos_actuales"] = progreso.get("puntos_actuales", 0) + puntaje

    # Si la barra se llena, sube de categoria y la barra se reinicia
    if progreso["puntos_actuales"] >= PUNTOS_PARA_LLENAR_BARRA:
        if progreso["categoria"] == "APRENDIZ":
            progreso["categoria"] = "ESTUDIANTE"
            progreso["puntos_actuales"] = 0
        elif progreso["categoria"] == "ESTUDIANTE":
            progreso["categoria"] = "MAESTRO"
            progreso["puntos_actuales"] = 0
        else:
            progreso["puntos_actuales"] = PUNTOS_PARA_LLENAR_BARRA  # Se queda llena

    guardar_progreso(progreso)
    return progreso


def calcular_nivel(puntos_actuales):
    """Devuelve el nivel (1 a 5) segun que tan llena esta la barra."""
    porcentaje = min(puntos_actuales / PUNTOS_PARA_LLENAR_BARRA, 1.0)
    if porcentaje >= 0.8:
        return 5
    elif porcentaje >= 0.6:
        return 4
    elif porcentaje >= 0.4:
        return 3
    elif porcentaje >= 0.2:
        return 2
    else:
        return 1
