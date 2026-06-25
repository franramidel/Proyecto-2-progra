class Estacion:
    def __init__(self, nombre, ingredientes_aceptados, tiempo_base=0.0):
        import pygame
        self._nombre                = nombre
        self._ingredientes_aceptados = ingredientes_aceptados
        self._tiempo_base           = tiempo_base
        self._x = 0
        self._y = 0
        self.rect = pygame.Rect(0, 0, 75, 75)

    # ── Propiedades ──────────────────────────────────────────────────
    @property
    def nombre(self):
        return self._nombre

    @property
    def ingredientes_aceptados(self):
        return self._ingredientes_aceptados

    @property
    def tiempo_base(self):
        return self._tiempo_base

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, valor):
        self._x = valor
        self.rect.x = valor

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, valor):
        self._y = valor
        self.rect.y = valor

    # ── Lógica base ──────────────────────────────────────────────────
    def puede_procesar(self, ingrediente):
        return type(ingrediente) in self._ingredientes_aceptados

    def procesar(self, ingrediente):
        """
        Método polimórfico: cada subclase decide cómo procesar.
        La base valida el tipo; las subclases llaman a preparar()
        del ingrediente — sin isinstance, con despacho por tipo.
        """
        if not self.puede_procesar(ingrediente):
            print(f"{self._nombre} no acepta {ingrediente.nombre}")
            return False
        ingrediente.preparar()
        return True

    def __str__(self):
        return f"Estación: {self._nombre}"


class Despensa(Estacion):
    def __init__(self, nombre, ingrediente_fijo):
        super().__init__(nombre, [type(ingrediente_fijo)], tiempo_base=0.0)
        self._ingrediente_fijo = ingrediente_fijo

    def obtener_ingrediente(self):
        return type(self._ingrediente_fijo)(self._ingrediente_fijo.nombre)

    def procesar(self, ingrediente):
        """La despensa no procesa; solo entrega."""
        return False


class Cocina(Estacion):
    def __init__(self):
        from clases.ingrediente import Proteina
        super().__init__("Cocina", [Proteina], tiempo_base=2.0)

    def procesar(self, ingrediente):
        """
        Polimorfismo: llama ingrediente.preparar() que en Proteina
        ejecuta cocinar() — sin necesidad de isinstance.
        """
        if not self.puede_procesar(ingrediente):
            print("La cocina solo acepta proteínas")
            return False
        if not ingrediente.puede_prepararse():
            print(f"{ingrediente.nombre} ya está cocinado")
            return False
        ingrediente.preparar()
        return True


class TablaDeCortar(Estacion):
    def __init__(self):
        from clases.ingrediente import VegetalesYFrutas
        super().__init__("Tabla de Cortar", [VegetalesYFrutas], tiempo_base=1.5)

    def procesar(self, ingrediente):
        """
        Polimorfismo: llama ingrediente.preparar() que en VegetalesYFrutas
        ejecuta cortar().
        """
        if not self.puede_procesar(ingrediente):
            print("La tabla solo acepta vegetales y frutas")
            return False
        if not ingrediente.puede_prepararse():
            print(f"{ingrediente.nombre} ya está preparado")
            return False
        ingrediente.preparar()
        return True


class Freidora(Estacion):
    def __init__(self):
        from clases.ingrediente import VegetalesYFrutas
        super().__init__("Freidora", [VegetalesYFrutas], tiempo_base=2.0)

    def procesar(self, ingrediente):
        """
        La freidora fríe en lugar de cortar — sobreescribe el comportamiento
        de preparar() usando freir() directamente sobre el vegetal.
        """
        if not self.puede_procesar(ingrediente):
            print("La freidora solo acepta vegetales")
            return False
        if not ingrediente.puede_prepararse():
            print(f"{ingrediente.nombre} ya está preparado")
            return False
        ingrediente.freir()
        return True


class EstacionEntrega(Estacion):
    def __init__(self):
        super().__init__("Entrega", [], tiempo_base=0.0)

    def procesar(self, ingrediente):
        """La entrega no procesa ingredientes directamente."""
        return False

    def entregar(self, receta, ingredientes):
        return receta.comparar_receta(ingredientes)


class MesaEnsamblaje(Estacion):
    def __init__(self):
        super().__init__("Ensamblaje", [], tiempo_base=0.0)
        self._ingrediente_fusionado = None

    @property
    def ingrediente_fusionado(self):
        return self._ingrediente_fusionado

    def depositar(self, ingrediente):
        if self._ingrediente_fusionado is None:
            self._ingrediente_fusionado = ingrediente
        else:
            self._ingrediente_fusionado.fusionar(ingrediente)
        return True

    def recoger(self):
        ing = self._ingrediente_fusionado
        self._ingrediente_fusionado = None
        return ing

    def limpiar(self):
        self._ingrediente_fusionado = None

    def esta_vacia(self):
        return self._ingrediente_fusionado is None

    def procesar(self, ingrediente):
        """La mesa ensambla, no procesa ingredientes individuales."""
        return False

    def __str__(self):
        if self._ingrediente_fusionado:
            return f"Mesa: {self._ingrediente_fusionado.nombre}"
        return "Mesa: vacía"