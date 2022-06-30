from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.core.window import Window

from random import random
from client import Socket
import os
import config

fps = 1/60
client = None
players = None
skins_list = []
path = 'assets/skins/'
skins_list = os.listdir(path)
skin = path+skins_list[0]


class Manager(ScreenManager):
    pass


class Menu(Screen):
    global skin, path, skins_list
    skin_1 = StringProperty(path+skins_list[0])
    skins = skins_list
    skin_index = 0

    def play(self, *args):
        global players
        players = 1
        print(players)
        # set to game-multiplayer for testing purposes
        App.get_running_app().root.current = 'game'

    def next_skin(self, *args):
        global skin, path
        next_index = self.skin_index + 1
        if next_index < len(self.skins):
            self.skin_index += 1
            self.skin_1 = path + self.skins[self.skin_index]
            skin = self.skin_1

            # # disable next_index button
            # next_index = self.skins.index(self.skin_1)+1
            # if not next_index < len(self.skins):
            #     self.ids.next_button.disabled = True

            # # enable previous button
            # self.ids.previous_button.disabled = False

    def previous_skin(self, *args):
        global skin
        previous = self.skin_index - 1
        if previous >= 0:
            self.skin_index -= 1
            self.skin_1 = path + self.skins[self.skin_index]
            skin = self.skin_1

            # # disable previous button
            # previous = self.skins.index(self.skin_1)-1
            # if not previous >= 0:
            #     self.ids.previous_button.disabled = True

            # # enable next_index button
            # self.ids.next_button.disabled = False


class MenuMultiplayer(Screen):
    status = StringProperty('Conectado')
    global skin, path, skins_list
    skins = skins_list
    skin_index = 0
    skin_1 = StringProperty(path+skins_list[0])

    def play(self, *args):
        global players
        players = 2
        client.player.ready = True
        client.sendMultiplayerReady()
        self.ids.start_button.disabled = True

    def next_skin(self, *args):
        global skin, path
        next_index = self.skin_index + 1
        if next_index < len(self.skins):
            self.skin_index += 1
            self.skin_1 = path + self.skins[self.skin_index]
            skin = self.skin_1
            client.player.skin = skin

            # send multiplayer data
            client.SendMultiplayerData()

    def previous_skin(self, *args):
        global skin
        previous = self.skin_index - 1
        if previous >= 0:
            self.skin_index -= 1
            self.skin_1 = path + self.skins[self.skin_index]
            skin = self.skin_1
            client.player.skin = skin

            # send multiplayer data
            client.SendMultiplayerData()

    def on_enter(self, *args):
        Clock.schedule_once(self.getPlayer2, 1)
        me = client.player
        client.player.skin = skin
        print(me.player)
        return super().on_enter(*args)

    def getPlayer2(self, *args):
        player = client.player2
        if not player:
            self.status = f'Aguardando jogador 2'
            Clock.schedule_once(self.getPlayer2, 1)
        else:
            # send multiplayer data
            client.SendMultiplayerData()
            self.status = f'Player 2 joined!'
            self.ids.start_button.disabled = False

            Clock.schedule_once(self.checkPlayer2, 1)

    def checkPlayer2(self, *args):
        player = client.player2
        Clock.schedule_once(self.checkPlayer2, 1)

        # player 2 skin chooser
        self.renderPlayer2Skin()

        if not player:
            self.status = f'Aguardando jogador 2'
            self.ids.start_button.disabled = True
            Clock.schedule_once(self.getPlayer2, 1)
        else:
            # get ready
            if client.player2.ready:
                self.status = f'Jogador 2 está pronto'

            # start game
            if client.start:
                client.start = False
                App.get_running_app().root.current = 'game-multiplayer'

    def renderPlayer2Skin(self, *args):
        if client.player2:
            if client.player2.skin:
                self.ids.player_2_skin.source = client.player2.skin
                self.ids.player_2_skin.opacity = 1

        else:
            self.ids.player_2_skin.opacity = 0

    def back(self, *args):
        # self.status = 'Desconectando do servidor'
        client.disconnect()
        App.get_running_app().root.current = 'start'


