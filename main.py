import pygame
import sys
import time
from clases.ingrediente import VegetalesYFrutas, Proteina, PanesYBases
from clases.estacion import Despensa, Cocina, TablaDeCortar, Freidora, EstacionEntrega
from clases.chef import Chef
from clases.receta import Receta
from clases.cocina import Cocina as CocinaJuego  # alias para no chocar con Cocina de estacion

# ============================================================
# COLORES
# ============================================================
BLANCO  = (255, 255, 255)
NEGRO   = (0, 0, 0)
ROJO    = (255, 0, 0)
VERDE   = (0, 255, 0)
AZUL    = (0, 0, 255)
GRIS    = (150, 150, 150)
AMARILLO = (255, 255, 0)
NARANJA = (255, 165, 0)

# ============================================================
# CONFIGURACIÓN DE VENTANA
# ============================================================
ANCHO = 800
ALTO  = 600
CELDA = 80

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Crazy Snack Rush TEC")
reloj = pygame.time.Clock()
fuente       = pygame.font.SysFont("arial", 20)
fuente_titulo = pygame.font.SysFont("arial", 48)


# ============================================================
# SPRITES
# ============================================================
# cargar_sprite intenta cargar una imagen PNG.
# Si el archivo aún no existe devuelve None y el juego dibuja
# un rectángulo de color como fallback, sin crashear.
def cargar_sprite(ruta, tamano=None):
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        if tamano:
            imagen = pygame.transform.scale(imagen, tamano)
        return imagen
    except (FileNotFoundError, pygame.error):
        return None

# Genera una versión oscura del sprite para el chef inactivo.
# BLEND_RGB_MULT multiplica el color sin tocar el canal alpha.
def oscurecer_sprite(sprite, factor=0.45):
    if sprite is None:
        return None
    oscuro = sprite.copy()
    nivel = int(255 * factor)
    oscuro.fill((nivel, nivel, nivel, 255), special_flags=pygame.BLEND_RGB_MULT)
    return oscuro

# --- Cargar sprites UNA sola vez al inicio (nunca dentro del while) ---
# Coloca tus PNGs en la carpeta assets/ con estos nombres exactos.
SPRITE_PISO = cargar_sprite("assets/floor.png", (CELDA, CELDA))

# Las claves deben coincidir EXACTAMENTE con estacion.nombre
SPRITES_ESTACIONES = {
    "Despensa Tomate":  cargar_sprite("assets/despensa_tomate.png",  (CELDA - 5, CELDA - 5)),
    "Despensa Pollo":   cargar_sprite("assets/despensa_pollo.png",   (CELDA - 5, CELDA - 5)),
    "Despensa Pan":     cargar_sprite("assets/despensa_pan.png",     (CELDA - 5, CELDA - 5)),
    # CORRECCIÓN: nombre unificado con TablaDeCortar.__init__ ("Tabla de Cortar")
    "Tabla de Cortar":  cargar_sprite("assets/tabla.png",            (CELDA - 5, CELDA - 5)),
    "Cocina":           cargar_sprite("assets/estufa.png",           (CELDA - 5, CELDA - 5)),
    "Freidora":         cargar_sprite("assets/freidora.png",         (CELDA - 5, CELDA - 5)),
    "Entrega":          cargar_sprite("assets/entrega.png",          (CELDA - 5, CELDA - 5)),
}

SPRITE_CHEF1       = cargar_sprite("assets/chef.png", (CELDA - 10, CELDA - 10))
SPRITE_CHEF2       = cargar_sprite("assets/chef.png", (CELDA - 10, CELDA - 10))
SPRITE_CHEF1_OSCURO = oscurecer_sprite(SPRITE_CHEF1)
SPRITE_CHEF2_OSCURO = oscurecer_sprite(SPRITE_CHEF2)


# ============================================================
# FUNCIONES DE DIBUJO
# ============================================================
def dibujar_grid(ventana):
    if SPRITE_PISO:
        for x in range(0, ANCHO, CELDA):
            for y in range(0, ALTO, CELDA):
                ventana.blit(SPRITE_PISO, (x, y))
    else:
        ventana.fill((40, 40, 40))
        for x in range(0, ANCHO, CELDA):
            pygame.draw.line(ventana, GRIS, (x, 0), (x, ALTO))
        for y in range(0, ALTO, CELDA):
            pygame.draw.line(ventana, GRIS, (0, y), (ANCHO, y))

