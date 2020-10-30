"""#### Game

This module contains classes responsible for launching game in preferred mode
- static (2D) or dynamic (3D). It set appropriate environment for game based
on `pygame` or `OpenGL`. It cover methods which pick proper elements, count
them, adjust speed and time of a game. Modules used: `OpenGL`, `pathlib`,
`PIL`, `pygame`, `random`, `sys`, `time`.

License:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from pathlib import Path
from random import sample, choice
from sys import platform
from time import time

import OpenGL.GL as gl
from OpenGL.GLU import gluPerspective
from PIL import Image
import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from memorizeit.figure import Wave3D, Wave2D
from memorizeit import gui
from memorizeit import colors
from memorizeit import config


class Game:
    """
    Run game.

    A class with collection of the same methods needed both in Dynamic and
    Static class. It is base, responsible for processing game, adjusting its
    settings and launching summarization afterwards.

    ...

    Attributes
    ----------
    resolution : tuple
        a tuple with two int values - width, height - according to resolution
        of used monitor
    settings : dict
        dictionary with loaded from file settings which will be used in a game
    timer : dict
        dictionary with information about beginning of a game, its length,
        single and last wave time
    colors : colors.Random
        object responsible for generating random color codes in RGB (0-1, 0-1,
        0-1) format
    elements : dict
        dictionary filled with names of elements used in game and corresponding
         them color
    counter : dictionary
        dictionary containing names of elements and their occurrence in game
    wave : figure.Wave2D or figure.Wave3D
        object responsible for creating wave of elements on the screen
    """

    def __init__(self, resolution):
        """Initialize steps to process game.

        Parameters
        ----------
        resolution : tuple
            a tuple with two int values - width, height - according to
            resolution of used monitor
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
        """Check if game is still running."""
        return self.timer['total'] > time() - self.timer['start']

    def create_timer(self):
        """Create dictionary with information about game time.

        It contains beginning of a game, length, single and last wave time.
        """
        total = self.settings['time']
        wave = 7 / self.settings['speed']
        return {
            'start': time(),
            'total': total,
            'wave': wave * 2,
            'last': total - wave
        }

    def play_sound(self):
        """Play sound if setting is turned on."""
        if self.settings['sound'] == 'On':
            try:
                path = Path(__file__).parent.absolute() / 'sound.ogg'
                pygame.mixer.init()
                pygame.mixer.Sound(str(path)).play()
            except (pygame.error, FileNotFoundError):
                pass

    def adjust_elements(self, figures, amount):
        """Set elements used in game.

        Parameters
        ----------
        figures : list
            a list with figures names from which will be picked figures taking
            part in a game
        amount : int
            number of elements taking part in a game - loaded from settings

        Returns
        -------
        dict
            dictionary with randomly picked elements and corresponding them
            color according to color difficulty setting
        """
        picked = sample(figures, amount)
        color = colors.pick(self.settings['colors'], amount)
        if type(color) is bool:
            color = [color] * amount
        return {figure: color[index] for index, figure in enumerate(picked)}

    def pick_element(self):
        """Return one randomly picked element with its color.

        Based on game difficulty color can be random for each wave or figure.
        """
        figure = choice(list(self.elements))
        color = self.elements[figure]
        if not isinstance(color, (pygame.Surface, tuple)):
            color = self.color.get_color() if color else False
        return figure, color

    def create_wave(self, function, *args):
        """Create wave of randomly picked element.

        Picks figure, creates from it wave which will be displayed on screen.
        It updates counter and play sound if it is set to on. Function says
        which type of wave will be created - 2D or 3D. *args passed depends on
        this type.

        Parameters
        ----------
        function : Wave2D or Wave3D
            used to create proper wave object depending on launched game mode
        *args
            values needed to create specified Wave type - 2D (screen,
            resolution) or 3D (z_position). To see more check documentation for
            proper Wave class in module figure

        Returns
        -------
        figure.Wave2D or figure.Wave3D
            object with created wave, used to display it - 2D or 3D type
            according to passed function
        """
        figure = self.pick_element()
        wave = function(*figure, *args)
        self.counter[figure[0]] = self.counter[figure[0]] + len(wave)
        self.play_sound()
        return wave

    def is_wave_finished(self, condition):
        """Specify if displayed wave should be replaced with new one."""
        if condition:
            if self.timer['last'] > time() - self.timer['start']:
                return True
        return False


