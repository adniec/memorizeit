from json import dumps, loads
import sys
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE


class Config:

    def __init__(self):
        self.config_file = 'settings.txt'
        self.settings = self.check_content(self.get_content())
        self.save(self.settings)

    def __repr__(self):
        return f'<Configuration with values: {self.settings}>'

    def check_content(self, content):
        default = {'figures': 3, 'time': 60, 'speed': 2, 'colors': 'Medium', 'sound': 'Off'}
        values = self.get_values()
        for key in default:
            try:
                if content[key] in values[key]:
                    default[key] = content[key]
            except (KeyError, TypeError):
                pass
        return default

    def get_content(self):
        try:
            with open(self.config_file, 'r') as config:
                return loads(config.read())
        except (FileNotFoundError, ValueError):
            return False

    def save(self, settings):
        self.settings = settings
        with open(self.config_file, 'w') as config:
            config.write(dumps(self.settings))

    def get_settings(self):
        return self.settings

    def get_values(self):
        return {
            'figures': (2, 3, 4),
            'time': tuple((x for x in range(5, 61, 5))),
            'speed': (1, 2, 3, 4),
            'colors': ('Easy', 'Medium', 'Hard'),
            'sound': ('Off', 'On')
        }


class Handler:

    def __init__(self, function, condition=lambda: True):
        self.function = function
        self.condition = condition

    def __repr__(self):
        return f'<Pygame event handler with {self.function} in loop.'

    def __call__(self):
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
        self.condition = lambda: False
