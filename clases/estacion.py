class Estacion: #clase padre
    def __init__(self, nombre, ingredientes_aceptados):
        self.nombre = nombre
        self.ingredientes_aceptados = ingredientes_aceptados

    def puede_procesar(self, ingrediente):
        return type(ingrediente) in self.ingredientes_aceptados #type da la clase del ingrediente,
                                                                #revisa si la clase esta en la lista de aceptados, retorna true o false

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            return True
        else:
            print(f"Esta estación no acepta {ingrediente.nombre}")
            return False

    def __str__(self):
        return f"Estación: {self.nombre}"


class Despensa(Estacion):
#despensa guarda un ingrediente especifico, type obtiene la clase del ingrediente para pasarsela al padre como lista de aceptados    
    def __init__(self, nombre, ingrediente_fijo):
        super().__init__(nombre, [type(ingrediente_fijo)])
        self.ingrediente_fijo = ingrediente_fijo

    def obtener_ingrediente(self):
        # Crea una copia nueva del ingrediente cada vez
        return type(self.ingrediente_fijo)(self.ingrediente_fijo.nombre)


class Cocina(Estacion):
    def __init__(self):
        from clases.ingrediente import Proteina
        super().__init__("Cocina", [Proteina])

    def procesar(self, ingrediente):
#sobreescribe el procesar del padre. si el ingrediente es válido, llama a cocinar() que ya definimos en proteina
        if self.puede_procesar(ingrediente):
            ingrediente.cocinar()
            return True
        else:
            print(f"La cocina solo acepta proteínas")
            return False


class TablaDeCortar(Estacion):
    def __init__(self):
        from clases.ingrediente import VegetalesYFrutas
        super().__init__("Tabla de cortar", [VegetalesYFrutas])

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.cortar()
            return True
        else:
            print(f"La tabla solo acepta vegetales")
            return False


class Freidora(Estacion):
    def __init__(self):
        from clases.ingrediente import PanesYBases
        super().__init__("Freidora", [PanesYBases])

    def procesar(self, ingrediente):
        if self.puede_procesar(ingrediente):
            ingrediente.estado = "frito"
            return True
        else:
            print(f"La freidora solo acepta bases")
            return False


class EstacionEntrega(Estacion):
    def __init__(self):
        super().__init__("Entrega", []) #lista empieza vacia pq no procesa ingredientes individuales, sino recetas completas

    def entregar(self, receta, ingredientes):
        return receta.comparar_receta(ingredientes)
#Recibe la receta y la lista de ingredientes que tiene el chef, 
#y llama a comparar_receta que definiremos después en la clase Receta.
#Retorna True si la receta está completa, False si no.
