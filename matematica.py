import math

# FUNZIONI MATEMATICHE/DI RENDERING

class Esagono:

    def __init__(self, centro_x, centro_y, raggio):
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.raggio = raggio

        self.sopra = []
        self.sotto = []
        self.sinistra = []
        self.destra = []
        self.punti = []

        self.crea_vertici()

    def crea_vertici(self):

        gradi = 90 - (360 / 6)
        for i in range(6):
            x = (math.cos(math.radians(gradi)) * self.raggio) + self.centro_x
            y = (math.sin(math.radians(gradi)) * self.raggio) + self.centro_y
            if i <= 2:
                self.sopra.append((x, y))
            if i >= 2 and i <= 3:
                self.sinistra.append((x, y))
            if i >= 3 and i <= 5:
                self.sotto.append((x, y))
            self.punti.append((x, y))
            gradi += 360 / 6

        self.destra.append(self.sotto[-1])
        self.destra.append(self.sopra[0])
