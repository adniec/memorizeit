"""Graphical User Interface Module

This module is responsible for creating and interacting between different
menus. It contains methods responsible for making button or displaying label,
animating them. Here is defined size (width, height) of application. It chains
elements showed to user with proper functions from other modules. On general
class Gui are based: main, settings and summary menus. Modules used:
`collections`, `pathlib`, `pygame`, `sys`.

License:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from collections import namedtuple
from pathlib import Path
import sys

import pygame

from memorizeit import colors
from memorizeit.config import Config, Handler
from memorizeit.game import Dynamic, Static


class Gui:
    """
    A class collecting general methods which are used in different menus.

    Responsible for drawing buttons, displaying labels and background. It also
    controls interaction between mouse and elements on the screen.

    ...

    Attributes
    ----------
    display : tuple
        a tuple with two int values - width, height - size of application
    screen : pygame.Surface
        `pygame.Surface` where we draw or bind displayed elements in each menu
    colors : tuple
        contains two color codes in RGB (0-255, 0-255, 0-255) format. On place
        0 is inactive color for interactive elements away of mouse cursor. On
        place 1 is active color for interactive elements under mouse cursor.
    Dimensions : namedtuple
        allows to created namedtuple with size of element - x values from and
        to, y values from and to.
    text_size : int
        specifies size of text used in buttons and labels
    """

    def __init__(self):
        """Set basic information used in each menu."""
        self.display = (800, 600)
        self.screen = pygame.display.set_mode(self.display)
        self.colors = colors.get_menu_colors()
        self.Dimensions = namedtuple('Dimensions',
                                     ('x_from', 'x_to', 'y_from', 'y_to'))
        self.text_size = 25
        self.blit_background()

    def blit_background(self):
        """Set menu color to default, display logo and application name."""
        self.screen.fill(colors.get_background_color())

        size = self.text_size * 5
        if not self.display[0] >= 800:
            size = int(size * self.display[0] / 1000)

        self.create_label(
            'MemorizeIT',
            (self.display[0] // 2, size),
            colors.get_logo_color(),
            size
        )
        try:
            image = self.adjust_image()
            size = image.get_size()
            self.screen.blit(image, (0, self.display[1] - size[1]))
        except pygame.error:
            pass

    def adjust_image(self):
        """Convert logo image to appropriate size."""
        path = Path(__file__).parent.absolute() / 'img' / 'logo.png'
        image = pygame.image.load(str(path))
        size = image.get_size()[0]
        display = min(self.display)

        if display - size - 180 < 0:
            size = [int(display * 0.7)] * 2
            image = pygame.transform.scale(image, size)
        return image

    def animate_element(self, point, dimensions, function,
                        arguments=None, button=False, message=''):
        """Highlight element when mouse is over (use active color [1]).

        Parameters
        ----------
        point : tuple
            a tuple with two int values - width, height allowing to draw
            animated element
        dimensions : namedtuple
            namedtuple with size of area - x values from and to, y values from
            and to. Moving cursor over this area will animate element and
            clicking will run passed function
        function : function
            function used during mouse click in set area
        arguments : list, None, optional
            a list with arguments passed to function if they are needed
            (default is None - function without arguments)
        button : str, bool, optional
            specifies what type of button will be animated (True - with
            border, False - only label, left or right - arrow with set
            direction (default is False - label)
        message : str, optional
            text used in animated button (default is '' which means empty - no
            text at all, used with arrow buttons)
        """
        if self.is_mouse_over(dimensions):
            if button:
                if button == 'left':
                    self.draw_triangle(self.colors[1], point)
                elif button == 'right':
                    self.draw_triangle(self.colors[1], point, left=False)
                else:
                    self.draw_button(message, self.colors[1], point)
            else:
                self.create_label(message, point, self.colors[1])
            self.use_on_click(function, arguments)

    @staticmethod
    def is_mouse_over(dimensions):
        """Specify if mouse is over area.

        Parameters
        ----------
        dimensions : namedtuple
            namedtuple with size of area - x values from and to, y values from
            and to

        Returns
        -------
        bool
            True when mouse cursor is over set area else False
        """
        mouse = pygame.mouse.get_pos()
        if dimensions.x_from < mouse[0] < dimensions.x_to:
            if dimensions.y_from < mouse[1] < dimensions.y_to:
                return True
        return False

    @staticmethod
    def use_on_click(function, arguments):
        """Use function when mouse button is pressed.

        Parameters
        ----------
        function : function
            function used when mouse button is pressed
        arguments : list, None, optional
            a list with arguments passed to function or None if function
            doesn't require arguments
        """
        if pygame.mouse.get_pressed()[0]:
            function(*arguments) if arguments else function()
            pygame.time.delay(100)

    def create_arrows(self, point, position, gap,
                      value, left_condition, right_condition, function):
        """Draw and animates arrows buttons according to set conditions.

        Parameters
        ----------
        point : tuple
            a tuple with two int values - width, height allowing to draw and
            animate element
        position : str
            name of setting which arrows are chained to (to decrease, increase
            proper value)
        gap : int
            distance between arrows
        value : int
            index of showed option - compared with conditions to animate arrow
            or not
        left_condition : int
            index of side option on the left - until which left arrow will be
            animated
        right_condition : int
            index of side option on the right - until which right arrow will
            be animated
        function : function
            function used during mouse click on animated element
        """
        new_point = [point[0] - gap // 2, point[1]]
        left = self.draw_triangle(self.colors[0], new_point)
        if value > left_condition:
            self.animate_element(
                new_point, left, function, [position, False], 'left'
            )

        new_point[0] += gap
        right = self.draw_triangle(self.colors[0], new_point, False)
        if value < right_condition:
            self.animate_element(
                new_point, right, function, [position], 'right'
            )

    def draw_triangle(self, color, point, left=True):
        """Draw triangle on the screen.

        Parameters
        ----------
        color : tuple
            RGB color code in format (0-255, 0-255, 0-255)
        point : tuple
            a tuple with two int values - width, height specifies where
            triangle will be drawn
        left : bool, optional
            parameter specifying which side triangle will be pointed (default
            is True - left side)

        Returns
        -------
        Dimensions
            namedtuple with size of triangle - x values from and to, y values
            from and to
        """
        dimensions = self.Dimensions(
            point[0] - 10, point[0], point[1] - 10, point[1] + 10
        )
        coordinates = [(dimensions.x_to, point[1])]
        x = 'x_from'
        if left:
            dimensions = self.Dimensions(
                point[0], point[0] + 10, point[1] - 10, point[1] + 10
            )
            x = 'x_to'
        coordinates.extend([(getattr(dimensions, x), dimensions.y_from),
                            (getattr(dimensions, x), dimensions.y_to)])
        pygame.draw.polygon(self.screen, color, coordinates)
        return dimensions

    def create_button(self, message,
                      point, function, arguments=None, border=False):
        """Draw and animates button.

        Parameters
        ----------
        message : str
            text displayed in button
        point : tuple
            a tuple with two int values - width, height specifies where button
            will be drawn
        left : bool, optional
            parameter specifying which side triangle will be pointed (default
            is True - left side)
        function : function
            function used when button is pressed
        arguments : list, None, optional
            a list with arguments passed to function if they are needed
            (default is None - function without arguments)
        border : bool
            specifies if button is surrounded by border (True) or is just a
            label (default False - label)
        """
        if border:
            button = self.draw_button(message, self.colors[0], point)
        else:
            button = self.create_label(message, point)
        self.animate_element(
            point, button, function, arguments, border, message
        )

    def draw_button(self, message, color, point):
        """Draw button on the screen.

        Parameters
        ----------
        message : str
            text displayed in button
        color : tuple
            RGB color code in format (0-255, 0-255, 0-255)
        point : tuple
            a tuple with two int values - width, height specifies where
            button will be drawn

        Returns
        -------
        Dimensions
            namedtuple with size of button - x values from and to, y values
            from and to
        """
        border = self.draw_border(color, point)
        mid_point = ((border.x_from + border.x_to) // 2,
                     (border.y_from + border.y_to) // 2)
        self.create_label(message, mid_point, color, int(self.text_size * 1.5))
        return border

    def create_label(self, message, mid_point, color=None, size=None):
        """Display text on the screen.

        Parameters
        ----------
        message : str
            text displayed as label
        mid_point : tuple
            a tuple with two int values - width, height specifies middle point
            of text which will be displayed
        color : tuple, None, optional
             RGB color code in format (0-255, 0-255, 0-255) or None if
             inactive color from colors attribute [0] should
             be used (default is None)
        size : int, None, optional
            size of displayed text or None if text should use text_size
            attribute (default is None)
        """
        if color is None:
            color = self.colors[0]

        if size is None:
            size = self.text_size

        text = pygame.font.SysFont('carlito', size, True).render(message,
                                                                 True, color)
        x_shift = text.get_width() // 2
        y_shift = text.get_height() // 2

        self.screen.blit(text, (mid_point[0] - x_shift,
                                mid_point[1] - y_shift))

        return self.Dimensions(mid_point[0] - x_shift,
                               mid_point[0] + x_shift,
                               mid_point[1] - y_shift,
                               mid_point[1] + y_shift)

    def draw_border(self, color, point):
        """Draw border surrounding set point.

        Parameters
        ----------
        color : tuple
            RGB color code in format (0-255, 0-255, 0-255)
        point : tuple
            a tuple with two int values - width, height specifies where
            border will be drawn

        Returns
        -------
        Dimensions
            namedtuple with size of border - x values from and to, y values
            from and to
        """
        width = self.text_size * 10
        height = self.text_size * 2
        border = pygame.Rect(point[0], point[1], width, height)

        pygame.draw.rect(self.screen, color, border, self.text_size // 10)

        return self.Dimensions(point[0],
                               point[0] + width,
                               point[1],
                               point[1] + height)


class Menu(Gui):
    """
    A class responsible for displaying main menu of application.

    It extends Gui class.

    ...

    Attributes
    ----------
    resolution : tuple
        a tuple with two int values - width, height - size of display
        resolution
    positions : dict
        a dictionary with names of displayed buttons and corresponding to them
        classes or functions


    Methods
    -------
    call()
        draws and animates elements on screen - it is send to `pygame` event
        handler class to run in loop
    close()
        shuts down application
    """

    def __init__(self):
        """Initialize main menu."""
        self.resolution = (pygame.display.Info().current_w,
                           pygame.display.Info().current_h)
        self.positions = {
            'New game': Dynamic,
            'Static game': Static,
            'Settings': Settings,
            'Exit': self.close
        }
        super().__init__()
        Handler(self)()

    def __call__(self):
        """Draw and animate menu buttons.

        It chains to them proper classes or functions. Displays background
        used in application. This method is send to `pygame` event handler
        class to run in loop.
        """
        self.blit_background()
        point = tuple(x - 325 for x in self.display)

        for gap, position in enumerate(self.positions):
            gap *= 70
            new_point = (point[0], point[1] + gap)
            arguments = [self.resolution] if 'game' in position else []

            self.create_button(position, new_point,
                               self.positions[position], arguments, True)

    @staticmethod
    def close():
        """Shut down application."""
        pygame.quit()
        sys.exit()


class Settings(Gui):
    """
    A class responsible for displaying settings menu of application.

    It extends Gui class.

    ...

    Attributes
    ----------
    config : Config
        object from config module used to load and save settings
    settings : dict
        a dictionary with settings loaded from config
    range : dict
        a dictionary with allowed values for each setting
    run : Handler
        object from config module allowing for handling `pygame` events.
        Chained to run variable for communication.
    """

    def __init__(self):
        """Initialize settings menu."""
        super().__init__()
        self.config = Config()
        self.run = Handler(self)
        self.run()

    def __call__(self):
        """Draw and animates elements in settings menu.

        According to loaded settings it takes each name stored there and
        creates label, arrows for increasing or decreasing setting value and
        displays in between them. This method is send to `pygame` event
        handler class to run in loop.
        """
        self.blit_background()
        point = (self.display[0] - 150, self.display[1] - 375)

        for position in self.config.settings:
            point = (point[0], point[1] + 50)
            self.create_label(position.capitalize() + ':',
                              (point[0] - 150, point[1]))
            text = str(self.config.settings[position])
            self.create_label(text, point)

            scope = self.config.range[position]
            index = scope.index(self.config.settings[position])
            self.create_arrows(
                point, position, 150, index, 0,
                len(self.config.range[position]) - 1,
                self.change_setting
            )

        point = (self.display[0] - 75, self.display[1] - 50)
        self.create_button(
            'Back', point,
            lambda: self.run.stop(),
            self.config.save(self.config.settings)
        )

    def change_setting(self, position, add=True):
        """Set displayed setting to lower or higher value.

        According to specified position (name of setting) and operation:
        addition or subtraction - it takes next or previous setting from range
        attribute.

        Parameters
        ----------
        position : str
            name of setting which will be increased or decreased
        add : bool, optional
            True if value will be increased, False when decreased (default is
            True)
        """
        scope = self.config.range[position]
        index = scope.index(self.config.settings[position])
        modify = index + 1 if add else index - 1
        self.config.settings[position] = self.config.range[position][modify]


class Summary(Gui):
    """
    A class responsible for displaying summary menu of gameplay.

    It extends Gui class.

    ...

    Attributes
    ----------
    result : dict
       a dictionary with names and numbers of elements spawned during game
    counted : dict
       a dictionary with values filled by user
    submitted : bool
       value specifying if user pressed submit button to check his result
    run : Handler
       object from config module allowing for handling `pygame` events.
       Chained to run variable for communication.


    Methods
    -------
    call()
        draws and animates elements on screen - it is send to `pygame` event
        handler class to run in loop
    change_counter(position, add)
        method used to increase or decrease number of element filled by user.
        It is send to create_arrows method
    submit()
        changes submitted attribute to False which changes menu and highlight
        correct values
    """

    def __init__(self, result):
        """Initialize summary menu.

        Parameters
        ----------
        result : dict
            a dictionary with names and numbers of elements spawned during game
        """
        super().__init__()
        self.result = result
        self.counted = {key: 0 for key in result}
        self.submitted = False
        self.run = Handler(self)
        self.run()

    def __call__(self):
        """Draw and animate elements on screen.

        Responsible for interaction with user - allows to enter his results
        and compare them with correct ones. Colors module is used to verify
        numbers - it marks wrong values with red color and good with green.
        This method is send to `pygame` event handler class to run in loop.
        """
        self.screen.fill(colors.get_background_color())
        self.create_label('Check your result:',
                          (self.display[0] // 2, 75), size=50)
        point = (self.display[0] // 2, 100)

        for position in self.counted:
            point = (point[0], point[1] + 50)
            self.create_label(position.capitalize() + 's:',
                              (point[0] - 125, point[1]))
            text = str(self.counted[position])

            if self.submitted:
                color = colors.get_rate_colors()
                if self.result[position] == self.counted[position]:
                    color = color[1]
                else:
                    self.create_label(str(self.result[position]),
                                      (point[0] + 175, point[1]), color[1])
                    color = color[0]

                self.create_label(text, (point[0] + 100, point[1]), color)
            else:
                self.create_label(text, (point[0] + 100, point[1]))
                self.create_arrows(
                    (point[0] + 100, point[1]), position, 150,
                    self.counted[position], 0, 99, self.change_counter
                )

        point = [self.display[0] - 175, self.display[1] - 50]
        if not self.submitted:
            self.create_button('Submit', point, self.submit)
        point[0] += 100
        self.create_button('Back', point, self.run.stop)

    def change_counter(self, position, add=True):
        """Set displayed occurrence of element to lower or higher value.

        Parameters
        ----------
        position : str
            name of element which number will be changed
        add : bool, optional
            True if value will be increased, False when decreased (default is
            True)
        """
        self.counted[position] += 1 if add else -1

    def submit(self):
        """Submit user answer and proceed to check."""
        self.submitted = True
