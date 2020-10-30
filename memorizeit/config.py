"""#### Config

This module allows to load and store game settings in file. It is responsible
for checking if stored data was correct and eventually replace it with default
value. It also handles `pygame` events and executes passed code in proper loop
based on condition. Modules used: `json`, `pygame` and `sys`.

License:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from json import dumps, loads
import sys

import pygame
from pygame.locals import KEYDOWN, K_ESCAPE


class Config:
    """
    A class used to load, check and store game settings in file.

    ...

    Attributes
    ----------
    config_file : str
        string containing configuration file path
    settings : dict
        dictionary with loaded and checked settings
    """

    def __init__(self):
        """Load, check and store settings.

        It has defined config_file name. Settings are loaded from this file.
        Then they are checked with default values. Correct settings are kept
        in variable and saved to file (to replace corrupted data if there were
        any wrong values).
        """
        self.config_file = 'memorizeit/settings.json'
        self.range = {
            'figures': (2, 3, 4),
            'time': tuple((x for x in range(5, 61, 5))),
            'speed': (1, 2, 3, 4),
            'colors': ('Easy', 'Medium', 'Hard'),
            'sound': ('Off', 'On')
        }
        self.settings = self.check_content(self.get_content())
        self.save(self.settings)

    def __repr__(self):
        """Return `Config` class representation."""
        return f'<Configuration with values: {self.settings}>'

    def check_content(self, content):
        """Return dictionary with correct values of settings.

        It iterates through default dictionary and compares values passed in
        content with allowed values. If value is accepted function replaces
        default value. Modified dictionary is returned.

        Parameters
        ----------
        content : dict
            a dictionary which will be checked

        Returns
        -------
        dict
            a dictionary with correct settings
        """
        default = {
            'figures': 3,
            'time': 60,
            'speed': 2,
            'colors': 'Medium',
            'sound': 'Off'
        }
        for key in default:
            try:
                if content[key] in self.range[key]:
                    default[key] = content[key]
            except (KeyError, TypeError):
                pass
        return default

    def get_content(self):
        """Return content of configuration file or False in case of error."""
        try:
            with open(self.config_file, 'r') as config:
                return loads(config.read())
        except (FileNotFoundError, ValueError):
            return False

    def save(self, settings):
        """Save passed settings to configuration file.

        Parameters
        ----------
        settings : dict
            dictionary settings which will be saved to configuration file
        """
        self.settings = settings
        with open(self.config_file, 'w') as config:
            config.write(dumps(self.settings))

    def get_settings(self):
        """Return correct settings in dictionary.

        Which are previously checked and loaded from configuration file.
        """
        return self.settings


class Handler:
    """
    A class responsible for handling `pygame` events.

    Running passed function in loop based on set condition.

    ...

    Attributes
    ----------
    function : function
        function which will be run inside loop
    condition : function
        function which return True or False based on its condition

    Methods
    -------
    call()
        loops passed functions and handles `pygame` events
    stop()
        breaks loop and stops Handler from running
    """

    def __init__(self, function, condition=lambda: True):
        """Initialize event handler.

        Parameters
        ----------
        function : function
            function which will be run inside loop
        condition : function, optional
            function which return True or False based on its condition
            (default is lambda: True)
        """
        self.function = function
        self.condition = condition

    def __repr__(self):
        """Return `Handler` class representation."""
        return f'<Pygame event handler with {self.function} in loop.'

    def __call__(self):
        """Loops passed functions and handles `pygame` events."""
        while self.condition():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.function.__class__.__name__ == 'Menu':
                            pygame.quit()
                            sys.exit()
                        self.stop()
            self.function()

            try:
                pygame.display.update()
            except pygame.error:
                pygame.display.flip()

    def stop(self):
        """Break loop and stop `Handler` from running."""
        self.condition = lambda: False