class Static(Game):
    """
    Setup static game.

    A class containing methods used in static game mode. Sets environment for
    binding 2D figures or images to game screen represented by
    `pygame.Surface`. It extend `Game` class.

    ...

    Attributes
    ----------
    screen: pygame.Surface
        object representing game screen where created 2D figures or images
        will be binded
    """

    def prepare_environment(self):
        """Set basics needed to launch 2D game mode.

        Specify attribute used only in static game mode - screen. Extend
        attribute timer by interval allowing to control spawning new 2D waves
        on screen.
        """
        self.screen = pygame.display.set_mode(
            self.resolution,
            pygame.FULLSCREEN
        )
        self.timer['interval'] = self.timer['start']
        self.wave = self.create_wave(Wave2D, self.screen, self.resolution)

    def run_game(self):
        """Spawn waves of 2D figures based on time interval."""
        if self.is_wave_finished(
                time() > self.timer['interval'] + self.timer['wave']
        ):
            self.timer['interval'] += self.timer['wave']
            self.spawn_new_wave()
        else:
            self.wave()

    def spawn_new_wave(self):
        """Clear screen and spawn new wave of figures or images."""
        self.screen.fill((0, 0, 0))
        self.wave = self.create_wave(Wave2D, self.screen, self.resolution)

    def get_images(self):
        """Load images from their directory ('memorizeit/img/elements/').

        Returns
        -------
        dict
            dictionary with image name and its representation as
            `pygame.Surface`
        """
        images = {}
        try:
            path = Path(__file__).parent.absolute() / 'img' / 'elements'
            for image in path.iterdir():
                images[image.stem] = self.load_image(image)
        except OSError:
            pass
        return images

    def load_image(self, path):
        """Load image from set path and scale it.

        Parameters
        ----------
        path : pathlib.Path
            location of image to load

        Returns
        -------
        pygame.Surface
            information about loaded and scaled image represented as
            `pygame.Surface`
        """
        image = Image.open(path)
        image = self.fit_image(image)
        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

    def fit_image(self, image):
        """Scale image.

        Lower width or height of image as long as it will fit dedicated place
        on screen (calculated from monitor resolution).

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
        """Return elements used in game.

        It contain list of allowed elements in game. At first load images from
        their directory then fill missing elements by drawing 2D figures
        picked from elements list according to game settings (amount).
        Returned elements are gathered in dictionary with their names and
        color code or image.
        """
        amount = self.settings['figures']
        images = self.get_images()
        if len(images) < amount:
            figures = self.adjust_elements(
                ['square', 'triangle', 'octagon', 'diamond'],
                amount - len(images)
            )
            return {**images, **figures}
        else:
            picked = sample(list(images), amount)
            return {x: images[x] for x in picked}


class Dynamic(Game):
    """
    Setup dynamic game.

    A class containing methods used in dynamic game mode. Sets environment for
    creating 3D figures and moves camera during gameplay. It extend `Game`
    class.

    ...

    Attributes
    ----------
    spawned_at : int
        camera Z value (how far from beginning it moved) - needed to create
        figures and make them visible
    """

    def prepare_environment(self):
        """Set basics needed to launch 3D game mode."""
        pygame.display.set_mode(
            self.resolution,
            DOUBLEBUF | OPENGL | pygame.FULLSCREEN
        )
        gluPerspective(45, (self.resolution[0] / self.resolution[1]), 0.1, 50)
        self.spawned_at = -10
        self.wave = self.create_wave(Wave3D, self.spawned_at)

    def run_game(self):
        """Spawn waves of 3D figures based on length of camera Z movement."""
        camera_z = self.move_view()
        if self.is_wave_finished(camera_z < self.spawned_at - 100):
            self.spawn_new_wave(camera_z)
        else:
            self.wave()

    def spawn_new_wave(self, z_position):
        """Remove old wave and spawn new one according to position of camera.

        Parameters
        ----------
        z_position : int
            value of camera Z - where it is moved
        """
        del self.wave
        self.wave = self.create_wave(Wave3D, z_position)
        self.spawned_at = z_position

    def move_view(self):
        """Responsible for camera movement, return z position."""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glTranslatef(0, 0, self.get_speed())
        camera_z = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)[3][2]
        return int(camera_z)

    def get_speed(self):
        """According to used platform adjust speed for moving camera."""
        s = self.settings['speed']
        return s / 5 - 0.15 * s if 'win' in platform else s / 5

    def set_elements(self):
        """From allowed figures return those which are picked to game."""
        return self.adjust_elements(
            ['Cube', 'Pyramid', 'Octahedron', 'Octagon'],
            self.settings['figures']
        )
