"""Application Color Module

This module defines colors used in application. They are represented as (0-1, 0-1, 0-1) or (0-255, 0-255, 0-255)
(r, g, b) values. Module allows for conversion from 0-1 color code to 0-255. 0-1 representation is used with 3D figures
created via `OpenGL`. 0-255 is used by `pygame`.

Module uses functions `choice` and `sample` from `random` module. It is required to provide them before running
application.

It contains data:

    * COLORS - dictionary with colors names as keys and their RGB (0-1, 0-1, 0-1) representation

functions:

    * pick - returns colors values based on game setting
    * convert - gets RGB (0-1, 0-1, 0-1) color code as parameter and returns this color in RGB (0-255, 0-255, 0-255)
    format.
    * get_menu_colors - returns tuple with colors codes for element which is inactive and active (mouse over element)
    * get_backround_color - returns color code of background used in menu of application
    * get_logo_color - returns color code for application logo
    * get_rate_color - returns tuple with incorrect and correct colors codes used in summary menu for counting
    occurrence of elements

and class:

    * Random - stores last used color name (default grey) and method responsible for picking one random color
    (different than last used).

License:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from random import choice, sample

COLORS = {
    'Green': (0, 1, 0),
    'Orange': (1, 0.5, 0),
    'Red': (0.8, 0, 0),
    'Blue': (0, 0, 1),
    'Yellow': (1, 1, 0),
    'Violet': (1, 0, 1),
    'Grey': (0.5, 0.5, 0.5)
}


def pick(setting, amount):
    """Returns colors values based on game setting

    Parameters
    ----------
    setting : str
        Color difficulty level. Should be one of following: Easy, Medium, Hard.
    amount: int
        Number of elements picked to game.

    Returns
    -------
    list
        a list of unique colors codes in RGB format (0-1, 0-1, 0-1) with a length given in parameter amount when
        setting is Easy. Ensures always the same color for wave made with elements of exact type.
    True
        when setting is Medium. Ensures picking one random color for each wave of elements.
    False
        when setting is Hard. Ensures that each element in wave will have random color.
    """

    if setting == 'Easy':
        colors = sample(COLORS.keys(), amount)
        return [COLORS[x] for x in colors]
    return True if setting == 'Medium' else False


def convert(color):
    """Gets (0-1, 0-1, 0-1) RGB color code and converts it to (0-255, 0-255, 0-255).

    Parameters
    ----------
    color : tuple
        RGB code in format (0-1, 0-1, 0-1)

    Returns
    -------
    list
        a list representing RBG color code in format (0-255, 0-255, 0-255)
    """

    return [int(x * 255) for x in color]


def get_menu_colors():
    """Returns colors used in menu

    Returns tuple with inactive [0] and active [1] color code in RGB format (0-255, 0-255, 0-255). Where active means
    mouse over colored element in application menu. Those colors are used for creating labels and buttons. Dark and
    Light yellow applied.
    """

    return (255, 204, 0), (255, 255, 0)


def get_background_color():
    """Returns color of background used in application menu. RGB format (0-255, 0-255, 0-255). Grey applied."""

    return (50, 50, 50)


def get_logo_color():
    """Returns color of logo used in application main menu. RGB format (0-255, 0-255, 0-255). Orange applied."""

    return (255, 128, 0)


def get_rate_colors():
    """Returns colors of result check

    Returns tuple with incorrect [0] and correct [1] color code in RGB format (0-255, 0-255, 0-255). They are used to
    highlight result of game filled by user with actual result. It occurs by pressing submit button in summary menu.
    Red and green applied.
    """

    return (220, 0, 0), (0, 180, 0)


class Random:
    """
    A class used to choose random color different than last one picked.

    ...

    Attributes
    ----------
    active_color : str
        string containing color picked last time (default grey)

    Methods
    -------
    get_random_color()
        Picks one random color (different than last choice) from dictionary and returns its RGB code.
    """

    def __init__(self):
        """Sets attribute active_color to grey."""

        self.active_color = 'Grey'

    def __repr__(self):
        return f'<One color code of {[x for x in COLORS.keys() if not x == self.active_color]} picked randomly>'

    def get_color(self):
        """Returns random color

        Picks one color from COLORS different than active_color (color chosen last time). Updates active_color
        and returns picked color code in RGB format (0-1, 0-1, 0-1).
        """

        colors = list(filter((lambda x: self.active_color not in x), COLORS))
        self.active_color = choice(colors)
        return COLORS[self.active_color]
