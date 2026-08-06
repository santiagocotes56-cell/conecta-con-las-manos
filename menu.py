import pygame
import sys
import os
import cv2

from progreso import cargar_progreso, registrar_resultado_leccion, calcular_nivel, PUNTOS_PARA_LLENAR_BARRA
from juego_leccion import jugar_leccion
from juego_diccionario import jugar_diccionario
from recursos import ruta_recurso, ruta_datos

pygame.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Aprende Lengua de Senas")

# --- Colores (tomados directamente del logo: negro, azul cian, morado) ---
COLOR_FONDO = (8, 8, 12)
COLOR_BOTON = (2, 192, 252)        # azul cian del logo
COLOR_BOTON_HOVER = (106, 59, 204)  # morado del logo
COLOR_TEXTO = (255, 255, 255)
COLOR_TITULO = (2, 192, 252)
COLOR_ACENTO = (106, 59, 204)

RUTA_LOGO = ruta_recurso("logo.png")

logo_imagen = None
if os.path.exists(RUTA_LOGO):
    try:
        logo_original = pygame.image.load(RUTA_LOGO).convert_alpha()
        ancho_logo = 220
        proporcion = ancho_logo / logo_original.get_width()
        alto_logo = int(logo_original.get_height() * proporcion)
        logo_imagen = pygame.transform.smoothscale(logo_original, (ancho_logo, alto_logo))
    except Exception as error:
        print(f"No se pudo cargar el logo: {error}")
else:
    print(f"Aviso: no encontre '{RUTA_LOGO}' en esta carpeta. El menu se vera sin el logo.")

fuente_titulo = pygame.font.SysFont("Arial", 44, bold=True)
fuente_boton = pygame.font.SysFont("Arial", 18, bold=True)
fuente_pequena = pygame.font.SysFont("Arial", 16)

# --- AQUI puedes editar tus lecciones y palabras ---
LECCIONES = [
    {"numero": 1, "nombre": "Animales", "palabras": ["GATO", "PERRO", "OSO", "LEON", "PEZ"]},
    {"numero": 2, "nombre": "Colores", "palabras": ["ROJO", "AZUL", "VERDE", "NEGRO", "GRIS"]},
    {"numero": 3, "nombre": "Frutas", "palabras": ["PERA", "UVA", "MANGO", "LIMON", "KIWI"]},
    {"numero": 4, "nombre": "Familia", "palabras": ["MAMA", "PAPA", "HIJO", "TIA", "ABUELO"]},
    {"numero": 5, "nombre": "Objetos de casa", "palabras": ["MESA", "SILLA", "CAMA", "PUERTA", "LLAVE"]},
    {"numero": 6, "nombre": "Numeros", "palabras": ["UNO", "DOS", "TRES", "CUATRO", "CINCO"]},
    {"numero": 7, "nombre": "Cuerpo humano", "palabras": ["OJO", "MANO", "PIE", "BOCA", "NARIZ"]},
    {"numero": 8, "nombre": "Ropa", "palabras": ["GORRA", "CAMISA", "FALDA", "MEDIA", "BOTA"]},
    {"numero": 9, "nombre": "Escuela", "palabras": ["LIBRO", "LAPIZ", "MOCHILA", "REGLA", "GOMA"]},
    {"numero": 10, "nombre": "Naturaleza", "palabras": ["SOL", "LUNA", "RIO", "MAR", "ARBOL"]},
    {"numero": 11, "nombre": "Comida", "palabras": ["PAN", "SOPA", "ARROZ", "QUESO", "LECHE"]},
    {"numero": 12, "nombre": "Deportes", "palabras": ["TENIS", "NADAR", "CORRER", "GOL", "EQUIPO"]},
    {"numero": 13, "nombre": "Transporte", "palabras": ["CARRO", "BUS", "AVION", "MOTO", "BARCO"]},
    {"numero": 14, "nombre": "Lugares", "palabras": ["CASA", "PARQUE", "CIUDAD", "PLAYA", "TIENDA"]},
    {"numero": 15, "nombre": "Repaso final", "palabras": ["ELEFANTE", "MARIPOSA", "JIRAFA", "ZAPATO", "AMISTAD"]},
]

