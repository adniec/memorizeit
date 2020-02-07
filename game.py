import pygame
from pygame.locals import DOUBLEBUF, OPENGL
import OpenGL.GL as gl
from OpenGL.GLU import gluPerspective
from time import time
from random import sample, choice
from pathlib import Path
from PIL import Image
from sys import platform
from figure import Wave3D, Wave2D
import gui
import colors
import config


class Game:

    def __init__(self, resolution):
        self.resolution = resolution
        pygame.mouse.set_visible(False)
        self.settings = config.Config().get_settings()
        self.timer = self.create_timer()
        self.color = colors.Random()
        self.elements = self.set_elements()
        self.counter = {x: 0 for x in list(self.elements)}
        self.wave = None
        self.prepare_environment()
        config.Handler(self.run_game, self.has_time_left)()
        pygame.mouse.set_visible(True)
        gui.Summary(self.counter)

    def has_time_left(self):
        return self.timer['total'] > time() - self.timer['start']

    def create_timer(self):
        total = self.settings['time']
        wave = 7 / self.settings['speed']
        return {'start': time(), 'total': total, 'wave': wave * 2, 'last': total - wave}

    def play_sound(self):
        if self.settings['sound'] == 'On':
            try:
                pygame.mixer.init()
                pygame.mixer.Sound("sound.ogg").play()
            except (pygame.error, FileNotFoundError):
                pass

    def adjust_elements(self, figures, amount):
        picked = sample(figures, amount)
        color = colors.pick(self.settings['colors'], amount)
        if type(color) is bool: color = [color] * amount
        return {figure: color[index] for index, figure in enumerate(picked)}

    def pick_element(self):
        figure = choice(list(self.elements))
        color = self.elements[figure]
        if not isinstance(color, (pygame.Surface, tuple)):
            color = self.color.get_color() if color else False
        return figure, color

    def create_wave(self, function, *args):
        figure = self.pick_element()
        wave = function(*figure, *args)
        self.counter[figure[0]] = self.counter[figure[0]] + len(wave)
        self.play_sound()
        return wave

    def is_wave_finished(self, condition):
        if condition:
            if self.timer['last'] > time() - self.timer['start']:
                return True
        return False


class Static(Game):

    def prepare_environment(self):
        self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        self.timer['interval'] = self.timer['start']
        self.wave = self.create_wave(Wave2D, self.screen, self.resolution)

    def run_game(self):
        if self.is_wave_finished(time() > self.timer['interval'] + self.timer['wave']):
            self.timer['interval'] += self.timer['wave']
            self.spawn_new_wave()
        else:
            self.wave()

    def spawn_new_wave(self):
        self.screen.fill((0, 0, 0))
        self.wave = self.create_wave(Wave2D, self.screen, self.resolution)

    def get_images(self):
        images = {}
        try:
            for image in Path("images/elements").iterdir():
                images[image.stem] = self.load_image(image)
        except OSError:
            pass
        return images

    def load_image(self, path):
        image = Image.open(path)
        image = self.fit_image(image)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    def fit_image(self, image):
        x, y = [x / 5 for x in self.resolution]
        w, h = image.size
        ratio = x / w if x < w else y / h if y < h else False
        if ratio:
            size = [int(x * ratio) for x in image.size]
            image = image.resize(size, Image.ANTIALIAS)
            return self.fit_image(image)
        return image

    def set_elements(self):
        amount = self.settings['figures']
        images = self.get_images()
        if len(images) < amount:
            figures = self.adjust_elements(['square', 'triangle', 'octagon', 'diamond'], amount - len(images))
            return {**images, **figures}
        else:
            picked = sample(list(images), amount)
            return {x: images[x] for x in picked}


class Dynamic(Game):

    def prepare_environment(self):
        pygame.display.set_mode(self.resolution, DOUBLEBUF | OPENGL | pygame.FULLSCREEN)
        gluPerspective(45, (self.resolution[0] / self.resolution[1]), 0.1, 50)
        self.spawned_at = -10
        self.wave = self.create_wave(Wave3D, self.spawned_at)

    def run_game(self):
        cameraZ = self.move_view()
        if self.is_wave_finished(cameraZ < self.spawned_at - 100):
            self.spawn_new_wave(cameraZ)
        else:
            self.wave()

    def spawn_new_wave(self, positionZ):
        del self.wave
        self.wave = self.create_wave(Wave3D, positionZ)
        self.spawned_at = positionZ

    def move_view(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glTranslatef(0, 0, self.get_speed())
        cameraZ = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)[3][2]
        return int(cameraZ)

    def get_speed(self):
        s = self.settings['speed']
        return s / 5 - 0.15 * s if 'win' in platform else s / 5

    def set_elements(self):
        return self.adjust_elements(['Cube', 'Pyramid', 'Octahedron', 'Octagon'], self.settings['figures'])
