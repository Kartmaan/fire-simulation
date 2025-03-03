import pygame

pygame.init()

clock = pygame.time.Clock()
fps = 30

# Favicon
favicon = pygame.image.load("assets/favicon.png")
pygame.display.set_icon(favicon)

# The size of the window is a fraction of the size of the user's screen. It's on the basis of this window's dimensions
# that cell size (if required) and the number of cells per row and column are adjusted.

# Recovering screen dimensions.
user_screen_info = pygame.display.Info()
USER_SCREEN_WIDTH = user_screen_info.current_w
USER_SCREEN_HEIGHT = user_screen_info.current_h
scale = 0.66

# Sizing the window to the desired scale
WIN_WIDTH = int(USER_SCREEN_WIDTH * scale)
WIN_HEIGHT = int(USER_SCREEN_HEIGHT * scale)

# Initial cell size
# These sizes will be adjusted, if necessary, so that a whole number of cells can be contained within surface
# dimensions.
CELL_WIDTH_INIT = 10
CELL_HEIGHT_INIT = 10

# Margin between two cells (px).
MARGIN = 2

# Calculation of the integer number of cells that can be contained in the surface according to the initial parameters.
cells_in_row_init = int(WIN_WIDTH // (CELL_WIDTH_INIT + MARGIN))
cells_in_col_init = int(WIN_HEIGHT // (CELL_HEIGHT_INIT + MARGIN))

# Calculation of total grid size based on initial parameters.
grid_width_init = (cells_in_row_init * (CELL_WIDTH_INIT + MARGIN)) + MARGIN
grid_height_init = (cells_in_col_init * (CELL_HEIGHT_INIT + MARGIN)) + MARGIN

CELL_WIDTH = CELL_WIDTH_INIT
CELL_HEIGHT = CELL_HEIGHT_INIT

# Checks that the grid size doesn't exceed that of the desired window size.
if grid_width_init > WIN_WIDTH or grid_height_init > WIN_HEIGHT:
    width_ratio = WIN_WIDTH / grid_width_init if grid_width_init > WIN_WIDTH else 1.0
    height_ratio = WIN_HEIGHT / grid_height_init if grid_height_init > WIN_HEIGHT else 1.0
    scale_ratio = min(width_ratio, height_ratio)

    CELL_WIDTH = int(CELL_WIDTH_INIT * scale_ratio)
    CELL_HEIGHT = int(CELL_HEIGHT_INIT * scale_ratio)

    if CELL_WIDTH < 1:  # Ensure cell width is at least 1px
        CELL_WIDTH = 1

    if CELL_HEIGHT < 1:  # Ensure cell height is at least 1px
        CELL_HEIGHT = 1

    print(f"Cell size adjusted from {CELL_WIDTH_INIT}x{CELL_HEIGHT_INIT} to {CELL_WIDTH}x{CELL_HEIGHT}")

# Adjusting the number of cells per row/column
cells_in_row = int(WIN_WIDTH // (CELL_WIDTH + MARGIN))
cells_in_col = int(WIN_HEIGHT // (CELL_HEIGHT + MARGIN))
print(f"Cells : {cells_in_row}x{cells_in_col} = {cells_in_row*cells_in_col}")

# Applying window dimensions
WINDOW_SIZE = [WIN_WIDTH, WIN_HEIGHT]

screen = pygame.display.set_mode(WINDOW_SIZE)