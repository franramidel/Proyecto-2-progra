class Receta:
    def __init__(self, nombre, ingredientes, puntos_base, tiempo_maximo):
        self._nombre             = nombre
        self._ingredientes       = ingredientes
        self._puntos_base        = puntos_base
        self._puntos_actuales    = puntos_base
        self._tiempo_maximo      = tiempo_maximo
        self._tiempo_transcurrido = 0.0
        self._activa             = True

    # ── Propiedades ──────────────────────────────────────────────────
    @property
    def nombre(self):
        return self._nombre

    @property
    def ingredientes(self):
        return self._ingredientes

    @property
    def puntos_base(self):
        return self._puntos_base

    @property
    def puntos_actuales(self):
        return self._puntos_actuales

    @property
    def tiempo_maximo(self):
        return self._tiempo_maximo

    @property
    def activa(self):
        return self._activa

    # ── Lógica ───────────────────────────────────────────────────────
    def actualizar_tiempo(self, delta):
        if not self._activa:
            return

        self._tiempo_transcurrido += delta

        while self._tiempo_transcurrido >= self._tiempo_maximo:
            self._tiempo_transcurrido -= self._tiempo_maximo
            self._puntos_actuales = self._puntos_actuales // 2

            if self._puntos_actuales == 0:
                self._activa = False
                return

    def tiempo_restante(self):
        return max(0.0, self._tiempo_maximo - self._tiempo_transcurrido)

    def comparar_receta(self, ingredientes_entregados):
        """
        Compara ingredientes entregados contra los requeridos.
        Desempaca ingredientes compuestos antes de comparar.
        """
        desempacados = []
        for ing in ingredientes_entregados:
            if ing.es_compuesto():
                desempacados.extend(ing.componentes)
            else:
                desempacados.append(ing)

        if len(desempacados) != len(self._ingredientes):
            return False

        requeridos = sorted([
            type(i).__name__ + i.nombre + i.estado
            for i in self._ingredientes
        ])
        entregados = sorted([
            type(i).__name__ + i.nombre + i.estado
            for i in desempacados
        ])
        return requeridos == entregados

    def __str__(self):
        return (f"{self._nombre} | "
                f"Puntos: {self._puntos_actuales}/{self._puntos_base} | "
                f"Tiempo restante: {self.tiempo_restante():.1f}s")