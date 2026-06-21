class Chef:
    def __init__(self, nombre, x, y):
        self.nombre = nombre
        self.x = x  # posición horizontal en pantalla
        self.y = y  # posición vertical en pantalla
        self.velocidad = 5  # píxeles por frame
        self.ingrediente_en_mano = None  # empieza sin nada en la mano
        # CORRECCIÓN: según el enunciado "cada Chef puede sostener únicamente
        # un Ingrediente a la vez". La lista ingredientes_recolectados implicaba
        # que el chef acumulaba varios. Se elimina: el chef solo tiene una mano.
        # La lógica de armar la receta se maneja en la EstacionEntrega,
        # que recibe la lista de ingredientes directamente desde la Cocina/juego.
        self.activo = True  # indica si este chef es el que se controla ahora

    def mover(self, dx, dy):
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad

    def recoger_ingrediente(self, estacion):
        """Recoge un ingrediente de una Despensa. Solo si tiene la mano vacía."""
        if self.ingrediente_en_mano is None:
            self.ingrediente_en_mano = estacion.obtener_ingrediente()
            return True
        else:
            print(f"{self.nombre} ya tiene un ingrediente en la mano")
            return False

    def usar_estacion(self, estacion):
        """
        Acción general de interacción con una estación de trabajo.
        El chef coloca su ingrediente en la estación y esta lo procesa.
        CORRECCIÓN: antes el ingrediente quedaba en mano después de procesarse,
        lo que era inconsistente. Ahora procesar() modifica el ingrediente
        in-place (cambia su estado), y el chef lo sigue teniendo en mano
        listo para llevar a la siguiente estación o a la entrega.
        """
        if self.ingrediente_en_mano is not None:
            resultado = estacion.procesar(self.ingrediente_en_mano)
            return resultado
        else:
            print(f"{self.nombre} no tiene ningún ingrediente")
            return False

    def soltar_ingrediente(self):
        """
        Suelta el ingrediente que el chef tiene en mano.
        AÑADIDO: necesario para que la EstacionEntrega pueda recoger
        el ingrediente. El chef lo entrega y queda con mano vacía.
        Retorna el ingrediente soltado, o None si no tenía nada.
        """
        ingrediente = self.ingrediente_en_mano
        self.ingrediente_en_mano = None
        return ingrediente

    def __str__(self):
        mano = self.ingrediente_en_mano.nombre if self.ingrediente_en_mano else "nada"
        return f"{self.nombre} | en mano: {mano} | activo: {self.activo}"