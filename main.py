import pygame
import sys #para cerrar el programa limpiamente
import time
from clases.ingrediente import VegetalesYFrutas, Proteina, PanesYBases
from clases.estacion import Despensa, Cocina, TablaDeCortar, Freidora, EstacionEntrega
from clases.chef import Chef
from clases.receta import Receta
from clases.cocina import Cocina as CocinaJuego #otro nombre para q no choque con el nombre de la clase Cocina
 
# colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
GRIS = (150, 150, 150)
AMARILLO = (255, 255, 0)
 
# tamaño de la ventana
ANCHO = 800
ALTO = 600
 
# inicializar pygame
pygame.init() #arranca todos los modulos de pygame
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Crazy Snack Rush TEC")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 20)
fuente_titulo = pygame.font.SysFont("arial", 48)  # fuente mas grande para titulos de menus
 
# tamaño de cada celda del grid
CELDA = 80
 
 
# ============================================================
# SECCION DE SPRITES
# ============================================================
# cargar_sprite intenta cargar una imagen. Si no existe todavia
# (porque el pixel art no esta listo), devuelve None y el juego
# sigue dibujando rectangulos de color como fallback, sin crashear.
def cargar_sprite(ruta, tamano=None):
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        if tamano:
            imagen = pygame.transform.scale(imagen, tamano)
        return imagen
    except (FileNotFoundError, pygame.error):
        return None
 
# Genera una copia mas oscura de un sprite (para el chef inactivo).
# factor entre 0.0 (negro total) y 1.0 (igual de claro que el original).
# BLEND_RGB_MULT multiplica solo el color, no toca el canal alpha,
# asi que los bordes transparentes del pixel art se mantienen intactos.
def oscurecer_sprite(sprite, factor=0.45):
    if sprite is None:
        return None
    oscuro = sprite.copy()
    nivel = int(255 * factor)
    oscuro.fill((nivel, nivel, nivel, 255), special_flags=pygame.BLEND_RGB_MULT)
    return oscuro
 
# Aqui se cargan los sprites una sola vez al inicio (NUNCA dentro
# del while, cargar imagenes cada frame es muy lento).
# Cambien las rutas cuando tengan los archivos. Sugerencia de carpeta: assets/
SPRITE_PISO = cargar_sprite("assets/floor.png", (CELDA, CELDA))
 
SPRITES_ESTACIONES = {
    "Despensa Tomate": cargar_sprite("assets/despensa_tomate.png", (CELDA - 5, CELDA - 5)),
    "Despensa Pollo":  cargar_sprite("assets/despensa_pollo.png", (CELDA - 5, CELDA - 5)),
    "Despensa Pan":    cargar_sprite("assets/despensa_pan.png", (CELDA - 5, CELDA - 5)),
    "Tabla de Cortar": cargar_sprite("assets/tabla.png", (CELDA - 5, CELDA - 5)),
    "Cocina":          cargar_sprite("assets/estufa.png", (CELDA - 5, CELDA - 5)),
    "Freidora":        cargar_sprite("assets/freidora.png", (CELDA - 5, CELDA - 5)),
    "Entrega":         cargar_sprite("assets/entrega.png", (CELDA - 5, CELDA - 5)),
}
# nota: las claves del diccionario deben coincidir EXACTO con estacion.nombre
# si el nombre real en su clase Estacion es distinto, solo ajusten las claves aqui
 
SPRITE_CHEF1 = cargar_sprite("assets/chef.png", (CELDA - 10, CELDA - 10))
SPRITE_CHEF2 = cargar_sprite("assets/chef.png", (CELDA - 10, CELDA - 10))
 
