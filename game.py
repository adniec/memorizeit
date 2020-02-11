"""Game Module

This module contains classes responsible for launching game in preferred mode - static (2D) or dynamic (3D). It sets
appropriate environment for game based on `pygame` or `OpenGL`. It covers methods which pick proper elements, count
them, adjust speed and time of a game.

Modules used are: `pygame`, `pygame.locals`, `OpenGL.GL`, `OpenGL.GLU`, `time`, `random`, `pathlib`, `PIL`, `sys`,
`figure`, `gui`, `colors`, `config`. It is required to provide them before running application.

It contains classes:

    * Game - general methods used both in dynamic and static mode, showing how game game is processed
    * Dynamic - specified methods allowing to run game in 3D mode. `OpenGL` in use. Responsible for camera movement.
    * Static - methods needed to run 2D game mode. Responsible for loading and processing images.

License:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
    """
    A class with collection of the same methods needed both in Dynamic and Static class. It is base, responsible for
    processing game, adjusting its settings, launching summarization afterwards.

    ...

    Attributes
    ----------
    resolution : tuple
        a tuple with two int values - width, height - according to resolution of used monitor
    settings : dict
        dictionary with loaded from file settings which will be used in a game
    timer : dict
        dictionary with information about beginning of a game, its length, single and last wave time
    colors : colors.Random
        object responsible for generating random color codes in RGB (0-1, 0-1, 0-1) format
    elements : dict
        dictionary filled with names of elements used in game and corresponding them color
    counter : dictionary
        dictionary containing names of elements and their occurrence in game
    wave : figure.Wave2D or figure.Wave3D
        object responsible for creating wave of elements on the screen

    Methods
    -------
    has_time_left()
        returns True in case when game is still running - according to set time else False
    create_timer()
        creates dictionary with information about beginning of a game, its length, single and last wave time
    play_sound()
        if sound is turned on in game settings this method plays it
    adjust_elements(figures, amount)
        returns dictionary with randomly picked elements from list and corresponding them color in length of set amount
    pick_element()
        randomly picks one element from elements attribute and returns it with proper color (if nothing is set picks
        random color)
    create_wave(function, *args)
        picks figure, creates from it wave which will be displayed on screen. It updates counter and play sound if it is
        set to on. Function says which type of wave will be created - 2D or 3D. *args passed depends on this type - to
        see more check documentation for Wave class in module figure
    is_wave_finished()
        returns True if currently displayed wave should be replaced with new one else False
    """

    def __init__(self, resolution):
        """Shows steps how game is processed.

        Parameters
        ----------
        resolution : tuple
            a tuple with two int values - width, height - according to resolution of used monitor
        """

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
        """Returns True in case when game is still running - according to set time else False"""

        return self.timer['total'] > time() - self.timer['start']

    def create_timer(self):
        """Creates dictionary with information about beginning of a game, its length, single and last wave time"""

        total = self.settings['time']
        wave = 7 / self.settings['speed']
        return {'start': time(), 'total': total, 'wave': wave * 2, 'last': total - wave}

    def play_sound(self):
        """If sound is turned on in game settings this method plays it"""

        if self.settings['sound'] == 'On':
            try:
                pygame.mixer.init()
                pygame.mixer.Sound("sound.ogg").play()
            except (pygame.error, FileNotFoundError):
                pass

    def adjust_elements(self, figures, amount):
        """Sets elements used in game

        Parameters
        ----------
        figures : list
            a list with figures names from which will be picked figures taking part in a game
        amount : int
            number of elements taking part in a game - loaded from settings

        Returns
        -------
        dict
            dictionary with randomly picked elements and corresponding them color according to color difficulty setting
        """

        picked = sample(figures, amount)
        color = colors.pick(self.settings['colors'], amount)
        if type(color) is bool: color = [color] * amount
        return {figure: color[index] for index, figure in enumerate(picked)}

    def pick_element(self):
        """returns one randomly picked element with its color (if nothing is set picks random color)"""

        figure = choice(list(self.elements))
        color = self.elements[figure]
        if not isinstance(color, (pygame.Surface, tuple)):
            color = self.color.get_color() if color else False
        return figure, color

    def create_wave(self, function, *args):
        """Create wave of randomly picked element

        Picks figure, creates from it wave which will be displayed on screen. It updates counter and play sound if it is
        set to on. Function says which type of wave will be created - 2D or 3D. *args passed depends on this type.

        Parameters
        ----------
        function : Wave2D or Wave3D
            used to create proper wave object depending on launched game mode
        *args
            values needed to create specified Wave type - 2D (screen, resolution) or 3D (positionZ). To see more check
            documentation for proper Wave class in module figure

        Returns
        -------
        figure.Wave2D or figure.Wave3D
            object with created wave, used to display it - 2D or 3D type according to passed function
        """

        figure = self.pick_element()
        wave = function(*figure, *args)
        self.counter[figure[0]] = self.counter[figure[0]] + len(wave)
        self.play_sound()
        return wave

    def is_wave_finished(self, condition):
        """returns True if currently displayed wave should be replaced with new one else False"""

        if condition:
            if self.timer['last'] > time() - self.timer['start']:
                return True
        return False


class Static(Game):
    """
    A class containing methods used in static game mode. Sets environment for binding 2D figures or images to game
    screen represented by `pygame.Surface`. It is child of Game class.

    ...

    Attributes
    ----------
    screen: pygame.Surface
        object representing game screen where created 2D figures or images will be binded


    Methods
    -------
    prepare_environment()
        sets basics needed to launch 2D game mode. Specifies attribute used only in static game mode - screen. Extends
        attribute timer by interval allowing to control spawning new 2D waves on screen.
    run_game()
        function (game base) which is sent to `pygame` event handler - it will be run in loop. Responsible for spawning
        waves of 2D figures based on time interval
    spawn_new_wave()
        clears screen and spawns new wave of figures or images
    get_images()
        returns dictionary with images names and their representation as `pygame.Surface`
    load_image(path)
        returns image representation as `pygame.Surface` loading it from set path
    fit_image(image)
        scales set image to size appropriate to display it during game
    set_elements()
        contains list of allowed elements in game. At first loads images from their directory then fill missing elements
        by drawing 2D figures picked from elements list according to game settings.
    """

    def prepare_environment(self):
        """Sets basics needed to launch 2D game mode

        Specifies attribute used only in static game mode - screen. Extends attribute timer by interval allowing to
        control spawning new 2D waves on screen.
        """

        self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        self.timer['interval'] = self.timer['start']
        self.wave = self.create_wave(Wave2D, self.screen, self.resolution)

    def run_game(self):
        """Spawns waves of 2D figures based on time interval"""

        if self.is_wave_finished(time() > self.timer['interval'] + self.timer['wave']):
            self.timer['interval'] += self.timer['wave']
            self.spawn_new_wave()
        else:
            self.wave()

    def spawn_new_wave(self):
        """Clears screen and spawns new wave of figures or images"""

        self.screen.fill((0, 0, 0))
        self.wave = self.create_wave(Wave2D, self.screen, self.resolution)

    def get_images(self):
        """Loads images from their directory ('images/elements')

        Returns
        -------
        dict
            dictionary with image name and its representation as `pygame.Surface`
        """

        images = {}
        try:
            for image in Path("images/elements").iterdir():
                images[image.stem] = self.load_image(image)
        except OSError:
            pass
        return images

    def load_image(self, path):
        """Loads image from set path and scales it

        Parameters
        ----------
        path : pathlib.Path
            location of image to load

        Returns
        -------
        pygame.Surface
            information about loaded and scaled image represented as `pygame.Surface`
        """

        image = Image.open(path)
        image = self.fit_image(image)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    def fit_image(self, image):
        """Scales image

        Lowers width or height of image as long as it will fit dedicated place on screen (calculated from monitor
        resolution).

        Parameters
        ----------
        image : PIL.Image
            image representation from PIL library

        Returns
        -------
        PIL.Image
            scaled image represented by PIL
        """

        x, y = [x / 5 for x in self.resolution]
        w, h = image.size
        ratio = x / w if x < w else y / h if y < h else False
        if ratio:
            size = [int(x * ratio) for x in image.size]
            image = image.resize(size, Image.ANTIALIAS)
            return self.fit_image(image)
        return image

    def set_elements(self):
        """Returns elements used in game

        It contains list of allowed elements in game. At first loads images from their directory then fill missing
        elements by drawing 2D figures picked from elements list according to game settings (amount). Returned elements
        are gathered in dictionary with their names and color code or image.
        """

        amount = self.settings['figures']
        images = self.get_images()
        if len(images) < amount:
            figures = self.adjust_elements(['square', 'triangle', 'octagon', 'diamond'], amount - len(images))
            return {**images, **figures}
        else:
            picked = sample(list(images), amount)
            return {x: images[x] for x in picked}


class Dynamic(Game):
    """
    A class containing methods used in dynamic game mode. Sets environment for creating 3D figures and moves camera
    during gameplay. It is child of Game class.

    ...

    Attributes
    ----------
    spawned_at : int
        camera Z value (how far from beginning it moved) - needed to create figures and make them visible


    Methods
    -------
    prepare_environment()
        sets basics needed to launch 3D game mode. Specifies attribute used only in dynamic game mode - spawned_at
    run_game()
        function (game base) which is sent to `pygame` event handler - it will be run in loop. Responsible for spawning
        waves of 3D figures based on length of camera Z movement
    spawn_new_wave(positionZ)
        removes old wave and spawns new one according to set position of camera
    move_view()
        responsible for camera movement, returns Z position needed to create figures waves
    get_speed()
        according to used platform adjust speed for moving camera
    set_elements()
        contains list of allowed elements in game and returns those which are picked by method adjust_elements
    """

    def prepare_environment(self):
        """sets basics needed to launch 3D game mode"""

        pygame.display.set_mode(self.resolution, DOUBLEBUF | OPENGL | pygame.FULLSCREEN)
        gluPerspective(45, (self.resolution[0] / self.resolution[1]), 0.1, 50)
        self.spawned_at = -10
        self.wave = self.create_wave(Wave3D, self.spawned_at)

    def run_game(self):
        """Spawns waves of 3D figures based on length of camera Z movement"""

        cameraZ = self.move_view()
        if self.is_wave_finished(cameraZ < self.spawned_at - 100):
            self.spawn_new_wave(cameraZ)
        else:
            self.wave()

    def spawn_new_wave(self, positionZ):
        """Removes old wave and spawns new one according to set position of camera

        Parameters
        ----------
        positionZ : int
            value of camera Z - where it is moved
        """

        del self.wave
        self.wave = self.create_wave(Wave3D, positionZ)
        self.spawned_at = positionZ

    def move_view(self):
        """Responsible for camera movement, returns Z position"""

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glTranslatef(0, 0, self.get_speed())
        cameraZ = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)[3][2]
        return int(cameraZ)

    def get_speed(self):
        """According to used platform adjust speed for moving camera."""

        s = self.settings['speed']
        return s / 5 - 0.15 * s if 'win' in platform else s / 5

    def set_elements(self):
        """From allowed figures returns those which are picked to game"""

        return self.adjust_elements(['Cube', 'Pyramid', 'Octahedron', 'Octagon'], self.settings['figures'])
