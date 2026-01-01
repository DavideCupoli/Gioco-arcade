import arcade
import arcade.gui
import threading

# GESTIONE INTERFACCIA

class BarraProgressiva(arcade.gui.UIWidget):
    value = arcade.gui.Property(0.0)
    """The fill level of the progress bar. A value between 0 and 1."""

    def __init__(
        self,
        value,
        width,
        height,
        color
    ):
        super().__init__(
            width = width,
            height = height,
            size_hint = None,  # disable size hint, so it just uses the size given
        )
        self.with_background(color=arcade.uicolor.WHITE)
        self.with_border(color=arcade.uicolor.GRAY_CONCRETE)

        self.value = value
        self.color = color

        # trigger a render when the value changes
        arcade.gui.bind(self, "value", self.trigger_render)

    def on_event(self, event):
        if str(event.__class__).find('UIMousePressEvent') != -1: 
            if event.y > self.position.y and event.y - self.position.y < self.height:
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

class GestoreInterfaccia(arcade.gui.UIManager):

    def __init__(self, gioco):
        super().__init__()

        self.gioco = gioco
        self.muovi_soldati = False
        self.provincia_precedente = None
        self.soldati_da_muovere = 0
        self.stato = gioco.stato_player
        self.provincia_selezionata = gioco.mappa.province[0][0]
        self.arruola = False

        layout = self.add(arcade.gui.UIAnchorLayout())

        self.barra = BarraProgressiva(
            0.5,
            400,
            20,
            arcade.color.RED
        )
        self.barra.visible = False

        layout.add(self.barra, anchor_x='center', anchor_y='bottom', align_y=20)

    def soldati_barra(self):
        if self.muovi_soldati:
            return int(self.provincia_precedente.soldati * self.barra.value)
        if self.arruola:
            return int(self.barra.value * min(self.stato.soldi / self.stato.costo_soldato, self.provincia_selezionata.abitanti * self.stato.tasso_arruolamento))

    # cambia la provincia selezionata dall'utente
    def cambia_provincia(self, provincia):
        if provincia != None:
            self.provincia_selezionata = provincia
        self.muovi_esercito()
    
    def input_muovi_soldati(self):
        if self.gioco.turno_stato == 0 and self.provincia_selezionata.stato == self.stato and self.stato.punti_azione != 0:
            self.barra.value = 1
            self.barra.visible = True
            self.muovi_soldati = True
            self.provincia_precedente = self.provincia_selezionata

    def muovi_esercito(self):
        soldati = self.soldati_barra()
        if self.muovi_soldati and self.provincia_precedente != self.provincia_selezionata and soldati != 0:
            self.stato.muovi_soldati(soldati, self.provincia_precedente, self.provincia_selezionata)
        self.muovi_soldati = False
        self.provincia_precedente = None
        self.barra.value = 0
        self.barra.visible = False

    def input_arruola_soldati(self):
        for azione in self.provincia_selezionata.azioni:
            if azione['azione'] == 'arruola':
                return
        if self.gioco.turno_stato == 0 and self.provincia_selezionata.stato == self.stato and self.stato.punti_azione != 0:
            self.barra.value = 1
            self.barra.visible = True
            self.arruola = True

    def arruola_soldati(self):
        soldati = self.soldati_barra()
        if self.arruola and soldati:
            self.stato.arruola_soldati(soldati, self.provincia_selezionata)
            self.arruola = False
            self.barra.value = 0
            self.barra.visible = False

