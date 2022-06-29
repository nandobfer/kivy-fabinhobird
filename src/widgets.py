from kivy.uix.widget import Widget
from kivy.animation import Animation


class Obstacle(Widget):
    # color = ListProperty([0.3, 0.2, 0.2, 1])
    game_screen = None
    scored = False

    def __init__(self, game_screen=None, **kwargs):
        global players
        super().__init__(**kwargs)
        self.animation = Animation(x=-self.width, duration=3)
        self.animation.bind(on_complete=self.vanish)
        self.animation.start(self)
        self.game_screen = game_screen

    def on_x(self, *args):
        if self.game_screen:
            player = self.game_screen.ids.player
            if self.x < player.x and not self.scored:
                self.game_screen.increaseScore()
                self.scored = True

    def vanish(self, *args):
        self.game_screen.remove_widget(self)
        self.game_screen.obstacles.remove(self)