def dibujar_hud(ventana, cocina, fuente):
    # Puntos y tiempo
    texto_puntos = fuente.render(f"Puntos: {cocina.puntos}", True, BLANCO)
    texto_tiempo = fuente.render(f"Tiempo: {cocina.tiempo_restante:.1f}s", True, BLANCO)
    ventana.blit(texto_puntos, (10, 10))
    ventana.blit(texto_tiempo, (ANCHO - 200, 10))

    # AÑADIDO: mostrar órdenes activas en pantalla
    y_orden = 40
    for i, orden in enumerate(cocina.ordenes):
        color = VERDE if orden.tiempo_restante() > orden.tiempo_maximo * 0.4 else NARANJA
        texto_orden = fuente.render(str(orden), True, color)
        ventana.blit(texto_orden, (10, y_orden + i * 22))

def dibujar_chef(ventana, chef, fuente, sprite_normal=None, sprite_oscuro=None):
    sprite = sprite_normal if chef.activo else sprite_oscuro
    if sprite:
        ventana.blit(sprite, (chef.x, chef.y))
    else:
        color = VERDE if chef.activo else AZUL
        pygame.draw.rect(ventana, color, (chef.x, chef.y, CELDA - 10, CELDA - 10))
        texto = fuente.render(chef.nombre[0], True, NEGRO)
        ventana.blit(texto, (chef.x + 25, chef.y + 25))

    # Mostrar ingrediente en mano sobre el chef
    if chef.ingrediente_en_mano:
        texto_ing = fuente.render(chef.ingrediente_en_mano.nombre[0], True, AMARILLO)
        ventana.blit(texto_ing, (chef.x, chef.y - 18))

def dibujar_estaciones(ventana, estaciones, fuente):
    for estacion in estaciones:
        sprite = SPRITES_ESTACIONES.get(estacion.nombre)
        if sprite:
            ventana.blit(sprite, (estacion.x, estacion.y))
        else:
            pygame.draw.rect(ventana, AMARILLO,
                             (estacion.x, estacion.y, CELDA - 5, CELDA - 5))
            texto = fuente.render(estacion.nombre[:2], True, NEGRO)
            ventana.blit(texto, (estacion.x + 10, estacion.y + 25))


# ============================================================
# BOTÓN REUTILIZABLE
# ============================================================
class Boton:
    def __init__(self, x, y, ancho, alto, texto,
                 color_normal=GRIS, color_hover=AMARILLO):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_normal = color_normal
        self.color_hover  = color_hover

    def dibujar(self, ventana, fuente):
        color = (self.color_hover
                 if self.rect.collidepoint(pygame.mouse.get_pos())
                 else self.color_normal)
        pygame.draw.rect(ventana, color, self.rect)
        pygame.draw.rect(ventana, NEGRO, self.rect, 2)
        texto_render = fuente.render(self.texto, True, NEGRO)
        ventana.blit(texto_render, texto_render.get_rect(center=self.rect.center))

    def fue_clickeado(self, pos):
        return self.rect.collidepoint(pos)


