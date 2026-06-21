class Ingrediente:  # clase padre
    def __init__(self, nombre):
        self.nombre = nombre
        self.estado = "crudo"  # los ingredientes son crudos por defecto

    def __str__(self):
        return f"{self.nombre} ({self.estado})"


class VegetalesYFrutas(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)

    def cortar(self):
        self.estado = "cortado"


class PanesYBases(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
        # el pan no necesita preparacion, viene listo para usar
        # CORRECCIÓN: el estado se mantiene "crudo" por defecto desde el padre,
        # pero semánticamente el pan está "listo". Lo marcamos explícitamente
        # para que comparar_receta() lo encuentre igual en receta y en mano del chef.
        self.estado = "listo"


class Proteina(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
        self.cocinada = False  # empieza con False porque aún no pasó por la cocina

    def cocinar(self):
        self.cocinada = True
        self.estado = "cocinado"