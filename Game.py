"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade
import math

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Starting Template"

class Provincia:

    def __init__(self, x, y, raggio):
        self.x = x
        self.y = y
        self.raggio = raggio

        self.est = None
        self.ovest = None
        self.nordest = None
        self.nordovest = None
        self.sudest = None
        self.sudovest = None

class Mappa:
    def __init__(self):

        self.province = []

    # modifica la lista 'province'
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
            
    def disegna(self):

        for i in self.province:
            for j in i:
                arcade.draw_polygon_outline(
                    punti_esagono(
                        j.x,
                        j.y,
                        j.raggio
                    ),
                    arcade.color.RED
                )
        
def punti_esagono(cx, cy, r):
    """
    Restituisce la lista dei punti (x, y) che formano un esagono regolare
    centrato in (cx, cy) con raggio r.
    L'angolo 0° è sulla destra e i vertici proseguono in senso antiorario.
    """
    punti = []
    for i in range(6):
        angolo = math.radians(60 * i + 90)  # 6 lati → 360/6 = 60°
        x = cx + r * math.cos(angolo)
        y = cy + r * math.sin(angolo)
        punti.append((x, y))
    return punti


class GameView(arcade.View):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.AMAZON
        
        self.mappa = Mappa()
        self.mappa.crea_province(10, 10, 20)

        self.camera = arcade.Camera2D(position=(-100, -100), zoom=1)

        self.cam_direction = [0, 0]

        self.provincia_selezionata = self.mappa.province[0][0]

        # If you have sprite lists, you should create them here,
        # and set them to None

    def reset(self):
        """Reset the game to the initial state."""
        # Do changes needed to restart the game here if you want to support that
        pass

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.camera.use()
        self.clear()

        self.mappa.disegna()

        arcade.draw_polygon_filled(
            punti_esagono(
                self.provincia_selezionata.x,
                self.provincia_selezionata.y,
                self.provincia_selezionata.raggio
            ),
            arcade.color.GREEN
        )

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        self.camera.position = (self.camera.position[0] + self.cam_direction[0], self.camera.position[1] + self.cam_direction[1])
        
    def cambia_provincia(self, provincia):
        if provincia != None:
            self.provincia_selezionata = provincia

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        speed = 10

        if key == arcade.key.UP:
            self.cam_direction[1] = speed
        if key == arcade.key.DOWN:
            self.cam_direction[1] = -speed
        if key == arcade.key.LEFT:
            self.cam_direction[0] = -speed
        if key == arcade.key.RIGHT:
            self.cam_direction[0] = speed

        if key == arcade.key.W:
            self.cambia_provincia(self.provincia_selezionata.nordovest)
        if key == arcade.key.E:
            self.cambia_provincia(self.provincia_selezionata.nordest)
        if key == arcade.key.H:
            self.cambia_provincia(self.provincia_selezionata.est)
        if key == arcade.key.L:
            self.cambia_provincia(self.provincia_selezionata.ovest)
        if key == arcade.key.S:
            self.cambia_provincia(self.provincia_selezionata.sudovest)
        if key == arcade.key.D:
            self.cambia_provincia(self.provincia_selezionata.sudest)
        
    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
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
