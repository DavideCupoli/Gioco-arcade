import arcade
import math
import random
from pyglet.graphics import Batch

# COSTANTI

# informazioni della finestra di gioco 
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Gioco di strategia"

MAPPA_RIGHE = 10
MAPPA_COLONNE = 10
RAGGIO = 30
NUM_STATI = 2
ABITANTI_PER_PROVINCIA = 5000
COSTO_SOLDATO = 10

FONT_SIZE_TRUPPE = 10

# velocità con cui si sposta la visuale
CAM_SPEED = 200

# di quanto aumenta/diminuisce lo zoom
ZOOM = 0.25
MAXIMUM_ZOOM = 1.5

# colori nel gioco usati dagli stati
COLORI_STATI = [
    arcade.color.RED,
    arcade.color.YELLOW,
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.CYAN,
    arcade.color.PURPLE,
    arcade.color.BROWN,
    arcade.color.GRAY,
    arcade.color.PINK,
    arcade.color.BLUE,
    arcade.color.CARIBBEAN_GREEN
]

# FUNZIONI MATEMATICHE/DI RENDERING

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
            x = (math.cos(math.radians(gradi)) * self.raggio) + self.centro_x
            y = (math.sin(math.radians(gradi)) * self.raggio) + self.centro_y
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

# DEFINIZIONE OGGETTI PRESENTI NEL GIOCO

class Stato:

    def __init__(self):

        self.elenco_province = []
        self.colore = None
        self.forma = None

        self.soldi = 1000
        # altri Stati con cui lo Stato è in guerra
        self.guerra = []

    # aggiorna i vertici che compongono la forma dello Stato (la linea del confine)
    def aggiorna_forma(self):
        
        # viene creato un mesh unico che unisce ogni esagono (ogni provincia) per rendere la renderizzazione più efficiente
        self.forma = arcade.shape_list.ShapeElementList()
        
        for i in self.elenco_province:
            punti = i.esagono.punti
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
        self.elenco_province.append(provincia)
        provincia.stato = self
        self.aggiorna_forma()

    # aggiunge allo Stato tutte le province confinanti non appartenenti a nessuno; ritorna le province aggiunte
    def espandi(self):

        province_aggiunte = 0
        massimo_province = 6
        prov_da_scegliere = self.elenco_province.copy()
        while len(prov_da_scegliere) > 0:
            p = random.choice(prov_da_scegliere)
            vicine = [
                p.est,
                p.ovest,
                p.nordest,
                p.nordovest,
                p.sudest,
                p.sudovest
            ]

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

    def mostra_truppe(self):
        batch = Batch()
        numeri = []
        for p in self.elenco_province:
            if p.soldati != 0: 
                numeri.append(arcade.Text(
                    str(p.soldati),
                    p.x - (p.raggio / 5 * 4),
                    p.y - (FONT_SIZE_TRUPPE / 2),
                    arcade.color.BLACK,
                    font_size = FONT_SIZE_TRUPPE,
                    width = (p.raggio * 2) / 5 * 4,
                    align = 'center',
                    batch = batch
                ))
        batch.draw()

class Provincia:

    def __init__(self, x, y, raggio):

        self.x = x
        self.y = y
        self.raggio = raggio
        self.stato = None
        self.esagono = Esagono(x, y, raggio)

        self.abitanti = ABITANTI_PER_PROVINCIA
        self.soldati = 100

        # province vicine
        self.est = None
        self.ovest = None
        self.nordest = None
        self.nordovest = None
        self.sudest = None
        self.sudovest = None

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

class GestoreInterfaccia:

    def __init__(self, stato_player, provincia_selezionata):
        self.muovi_soldati = False
        self.provincia_precedente = None
        self.soldati_da_muovere = 0
        self.stato = stato_player
        self.provincia_selezionata = provincia_selezionata

    def input_muovi_soldati(self):
        if self.muovi_soldati:
            self.muovi_soldati = False
            return
        self.muovi_soldati = True
        soldati = int(input('Quanti soldati muovere? '))
        if soldati > self.provincia_selezionata.soldati:
            print(f'Numero soldati selezionato maggiore a soldati presenti ({self.provincia_selezionata.soldati})')
            self.muovi_soldati = False
        if soldati < 0:
            print('Numero minore di 0')
            self.muovi_soldati = False
        else:
            self.soldati_da_muovere = soldati
            self.provincia_precedente = self.provincia_selezionata

    def muovi_esercito(self):
        if self.muovi_soldati and (self.provincia_selezionata.stato == self.stato or self.provincia_selezionata.stato in self.stato.guerra):
            self.provincia_selezionata.soldati += self.soldati_da_muovere
            self.provincia_precedente.soldati -= self.soldati_da_muovere
            self.soldati_da_muovere = 0
            self.muovi_soldati = False
            self.provincia_precedente = None
   
    def input_arruola_soldati(self):
        soldati = int(input(f'Quanti soldati arruolare (Costo di un soldato: {COSTO_SOLDATO})? '))
        if soldati > self.provincia_selezionata.abitanti / 4:
            print(f'Numero di soldati oltre {int(provincia_selezionata.abitanti / 4)}')
        elif self.stato.soldi < COSTO_SOLDATO * soldati:
            print(f'Soldi insufficienti. Richiesti: {COSTO_SOLDATO * soldati}')
        else:
            self.provincia_selezionata.soldati += soldati
            self.stato.soldi -= COSTO_SOLDATO * soldati

