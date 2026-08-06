import cv2
import mediapipe as mp
import joblib
import numpy as np
import os

from recursos import ruta_datos

ARCHIVO_MODELO   = ruta_datos("modelo_senas.pkl")
# Buscar la carpeta letras relativa al propio juego_leccion.py
CARPETA_LETRAS   = r"C:\Users\HORTENCIA\Desktop\juego\letras"
TAMANO_REFERENCIA = 160
print(f"[juego] Buscando imágenes de letras en: {CARPETA_LETRAS}")

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils

FRAMES_PARA_CONFIRMAR = 15
CONFIANZA_MINIMA      = 0.55

from PIL import Image as PILImage

# Caché para no releer la imagen del disco en cada fotograma
_cache_imagenes = {}

def _imagen_letra(letra):
    """Carga la imagen con PIL (soporta PNG transparente) y la convierte a BGR para OpenCV."""
    if letra in _cache_imagenes:
        return _cache_imagenes[letra]
    carpeta = r"C:\Users\HORTENCIA\Desktop\juego\letras"
    intentos = [
        os.path.join(carpeta, f"{letra}.png"),
        os.path.join(carpeta, f"{letra.lower()}.png"),
        os.path.join(carpeta, f"{letra.upper()}.png"),
    ]
    for ruta in intentos:
        if os.path.exists(ruta):
            try:
                pil_img = PILImage.open(ruta).convert("RGB")
                pil_img = pil_img.resize((TAMANO_REFERENCIA, TAMANO_REFERENCIA))
                img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                _cache_imagenes[letra] = img_bgr
                print(f"[juego] OK imagen: {ruta}")
                return img_bgr
            except Exception as e:
                print(f"[juego] Error leyendo {ruta}: {e}")
    print(f"[juego] NO encontrada: letra {letra}")
    _cache_imagenes[letra] = None
    return None


