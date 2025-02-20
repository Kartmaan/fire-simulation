import pygame
from pygame.math import Vector2

from src.scaling_option import screen, clock, fps, cells_in_row, cells_in_col, CELL_WIDTH, CELL_HEIGHT, MARGIN
from src.cell import Cell
from src.colors import Colors

colors = Colors()

# Création d'une liste de Cell objects.
grid: list[list[Cell]] = [[Cell(row, col) for col in range(cells_in_row)] for row in range(cells_in_col)]

# -------- MAIN LOOP -----------
run = True
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False  # Exit from main loop
            break

        # Clic souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos() # Coordonnées du curseur.

            # Les coordonnées pixel du curseur sont converties en coordonnées de grille.
            column = pos[0] // (CELL_WIDTH + MARGIN)
            row = pos[1] // (CELL_HEIGHT + MARGIN)

            clicked_cell: Cell = grid[row][column] # Récupération de l'objet Cell cliqué.

            # Clic gauche
            # Monte la température de la cellule au-delà du point d'ignition du matériau qu'il contient.
            if pygame.mouse.get_pressed()[0]:
                if clicked_cell.temperature < clicked_cell.material.value.ignition_temp:
                    excess_temp = 500
                    clicked_cell.temperature = clicked_cell.material.value.ignition_temp + excess_temp

                    #clicked_cell.heat_conduction(grid, delta_time=0.1)

                    print(f"({clicked_cell.row}x{clicked_cell.col}) Ignition temperature exceeded "
                          f"({clicked_cell.material.name}) : {clicked_cell.temperature}/"
                          f"{clicked_cell.material.value.ignition_temp}")

            # Clic droit
            # Affiche la température de la cellule
            if pygame.mouse.get_pressed()[2]:
                print(f"({clicked_cell.row}x{clicked_cell.col}) Temperature ({clicked_cell.material.name}) : "
                      f"{clicked_cell.temperature}")

    delta_time = 0.08
    for row in range(cells_in_col):
        for column in range(cells_in_row):
            cell = grid[row][column]
            if cell.timer("delta_time", delta_time):
                cell.heat_conduction(grid, delta_time)

    # Arrière-plan
    screen.fill((50, 50, 50))

    # Dessin de la grille
    for row in range(cells_in_col):  # Itération sur ligne (y-axis, cells_in_col)
        for column in range(cells_in_row):  # Itération sur colonne (x-axis, cells_in_row)
            cell = grid[row][column]  # Récupération de l'objet Cell pour chaque position.
            cell.draw()

    # Affichage de la flamme à proximité du curseur.
    flame_radius = 5
    cursor_pos = Vector2(pygame.mouse.get_pos())
    flame_pos = Vector2(cursor_pos.x + 12, cursor_pos.y - 2)
    pygame.draw.circle(screen, colors.black, flame_pos, flame_radius + 2) # Contour
    pygame.draw.circle(screen, colors.red, flame_pos, flame_radius)

    # Set the FPS
    clock.tick(fps)

    # Update display
    pygame.display.flip()

pygame.quit()