import random
from appdirs import AppDirs
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader
import json
from kivy.animation import Animation

dirs = AppDirs("GameApp", "Test")
user_save_directory = dirs.user_data_dir
sfx_score = SoundLoader.load('audio/score.wav')
sfx_die = SoundLoader.load('audio/hit.wav')
music = SoundLoader.load('audio/music.wav')


class MultiSound(object):
    def __init__(self, file, num):
        self.num = num
        self.sounds = [SoundLoader.load(file) for n in range(num)]
        self.index = 0

    def play(self):
        self.sounds[self.index].volume = 0.4
        self.sounds[self.index].play()
        self.index += 1
        if self.index == self.num:
            self.index = 0


sfx_flap = MultiSound('audio/jump.wav', 3)


class Sprite(Image):
    def __init__(self, **kwargs):
        super(Sprite, self).__init__(allow_stretch=True, **kwargs)
        self.size = self.texture_size
        self.texture.mag_filter = 'nearest'


class Pipe(Widget):
    def __init__(self, pos):
        super(Pipe, self).__init__(pos=pos)
        self.top_image = Sprite(source='images/pipe_top.png')
        self.top_image.pos = (self.x, self.y + 3.5 * 100)
        self.add_widget(self.top_image)
        self.bottom_image = Sprite(source='images/pipe.png')
        self.bottom_image.pos = (self.x, self.y - self.bottom_image.height)
        self.add_widget(self.bottom_image)
        self.width = self.top_image.width
        self.scored = False

    def update(self):
        self.x -= 4
        self.top_image.x = self.bottom_image.x = self.x
        if self.right < 0:
            self.parent.remove_widget(self)


class Pipes(Widget):
    add_pipe = 0

    def update(self, dt):
        for child in list(self.children):
            child.update()
        self.add_pipe -= dt
        if self.add_pipe < 0:
            lowend = (self.y + 50)
            highend = (self.height - 50 - (3.5 * 100))
            y = random.randint(lowend, highend)
            self.add_widget(Pipe(pos=(self.width, y)))
            pipe_interval = float(random.randint(3, 15)/10)
            self.add_pipe = 1 + pipe_interval


class Menu(Widget):
    def __init__(self):
        super(Menu, self).__init__()
        self.highscore = Game.get_highscore(Game)
        self.add_widget(Sprite(source='images/background.png'))
        self.size = self.children[0].size
        self.birdman = Sprite(source='images/birdman1.png',  pos=(800, 100))
        self.add_widget(self.birdman)
        self.add_widget(Ground(source='images/ground.png'))
        self.add_widget(Label(pos=(450, 650), text="Flappers", font_size=180))
        self.add_widget(Label(pos=(500, 400), text="High Score: " + str(self.highscore)))
        l = Label(text='Tap to Start', pos=(-200, 0))
        self.add_widget(l)
        self.animate(l)
        music.volume = 1
        music.loop = True
        music.play()
        # Clock.schedule_interval(self.check_sound, 30)

    def on_touch_down(self, *ignore):
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(Game())

    # def check_sound(self, dt=None):
    #     music.play()

    def animate(self, instance):
        # create an animation object. This object could be stored
        # and reused each call or reused across different widgets.
        # += is a sequential step, while &= is in parallel
        animation = Animation(pos=(600, 200), t='out_bounce')

        # apply the animation on the button, passed in the "instance" argument
        # Notice that default 'click' animation (changing the button
        # color while the mouse is down) is unchanged.
        animation.start(instance)


class Ground(Widget):
    def __init__(self, source):
        super(Ground, self).__init__()
        self.image = Sprite(source=source)
        self.add_widget(self.image)
        self.size = self.image.size
        self.image_dupe = Sprite(source=source, x=self.width)
        self.add_widget(self.image_dupe)
        self.image_dupe2 = Sprite(source=source, x=self.width * 2)
        self.add_widget(self.image_dupe2)
        self.image_dupe3 = Sprite(source=source, x=self.width * 3)
        self.add_widget(self.image_dupe3)
        self.image_dupe4 = Sprite(source=source, x=self.width * 4)
        self.add_widget(self.image_dupe4)
        self.image_dupe5 = Sprite(source=source, x=self.width * 5)
        self.add_widget(self.image_dupe5)

    def update(self):
        self.image.x -= 4
        self.image_dupe.x -= 4
        self.image_dupe2.x -= 4
        self.image_dupe3.x -= 4
        self.image_dupe4.x -= 4
        self.image_dupe5.x -= 4

        if self.image.right <= 0:
            self.image.x = 0
            self.image_dupe.x = self.width
            self.image_dupe2.x = self.width * 2
            self.image_dupe3.x = self.width * 3
            self.image_dupe4.x = self.width * 4
            self.image_dupe5.x = self.width * 5


