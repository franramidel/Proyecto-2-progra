class Estacion:
    def __init__(self, nombre, ingredientes_aceptados, tiempo_base=0.0):
        import pygame
        self.nombre = nombre
        self.ingredientes_aceptados = ingredientes_aceptados
        self.tiempo_base = tiempo_base  # segundos base para holdeo (0 = instantáneo)
        self._x = 0
        self._y = 0
        self.rect = pygame.Rect(0, 0, 75, 75)

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

    def puede_procesar(self, ingrediente):
        return type(ingrediente) in self.ingredientes_aceptados

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            return True
        else:
            print(f"Esta estación no acepta {ingrediente.nombre}")
            return False

    def __str__(self):
        return f"Estación: {self.nombre}"


class Despensa(Estacion):
    def __init__(self, nombre, ingrediente_fijo):
        super().__init__(nombre, [type(ingrediente_fijo)], tiempo_base=0.0)
        self.ingrediente_fijo = ingrediente_fijo

    def obtener_ingrediente(self):
        return type(self.ingrediente_fijo)(self.ingrediente_fijo.nombre)


class Cocina(Estacion):
    def __init__(self):
        from clases.ingrediente import Proteina
        super().__init__("Cocina", [Proteina], tiempo_base=2.0)

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.cocinar()
            return True
        else:
            print("La cocina solo acepta proteínas")
            return False


class TablaDeCortar(Estacion):
    def __init__(self):
        from clases.ingrediente import VegetalesYFrutas
        super().__init__("Tabla de Cortar", [VegetalesYFrutas], tiempo_base=1.5)

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.cortar()
            return True
        else:
            print("La tabla solo acepta vegetales y frutas")
            return False


class Freidora(Estacion):
    def __init__(self):
        from clases.ingrediente import VegetalesYFrutas
        super().__init__("Freidora", [VegetalesYFrutas], tiempo_base=2.0)

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.estado = "frito"
            return True
        else:
            print("La freidora solo acepta vegetales/papas")
            return False


class EstacionEntrega(Estacion):
    def __init__(self):
        super().__init__("Entrega", [], tiempo_base=0.0)

    def entregar(self, receta, ingredientes):
        return receta.comparar_receta(ingredientes)


class MesaEnsamblaje(Estacion):
    def __init__(self):
        super().__init__("Ensamblaje", [], tiempo_base=0.0)
        self.ingredientes_depositados = []

    def depositar(self, ingrediente):
        self.ingredientes_depositados.append(ingrediente)
        return True

    def recoger_todo(self):
        """Retorna la lista y la vacía."""
        items = list(self.ingredientes_depositados)
        self.ingredientes_depositados.clear()
        return items

    def esta_vacia(self):
        return len(self.ingredientes_depositados) == 0