import math

# FUNZIONI MATEMATICHE/DI RENDERING

def distanza(puntoA, puntoB):
    return ((puntoA[0] - puntoB[0]) ** 2 + (puntoA[1] - puntoB[1]) ** 2) ** 0.5

def funzione(m, q):
    return {
        'verticale': False,
        'pendenza': m,
        'intercetta': q
    }

def retta(puntoA, puntoB):
    x1 = puntoA[0]
    y1 = puntoA[1]
    x2 = puntoB[0]
    y2 = puntoB[1]
    if x1 == x2:
        # verticale
        return {
            'verticale': True,
            'x': x1
        }
    pendenza = (y2 - y1) / (x2 - x1)
    return {
        'verticale': False,
        'pendenza': pendenza,
        'intercetta': y1 - (x1 * pendenza)
    }

def intersezione(retta1, retta2):
    if (retta1['verticale'] and retta2['verticale'] and
        retta1['x'] == retta2['x']):
        # indeterminato
        return 0
    if (retta1['verticale'] and retta2['verticale'] and
        retta1['x'] != retta2['x']):
        # impossibile
        return 1
    if not retta1['verticale'] and not retta2['verticale']:
        if (retta1['pendenza'] == retta2['pendenza'] and
            retta1['intercetta'] == retta2['intercetta']):
            print('Indeterminato')
            return 0
        elif (retta1['pendenza'] == retta2['pendenza'] and
             retta1['intercetta'] != retta2['intercetta']):
            print('Impossibile')
            return 1
    
    x = 0
    if retta1['verticale']:
        x = retta1['x']
        y = x * retta2['pendenza'] + retta2['intercetta']
    elif retta2['verticale']:
        x = retta2['x']
        y = x * retta1['pendenza'] + retta1['intercetta']
    else:
        x = -1 * (
            retta1['intercetta'] - retta2['intercetta']
        ) / (
            retta1['pendenza'] - retta2['pendenza']
        )
    
        y = x * retta1['pendenza'] + retta1['intercetta']

    return (x, y)

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
            x = round(
                (math.cos(math.radians(gradi)) * self.raggio) + self.centro_x,
                5
            )
            y = round(
                (math.sin(math.radians(gradi)) * self.raggio) + self.centro_y,
                5
            )
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

    def dentro(self, x, y):
        if x == 0 and y == 0:
            return True
        r = retta((self.centro_x, self.centro_y), (x, y))
        if r == 1:
            return distanza(
                (x, y),
                (self.centro_x, self.centro_y)
            ) < self.raggio
        for i in range(6):
            puntoA = self.punti[i]
            puntoB = self.punti[(i + 1) % 6]
            lato = retta(puntoA, puntoB)
            inter = intersezione(r, lato)
            if inter != 0 and inter != 1:
                d = distanza(
                    inter,
                    (self.centro_x, self.centro_y)
                )
                if (d < self.raggio and
                    d > distanza(
                        (x, y),
                        (self.centro_x, self.centro_y)
                    )):
                    return True
        return False
