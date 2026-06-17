import random
import time

class Cocina:
    def __init__(self, nombre, recetas_posibles, tiempo_juego, intervalo_recetas):
        self.nombre = nombre  # nombre del escenario
        self.recetas_posibles = recetas_posibles  # recetas que pueden aparecer
        self.tiempo_juego = tiempo_juego  # duracion total de la partida en segundos
        self.tiempo_restante = tiempo_juego
        self.intervalo_recetas = intervalo_recetas  # cada cuantos segundos aparece una receta nueva
        self.tiempo_ultima_receta = time.time()  # momento en que aparecio la ultima receta, time.time() devuelve tiempo actual
        self.chefs = []  # lista de chefs en la cocina
        self.estaciones = []  # lista de estaciones en la cocina
        self.ordenes = []  # recetas activas que hay que completar
        self.puntos = 0  # puntaje total del jugador

    def agregar_chef(self, chef):
        self.chefs.append(chef)

    def agregar_estacion(self, estacion):
        self.estaciones.append(estacion)

    def generar_receta(self):
        # elige una receta al azar de las posibles y la agrega a las ordenes
        receta = random.choice(self.recetas_posibles)
        self.ordenes.append(receta)
        print(f"nueva orden: {receta.nombre}")

    def actualizar(self, delta):
        # descuenta el tiempo restante de la partida
        self.tiempo_restante -= delta #delta es el tiempo q paso desde el ultimo frame

        # genera una nueva receta si paso el intervalo
        ahora = time.time()
        if ahora - self.tiempo_ultima_receta >= self.intervalo_recetas:
            self.generar_receta()
            self.tiempo_ultima_receta = ahora

        # actualiza el tiempo de cada orden activa
        for orden in self.ordenes:
            orden.actualizar_tiempo(delta)

        # elimina ordenes expiradas y descuenta puntos
        for orden in self.ordenes[:]:  # [:] para no modificar la lista mientras la recorremos
            if not orden.activa:
                self.puntos -= orden.puntos_base  # descuenta el valor original
                if self.puntos < 0:
                    self.puntos = 0  # el puntaje minimo es cero
                self.ordenes.remove(orden)

    def entregar_orden(self, chef, receta, estacion_entrega):
        if chef.entregar_receta(estacion_entrega, receta):
            self.puntos += receta.puntos_actuales  # suma los puntos actuales
            self.ordenes.remove(receta)  # elimina la orden completada
            return True
        return False

    def juego_terminado(self):
        return self.tiempo_restante <= 0

    def __str__(self):
        return f"{self.nombre} | puntos: {self.puntos} | tiempo: {self.tiempo_restante:.1f}s | ordenes activas: {len(self.ordenes)}"