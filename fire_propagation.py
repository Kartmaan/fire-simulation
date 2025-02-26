import pygame
from pygame.math import Vector2
import numpy as np

from src.window_option import screen, clock, fps, cells_in_row, cells_in_col, CELL_WIDTH, CELL_HEIGHT, MARGIN
from src.physics import heat_conduction, update_ignition, update_combustion
from src.cell import Cell
from src.colors import Colors

colors = Colors()

SHOW_FLAME_ON_CURSOR = False

# Create a list of Cell objects.
grid: list[list[Cell]] = [[Cell(row, col) for col in range(cells_in_row)] for row in range(cells_in_col)]

# -------- MAIN LOOP -----------
run = True
left_click_pressed = False
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False  # Exit from main loop
            break

        mouse_buttons = pygame.mouse.get_pressed()

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
        #if mouse_buttons[0]:
            pos = pygame.mouse.get_pos() # Cursor coordinates.

            # The cursor's pixel coordinates are converted to grid coordinates.
            column = pos[0] // (CELL_WIDTH + MARGIN)
            row = pos[1] // (CELL_HEIGHT + MARGIN)

            clicked_cell: Cell = grid[row][column] # Recover clicked Cell object.

            # Left click
            # Raises the cell temperature above the ignition point of the material it contains.
            #if pygame.mouse.get_pressed()[0]:
            if mouse_buttons[0]:
                excess_temp = 500

                clicked_cell.temperature += excess_temp

                print(f"({clicked_cell.row}x{clicked_cell.col}) Ignition temperature exceeded "
                          f"({clicked_cell.material.name}) : {clicked_cell.temperature}/"
                          f"{clicked_cell.material.value.ignition_temp}")

            # Right click
            # Displays cell's temperature
            #if pygame.mouse.get_pressed()[2]:
            if mouse_buttons[2]:
                print(f"({clicked_cell.row}x{clicked_cell.col}) Temperature ({clicked_cell.material.name}) : "
                      f"{clicked_cell.temperature} Oxygen : {clicked_cell.oxygen_rate} "
                      f"Fuel : {clicked_cell.fuel_level}")

    delta_time = clock.tick(fps) / 1000
    delta_time = min(delta_time, 0.02)
    
    # Matrices des propriétés physiques des cellules
    temp_grid = np.array([[cell.temperature for cell in row] for row in grid])
    fuel_grid = np.array([[cell.fuel_level for cell in row] for row in grid])
    oxygen_grid = np.array([[cell.oxygen_rate for cell in row] for row in grid])
    burned_grid = np.array([[cell.burned for cell in row] for row in grid])
    cell_humidity_grid = np.array([[cell.humidity_rate for cell in row] for row in grid])

    # Matrices des propriétés physiques des matériaux
    conductivity_grid = np.array([[cell.material.value.thermal_conductivity for cell in row] for row in grid])
    capacity_grid = np.array([[cell.material.value.thermal_capacity for cell in row] for row in grid])
    humidity_grid = np.array([[cell.material.value.humidity for cell in row] for row in grid])
    ignition_temp_grid = np.array([[cell.material.value.ignition_temp for cell in row] for row in grid])
    burn_rate_grid = np.array([[cell.material.value.burn_rate for cell in row] for row in grid])
    combustion_heat_grid = np.array([[cell.material.value.combustion_heat for cell in row] for row in grid])
    density_grid = np.array([[cell.material.value.density for cell in row] for row in grid])

    # Conduction de la chaleur
    temp_grid = heat_conduction(temp_grid, conductivity_grid, capacity_grid, delta_time)

    # Propagation du feu
    is_burning_grid = update_ignition(temp_grid, ignition_temp_grid, humidity_grid, burned_grid)
    temp_grid, fuel_grid, oxygen_grid, is_burning_grid, burned_grid = update_combustion(temp_grid, fuel_grid,
                                                                                         oxygen_grid, is_burning_grid,
                                                                                         burn_rate_grid,
                                                                                         combustion_heat_grid,
                                                                                         density_grid, capacity_grid,
                                                                                         delta_time)

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            cell.temperature = temp_grid[i, j]
            cell.fuel_level = fuel_grid[i, j]
            cell.oxygen_rate = oxygen_grid[i, j]
            cell.is_burning = is_burning_grid[i, j]
            cell.burned = burned_grid[i, j]

    # Background color
    screen.fill(colors.background)

    # Grid drawing
    for row in range(cells_in_col):  # Row iteration (y-axis, cells_in_col)
        for column in range(cells_in_row):  # Column iteration (x-axis, cells_in_row)
            cell = grid[row][column]  # Retrieve the Cell object for each position.
            cell.draw()

    if SHOW_FLAME_ON_CURSOR:
        # Flame display near cursor.
        flame_radius = 5
        cursor_pos = Vector2(pygame.mouse.get_pos())
        flame_pos = Vector2(cursor_pos.x + 12, cursor_pos.y - 2)
        pygame.draw.circle(screen, colors.black, flame_pos, flame_radius + 2) # Outline
        pygame.draw.circle(screen, colors.red, flame_pos, flame_radius)

    # Set the FPS
    clock.tick(fps)

    # Update display
    pygame.display.flip()

pygame.quit()