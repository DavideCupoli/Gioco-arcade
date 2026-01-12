import arcade
import random
from matematica import *
from ui import *
from oggetti import *
from costanti import *

# ESECUZIONE AZIONI

# vengono eseguiti gli ordini dello Stato, controllando ogni sua provincia
def esegui_azioni(stato):
    for p in stato.elenco_province:
        if len(p.azioni) > 0:
            for azione in p.azioni:
                if azione['azione'] == 'arruola':
                    p.soldati += azione['soldati']
                if azione['azione'] == 'muovi':
                    destinazione = azione['destinazione']
                    soldati = azione['soldati']
                    if destinazione.stato == stato:
                        destinazione.soldati += soldati
                    else:
                        if destinazione.soldati < soldati:
                            stato.aggiungi_provincia(destinazione)
                        destinazione.soldati = int(
                            math.fabs(
                                destinazione.soldati - soldati
                            )
                        )
                    for a in azione['destinazione'].azioni:
                        if a['azione'] == 'arrivo truppe' and a['stato'] == stato:
                            azione['destinazione'].azioni.remove(a)
                            break
                            
            p.azioni = []

# GESTIONE BOT

# Questa classe costituisce un thread, che viene chiamato ogni volta che i BOT devono prendere delle decisioni
class GestoreDecisioni(threading.Thread):
    def __init__(self, gioco):
        super().__init__()
        self.gioco = gioco
        
    def run(self):
        while self.gioco.turno_stato != 0:
            stato = self.gioco.stati[self.gioco.turno_stato]
            stato.punti_azione = PUNTI_AZIONE
            confini = stato.ottieni_confini(False)
            random.shuffle(confini)
            if len(confini) != 0:
                for i in range(stato.punti_azione // 2):
                    provincia = random.choice(confini)  
                    soldati = int(min(stato.soldi / COSTO_SOLDATO, provincia.abitanti * TASSO_ARRUOLAMENTO))
                    stato.arruola_soldati(soldati, provincia)
                for p in confini:
                    if p.soldati > 0:
                        vicine = p.province_vicine()
                        prov_confinanti = []
                        for v in vicine:
                            if v != None and v.stato != stato:
                                prov_confinanti.append(v)
                        soldati = int(p.soldati / len(prov_confinanti))
                        for c in prov_confinanti:
                            if stato.punti_azione > 0:
                                stato.muovi_soldati(soldati, p, c)
                            else:
                                break

            esegui_azioni(stato)
            self.gioco.turno_stato += 1
            if self.gioco.turno_stato == len(self.gioco.stati):
                self.gioco.turno_stato = 0

# CLASSE PRINCIPALE

class GameView(arcade.View):

    # inizializzazione oggetti principali
    def __init__(self):

        super().__init__()

        # colore sfondo
        self.background_color = arcade.color.BLACK
        
        # inizializzazione mappa
        self.mappa = Mappa()
        self.mappa.crea_province(MAPPA_RIGHE, MAPPA_COLONNE, RAGGIO)

        # lista di tutti gli Stati nel gioco
        self.stati = []

        # inizializzazione della visuale (camera) nel gioco
        self.camera = arcade.Camera2D(position=(0, 0), zoom=1)

        # direzione verso cui si muove la visuale
        self.cam_direction = [0, 0]
        # colori che possono essere scelti dagli stati
        self.colori_stati_disponibili = COLORI_STATI.copy()

        self.aggiungi_stati(NUM_STATI)
        self.espandi_stati()

        self.stato_player = self.stati[0]

        self.interfaccia = GestoreInterfaccia(self)
       
        self.turno_stato = 0
        self.bot = None

        self.modalita_truppe = 1
        
        self.indice_truppe = 0

    # viene chiamato un nuovo thread
    def nuovo_thread(self):
        self.bot = GestoreDecisioni(self)
        self.bot.start()
        #self.bot.join()

    # aggiunge un certo numero di Stati alla lista stati, impostando il colore e aggiungendo una provincia con una posizione casuale
    def aggiungi_stati(self, n_stati):
        for i in range(n_stati):
            stato = Stato()
            self.colori_stati_disponibili = stato.scegli_colore(self.colori_stati_disponibili)

            num_righe = len(self.mappa.province)
            num_colonne = len(self.mappa.province[0])

            r = None
            c = None
            
            posizione_valida = False

            while not posizione_valida:
                r = random.randint(0, num_righe - 1)
                c = random.randint(0, num_colonne - 1)
                for s in self.stati:
                    if s.elenco_province[0] != self.mappa.province[r][c]:
                        posizione_valida = True
                        break
                    else:
                        print(r, c)

                posizione_valida |= len(self.stati) == 0
                        
            provincia = self.mappa.province[r][c]
            stato.aggiungi_provincia(provincia)
            self.stati.append(stato)

    # gli stati si espandono a turno
    def espandi_stati(self):

        province = len(self.mappa.province) * len(self.mappa.province[0]) - len(self.stati)
        i = 0
        while province > 0:
            p = self.stati[i % len(self.stati)].espandi()
            province -= p
            i += 1

    def reset(self):
        """Reset the game to the initial state."""
        # Do changes needed to restart the game here if you want to support that
        pass

    # funzione chiamata ad ogni frame per la renderizzazione
    def on_draw(self):
    
        self.clear()

        # utilizza la posizione della camera per disegnare le figure sullo schermo
        with self.camera.activate():
    
            for i in self.stati:
                i.disegna()

            # disegna gli esagoni che delimitano le province
            self.mappa.disegna_scacchiera()

            # disegna la provincia selezionata
            punti = self.interfaccia.provincia_selezionata.esagono.punti
            arcade.draw_polygon_filled(punti, arcade.color.WHITE)

            self.stati[self.indice_truppe].mostra_truppe()

        # disegna i soldi dello stato
        arcade.draw_text(
            f'Soldi: {self.stato_player.soldi}',
            50,
            WINDOW_HEIGHT - 50
        )

        arcade.draw_text(
            f'Punti azione: {self.stato_player.punti_azione}',
            50,
            WINDOW_HEIGHT - 100
        )
        
        if self.interfaccia.muovi_soldati or self.interfaccia.arruola:
            arcade.draw_text(
                f'Soldati: {self.interfaccia.soldati_barra()}',
                50,
                WINDOW_HEIGHT - 150
            )

        self.interfaccia.draw()

    def on_show_view(self):
        self.interfaccia.enable()
    
    def on_hide_view(self):
        self.interfaccia.disable()

    def on_update(self, delta_time):

        # aggiorna la posizione della camera
        self.camera.position = (
            self.camera.position[0] + (self.cam_direction[0] * delta_time * CAM_SPEED / self.camera.zoom),
            self.camera.position[1] + (self.cam_direction[1] * delta_time * CAM_SPEED / self.camera.zoom)
        )

    def on_key_press(self, key, key_modifiers):

        # cambia la direzione verso cui si sposta la camera
        if key == arcade.key.UP:
            self.cam_direction[1] = 1
        if key == arcade.key.DOWN:
            self.cam_direction[1] = -1
        if key == arcade.key.LEFT:
            self.cam_direction[0] = -1
        if key == arcade.key.RIGHT:
            self.cam_direction[0] = 1

        # principali comandi con cui si dànno ordini
        if key == arcade.key.M:
            self.interfaccia.input_muovi_soldati()
        if key == arcade.key.N:
            self.interfaccia.input_arruola_soldati()
        if key == arcade.key.ENTER:
            self.interfaccia.arruola_soldati()
        
        # passare da un turno all'altro
        if key == arcade.key.SPACE and self.turno_stato == 0:
            esegui_azioni(self.stato_player)
            self.stato_player.punti_azione = PUNTI_AZIONE
            self.turno_stato += 1
            self.nuovo_thread()
        # vedere le truppe di un altro Stato
        if key == arcade.key.X:
            self.indice_truppe = (self.indice_truppe + 1) % len(self.stati)

        # cambia lo zoom
        if key == arcade.key.NUM_ADD and self.camera.zoom < MAXIMUM_ZOOM:
            self.camera.zoom += ZOOM
        if key == arcade.key.NUM_SUBTRACT and self.camera.zoom > ZOOM:
            self.camera.zoom -= ZOOM

        # cambia la provincia selezionata
        if key == arcade.key.W:
            self.interfaccia.cambia_provincia(self.interfaccia.provincia_selezionata.nordovest)
        if key == arcade.key.E:
            self.interfaccia.cambia_provincia(self.interfaccia.provincia_selezionata.nordest)
        if key == arcade.key.A:
            self.interfaccia.cambia_provincia(self.interfaccia.provincia_selezionata.est)
        if key == arcade.key.F:
            self.interfaccia.cambia_provincia(self.interfaccia.provincia_selezionata.ovest)
        if key == arcade.key.S:
            self.interfaccia.cambia_provincia(self.interfaccia.provincia_selezionata.sudovest)
        if key == arcade.key.D:
            self.interfaccia.cambia_provincia(self.interfaccia.provincia_selezionata.sudest)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        # la camera non si sposta più quando vengono rilasciati i tasti delle frecce
        if key == arcade.key.UP:
            self.cam_direction[1] = 0
        elif key == arcade.key.DOWN:
            self.cam_direction[1] = 0
        elif key == arcade.key.LEFT:
            self.cam_direction[0] = 0
        elif key == arcade.key.RIGHT:
            self.cam_direction[0] = 0

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass

def main():
    """ Main function """

    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()

if __name__ == "__main__":
    main()
