import pygame

CELDA = 80

class Chef:
    def __init__(self, nombre, x, y, velocidad=4, multiplicador_proceso=1.0):
        self.nombre = nombre
        self.velocidad = velocidad
        self.multiplicador_proceso = multiplicador_proceso
        self.ingrediente_en_mano = None
        self.activo = True

        self.rect = pygame.Rect(x, y, CELDA - 16, CELDA - 16)

        # Holdeo de estación
        self.progreso_proceso  = 0.0   # tiempo acumulado hoelando
        self.estacion_actual   = None  # estación que está procesando

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, valor):
        self.rect.x = valor

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, valor):
        self.rect.y = valor

    def mover(self, dx, dy, obstaculos, area_x, area_y, area_ancho, area_alto):
        limite = pygame.Rect(area_x, area_y, area_ancho, area_alto)

        self.rect.x += dx * self.velocidad
        for obs in obstaculos:
            if self.rect.colliderect(obs):
                self.rect.x -= dx * self.velocidad

        self.rect.y += dy * self.velocidad
        for obs in obstaculos:
            if self.rect.colliderect(obs):
                self.rect.y -= dy * self.velocidad

        self.rect.clamp_ip(limite)

    def rect_interaccion(self, dx_dir, dy_dir):
        alcance = 20
        grosor  = self.rect.width + 16

        if dx_dir == 0 and dy_dir == 0:
            return self.rect.inflate(alcance * 2, alcance * 2)

        r = pygame.Rect(0, 0, 0, 0)

        if dx_dir != 0:
            r.width  = alcance
            r.height = grosor
            r.centerx = self.rect.centerx + dx_dir * (self.rect.width // 2 + alcance // 2)
            r.centery = self.rect.centery
        else:
            r.width  = grosor
            r.height = alcance
            r.centerx = self.rect.centerx
            r.centery = self.rect.centery + dy_dir * (self.rect.height // 2 + alcance // 2)

        return r

    def actualizar_holdeo(self, hoeleando, estacion, delta):
        """
        Lllamar cada frame con si ESPACIO está presionado y la estación frente al chef.
        Retorna True en el momento exacto que se completa el proceso.
        """
        if not hoeleando or estacion is None:
            # Soltó espacio o se alejó — cancela progreso
            self.progreso_proceso = 0.0
            self.estacion_actual  = None
            return False

        # Si cambió de estación, reinicia
        if estacion is not self.estacion_actual:
            self.progreso_proceso = 0.0
            self.estacion_actual  = estacion

        tiempo_requerido = estacion.tiempo_base * self.multiplicador_proceso
        self.progreso_proceso += delta

        if self.progreso_proceso >= tiempo_requerido:
            self.progreso_proceso = 0.0
            self.estacion_actual  = None
            return True  # ¡completado!

        return False

    def recoger_ingrediente(self, estacion):
        if self.ingrediente_en_mano is None:
            self.ingrediente_en_mano = estacion.obtener_ingrediente()
            return True
        return False

    def usar_estacion(self, estacion):
        if self.ingrediente_en_mano is not None:
            return estacion.procesar(self.ingrediente_en_mano)
        return False

    def soltar_ingrediente(self):
        ingrediente = self.ingrediente_en_mano
        self.ingrediente_en_mano = None
        return ingrediente

    def __str__(self):
        mano = self.ingrediente_en_mano.nombre if self.ingrediente_en_mano else "nada"
        return f"{self.nombre} | en mano: {mano} | activo: {self.activo}"