def _dibujar_referencia(frame, letra):
    """
    Pega en la esquina superior derecha del frame la imagen de referencia
    de cómo hacer la seña. Si no hay imagen, dibuja un recuadro con la letra.
    """
    h, w = frame.shape[:2]
    margen = 10
    tam    = TAMANO_REFERENCIA
    x1     = w - tam - margen
    y1     = margen
    x2     = x1 + tam
    y2     = y1 + tam

    img_ref = _imagen_letra(letra)

    if img_ref is not None:
        # Borde blanco alrededor de la imagen
        cv2.rectangle(frame, (x1 - 3, y1 - 3), (x2 + 3, y2 + 3), (255, 255, 255), 3)
        frame[y1:y2, x1:x2] = img_ref
    else:
        # Recuadro de respaldo con la letra grande
        cv2.rectangle(frame, (x1, y1), (x2, y2), (40, 40, 50), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(frame, letra, (x1 + 30, y2 - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 255, 255), 6)

    # Etiqueta debajo del recuadro
    cv2.putText(frame, "Referencia", (x1 + 5, y2 + 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)


def _cargar_modelo():
    if not os.path.exists(ARCHIVO_MODELO):
        print(f"Error: no encontre '{ARCHIVO_MODELO}'. Entrena el modelo primero con 'entrenar_modelo.py'.")
        return None
    return joblib.load(ARCHIVO_MODELO)


def _predecir_letra(modelo, puntos_mano):
    """Misma normalizacion que se usa en recolectar_datos.py y reconocer_en_tiempo_real.py,
    pero aqui tambien devolvemos la confianza de la prediccion."""
    base = puntos_mano.landmark[0]
    fila = []
    for lm in puntos_mano.landmark:
        fila += [lm.x - base.x, lm.y - base.y, lm.z - base.z]
    entrada = np.array(fila).reshape(1, -1)

    if hasattr(modelo, "predict_proba"):
        probabilidades = modelo.predict_proba(entrada)[0]
        indice_max = int(np.argmax(probabilidades))
        letra = modelo.classes_[indice_max]
        confianza = float(probabilidades[indice_max])
        return letra, confianza

    letra = modelo.predict(entrada)[0]
    return letra, 1.0


def jugar_leccion(leccion):
    """
    Abre la camara y guia al jugador para deletrear, letra por letra, cada palabra
    de la leccion usando lenguaje de senas.

    Devuelve:
        - un puntaje de 0 a 100 si el jugador termino toda la leccion.
        - None si no se pudo abrir la camara/modelo, o si el jugador salio antes con ESC.

    Controles dentro del juego:
        - Mantener la letra correcta frente a la camara hasta que la barra se llene.
        - 'S' : saltar la letra actual (cuenta como no acertada).
        - ESC : salir de la leccion sin guardar puntaje.
    """
    modelo = _cargar_modelo()
    if modelo is None:
        return None

    palabras = leccion["palabras"]
    letras_totales = sum(len(p) for p in palabras)
    letras_correctas = 0

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: no se pudo abrir la camara.")
        return None

    print(f"\n=== Leccion {leccion['numero']}: {leccion['nombre']} ===")
    print("Deletrea cada palabra con lenguaje de senas. 'S' para saltar letra, ESC para salir.\n")

    salio = False

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:
        try:
            for palabra in palabras:
                if salio:
                    break

                for indice_letra, letra_objetivo in enumerate(palabra):
                    if salio:
                        break

                    cuadros_correctos_seguidos = 0
                    acertada = False

                    while not acertada:
                        exito, frame = cap.read()
                        if not exito:
                            continue

                        frame = cv2.flip(frame, 1)
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        resultado = hands.process(rgb_frame)

                        letra_predicha = "-"
                        confianza = 0.0

                        if resultado.multi_hand_landmarks:
                            puntos_mano = resultado.multi_hand_landmarks[0]
                            mp_draw.draw_landmarks(frame, puntos_mano, mp_hands.HAND_CONNECTIONS)
                            letra_predicha, confianza = _predecir_letra(modelo, puntos_mano)

                            if letra_predicha == letra_objetivo and confianza >= CONFIANZA_MINIMA:
                                cuadros_correctos_seguidos += 1
                            else:
                                cuadros_correctos_seguidos = 0
                        else:
                            cuadros_correctos_seguidos = 0

                        # --- Texto informativo en pantalla ---
                        prefijo = palabra[:indice_letra]
                        resto = palabra[indice_letra + 1:]
                        letras_mostrar = f"{prefijo}[{letra_objetivo}]{resto}"

                        cv2.putText(frame, f"Palabra: {letras_mostrar}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        cv2.putText(frame, f"Forma la letra: {letra_objetivo}", (10, 65),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                        cv2.putText(frame, f"Prediccion: {letra_predicha} ({confianza:.2f})", (10, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        # Barra de progreso de confirmacion de la letra actual
                        barra_ancho = int(200 * min(cuadros_correctos_seguidos / FRAMES_PARA_CONFIRMAR, 1.0))
                        cv2.rectangle(frame, (10, 115), (210, 130), (60, 60, 60), -1)
                        cv2.rectangle(frame, (10, 115), (10 + barra_ancho, 130), (0, 255, 0), -1)

                        # Imagen de referencia de la letra (esquina superior derecha)
                        _dibujar_referencia(frame, letra_objetivo)

                        cv2.putText(frame, "S: saltar letra | ESC: salir",
                                    (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                        cv2.imshow("Leccion - Lenguaje de senas", frame)

                        if cuadros_correctos_seguidos >= FRAMES_PARA_CONFIRMAR:
                            letras_correctas += 1
                            acertada = True
                            cv2.waitKey(300)  # breve pausa para que el jugador vea que acerto

                        tecla = cv2.waitKey(1) & 0xFF
                        if tecla == 27:  # ESC
                            salio = True
                            break
                        elif tecla in (ord('s'), ord('S')):
                            acertada = True  # se salta, no se cuenta como correcta
        finally:
            cap.release()
            cv2.destroyAllWindows()

    if salio:
        print("Saliste de la leccion sin terminarla. No se guardo puntaje.\n")
        return None

    puntaje = round((letras_correctas / letras_totales) * 100) if letras_totales else 0
    print(f"\nLeccion terminada. Letras correctas: {letras_correctas}/{letras_totales}  ->  Puntaje: {puntaje}/100\n")
    return puntaje
