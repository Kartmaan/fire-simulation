import pygame

pygame.init()

# Récupération des dimensions de l'écran
user_screen_info = pygame.display.Info()
USER_SCREEN_WIDTH = user_screen_info.current_w
USER_SCREEN_HEIGHT = user_screen_info.current_h
scale = 1.5

# Dimensionnement de la fenêtre
WIN_WIDTH = USER_SCREEN_WIDTH // scale  # 1280
WIN_HEIGHT = USER_SCREEN_HEIGHT // scale  # 720

# Taille initiale des cellules
# Ces tailles seront, au besoin, ajustées de manière à ce qu'un nombre entier de cellules puisse être contenu dans
# les dimensions de la surface
CELL_WIDTH_INIT = 10
CELL_HEIGHT_INIT = 10

# Marge entre deux cellules (px)
MARGIN = 2

# Calcul du nombre entier de cellules pouvant être contenu dans la surface selon les paramètres initiaux
cells_in_row_init = int(WIN_WIDTH // (CELL_WIDTH_INIT + MARGIN))
cells_in_col_init = int(WIN_HEIGHT // (CELL_HEIGHT_INIT + MARGIN))

# Calcul de la taille totale de la grille selon les paramètres initiaux
grid_width_init = (cells_in_row_init * (CELL_WIDTH_INIT + MARGIN)) + MARGIN
grid_height_init = (cells_in_col_init * (CELL_HEIGHT_INIT + MARGIN)) + MARGIN

CELL_WIDTH = CELL_WIDTH_INIT
CELL_HEIGHT = CELL_HEIGHT_INIT

# Vérifie si la taille de la grille ne dépasse pas celle de la surface souhaitée
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

# Ajustement du nombre de cellules par ligne/colonne
cells_in_row = int(WIN_WIDTH // (CELL_WIDTH + MARGIN))
cells_in_col = int(WIN_HEIGHT // (CELL_HEIGHT + MARGIN))
print(f"Cells : {cells_in_row}x{cells_in_col} = {cells_in_row*cells_in_col}")

# Application des dimensions de la fenêtre
WINDOW_SIZE = [WIN_WIDTH, WIN_HEIGHT]

screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
fps = 30

pygame.display.set_caption("Fire propagation")