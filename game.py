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

def gestisci_bot(gioco):
    if len(gioco.stati) == 1:
        gioco.turno_stato = 0
        return
    while gioco.turno_stato != 0:
        stato = gioco.stati[gioco.turno_stato]
        confini = stato.ottieni_confini(False)
        random.shuffle(confini)
        if len(confini) != 0:
            for i in range(stato.punti_azione // 2):
                provincia = random.choice(confini)  
                soldati = int(max(0, min(0.4, random.random()) * stato.massimo_soldati(provincia)))
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
                            stato.aggiungi_spostamento(soldati, p, c)
                        else:
                            break

        gioco.nuovo_turno(stato)
        if len(stato.elenco_province) == 0:
            gioco.stati.remove(stato)
            gioco.turno_stato -= 1
        if gioco.turno_stato == len(gioco.stati):
            gioco.turno_stato = 0

# CLASSE PRINCIPALE

class GameView(arcade.View):

    # inizializzazione oggetti principali
    def __init__(self):

        super().__init__()

        # colore sfondo
        self.background_color = arcade.color.BLACK
        
        # inizializzazione mappa
        self.mappa = Mappa(MAPPA_RIGHE, MAPPA_COLONNE, RAGGIO)
        self.mappa.crea_province()

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

        # indice di uno stato nella lista_stati dove vengono mostrate le truppe
        self.indice_truppe = 0

        # quanti fps fa il gioco
        self.fps = 0
        self.num_updates = 0
        # tempo di aggiornamento bot
        self.fps_time = 0
        
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

                posizione_valida |= len(self.stati) == 0
                        
            provincia = self.mappa.province[r][c]
            stato.aggiungi_provincia(provincia)
            self.stati.append(stato)

            if i == 0:
                self.camera.position = self.camera.project(
                    (stato.elenco_province[0].x - (WINDOW_WIDTH / 2),
                    stato.elenco_province[0].y - (WINDOW_HEIGHT / 2))
                )

    # gli stati si espandono a turno
    def espandi_stati(self):

        province = len(self.mappa.province) * len(self.mappa.province[0]) - len(self.stati)
        i = 0
        while province > 0:
            p = self.stati[i % len(self.stati)].espandi()
            province -= p
            i += 1
    
        for i in self.stati:
            i.aggiorna_forma()

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

            # disegna la provincia da selezionare
            punti = self.interfaccia.prov_da_selezionare.esagono.punti
            arcade.draw_polygon_outline(punti, arcade.color.BLACK, 2)
            
            # disegna la provincia selezionata (se non è nulla)
            province = [self.interfaccia.provincia_selezionata]
            if self.interfaccia.province_multiple:
                province = self.interfaccia.province_selezionate
            for p in province:
                if p != None:
                    punti = p.esagono.punti
                    arcade.draw_polygon_outline(punti, arcade.color.WHITE, 3)
            
            self.stati[self.indice_truppe].mostra_truppe()

        arcade.draw_lbwh_rectangle_filled(
            50,
            50,
            50,
            50,
            self.stati[0].colore
        )
        arcade.draw_lbwh_rectangle_outline(
            50,
            50,
            50,
            50,
            arcade.color.BLACK,
            2
        )

        # disegna i soldi dello stato selezionato
        arcade.draw_text(
            f'Soldi: {format(self.stati[self.indice_truppe].soldi, ",")}',
            50,
            WINDOW_HEIGHT - 50
        )

        arcade.draw_text(
            f'Punti azione: {self.stato_player.punti_azione}',
            50,
            WINDOW_HEIGHT - 100
        )

        arcade.draw_text(
            f'FPS: {int(self.fps)}',
            WINDOW_WIDTH - 100,
            WINDOW_HEIGHT - 50,
        )
        
        if self.interfaccia.muovi or self.interfaccia.arruola:
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

        if self.fps_time >= 1:
            self.fps = self.num_updates
            self.fps_time = 0
            self.num_updates = 0

        self.fps_time += delta_time
        self.num_updates += 1

    def nuovo_turno(self, stato):
        esegui_azioni(stato)
        stato.aggiungi_azioni_spostamenti(stato.spostamenti_truppe)
        stato.aggiorna_statistiche()
        stato.punti_azione = PUNTI_AZIONE
        self.turno_stato += 1
        
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
            if self.interfaccia.provincia_selezionata != None:
                self.interfaccia.input_muovi_soldati()
        if key == arcade.key.N:
            if self.interfaccia.provincia_selezionata != None:
                self.interfaccia.input_arruola_soldati()
        if key == arcade.key.ENTER:
            self.interfaccia.arruola_soldati()
        
        # passare da un turno all'altro
        if key == arcade.key.SPACE and self.turno_stato == 0:
            self.interfaccia.resetta()

            self.nuovo_turno(self.stato_player)
            gestisci_bot(self)
            self.stati[self.indice_truppe].renderizza_truppe()
            
            for i in self.stati:
                i.aggiorna_forma()

        # vedere le truppe di un altro Stato
        if key == arcade.key.X:
            self.indice_truppe = (self.indice_truppe + 1) % len(self.stati)
            self.stati[self.indice_truppe].renderizza_truppe()

        # cambia lo zoom
        if key == arcade.key.PLUS and self.camera.zoom < MAXIMUM_ZOOM:
            self.camera.zoom += ZOOM
        if key == arcade.key.MINUS and self.camera.zoom >= ZOOM * 2:
            self.camera.zoom -= ZOOM

        # cambia la provincia selezionata
        if key == arcade.key.W:
            self.interfaccia.cambia_provincia(NORDOVEST)
        if key == arcade.key.E:
            self.interfaccia.cambia_provincia(NORDEST)
        if key == arcade.key.A:
            self.interfaccia.cambia_provincia(EST)
        if key == arcade.key.F:
            self.interfaccia.cambia_provincia(OVEST)
        if key == arcade.key.S:
            self.interfaccia.cambia_provincia(SUDOVEST)
        if key == arcade.key.D:
            self.interfaccia.cambia_provincia(SUDEST)
        
        # cambia valore della barra
        if key == arcade.key.KEY_0:
            self.interfaccia.barra.value = 0
        if key == arcade.key.KEY_1:
            self.interfaccia.barra.value = 1
        if key == arcade.key.KEY_2:
            self.interfaccia.barra.value = 1 / 2
        if key == arcade.key.KEY_3:
            self.interfaccia.barra.value = 1 / 3
        if key == arcade.key.KEY_4:
            self.interfaccia.barra.value = 1 / 4

        # passa a modalità province_multiple
        if key == arcade.key.MOD_SHIFT:
            self.interfaccia.province_multiple = True

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

        # disattiva modalità province_multiple
        if key == arcade.key.MOD_SHIFT:
            self.interfaccia.province_multiple = False

    def seleziona_provincia(self, x, y):

        pos = self.camera.unproject((x, y))
            
        prov = self.mappa.trova_provincia(pos[0], pos[1])

        for p in [prov, prov.sudest, prov.sudovest]:
            if p != None and p.esagono.dentro(pos[0], pos[1]):
                self.interfaccia.prov_da_selezionare = p

    def on_mouse_motion(self, x, y, delta_x, delta_y):

        if (not self.interfaccia.arruola and
            not self.interfaccia.dentro(x, y, self.interfaccia.bottone_muovi) and
            not self.interfaccia.dentro(x, y, self.interfaccia.bottone_arruola) and
            not self.interfaccia.dentro(x, y, self.interfaccia.barra)
            ):
            self.seleziona_provincia(x, y)

    def on_mouse_press(self, x, y, button, key_modifiers):
        
        if (not self.interfaccia.arruola and
            not self.interfaccia.dentro(x, y, self.interfaccia.bottone_muovi) and
            not self.interfaccia.dentro(x, y, self.interfaccia.bottone_arruola) and
            not self.interfaccia.dentro(x, y, self.interfaccia.barra)
            ):
            self.interfaccia.provincia_selezionata = self.interfaccia.prov_da_selezionare
            if self.interfaccia.muovi:
                self.interfaccia.muovi_esercito()
     
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