# CLASSE PRINCIPALE

class GameView(arcade.View):

    # inizializzazione oggetti principali
    def __init__(self):

        super().__init__()

        # colore sfondo
        self.background_color = arcade.color.AMAZON
        
        # inizializzazione mappa
        self.mappa = Mappa()
        self.mappa.crea_province(MAPPA_RIGHE, MAPPA_COLONNE, RAGGIO)

        # lista di tutti gli Stati nel gioco
        self.stati = []

        # inizializzazione della visuale (camera) nel gioco
        self.camera = arcade.Camera2D(position=(0, 0), zoom=1)

        # direzione verso cui si muove la visuale
        self.cam_direction = [0, 0]

        self.provincia_selezionata = self.mappa.province[0][0]
        print(self.provincia_selezionata)

        # colori che possono essere scelti dagli stati
        self.colori_stati_disponibili = COLORI_STATI.copy()

        self.aggiungi_stati(NUM_STATI)
        self.espandi_stati()

        self.stato_player = self.stati[0]

        self.gestore = GestoreInterfaccia(self.stato_player, self.provincia_selezionata)

    # cambia la provincia selezionata dall'utente
    def cambia_provincia(self, provincia):
        if provincia != None:
            self.provincia_selezionata = provincia
            self.gestore.provincia_selezionata = provincia
        self.gestore.muovi_esercito()

    # aggiunge un certo numero di Stati alla lista stati, impostando il colore e aggiungendo una provincia con una posizione casuale
    def aggiungi_stati(self, n_stati):
        for i in range(n_stati):
            stato = Stato()
            self.colori_stati_disponibili = stato.scegli_colore(self.colori_stati_disponibili)

            num_righe = len(self.mappa.province)
            num_colonne = len(self.mappa.province[0])

            r = random.randint(0, num_righe - 1)
            c = random.randint(0, num_colonne - 1)
            provincia = self.mappa.province[r][c]
            stato.aggiungi_provincia(provincia)
            self.stati.append(stato)

    # gli stati si espandono a turno
    def espandi_stati(self):

        province = len(self.mappa.province) * len(self.mappa.province[0]) - len(self.stati)
        i = 0
        while province > 0:
            province -= self.stati[i % len(self.stati)].espandi()
            i += 1

    def reset(self):
        """Reset the game to the initial state."""
        # Do changes needed to restart the game here if you want to support that
        pass

    def on_draw(self):
        """
        Render the screen.
        """

        # pulisce lo schermo
        self.clear()

        # disegna i soldi dello stato
        arcade.draw_text(
            f'Soldi: {self.stato_player.soldi}',
            50,
            WINDOW_HEIGHT - 50
        )

        # utilizza la posizione della camera per disegnare le figure sullo schermo
        with self.camera.activate():
    
            for i in self.stati:
                i.disegna()

            # disegna gli esagoni che delimitano le province
            self.mappa.disegna_scacchiera()

            # disegna la provincia selezionata
            punti = self.provincia_selezionata.esagono.punti
            arcade.draw_polygon_filled(punti, arcade.color.WHITE)

            self.stato_player.mostra_truppe()

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
       
        if key == arcade.key.M:
            self.gestore.input_muovi_soldati()
        if key == arcade.key.N:
            self.gestore.input_arruola_soldati()

        # cambia lo zoom
        if key == arcade.key.NUM_ADD and self.camera.zoom < MAXIMUM_ZOOM:
            self.camera.zoom += ZOOM
        if key == arcade.key.NUM_SUBTRACT and self.camera.zoom > ZOOM:
            self.camera.zoom -= ZOOM

        # cambia la provincia selezionata
        if key == arcade.key.W:
            self.cambia_provincia(self.provincia_selezionata.nordovest)
        if key == arcade.key.E:
            self.cambia_provincia(self.provincia_selezionata.nordest)
        if key == arcade.key.A:
            self.cambia_provincia(self.provincia_selezionata.est)
        if key == arcade.key.F:
            self.cambia_provincia(self.provincia_selezionata.ovest)
        if key == arcade.key.S:
            self.cambia_provincia(self.provincia_selezionata.sudovest)
        if key == arcade.key.D:
            self.cambia_provincia(self.provincia_selezionata.sudest)

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
