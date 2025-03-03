from dataclasses import dataclass

@dataclass
class Colors:
    """
    A collection of commonly used RGB color tuples.

    This class provides a convenient way to access predefined colors through named attributes.
    """
    black: tuple = (0, 0, 0)
    white: tuple = (255, 255, 255)
    red: tuple = (255, 0, 0)
    green: tuple = (0, 255, 0)
    blue: tuple = (0, 0, 255)
    yellow: tuple = (255, 255, 0)
    orange: tuple = (255, 165, 0)

    background: tuple = (112, 128, 144)
    grass: tuple = (34, 139, 34)
    wood: tuple = (164, 114, 11)
    water: tuple = (0, 170, 170) # (0, 170, 255)
    fuel: tuple = (210, 0, 210)