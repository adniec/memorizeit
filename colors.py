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
    if setting == 'Easy':
        colors = sample(COLORS.keys(), amount)
        return [COLORS[x] for x in colors]
    return True if setting == 'Medium' else False


def convert(color):
    return [int(x * 255) for x in color]


def get_menu_colors():
    return (255, 204, 0), (255, 255, 0)


def get_background_color():
    return (50, 50, 50)


def get_logo_color():
    return (255, 128, 0)


def get_rate_colors():
    return (220, 0, 0), (0, 180, 0)


class Random:

    def __init__(self):
        self.active_color = 'Grey'

    def __repr__(self):
        return f'<One color code of {[x for x in COLORS.keys() if not x == self.active_color]} picked randomly>'

    def get_color(self):
        colors = list(filter((lambda x: self.active_color not in x), COLORS))
        self.active_color = choice(colors)
        return COLORS[self.active_color]
