import pygame
from pygame.math import Vector2
import numpy as np

from src.window_option import screen, clock, fps, cells_in_row, cells_in_col, CELL_WIDTH, CELL_HEIGHT, MARGIN
from src.physics import heat_conduction, update_ignition, update_combustion, MAX_TEMP
from src.cell import Cell
from src.colors import Colors

colors = Colors()

SHOW_FLAME_ON_CURSOR = False
MANUAL_IGNITION_DURATION = 15.0 # seconds

# Create a list of Cell objects.
grid: list[list[Cell]] = [[Cell(row, col) for col in range(cells_in_row)] for row in range(cells_in_col)]

# Used to track the expiration time of manual ignitions (caused by left mouse clicks) on each cell.
manual_ignition_expiration_grid = np.zeros_like(grid, dtype=np.int64)

# -------- MAIN LOOP -----------
run = True
while run:
    for event in pygame.event.get():  # All user events
        if event.type == pygame.QUIT:  # Closing window
            run = False  # Exit from main loop
            break

        # ===========================================================================================================
        #                                             MOUSE EVENTS
        # ===========================================================================================================
        # LEFT CLICK : MANUAL IGNITION ON CELL
        # RIGHT CLICK : PRINT CELL INFO

        mouse_buttons = pygame.mouse.get_pressed()

        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos() # Cursor coordinates.

            # The cursor's pixel coordinates are converted to grid coordinates.
            column = pos[0] // (CELL_WIDTH + MARGIN)
            row = pos[1] // (CELL_HEIGHT + MARGIN)

            clicked_cell: Cell = grid[row][column] # Recover clicked Cell object.

            # LEFT CLICK - MANUAL IGNITION
            # When left-clicked, the temperature of the clicked cell rises to the maximum temperature value allowed by
            # the simulation (MAX_TEMP). This temperature is applied for several seconds to hasten heat propagation to
            # neighboring cells and thus combustion. When clicked, the timestamp of the ignition duration expiration is
            # written to the element of the 'manual_ignition_expiration_grid' matrix corresponding to the clicked cell.
            # Checking the continuity of this duration, applying the temperature and resetting expired timers are
            # carried out later in the main loop.
            if mouse_buttons[0]:
                manual_ignition_expiration_grid[row, column] = pygame.time.get_ticks() + MANUAL_IGNITION_DURATION * 1000

            # RIGHT CLICK - CELL'S INFO
            if mouse_buttons[2]:
                print(f"({clicked_cell.row}x{clicked_cell.col}) Temperature ({clicked_cell.material.name}) : "
                      f"{clicked_cell.temperature} Oxygen : {clicked_cell.oxygen_rate} "
                      f"Fuel : {clicked_cell.fuel_level}")

    # ===========================================================================================================
    #                                          DELTA TIME SETTING
    # ===========================================================================================================
    # 'delta_time' serves as a step for simulation, synchronizing physical calculations with real time.

    # 1- 'delta_time' represents the time elapsed since the last frame, in seconds. It's calculated using
    # clock.tick(fps), which returns the time in milliseconds since the last call, and is divided by 1000 to convert
    # it to seconds.
    # 2- We cap 'delta_time' at 0.02 seconds (50 FPS) to prevent excessively large time steps, which could lead to
    # unstable or unrealistic simulation behavior.
    delta_time = clock.tick(fps) / 1000 # 1
    delta_time = min(delta_time, 0.02) # 2

    # ===========================================================================================================
    #                                    UPDATING PHYSICAL PROPERTY MATRICES
    # ===========================================================================================================
    # All the physical properties of the cells and the materials they contain (temperature, conductivity, etc.) are
    # extracted and aligned in NumPy matrices of the same dimensions as the grid.
    #
    # These matrices enable us to manipulate all the cells in a single operation, thus reducing the need for lists and
    # loops. This not only facilitates combined calculations thanks to NumPy methods, but also brings a significant
    # performance gain thanks to the library's strong C optimization. This is highly desirable when several thousand
    # cells need to be calculated 30x per second.

    # Matrices of cell physical properties
    temp_grid = np.array([[cell.temperature for cell in row] for row in grid])
    fuel_grid = np.array([[cell.fuel_level for cell in row] for row in grid])
    oxygen_grid = np.array([[cell.oxygen_rate for cell in row] for row in grid])
    burned_grid = np.array([[cell.burned for cell in row] for row in grid])

    # Matrices of materials physical properties
    conductivity_grid = np.array([[cell.material.value.thermal_conductivity for cell in row] for row in grid])
    capacity_grid = np.array([[cell.material.value.thermal_capacity for cell in row] for row in grid])
    humidity_grid = np.array([[cell.material.value.humidity for cell in row] for row in grid])
    ignition_temp_grid = np.array([[cell.material.value.ignition_temp for cell in row] for row in grid])
    burn_rate_grid = np.array([[cell.material.value.burn_rate for cell in row] for row in grid])
    combustion_heat_grid = np.array([[cell.material.value.combustion_heat for cell in row] for row in grid])
    density_grid = np.array([[cell.material.value.density for cell in row] for row in grid])

    # ===========================================================================================================
    #                                       MANUAL IGNITION CONTINUITY
    # ===========================================================================================================
    # Check the continuity of the heat exerted on a cell following manual ignition (left click).

    # 1- The current time is retrieved using the 'get_ticks' method, which returns the number of milliseconds that have
    # elapsed since Pygame was initialized.
    # 2- A Boolean mask is created which sets to True all elements of the 'manual_ignition_expiration_grid' matrix whose
    # timestamp value is greater than 'now', i.e. timestamps in the future.
    # 3- This mask is applied to the 'temp_grid' matrix, whose True elements will have a temperature value equal to
    # 'MAX_TEMP'.
    now = pygame.time.get_ticks() # 1
    mask = manual_ignition_expiration_grid > now # 2
    temp_grid[mask] = MAX_TEMP # 3

    # ===========================================================================================================
    #                                  MATRIX UPDATE AFTER THERMAL REACTIONS
    # ===========================================================================================================
    # Applying physical operations to the concerned matrices.

    # HEAT CONDUCTION
    temp_grid = heat_conduction(temp_grid, conductivity_grid, capacity_grid, delta_time)

    # IGNITION
    is_burning_grid = update_ignition(temp_grid, ignition_temp_grid, humidity_grid, burned_grid)

    # COMBUSTION
    temp_grid, fuel_grid, oxygen_grid, is_burning_grid, burned_grid = update_combustion(temp_grid, fuel_grid,
                                                                                         oxygen_grid, is_burning_grid,
                                                                                         burn_rate_grid,
                                                                                         combustion_heat_grid,
                                                                                         density_grid, capacity_grid,
                                                                                         delta_time)

    # ===========================================================================================================
    #                                         MANUAL IGNITION RESET
    # ===========================================================================================================
    # All elements in the matrix with a timestamp that is out of date (past) no longer match the mask criteria, so the
    # timestamps of these elements are reset to zero.
    manual_ignition_expiration_grid[~mask] = 0

    # ===========================================================================================================
    #                                   APPLYING PHYSICAL PROPERTIES TO CELLS
    # ===========================================================================================================
    # Once the physical operations (conduction, combustion, etc.) have been applied to all the matrices concerned, they
    # are reinjected into the `Cell` objects.

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            cell.temperature = temp_grid[i, j]
            cell.fuel_level = fuel_grid[i, j]
            cell.oxygen_rate = oxygen_grid[i, j]
            cell.is_burning = is_burning_grid[i, j]
            cell.burned = burned_grid[i, j]

    # ===========================================================================================================
    #                                               DRAWING
    # ===========================================================================================================

    # Background color
    screen.fill(colors.background)

    # Grid drawing
    for row in range(cells_in_col):  # Row iteration (y-axis, cells_in_col)
        for column in range(cells_in_row):  # Column iteration (x-axis, cells_in_row)
            cell = grid[row][column]  # Retrieve the Cell object for each position.
            cell.draw()

    # Flame display near cursor.
    if SHOW_FLAME_ON_CURSOR:
        flame_radius = 5
        cursor_pos = Vector2(pygame.mouse.get_pos())
        flame_pos = Vector2(cursor_pos.x + 12, cursor_pos.y - 2)
        pygame.draw.circle(screen, colors.black, flame_pos, flame_radius + 2) # Outline
        pygame.draw.circle(screen, colors.red, flame_pos, flame_radius)

    # Stats on window title
    mean_temp = round(temp_grid.mean(), 2)
    max_temp = round(temp_grid.max(), 2)
    mean_oxygen = round(oxygen_grid.mean(), 2)
    burning = np.count_nonzero(is_burning_grid)
    burned = np.count_nonzero(burned_grid)
    pygame.display.set_caption(f"Fire propagation | Mean temp : {mean_temp}°C | Max temp : {max_temp}°C | "
                               f"Mean oxygen : {mean_oxygen}% | Burning cells : {burning} | Burned cells : {burned}")

    # Set the FPS
    clock.tick(fps)

    # Update display
    pygame.display.flip()

pygame.quit()