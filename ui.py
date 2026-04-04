import arcade.gui
import math
from costanti import *

# GESTIONE INTERFACCIA

def converti_soldi(soldi):

    if soldi == 0:
        return '000'
    if soldi >= 10**12:
        return '999+B'

    multipli = 'KMB'

    segno = ''

    if soldi < 0:
        segno = '-'
        soldi *= -1

    cifre = int(math.log(soldi, 10))

    if cifre < 3:
        return f'{segno}{soldi:03d}'
    else:
        return f'{segno}{(soldi // (10 ** (cifre - (cifre % 3)))):03d}{multipli[cifre // 3 - 1]}'

# Widget per spostare/arruolare un certo numero di soldati
class BarraProgressiva(arcade.gui.UIWidget):
    value = arcade.gui.Property(0.0)

    def __init__(self, value, width, height, color, interfaccia):
        super().__init__(
            width = width,
            height = height,
            size_hint = None
        )
        self.with_background(color=arcade.uicolor.WHITE)
        self.with_border(color=arcade.uicolor.GRAY_CONCRETE)

        self.value = value
        self.color = color
        self.interfaccia = interfaccia

        # trigger a render when the value changes
        arcade.gui.bind(self, "value", self.trigger_render)

    def on_event(self, event):
        if isinstance(event, arcade.gui.events.UIMousePressEvent) and self.interfaccia.dentro(event.x, event.y, self):
            self.value = max(0, min(1, (event.x - self.position.x) / self.width))
        if isinstance(event, arcade.gui.events.UIMouseDragEvent): 
            x = event.x + event.dx
            y = event.y + event.dy
            if y > self.position.y and y - self.position.y < self.height:
                self.value = max(0, min(1, (x - self.position.x) / self.width))

    def do_render(self, surface: arcade.gui.Surface):
        """Draw the actual progress bar."""
        # this will set the viewport to the size of the widget
        # so that 0,0 is the bottom left corner of the widget content
        self.prepare_render(surface)

        # Draw the actual bar
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self.content_width * self.value,
            self.content_height,
            self.color,
        )

class Etichetta(arcade.gui.UILabel):

    testo = arcade.gui.Property()

    def __init__(self, width, height, margine, testo, percorso_icona):
        super().__init__(
            width = width,
            height = height,
            size_hint = None,
            text=testo,
            align='right',
            font_size = 0.8 * height
        )

        self.icona = arcade.load_texture(percorso_icona)
        self.testo = testo
        arcade.gui.bind(self, "testo", self.trigger_render)

        self.margine = margine
    
        self._label.x -= margine
        self._label.y += margine

    def aggiorna_testo(self, t):
        self.testo = t
    
    def do_render(self, surface: arcade.gui.Surface):

        self.prepare_render(surface)

        rect = arcade.LBWH(
            0,
            0, 
            self.content_width,
            self.content_height
        )

        arcade.draw_rect_filled(
            rect,
            (50, 50, 50)
        )
        arcade.draw_rect_outline(
            rect,
            arcade.color.WHITE,
            1
        )
        margine = self.content_height * self.margine
        
        arcade.draw_texture_rect(
            self.icona,
            arcade.LBWH(
                margine,
                margine,
                self.content_height - 2 * margine,
                self.content_height - 2 * margine
            )
        )

        self._label.text = self.testo

        if self._label.text[0] == '-':
            self._label.color = arcade.color.RED
        else:
            self._label.color = arcade.color.WHITE

        self._label.draw()

class BottoneArruola(arcade.gui.UIFlatButton):
    def __init__(self, width, height, text, interfaccia):
        super().__init__(
            width = width,
            height = height,
            text = text,
            size_hint = None
        )
        self.interfaccia = interfaccia

    # rende visible la barra e chiede quanti soldati spostare
    def on_event(self, event):
        if (isinstance(event, arcade.gui.UIMousePressEvent) and 
            self.interfaccia.dentro(event.x, event.y, self) and
            (self.interfaccia.provincia_selezionata != None or
            self.interfaccia.province_selezionate != [])
            ):
                self.interfaccia.input_arruola_soldati()

