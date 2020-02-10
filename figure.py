"""Figure Module

This module contains figures representation both 2D (`pygame`) and 3D (`OpenGL`). It covers all necessary information as
points for 2D figures, edges, vertices, surfaces for 3D figures. It is also responsible for creating waves of elements
based on `random` module.

Module uses functions `choice`, `choices`, `randrange`, `randint`, `sample` from `random` module. `OpenGL.GL`, `pygame`,
`colors` are also in use. It is required to provide them before running application.

It contains classes:

    * Wave - covers general methods used both in Wave2D and Wave3D
    * Wave2D - specifies methods mandatory to create wave of figures in 2D
    * Wave3D - includes method to create wave of figures in 3D
    * Figure2D - has methods responsible for drawing figure in 2D with use of `pygame`
    * Figure3D - covers methods for drawing 3D figures with `OpenGL`
    * Cube - contains methods allowing to draw Cube in 3D
    * Octagon - contains methods allowing to draw Octagon in 3D
    * Octahedron - contains methods allowing to draw Octahedron in 3D
    * Pyramid - contains methods allowing to draw Pyramid in 3D

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
from OpenGL.GL import *
from random import choice, choices, randrange, randint, sample
import colors


class Wave:
    """
    A class with collection of the same methods needed both in Wave2D and Wave3D. It is base, responsible for creating
    wave of elements, iterating through its objects, counting and calling them (drawing).

    ...

    Attributes
    ----------
    figure_type : str
        name of figures which will be in the wave
    color : tuple or pygame.Surface or False
        RGB code of color for wave (0-1, 0-1, 0-1), False if each element in wave will have his own color or
        pygame.Surface in case if photo will be used as displayed element
    *args
        rest of parameters needed to create specified type of wave, see Wave2D and Wave3D

    Methods
    -------
    call()
        spawns (displays) wave on screen
    """

    def __init__(self, figure_type, color, *args):
        """
        Parameters
        ----------
        figure_type : str
            name of figures which will be in the wave
        color : tuple or pygame.Surface or False
            RGB code of color for wave (0-1, 0-1, 0-1), False if each element in wave will have his own color or
            pygame.Surface in case if photo will be used as displayed element
        *args
            rest of parameters needed to create specified type of wave, see Wave2D and Wave3D
        """
        self.figure = figure_type
        self.figures = []
        self.fill(color, *args)

    def __repr__(self):
        return f'<{self.__class__.__name__} of {self.__len__()} {self.figure.lower()}s>'

    def __iter__(self):
        return (x for x in self.figures)

    def __len__(self):
        return len(self.figures)

    def __call__(self):
        """Spawns (displays) wave on screen"""

        for figure in self: figure()


class Wave2D(Wave):
    """
    A class with methods needed to display 2D wave. It is responsible for calculating proper points on screen to display
    objects, setting their size, pick amount. Has description how 2D wave should be created. It is child of class Wave.

    ...

    Methods
    -------
    get_amount()
        randomly pick number of elements from 1 to 9 according to their weights
    get_mid_points(resolution)
        according to resolution of screen - tuple (width, height) divides screen into nine equal fields (net 3x3) and
        returns list with their middle points (width, height)
    get_figure_size(resolution)
        according to resolution of screen - tuple (width, height) returns integer with size of figure
    fill(color, screen, resolution)
        populates figures list with 2D figures objects binded to screen (`pygame.Surface`). Use wave color or photo if
        it is passed else pick random color for each element. Resolution is used to set figure size and region of screen
        where it will be displayed
    """

    @staticmethod
    def get_amount():
        """Randomly pick number of elements from 1 to 9 according to their weights."""

        return choices(range(1, 10), weights=[0.03, 0.1, 0.2, 0.2, 0.2, 0.15, 0.1, 0.01, 0.01])[0]

    @staticmethod
    def get_mid_points(resolution):
        """Divides screen in nine fields (net 3x3) and returns middle point of each field

        Parameters
        ----------
        resolution : tuple
            a tuple with two int values - width, height - according to resolution of used monitor

        Returns
        -------
        list
            a list with 9 positions (screen divided in net 3x3) - middle point of each part of divided screen
        """

        w, h = resolution
        return [(int(x), int(y)) for x in (w / 6, w / 2, w - w / 6) for y in (h / 6, h / 2, h - h / 6)]

    @staticmethod
    def get_figure_size(resolution):
        """Returns size of figure (used in drawing).

        Parameters
        ----------
        resolution : tuple
            a tuple with two int values - width, height - according to resolution of used monitor

        Returns
        -------
        int
            size of figure which will be drawn
        """

        w, h = resolution
        return int(min(w / 3, h / 3) / 4)

    def fill(self, color, screen, resolution):
        """Populates figures list

        2D figures objects are created and binded to screen (`pygame.Surface`). It uses wave color (RGB code
        (0-1, 0-1, 0-1) which is converted to (0-255, 0-255, 0-255)) or photo if it is passed else it picks random color
        for each element. Resolution is used to set figure size and region of screen where it will be displayed. Amount
        of elements in wave is picked randomly according to method get_amount().

        Parameters
        ----------
        color : tuple or pygame.Surface or False
            RGB color code represented as (0-1, 0-1, 0-1) values, pygame.Surface if each object will display photo or
            False in case when we don't want to create wave in solid color, but use random color for each object
        screen: pygame.Surface
            object representing game screen where created figures will be binded
        resolution : tuple
            a tuple with two int values - width, height - according to resolution of used monitor
        """

        for point in sample(self.get_mid_points(resolution), self.get_amount()):
            figure_color = color if color else colors.Random().get_color()
            if not isinstance(color, pygame.Surface):
                figure_color = colors.convert(figure_color)
            self.figures.append(Figure2D(screen, self.figure, figure_color, point, self.get_figure_size(resolution)))


class Wave3D(Wave):
    """
    A class with method allowing to create 3D wave -it fills figure list with proper objects. It is child of class Wave.

    ...

    Methods
    -------
    fill(color, position)
        populates figures list with 3D figures objects. Position Z of camera must be specified (how far from beginning
        figure will be drawn). It uses wave color if it is passed else picks random color for each element.
    """

    def fill(self, color, positionZ):
        """Populates figures list

        3D figures objects are created according to randomly generated number in range 2-6. It uses wave color (RGB code
        (0-1, 0-1, 0-1) if it is passed else it picks random color for each element. Figures are created in normal mode.
        Easter egg (for those who like to read documentation as I do): there is also available fire mode (see Figure3D
        fire @classmethod) which will simulate flames. Be aware that each object will be colored same way. Replace
        .normal with .fire in loop below - where objects are created.

        Parameters
        ----------
        color : tuple or False
            RGB color code represented as (0-1, 0-1, 0-1) or False in case when we don't want to create wave in solid
            color, but use random color for each object
        positionZ : int
            position of camera Z where figure will be drawn (how far from beginning - where camera started to move)
        """

        for _ in range(randint(2, 6)):
            figure_color = color if color else colors.Random().get_color()
            self.figures.append(eval(self.figure).normal(positionZ, figure_color))


class Figure2D:
    """
    A class with methods allowing to display 2D figures on screen.

    ...

    Attributes
    ----------
    screen: pygame.Surface
        object representing game screen where created figure will be binded
    figure : str
        name of created figure
    color : tuple or pygame.Surface
        RGB color code represented as (0-255, 0-255, 0-255) values, pygame.Surface if photo is used
    points : list
        list with points needed to draw figure

    Methods
    -------
    call()
        displays element on screen
    adjust_points(mid_point, size)
        according to type of created figure and its size adjusts points to draw it or returns proper point for placing
        photo on the screen
    get_diamond_points(mid_point, size)
        according to passed mid_point and size returns points to draw diamond
    get_square_points(mid_point, size)
        according to passed mid_point and size returns points to draw square
    get_triangle_points(mid_point, size)
        according to passed mid_point and size returns points to draw triangle
    get_octagon_points(mid_point, size)
        according to passed mid_point and size returns points to draw octagon
    """

    def __init__(self, screen, figure, color, mid_point, size):
        """
        Parameters
        ----------
        screen: pygame.Surface
            object representing game screen where created figure will be binded
        figure : str
            name of created figure
        color : tuple or pygame.Surface
            RGB color code represented as (0-255, 0-255, 0-255) values, pygame.Surface if photo is used
        mid_point : tuple
            center of figure - tuple with two elements - width and height
        size : int
            size of figure which will be drawn
        """

        self.screen = screen
        self.figure = figure
        self.color = color
        self.points = self.adjust_points(mid_point, size)

    def __repr__(self):
        return f'<{self.figure} with points: {self.points}>'

    def __call__(self):
        """Draws figure or displays photo on screen"""

        if isinstance(self.color, pygame.Surface):
            self.screen.blit(self.color, self.points)
        else:
            pygame.draw.polygon(self.screen, self.color, self.points)

    def adjust_points(self, mid_point, size):
        """Returns points needed to display element

        Parameters
        ----------
        mid_point : tuple
            center of figure - tuple with two elements - width and height
        size : int
            size of figure which will be drawn

        Returns
        -------
        list
            list with points needed to draw or display element on screen (each has width and height value)
        """

        if isinstance(self.color, pygame.Surface):
            w, h = self.color.get_size()
            return [int(mid_point[0] - w / 2), int(mid_point[1] - h / 2)]
        return eval('self.get_' + self.figure + '_points')(mid_point, size)

    @staticmethod
    def get_diamond_points(mid_point, size):
        """Returns points needed to draw diamond

        Parameters
        ----------
        mid_point : tuple
            center of figure - tuple with two elements - width and height
        size : int
            size of figure which will be drawn

        Returns
        -------
        list
            list with points needed to draw diamond on screen (each has width and height value)
        """

        x, y = mid_point
        s = size
        return [(x, y - s), (x - s, y), (x, y + s), (x + s, y)]

    @staticmethod
    def get_square_points(mid_point, size):
        """Returns points needed to draw square

        Parameters
        ----------
        mid_point : tuple
            center of figure - tuple with two elements - width and height
        size : int
            size of figure which will be drawn

        Returns
        -------
        list
            list with points needed to draw square on screen (each has width and height value)
        """

        x, y = mid_point
        s = size
        return [(x - s, y - s), (x - s, y + s), (x + s, y + s), (x + s, y - s)]

    @staticmethod
    def get_triangle_points(mid_point, size):
        """Returns points needed to draw triangle

        Parameters
        ----------
        mid_point : tuple
            center of figure - tuple with two elements - width and height
        size : int
            size of figure which will be drawn

        Returns
        -------
        list
            list with points needed to draw triangle on screen (each has width and height value)
        """

        x, y = mid_point
        s = size
        return [(x - s, y + s), (x + s, y + s), (x, y - s)]

    @staticmethod
    def get_octagon_points(mid_point, size):
        """Returns points needed to draw octagon

        Parameters
        ----------
        mid_point : tuple
            center of figure - tuple with two elements - width and height
        size : int
            size of figure which will be drawn

        Returns
        -------
        list
            list with points needed to draw octagon on screen (each has width and height value)
        """

        x, y = mid_point
        s = size
        return [(x - s, y + s / 2), (x - s, y - s / 2), (x - s / 2, y - s), (x + s / 2, y - s), (x + s, y - s / 2),
                (x + s, y + s / 2), (x + s / 2, y + s), (x - s / 2, y + s)]


class Figure3D:
    """
    A class with methods allowing to display 3D figures on screen.

    ...

    Attributes
    ----------
    color : tuple
        RGB color code represented as (0-1, 0-1, 0-1) values
    mode : OpenGL.constant.IntConstant
        mode used to draw figures in 3D - GL_LINES or GL_QUADS
    operation : function
        method used in specified mode to provide values needed to draw figure - get_edges or get_surfaces
    vertices : list
        list filled with vertices needed to draw figure

    Methods
    -------
    call()
        displays figure on screen
    normal(positionZ, color)
        sets class parameters to draws contour of figure in set color
    fire(positionZ)
        sets class parameters to draws full figure with color movement imitating flame
    get_random_shift(positionZ)
        returns adjusted point according to moving camera
    adjust_vertices(point)
        returns adjusted figure vertices according to set point
    """

    def __init__(self, positionZ, color, mode, operation):
        """
        Parameters
        ----------
        positionZ : int
            position of camera Z where figure will be drawn (how far from beginning - where camera started to move)
        color : tuple
            RGB color code represented as (0-1, 0-1, 0-1) values
        mode : OpenGL.constant.IntConstant
            mode used to draw figures in 3D - GL_LINES or GL_QUADS
        operation : function
            method used in specified mode to provide values needed to draw figure - get_edges or get_surfaces
        """

        self.color = color
        self.mode = mode
        self.operation = operation
        self.vertices = self.adjust_vertices(self.get_random_shift(positionZ))

    def __repr__(self):
        return f'<{self.__class__.__name__} with vertices: {self.vertices}>'

    def __call__(self):
        """Displays figure on screen"""

        glBegin(self.mode)
        for element in self.operation():
            for vertex in element:
                color = choice(self.color) if all([isinstance(x, tuple) for x in self.color]) else self.color
                glColor3fv(color)
                glVertex3fv(self.vertices[vertex])
        glEnd()

    @classmethod
    def normal(cls, positionZ, color, *args):
        """Sets class parameters to draws contour of figure in set color"""

        return cls(positionZ, color, GL_LINES, cls.get_edges)

    @classmethod
    def fire(cls, positionZ, *args):
        """Sets class parameters to draws full figure with color movement imitating flame"""

        return cls(positionZ, ((0.5, 0, 0), (1, 0.5, 0)), GL_QUADS, cls.get_surfaces)

    @staticmethod
    def get_random_shift(positionZ):
        """Returns adjusted point according to moving camera


        Parameters
        ----------
        positionZ : int
            position of camera Z where figure will be drawn (how far from beginning - where camera started to move)

        Returns
        -------
        tuple
            containing x, y, z randomized values for point where figure will be drawn
        """

        x = choice((-1, 1)) * randrange(2, 10)
        y = choice((-1, 1)) * randrange(2, 10)
        z = randrange(int(positionZ - 90), int(positionZ - 60))
        return x, y, z

    def adjust_vertices(self, point):
        """Returns adjusted figure vertices according to set point

        Parameters
        ----------
        point : tuple
            tuple with x, y, z value - position where figure will be drawn

        Returns
        -------
        list
            containing new vertices values allowing to draw 3D figure
        """

        new_vertices = []
        for vertice in self.get_vertices():
            new = []
            new.append(vertice[0] + point[0])
            new.append(vertice[1] + point[1])
            new.append(vertice[2] + point[2])
            new_vertices.append(new)
        return new_vertices


class Cube(Figure3D):
    """
    A class representing cube. It is children of Figure3D.

    ...


    Methods
    -------
    get_vertices()
        returns tuple with points later processed to draw figure
    get_edges()
        returns tuple with connections between vertices - allowing to draw contour of figure
    get_surfaces()
        returns tuple with connections between vertices - allowing to draw full figure

    """

    @staticmethod
    def get_vertices():
        return (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)
        )

    @staticmethod
    def get_edges():
        return (
            (0, 1),
            (0, 3),
            (0, 4),
            (2, 1),
            (2, 3),
            (2, 7),
            (6, 3),
            (6, 4),
            (6, 7),
            (5, 1),
            (5, 4),
            (5, 7)
        )

    @staticmethod
    def get_surfaces():
        return (
            (0, 1, 2, 3),
            (3, 2, 7, 6),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 7, 2),
            (4, 0, 3, 6)
        )


class Octagon(Figure3D):
    """
    A class representing octagon. It is children of Figure3D.

    ...


    Methods
    -------
    get_vertices()
        returns tuple with points later processed to draw figure
    get_edges()
        returns tuple with connections between vertices - allowing to draw contour of figure
    get_surfaces()
        returns tuple with connections between vertices - allowing to draw full figure

    """

    @staticmethod
    def get_vertices():
        return (
            (-0.25, 0, -0.5),
            (0.25, 0, -0.5),
            (0.5, 0, -0.25),
            (0.5, 0, 0.25),
            (0.25, 0, 0.5),
            (-0.25, 0, 0.5),
            (-0.5, 0, 0.25),
            (-0.5, 0, -0.25),
            (-0.25, 1, -0.5),
            (0.25, 1, -0.5),
            (0.5, 1, -0.25),
            (0.5, 1, 0.25),
            (0.25, 1, 0.5),
            (-0.25, 1, 0.5),
            (-0.5, 1, 0.25),
            (-0.5, 1, -0.25)
        )

    @staticmethod
    def get_edges():
        return (
            (0, 7),
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (8, 15),
            (8, 9),
            (9, 10),
            (10, 11),
            (11, 12),
            (12, 13),
            (13, 14),
            (14, 15),
            (0, 8),
            (1, 9),
            (2, 10),
            (3, 11),
            (4, 12),
            (5, 13),
            (6, 14),
            (7, 15)
        )

    @staticmethod
    def get_surfaces():
        return (
            (9, 8, 11, 10, 12, 15, 8, 11, 13, 12, 15, 14),
            (1, 0, 3, 2, 4, 7, 0, 3, 5, 4, 7, 6),
            (0, 1, 9, 8),
            (1, 2, 10, 9),
            (2, 3, 11, 10),
            (3, 4, 12, 11),
            (4, 5, 13, 12),
            (5, 6, 14, 13),
            (6, 7, 15, 14),
            (7, 15, 8, 0)
        )


class Octahedron(Figure3D):
    """
    A class representing octahedron. It is children of Figure3D.

    ...


    Methods
    -------
    get_vertices()
        returns tuple with points later processed to draw figure
    get_edges()
        returns tuple with connections between vertices - allowing to draw contour of figure
    get_surfaces()
        returns tuple with connections between vertices - allowing to draw full figure

    """

    @staticmethod
    def get_vertices():
        return (
            (0, 1, 0),
            (-0.5, 0, -0.5),
            (0.5, 0, -0.5),
            (0.5, 0, 0.5),
            (-0.5, 0, 0.5),
            (0, -1, 0)
        )

    @staticmethod
    def get_edges():
        return (
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),
            (5, 1),
            (5, 2),
            (5, 3),
            (5, 4)
        )

    @staticmethod
    def get_surfaces():
        return (
            (0, 1, 2),
            (0, 3, 2),
            (0, 4, 3),
            (0, 4, 1),
            (5, 1, 2),
            (5, 3, 2),
            (5, 4, 3),
            (5, 4, 1)
        )


class Pyramid(Figure3D):
    """
    A class representing pyramid. It is children of Figure3D.

    ...


    Methods
    -------
    get_vertices()
        returns tuple with points later processed to draw figure
    get_edges()
        returns tuple with connections between vertices - allowing to draw contour of figure
    get_surfaces()
        returns tuple with connections between vertices - allowing to draw full figure

    """

    @staticmethod
    def get_vertices():
        return (
            (0, 1, 0),
            (-1, -1, -1),
            (1, -1, -1),
            (1, -1, 1),
            (-1, -1, 1)
        )

    @staticmethod
    def get_edges():
        return (
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1)
        )

    @staticmethod
    def get_surfaces():
        return (
            (0, 1, 2),
            (0, 3, 2),
            (0, 4, 3),
            (0, 4, 1),
            (1, 2, 3, 4)
        )
