from copy import copy


class Ingrediente:
    def __init__(self, nombre):
        self._nombre     = nombre
        self._estado     = "crudo"
        self._componentes = []

    # ── Propiedades ──────────────────────────────────────────────────
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        self._estado = valor

    @property
    def componentes(self):
        return self._componentes

    @componentes.setter
    def componentes(self, valor):
        self._componentes = valor

    # ── Polimorfismo: cada subclase implementa preparar() ────────────
    def preparar(self):
        """
        Método polimórfico base. Cada subclase lo sobreescribe
        con la lógica de preparación que le corresponde.
        """
        raise NotImplementedError(
            f"{type(self).__name__} debe implementar preparar()"
        )

    def puede_prepararse(self):
        """
        Indica si el ingrediente aún puede ser procesado.
        Las subclases pueden sobreescribir para agregar condiciones.
        """
        return self._estado == "crudo"

    # ── Lógica de fusión (compuesto) ─────────────────────────────────
    def es_compuesto(self):
        return len(self._componentes) > 0

    def fusionar(self, otro):
        if not self.es_compuesto():
            primero = copy(self)
            primero.componentes = []
            self._componentes.append(primero)
        self._componentes.append(otro)
        self._nombre = "+".join(c.nombre for c in self._componentes)
        self._estado = "listo"
        return self

    def __str__(self):
        return f"{self._nombre} ({self._estado})"


class VegetalesYFrutas(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)

    def preparar(self):
        """Corta el vegetal o fruta."""
        self._estado = "cortado"

    def freir(self):
        """Alternativa para papas u otros vegetales que se fríen."""
        self._estado = "frito"

    def puede_prepararse(self):
        return self._estado == "crudo"


class PanesYBases(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
        self._estado = "listo"

    def preparar(self):
        """El pan no necesita preparación; ya está listo."""
        self._estado = "listo"

    def puede_prepararse(self):
        return False  # no requiere procesamiento


class Proteina(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
        self._cocinada = False

    @property
    def cocinada(self):
        return self._cocinada

    @cocinada.setter
    def cocinada(self, valor):
        self._cocinada = valor

    def preparar(self):
        """Cocina la proteína."""
        self._cocinada = True
        self._estado   = "cocinado"

    def puede_prepararse(self):
        return not self._cocinada