import pygame
import sys
import time
from clases.ingrediente import VegetalesYFrutas, Proteina, PanesYBases
from clases.estacion import Despensa, Cocina, TablaDeCortar, Freidora, EstacionEntrega, MesaEnsamblaje
from clases.chef import Chef
from clases.receta import Receta
from clases.cocina import Cocina as CocinaJuego

BLANCO   = (255, 255, 255)
NEGRO    = (0, 0, 0)
ROJO     = (255, 0, 0)
VERDE    = (0, 200, 0)
AZUL     = (0, 100, 255)
GRIS     = (150, 150, 150)
AMARILLO = (255, 220, 0)
NARANJA  = (255, 140, 0)
CAFE     = (139, 90, 43)
MORADO   = (150, 0, 200)

COLOR_INGREDIENTE = {
    "Tomate":  (220,  50,  50),
    "Pollo":   (240, 200, 100),
    "Pan":     (210, 170,  90),
    "Papa":    (230, 210, 130),
}
COLOR_INGREDIENTE_DEFAULT = (180, 180, 180)

ANCHO = 800
ALTO  = 600
CELDA = 80

HUD_ALTO    = 40
PANEL_ANCHO = 200

COCINA_X     = 0
COCINA_Y     = HUD_ALTO
COCINA_ANCHO = ANCHO - PANEL_ANCHO
COCINA_ALTO  = ALTO - HUD_ALTO

pygame.init()
COCINA_RECT = pygame.Rect(COCINA_X, COCINA_Y, COCINA_ANCHO, COCINA_ALTO)

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Crazy Snack Rush TEC")
reloj = pygame.time.Clock()
fuente        = pygame.font.SysFont("arial", 18)
fuente_titulo = pygame.font.SysFont("arial", 46)
fuente_chica  = pygame.font.SysFont("arial", 14)


def cargar_sprite(ruta, tamano=None):
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        if tamano:
            imagen = pygame.transform.scale(imagen, tamano)
        return imagen
    except (FileNotFoundError, pygame.error):
        return None

def oscurecer_sprite(sprite, factor=0.45):
    if sprite is None:
        return None
    oscuro = sprite.copy()
    nivel = int(255 * factor)
    oscuro.fill((nivel, nivel, nivel, 255), special_flags=pygame.BLEND_RGB_MULT)
    return oscuro

SPRITE_PISO = cargar_sprite("assets/floor.png", (CELDA, CELDA))

SPRITES_ESTACIONES = {
    "Despensa Tomate": cargar_sprite("assets/despensa_tomate.png", (CELDA-5, CELDA-5)),
    "Despensa Pollo":  cargar_sprite("assets/despensa_pollo.png",  (CELDA-5, CELDA-5)),
    "Despensa Pan":    cargar_sprite("assets/despensa_pan.png",    (CELDA-5, CELDA-5)),
    "Tabla de Cortar": cargar_sprite("assets/tabla.png",           (CELDA-5, CELDA-5)),
    "Cocina":          cargar_sprite("assets/estufa.png",          (CELDA-5, CELDA-5)),
    "Freidora":        cargar_sprite("assets/freidora.png",        (CELDA-5, CELDA-5)),
    "Entrega":         cargar_sprite("assets/entrega.png",         (CELDA-5, CELDA-5)),
    "Ensamblaje":      cargar_sprite("assets/ensamblaje.png",      (CELDA-5, CELDA-5)),
}

SPRITE_CHEF1        = cargar_sprite("assets/chef1.png", (CELDA-16, CELDA-16))
SPRITE_CHEF2        = cargar_sprite("assets/chef2.png", (CELDA-16, CELDA-16))
SPRITE_CHEF1_OSCURO = oscurecer_sprite(SPRITE_CHEF1)
SPRITE_CHEF2_OSCURO = oscurecer_sprite(SPRITE_CHEF2)


def dibujar_grid(ventana):
    if SPRITE_PISO:
        for x in range(COCINA_X, COCINA_X + COCINA_ANCHO, CELDA):
            for y in range(COCINA_Y, COCINA_Y + COCINA_ALTO, CELDA):
                ventana.blit(SPRITE_PISO, (x, y))
    else:
        pygame.draw.rect(ventana, (45, 45, 45), COCINA_RECT)
        for x in range(COCINA_X, COCINA_X + COCINA_ANCHO, CELDA):
            pygame.draw.line(ventana, (70, 70, 70), (x, COCINA_Y), (x, COCINA_Y + COCINA_ALTO))
        for y in range(COCINA_Y, COCINA_Y + COCINA_ALTO, CELDA):
            pygame.draw.line(ventana, (70, 70, 70), (COCINA_X, y), (COCINA_X + COCINA_ANCHO, y))


