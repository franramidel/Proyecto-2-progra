import pygame
from clases.ingrediente import VegetalesYFrutas, Proteina, PanesYBases
from clases.estacion import Despensa, Cocina, TablaDeCortar, Freidora, EstacionEntrega, MesaEnsamblaje
from clases.chef import Chef
from clases.receta import Receta
from clases.cocina import Cocina as CocinaJuego

CELDA        = 80
HUD_ALTO     = 40
PANEL_ANCHO  = 200
ANCHO        = 800
ALTO         = 600
COCINA_X     = 0
COCINA_Y     = HUD_ALTO
COCINA_ANCHO = ANCHO - PANEL_ANCHO
COCINA_ALTO  = ALTO - HUD_ALTO


def _chefs_default():
    cx = COCINA_X + COCINA_ANCHO // 2
    cy = COCINA_Y + COCINA_ALTO  // 2
    chef1 = Chef("Chef1", cx - CELDA, cy, velocidad=4, multiplicador_proceso=1.0)
    chef2 = Chef("Chef2", cx + CELDA, cy, velocidad=7, multiplicador_proceso=3.0)
    chef2.activo = False
    return chef1, chef2


class Nivel:
    """
    Encapsula toda la información y lógica de un nivel:
    - estaciones y su layout
    - recetas disponibles
    - asset del piso
    - configuración de tiempo e intervalos
    """

    def __init__(self, id_nivel):
        self.id_nivel = id_nivel
        self.cocina_juego = None
        self.estaciones   = []
        self.chef1        = None
        self.chef2        = None
        self.sprite_piso  = None  # se carga con cargar_assets()

        self._construir()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def cargar_assets(self, tamano_celda):
        """Carga el sprite de piso correspondiente al nivel."""
        rutas = {
            "nivel_1": "assets/water.png",
            "nivel_2": "assets/jungle.png",
            "nivel_3": "assets/floor.jpg",
        }
        ruta = rutas.get(self.id_nivel, "assets/floor.jpg")
        try:
            img = pygame.image.load(ruta).convert()
            self.sprite_piso = pygame.transform.scale(img, (tamano_celda, tamano_celda))
        except (FileNotFoundError, pygame.error):
            self.sprite_piso = None

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _construir(self):
        constructores = {
            "nivel_1": self._nivel_1,
            "nivel_2": self._nivel_2,
            "nivel_3": self._nivel_3,
        }
        constructores[self.id_nivel]()

    def _receta(self, nombre, ingredientes, tiempo):
        """Atajo para crear recetas con puntos proporcionales al tiempo."""
        puntos = tiempo * 2   # relación sencilla puntos ↔ tiempo
        return Receta(nombre, ingredientes, puntos, tiempo)

    def _ing(self, clase, nombre, estado=None, cocinada=False):
        """Crea un ingrediente con el estado requerido por la receta."""
        ing = clase(nombre)
        if estado:
            ing.estado = estado
        if cocinada and isinstance(ing, Proteina):
            ing.cocinada = True
        return ing

    # ------------------------------------------------------------------
    # Layouts de estaciones
    # ------------------------------------------------------------------

    def _estaciones_nivel1(self):
        despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
        despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
        despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
        tabla           = TablaDeCortar()
        cocina_est      = Cocina()
        freidora        = Freidora()
        ensamblaje      = MesaEnsamblaje()
        entrega         = EstacionEntrega()

        # Fila top
        despensa_tomate.x, despensa_tomate.y = COCINA_X,             COCINA_Y
        despensa_pollo.x,  despensa_pollo.y  = COCINA_X + CELDA * 2, COCINA_Y
        despensa_pan.x,    despensa_pan.y    = COCINA_X + CELDA * 4, COCINA_Y
        # Columna izquierda
        tabla.x,           tabla.y           = COCINA_X,             COCINA_Y + CELDA * 2
        cocina_est.x,      cocina_est.y      = COCINA_X,             COCINA_Y + CELDA * 4
        # Fila bottom
        freidora.x,        freidora.y        = COCINA_X + CELDA * 2, COCINA_Y + COCINA_ALTO - CELDA
        ensamblaje.x,      ensamblaje.y      = COCINA_X + CELDA * 4, COCINA_Y + COCINA_ALTO - CELDA
        entrega.x,         entrega.y         = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA

        return [despensa_tomate, despensa_pollo, despensa_pan,
                tabla, cocina_est, freidora, ensamblaje, entrega]

    def _estaciones_nivel2(self):
        despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
        despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
        despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
        despensa_papa   = Despensa("Despensa Papa",    VegetalesYFrutas("Papa"))
        tabla           = TablaDeCortar()
        cocina_est      = Cocina()
        freidora        = Freidora()
        ensamblaje      = MesaEnsamblaje()
        entrega         = EstacionEntrega()

        # Base = nivel 1. Swaps puros entre elementos distantes:
        # 1) Despensa Tomate (top col 0)    ↔ Freidora     (bottom col 2)
        # 2) Despensa Pollo  (top col 2)    ↔ Cocina       (col izq fila 4)
        # 3) Tabla           (col izq fila 2) ↔ Ensamblaje (bottom col 4)
        # 4) Despensa Pan    (top col 4)    ↔ Despensa Papa (nueva, top col 6)

        # Fila top
        freidora.x,        freidora.y        = COCINA_X,             COCINA_Y               # swap 1: era Tomate
        cocina_est.x,      cocina_est.y      = COCINA_X + CELDA * 2, COCINA_Y               # swap 2: era Pollo
        despensa_papa.x,   despensa_papa.y   = COCINA_X + CELDA * 4, COCINA_Y               # swap 4: era Pan
        despensa_pan.x,    despensa_pan.y    = COCINA_X + CELDA * 6, COCINA_Y               # swap 4: era Papa
        # Columna izquierda
        ensamblaje.x,      ensamblaje.y      = COCINA_X,             COCINA_Y + CELDA * 2   # swap 3: era Tabla
        despensa_pollo.x,  despensa_pollo.y  = COCINA_X,             COCINA_Y + CELDA * 4   # swap 2: era Cocina
        # Fila bottom
        despensa_tomate.x, despensa_tomate.y = COCINA_X + CELDA * 2, COCINA_Y + COCINA_ALTO - CELDA  # swap 1: era Freidora
        tabla.x,           tabla.y           = COCINA_X + CELDA * 4, COCINA_Y + COCINA_ALTO - CELDA  # swap 3: era Ensamblaje
        entrega.x,         entrega.y         = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA  # sin cambio

        return [despensa_tomate, despensa_pollo, despensa_pan, despensa_papa,
                tabla, cocina_est, freidora, ensamblaje, entrega]

    def _estaciones_nivel3(self):
        despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
        despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
        despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
        despensa_papa   = Despensa("Despensa Papa",    VegetalesYFrutas("Papa"))
        tabla           = TablaDeCortar()
        cocina_est      = Cocina()
        freidora        = Freidora()
        ensamblaje      = MesaEnsamblaje()
        entrega         = EstacionEntrega()

        # Base = nivel 1. Swaps aplicados (distintos a nivel 2):
        # 1) Tomate ↔ Pan          (top: columna 0 ↔ columna 4)
        # 2) Pollo ↔ Papa          (top: columna 2 ↔ columna 6, Papa es nueva)
        # 3) Tabla ↔ Ensamblaje    (tabla sube de (0,2) a bottom col 4; ensamblaje baja)
        # 4) Freidora ↔ Entrega    (bottom: columna 2 ↔ columna 6)

        # Fila top
        despensa_pan.x,    despensa_pan.y    = COCINA_X,             COCINA_Y          # swap 1: era Tomate
        despensa_pollo.x,  despensa_pollo.y  = COCINA_X + CELDA * 2, COCINA_Y          # sin cambio
        despensa_tomate.x, despensa_tomate.y = COCINA_X + CELDA * 4, COCINA_Y          # swap 1: era Pan
        despensa_papa.x,   despensa_papa.y   = COCINA_X + CELDA * 6, COCINA_Y          # swap 2: nueva pos
        # Columna izquierda / centro
        ensamblaje.x,      ensamblaje.y      = COCINA_X,             COCINA_Y + CELDA * 2  # swap 3: era Tabla
        cocina_est.x,      cocina_est.y      = COCINA_X,             COCINA_Y + CELDA * 4  # sin cambio
        # Fila bottom
        entrega.x,         entrega.y         = COCINA_X + CELDA * 2, COCINA_Y + COCINA_ALTO - CELDA  # swap 4: era Freidora
        tabla.x,           tabla.y           = COCINA_X + CELDA * 4, COCINA_Y + COCINA_ALTO - CELDA  # swap 3: era Ensamblaje
        freidora.x,        freidora.y        = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA  # swap 4: era Entrega

        return [despensa_tomate, despensa_pollo, despensa_pan, despensa_papa,
                tabla, cocina_est, freidora, ensamblaje, entrega]

    # ------------------------------------------------------------------
    # Constructores por nivel
    # ------------------------------------------------------------------

    def _nivel_1(self):
        self.estaciones = self._estaciones_nivel1()

        recetas = [
            # 1 ingrediente → 40s
            self._receta("Ensalada",
                [self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                40),
            self._receta("Pollo Asado",
                [self._ing(Proteina, "Pollo", "cocinado", cocinada=True)],
                40),
        ]

        self.cocina_juego = CocinaJuego(
            "Oceano", recetas,
            tiempo_juego=120, intervalo_recetas=20
        )
        self.chef1, self.chef2 = _chefs_default()
        self._registrar()

    def _nivel_2(self):
        self.estaciones = self._estaciones_nivel2()

        recetas = [
            # 1 ingrediente → 40s
            self._receta("Ensalada",
                [self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                40),
            self._receta("Papa Frita",
                [self._ing(VegetalesYFrutas, "Papa", "frito")],
                40),
            # 2 ingredientes → 60s
            self._receta("Pollo Bowl",
                [self._ing(Proteina, "Pollo", "cocinado", cocinada=True),
                 self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                60),
            self._receta("Combo",
                [self._ing(VegetalesYFrutas, "Papa", "frito"),
                 self._ing(Proteina, "Pollo", "cocinado", cocinada=True)],
                60),
        ]

        self.cocina_juego = CocinaJuego(
            "Selva", recetas,
            tiempo_juego=120, intervalo_recetas=20
        )
        self.chef1, self.chef2 = _chefs_default()
        self._registrar()

    def _nivel_3(self):
        self.estaciones = self._estaciones_nivel3()

        recetas = [
            # 2 ingredientes → 60s
            self._receta("Pollo Bowl",
                [self._ing(Proteina, "Pollo", "cocinado", cocinada=True),
                 self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                60),
            self._receta("Combo",
                [self._ing(VegetalesYFrutas, "Papa", "frito"),
                 self._ing(Proteina, "Pollo", "cocinado", cocinada=True)],
                60),
            # 3 ingredientes → 80s
            self._receta("Sandwich",
                [self._ing(PanesYBases, "Pan"),
                 self._ing(Proteina, "Pollo", "cocinado", cocinada=True),
                 self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                80),
            self._receta("Combo Deluxe",
                [self._ing(VegetalesYFrutas, "Papa", "frito"),
                 self._ing(Proteina, "Pollo", "cocinado", cocinada=True),
                 self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                80),
            # 4 ingredientes → 100s
            self._receta("Mega Plato",
                [self._ing(PanesYBases, "Pan"),
                 self._ing(VegetalesYFrutas, "Papa", "frito"),
                 self._ing(Proteina, "Pollo", "cocinado", cocinada=True),
                 self._ing(VegetalesYFrutas, "Tomate", "cortado")],
                100),
        ]

        self.cocina_juego = CocinaJuego(
            "Espacio", recetas,
            tiempo_juego=120, intervalo_recetas=20
        )
        self.chef1, self.chef2 = _chefs_default()
        self._registrar()

    def _registrar(self):
        """Registra chefs y estaciones en la cocina."""
        self.cocina_juego.agregar_chef(self.chef1)
        self.cocina_juego.agregar_chef(self.chef2)
        for est in self.estaciones:
            self.cocina_juego.agregar_estacion(est)