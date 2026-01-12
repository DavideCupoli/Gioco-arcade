import arcade

# informazioni della finestra di gioco 
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 680
WINDOW_TITLE = "Gioco di strategia"

MAPPA_RIGHE = 10
MAPPA_COLONNE = 10
RAGGIO = 30
NUM_STATI = 3

# velocità con cui si sposta la visuale
CAM_SPEED = 200

# di quanto aumenta/diminuisce lo zoom
ZOOM = 0.10
MAXIMUM_ZOOM = 1.5

# colori nel gioco usati dagli stati
COLORI_STATI = [
    arcade.color.RED,
    arcade.color.YELLOW,
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.CYAN,
    arcade.color.PURPLE,
    arcade.color.BROWN, arcade.color.GRAY,
    arcade.color.PINK,
    arcade.color.BLUE,
    arcade.color.CARIBBEAN_GREEN
]

# informazioni legate al gioco
PUNTI_AZIONE = 10
FONT_SIZE_TRUPPE = 8
ABITANTI_PER_PROVINCIA = 10000
SOLDI = 100000000000
COSTO_SOLDATO = 10
TASSO_ARRUOLAMENTO = 0.1