def dibujar_estaciones(ventana, estaciones, fuente):
    for est in estaciones:
        sprite = SPRITES_ESTACIONES.get(est.nombre)
        if sprite:
            ventana.blit(sprite, (est.x, est.y))
        else:
            color_fondo = MORADO if isinstance(est, MesaEnsamblaje) else AMARILLO
            pygame.draw.rect(ventana, color_fondo, (est.x, est.y, CELDA-5, CELDA-5))
            pygame.draw.rect(ventana, NEGRO,       (est.x, est.y, CELDA-5, CELDA-5), 2)
            palabras = est.nombre.split()
            for i, p in enumerate(palabras[:2]):
                t = fuente_chica.render(p, True, NEGRO)
                ventana.blit(t, (est.x + 4, est.y + 8 + i * 16))

        # Si es mesa de ensamblaje, muestra cuadraditos de ingredientes depositados
        if isinstance(est, MesaEnsamblaje):
            for k, ing in enumerate(est.ingredientes_depositados[:4]):
                dibujar_ingrediente_cuadrado(ventana, ing,
                                             est.x + 12 + k * 16,
                                             est.y + CELDA - 22)


def dibujar_ingrediente_cuadrado(ventana, ingrediente, cx, cy, size=20):
    color_relleno = COLOR_INGREDIENTE.get(ingrediente.nombre, COLOR_INGREDIENTE_DEFAULT)
    colores_borde = {
        "crudo":    NEGRO,
        "cortado":  VERDE,
        "cocinado": NARANJA,
        "frito":    CAFE,
        "listo":    BLANCO,
    }
    color_borde = colores_borde.get(ingrediente.estado, GRIS)
    rect = pygame.Rect(cx - size//2, cy - size//2, size, size)
    pygame.draw.rect(ventana, color_relleno, rect)
    pygame.draw.rect(ventana, color_borde,   rect, 3)
    inicial = ingrediente.estado[0].upper()
    t = fuente_chica.render(inicial, True, NEGRO)
    ventana.blit(t, (rect.x + 4, rect.y + 3))


def dibujar_barra_progreso(ventana, chef, estaciones, dir_actual):
    """Dibuja barra de progreso sobre la estación que está procesando el chef."""
    if chef.estacion_actual is None or chef.progreso_proceso <= 0:
        return
    est = chef.estacion_actual
    tiempo_req = est.tiempo_base * chef.multiplicador_proceso
    ratio = min(chef.progreso_proceso / tiempo_req, 1.0)

    bx = est.x
    by = est.y - 12
    bw = CELDA - 5
    bh = 8

    pygame.draw.rect(ventana, GRIS,  (bx, by, bw, bh))
    pygame.draw.rect(ventana, VERDE, (bx, by, int(bw * ratio), bh))
    pygame.draw.rect(ventana, BLANCO,(bx, by, bw, bh), 1)


def dibujar_chef(ventana, chef, fuente, sprite_normal=None, sprite_oscuro=None):
    sprite = sprite_normal if chef.activo else sprite_oscuro
    if sprite:
        ventana.blit(sprite, (chef.x, chef.y))
    else:
        color = VERDE if chef.activo else AZUL
        pygame.draw.rect(ventana, color, chef.rect)
        pygame.draw.rect(ventana, BLANCO, chef.rect, 2)
        t = fuente.render(chef.nombre[0], True, NEGRO)
        ventana.blit(t, (chef.x + 22, chef.y + 22))

    if chef.ingrediente_en_mano:
        dibujar_ingrediente_cuadrado(
            ventana, chef.ingrediente_en_mano,
            chef.x + (CELDA-16)//2,
            chef.y - 14
        )


def dibujar_hud(ventana, cocina, fuente, fuente_chica):
    pygame.draw.rect(ventana, (20, 20, 20), (0, 0, ANCHO, HUD_ALTO))
    pygame.draw.line(ventana, GRIS, (0, HUD_ALTO), (ANCHO, HUD_ALTO), 1)

    t_puntos = fuente.render(f"Puntos: {cocina.puntos}", True, AMARILLO)
    t_tiempo  = fuente.render(f"Tiempo: {max(0, cocina.tiempo_restante):.0f}s", True, BLANCO)
    ventana.blit(t_puntos, (10, HUD_ALTO // 2 - t_puntos.get_height() // 2))
    ventana.blit(t_tiempo,  (ANCHO - PANEL_ANCHO - t_tiempo.get_width() - 10,
                              HUD_ALTO // 2 - t_tiempo.get_height() // 2))

    panel_x = ANCHO - PANEL_ANCHO
    pygame.draw.rect(ventana, (25, 25, 25), (panel_x, 0, PANEL_ANCHO, ALTO))
    pygame.draw.line(ventana, GRIS, (panel_x, 0), (panel_x, ALTO), 1)

    t_header = fuente_chica.render("── ÓRDENES ──", True, GRIS)
    ventana.blit(t_header, (panel_x + 10, HUD_ALTO // 2 - t_header.get_height() // 2))
    pygame.draw.line(ventana, GRIS, (panel_x, HUD_ALTO), (ANCHO, HUD_ALTO), 1)

    margen_barra = 14
    ancho_barra  = PANEL_ANCHO - margen_barra * 2

    for i, orden in enumerate(cocina.ordenes):
        y_base = HUD_ALTO + 10 + i * 90
        if y_base + 86 > ALTO:
            break
        ratio = orden.tiempo_restante() / orden.tiempo_maximo
        color_tiempo = VERDE if ratio > 0.5 else (NARANJA if ratio > 0.25 else ROJO)

        t_nombre   = fuente_chica.render(orden.nombre, True, BLANCO)
        t_pts      = fuente_chica.render(f"Pts: {orden.puntos_actuales}", True, AMARILLO)
        t_tiempo_o = fuente_chica.render(f"{orden.tiempo_restante():.0f}s", True, color_tiempo)

        ventana.blit(t_nombre,   (panel_x + margen_barra, y_base))
        ventana.blit(t_pts,      (panel_x + margen_barra, y_base + 16))
        ventana.blit(t_tiempo_o, (panel_x + margen_barra, y_base + 32))

        for j, ing in enumerate(orden.ingredientes):
            texto_ing = f"• {ing.nombre} ({ing.estado})"
            color_ing = VERDE if ing.estado in ("cortado", "cocinado", "frito", "listo") else GRIS
            t_ing = fuente_chica.render(texto_ing, True, color_ing)
            ventana.blit(t_ing, (panel_x + margen_barra, y_base + 48 + j * 14))

        barra_y = y_base + 48 + len(orden.ingredientes) * 14 + 4
        pygame.draw.rect(ventana, GRIS,         (panel_x + margen_barra, barra_y, ancho_barra, 6))
        pygame.draw.rect(ventana, color_tiempo, (panel_x + margen_barra, barra_y, int(ancho_barra * ratio), 6))


def agregar_flotante(lista, texto, x, y, color, duracion=1.0):
    lista.append({"texto": texto, "x": x, "y": y,
                  "color": color, "vida": duracion})

def dibujar_flotantes(ventana, fuente_chica, lista, delta):
    for m in lista[:]:
        t = fuente_chica.render(m["texto"], True, m["color"])
        ventana.blit(t, (m["x"] - t.get_width()//2, int(m["y"])))
        m["y"]    -= 40 * delta
        m["vida"] -= delta
        if m["vida"] <= 0:
            lista.remove(m)


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
        pygame.draw.rect(ventana, color, self.rect, border_radius=8)
        pygame.draw.rect(ventana, NEGRO, self.rect, 2, border_radius=8)
        t = fuente.render(self.texto, True, NEGRO)
        ventana.blit(t, t.get_rect(center=self.rect.center))

    def fue_clickeado(self, pos):
        return self.rect.collidepoint(pos)


def pantalla_inicio(ventana, fuente, fuente_titulo, reloj):
    boton_jugar = Boton(ANCHO//2 - 100, 320, 200, 60, "JUGAR")
    boton_salir = Boton(ANCHO//2 - 100, 400, 200, 60, "SALIR")
    titulo = fuente_titulo.render("Crazy Snack Rush TEC", True, BLANCO)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_jugar.fue_clickeado(evento.pos): return "jugar"
                if boton_salir.fue_clickeado(evento.pos): return "salir"

        ventana.fill(NEGRO)
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 180))
        boton_jugar.dibujar(ventana, fuente)
        boton_salir.dibujar(ventana, fuente)
        pygame.display.flip()
        reloj.tick(60)


def pantalla_seleccion_niveles(ventana, fuente, fuente_titulo, reloj):
    niveles = [
        {"nombre": "Nivel 1 - Oceano",   "id": "nivel_1", "disponible": True},
        {"nombre": "Nivel 2 - Selva",    "id": "nivel_2", "disponible": True},
        {"nombre": "Nivel 3 - Espacio",  "id": "nivel_3", "disponible": True},
    ]
    botones = []
    for i, niv in enumerate(niveles):
        color = GRIS if niv["disponible"] else (70, 70, 70)
        botones.append(Boton(ANCHO//2 - 150, 160 + i*100, 300, 70,
                             niv["nombre"], color_normal=color))

    boton_volver = Boton(20, 20, 120, 50, "Volver")
    titulo = fuente_titulo.render("Selecciona un nivel", True, BLANCO)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.fue_clickeado(evento.pos): return "volver"
                for i, boton in enumerate(botones):
                    if boton.fue_clickeado(evento.pos) and niveles[i]["disponible"]:
                        return niveles[i]["id"]

        ventana.fill(NEGRO)
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 80))
        for b in botones: b.dibujar(ventana, fuente)
        boton_volver.dibujar(ventana, fuente)
        pygame.display.flip()
        reloj.tick(60)


def crear_nivel(id_nivel):
    if id_nivel == "nivel_1":
        return _nivel_1()
    elif id_nivel == "nivel_2":
        return _nivel_2()
    elif id_nivel == "nivel_3":
        return _nivel_3()


def _chefs_default():
    cx = COCINA_X + COCINA_ANCHO // 2
    cy = COCINA_Y + COCINA_ALTO  // 2
    # Chef1: cocinero — velocidad normal, procesa rápido
    chef1 = Chef("Chef1", cx - CELDA, cy, velocidad=4, multiplicador_proceso=1.0)
    # Chef2: ayudante — velocidad alta, procesa lento
    chef2 = Chef("Chef2", cx + CELDA, cy, velocidad=7, multiplicador_proceso=3.0)
    chef2.activo = False
    return chef1, chef2


def _nivel_1():
    despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
    despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
    despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
    tabla           = TablaDeCortar()
    cocina_est      = Cocina()
    freidora        = Freidora()
    ensamblaje      = MesaEnsamblaje()
    entrega         = EstacionEntrega()

    despensa_tomate.x, despensa_tomate.y = COCINA_X,             COCINA_Y
    despensa_pollo.x,  despensa_pollo.y  = COCINA_X + CELDA * 2, COCINA_Y
    despensa_pan.x,    despensa_pan.y    = COCINA_X + CELDA * 4, COCINA_Y
    tabla.x,           tabla.y           = COCINA_X,             COCINA_Y + CELDA * 2
    cocina_est.x,      cocina_est.y      = COCINA_X,             COCINA_Y + CELDA * 4
    freidora.x,        freidora.y        = COCINA_X + CELDA * 2, COCINA_Y + COCINA_ALTO - CELDA
    ensamblaje.x,      ensamblaje.y      = COCINA_X + CELDA * 4, COCINA_Y + COCINA_ALTO - CELDA
    entrega.x,         entrega.y         = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA

    estaciones = [despensa_tomate, despensa_pollo, despensa_pan,
                  tabla, cocina_est, freidora, ensamblaje, entrega]

    tomate_c = VegetalesYFrutas("Tomate"); tomate_c.estado = "cortado"
    receta_ensalada = Receta("Ensalada", [tomate_c], 100, 30)

    pollo_c = Proteina("Pollo"); pollo_c.estado = "cocinado"; pollo_c.cocinada = True
    receta_pollo = Receta("Pollo Asado", [pollo_c], 150, 40)

    cocina_juego = CocinaJuego("Oceano", [receta_ensalada, receta_pollo],
                               tiempo_juego=120, intervalo_recetas=10)
    chef1, chef2 = _chefs_default()
    cocina_juego.agregar_chef(chef1)
    cocina_juego.agregar_chef(chef2)
    for est in estaciones:
        cocina_juego.agregar_estacion(est)

    return cocina_juego, estaciones, chef1, chef2


def _nivel_2():
    despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
    despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
    despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
    despensa_papa   = Despensa("Despensa Papa",    VegetalesYFrutas("Papa"))
    tabla           = TablaDeCortar()
    cocina_est      = Cocina()
    freidora        = Freidora()
    ensamblaje      = MesaEnsamblaje()
    entrega         = EstacionEntrega()

    # Layout en U — estaciones más separadas
    despensa_tomate.x, despensa_tomate.y = COCINA_X,             COCINA_Y
    despensa_pollo.x,  despensa_pollo.y  = COCINA_X + CELDA * 3, COCINA_Y
    despensa_pan.x,    despensa_pan.y    = COCINA_X + CELDA * 6, COCINA_Y
    despensa_papa.x,   despensa_papa.y   = COCINA_X + CELDA * 6, COCINA_Y + CELDA * 2
    tabla.x,           tabla.y           = COCINA_X,             COCINA_Y + CELDA * 2
    cocina_est.x,      cocina_est.y      = COCINA_X,             COCINA_Y + CELDA * 4
    freidora.x,        freidora.y        = COCINA_X + CELDA * 3, COCINA_Y + COCINA_ALTO - CELDA
    ensamblaje.x,      ensamblaje.y      = COCINA_X + CELDA * 5, COCINA_Y + CELDA * 3
    entrega.x,         entrega.y         = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA

    estaciones = [despensa_tomate, despensa_pollo, despensa_pan, despensa_papa,
                  tabla, cocina_est, freidora, ensamblaje, entrega]

    # Receta simple
    tomate_c = VegetalesYFrutas("Tomate"); tomate_c.estado = "cortado"
    receta_ensalada = Receta("Ensalada", [tomate_c], 100, 25)

    # Receta 2 ingredientes: pollo + tomate cortado
    pollo_c  = Proteina("Pollo");          pollo_c.estado = "cocinado"; pollo_c.cocinada = True
    tomate_c2 = VegetalesYFrutas("Tomate"); tomate_c2.estado = "cortado"
    receta_bowl = Receta("Pollo Bowl", [pollo_c, tomate_c2], 200, 45)

    # Receta 2 ingredientes: papa frita + pollo
    papa_f   = VegetalesYFrutas("Papa");   papa_f.estado = "frito"
    pollo_c3 = Proteina("Pollo");          pollo_c3.estado = "cocinado"; pollo_c3.cocinada = True
    receta_combo = Receta("Combo", [papa_f, pollo_c3], 220, 50)

    cocina_juego = CocinaJuego("Selva", [receta_ensalada, receta_bowl, receta_combo],
                               tiempo_juego=120, intervalo_recetas=8)
    chef1, chef2 = _chefs_default()
    cocina_juego.agregar_chef(chef1)
    cocina_juego.agregar_chef(chef2)
    for est in estaciones:
        cocina_juego.agregar_estacion(est)

    return cocina_juego, estaciones, chef1, chef2


def _nivel_3():
    despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
    despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
    despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
    despensa_papa   = Despensa("Despensa Papa",    VegetalesYFrutas("Papa"))
    tabla           = TablaDeCortar()
    cocina_est      = Cocina()
    freidora        = Freidora()
    ensamblaje      = MesaEnsamblaje()
    entrega         = EstacionEntrega()

    # Layout disperso — máxima distancia entre estaciones relacionadas
    despensa_tomate.x, despensa_tomate.y = COCINA_X,             COCINA_Y
    despensa_pollo.x,  despensa_pollo.y  = COCINA_X + CELDA * 6, COCINA_Y
    despensa_pan.x,    despensa_pan.y    = COCINA_X + CELDA * 6, COCINA_Y + CELDA * 2
    despensa_papa.x,   despensa_papa.y   = COCINA_X,             COCINA_Y + CELDA * 4
    tabla.x,           tabla.y           = COCINA_X + CELDA * 3, COCINA_Y
    cocina_est.x,      cocina_est.y      = COCINA_X + CELDA * 3, COCINA_Y + COCINA_ALTO - CELDA
    freidora.x,        freidora.y        = COCINA_X,             COCINA_Y + COCINA_ALTO - CELDA
    ensamblaje.x,      ensamblaje.y      = COCINA_X + CELDA * 5, COCINA_Y + CELDA * 3
    entrega.x,         entrega.y         = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA

    estaciones = [despensa_tomate, despensa_pollo, despensa_pan, despensa_papa,
                  tabla, cocina_est, freidora, ensamblaje, entrega]

    # Receta 2 ingredientes
    pollo_c  = Proteina("Pollo");           pollo_c.estado = "cocinado"; pollo_c.cocinada = True
    tomate_c = VegetalesYFrutas("Tomate");  tomate_c.estado = "cortado"
    receta_bowl = Receta("Pollo Bowl", [pollo_c, tomate_c], 200, 35)

    # Receta 3 ingredientes: pan + pollo + tomate
    pan      = PanesYBases("Pan")
    pollo_c2 = Proteina("Pollo");           pollo_c2.estado = "cocinado"; pollo_c2.cocinada = True
    tomate_c2 = VegetalesYFrutas("Tomate"); tomate_c2.estado = "cortado"
    receta_sandwich = Receta("Sandwich", [pan, pollo_c2, tomate_c2], 300, 50)

    # Receta 3 ingredientes: papa frita + pollo + tomate
    papa_f   = VegetalesYFrutas("Papa");    papa_f.estado = "frito"
    pollo_c3 = Proteina("Pollo");           pollo_c3.estado = "cocinado"; pollo_c3.cocinada = True
    tomate_c3 = VegetalesYFrutas("Tomate"); tomate_c3.estado = "cortado"
    receta_plato = Receta("Plato Fuerte", [papa_f, pollo_c3, tomate_c3], 350, 60)

    cocina_juego = CocinaJuego("Espacio", [receta_bowl, receta_sandwich, receta_plato],
                               tiempo_juego=120, intervalo_recetas=6)
    chef1, chef2 = _chefs_default()
    cocina_juego.agregar_chef(chef1)
    cocina_juego.agregar_chef(chef2)
    for est in estaciones:
        cocina_juego.agregar_estacion(est)

    return cocina_juego, estaciones, chef1, chef2


def jugar_nivel(ventana, fuente, fuente_chica, reloj,
                cocina_juego, estaciones, chef1, chef2):

    chef_activo   = chef1
    ultimo_tiempo = time.time()
    dir_actual    = [0, 0]
    flotantes     = []

    rects_estaciones = [est.rect for est in estaciones]

    while not cocina_juego.juego_terminado():
        ahora = time.time()
        delta = min(ahora - ultimo_tiempo, 0.05)
        ultimo_tiempo = ahora

        teclas     = pygame.key.get_pressed()
        hoeleando  = teclas[pygame.K_SPACE]
        dx = int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT])
        dy = int(teclas[pygame.K_DOWN])  - int(teclas[pygame.K_UP])

        if dx != 0 or dy != 0:
            dir_actual = [dx, dy]

        # Detectar estación frente al chef activo
        rect_frente = chef_activo.rect_interaccion(*dir_actual)
        estacion_frente = None
        for est in estaciones:
            if rect_frente.colliderect(est.rect):
                estacion_frente = est
                break

        # Actualizar holdeo — solo para estaciones de proceso (tiempo_base > 0)
        fx = chef_activo.x + (CELDA - 16) // 2
        fy = chef_activo.y

        if (estacion_frente is not None
                and estacion_frente.tiempo_base > 0
                and chef_activo.ingrediente_en_mano is not None
                and not isinstance(estacion_frente, (Despensa, EstacionEntrega, MesaEnsamblaje))):

            completado = chef_activo.actualizar_holdeo(hoeleando, estacion_frente, delta)
            if completado:
                estado_antes = chef_activo.ingrediente_en_mano.estado
                if chef_activo.usar_estacion(estacion_frente):
                    estado_nuevo = chef_activo.ingrediente_en_mano.estado
                    if estado_nuevo != estado_antes:
                        agregar_flotante(flotantes, f"{estado_nuevo.capitalize()}!",
                                         fx, fy, VERDE)
                else:
                    agregar_flotante(flotantes, "No puedes", fx, fy, ROJO)
        else:
            chef_activo.actualizar_holdeo(False, None, delta)  # cancela progreso

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_TAB:
                    if chef_activo == chef1:
                        chef_activo = chef2
                        chef1.activo, chef2.activo = False, True
                    else:
                        chef_activo = chef1
                        chef1.activo, chef2.activo = True, False
                    dir_actual = [0, 0]

                # Acciones instantáneas con ESPACIO (despensa, ensamblaje, entrega)
                if evento.key == pygame.K_SPACE:
                    if estacion_frente is None:
                        pass
                    elif isinstance(estacion_frente, Despensa):
                        if chef_activo.recoger_ingrediente(estacion_frente):
                            agregar_flotante(flotantes,
                                             chef_activo.ingrediente_en_mano.nombre,
                                             fx, fy, BLANCO)
                        else:
                            agregar_flotante(flotantes, "Manos llenas", fx, fy, ROJO)

                    elif isinstance(estacion_frente, MesaEnsamblaje):
                        if chef_activo.ingrediente_en_mano is not None:
                            ing = chef_activo.soltar_ingrediente()
                            estacion_frente.depositar(ing)
                            agregar_flotante(flotantes, f"{ing.nombre} depositado",
                                             fx, fy, MORADO)
                        else:
                            # Sin ingrediente: recoge todo lo de la mesa
                            items = estacion_frente.recoger_todo()
                            if items:
                                agregar_flotante(flotantes, "Recogido", fx, fy, BLANCO)

                    elif isinstance(estacion_frente, EstacionEntrega):
                        # Intenta entregar con ingredientes de la mesa de ensamblaje
                        mesa = next((e for e in estaciones
                                     if isinstance(e, MesaEnsamblaje)), None)
                        ingredientes_a_entregar = []
                        if mesa and not mesa.esta_vacia():
                            ingredientes_a_entregar = list(mesa.ingredientes_depositados)
                        elif chef_activo.ingrediente_en_mano is not None:
                            ingredientes_a_entregar = [chef_activo.ingrediente_en_mano]

                        entregado = False
                        for orden in cocina_juego.ordenes[:]:
                            if orden.comparar_receta(ingredientes_a_entregar):
                                cocina_juego.puntos += orden.puntos_actuales
                                agregar_flotante(flotantes,
                                                 f"+{orden.puntos_actuales} pts",
                                                 fx, fy, AMARILLO)
                                cocina_juego.ordenes.remove(orden)
                                if mesa and not mesa.esta_vacia():
                                    mesa.ingredientes_depositados.clear()
                                elif chef_activo.ingrediente_en_mano is not None:
                                    chef_activo.soltar_ingrediente()
                                entregado = True
                                break
                        if not entregado:
                            agregar_flotante(flotantes, "No coincide", fx, fy, ROJO)

                # Q: soltar ingrediente
                if evento.key == pygame.K_q:
                    if chef_activo.ingrediente_en_mano is not None:
                        chef_activo.soltar_ingrediente()
                        agregar_flotante(flotantes, "Soltado", fx, fy, GRIS)

        chef_activo.mover(dx, dy, rects_estaciones,
                          COCINA_X, COCINA_Y, COCINA_ANCHO, COCINA_ALTO)

        cocina_juego.actualizar(delta)

        ventana.fill(NEGRO)
        dibujar_grid(ventana)
        dibujar_estaciones(ventana, estaciones, fuente)
        dibujar_chef(ventana, chef1, fuente, SPRITE_CHEF1, SPRITE_CHEF1_OSCURO)
        dibujar_chef(ventana, chef2, fuente, SPRITE_CHEF2, SPRITE_CHEF2_OSCURO)
        dibujar_barra_progreso(ventana, chef1, estaciones, dir_actual)
        dibujar_barra_progreso(ventana, chef2, estaciones, dir_actual)
        dibujar_hud(ventana, cocina_juego, fuente, fuente_chica)
        dibujar_flotantes(ventana, fuente_chica, flotantes, delta)

        pygame.display.flip()
        reloj.tick(60)

    return "fin"


def pantalla_fin(ventana, fuente, fuente_titulo, cocina_juego):
    ventana.fill(NEGRO)
    titulo  = fuente_titulo.render("¡Tiempo!", True, AMARILLO)
    puntos  = fuente.render(f"Puntuación final: {cocina_juego.puntos}", True, BLANCO)
    volver  = fuente.render("Volviendo al menú...", True, GRIS)
    ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 200))
    ventana.blit(puntos, (ANCHO//2 - puntos.get_width()//2, 300))
    ventana.blit(volver, (ANCHO//2 - volver.get_width()//2, 360))
    pygame.display.flip()
    time.sleep(3)


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
        resultado = jugar_nivel(ventana, fuente, fuente_chica, reloj,
                                cocina_juego, estaciones, chef1, chef2)
        if resultado == "fin":
            pantalla_fin(ventana, fuente, fuente_titulo, cocina_juego)
            estado = "menu"
        else:
            estado = "salir"

pygame.quit()
sys.exit()