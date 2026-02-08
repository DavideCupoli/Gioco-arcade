import arcade
import arcade.gui
from costanti import *

# GESTIONE INTERFACCIA

# Widget per spostare/arruolare un certo numero di soldati
class BarraProgressiva(arcade.gui.UIWidget):
    value = arcade.gui.Property(0.0)

    def __init__(
        self,
        value,
        width,
        height,
        color,
        interfaccia
    ):
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
        if str(event.__class__).find('UIMousePressEvent') != -1 and self.interfaccia.dentro(event.x, event.y, self):
            self.value = max(0, min(1, (event.x - self.position.x) / self.width))
        if str(event.__class__).find('UIMouseDragEvent') != -1: 
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
        if (str(event.__class__).find('UIMousePressEvent') != -1 and 
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
        if (str(event.__class__).find('UIMousePressEvent') != -1 and 
            self.interfaccia.dentro(event.x, event.y, self) and
            self.interfaccia.provincia_selezionata != None):
                self.interfaccia.input_muovi_soldati()

# Classe che contiene le funzioni principali per la gestione della GUI e alcune funzioni per dare ordini allo Stato del giocatore principale
class GestoreInterfaccia(arcade.gui.UIManager):

    def __init__(self, gioco):
        super().__init__()

        self.gioco = gioco
        self.provincia_precedente = None
        self.soldati_da_muovere = 0
        self.stato = gioco.stato_player
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

        self.bottone_arruola = BottoneArruola(
            100,
            50,
            'Arruola',
            self
        )
        self.bottone_muovi = BottoneMuovi(
            100,
            50,
            'Muovi',
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

    # ritorna il numero di soldati che sta indicando la barra (prendendo in considerazione le condizioni della provincia, i soldi ecc.)
    def soldati_barra(self, provincia):
        if self.muovi:
            return int(self.provincia_precedente.soldati * self.barra.value)
        if self.arruola:
            return int(self.barra.value * self.stato.massimo_soldati(provincia))

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
        if (self.provincia_selezionata.stato == self.stato and
            self.stato.punti_azione != 0 and
            self.provincia_selezionata.soldati != 0):
            if self.barra.value == 0:
                self.barra.value = 1
            self.barra.visible = True
            self.bottone_muovi.visible = False
            self.bottone_arruola.visible = False
            self.muovi = True
            self.provincia_precedente = self.provincia_selezionata

    # chiede allo Stato di aggiungere un'azione per spostare una truppa
    def muovi_esercito(self):
        soldati = self.soldati_barra(self.provincia_selezionata)
        if (self.muovi and
            self.provincia_precedente != self.provincia_selezionata and
            soldati != 0
            ):
            self.stato.aggiungi_spostamento(soldati, self.provincia_precedente, self.provincia_selezionata)
            self.stato.renderizza_truppe()
        self.muovi = False
        self.provincia_precedente = None
        self.barra.visible = False
        self.bottone_muovi.visible = True
        self.bottone_arruola.visible = True

    # rende visibile la barra e chiede quanti soldati arruolare
    def input_arruola_soldati(self):
        if self.barra.value == 0:
            self.barra.value = 1
        self.barra.visible = True
        self.arruola = True
        self.bottone_muovi.visible = False
        self.bottone_arruola.visible = False

    # chiede allo Stato di aggiungere un'azione per arruolare dei soldati
    def arruola_soldati(self):
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

    def resetta(self):
        self.barra.visible = False
        self.arruola = False
        self.muovi = False
        self.provincia_selezionata = None
        self.province_selezionate.clear()
        self.province_multiple = False
        self.bottone_arruola.visible = True
        self.bottone_muovi.visible = True