class Bird(Sprite):
    def __init__(self, pos):
        super(Bird, self).__init__(source='atlas://images/bird_anim.atlas/wing-up', pos=pos)
        self.velocity_y = 0
        self.gravity = -0.3

    def update(self):
        self.velocity_y += self.gravity
        self.velocity_y = max(self.velocity_y, -10)
        self.y += self.velocity_y
        if self.velocity_y < -5:
            self.source = 'atlas://images/bird_anim.atlas/wing-up'
        elif self.velocity_y < 0:
            self.source = 'atlas://images/bird_anim.atlas/wing-mid'

    def on_touch_down(self, *ignore):
        self.velocity_y = 6.5
        self.source = 'atlas://images/bird_anim.atlas/wing-down'
        sfx_flap.volume = 0.4
        sfx_flap.play()


class Background(Widget):
    def __init__(self, source):
        super(Background, self).__init__()
        self.image = Sprite(source=source)
        self.add_widget(self.image)
        self.size = self.image.size
        self.image_dupe = Sprite(source=source, x=self.width)
        self.add_widget(self.image_dupe)

    def update(self):
        self.image.x -= 2
        self.image_dupe.x -= 2

        if self.image.right <= 0:
            self.image.x = 0
            self.image_dupe.x = self.width


class Game(Widget):
    def __init__(self):
        super(Game, self).__init__()
        Window.bind(on_key_down=self.key_action)
        self.score = 0
        self.high_score = self.get_highscore()
        self.background = Background(source='images/background.jpg')
        self.size = self.background.size
        self.add_widget(self.background)
        self.ground = Ground(source='images/ground.png')
        self.pipes = Pipes(pos=(0, self.ground.height), size=self.size)
        self.add_widget(self.pipes)
        self.add_widget(self.ground)
        self.score_label = Label(text="0")
        self.add_widget(self.score_label)
        self.high_score_label = Label(center_x=self.center_x, text="High Score: " + str(self.high_score))
        self.add_widget(self.high_score_label)
        self.over_label = Label(center=self.center, opacity=0, text="Game Over")
        self.add_widget(self.over_label)
        self.bird = Bird(pos=(20, self.height / 2))
        self.add_widget(self.bird)
        Clock.schedule_interval(self.update, 1.0/60)
        self.game_over = False


    def update(self, dt):
        if self.game_over:
            return

        self.background.update()
        self.bird.update()
        self.ground.update()
        self.pipes.update(dt)

        if self.bird.collide_widget(self.ground):
            self.game_over = True

        for pipe in self.pipes.children:
            if not pipe.scored and pipe.right < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.score_label.text = str(self.score)
                sfx_score.volume = 0.3
                sfx_score.play()
            elif pipe.top_image.collide_widget(self.bird):
                self.game_over = True
            elif pipe.bottom_image.collide_widget(self.bird):
                self.game_over = True

        if self.game_over:
            sfx_die.volume = 0.5
            sfx_die.play()
            music.stop()
            self.over_label.opacity = 1
            self.bind(on_touch_down=self._on_touch_down)
            self.set_highscore()


    def _on_touch_down(self, *ignore):
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(Menu())

    def get_highscore(self):
        with open('data/user_data.json') as jsonFile:
            data = json.load(jsonFile)
            self.high_score = data["highscores"][0]["score"]
            return self.high_score

    def set_highscore(self):
        with open('data/user_data.json') as jsonFile:
            data = json.load(jsonFile)
            self.high_score = data["highscores"][0]["score"]
            print (self.high_score)
            if self.score > self.high_score:
                with open('data/user_data.json', 'w') as jsonFile:
                    data["highscores"][0]["score"] = self.score
                    json.dump(data, jsonFile, indent=2)
                    jsonFile.truncate()
        self.high_score_label.text = "High score: " + str(self.high_score)

    def key_action(self, *args):
        # print ("got a key event: %s" % list(args))
        self.bird.on_touch_down(self)


class GameApp(App):
    def build(self):
        top = Widget()
        top.add_widget(Menu())
        Window.size = 720, 460
        return top


if __name__ == "__main__":
    GameApp().run()