# ============================================================
# PANTALLA DE INICIO
# ============================================================
def pantalla_inicio(ventana, fuente, fuente_titulo, reloj):
    boton_jugar = Boton(ANCHO // 2 - 100, 320, 200, 60, "JUGAR")
    boton_salir = Boton(ANCHO // 2 - 100, 400, 200, 60, "SALIR")
    titulo = fuente_titulo.render("Crazy Snack Rush TEC", True, BLANCO)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_jugar.fue_clickeado(evento.pos):
                    return "jugar"
                if boton_salir.fue_clickeado(evento.pos):
                    return "salir"

        ventana.fill(NEGRO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 180))
        boton_jugar.dibujar(ventana, fuente)
        boton_salir.dibujar(ventana, fuente)
        pygame.display.flip()
        reloj.tick(60)


# ============================================================
# PANTALLA DE SELECCIÓN DE NIVELES
# ============================================================
def pantalla_seleccion_niveles(ventana, fuente, fuente_titulo, reloj):
    niveles = [
        {"nombre": "Nivel 1 - Oceano",  "id": "nivel_1", "disponible": True},
        {"nombre": "Nivel 2 (pronto)",  "id": "nivel_2", "disponible": False},
        {"nombre": "Nivel 3 (pronto)",  "id": "nivel_3", "disponible": False},
    ]

    botones = []
    for i, nivel in enumerate(niveles):
        color = GRIS if nivel["disponible"] else (80, 80, 80)
        botones.append(Boton(ANCHO // 2 - 150, 160 + i * 100, 300, 70,
                             nivel["nombre"], color_normal=color))

    boton_volver = Boton(20, 20, 120, 50, "Volver")
    titulo = fuente_titulo.render("Selecciona un nivel", True, BLANCO)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.fue_clickeado(evento.pos):
                    return "volver"
                for i, boton in enumerate(botones):
                    if boton.fue_clickeado(evento.pos) and niveles[i]["disponible"]:
                        return niveles[i]["id"]

        ventana.fill(NEGRO)
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 80))
        for boton in botones:
            boton.dibujar(ventana, fuente)
        boton_volver.dibujar(ventana, fuente)
        pygame.display.flip()
        reloj.tick(60)


# ============================================================
# CREACIÓN DE NIVEL
# ============================================================
def crear_nivel(id_nivel):
    """
    Crea y devuelve todos los objetos del nivel indicado.
    Para agregar Nivel 2 o 3, agregar un elif aquí con sus propias estaciones y recetas.
    """
    # --- Estaciones comunes al Nivel 1 ---
    despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
    despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
    despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
    tabla      = TablaDeCortar()
    cocina_est = Cocina()
    freidora   = Freidora()
    entrega    = EstacionEntrega()

    # Posiciones en el grid (x, y en píxeles)
    despensa_tomate.x, despensa_tomate.y = 0,   0
    despensa_pollo.x,  despensa_pollo.y  = 80,  0
    despensa_pan.x,    despensa_pan.y    = 160, 0
    tabla.x,      tabla.y      = 0,   80
    cocina_est.x, cocina_est.y = 80,  80
    freidora.x,   freidora.y   = 160, 80
    entrega.x,    entrega.y    = 240, 80

    estaciones = [despensa_tomate, despensa_pollo, despensa_pan,
                  tabla, cocina_est, freidora, entrega]

    # --- Recetas del Nivel 1 ---
    # Ensalada: solo un tomate cortado
    # CORRECCIÓN en estado: VegetalesYFrutas empieza "crudo",
    # la receta debe pedir el estado DESPUÉS de procesarse ("cortado").
    tomate_cortado = VegetalesYFrutas("Tomate")
    tomate_cortado.estado = "cortado"
    receta_ensalada = Receta("Ensalada", [tomate_cortado], 100, 30)

    # Pollo cocinado: una proteína cocida
    pollo_cocinado = Proteina("Pollo")
    pollo_cocinado.estado = "cocinado"
    pollo_cocinado.cocinada = True
    receta_pollo = Receta("Pollo cocinado", [pollo_cocinado], 150, 40)

    recetas_posibles = [receta_ensalada, receta_pollo]

    # --- Cocina del juego ---
    cocina_juego = CocinaJuego("Oceano", recetas_posibles, tiempo_juego=120,
                               intervalo_recetas=10)

    # --- Chefs ---
    chef1 = Chef("Chef1", 320, 240)
    chef2 = Chef("Chef2", 400, 240)
    chef2.activo = False  # empieza inactivo; se activa con TAB

    cocina_juego.agregar_chef(chef1)
    cocina_juego.agregar_chef(chef2)
    for est in estaciones:
        cocina_juego.agregar_estacion(est)

    return cocina_juego, estaciones, chef1, chef2


