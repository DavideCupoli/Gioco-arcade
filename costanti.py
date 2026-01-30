import arcade

# informazioni legate al gioco

MAPPA_RIGHE = 30
MAPPA_COLONNE = 30
RAGGIO = 30
NUM_STATI = 10

PUNTI_AZIONE = 10
FONT_SIZE_TRUPPE = 8
ABITANTI_PER_PROVINCIA = 10000
SOLDI = 0
TASSO_ARRUOLAMENTO = 0.1
PRODUZIONE_PER_ABITANTE = 0.005
COSTO_MANTENIMENTO_SOLDATO = 0.2
COSTO_SOLDATO = 0.25
CRESCITA_POPOLAZIONE = 1

# informazioni della finestra di gioco 
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 600
#WINDOW_WIDTH = 400
#WINDOW_HEIGHT = 333
WINDOW_TITLE = "The Age of Conquests"

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

# direzioni

NORDOVEST = 0
NORDEST = 1
EST = 2
OVEST = 3
SUDOVEST = 4
SUDEST = 5
