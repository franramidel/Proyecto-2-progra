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

# tamaño de cada celda del grid
CELDA = 80

def dibujar_grid(ventana): #grid es una cuadricula
    # dibuja las lineas del grid en la cocina
    for x in range(0, ANCHO, CELDA):
        pygame.draw.line(ventana, GRIS, (x, 0), (x, ALTO))
    for y in range(0, ALTO, CELDA):
        pygame.draw.line(ventana, GRIS, (0, y), (ANCHO, y))

def dibujar_hud(ventana, cocina, fuente):
    # muestra el puntaje y el tiempo restante arriba
    texto_puntos = fuente.render(f"Puntos: {cocina.puntos}", True, BLANCO) #fuente.render hacer el texto en una superficie dibujable
    texto_tiempo = fuente.render(f"Tiempo: {cocina.tiempo_restante:.1f}s", True, BLANCO)
    ventana.blit(texto_puntos, (10, 10)) #blit dibuja la superficie en una posicion indicada
    ventana.blit(texto_tiempo, (ANCHO - 200, 10))

def dibujar_chef(ventana, chef):
    # dibuja el chef como un rectangulo
    color = VERDE if chef.activo else AZUL
    pygame.draw.rect(ventana, color, (chef.x, chef.y, CELDA - 10, CELDA - 10))
    texto = fuente.render(chef.nombre[0], True, NEGRO)  # primera letra del nombre
    ventana.blit(texto, (chef.x + 25, chef.y + 25))

def dibujar_estaciones(ventana, estaciones, fuente):
    for estacion in estaciones:
        pygame.draw.rect(ventana, AMARILLO, (estacion.x, estacion.y, CELDA - 5, CELDA - 5))
        texto = fuente.render(estacion.nombre[0], True, NEGRO)  # primera letra
        ventana.blit(texto, (estacion.x + 25, estacion.y + 25))

# agregar x e y a la clase estacion en estacion.py
# por ahora las posicionamos directamente aqui

# crear ingredientes base
tomate = VegetalesYFrutas("Tomate")
pollo = Proteina("Pollo")
pan = PanesYBases("Pan")

# crear estaciones con posicion en el grid
despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
despensa_pollo = Despensa("Despensa Pollo", Proteina("Pollo"))
despensa_pan = Despensa("Despensa Pan", PanesYBases("Pan"))
tabla = TablaDeCortar()
cocina_est = Cocina()
freidora = Freidora()
entrega = EstacionEntrega()

# posiciones en el grid (x, y)
despensa_tomate.x, despensa_tomate.y = 0, 0
despensa_pollo.x, despensa_pollo.y = 80, 0
despensa_pan.x, despensa_pan.y = 160, 0
tabla.x, tabla.y = 0, 80
cocina_est.x, cocina_est.y = 80, 80
freidora.x, freidora.y = 160, 80
entrega.x, entrega.y = 240, 80

estaciones = [despensa_tomate, despensa_pollo, despensa_pan,
              tabla, cocina_est, freidora, entrega]

# crear receta de prueba
receta_prueba = Receta("Ensalada", [VegetalesYFrutas("Tomate")], 100, 30)

# crear cocina del juego
cocina_juego = CocinaJuego("Oceano", [receta_prueba], 120, 10)

# crear chefs
chef1 = Chef("Chef1", 320, 240)
chef2 = Chef("Chef2", 400, 240)
chef2.activo = False
chef_activo = chef1

cocina_juego.agregar_chef(chef1)
cocina_juego.agregar_chef(chef2)
for est in estaciones:
    cocina_juego.agregar_estacion(est)  


# loop principal
ultimo_tiempo = time.time()

while not cocina_juego.juego_terminado():
    # calcular delta (tiempo entre frames)
    ahora = time.time()
    delta = ahora - ultimo_tiempo
    ultimo_tiempo = ahora

    # eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            # cambiar entre chefs con la tecla tab
            if evento.key == pygame.K_TAB:
                if chef_activo == chef1:
                    chef_activo = chef2
                    chef1.activo = False
                    chef2.activo = True
                else:
                    chef_activo = chef1
                    chef1.activo = True
                    chef2.activo = False

    # movimiento del chef activo
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

    # actualizar cocina
    cocina_juego.actualizar(delta)

    # dibujar
    ventana.fill(NEGRO)
    dibujar_grid(ventana)
    dibujar_estaciones(ventana, estaciones, fuente)
    dibujar_chef(ventana, chef1)
    dibujar_chef(ventana, chef2)
    dibujar_hud(ventana, cocina_juego, fuente)

    pygame.display.flip()
    reloj.tick(60)

# pantalla de fin de juego
ventana.fill(NEGRO)
texto_fin = fuente.render(f"Juego terminado! Puntos: {cocina_juego.puntos}", True, BLANCO)
ventana.blit(texto_fin, (ANCHO//2 - 150, ALTO//2))
pygame.display.flip()
time.sleep(3)
pygame.quit()
sys.exit()          