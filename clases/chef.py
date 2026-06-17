class Chef:
    def __init__(self, nombre, x, y):
        self.nombre = nombre
        self.x = x  # posicion horizontal en la pantalla
        self.y = y  # posicion vertical en la pantalla
        self.velocidad = 5  # pixeles que se mueve por frame
        self.ingrediente_en_mano = None  # empieza sin nada en la mano
        self.ingredientes_recolectados = []  # ingredientes listos para entregar
        self.activo = True  # indica si este chef es el que se controla

    def mover(self, dx, dy):
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad

    def recoger_ingrediente(self, estacion):
        if self.ingrediente_en_mano is None:  # solo recoge si tiene manos vacias
            self.ingrediente_en_mano = estacion.obtener_ingrediente()
            return True
        else:
            print(f"{self.nombre} ya tiene un ingrediente en la mano")
            return False

    def usar_estacion(self, estacion):
        if self.ingrediente_en_mano is not None:  # solo usa si tiene algo en mano
            resultado = estacion.procesar(self.ingrediente_en_mano)
            return resultado
        else:
            print(f"{self.nombre} no tiene ningun ingrediente")
            return False

    def guardar_ingrediente(self):
        if self.ingrediente_en_mano is not None:
            self.ingredientes_recolectados.append(self.ingrediente_en_mano)
            self.ingrediente_en_mano = None  # vacia la mano despues de guardar
            return True
        return False

    def entregar_receta(self, estacion_entrega, receta):
        if estacion_entrega.entregar(receta, self.ingredientes_recolectados):
            self.ingredientes_recolectados = []  # limpia la lista si fue exitoso
            return True
        else:
            print("los ingredientes no coinciden con la receta")
            return False

    def __str__(self):
        mano = self.ingrediente_en_mano.nombre if self.ingrediente_en_mano else "nada"
        #Esto es un operador ternario, es una forma corta de escribir un if/else en una línea. 
        #Si tiene algo en mano muestra el nombre, si no muestra "nada".
        return f"{self.nombre} | en mano: {mano} | recolectados: {len(self.ingredientes_recolectados)}"