import arcade
import random
import math
from pyglet.graphics import Batch

from matematica import *

PUNTI_AZIONE = 10
FONT_SIZE_TRUPPE = 8
ABITANTI_PER_PROVINCIA = 10000
SOLDI = 100000000000

# DEFINIZIONE OGGETTI PRESENTI NEL GIOCO

class Stato:

    def __init__(self):

        self.elenco_province = []
        self.colore = None
        self.forma = arcade.shape_list.ShapeElementList()

        self.soldi = SOLDI
        self.punti_azione = PUNTI_AZIONE
        # altri Stati con cui lo Stato è in guerra
        self.guerra = []

        self.costo_soldato = 10
        self.tasso_arruolamento = 0.1

    def aggiungi_forma(self, provincia):
        
        punti = provincia.esagono.punti
        shape_list = arcade.shape_list.create_polygon(punti, self.colore)
        self.forma.append(shape_list)
        provincia.forma = shape_list
    
    def rimuovi_forma(self, provincia):
        try:
            self.forma.remove(provincia.forma)
            provincia.forma = None
        except:
            print('ERRORE: provincia non esistente nella forma dello stato')

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
            provincia.stato.rimuovi_forma(provincia)
        provincia.stato = self
        self.aggiungi_forma(provincia)
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

    # viene renderizzato lo Stato
    def disegna(self):

        if self.forma == None:
            self.aggiorna_forma()
        self.forma.draw()
    
    def disegna_sfondo_testo(self, p, shift):
        arcade.draw_lbwh_rectangle_filled(
            p.x - (p.raggio / 5 * 4),
            p.y - (FONT_SIZE_TRUPPE / 2) - 3 + shift,
            (p.raggio * 2) / 5 * 4,
            FONT_SIZE_TRUPPE + 6,
            arcade.color.BLACK    
        )

    def testo_truppa(self, p, soldati, colore, shift, b):
        return arcade.Text(
            str(soldati),
            p.x - (p.raggio / 5 * 4),
            p.y - (FONT_SIZE_TRUPPE / 2) + shift,
            colore,
            font_size = FONT_SIZE_TRUPPE,
            width = (p.raggio * 2) / 5 * 4,
            align = 'center',
            batch = b
        )

    def mostra_truppe(self):

        batch = Batch()
        testi = []

        province = self.elenco_province + self.ottieni_confini(True)

        for p in province:

            soldati_stanziati = p.soldati
            if soldati_stanziati != 0 and p.stato == self:
                self.disegna_sfondo_testo(p, 0)
                testo = self.testo_truppa(p, soldati_stanziati, arcade.color.WHITE, 0, batch)
                testi.append(testo)

            t = False
    
            soldati_spostati = 0

            for azione in p.azioni:
                if azione['azione'] == 'arruola' and not t and azione['soldati'] != 0 and p.stato == self:
                    self.disegna_sfondo_testo(p, -FONT_SIZE_TRUPPE * 2)
                    testo = self.testo_truppa(p, azione['soldati'], arcade.color.GREEN, -FONT_SIZE_TRUPPE * 2, batch)
                    testi.append(testo)
                    t = True
                if azione['azione'] == 'arrivo truppe' and azione['stato'] == self:
                    soldati_spostati += azione['soldati']

            if soldati_spostati != 0:
                self.disegna_sfondo_testo(p, FONT_SIZE_TRUPPE * 2)
                testo = self.testo_truppa(p, soldati_spostati, arcade.color.RED, FONT_SIZE_TRUPPE * 2, batch)
                testi.append(testo)

        batch.draw()

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

    def arruola_soldati(self, soldati, provincia):
        self.soldi -= self.costo_soldato * soldati
        provincia.abitanti -= soldati
        self.punti_azione -= 1
        # aggiungi azioni
        provincia.azioni.append({
            'azione': 'arruola',
            'soldati': soldati
        })

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

class Provincia:

    def __init__(self, x, y, raggio):

        self.x = x
        self.y = y
        self.raggio = raggio
        self.stato = None
        self.esagono = Esagono(x, y, raggio)

        self.abitanti = ABITANTI_PER_PROVINCIA
        self.soldati = 0

        # province vicine
        self.est = None
        self.ovest = None
        self.nordest = None
        self.nordovest = None
        self.sudest = None
        self.sudovest = None

        self.azioni = []
        
        self.forma = None

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