class BottoneMuovi(arcade.gui.UIFlatButton):
    def __init__(self, width, height, text, interfaccia):
        super().__init__(
            width = width,
            height = height,
            text = text,
            size_hint = None
        )
        self.interfaccia = interfaccia

    # rende visible la barra e chiede quanti soldati spostare
    def on_event(self, event):
        if (isinstance(event, arcade.gui.UIMousePressEvent) and 
            self.interfaccia.dentro(event.x, event.y, self) and
            (self.interfaccia.provincia_selezionata != None or
            self.interfaccia.province_selezionate != [])
            ):
                self.interfaccia.input_muovi_soldati()

class BottoneGuerra(arcade.gui.UIFlatButton):
    def __init__(self, width, height, text, interfaccia):
        super().__init__(
            width = width,
            height = height,
            text = text,
            size_hint = None
        )
        self.interfaccia = interfaccia

    def on_event(self, event):
        if (isinstance(event, arcade.gui.UIMousePressEvent) and
            self.interfaccia.dentro(event.x, event.y, self) and
            self.interfaccia.provincia_selezionata != None and
            self.interfaccia.provincia_selezionata.stato != self.interfaccia.stato and
            not self.interfaccia.provincia_selezionata.stato in self.interfaccia.stato.guerra
        ):
            self.interfaccia.stato.dichiara_guerra(self.interfaccia.provincia_selezionata.stato)

