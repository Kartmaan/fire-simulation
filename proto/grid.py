from enum import Enum

import numpy as np
import pygame

# Surface size (preferably a square)
WIN_WIDTH = 1024
WIN_HEIGHT = 800

# Cell size (preferably a square)
CELL_WIDTH = 5
CELL_HEIGHT = 5
 
# Margin between 2 cells (px)
MARGIN = 3

# Number of cells on each row
# Proportional to surface width
cells_in_row = WIN_WIDTH // (CELL_WIDTH + MARGIN)
print("-- Dimensions --")
print("{}x{} px".format(WIN_WIDTH, WIN_HEIGHT))
print("{}x{} ({}) cells\n".format(cells_in_row, cells_in_row, cells_in_row**2))

run = True # Main loop flag
random_anim = False # Cells color randomization flag
fps = 60 # Frame Per Second
anim_speed = 0.01 # Speed animation (second)

# Set colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Material(Enum):
    EMPTY = 0
    WOOD = 0
    FABRIC = 0

class Cell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.temperature = 20.0
        self.oxygen = 21.0
        self.material = Material.EMPTY
        self.in_fire = False
        self.burned = False

    def ignite(self):
        if self.material in [Material.WOOD, Material.FABRIC]:
            self.in_fire = True

    def update(self):
        if self.in_fire:
            self.temperature += 5
            self.oxygen -= 1
            if self.oxygen <= 0 or self.temperature >= 600:
                self.in_fire = False
                self.burned = True

# CREATING A 2 DIMENSIONAL ARRAY
# An cells_in_row X cells_in_row dimension array where each value 
# represents the state of a cell. These values can be 0 for a white
# cell or 1 for a black cell. Initially all values are 
# initialized to zero

# Numpy has a quick and easy method to initialize all 
# values of an array of a desired dimension to zero
grid = np.zeros([cells_in_row, cells_in_row], dtype = int)
grid = [[Cell]]
 
pygame.init()
 
# Set surface dimension
WINDOW_SIZE = [WIN_WIDTH, WIN_HEIGHT]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
pygame.display.set_caption("Space Grid")

clock = pygame.time.Clock()

timers = {}
def timer(timer_name: str, duration: float) -> bool:
    """Checks if a timer has expired.

    Args:
        timer_name (str): Timer name.
        duration (float): Desired duration in seconds.

    Returns:
        bool: True if time is up, False otherwise.
    """
    now = pygame.time.get_ticks() // 1000

    if timer_name not in timers:
        timers[timer_name] = now
        return False

    elapsed_time = now - timers[timer_name]
    if elapsed_time >= duration:
        timers[timer_name] = now
        return True

    return False

# -------- MAIN LOOP -----------
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False # Exit from main loop
            break

        if event.type == pygame.MOUSEBUTTONDOWN: # Mouse click
            if pygame.mouse.get_pressed()[0]: # Left click
                pos = pygame.mouse.get_pos() # Get cursor coordinates

                # Conversion of x,y coordinates to grid coordinates
                column = pos[0] // (CELL_WIDTH + MARGIN) # Column localisation (x axis)
                row = pos[1] // (CELL_HEIGHT + MARGIN) # Row localisation (y axis)
                print("[Column : {} - Row : {}]".format(column, row))
                
                # Cell state change
                # These values will define the color with which 
                # each cell should be drawn
                if grid[row][column] == 0:
                    grid[row][column] = 1 # Black cell
                else:
                    grid[row][column] = 0 # White cell
 
    # Background color (margin color)
    screen.fill((0, 0, 0))
 
    # GRID DRAWING
    for row in range(cells_in_row):
        for column in range(cells_in_row):
            color = WHITE
            if grid[row][column] == 1:
                color = RED
            else :
                color = WHITE
            pygame.draw.rect(screen,
                            color,
                            [(MARGIN + CELL_WIDTH) * column + MARGIN,
                            (MARGIN + CELL_HEIGHT) * row + MARGIN,
                            CELL_WIDTH,
                            CELL_HEIGHT])

    # Set the FPS
    clock.tick(fps)
 
    # Update display
    pygame.display.flip()
 
pygame.quit()