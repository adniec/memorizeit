from collections import namedtuple
import pygame
import sys
import colors
from config import *
from game import *


class Gui:

    def __init__(self):
        self.display = (800, 600)
        self.screen = pygame.display.set_mode(self.display)
        self.colors = colors.get_menu_colors()
        self.Dimensions = namedtuple('Dimensions', ('x_from', 'x_to', 'y_from', 'y_to'))
        self.text_size = 25
        self.blit_background()

    def blit_background(self):
        self.screen.fill(colors.get_background_color())
        size = self.text_size * 5
        size = size if self.display[0] >= 800 else int(size * self.display[0] / 1000)
        self.create_label('MemorizeIT', (self.display[0] // 2, size), colors.get_logo_color(), size)
        try:
            image = self.adjust_image()
            size = image.get_size()
            self.screen.blit(image, (0, self.display[1] - size[1]))
        except pygame.error:
            pass

    def adjust_image(self):
        image = pygame.image.load('images/brain.png')
        size = image.get_size()[0]
        display = min(self.display)
        if display - size - 180 < 0:
            size = [int(display * 0.7)] * 2
            image = pygame.transform.scale(image, size)
        return image

    def animate_element(self, point, dimensions, function, arguments=None, button=False, message=''):
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
        mouse = pygame.mouse.get_pos()
        if dimensions.x_from < mouse[0] < dimensions.x_to and dimensions.y_from < mouse[1] < dimensions.y_to:
            return True
        return False

    @staticmethod
    def use_on_click(function, arguments):
        if pygame.mouse.get_pressed()[0]:
            function(*arguments) if arguments else function()
            pygame.time.delay(100)

    def create_arrows(self, point, position, gap, value, left_condition, right_condition, function):
        new_point = [point[0] - gap // 2, point[1]]
        left = self.draw_triangle(self.colors[0], new_point)
        if value > left_condition:
            self.animate_element(new_point, left, function, [position, False], 'left')

        new_point[0] += gap
        right = self.draw_triangle(self.colors[0], new_point, False)
        if value < right_condition:
            self.animate_element(new_point, right, function, [position], 'right')

    def draw_triangle(self, color, point, left=True):
        dimensions = self.Dimensions(point[0] - 10, point[0], point[1] - 10, point[1] + 10)
        coordinates = [(dimensions.x_to, point[1])]
        x = 'x_from'
        if left:
            dimensions = self.Dimensions(point[0], point[0] + 10, point[1] - 10, point[1] + 10)
            x = 'x_to'
        coordinates.extend([(eval('dimensions.' + x), dimensions.y_from), (eval('dimensions.' + x), dimensions.y_to)])
        pygame.draw.polygon(self.screen, color, coordinates)
        return dimensions

    def create_button(self, message, point, function, arguments=None, border=False):
        if border:
            button = self.draw_button(message, self.colors[0], point)
        else:
            button = self.create_label(message, point)
        self.animate_element(point, button, function, arguments, border, message)

    def draw_button(self, message, color, point):
        border = self.draw_border(color, point)
        mid_point = ((border.x_from + border.x_to) // 2, (border.y_from + border.y_to) // 2)
        self.create_label(message, mid_point, color, int(self.text_size * 1.5))
        return border

    def create_label(self, message, mid_point, color=None, size=None):
        if color is None: color = self.colors[0]
        if size is None: size = self.text_size
        text = pygame.font.SysFont('carlito', size, True).render(message, True, color)
        x_shift = text.get_width() // 2
        y_shift = text.get_height() // 2
        self.screen.blit(text, (mid_point[0] - x_shift, mid_point[1] - y_shift))
        return self.Dimensions(mid_point[0] - x_shift, mid_point[0] + x_shift, mid_point[1] - y_shift,
                               mid_point[1] + y_shift)

    def draw_border(self, color, point):
        width = self.text_size * 10
        height = self.text_size * 2
        border = pygame.Rect(point[0], point[1], width, height)
        pygame.draw.rect(self.screen, color, border, self.text_size // 10)
        return self.Dimensions(point[0], point[0] + width, point[1], point[1] + height)


class Menu(Gui):

    def __init__(self):
        self.resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.positions = {'New game': Dynamic, 'Static game': Static, 'Settings': Settings, 'Exit': self.close}
        super().__init__()
        Handler(self)()

    def __call__(self):
        self.blit_background()
        point = tuple(x - 325 for x in self.display)

        for gap, position in enumerate(self.positions):
            gap *= 70
            new_point = (point[0], point[1] + gap)
            arguments = [self.resolution] if 'game' in position else []
            self.create_button(position, new_point, self.positions[position], arguments, True)

    def close(self):
        pygame.quit()
        sys.exit()


class Settings(Gui):

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.settings = self.config.get_settings()
        self.range = self.config.get_values()
        self.run = Handler(self)
        self.run()

    def __call__(self):
        self.blit_background()
        point = (self.display[0] - 150, self.display[1] - 375)
        for position in self.settings:
            point = (point[0], point[1] + 50)
            self.create_label(position.capitalize() + ':', (point[0] - 150, point[1]))
            text = str(self.settings[position])
            self.create_label(text, point)
            index = self.range[position].index(self.settings[position])
            self.create_arrows(point, position, 150, index, 0, len(self.range[position]) - 1, self.change_setting)

        point = (self.display[0] - 75, self.display[1] - 50)
        self.create_button('Back', point, lambda: self.run.stop(), self.config.save(self.settings))

    def change_setting(self, position, add=True):
        index = self.range[position].index(self.settings[position])
        index = index + 1 if add else index - 1
        self.settings[position] = self.range[position][index]


class Summary(Gui):

    def __init__(self, result):
        super().__init__()
        self.result = result
        self.counted = {key: 0 for key in result}
        self.submitted = False
        self.run = Handler(self)
        self.run()

    def __call__(self):
        self.screen.fill(colors.get_background_color())
        self.create_label('Check your result:', (self.display[0] // 2, 75), size=50)
        point = (self.display[0] // 2, 100)
        for position in self.counted:
            point = (point[0], point[1] + 50)
            self.create_label(position.capitalize() + 's:', (point[0] - 125, point[1]))
            text = str(self.counted[position])

            if self.submitted:
                color = colors.get_rate_colors()
                if self.result[position] == self.counted[position]:
                    color = color[1]
                else:
                    self.create_label(str(self.result[position]), (point[0] + 175, point[1]), color[1])
                    color = color[0]

                self.create_label(text, (point[0] + 100, point[1]), color)
            else:
                self.create_label(text, (point[0] + 100, point[1]))
                self.create_arrows((point[0] + 100, point[1]), position, 150, self.counted[position], 0, 99,
                                   self.change_counter)

        point = [self.display[0] - 175, self.display[1] - 50]
        if not self.submitted:
            self.create_button('Submit', point, self.submit)
        point[0] += 100
        self.create_button('Back', point, self.run.stop)

    def change_counter(self, position, add=True):
        self.counted[position] += 1 if add else -1

    def submit(self):
        self.submitted = True
