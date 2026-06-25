from clases.ingrediente import VegetalesYFrutas, Proteina, PanesYBases
from clases.estacion import (Despensa, Cocina, TablaDeCortar,
                              Freidora, EstacionEntrega, MesaEnsamblaje)
from clases.chef import Chef
from clases.receta import Receta
from clases.cocina import Cocina as CocinaJuego
 
# Constantes de layout — deben coincidir con las de main.py
CELDA       = 80
HUD_ALTO    = 40
PANEL_ANCHO = 200
ANCHO       = 800
ALTO        = 600
COCINA_X    = 0
COCINA_Y    = HUD_ALTO
COCINA_ANCHO = ANCHO - PANEL_ANCHO
COCINA_ALTO  = ALTO - HUD_ALTO
 
 
class Nivel:
    """
    Encapsula toda la información y construcción de un escenario de juego.
 
    Atributos:
        id         (str)       : identificador único, ej "nivel_1"
        nombre     (str)       : nombre del escenario, ej "Oceano"
        disponible (bool)      : si el nivel puede seleccionarse en el menú
        cocina     (CocinaJuego): instancia del juego ya configurada
        estaciones (list)      : lista de estaciones posicionadas
        chef1      (Chef)      : primer chef (activo por defecto)
        chef2      (Chef)      : segundo chef
 
    Uso:
        nivel = Nivel.desde_id("nivel_1")
        cocina, estaciones, chef1, chef2 = nivel.construir()
    """
 
    # Catálogo de niveles disponibles — agregar aquí nuevos niveles
    CATALOGO = [
        {"id": "nivel_1", "nombre": "Nivel 1 - Oceano",  "disponible": True},
        {"id": "nivel_2", "nombre": "Nivel 2 - Selva",   "disponible": True},
        {"id": "nivel_3", "nombre": "Nivel 3 - Espacio", "disponible": True},
    ]
 
    def __init__(self, id_nivel, nombre, disponible=True):
        self.id         = id_nivel
        self.nombre     = nombre
        self.disponible = disponible
 
        # Se rellenan al llamar construir()
        self.cocina     = None
        self.estaciones = []
        self.chef1      = None
        self.chef2      = None
 
    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
 
    @classmethod
    def desde_id(cls, id_nivel):
        """Devuelve la instancia de Nivel correspondiente al id dado."""
        constructores = {
            "nivel_1": cls._nivel_1,
            "nivel_2": cls._nivel_2,
            "nivel_3": cls._nivel_3,
        }
        if id_nivel not in constructores:
            raise ValueError(f"Nivel desconocido: {id_nivel}")
        return constructores[id_nivel]()
 
    def construir(self):
        """Devuelve (cocina, estaciones, chef1, chef2) listos para jugar."""
        return self.cocina, self.estaciones, self.chef1, self.chef2
 
    def __str__(self):
        return f"Nivel({self.id}, '{self.nombre}', disponible={self.disponible})"
 
    # ------------------------------------------------------------------
    # Helpers privados compartidos
    # ------------------------------------------------------------------
 
    @staticmethod
    def _chefs_default():
        cx = COCINA_X + COCINA_ANCHO // 2
        cy = COCINA_Y + COCINA_ALTO  // 2
        chef1 = Chef("Chef1", cx - CELDA, cy, velocidad=4, multiplicador_proceso=1.0)
        chef2 = Chef("Chef2", cx + CELDA, cy, velocidad=7, multiplicador_proceso=3.0)
        chef2.activo = False
        return chef1, chef2
 
    def _registrar(self, cocina_juego, estaciones, chef1, chef2):
        """Guarda las referencias y registra chefs y estaciones en la cocina."""
        self.cocina     = cocina_juego
        self.estaciones = estaciones
        self.chef1      = chef1
        self.chef2      = chef2
        cocina_juego.agregar_chef(chef1)
        cocina_juego.agregar_chef(chef2)
        for est in estaciones:
            cocina_juego.agregar_estacion(est)
 
    # ------------------------------------------------------------------
    # Constructores de cada nivel
    # ------------------------------------------------------------------
 
    @classmethod
    def _nivel_1(cls):
        nivel = cls("nivel_1", "Nivel 1 - Oceano")
 
        # Estaciones
        despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
        despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
        despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
        despensa_papa   = Despensa("Despensa Papa",    VegetalesYFrutas("Papa"))
        tabla           = TablaDeCortar()
        cocina_est      = Cocina()
        freidora        = Freidora()
        ensamblaje      = MesaEnsamblaje()
        entrega         = EstacionEntrega()
 
        # Posiciones — fila superior: despensas | media: procesado | inferior: ensamblaje y entrega
        despensa_tomate.x, despensa_tomate.y = COCINA_X,             COCINA_Y
        despensa_pollo.x,  despensa_pollo.y  = COCINA_X + CELDA * 2, COCINA_Y
        despensa_pan.x,    despensa_pan.y    = COCINA_X + CELDA * 4, COCINA_Y
        despensa_papa.x,   despensa_papa.y   = COCINA_X + CELDA * 6, COCINA_Y
        tabla.x,           tabla.y           = COCINA_X,             COCINA_Y + CELDA * 2
        cocina_est.x,      cocina_est.y      = COCINA_X,             COCINA_Y + CELDA * 4
        freidora.x,        freidora.y        = COCINA_X + CELDA * 2, COCINA_Y + CELDA * 2
        ensamblaje.x,      ensamblaje.y      = COCINA_X + CELDA * 4, COCINA_Y + COCINA_ALTO - CELDA
        entrega.x,         entrega.y         = COCINA_X + CELDA * 6, COCINA_Y + COCINA_ALTO - CELDA
 
        estaciones = [despensa_tomate, despensa_pollo, despensa_pan, despensa_papa,
                      tabla, cocina_est, freidora, ensamblaje, entrega]
 
        # Recetas — dificultad creciente dentro del nivel
        tomate_c = VegetalesYFrutas("Tomate"); tomate_c.estado = "cortado"
        receta_ensalada = Receta("Ensalada", [tomate_c], 100, 35)
 
        papa_f = VegetalesYFrutas("Papa"); papa_f.estado = "frito"
        receta_papas = Receta("Papas Fritas", [papa_f], 120, 35)
 
        pan_r   = PanesYBases("Pan")
        pollo_c = Proteina("Pollo"); pollo_c.estado = "cocinado"; pollo_c.cocinada = True
        receta_sandwich = Receta("Sandwich", [pan_r, pollo_c], 200, 50)
 
        cocina_juego = CocinaJuego("Oceano",
                                   [receta_ensalada, receta_papas, receta_sandwich],
                                   tiempo_juego=120, intervalo_recetas=10)
 
        chef1, chef2 = cls._chefs_default()
        nivel._registrar(cocina_juego, estaciones, chef1, chef2)
        return nivel
 
    @classmethod
    def _nivel_2(cls):
        nivel = cls("nivel_2", "Nivel 2 - Selva")
 
        despensa_tomate = Despensa("Despensa Tomate", VegetalesYFrutas("Tomate"))
        despensa_pollo  = Despensa("Despensa Pollo",  Proteina("Pollo"))
        despensa_pan    = Despensa("Despensa Pan",     PanesYBases("Pan"))
        despensa_papa   = Despensa("Despensa Papa",    VegetalesYFrutas("Papa"))
        tabla           = TablaDeCortar()
        cocina_est      = Cocina()
        freidora        = Freidora()
        ensamblaje      = MesaEnsamblaje()
        entrega         = EstacionEntrega()
 
        # Layout en U — estaciones más separadas que nivel 1
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
 
        tomate_c = VegetalesYFrutas("Tomate"); tomate_c.estado = "cortado"
        receta_ensalada = Receta("Ensalada", [tomate_c], 100, 25)
 
        pollo_c   = Proteina("Pollo");           pollo_c.estado = "cocinado"; pollo_c.cocinada = True
        tomate_c2 = VegetalesYFrutas("Tomate");  tomate_c2.estado = "cortado"
        receta_bowl = Receta("Pollo Bowl", [pollo_c, tomate_c2], 200, 45)
 
        papa_f   = VegetalesYFrutas("Papa");  papa_f.estado = "frito"
        pollo_c2 = Proteina("Pollo");         pollo_c2.estado = "cocinado"; pollo_c2.cocinada = True
        receta_combo = Receta("Combo", [papa_f, pollo_c2], 220, 50)
 
        pan_r    = PanesYBases("Pan")
        pollo_c3 = Proteina("Pollo"); pollo_c3.estado = "cocinado"; pollo_c3.cocinada = True
        receta_sandwich = Receta("Sandwich", [pan_r, pollo_c3], 200, 45)
 
        cocina_juego = CocinaJuego("Selva",
                                   [receta_ensalada, receta_bowl,
                                    receta_combo, receta_sandwich],
                                   tiempo_juego=120, intervalo_recetas=8)
 
        chef1, chef2 = cls._chefs_default()
        nivel._registrar(cocina_juego, estaciones, chef1, chef2)
        return nivel
 
    @classmethod
    def _nivel_3(cls):
        nivel = cls("nivel_3", "Nivel 3 - Espacio")
 
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
 
        pollo_c  = Proteina("Pollo");          pollo_c.estado = "cocinado"; pollo_c.cocinada = True
        tomate_c = VegetalesYFrutas("Tomate"); tomate_c.estado = "cortado"
        receta_bowl = Receta("Pollo Bowl", [pollo_c, tomate_c], 200, 35)
 
        pan_r     = PanesYBases("Pan")
        pollo_c2  = Proteina("Pollo");          pollo_c2.estado = "cocinado"; pollo_c2.cocinada = True
        tomate_c2 = VegetalesYFrutas("Tomate"); tomate_c2.estado = "cortado"
        receta_sandwich = Receta("Sandwich", [pan_r, pollo_c2, tomate_c2], 300, 50)
 
        papa_f    = VegetalesYFrutas("Papa");   papa_f.estado = "frito"
        pollo_c3  = Proteina("Pollo");          pollo_c3.estado = "cocinado"; pollo_c3.cocinada = True
        tomate_c3 = VegetalesYFrutas("Tomate"); tomate_c3.estado = "cortado"
        receta_plato = Receta("Plato Fuerte", [papa_f, pollo_c3, tomate_c3], 350, 55)
 
        pan_r2    = PanesYBases("Pan")
        pollo_c4  = Proteina("Pollo");          pollo_c4.estado = "cocinado"; pollo_c4.cocinada = True
        tomate_c4 = VegetalesYFrutas("Tomate"); tomate_c4.estado = "cortado"
        papa_f2   = VegetalesYFrutas("Papa");   papa_f2.estado = "frito"
        receta_suprema = Receta("Suprema", [pan_r2, pollo_c4, tomate_c4, papa_f2], 450, 70)
 
        cocina_juego = CocinaJuego("Espacio",
                                   [receta_bowl, receta_sandwich,
                                    receta_plato, receta_suprema],
                                   tiempo_juego=120, intervalo_recetas=6)
 
        chef1, chef2 = cls._chefs_default()
        nivel._registrar(cocina_juego, estaciones, chef1, chef2)
        return nivel