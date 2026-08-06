import cv2
import mediapipe as mp
import csv
import os

# --- Configuración ---
ARCHIVO_CSV = "dataset_keypoints.csv"
MUESTRAS_POR_LETRA = 200  # cuántas muestras se guardan cada vez que grabas

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: no se pudo abrir la cámara.")
    exit()

# Si el archivo CSV no existe todavía, creamos el encabezado
if not os.path.exists(ARCHIVO_CSV):
    encabezado = ["letra"] + [f"{eje}{i}" for i in range(21) for eje in ("x", "y", "z")]
    with open(ARCHIVO_CSV, "w", newline="") as f:
        csv.writer(f).writerow(encabezado)

letra_actual = None
grabando = False
contador = 0

print("=== Recolección de datos ===")
print("- Presiona una letra (a-z) para seleccionarla.")
print("- Presiona ESPACIO para empezar/detener la grabación de esa letra.")
print("- Presiona ESC para salir.\n")

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = hands.process(rgb_frame)

            if resultado.multi_hand_landmarks:
                puntos_mano = resultado.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, puntos_mano, mp_hands.HAND_CONNECTIONS)

                if grabando and letra_actual:
                    # Usamos la muñeca (landmark 0) como punto de referencia,
                    # así no importa en qué parte de la pantalla esté la mano.
                    base = puntos_mano.landmark[0]
                    fila = [letra_actual]
                    for lm in puntos_mano.landmark:
                        fila += [lm.x - base.x, lm.y - base.y, lm.z - base.z]

                    with open(ARCHIVO_CSV, "a", newline="") as f:
                        csv.writer(f).writerow(fila)

                    contador += 1
                    if contador >= MUESTRAS_POR_LETRA:
                        grabando = False
                        print(f"Listo: {MUESTRAS_POR_LETRA} muestras guardadas para la letra '{letra_actual}'")
                        contador = 0

            # Texto informativo en pantalla
            estado = f"Letra: {letra_actual or '-'}  |  Grabando: {'SI' if grabando else 'NO'}  |  Muestras: {contador}"
            color = (0, 0, 255) if grabando else (0, 255, 0)
            cv2.putText(frame, estado, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, "ESPACIO: grabar/parar | letra a-z: elegir | ESC: salir",
                        (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Recoleccion de datos - Lenguaje de senas", frame)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla == 27:  # ESC
                break
            elif tecla == 32:  # barra espaciadora
                if letra_actual:
                    grabando = not grabando
                    contador = 0
            elif 97 <= tecla <= 122:  # letras de la 'a' a la 'z'
                letra_actual = chr(tecla).upper()
                grabando = False
                contador = 0

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nDatos guardados en: {os.path.abspath(ARCHIVO_CSV)}")