# --- Frases y saludos: cada una necesita un video en la carpeta "videos" ---
# El nombre del archivo debe coincidir exactamente con "archivo".
CARPETA_VIDEOS = ruta_datos("videos")
FRASES = [
    {"texto": "Hola", "archivo": "hola.mp4"},
    {"texto": "Buenos dias", "archivo": "buenos_dias.mp4"},
    {"texto": "Buenas tardes", "archivo": "buenas_tardes.mp4"},
    {"texto": "Buenas noches", "archivo": "buenas_noches.mp4"},
    {"texto": "Mucho gusto", "archivo": "mucho_gusto.mp4"},
    {"texto": "¿Cómo te llamas?", "archivo": "como_te_llamas.mp4"},
    {"texto": "Mi nombre es", "archivo": "mi_nombre_es.mp4"},
    {"texto": "Estoy cansado", "archivo": "estoy_cansado.mp4"},
    {"texto": "¿Cuántos años tienes?", "archivo": "cuantos_anios_tienes.mp4"},
    {"texto": "¿Dónde vives?", "archivo": "donde_vives.mp4"},
    {"texto": "Gracias", "archivo": "gracias.mp4"},
    {"texto": "De nada", "archivo": "de_nada.mp4"},
    {"texto": "Lo siento", "archivo": "lo_siento.mp4"},
    {"texto": "Sí", "archivo": "si.mp4"},
    {"texto": "No", "archivo": "no.mp4"},
    {"texto": "No entiendo", "archivo": "no_entiendo.mp4"},
    {"texto": "Yo me llamo Sofía", "archivo": "yo_me_llamo_sofia.mp4"},
    {"texto": "Yo vivo en Uribia", "archivo": "yo_vivo_en_uribia.mp4"},
    {"texto": "Yo tengo 18", "archivo": "yo_tengo_18.mp4"},
    {"texto": "Gusto en conocerte", "archivo": "gusto_conocerte.mp4"},
    {"texto": "Tal vez", "archivo": "tal_vez.mp4"},
    {"texto": "Adiós", "archivo": "adios.mp4"},
    {"texto": "Nos vemos", "archivo": "nos_vemos.mp4"},
    {"texto": "Yo estoy feliz", "archivo": "yo_estoy_feliz.mp4"},
    {"texto": "Yo estoy triste", "archivo": "yo_estoy_triste.mp4"},
    {"texto": "Por favor", "archivo": "por_favor.mp4"},
    {"texto": "¿Cómo estás?", "archivo": "como_estas.mp4"},
    {"texto": "Bien", "archivo": "bien.mp4"},
    {"texto": "Mal", "archivo": "mal.mp4"},
    {"texto": "Perdón", "archivo": "perdon.mp4"},
]

# ── Lecciones del Diccionario: cada una agrupa 3 frases ───────────────────
# Las lecciones se desbloquean en orden, igual que en JUGAR.
def _agrupar_frases(frases, tam=15):
    grupos = []
    nombres = [
        "Saludos y presentaciones",
        "Emociones y cortesía",
        "Conversación del día a día",
        "Respuestas y despedidas",
        "Repaso general",
    ]
    for i in range(0, len(frases), tam):
        num    = i // tam + 1
        nombre = nombres[num - 1] if num - 1 < len(nombres) else f"Leccion {num}"
        grupos.append({
            "numero": num,
            "nombre": nombre,
            "frases": frases[i:i + tam],
        })
    return grupos

LECCIONES_DICCIONARIO = _agrupar_frases(FRASES)