# version oscura de cada chef, para cuando NO esta activo (no se esta controlando)
SPRITE_CHEF1_OSCURO = oscurecer_sprite(SPRITE_CHEF1)
SPRITE_CHEF2_OSCURO = oscurecer_sprite(SPRITE_CHEF2)
 
 
# ============================================================
# FUNCIONES DE DIBUJO (usan sprite si existe, si no dibujan rectangulo)
# ============================================================
def dibujar_grid(ventana):
    if SPRITE_PISO:
        for x in range(0, ANCHO, CELDA):
            for y in range(0, ALTO, CELDA):
                ventana.blit(SPRITE_PISO, (x, y))
    else:
        for x in range(0, ANCHO, CELDA):
            pygame.draw.line(ventana, GRIS, (x, 0), (x, ALTO))
        for y in range(0, ALTO, CELDA):
            pygame.draw.line(ventana, GRIS, (0, y), (ANCHO, y))
 
def dibujar_hud(ventana, cocina, fuente):
    texto_puntos = fuente.render(f"Puntos: {cocina.puntos}", True, BLANCO)
    texto_tiempo = fuente.render(f"Tiempo: {cocina.tiempo_restante:.1f}s", True, BLANCO)
    ventana.blit(texto_puntos, (10, 10))
    ventana.blit(texto_tiempo, (ANCHO - 200, 10))
 
def dibujar_chef(ventana, chef, sprite_normal=None, sprite_oscuro=None):
    sprite = sprite_normal if chef.activo else sprite_oscuro
    if sprite:
        ventana.blit(sprite, (chef.x, chef.y))
    else:
        color = VERDE if chef.activo else AZUL
        pygame.draw.rect(ventana, color, (chef.x, chef.y, CELDA - 10, CELDA - 10))
        texto = fuente.render(chef.nombre[0], True, NEGRO)
        ventana.blit(texto, (chef.x + 25, chef.y + 25))
 
def dibujar_estaciones(ventana, estaciones, fuente):
    for estacion in estaciones:
        sprite = SPRITES_ESTACIONES.get(estacion.nombre)
        if sprite:
            ventana.blit(sprite, (estacion.x, estacion.y))
        else:
            pygame.draw.rect(ventana, AMARILLO, (estacion.x, estacion.y, CELDA - 5, CELDA - 5))
            texto = fuente.render(estacion.nombre[0], True, NEGRO)
            ventana.blit(texto, (estacion.x + 25, estacion.y + 25))
 
 
