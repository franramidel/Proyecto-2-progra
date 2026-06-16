class Ingrediente: #clase padre
    def __init__(self, nombre):
        self.nombre=nombre
        self.estado="crudo" #los ingredientes son crudos por defecto
        
    def __str__(self):
        return f"{self.nombre} ({self.estado})"
    
class VegetalesYFrutas(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
    
    def cortar(self):
        self.estado="cortado"
    
class PanesYBases(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
    #no tiene metodos pq el pan no necesita preparacion, viene listo para usar
    
class Proteina(Ingrediente):
    def __init__(self, nombre):
        super().__init__(nombre)
        self.cocinada= False #empieza con false pq la proteina aun no pasó por la cocina
        
    
    def cocinar(self): #aqui la cocina
        self.cocinada= True
        self.estado= "cocinado"
        

