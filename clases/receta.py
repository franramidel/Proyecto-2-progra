class Receta:
    def __init__(self, nombre, ingredientes, puntos_base, tiempo_maximo):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.puntos_base = puntos_base
        self.puntos_actuales = puntos_base
        
    #puntos_base guarda el valor original de la receta para siempre.
    #puntos_actuales es el que va cambiando con las penalizaciones. 
    #los separamos porque el proyecto pide descontar el valor original si la receta expira
        self.tiempo_maximo = tiempo_maximo
        self.tiempo_transcurrido = 0
        self.activa = True
        
    #tiempo_transcurrido empieza en 0 y va aumentando. 
    #activa indica si la receta sigue en juego o ya expiró.
    
    def actualizar_tiempo(self, delta):
        if not self.activa:
            return
        #delta es el tiempo que pasó desde el último frame del juego.
        #Si la receta ya no está activa, no hace nada y sale.
        self.tiempo_transcurrido += delta #acomula el tiempo que ha pasado

        if self.tiempo_transcurrido >= self.tiempo_maximo:
            self.tiempo_transcurrido = 0
            self.puntos_actuales = self.puntos_actuales // 2
        #Cuando se cumple el tiempo máximo, reinicia el contador y divide los puntos a la mitad.
        #// es división entera, así nunca se tiene decimales
        
            if self.puntos_actuales == 0:
                self.activa = False
            #cuando los puntos llegan a 0, la receta se desactiva automáticamente.
    
    def comparar_receta(self, ingredientes_chef):
        if len(ingredientes_chef) != len(self.ingredientes):
            return False
        #si la cantidad de ingredientes no coincide, ni vale la pena comparar, retorna False directo
        requeridos = sorted([type(i).__name__ + i.estado 
                            for i in self.ingredientes])
        entregados = sorted([type(i).__name__ + i.estado 
                            for i in ingredientes_chef])
        #Esto es una lista por comprensión. 
        #Para cada ingrediente crea un texto combinando su tipo y su estado, 
        #por ejemplo "Proteina cocinado" o "VegetalesYFrutas cortado". Luego los ordena alfabéticamente con sorted para que el orden no importe al comparar
        return requeridos == entregados

    def __str__(self):
        return f"{self.nombre} | Puntos: {self.puntos_actuales} | Tiempo: {self.tiempo_maximo - self.tiempo_transcurrido:.1f}s"