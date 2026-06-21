import random
import time


class Cocina:
    def __init__(self, nombre, recetas_posibles, tiempo_juego, intervalo_recetas):
        self.nombre = nombre               # nombre del escenario
        self.recetas_posibles = recetas_posibles  # recetas que pueden aparecer
        self.tiempo_juego = tiempo_juego   # duración total en segundos
        self.tiempo_restante = tiempo_juego
        self.intervalo_recetas = intervalo_recetas  # segundos entre cada nueva receta
        self.tiempo_ultima_receta = 0.0    # CORRECCIÓN: antes usaba time.time() aquí,
                                           # lo que provocaba que la primera receta tardara
                                           # un intervalo completo en aparecer. Ahora empieza
                                           # en 0 para que aparezca casi de inmediato.
        self.chefs = []
        self.estaciones = []
        self.ordenes = []   # recetas activas en este momento
        self.puntos = 0     # puntaje total del jugador

    def agregar_chef(self, chef):
        self.chefs.append(chef)

    def agregar_estacion(self, estacion):
        self.estaciones.append(estacion)

    def generar_receta(self):
        """
        Elige una receta al azar de las posibles y crea una COPIA nueva.
        CORRECCIÓN IMPORTANTE: antes se agregaba la misma instancia de Receta
        a las órdenes, lo que significa que si la misma receta se generaba dos
        veces, ambas órdenes compartían el mismo objeto (mismo tiempo, mismos puntos).
        Ahora se crea una instancia nueva cada vez con los mismos parámetros.
        """
        plantilla = random.choice(self.recetas_posibles)
        # Importación local para evitar ciclos de importación
        from clases.receta import Receta
        nueva = Receta(
            plantilla.nombre,
            list(plantilla.ingredientes),  # copia superficial de la lista de ingredientes
            plantilla.puntos_base,
            plantilla.tiempo_maximo
        )
        self.ordenes.append(nueva)
        print(f"Nueva orden: {nueva.nombre}")
        return nueva

    def actualizar(self, delta):
        """Llamar una vez por frame con el tiempo transcurrido desde el último frame."""
        # 1. Descontar tiempo de la partida
        self.tiempo_restante -= delta

        # 2. Generar receta si pasó el intervalo
        # CORRECCIÓN: se acumula tiempo propio en vez de comparar con time.time(),
        # para ser consistente con el sistema de delta del resto del juego.
        self.tiempo_ultima_receta += delta
        if self.tiempo_ultima_receta >= self.intervalo_recetas:
            self.generar_receta()
            self.tiempo_ultima_receta = 0.0  # reinicia el contador del intervalo

        # 3. Actualizar tiempo de cada orden activa
        for orden in self.ordenes:
            orden.actualizar_tiempo(delta)

        # 4. Eliminar órdenes expiradas y descontar puntos
        # Se itera sobre una copia [:] para poder modificar la lista original
        for orden in self.ordenes[:]:
            if not orden.activa:
                self.puntos -= orden.puntos_base  # descuenta el valor ORIGINAL
                if self.puntos < 0:
                    self.puntos = 0  # el puntaje mínimo es cero
                self.ordenes.remove(orden)
                print(f"Orden expirada: {orden.nombre} (-{orden.puntos_base} puntos)")

    def entregar_orden(self, chef, receta, estacion_entrega):
        """
        El chef entrega los ingredientes que tiene en mano a la estación de entrega.
        CORRECCIÓN: la lógica de comparación antes dependía de ingredientes_recolectados
        (lista eliminada del Chef). Ahora la entrega funciona con un solo ingrediente
        en mano por chef. Para recetas con varios ingredientes, ambos chefs deben
        coordinar sus entregas — esto es parte de la jugabilidad cooperativa del enunciado.
        Por simplicidad en esta base, se acepta que la entrega valide con lo que el
        chef activo tiene en mano en ese momento.
        """
        ingredientes_entregados = []
        if chef.ingrediente_en_mano is not None:
            ingredientes_entregados.append(chef.ingrediente_en_mano)

        if estacion_entrega.entregar(receta, ingredientes_entregados):
            self.puntos += receta.puntos_actuales
            chef.soltar_ingrediente()  # vacía la mano del chef
            self.ordenes.remove(receta)
            print(f"Receta entregada: {receta.nombre} (+{receta.puntos_actuales} puntos)")
            return True
        return False

    def juego_terminado(self):
        return self.tiempo_restante <= 0

    def __str__(self):
        return (f"{self.nombre} | "
                f"Puntos: {self.puntos} | "
                f"Tiempo: {self.tiempo_restante:.1f}s | "
                f"Órdenes activas: {len(self.ordenes)}")