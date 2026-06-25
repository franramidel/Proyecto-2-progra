import random


class Cocina:
    def __init__(self, nombre, recetas_posibles, tiempo_juego, intervalo_recetas):
        self._nombre             = nombre
        self._recetas_posibles   = recetas_posibles
        self._tiempo_juego       = tiempo_juego
        self._tiempo_restante    = tiempo_juego
        self._intervalo_recetas  = intervalo_recetas
        self._tiempo_ultima_receta = 0.0
        self._chefs              = []
        self._estaciones         = []
        self._ordenes            = []
        self._puntos             = 0

    # ── Propiedades de solo lectura / controladas ────────────────────
    @property
    def nombre(self):
        return self._nombre

    @property
    def tiempo_restante(self):
        return self._tiempo_restante

    @property
    def ordenes(self):
        return self._ordenes

    @property
    def chefs(self):
        return self._chefs

    @property
    def estaciones(self):
        return self._estaciones

    @property
    def puntos(self):
        return self._puntos

    @puntos.setter
    def puntos(self, valor):
        """El puntaje nunca puede bajar de cero."""
        self._puntos = max(0, valor)

    # ── API pública ──────────────────────────────────────────────────
    def agregar_chef(self, chef):
        self._chefs.append(chef)

    def agregar_estacion(self, estacion):
        self._estaciones.append(estacion)

    def sumar_puntos(self, cantidad):
        """Suma puntos de forma controlada."""
        self._puntos += cantidad

    def restar_puntos(self, cantidad):
        """Resta puntos sin bajar de cero."""
        self._puntos = max(0, self._puntos - cantidad)

    def generar_receta(self):
        """
        Elige una receta al azar de las posibles y crea una copia nueva
        para que cada orden sea una instancia independiente.
        """
        plantilla = random.choice(self._recetas_posibles)
        from clases.receta import Receta
        nueva = Receta(
            plantilla.nombre,
            list(plantilla.ingredientes),
            plantilla.puntos_base,
            plantilla.tiempo_maximo
        )
        self._ordenes.append(nueva)
        print(f"Nueva orden: {nueva.nombre}")
        return nueva

    def actualizar(self, delta):
        """Llamar una vez por frame con el delta time."""
        self._tiempo_restante -= delta

        self._tiempo_ultima_receta += delta
        if self._tiempo_ultima_receta >= self._intervalo_recetas:
            self.generar_receta()
            self._tiempo_ultima_receta = 0.0

        for orden in self._ordenes:
            orden.actualizar_tiempo(delta)

        for orden in self._ordenes[:]:
            if not orden.activa:
                self.restar_puntos(orden.puntos_base)
                self._ordenes.remove(orden)
                print(f"Orden expirada: {orden.nombre} (-{orden.puntos_base} puntos)")

    def entregar_orden(self, chef, receta, estacion_entrega):
        ingredientes_entregados = []
        if chef.ingrediente_en_mano is not None:
            ingredientes_entregados.append(chef.ingrediente_en_mano)

        if estacion_entrega.entregar(receta, ingredientes_entregados):
            self.sumar_puntos(receta.puntos_actuales)
            chef.soltar_ingrediente()
            self._ordenes.remove(receta)
            print(f"Receta entregada: {receta.nombre} (+{receta.puntos_actuales} puntos)")
            return True
        return False

    def juego_terminado(self):
        return self._tiempo_restante <= 0

    def __str__(self):
        return (f"{self._nombre} | "
                f"Puntos: {self._puntos} | "
                f"Tiempo: {self._tiempo_restante:.1f}s | "
                f"Órdenes activas: {len(self._ordenes)}")