# ============================================================
# BOTON REUTILIZABLE (para menu y seleccion de niveles)
# ============================================================
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color_normal=GRIS, color_hover=AMARILLO):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_normal = color_normal
        self.color_hover = color_hover
 
    def dibujar(self, ventana, fuente):
        mouse_pos = pygame.mouse.get_pos()
        color = self.color_hover if self.rect.collidepoint(mouse_pos) else self.color_normal
        pygame.draw.rect(ventana, color, self.rect)
        pygame.draw.rect(ventana, NEGRO, self.rect, 2)  # borde
        texto_render = fuente.render(self.texto, True, NEGRO)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        ventana.blit(texto_render, texto_rect)
 
    def fue_clickeado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)
 
 
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
# PANTALLA DE SELECCION DE NIVELES (basica)
# ============================================================
def pantalla_seleccion_niveles(ventana, fuente, fuente_titulo, reloj):
    # por ahora solo "Nivel 1" esta jugable, los otros son placeholder
    # para cuando agreguen mas niveles solo hay que crear su crear_nivel()
    niveles = [
        {"nombre": "Nivel 1 - Oceano", "id": "nivel_1", "disponible": True},
        {"nombre": "Nivel 2 (pronto)", "id": "nivel_2", "disponible": False},
        {"nombre": "Nivel 3 (pronto)", "id": "nivel_3", "disponible": False},
    ]
 
    botones = []
    for i, nivel in enumerate(niveles):
        color = GRIS if nivel["disponible"] else (80, 80, 80)
        boton = Boton(ANCHO // 2 - 150, 160 + i * 100, 300, 70, nivel["nombre"], color_normal=color)
        botones.append(boton)
 
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
# CREACION DE NIVEL
# ============================================================
# Todo lo que antes estaba "suelto" antes del while ahora vive aqui.
# Recibe el id del nivel para que en el futuro cada nivel pueda tener
# su propia receta, tiempo, distribucion de estaciones, etc.
def crear_nivel(id_nivel):
    despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
    despensa_pollo = Despensa("Despensa Pollo", Proteina("Pollo"))
    despensa_pan = Despensa("Despensa Pan", PanesYBases("Pan"))
    tabla = TablaDeCortar()
    cocina_est = Cocina()
    freidora = Freidora()
    entrega = EstacionEntrega()
 
    despensa_tomate.x, despensa_tomate.y = 0, 0
    despensa_pollo.x, despensa_pollo.y = 80, 0
    despensa_pan.x, despensa_pan.y = 160, 0
    tabla.x, tabla.y = 0, 80
    cocina_est.x, cocina_est.y = 80, 80
    freidora.x, freidora.y = 160, 80
    entrega.x, entrega.y = 240, 80
 
    estaciones = [despensa_tomate, despensa_pollo, despensa_pan,
                  tabla, cocina_est, freidora, entrega]
 
    receta_prueba = Receta("Ensalada", [VegetalesYFrutas("Tomate")], 100, 30)
    cocina_juego = CocinaJuego("Oceano", [receta_prueba], 120, 10)
 
    chef1 = Chef("Chef1", 320, 240)
    chef2 = Chef("Chef2", 400, 240)
    chef2.activo = False
 
    cocina_juego.agregar_chef(chef1)
    cocina_juego.agregar_chef(chef2)
    for est in estaciones:
        cocina_juego.agregar_estacion(est)
 
    return cocina_juego, estaciones, chef1, chef2
 
 
# ============================================================
# LOOP DE JUEGO (el while original, ahora dentro de una funcion)
# ============================================================
def jugar_nivel(ventana, fuente, reloj, cocina_juego, estaciones, chef1, chef2):
    chef_activo = chef1
    ultimo_tiempo = time.time()
 
    while not cocina_juego.juego_terminado():
        ahora = time.time()
        delta = ahora - ultimo_tiempo
        ultimo_tiempo = ahora
 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_TAB:
                    if chef_activo == chef1:
                        chef_activo = chef2
                        chef1.activo = False
                        chef2.activo = True
                    else:
                        chef_activo = chef1
                        chef1.activo = True
                        chef2.activo = False
 
        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0
        if teclas[pygame.K_LEFT]:
            dx = -1
        if teclas[pygame.K_RIGHT]:
            dx = 1
        if teclas[pygame.K_UP]:
            dy = -1
        if teclas[pygame.K_DOWN]:
            dy = 1
        chef_activo.mover(dx, dy)
 
        cocina_juego.actualizar(delta)
 
        ventana.fill(NEGRO)
        dibujar_grid(ventana)
        dibujar_estaciones(ventana, estaciones, fuente)
        dibujar_chef(ventana, chef1, SPRITE_CHEF1, SPRITE_CHEF1_OSCURO)
        dibujar_chef(ventana, chef2, SPRITE_CHEF2, SPRITE_CHEF2_OSCURO)
        dibujar_hud(ventana, cocina_juego, fuente)
 
        pygame.display.flip()
        reloj.tick(60)
 
    return "fin"
 
 
def pantalla_fin(ventana, fuente, cocina_juego):
    ventana.fill(NEGRO)
    texto_fin = fuente.render(f"Juego terminado! Puntos: {cocina_juego.puntos}", True, BLANCO)
    ventana.blit(texto_fin, (ANCHO // 2 - 150, ALTO // 2))
    pygame.display.flip()
    time.sleep(3)
 
 
# ============================================================
# MAQUINA DE ESTADOS PRINCIPAL
# ============================================================
estado = "menu"
cocina_juego = None
estaciones = None
chef1 = None
chef2 = None
 
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
            # resultado es el id del nivel elegido, ej "nivel_1"
            cocina_juego, estaciones, chef1, chef2 = crear_nivel(resultado)
            estado = "jugando"
 
    elif estado == "jugando":
        resultado = jugar_nivel(ventana, fuente, reloj, cocina_juego, estaciones, chef1, chef2)
        if resultado == "fin":
            pantalla_fin(ventana, fuente, cocina_juego)
            estado = "menu"
        else:
            estado = "salir"
 
pygame.quit()
sys.exit()