class Boton:
    def __init__(self, x, y, ancho, alto, texto, accion=None, bloqueado=False):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.accion = accion
        self.bloqueado = bloqueado

    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()

        if self.bloqueado:
            color = (35, 35, 40)
            borde = (60, 60, 66)
            color_texto = (120, 120, 128)
        else:
            color = COLOR_BOTON_HOVER if self.rect.collidepoint(mouse_pos) else COLOR_BOTON
            borde = COLOR_BOTON if self.rect.collidepoint(mouse_pos) else COLOR_ACENTO
            color_texto = COLOR_TEXTO

        pygame.draw.rect(superficie, color, self.rect, border_radius=15)
        pygame.draw.rect(superficie, borde, self.rect, width=2, border_radius=15)

        lineas = self.texto.split("\n")
        alto_linea = fuente_boton.get_height()
        y_inicio = self.rect.centery - (len(lineas) * alto_linea) // 2
        for i, linea in enumerate(lineas):
            texto_render = fuente_boton.render(linea, True, color_texto)
            centro_y = y_inicio + i * alto_linea + alto_linea // 2
            texto_rect = texto_render.get_rect(center=(self.rect.centerx, centro_y))
            superficie.blit(texto_render, texto_rect)

    def click(self, pos):
        if self.bloqueado:
            return
        if self.rect.collidepoint(pos) and self.accion:
            self.accion()


