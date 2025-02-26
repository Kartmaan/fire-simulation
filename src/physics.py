import numpy as np

from src.window_option import CELL_WIDTH, CELL_HEIGHT

MAX_TEMP = 2138
MIN_TEMP = 20

def heat_conduction(temp_grid: np.ndarray, conductivity_grid: np.ndarray, capacity_grid: np.ndarray, delta_time: float):
    """
    Calculates and applies heat conduction between neighboring cells in a grid.

    This function simulates heat transfer between cells based on their temperature differences,
    thermal conductivities, and thermal capacities. It uses a vectorized approach with NumPy
    to efficiently compute heat transfer across the entire grid.

    The function assumes heat transfer occurs between each cell and its direct horizontal and
    vertical neighbors. It calculates the heat transfer based on a simplified form of Fourier's
    law of heat conduction.

    Args:
        temp_grid (np.ndarray): A 2D NumPy array representing the temperature of each cell in the grid.
        conductivity_grid (np.ndarray): A 2D NumPy array representing the thermal conductivity of each cell's material.
        capacity_grid (np.ndarray): A 2D NumPy array representing the thermal capacity of each cell's material.
        delta_time (float): The time step for the simulation, used to scale the amount of heat transferred.

    Returns:
        np.ndarray: A 2D NumPy array representing the updated temperature of each cell after heat conduction.

    Process:
        1. Calculate Temperature Differences:
           - Computes the temperature difference between each cell and its right neighbor (`delta_temp_right`).
           - Computes the temperature difference between each cell and its bottom neighbor (`delta_temp_down`).

        2. Calculate Average Conductivity:
           - Determines the average thermal conductivity at the interface between neighboring cells
             for both horizontal (`k_right`) and vertical (`k_down`) neighbors.

        3. Calculate Heat Transfer:
           - Computes the amount of heat transferred between neighbors based on the temperature
             difference, average conductivity, contact area, distance between cell centers, and
             the simulation time step. The formula used is a simplified form of Fourier's Law.
            - `contact_area`: is the contact surface between two cells.
            - `distance`: The distance between the centers of two neighboring cells.
           - `heat_transfer_right`: Heat transferred from a cell to it's right neighbor.
           - `heat_transfer_down`: Heat transferred from a cell to it's neighbor below.

        4. Update Temperatures:
           - Updates the temperature of each cell by decreasing the temperature of the heat-donating
             cell and increasing the temperature of the heat-receiving cell.
           - The temperature change is scaled by the inverse of the cell's thermal capacity.
           - Cells are indexed in such a way that the energy is correctly transferred from one to the other.

        5. Temperature Clamping:
           - Ensures that no cell's temperature drops below 20.0 (ambient temperature) by applying a minimum value.

    Assumptions:
        - Heat transfer only occurs between direct horizontal and vertical neighbors.
        - The contact area between cells is considered constant.
        - The distance between cell centers is constant and calculated based on `CELL_WIDTH` and `CELL_HEIGHT`.
        - The mass of the cell is included in the thermal capacity.
        - Heat diffusion is considered isotropic.
        - The simulation grid has constant `CELL_WIDTH` and `CELL_HEIGHT`.
    """
    # --- 1. Calculate Temperature Differences ---
    # Calculate the temperature difference between each cell and its right neighbor.
    # We create an array of the same size and type as 'temp_grid', initialized with zeros.
    # Then, we calculate the temperature differences between each cell and its right neighbor,
    # excluding the last column because cells in the last column have no right neighbor.
    # The temperature difference is calculated as (temperature of the cell) - (temperature of the right neighbor).
    delta_temp_right = np.zeros_like(temp_grid)
    delta_temp_right[:, :-1] = temp_grid[:, :-1] - temp_grid[:, 1:]

    # Calculate the temperature difference between each cell and its bottom neighbor.
    # This is done similarly to the horizontal difference, but this time we exclude the last row,
    # because cells in the last row have no bottom neighbor.
    # The temperature difference is calculated as (temperature of the cell) - (temperature of the bottom neighbor).
    delta_temp_down = np.zeros_like(temp_grid)
    delta_temp_down[:-1, :] = temp_grid[:-1, :] - temp_grid[1:, :]

    # --- 2. Calculate Average Conductivity ---
    # Calculate the average thermal conductivity between each cell and its right neighbor.
    # We initialize an array of zeros and calculate the average by summing the conductivity of each cell
    # with the conductivity of its right neighbor and dividing by 2.
    # We exclude the last column, similar to the temperature difference calculation.
    k_right = np.zeros_like(temp_grid)
    k_right[:, :-1] = (conductivity_grid[:, :-1] + conductivity_grid[:, 1:]) / 2

    # Calculate the average thermal conductivity between each cell and its bottom neighbor.
    # This is done similarly to the horizontal average conductivity, but we exclude the last row.
    k_down = np.zeros_like(temp_grid)
    k_down[:-1, :] = (conductivity_grid[:-1, :] + conductivity_grid[1:, :]) / 2

    # --- 3. Calculate Heat Transfer ---
    # Define the contact area between two cells, assuming a uniform square grid.
    contact_area = CELL_WIDTH * CELL_HEIGHT
    # Calculate the distance between the centers of two adjacent cells, assuming they are touching edge to edge.
    # Because they are squares the distance between their center will correspond to the hypothenus of a triangle
    # where the sides are equal to the width and height of the cell.
    distance = np.sqrt(CELL_WIDTH ** 2 + CELL_HEIGHT ** 2)

    # Calculate the heat transfer between each cell and its right neighbor based on a simplified Fourier's Law.
    # The heat transfer is proportional to the average conductivity, the temperature difference, the contact area,
    # the inverse of the distance, and the time step.
    heat_transfer_right = k_right * delta_temp_right * contact_area / distance * delta_time
    # Calculate the heat transfer between each cell and its bottom neighbor, similar to the horizontal transfer.
    heat_transfer_down = k_down * delta_temp_down * contact_area / distance * delta_time

    # --- 4. Update Temperatures ---
    # Update the temperature of the cells by applying the calculated heat transfer.
    # For each pair of horizontal neighbors, the cell on the left loses heat, and the cell on the right gains heat.
    # The amount of heat gained or lost is divided by the cell's thermal capacity.
    # The array indexing is critical here: we are decreasing the temperature of cells in the left part of the grid
    # and increasing the temperature of the cells in the right part of the grid, but using the same heat_transfer
    # array to avoid double-counting.
    temp_grid[:, :-1] -= heat_transfer_right[:, :-1] / capacity_grid[:, :-1] # Cell on the left lose heat
    temp_grid[:, 1:] += heat_transfer_right[:, :-1] / capacity_grid[:, 1:] # Cell on the right gain heat

    # Do the same for vertical neighbors. The cell above loses heat, and the cell below gains it.
    # The temperature change is scaled by the inverse of the cell's thermal capacity.
    temp_grid[:-1, :] -= heat_transfer_down[:-1, :] / capacity_grid[:-1, :] # Cell above lose heat
    temp_grid[1:, :] += heat_transfer_down[:-1, :] / capacity_grid[1:, :] # Cell below gain heat

    # --- 5. Temperature Clamping ---
    # Ensure that no cell's temperature drops below MIN_TEMP (ambient temperature) and no cell's temperature exceeds MAX_TEMP.
    # We use np.clip() to limit the values to the range [MIN_TEMP, MAX_TEMP].
    np.clip(temp_grid, MIN_TEMP, MAX_TEMP, out=temp_grid)

    return temp_grid