class Game(Screen):
    obstacles = []
    score = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == ' ':
            self.tap()
        return True

    def on_enter(self, *args):
        Clock.schedule_interval(self.update, fps)
        Clock.schedule_interval(self.spawnObstacle, 1)

    def on_pre_enter(self, *args):
        global skin
        self.score = 0
        self.ids.player.y = self.height / 2
        self.ids.player.speed = 0

        self.ids.player.source = skin

    def increaseScore(self, *args):
        self.score += 0.5
        if client:
            client.sio.emit('score', self.score)

    def spawnObstacle(self, *args):
        gap = self.height*config.obstacle
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
        self.ids.player.speed += -self.height * config.gravity * fps
        self.ids.player.y += self.ids.player.speed * fps

        if self.ids.player.y > self.height or self.ids.player.y < 0:
            self.gameOver()
        elif self.playerCollided():
            self.gameOver()

    def on_touch_down(self, *args):
        self.tap(*args)

    def tap(self, *args):
        self.ids.player.speed = self.height * config.player_speed

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


class GameMultiplayer(Game):
    frame = 0

    def on_pre_enter(self, *args):
        global skin
        self.score = 0
        self.ids.player.y = self.height / 2
        self.ids.player.speed = 0

        self.ids.player.source = skin

        self.ids.player2.y = self.height / 2
        self.ids.player2.speed = 0

        self.ids.player2.source = client.player2.skin

    def on_touch_down(self, *args):
        self.ids.player.speed = self.height * config.player_speed
        client.sendGameTap()

    def update(self, *args):

        if client.player2.tapped:
            self.ids.player2.speed = self.height * config.player_speed
            client.player2.tapped = False

        self.frame += 1
        if self.frame == 30:
            self.ids.player2.pos = client.sendPos()
            self.frame = 0

        self.ids.player.speed += -self.height * config.gravity * fps
        self.ids.player.y += self.ids.player.speed * fps

        self.ids.player2.speed += -self.height * config.gravity * fps
        self.ids.player2.y += self.ids.player2.speed * fps

        client.player2.pos = (self.ids.player2.pos)
        client.player2.pos = (self.ids.player2.pos)

        if self.ids.player.y > self.height or self.ids.player.y < 0:
            self.gameOver()
        elif self.playerCollided():
            self.gameOver()


class GameOver(Screen):
    game_screen = None
    score = NumericProperty(0)

    def on_enter(self, *args):
        global players
        if players == 1:
            self.game_screen = App.get_running_app().root.get_screen('game')
        else:
            self.game_screen = App.get_running_app().root.get_screen('game-multiplayer')

        self.score = self.game_screen.score

    def replay(self, *args):
        global players
        if players == 1:
            App.get_running_app().root.current = 'game'
        else:
            App.get_running_app().root.current = 'game-multiplayer'

    def menu(self, *args):
        global players
        if players == 2:
            client.disconnect()
        App.get_running_app().root.current = 'start'


class LoadingScreen(Screen):

    def on_enter(self, *args):
        Clock.schedule_once(self.connect, 2)

    def connect(self, *args):
        global client
        client = Socket()
        client.app = App.get_running_app()
        App.get_running_app().root.current = 'menu-multiplayer'


class StartMenu(Screen):
    def on_enter(self, *args):
        global players
        players = None
        return super().on_enter(*args)


class Player(Image):
    speed = NumericProperty(0)


class Player2(Image):
    speed = NumericProperty(0)


class Obstacle(Widget):
    # color = ListProperty([0.3, 0.2, 0.2, 1])
    game_screen = None
    scored = False

    def __init__(self, **kwargs):
        global players
        super().__init__(**kwargs)
        self.animation = Animation(x=-self.width, duration=3)
        self.animation.bind(on_complete=self.vanish)
        self.animation.start(self)

        if players == 1:
            self.game_screen = App.get_running_app().root.get_screen('game')
        else:
            self.game_screen = App.get_running_app().root.get_screen('game-multiplayer')

    def on_x(self, *args):
        if self.game_screen:
            player = self.game_screen.ids.player
            if self.x < player.x and not self.scored:
                self.game_screen.increaseScore()
                self.scored = True

    def vanish(self, *args):
        self.game_screen.remove_widget(self)
        self.game_screen.obstacles.remove(self)


class FabinhoBird(App):
    def on_stop(self, *args):
        if client:
            client.disconnect()


FabinhoBird().run()