def pantalla_inicio():
    """Pantalla de bienvenida con tres modos: Letras/palabras, Frases o Progreso."""
    estado = {"modo": None}

    def accion_letras():
        estado["modo"] = "letras"

    def accion_frases():
        estado["modo"] = "frases"

    def accion_progreso():
        estado["modo"] = "progreso"

    boton_letras = Boton(ANCHO // 2 - 150, 375, 300, 58, "JUGAR", accion_frases)
    boton_frases = Boton(ANCHO // 2 - 150, 443, 300, 58, "LETRAS EN ACCIÓN", accion_letras)
    boton_progreso = Boton(ANCHO // 2 - 150, 511, 300, 58, "MI PROGRESO", accion_progreso)
    reloj = pygame.time.Clock()

    while estado["modo"] is None:
        pantalla.fill(COLOR_FONDO)

        if logo_imagen:
            pantalla.blit(logo_imagen, logo_imagen.get_rect(center=(ANCHO // 2, 160)))
        else:
            titulo = fuente_titulo.render("Aprende Lengua de Senas", True, COLOR_TITULO)
            pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 160)))

        subtitulo = fuente_pequena.render("Aprende lengua de senas jugando", True, COLOR_TEXTO)
        pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO // 2, 300)))

        boton_letras.dibujar(pantalla)
        boton_frases.dibujar(pantalla)
        boton_progreso.dibujar(pantalla)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                boton_letras.click(evento.pos)
                boton_frases.click(evento.pos)
                boton_progreso.click(evento.pos)

        pygame.display.flip()
        reloj.tick(60)

    return estado["modo"]


def pantalla_lecciones():
    """Pantalla con los botones de las lecciones. Devuelve la leccion elegida.
    Las lecciones se desbloquean en orden: para jugar la leccion N hay que haber
    completado antes la leccion N-1 (la primera siempre esta disponible)."""
    progreso = cargar_progreso()
    completadas = set(int(numero) for numero in progreso.get("historial", {}).keys())

    botones = []
    columnas = 3
    ancho_boton, alto_boton = 235, 78
    espacio_x, espacio_y = 20, 16
    total_ancho = columnas * ancho_boton + (columnas - 1) * espacio_x
    inicio_x = (ANCHO - total_ancho) // 2
    inicio_y = 80

    seleccion = {"leccion": None, "volver": False}

    for i, leccion in enumerate(LECCIONES):
        col = i % columnas
        fila = i // columnas
        x = inicio_x + col * (ancho_boton + espacio_x)
        y = inicio_y + fila * (alto_boton + espacio_y)

        desbloqueada = leccion["numero"] == 1 or (leccion["numero"] - 1) in completadas

        if desbloqueada:
            texto = f"Leccion {leccion['numero']}\n{leccion['nombre']}"
        else:
            texto = f"Leccion {leccion['numero']}\n(bloqueada)"

        def hacer_accion(leccion=leccion):
            seleccion["leccion"] = leccion

        accion = hacer_accion if desbloqueada else None
        botones.append(Boton(x, y, ancho_boton, alto_boton, texto, accion, bloqueado=not desbloqueada))

    boton_volver = Boton(20, 20, 130, 40, "< VOLVER", lambda: seleccion.update(volver=True))

    reloj = pygame.time.Clock()
    while seleccion["leccion"] is None and not seleccion["volver"]:
        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("Elige una leccion", True, COLOR_TITULO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 35)))

        for boton in botones:
            boton.dibujar(pantalla)
        boton_volver.dibujar(pantalla)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                for boton in botones:
                    boton.click(evento.pos)
                boton_volver.click(evento.pos)

        pygame.display.flip()
        reloj.tick(60)

    return seleccion["leccion"]


def pantalla_frases():
    """Pantalla con los botones de las frases/saludos, con scroll porque son muchas.
    Devuelve la frase elegida."""
    columnas = 3
    ancho_boton, alto_boton = 235, 68
    espacio_x, espacio_y = 20, 14
    total_ancho = columnas * ancho_boton + (columnas - 1) * espacio_x
    inicio_x = (ANCHO - total_ancho) // 2

    # Posicion "logica" de cada boton dentro del contenido (sin contar el scroll todavia)
    posiciones = []
    for i, frase in enumerate(FRASES):
        col = i % columnas
        fila = i // columnas
        x = inicio_x + col * (ancho_boton + espacio_x)
        y = fila * (alto_boton + espacio_y)
        posiciones.append((x, y, frase))

    filas_totales = (len(FRASES) - 1) // columnas + 1
    alto_contenido = filas_totales * (alto_boton + espacio_y) - espacio_y

    area_y_arriba = 90              # debajo del titulo
    area_y_abajo = ALTO - 30        # antes del borde inferior
    alto_area = area_y_abajo - area_y_arriba
    scroll_maximo = max(0, alto_contenido - alto_area)

    estado = {"frase": None, "volver": False, "scroll": 0}
    boton_volver = Boton(20, 20, 130, 40, "< VOLVER", lambda: estado.update(volver=True))

    reloj = pygame.time.Clock()
    while estado["frase"] is None and not estado["volver"]:
        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("Frases y saludos", True, COLOR_TITULO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 40)))

        # Recortamos el area de los botones para que no se dibujen sobre el titulo
        pantalla.set_clip(pygame.Rect(0, area_y_arriba, ANCHO, alto_area))

        botones_visibles = []
        for x, y, frase in posiciones:
            y_pantalla = area_y_arriba + y - estado["scroll"]
            if y_pantalla + alto_boton < area_y_arriba or y_pantalla > area_y_abajo:
                continue  # esta fuera de lo visible, no se dibuja ni se puede clickear

            boton = Boton(x, y_pantalla, ancho_boton, alto_boton, frase["texto"],
                          lambda frase=frase: estado.update(frase=frase))
            boton.dibujar(pantalla)
            botones_visibles.append(boton)

        pantalla.set_clip(None)
        boton_volver.dibujar(pantalla)

        if scroll_maximo > 0:
            texto_ayuda = fuente_pequena.render("Usa la rueda del mouse para ver mas frases", True, COLOR_TEXTO)
            pantalla.blit(texto_ayuda, texto_ayuda.get_rect(center=(ANCHO // 2, ALTO - 14)))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                for boton in botones_visibles:
                    boton.click(evento.pos)
                boton_volver.click(evento.pos)
            if evento.type == pygame.MOUSEWHEEL:
                estado["scroll"] -= evento.y * 35
                estado["scroll"] = max(0, min(estado["scroll"], scroll_maximo))

        pygame.display.flip()
        reloj.tick(60)

    return estado["frase"]


def pantalla_progreso():
    """Pantalla que muestra la categoria (APRENDIZ/ESTUDIANTE/MAESTRO), el nivel 1-5
    y la barra de progreso que se va llenando con los puntos de las lecciones."""
    estado = {"volver": False}
    boton_volver = Boton(20, 20, 130, 40, "< VOLVER", lambda: estado.update(volver=True))
    reloj = pygame.time.Clock()

    ancho_barra, alto_barra = 520, 38
    x_barra = (ANCHO - ancho_barra) // 2
    y_barra = 330

    while not estado["volver"]:
        progreso = cargar_progreso()
        puntos = progreso.get("puntos_actuales", 0)
        categoria = progreso.get("categoria", "APRENDIZ")
        nivel = calcular_nivel(puntos)
        porcentaje = min(puntos / PUNTOS_PARA_LLENAR_BARRA, 1.0)

        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("Tu progreso", True, COLOR_TITULO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 70)))

        # Categoria de aprendizaje (APRENDIZ / ESTUDIANTE / MAESTRO)
        texto_categoria = fuente_titulo.render(categoria, True, COLOR_BOTON)
        pantalla.blit(texto_categoria, texto_categoria.get_rect(center=(ANCHO // 2, 200)))

        # Nivel 1-5, debajo de la categoria
        texto_nivel = fuente_boton.render(f"NIVEL {nivel}", True, COLOR_TEXTO)
        pantalla.blit(texto_nivel, texto_nivel.get_rect(center=(ANCHO // 2, 255)))

        # Fondo de la barra
        rect_fondo_barra = pygame.Rect(x_barra, y_barra, ancho_barra, alto_barra)
        pygame.draw.rect(pantalla, (28, 28, 34), rect_fondo_barra, border_radius=19)

        # Relleno segun el porcentaje de puntos
        ancho_relleno = int(ancho_barra * porcentaje)
        if ancho_relleno > 0:
            rect_relleno = pygame.Rect(x_barra, y_barra, ancho_relleno, alto_barra)
            pygame.draw.rect(pantalla, COLOR_BOTON, rect_relleno, border_radius=19)

        # Borde de la barra
        pygame.draw.rect(pantalla, COLOR_ACENTO, rect_fondo_barra, width=2, border_radius=19)

        # Marcas de los 5 puntos/checkpoints dentro de la barra
        for i in range(1, 5):
            x_marca = x_barra + int(ancho_barra * (i / 5))
            pygame.draw.line(pantalla, COLOR_FONDO, (x_marca, y_barra + 5),
                              (x_marca, y_barra + alto_barra - 5), 2)

        # Puntos y lecciones jugadas, debajo de la barra
        texto_detalle = fuente_pequena.render(
            f"{puntos} / {PUNTOS_PARA_LLENAR_BARRA} puntos    |    Lecciones jugadas: {progreso.get('lecciones_jugadas', 0)}",
            True, COLOR_TEXTO
        )
        pantalla.blit(texto_detalle, texto_detalle.get_rect(center=(ANCHO // 2, y_barra + alto_barra + 35)))

        boton_volver.dibujar(pantalla)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                boton_volver.click(evento.pos)

        pygame.display.flip()
        reloj.tick(60)


def pantalla_resultado_leccion(leccion, puntaje):
    """Pantalla simple que muestra el resultado de la leccion recien jugada con la camara."""
    estado = {"continuar": False}
    boton_continuar = Boton(ANCHO // 2 - 110, 420, 220, 56, "CONTINUAR", lambda: estado.update(continuar=True))
    reloj = pygame.time.Clock()

    while not estado["continuar"]:
        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("Leccion completada", True, COLOR_TITULO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 150)))

        subtitulo = fuente_boton.render(f"Leccion {leccion['numero']}: {leccion['nombre']}", True, COLOR_TEXTO)
        pantalla.blit(subtitulo, subtitulo.get_rect(center=(ANCHO // 2, 220)))

        texto_puntaje = fuente_titulo.render(f"{puntaje} / 100", True, COLOR_BOTON)
        pantalla.blit(texto_puntaje, texto_puntaje.get_rect(center=(ANCHO // 2, 310)))

        boton_continuar.dibujar(pantalla)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                boton_continuar.click(evento.pos)

        pygame.display.flip()
        reloj.tick(60)


def reproducir_video_practica(frase):
    """Abre una ventana de OpenCV que reproduce en bucle el video de la frase elegida."""
    ruta_video = os.path.join(CARPETA_VIDEOS, frase["archivo"])

    if not os.path.exists(ruta_video):
        print(f"\nNo encontre el video para '{frase['texto']}'.")
        print(f"Falta el archivo: {os.path.abspath(ruta_video)}")
        print(f"Grabalo y guardalo con ese nombre exacto dentro de la carpeta '{CARPETA_VIDEOS}'.\n")
        return

    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        print(f"No se pudo abrir el video: {ruta_video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    demora = int(1000 / fps) if fps and fps > 0 else 33

    print(f"\nMostrando: {frase['texto']}  (R: repetir desde el inicio | ESC: volver al menu)")

    try:
        while True:
            exito, cuadro = cap.read()
            if not exito:
                # Termino el video: lo repetimos automaticamente
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            cv2.putText(cuadro, f"Practica: {frase['texto']}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(cuadro, "R: repetir | ESC: volver al menu",
                        (10, cuadro.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Practica de frases", cuadro)

            tecla = cv2.waitKey(demora) & 0xFF
            if tecla == 27:  # ESC
                break
            elif tecla == ord('r'):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    finally:
        cap.release()
        cv2.destroyAllWindows()


def pantalla_lecciones_diccionario():
    """Selector de lecciones del Diccionario con desbloqueo progresivo.
    Devuelve la lección elegida o None si el jugador volvió."""
    progreso = cargar_progreso()
    completadas_dic = set(
        int(n) for n in progreso.get("historial_diccionario", {}).keys()
    )

    botones = []
    columnas = 3
    ancho_boton, alto_boton = 235, 78
    espacio_x, espacio_y = 20, 16
    total_ancho = columnas * ancho_boton + (columnas - 1) * espacio_x
    inicio_x = (ANCHO - total_ancho) // 2
    inicio_y = 80

    seleccion = {"leccion": None, "volver": False}

    for i, lec in enumerate(LECCIONES_DICCIONARIO):
        col  = i % columnas
        fila = i // columnas
        x = inicio_x + col * (ancho_boton + espacio_x)
        y = inicio_y + fila * (alto_boton + espacio_y)

        desbloqueada = lec["numero"] == 1 or (lec["numero"] - 1) in completadas_dic
        texto = (f"Leccion {lec['numero']}\n{lec['nombre']}"
                 if desbloqueada else f"Leccion {lec['numero']}\n(bloqueada)")

        def hacer_accion(lec=lec):
            seleccion["leccion"] = lec

        accion = hacer_accion if desbloqueada else None
        botones.append(Boton(x, y, ancho_boton, alto_boton, texto, accion,
                             bloqueado=not desbloqueada))

    boton_volver = Boton(20, 20, 130, 40, "< VOLVER",
                         lambda: seleccion.update(volver=True))
    reloj = pygame.time.Clock()

    while seleccion["leccion"] is None and not seleccion["volver"]:
        pantalla.fill(COLOR_FONDO)

        titulo = fuente_titulo.render("Diccionario - Elige una leccion",
                                      True, COLOR_TITULO)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 35)))

        for boton in botones:
            boton.dibujar(pantalla)
        boton_volver.dibujar(pantalla)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                for boton in botones:
                    boton.click(evento.pos)
                boton_volver.click(evento.pos)

        pygame.display.flip()
        reloj.tick(60)

    return seleccion["leccion"]


# --- Flujo principal ---
if __name__ == "__main__":
    while True:
        modo = pantalla_inicio()

        if modo == "letras":
            leccion_elegida = pantalla_lecciones()
            if leccion_elegida:
                print(f"Eligio: Leccion {leccion_elegida['numero']} - {leccion_elegida['nombre']}")
                print(f"Palabras de esta leccion: {leccion_elegida['palabras']}")

                puntaje = jugar_leccion(leccion_elegida)
                if puntaje is not None:
                    registrar_resultado_leccion(leccion_elegida["numero"], puntaje)
                    pantalla_resultado_leccion(leccion_elegida, puntaje)

        elif modo == "frases":
            lec_dic = pantalla_lecciones_diccionario()
            if lec_dic:
                completado = jugar_diccionario(pantalla, lec_dic, FRASES, CARPETA_VIDEOS)
                if completado:
                    # Guardar en historial_diccionario para desbloquear la siguiente
                    progreso = cargar_progreso()
                    progreso.setdefault("historial_diccionario", {})[
                        str(lec_dic["numero"])] = True
                    from progreso import guardar_progreso
                    guardar_progreso(progreso)

        elif modo == "progreso":
            pantalla_progreso()
