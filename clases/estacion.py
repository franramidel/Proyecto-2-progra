class Estacion:  # clase padre
    def __init__(self, nombre, ingredientes_aceptados):
        self.nombre = nombre
        self.ingredientes_aceptados = ingredientes_aceptados
        # AÑADIDO: coordenadas para que el main pueda posicionar la estación
        # y dibujarla sin necesidad de asignarlas desde afuera cada vez
        self.x = 0
        self.y = 0

    def puede_procesar(self, ingrediente):
        # type() da la clase del ingrediente y revisa si está en la lista de aceptados
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
    # Despensa guarda un ingrediente específico e infinito (uno a la vez según enunciado)
    def __init__(self, nombre, ingrediente_fijo):
        super().__init__(nombre, [type(ingrediente_fijo)])
        self.ingrediente_fijo = ingrediente_fijo
        # CORRECCIÓN: PanesYBases tiene estado "listo" desde su __init__,
        # así que la copia también lo tendrá automáticamente.

    def obtener_ingrediente(self):
        # Crea una copia nueva del ingrediente cada vez que el chef interactúa
        return type(self.ingrediente_fijo)(self.ingrediente_fijo.nombre)


class Cocina(Estacion):
    # CORRECCIÓN DE NOMBRE: en el main se importa como "Cocina" desde estacion,
    # pero también existe la clase Cocina del juego. El main ya lo resuelve con alias.
    # Aquí solo nos aseguramos de que el nombre mostrado sea claro.
    def __init__(self):
        from clases.ingrediente import Proteina
        super().__init__("Cocina", [Proteina])

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
        # CORRECCIÓN: el nombre era "Tabla de cortar" (minúscula) pero en el
        # diccionario SPRITES_ESTACIONES del main era "Tabla de Cortar" (mayúscula).
        # Se unifica aquí para que el sprite se encuentre correctamente.
        super().__init__("Tabla de Cortar", [VegetalesYFrutas])

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.cortar()
            return True
        else:
            print("La tabla solo acepta vegetales y frutas")
            return False


class Freidora(Estacion):
    # CORRECCIÓN SEGÚN ENUNCIADO: la freidora es para papas fritas, no para PanesYBases.
    # El enunciado dice: "Freidora: utilizada para preparar papas fritas."
    # PanesYBases es la categoría del pan (ya listo). Las papas son VegetalesYFrutas.
    # Se cambia el tipo aceptado a VegetalesYFrutas y el estado resultante a "frito".
    # Si en el futuro agregan una clase Papa específica, solo cambiar aquí.
    def __init__(self):
        from clases.ingrediente import VegetalesYFrutas
        super().__init__("Freidora", [VegetalesYFrutas])

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.estado = "frito"
            return True
        else:
            print("La freidora solo acepta vegetales/papas")
            return False


class EstacionEntrega(Estacion):
    def __init__(self):
        # Lista vacía porque no procesa ingredientes individuales, sino recetas completas
        super().__init__("Entrega", [])

    def entregar(self, receta, ingredientes):
        # Delega la comparación a Receta.comparar_receta()
        return receta.comparar_receta(ingredientes)