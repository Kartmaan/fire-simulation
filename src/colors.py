from dataclasses import dataclass

@dataclass
class Colors:
    black: tuple = (0, 0, 0)
    white: tuple = (255, 255, 255)
    red: tuple = (255, 0, 0)
    green: tuple = (0, 255, 0)
    blue: tuple = (0, 0, 255)
    yellow: tuple = (255, 255, 0)
    orange: tuple = (255, 165, 0)

    background: tuple = (100, 100, 100)
    grass: tuple = (0, 180, 0)
    wood: tuple = (190, 102, 0)
    water: tuple = (102, 178, 255)
    fuel: tuple = (210, 0, 210)