# ============================================================
# LOOP DE JUEGO
# ============================================================
def jugar_nivel(ventana, fuente, reloj, cocina_juego, estaciones, chef1, chef2):
    chef_activo  = chef1
    ultimo_tiempo = time.time()

    while not cocina_juego.juego_terminado():
        ahora = time.time()
        delta = ahora - ultimo_tiempo
        ultimo_tiempo = ahora

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.KEYDOWN:
                # TAB: intercambiar chef activo
                if evento.key == pygame.K_TAB:
                    if chef_activo == chef1:
                        chef_activo, chef1.activo, chef2.activo = chef2, False, True
                    else:
                        chef_activo, chef1.activo, chef2.activo = chef1, True, False

                # ESPACIO: acción de interacción con estación más cercana
                # CORRECCIÓN AÑADIDA: antes no había tecla de acción implementada.
                # El enunciado dice "presionar el botón de acción" para usar estaciones.
                if evento.key == pygame.K_SPACE:
                    for estacion in estaciones:
                        # Detecta si el chef está adyacente a la estación (dentro de 1 celda)
                        if (abs(chef_activo.x - estacion.x) < CELDA and
                                abs(chef_activo.y - estacion.y) < CELDA):
                            from clases.estacion import Despensa, EstacionEntrega
                            if isinstance(estacion, Despensa):
                                chef_activo.recoger_ingrediente(estacion)
                            elif isinstance(estacion, EstacionEntrega):
                                # Intenta entregar con cada orden activa
                                for orden in cocina_juego.ordenes:
                                    if cocina_juego.entregar_orden(
                                            chef_activo, orden, estacion):
                                        break
                            else:
                                chef_activo.usar_estacion(estacion)
                            break  # solo interactúa con una estación por acción

        # Movimiento del chef activo con teclas de dirección
        teclas = pygame.key.get_pressed()
        dx = (teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT])
        dy = (teclas[pygame.K_DOWN]  - teclas[pygame.K_UP])
        chef_activo.mover(dx, dy)

        # Actualizar lógica del juego
        cocina_juego.actualizar(delta)

        # --- Dibujo ---
        ventana.fill(NEGRO)
        dibujar_grid(ventana)
        dibujar_estaciones(ventana, estaciones, fuente)
        dibujar_chef(ventana, chef1, fuente, SPRITE_CHEF1, SPRITE_CHEF1_OSCURO)
        dibujar_chef(ventana, chef2, fuente, SPRITE_CHEF2, SPRITE_CHEF2_OSCURO)
        dibujar_hud(ventana, cocina_juego, fuente)

        pygame.display.flip()
        reloj.tick(60)

    return "fin"


# ============================================================
# PANTALLA DE FIN
# ============================================================
def pantalla_fin(ventana, fuente, fuente_titulo, cocina_juego):
    ventana.fill(NEGRO)
    titulo  = fuente_titulo.render("¡Tiempo!", True, AMARILLO)
    puntos  = fuente.render(f"Puntuación final: {cocina_juego.puntos}", True, BLANCO)
    credito = fuente.render("Volviendo al menú...", True, GRIS)
    ventana.blit(titulo,  (ANCHO // 2 - titulo.get_width()  // 2, 200))
    ventana.blit(puntos,  (ANCHO // 2 - puntos.get_width()  // 2, 300))
    ventana.blit(credito, (ANCHO // 2 - credito.get_width() // 2, 360))
    pygame.display.flip()
    time.sleep(3)


# ============================================================
# MÁQUINA DE ESTADOS PRINCIPAL
# ============================================================
estado       = "menu"
cocina_juego = None
estaciones   = None
chef1 = chef2 = None

while estado != "salir":

    if estado == "menu":
        estado = pantalla_inicio(ventana, fuente, fuente_titulo, reloj)
        if estado == "jugar":
            estado = "seleccion_niveles"

    elif estado == "seleccion_niveles":
        resultado = pantalla_seleccion_niveles(ventana, fuente, fuente_titulo, reloj)
        if resultado == "volver":
            estado = "menu"
        elif resultado == "salir":
            estado = "salir"
        else:
            cocina_juego, estaciones, chef1, chef2 = crear_nivel(resultado)
            estado = "jugando"

    elif estado == "jugando":
        resultado = jugar_nivel(ventana, fuente, reloj,
                                cocina_juego, estaciones, chef1, chef2)
        if resultado == "fin":
            # CORRECCIÓN: pantalla_fin recibe fuente_titulo también
            pantalla_fin(ventana, fuente, fuente_titulo, cocina_juego)
            estado = "menu"
        else:
            estado = "salir"

pygame.quit()
sys.exit()