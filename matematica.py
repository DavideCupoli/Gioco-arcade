import math

# FUNZIONI MATEMATICHE/ALGORITMI GENERICI

# ricostruisce il percorso a partire dalla destinazione
def ricostruisci_percorso(genitori, destinazione):
    percorso = []
    corrente = destinazione
    while corrente != None:
        percorso.insert(0, corrente)
        corrente = genitori[corrente]
    return percorso

# restituisce il percorso più breve tra due province
def trova_percorso(origine, destinazione):
    coda = [origine]
    visitati = {origine}
    genitori = {origine: None}
    
    while len(coda) != 0:
        corrente = coda.pop(0)
        if corrente == destinazione:
            return ricostruisci_percorso(genitori, destinazione)
        for vicino in corrente.province_vicine():
            if (vicino != None and
                not vicino in visitati and
                (vicino.stato == origine.stato or vicino.stato in origine.stato.guerra)
                ):
                visitati.add(vicino)
                genitori[vicino] = corrente
                coda.append(vicino)
    return []

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

    # crea i vertici dell'esagono
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