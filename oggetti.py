import arcade
import random
import math
from pyglet.graphics import Batch
from matematica import *
from costanti import *

# DEFINIZIONE OGGETTI PRESENTI NEL GIOCO

class IndiceTruppa:
    # modalita 0 -> default
    # modalita 1 -> arruola
    # modalita 2 -> muovi
    def __init__(self, provincia, num_soldati, modalita, batch):

        self.forma = None

        colore = None
        offset = 0

        if modalita == 0:
            colore = arcade.color.WHITE
        elif modalita == 1:
            colore = arcade.color.GREEN
            offset = -FONT_SIZE_TRUPPE * 2
        elif modalita == 2:
            colore = arcade.color.RED
            offset = FONT_SIZE_TRUPPE * 2

        self.testo = arcade.Text(
            str(num_soldati),
            provincia.x - (provincia.raggio / 5 * 4),
            provincia.y - (FONT_SIZE_TRUPPE / 2) + offset,
            colore,
            font_size = FONT_SIZE_TRUPPE,
            width = (provincia.raggio * 2) / 5 * 4,
            align = 'center',
            batch = batch
        )

        self.forma = arcade.shape_list.create_rectangle_filled(
            provincia.x,
            provincia.y + offset,
            (provincia.raggio * 2) / 5 * 4,
            FONT_SIZE_TRUPPE + 6,
            arcade.color.BLACK    
        )

class Stato:

    def __init__(self):

        self.elenco_province = []
        self.colore = None
        self.forma = arcade.shape_list.ShapeElementList()

        self.soldi = SOLDI
        self.punti_azione = PUNTI_AZIONE
        # altri Stati con cui lo Stato è in guerra
        self.guerra = []

        self.forma_truppe = arcade.shape_list.ShapeElementList()
        self.truppe = []
        self.batch = None

    # aggiorna le condizioni dello Stato, includendo le risorse (es. soldi)
    def aggiorna_statistiche(self):
        for p in self.elenco_province:
            self.soldi += int(
                PRODUZIONE_PER_ABITANTE * p.abitanti - (
                COSTO_MANTENIMENTO_SOLDATO * p.soldati)
            )
            p.abitanti = int(p.abitanti * CRESCITA_POPOLAZIONE)
            

    def aggiorna_forma(self):
        
        self.forma.clear()

        for p in self.elenco_province:
            punti = p.esagono.punti
            shape_list = arcade.shape_list.create_polygon(punti, self.colore)
            self.forma.append(shape_list)
        
    # viene assegnato un colore allo Stato; ritorna i colori rimanenti
    def scegli_colore(self, colori_stati_disponibili):

        if len(colori_stati_disponibili) != 0:
            # il colore viene scelto casualmente
            self.colore = random.choice(colori_stati_disponibili)
            colori_stati_disponibili.remove(self.colore)
        else:
            print('Non ci sono altri colori disponibili')
        return colori_stati_disponibili

    # viene aggiunta una provincia allo Stato; essa cambia la propria appartenenza
    def aggiungi_provincia(self, provincia):
        if provincia.stato != None:
            provincia.stato.elenco_province.remove(provincia)
        provincia.stato = self
        self.elenco_province.append(provincia)

    # aggiunge allo Stato tutte le province confinanti non appartenenti a nessuno; ritorna le province aggiunte
    def espandi(self):

        province_aggiunte = 0
        massimo_province = 6
        prov_da_scegliere = self.elenco_province.copy()
        while len(prov_da_scegliere) > 0:
            p = random.choice(prov_da_scegliere)
            vicine = p.province_vicine()

            while len(vicine) > 0:
                v = random.choice(vicine)
                if v != None and v.stato == None:
                    self.aggiungi_provincia(v)
                    province_aggiunte += 1
                if province_aggiunte == massimo_province:
                    return massimo_province
                vicine.remove(v)

            prov_da_scegliere.remove(p)

        return province_aggiunte

    # viene renderizzato lo Stato. Se truppe è True, vengono mostrate anche le truppe
    def disegna(self):

        self.forma.draw()

    def mostra_truppe(self):
        if self.batch != None:
            self.forma_truppe.draw()           
            self.batch.draw()

    def renderizza_truppe(self):
        
        self.forma_truppe.clear()
        self.batch = Batch()
        self.truppe = []

        province = self.elenco_province + self.ottieni_confini(True)

        for p in province:

            indice = None

            # soldati già stanziati
            soldati_stanziati = p.soldati
            if soldati_stanziati != 0 and p.stato == self:
                indice = IndiceTruppa(p, soldati_stanziati, 0, self.batch)
                self.truppe.append(indice)
                self.forma_truppe.append(indice.forma)

            t = False
    
            soldati_spostati = 0

            for azione in p.azioni:
                # soldati da arruolare
                if azione['azione'] == 'arruola' and not t and azione['soldati'] != 0 and p.stato == self:
                    indice = IndiceTruppa(p, azione['soldati'], 1, self.batch)
                    self.truppe.append(indice)
                    self.forma_truppe.append(indice.forma)

                    t = True
                # si aggiunge a soldati_spostati il numero di soldati che devono arrivare nella provincia
                if azione['azione'] == 'arrivo truppe' and azione['stato'] == self:
                    soldati_spostati += azione['soldati']

            if soldati_spostati != 0:
                indice = IndiceTruppa(p, soldati_spostati, 2, self.batch)
                self.truppe.append(indice)
                self.forma_truppe.append(indice.forma)
    
    # restituisce le province lungo i confini con gli altri Stati. Se modalita è False restituisce le province confinanti all'interno dello Stato, se modalita è True, le province restituite sono appartenenti agli Stati confinanti

    def ottieni_confini(self, modalita):
        confini = []
        for p in self.elenco_province:
            vicine = p.province_vicine()
            for v in vicine:
                if v != None and v.stato != self and not modalita:
                    confini.append(p)
                    break
                if v != None and v.stato != self and modalita:
                    confini.append(v)

        return confini

    # aggiunge un'azione per arruolare i soldati
    def arruola_soldati(self, soldati, provincia):
        self.soldi = int(self.soldi - COSTO_SOLDATO * soldati)
        provincia.abitanti -= soldati
        self.punti_azione -= 1
        # aggiungi azioni
        provincia.azioni.append({
            'azione': 'arruola',
            'soldati': soldati
        })
        
    # aggiunge un'azione per muovere i soldati
    def muovi_soldati(self, soldati, origine, destinazione):
        origine.soldati -= soldati 
        self.punti_azione -= 1
        # aggiungi azioni
        origine.azioni.append({
            'azione': 'muovi',
            'destinazione': destinazione,
            'soldati': soldati
        })
        destinazione.azioni.append({
            'azione': 'arrivo truppe',
            'stato': self,
            'soldati': soldati,
            'origine': origine
        })
    
    # ritorna il massimo di soldati che possono essere arruolati in una provincia
    def massimo_soldati(self, provincia):
        return int(max(0, min(self.soldi / COSTO_SOLDATO, provincia.abitanti * TASSO_ARRUOLAMENTO)))

