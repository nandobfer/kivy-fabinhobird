from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty, StringProperty

from random import random
from client import Socket

fps = 1/60
client = None


class Manager(ScreenManager):
    pass


class Menu(Screen):
    pass


class MenuMultiplayer(Screen):
    status = StringProperty('Aguardando jogador 2')

    def on_enter(self, *args):
        Clock.schedule_once(self.getPlayer2, 1)
        return super().on_enter(*args)

    def getPlayer2(self, *args):
        player = client.player2
        if not player:
            Clock.schedule_once(self.getPlayer2, 1)
        else:
            self.status = f'Player 2 joined!'


class Game(Screen):
    obstacles = []
    score = NumericProperty(0)

    def on_enter(self, *args):
        Clock.schedule_interval(self.update, fps)
        Clock.schedule_interval(self.spawnObstacle, 1)

    def on_pre_enter(self, *args):
        self.score = 0
        self.ids.player.y = self.height / 2
        self.ids.player.speed = 0

    def increaseScore(self, *args):
        self.score += 0.5
        if client:
            client.sio.emit('score', self.score)

    def spawnObstacle(self, *args):
        gap = self.height*0.3
        position = (self.height-gap) * random()
        width = self.width * 0.05
        obstacle_lower = Obstacle(x=self.width, height=position, width=width)
        obstacle_upper = Obstacle(
            x=self.width, y=position+gap, height=self.height-position-gap, width=width)
        self.obstacles.append(obstacle_lower)
        self.obstacles.append(obstacle_upper)

        self.add_widget(obstacle_lower, 1)
        self.add_widget(obstacle_upper, 1)

    def update(self, *args):
        self.ids.player.speed += -self.height * 3 * fps
        self.ids.player.y += self.ids.player.speed * fps

        if self.ids.player.y > self.height or self.ids.player.y < 0:
            self.gameOver()
        elif self.playerCollided():
            self.gameOver()

    def on_touch_down(self, *args):
        self.ids.player.speed = self.height*1

    def gameOver(self, *args):
        Clock.unschedule(self.update, fps)
        Clock.unschedule(self.spawnObstacle, 1)
        for obstacle in self.obstacles:
            obstacle.animation.cancel(obstacle)
            self.remove_widget(obstacle)
        self.obstacles = []
        App.get_running_app().root.current = 'gameover'

    def getCollision(self, obj1, obj2):
        if obj2.x <= obj1.x + obj1.width and obj2.x + obj2.width >= obj1.x and obj2.y <= obj1.y + obj1.height and obj2.y + obj2.height >= obj1.y:
            return True

    def playerCollided(self):
        collision = False
        for obstacle in self.obstacles:
            if self.getCollision(self.ids.player, obstacle):
                collision = True
                return collision


class GameOver(Screen):
    game_screen = None
    score = NumericProperty(0)

    def on_enter(self, *args):
        self.game_screen = App.get_running_app().root.get_screen('game')
        self.score = self.game_screen.score


class LoadingScreen(Screen):

    def on_enter(self, *args):
        Clock.schedule_once(self.connect, 2)

    def connect(self, *args):
        global client
        client = Socket()
        App.get_running_app().root.current = 'menu-multiplayer'


class StartMenu(Screen):
    pass


class Player(Image):
    speed = NumericProperty(0)


class Obstacle(Widget):
    # color = ListProperty([0.3, 0.2, 0.2, 1])
    game_screen = None
    scored = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation = Animation(x=-self.width, duration=3)
        self.animation.bind(on_complete=self.vanish)
        self.animation.start(self)
        self.game_screen = App.get_running_app().root.get_screen('game')

    def on_x(self, *args):
        if self.game_screen:
            player = self.game_screen.ids.player
            if self.x < player.x and not self.scored:
                self.game_screen.increaseScore()
                self.scored = True

    def vanish(self, *args):
        self.game_screen.remove_widget(self)
        self.game_screen.obstacles.remove(self)


class FlappyBird(App):
    def on_stop(self, *args):
        if client:
            client.disconnect()


FlappyBird().run()
