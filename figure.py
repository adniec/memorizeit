import pygame
from OpenGL.GL import *
from random import choice, choices, randrange, randint, sample
import colors


class Wave:

    def __init__(self, figure_type, color, *args):
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
        for figure in self: figure()


class Wave2D(Wave):

    @staticmethod
    def get_amount():
        return choices(range(1, 10), weights=[0.03, 0.1, 0.2, 0.2, 0.2, 0.15, 0.1, 0.01, 0.01])[0]

    @staticmethod
    def get_mid_points(resolution):
        w, h = resolution
        return [(int(x), int(y)) for x in (w / 6, w / 2, w - w / 6) for y in (h / 6, h / 2, h - h / 6)]

    @staticmethod
    def get_figure_size(resolution):
        w, h = resolution
        return int(min(w / 3, h / 3) / 4)

    def fill(self, color, screen, resolution):
        for point in sample(self.get_mid_points(resolution), self.get_amount()):
            figure_color = color if color else colors.Random().get_color()
            if not isinstance(color, pygame.Surface):
                figure_color = colors.convert(figure_color)
            self.figures.append(Figure2D(screen, self.figure, figure_color, point, self.get_figure_size(resolution)))


class Wave3D(Wave):

    def fill(self, color, positionZ):
        for _ in range(randint(2, 6)):
            figure_color = color if color else colors.Random().get_color()
            self.figures.append(eval(self.figure).normal(positionZ, figure_color))


class Figure2D:

    def __init__(self, screen, figure, color, mid_point, size):
        self.screen = screen
        self.figure = figure
        self.color = color
        self.points = self.adjust_points(mid_point, size)

    def __repr__(self):
        return f'<{self.figure} with points: {self.points}>'

    def __call__(self):
        if isinstance(self.color, pygame.Surface):
            self.screen.blit(self.color, self.points)
        else:
            pygame.draw.polygon(self.screen, self.color, self.points)

    def adjust_points(self, mid_point, size):
        if isinstance(self.color, pygame.Surface):
            w, h = self.color.get_size()
            return [int(mid_point[0] - w / 2), int(mid_point[1] - h / 2)]
        return eval('self.get_' + self.figure + '_points')(mid_point, size)

    @staticmethod
    def get_diamond_points(mid_point, size):
        x, y = mid_point
        s = size
        return [(x, y - s), (x - s, y), (x, y + s), (x + s, y)]

    @staticmethod
    def get_square_points(mid_point, size):
        x, y = mid_point
        s = size
        return [(x - s, y - s), (x - s, y + s), (x + s, y + s), (x + s, y - s)]

    @staticmethod
    def get_triangle_points(mid_point, size):
        x, y = mid_point
        s = size
        return [(x - s, y + s), (x + s, y + s), (x, y - s)]

    @staticmethod
    def get_octagon_points(mid_point, size):
        x, y = mid_point
        s = size
        return [(x - s, y + s / 2), (x - s, y - s / 2), (x - s / 2, y - s), (x + s / 2, y - s), (x + s, y - s / 2),
                (x + s, y + s / 2), (x + s / 2, y + s), (x - s / 2, y + s)]


class Figure3D:

    def __init__(self, positionZ, color, mode, operation):
        self.color = color
        self.mode = mode
        self.operation = operation
        self.vertices = self.adjust_vertices(self.get_random_shift(positionZ))

    def __repr__(self):
        return f'<{self.__class__.__name__} with vertices: {self.vertices}>'

    def __call__(self):
        glBegin(self.mode)
        for element in self.operation():
            for vertex in element:
                color = choice(self.color) if all([isinstance(x, tuple) for x in self.color]) else self.color
                glColor3fv(color)
                glVertex3fv(self.vertices[vertex])
        glEnd()

    @classmethod
    def normal(cls, positionZ, color, *args):
        return cls(positionZ, color, GL_LINES, cls.get_edges)

    @classmethod
    def fire(cls, positionZ, *args):
        return cls(positionZ, ((0.5, 0, 0), (1, 0.5, 0)), GL_QUADS, cls.get_surfaces)

    @staticmethod
    def get_random_shift(positionZ):
        x = choice((-1, 1)) * randrange(2, 10)
        y = choice((-1, 1)) * randrange(2, 10)
        z = randrange(int(positionZ - 90), int(positionZ - 60))
        return x, y, z

    def adjust_vertices(self, point):
        new_vertices = []
        for vertice in self.get_vertices():
            new = []
            new.append(vertice[0] + point[0])
            new.append(vertice[1] + point[1])
            new.append(vertice[2] + point[2])
            new_vertices.append(new)
        return new_vertices


class Cube(Figure3D):

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