class Provincia:

    def __init__(self, x, y, raggio):

        # dati invariabili della provincia
        self.x = x
        self.y = y
        self.raggio = raggio
        self.esagono = Esagono(x, y, raggio)

        # condizioni della provincia
        self.stato = None
        self.abitanti = ABITANTI_PER_PROVINCIA
        self.soldati = 0

        # province vicine
        self.ovest = None
        self.est = None
        self.nordest = None
        self.nordovest = None
        self.sudest = None
        self.sudovest = None

        # ordini da eseguire
        self.azioni = []
        
    # restituisce le province vicine della provincia
    def province_vicine(self):
        return [
            self.est,
            self.ovest,
            self.nordest,
            self.nordovest,
            self.sudest,
            self.sudovest
        ] 

class Mappa:
    def __init__(self):

        self.province = []

    # aggiunge le province alla mappa: modifica la lista province
    def crea_province(self, num_righe, num_province_per_riga, raggio):

        y = 0
        for i in range(num_righe):

            x = 0
            if i % 2 != 0:
                x = raggio * math.cos(math.radians(30))

            self.province.append([])

            for j in range(num_province_per_riga):
                self.province[-1].append(Provincia(x, y, raggio))
                x += raggio * math.cos(math.radians(30)) * 2

            y += raggio + raggio * math.sin(math.radians(30))

        # a ogni provincia viene riferito quali sono le province vicine

        len_fila = len(self.province[0])
        for i in range(0, len(self.province)):
            for j in range(0, len_fila):
                # est
                if j - 1 >= 0:
                    self.province[i][j].est = self.province[i][j - 1]
                # ovest
                if j + 1 < len_fila:
                    self.province[i][j].ovest = self.province[i][j + 1]
                # sudest
                if i - 1 >= 0 and i % 2 == 0:
                    self.province[i][j].sudest = self.province[i - 1][j]
                if i - 1 >= 0 and i % 2 != 0 and j + 1 < len_fila:
                    self.province[i][j].sudest = self.province[i - 1][j + 1]
                # sudovest
                if i - 1 >= 0 and i % 2 == 0 and j - 1 >= 0:
                    self.province[i][j].sudovest = self.province[i - 1][j - 1]
                if i - 1 >= 0 and i % 2 != 0:
                    self.province[i][j].sudovest = self.province[i - 1][j]
                # nordest
                if i + 1 < len(self.province) and i % 2 == 0:
                    self.province[i][j].nordest = self.province[i + 1][j]
                if i + 1 < len(self.province) and i % 2 != 0 and j + 1 < len_fila:
                    self.province[i][j].nordest = self.province[i + 1][j + 1]
                # nordovest
                if i + 1 < len(self.province) and i % 2 == 0 and j - 1 >= 0:
                    self.province[i][j].nordovest = self.province[i + 1][j - 1]
                if i + 1 < len(self.province) and i % 2 != 0:
                    self.province[i][j].nordovest = self.province[i + 1][j]

    def trova_provincia(self, x, y):
        inizio_x = self.province[0][0].centro_x
        inizio_y = self.province[0][0].centro_y
        incremento_y = self.raggio + self.raggio * math.sin(math.radians(30))

    # disegna la scacchiera esagonale
    def disegna_scacchiera(self):

        linee = []
        for i in self.province:
            for j in i:
                punti = j.esagono.punti
                for i in range(len(punti)):
                    start = punti[i]
                    end = punti[(i + 1) % len(punti)]
                    linee.append(start)
                    linee.append(end)
        arcade.draw_lines(linee, arcade.color.BLACK, 1)