# Classe che contiene le funzioni principali per la gestione della GUI e alcune funzioni per dare ordini allo Stato del giocatore principale
class GestoreInterfaccia(arcade.gui.UIManager):

    def __init__(self, gioco):
        super().__init__()

        self.gioco = gioco
        self.province_precedenti = []
        self.soldati_da_muovere = 0
        self.stato = gioco.stati[0]
        self.prov_da_selezionare = self.stato.elenco_province[0]
        self.provincia_selezionata = None
        self.province_selezionate = []

        self.muovi = False
        self.arruola = False

        self.layout = self.add(arcade.gui.UIAnchorLayout())

        self.bottone_arruola = None
        self.bottone_muovi = None
        self.barra = None

        self.province_multiple = False

        self.setup()

    def setup(self):

        self.etichetta_soldi = Etichetta(
            180,
            40,
            0.1,
            '000 ',
            './assets/money.png'
        )

        self.bottone_arruola = BottoneArruola(
            120,
            50,
            'Arruola',
            self
        )
        self.bottone_muovi = BottoneMuovi(
            120,
            50,
            'Muovi',
            self
        )

        self.bottone_guerra = BottoneGuerra(
            120,
            50,
            'Dichiara guerra',
            self
        )

        self.barra = BarraProgressiva(
            0.5,
            400,
            30,
            arcade.color.RED,
            self
        )
    
        self.barra.visible = False

        self.layout.add(
            self.etichetta_soldi,
            anchor_x='left',
            anchor_y='top',
            align_x=50,
            align_y=-50
        )

        self.layout.add(
            self.bottone_arruola,
            anchor_x='right',
            anchor_y='bottom',
            align_x = -10,
            align_y = 10
        )

        self.layout.add(
            self.bottone_muovi,
            anchor_x='right',
            anchor_y='bottom',
            align_x = -10,
            align_y = 70
        ) 

        self.layout.add(
            self.bottone_guerra,
            anchor_x='right',
            anchor_y='bottom',
            align_x = -10,
            align_y = 130
        )

        self.layout.add(
            self.barra,
            anchor_x='center',
            anchor_y='bottom',
            align_y=20
        )

    def dentro(self, x, y, widget):
        return (
            x <= (widget.width + widget.position.x) and
            x >= widget.position.x and
            y <= (widget.height + widget.position.y) and
            y >= widget.position.y
        )

    # ritorna il numero di soldati che sta indicando la barra
    def soldati_barra(self, provincia):
        if self.arruola:
            return int(self.barra.value * self.stato.massimo_soldati(provincia))
        if self.muovi:
            return int(self.barra.value * provincia.soldati)

    # cambia la provincia selezionata dall'utente
    def cambia_provincia(self, direzione):
        provincia_precedente = self.provincia_selezionata
        if self.provincia_selezionata != None and not self.arruola:
            if direzione == NORDOVEST:
                self.prov_da_selezionare = self.provincia_selezionata.nordovest
            if direzione == NORDEST:
                self.prov_da_selezionare = self.provincia_selezionata.nordest
            if direzione == OVEST:
                self.prov_da_selezionare = self.provincia_selezionata.ovest
            if direzione == EST:
                self.prov_da_selezionare = self.provincia_selezionata.est
            if direzione == SUDEST:
                self.prov_da_selezionare = self.provincia_selezionata.sudest
            if direzione == SUDOVEST:
                self.prov_da_selezionare = self.provincia_selezionata.sudovest
            if self.prov_da_selezionare == None:
                self.prov_da_selezionare = provincia_precedente
        self.provincia_selezionata = self.prov_da_selezionare
        if self.muovi:
            self.muovi_esercito()
    
    # rende visible la barra e chiede quanti soldati spostare
    def input_muovi_soldati(self):
        province = [self.provincia_selezionata]
        if self.province_multiple:
            province = self.province_selezionate.copy()
        for p in province[:self.stato.punti_azione]:
            if not (p.stato == self.stato and
                self.stato.punti_azione > 0 and
                p.soldati > 0
                ):
                    return
        if self.barra.value == 0:
            self.barra.value = 1
        self.barra.visible = True
        self.bottone_muovi.visible = False
        self.bottone_arruola.visible = False
        self.muovi = True
        self.province_precedenti = province

    # chiede allo Stato di aggiungere un'azione per spostare una truppa
    def muovi_esercito(self):
        if not self.muovi:
            return
        for p in self.province_precedenti:
            soldati = int(self.barra.value * p.soldati)
            if (p != self.provincia_selezionata and
                (self.provincia_selezionata.stato in p.stato.guerra or
                self.provincia_selezionata.stato == self.stato) and
                soldati != 0
                ):
                self.stato.aggiungi_spostamento(soldati, p, self.provincia_selezionata)
                self.stato.renderizza_truppe()
        self.muovi = False
        self.province_precedenti = []
        self.barra.visible = False
        self.bottone_muovi.visible = True
        self.bottone_arruola.visible = True

    # rende visibile la barra e chiede quanti soldati arruolare
    def input_arruola_soldati(self):
        province = [self.provincia_selezionata]
        if self.province_multiple:
            province = self.province_selezionate.copy()
        for p in province:
            if p.stato != self.stato:
                return
            if p in self.stato.azioni:
                azione = None
                for az in self.stato.azioni[p]:
                    if az['azione'] == 'arruola':
                        azione = az
                        p.abitanti += az['soldati']
                        break
                if azione != None:
                    self.stato.punti_azione += 1
                    self.stato.azioni[p].remove(azione)
   
        if self.barra.value == 0:
            self.barra.value = 1
        self.barra.visible = True
        self.arruola = True
        self.bottone_muovi.visible = False
        self.bottone_arruola.visible = False

    # chiede allo Stato di aggiungere un'azione per arruolare dei soldati
    def arruola_soldati(self):
        if not self.arruola:
            return
        province = [self.provincia_selezionata]
        if self.province_multiple:
            province = self.province_selezionate.copy()
        for p in province:
            soldati = self.soldati_barra(p)
            if self.arruola and soldati != 0 and self.stato.punti_azione > 0:
                self.stato.arruola_soldati(soldati, p)
        self.stato.renderizza_truppe()
        self.arruola = False
        self.barra.visible = False
        self.bottone_arruola.visible = True
        self.bottone_muovi.visible = True

        self.province_multiple = False
        self.province_selezionate.clear()

    def resetta(self):
        self.barra.visible = False
        self.arruola = False
        self.muovi = False
        self.provincia_selezionata = None
        self.province_selezionate.clear()
        self.province_multiple = False
        self.bottone_arruola.visible = True
        self.bottone_muovi.visible = True