def update_ignition(temperature_grid, ignition_temp_grid, humidity_grid, burned_grid):
    """
    Determines which cells should ignite based on their effective ignition temperature.

    This function calculates whether each cell in the grid should start burning
    based on its current temperature, the material's ignition temperature, and
    the material's humidity. It uses a vectorized approach with NumPy for
    efficient computation across the entire grid.

    Args:
        temperature_grid (np.ndarray): A 2D NumPy array representing the current
            temperature of each cell in the grid.
        ignition_temp_grid (np.ndarray): A 2D NumPy array representing the
            ignition temperature of the material in each cell.
        humidity_grid (np.ndarray): A 2D NumPy array representing the humidity
            level of the material in each cell.
        burned_grid (np.ndarray): A 2D NumPy array of boolean values indicating
            whether each cell has already burned out.

    Returns:
        np.ndarray: A 2D NumPy array of boolean values indicating whether each
            cell is currently on fire (`True`) or not (`False`).

    Process:
        1. Calculate Effective Ignition Temperature:
           - Computes the effective ignition temperature for each cell, taking
             into account the material's humidity.
           - The humidity increases the effective ignition temperature, making
             it harder for the cell to ignite.
           - A scaling factor (`material_humidity_effect_scale`) controls how
             much the humidity affects the effective ignition temperature.
           - Ensures the effective ignition temperature is at least 100.0, preventing
             unrealistically low values.
           - The formula is:
             `effective_ignition_temp = ignition_temp * (1 + humidity / material_humidity_effect_scale)`.
           - Then, a minimum effective ignition temperature of 100.0 is enforced.

        2. Determine Ignited Cells:
           - Compares the current temperature of each cell to its effective
             ignition temperature.
           - A cell ignites if its temperature is greater than or equal to its
             effective ignition temperature AND it has not already burned out.
           - The `burned_grid` is used to avoid re-igniting cells that have
             already been consumed.
           - The formula is:
             `is_burning_grid = (temperature_grid >= effective_ignition_temp) & (~burned_grid)`.
             - `&`: used for logical AND.
             - `~`: used for logical NOT.

    Assumptions:
        - Higher humidity makes ignition harder.
        - Cells that have already burned out cannot re-ignite.
        - A `material_humidity_effect_scale` factor is used to control the
          impact of humidity.
        - A minimum effective ignition temperature of 100.0 is enforced.
        - The formula used to calculate the effective ignition temperature is linear with humidity.
        - The formula used to determine the ignition is a simple comparison with the effective ignition temperature.
        - All parameters (temperature, ignition temperature, humidity, burned status) are available for each cell.
    """
    # --- 1. Calculate Effective Ignition Temperature ---
    # Define the factor controlling the impact of humidity on the effective ignition temperature.
    # A smaller scale value results in a higher effective ignition temperature.
    material_humidity_effect_scale = 200
    # Calculate the effective ignition temperature for each cell, considering the humidity of the material.
    # Higher humidity increases the effective ignition temperature, making ignition harder.
    effective_ignition_temp = ignition_temp_grid * (1 + humidity_grid / material_humidity_effect_scale)
    # Ensure that the effective ignition temperature is at least 100.0 to avoid unrealistic values.
    effective_ignition_temp = np.maximum(effective_ignition_temp, 100.0)

    # --- 2. Determine Ignited Cells ---
    # Determine which cells are currently burning.
    # A cell ignites if its temperature is at or above its effective ignition temperature AND it has not already burned.
    is_burning_grid = (temperature_grid >= effective_ignition_temp) & (~burned_grid)
    
    return is_burning_grid

