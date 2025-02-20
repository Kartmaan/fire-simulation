from dataclasses import dataclass

@dataclass
class Colors:
    black: tuple = (0, 0, 0)
    white: tuple = (255, 255, 255)
    red: tuple = (255, 0, 0)
    green: tuple = (0, 255, 0)
    blue: tuple = (0, 0, 255)
    orange: tuple = (255, 165, 0)

    grass: tuple = (0, 180, 0)
    wood: tuple = (153, 76, 0)
    fuel: tuple = (210, 0, 210)