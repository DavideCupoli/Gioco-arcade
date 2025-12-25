import arcade
import arcade.gui
import threading

COSTO_SOLDATO = 10
TASSO_ARRUOLAMENTO = 0.1

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
            return int(self.barra.value * min(self.stato.soldi / COSTO_SOLDATO, self.provincia_selezionata.abitanti * TASSO_ARRUOLAMENTO))

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
            self.provincia_precedente.soldati -= soldati 
            self.stato.punti_azione -= 1
            # aggiungi azioni
            self.provincia_precedente.azioni.append({
                'azione': 'muovi',
                'destinazione': self.provincia_selezionata,
                'soldati': soldati
            })
            self.provincia_selezionata.azioni.append({
                'azione': 'arrivo truppe',
                'soldati': soldati,
                'origine': self.provincia_precedente
            })
        self.muovi_soldati = False
        self.provincia_precedente = None
        self.barra.value = 0
        self.barra.visible = False

    def input_arruola_soldati(self):
        for azione in self.provincia_selezionata.azioni:
            if azione['azione'] == 'arruola':
                return
        if self.gioco.turno_stato == 0 and self.provincia_selezionata.stato == self.stato and self.stato.punti_azione != 0:
            self.barra.value = 0.5
            self.barra.visible = True
            self.arruola = True

    def arruola_soldati(self):
        if self.arruola:
            soldati = self.soldati_barra()
            if soldati != 0:
                self.stato.soldi -= COSTO_SOLDATO * soldati
                self.provincia_selezionata.abitanti -= soldati
                self.arruola = False
                self.barra.value = 0
                self.barra.visible = False
                self.stato.punti_azione -= 1
                # aggiungi azioni
                self.provincia_selezionata.azioni.append({
                    'azione': 'arruola',
                    'soldati': soldati
                })

    '''
    def cancella_azione(self):
        if len(self.provincia_selezionata.azioni) != 0 and self.provincia_selezionata.stato == self.stato:
            azione = self.provincia_selezionata.azioni.pop()
            if azione['azione'] == 'muovi':
                destinazione = azione['destinazione']
                for azione in destinazione.azioni:
                    if azione['azione'] == 'arrivo truppe' and azione['origine'] == self.provincia_selezionata:
                        destinazione.azioni.remove(azione)
                        break
            if azione['azione'] == 'arrivo truppe':
                origine = azione['origine']
                for azione in origine.azioni:
                    if azione['azione'] == 'muovi' and azione['destinazione'] == self.provincia_selezionata:
                        origine.azioni.remove(azione)
                        break                  
            if azione['soldati'] != 0:
                self.stato.punti_azione += 1
            print('Rimossa azione ' + azione)
    '''
