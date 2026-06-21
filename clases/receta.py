class Receta:
    def __init__(self, nombre, ingredientes, puntos_base, tiempo_maximo):
        self.nombre = nombre
        self.ingredientes = ingredientes  # lista de Ingrediente requeridos
        # puntos_base: valor original, nunca cambia (se usa para descontar al expirar)
        # puntos_actuales: el que va bajando con penalizaciones
        self.puntos_base = puntos_base
        self.puntos_actuales = puntos_base
        self.tiempo_maximo = tiempo_maximo
        self.tiempo_transcurrido = 0.0
        self.activa = True

    def actualizar_tiempo(self, delta):
        if not self.activa:
            return

        self.tiempo_transcurrido += delta

        # CORRECCIÓN: el enunciado dice que cuando se cumple el tiempo máximo
        # los puntos se reducen a la mitad, y ESE proceso puede repetirse.
        # Es decir, el tiempo_maximo actúa como un ciclo que se repite.
        # Se usa un while para cubrir el caso de que pasen varios ciclos en un delta grande.
        while self.tiempo_transcurrido >= self.tiempo_maximo:
            self.tiempo_transcurrido -= self.tiempo_maximo  # reinicia el ciclo
            self.puntos_actuales = self.puntos_actuales // 2  # división entera, sin decimales

            if self.puntos_actuales == 0:
                self.activa = False
                return  # ya no hace falta seguir procesando ciclos

    def tiempo_restante(self):
        """Tiempo que queda en el ciclo actual antes de la próxima penalización."""
        return max(0.0, self.tiempo_maximo - self.tiempo_transcurrido)

    def comparar_receta(self, ingredientes_chef):
        """
        Compara los ingredientes entregados contra los requeridos.
        CORRECCIÓN: antes comparaba type(i).__name__ + i.estado, lo que fallaba
        si dos ingredientes del mismo tipo tenían distinto nombre (ej: "Tomate" vs "Papa").
        Ahora incluye también el nombre del ingrediente para mayor precisión.
        """
        if len(ingredientes_chef) != len(self.ingredientes):
            return False

        # Clave: tipo + nombre + estado. Ordenados para que el orden no importe.
        requeridos = sorted([
            type(i).__name__ + i.nombre + i.estado
            for i in self.ingredientes
        ])
        entregados = sorted([
            type(i).__name__ + i.nombre + i.estado
            for i in ingredientes_chef
        ])
        return requeridos == entregados

    def __str__(self):
        return (f"{self.nombre} | "
                f"Puntos: {self.puntos_actuales}/{self.puntos_base} | "
                f"Tiempo restante: {self.tiempo_restante():.1f}s")