def update_combustion(temperature_grid, fuel_grid, oxygen_grid, is_burning_grid, burn_rate_grid, combustion_heat_grid,
                      density_grid, thermal_capacity_grid, delta_time):
    """
    Updates the combustion state of cells in the grid based on fuel, oxygen, and burning status.

    This function simulates the combustion process in each cell, updating the amount of fuel and oxygen,
    the temperature, and the burning status based on the burn rate, combustion heat, density, and
    thermal capacity of the cell.

    Args:
        temperature_grid (np.ndarray): A 2D NumPy array representing the temperature of each cell.
        fuel_grid (np.ndarray): A 2D NumPy array representing the amount of fuel in each cell.
        oxygen_grid (np.ndarray): A 2D NumPy array representing the amount of oxygen in each cell.
        is_burning_grid (np.ndarray): A 2D NumPy array of boolean values indicating whether each cell is currently
        burning.
        burn_rate_grid (np.ndarray): A 2D NumPy array representing the burn rate of the material in each cell.
        combustion_heat_grid (np.ndarray): A 2D NumPy array representing the heat of combustion for the material in
        each cell.
        density_grid (np.ndarray): A 2D NumPy array representing the density of the material in each cell.
        thermal_capacity_grid (np.ndarray): A 2D NumPy array representing the thermal capacity of the material in
        each cell.
        delta_time (float): The time step for the simulation.

    Returns:
        tuple: A tuple containing the updated temperature_grid, fuel_grid, oxygen_grid, is_burning_grid, and burned_grid.

    Process:
        1. Calculate Fuel Consumption:
           - Determines the amount of fuel consumed in each burning cell based on the burn rate and time step.
           - Only burning cells (`is_burning_grid`) consume fuel.
           - The formula used is: `fuel_consumed = burn_rate * delta_time * is_burning_grid`.
        2. Update Fuel:
           - Decreases the fuel in each cell by the amount consumed.
           - Prevents negative fuel values by setting the minimum fuel to 0.0 using `np.maximum`.
        3. Calculate Heat Generation:
           - Computes the heat generated by combustion in each cell based on the fuel consumed and the heat of
             combustion.
           - The formula is: `heat_generated = fuel_consumed * combustion_heat * 1e7`.
           - The multiplication by 1e7 converts the result to the correct unit.
        4. Update Temperature:
           - Increases the temperature of each cell based on the heat generated, cell mass, and thermal capacity.
           - The formula is derived from: `Q = m * C * delta_T`, where Q is heat, m is mass, C is thermal
             capacity, and delta_T is the change in temperature.
           - We assume each cell has a volume of 1.0 m³.
           - We avoid excessive temperature by clamping it to `TEMP_MAX`.
        5. Update Oxygen:
           - Decreases the oxygen in each cell based on the fuel consumed.
           - Assumes a certain amount of oxygen is needed to burn a unit of fuel.
           - Prevents negative oxygen values by setting the minimum oxygen to 0.0 using `np.maximum`.
        6. Update Burning Status:
           - A cell stops burning if it has no fuel (`fuel_grid <= 0`), if it has not enough oxygen
            (`oxygen_grid < 5.0`) or it is already not burning (`~is_burning_grid`).
           - `&` is used for a logical AND operation.
        7. Update Burned Status :
            - A cell is considered `burned` if :
                - It has consumed all it's fuel `fuel_grid <= 0`.
                - It is not burning anymore AND have consumed all it's fuel `~is_burning_grid & (fuel_grid <= 1e-6)`.
                - It is not burning anymore AND have consumed all it's oxygen `~is_burning_grid & (oxygen_grid <= 5.0)`
            - Once a cell is `burned` there is no more fuel : `fuel_grid = np.where(burned_grid, 0.0, fuel_grid)`

    Assumptions:
        - Each cell has a volume of 1.0 m³.
        - Oxygen is consumed proportionally to fuel consumption.
        - The mass of a cell is obtained by multiplying its volume by its density.
        - The thermal capacity is considered to include the mass of the cell.
        - The heat of combustion is expressed in a certain unit (implied by the 1e7 conversion factor).
        - A cell stops burning if the oxygen level is below 5.0.
    """
    # --- 1. Calculate Fuel Consumption ---
    # Calculate the amount of fuel consumed in each burning cell.
    # 'is_burning_grid' is a boolean array; when used in arithmetic operations, True is treated as 1 and False as 0.
    # Therefore, only burning cells (True) will consume fuel.
    fuel_consumed = burn_rate_grid * delta_time * is_burning_grid

    # --- 2. Update Fuel ---
    # Decrease the fuel level in each cell by the consumed amount.
    fuel_grid -= fuel_consumed
    # Ensure fuel level does not go below zero.
    fuel_grid = np.maximum(fuel_grid, 0.0) # Prevent negative

    # --- 3. Calculate Heat Generation ---
    # Calculate the heat generated by the combustion of the consumed fuel.
    cell_volume = 1.0  # Assumption: 1 m³ per cell.
    cell_mass = cell_volume * density_grid

    # Heat generated per cell (assuming 1m³ and some implicit units for combustion_heat).
    heat_generated = fuel_consumed * combustion_heat_grid * 1e7 #1e6

    # --- 4. Update Temperature ---
    # Calculate the temperature change due to the heat generated.
    # We use the formula : delta_T = heat_generated / (mass * specific_heat_capacity)
    delta_temp = heat_generated / (cell_mass * thermal_capacity_grid * 1e3)
    # Update temperature by adding the temperature change.
    temperature_grid += delta_temp
    # Ensure that the maximum value is not exceeded.
    temperature_grid = np.minimum(temperature_grid, MAX_TEMP)

    # --- 5. Update Oxygen ---
    # Decrease the oxygen level in each cell based on fuel consumed.
    oxygen_consumed = fuel_consumed * 10.0 # 2.0
    oxygen_grid -= oxygen_consumed * delta_time
    # Ensure oxygen level does not go below zero.
    oxygen_grid = np.maximum(oxygen_grid, 0.0)

    # --- 6. Update Burning Status ---
    # Update the burning state based on fuel and oxygen availability.
    is_burning_grid &= (oxygen_grid > 5.0) & (fuel_grid > 0)

    # --- 7. Update Burned Status ---
    # Update the burned status if :
    # -There is no more fuel.
    # -If there is no more fuel AND the cell is not burning.
    # -If there is not enough oxygen AND the cell is not burning.
    burned_grid = fuel_grid <= 0
    burned_grid = burned_grid | (~is_burning_grid & (fuel_grid <= 1e-7))
    burned_grid = burned_grid | (~is_burning_grid & (oxygen_grid <= 5.0))

    # If burned status is True, there is no more fuel.
    fuel_grid = np.where(burned_grid, 0.0, fuel_grid)

    return temperature_grid, fuel_grid, oxygen_grid, is_burning_grid, burned_grid