import numpy as np
import pygame

pygame.init()

# Récupération des dimensions de l'écran
user_screen_info = pygame.display.Info()
USER_SCREEN_WIDTH = user_screen_info.current_w
USER_SCREEN_HEIGHT = user_screen_info.current_h
scale = 1.5

# Dimensionnement de la fenêtre
WIN_WIDTH = USER_SCREEN_WIDTH // scale # 1280
WIN_HEIGHT = USER_SCREEN_HEIGHT // scale # 720

# Taille initiale des cellules
# Ces tailles seront, au besoin, ajustées de manière à ce qu'un nombre entier de cellules puisse être contenu dans
# les dimensions de la surface
CELL_WIDTH_INIT = 8
CELL_HEIGHT_INIT = 8

# Marge entre deux cellules (px)
MARGIN = 2

run = True
fps = 60

# Couleurs (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)

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

    if CELL_WIDTH < 1: # Ensure cell width is at least 1px
        CELL_WIDTH = 1

    if CELL_HEIGHT < 1: # Ensure cell height is at least 1px
        CELL_HEIGHT = 1

    print(f"Cell size adjusted from {CELL_WIDTH_INIT}x{CELL_HEIGHT_INIT} to {CELL_WIDTH}x{CELL_HEIGHT}")

# Ajustement du nombre de cellules par ligne/colonne
cells_in_row = int(WIN_WIDTH // (CELL_WIDTH + MARGIN))
cells_in_col = int(WIN_HEIGHT // (CELL_HEIGHT + MARGIN))

# Création d'un array Numpy aux dimensions désirées avec toutes les valeurs à 0.
# Numpy utilise la convention [rows, columns], nous mettons donc la valeur du nombre de cellules par colonne dans la
# partie 'rows' et celle du nombre de cellules dans une ligne dans la partie 'columns'.
grid = np.zeros([cells_in_col, cells_in_row], dtype = int)

# Application des dimensions de la fenêtre
WINDOW_SIZE = [WIN_WIDTH, WIN_HEIGHT]
screen = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.set_caption("Space Grid")

clock = pygame.time.Clock()

# Rayon de propagation autour de la cellule cliquée.
NEIGHBORHOOD_RADIUS = 8

# -------- MAIN LOOP -----------
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False # Exit from main loop
            break

        if event.type == pygame.MOUSEBUTTONDOWN: # Mouse click
            if pygame.mouse.get_pressed()[0]: # Left click
                pos = pygame.mouse.get_pos() # Get cursor coordinates

                # Les coordonnées du curseur sont converties en coordonnées de grille.
                # Nous sommes dans l'indentation de la condition 'mouse.get_pressed' donc les valeurs de 'column'
                # et 'row' changent à chaque clic.
                column = pos[0] // (CELL_WIDTH + MARGIN) # Localisation sur la colonne (x axis)
                row = pos[1] // (CELL_HEIGHT + MARGIN) # Localisation sur la ligne (y axis)
                print("[Column : {} - Row : {}]".format(column, row))

                # Parcours de la grille pour réinitialiser les états.
                # À chaque nouveau clic, toutes les cellules colorées redeviennent blanches.
                for r in range(cells_in_col):
                    for c in range(cells_in_row):
                        if grid[r][c] == 1 or grid[r][c] == 2:
                            grid[r][c] = 0

                # Changement de couleur de la cellule cliquée.
                if grid[row][column] == 0:
                    grid[row][column] = 1 # Red cell (clicked)
                else:
                    grid[row][column] = 0 # White cell

                # Récupération du voisinage autour de la cellule cliquée.
                for offset_row in range(-NEIGHBORHOOD_RADIUS, NEIGHBORHOOD_RADIUS + 1):
                    for offset_col in range(-NEIGHBORHOOD_RADIUS, NEIGHBORHOOD_RADIUS + 1):
                        if offset_row == 0 and offset_col == 0: # Ne pas prendre en compte la cellule cliquée.
                            continue

                        neighbor_row = row + offset_row
                        neighbor_col = column + offset_col

                        # Check boundaries - use cells_in_col and cells_in_row
                        if 0 <= neighbor_row < cells_in_col and 0 <= neighbor_col < cells_in_row:
                            grid[neighbor_row][neighbor_col] = 2 # Orange cell (neighbor)

    # Arrière-plan
    screen.fill((50, 50, 50))

    # Dessin de la grille
    for row in range(cells_in_col): # Itération sur ligne (y-axis, cells_in_col)
        for column in range(cells_in_row): # Itération sur colonne (x-axis, cells_in_row)
            color = WHITE
            if grid[row][column] == 1:
                color = RED
            elif grid[row][column] == 2:
                color = ORANGE
            else :
                color = WHITE
            pygame.draw.rect(screen,
                            color,
                            [(MARGIN + CELL_WIDTH) * column + MARGIN, # x position based on column
                            (MARGIN + CELL_HEIGHT) * row + MARGIN, # y position based on row
                            CELL_WIDTH,
                            CELL_HEIGHT])

    # Set the FPS
    clock.tick(fps)

    # Update display
    pygame.display.flip()

pygame.quit()