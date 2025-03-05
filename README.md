# 🔥 Fire Propagation Simulation
**A realistic simulation of fire propagation** using thermodynamic and combustion principles, developed in Python with Pygame and NumPy.

[![Watch the video](/assets/readme/thumbnail.png)](https://youtu.be/OmK2kF2qTYU?si=1zg0MunhyuBElVxR)

## 📜 Description
This project models the propagation of a fire in a 2D environment composed of different materials. It integrates physical mechanisms such as:
- **Thermal conduction** between neighboring cells.
- **Self-sustained combustion** with fuel and oxygen consumption.
- The impact of **humidity** and material properties on ignition.

The simulation takes the form of a grid made up of a number of cells, each of which acts as a unit of space with a number of physical attributes, such as temperature or oxygen rate. Each cell also contains a material with intrinsic physical properties. 

![Cell](/assets/readme/cell.png)

The simulation supports 4 different materials:
- **Wood**
- **Grass**
- **Water** (_non-combustible_)
- **Gasoline**

These materials are randomly distributed on the grid according to the probability of appearance of each material.

## 🧮 Calculation of thermal reactions

### **Matrix-Based Calculations**
To achieve efficient and scalable simulation of fire propagation across a grid of cells, we utilize **NumPy arrays and vectorized operations**. This approach offers significant performance advantages over traditional Python loops, especially for large grids.

Instead of iterating through each cell individually, we represent key physical properties as 2D NumPy matrices (grids). This allows us to perform calculations on the entire grid (or parts of it) simultaneously using NumPy highly optimized functions.

At each frame of the simulation, the physical properties of the grid cells are extracted and aligned into separate matrices for processing by vectorization functions simulating the main thermal reactions. The modified matrix elements are then reinjected into their respective grid cells. The operation is repeated at the next frame.

![Matrices](/assets/readme/matrices.png)

**Matrices used in calculation**

| Grid name            | Description                                                                         |
|----------------------|-------------------------------------------------------------------------------------|
| temp_grid            | Temperature of each cell in the grid (°C)                                           |
| conductivity_grid    | Thermal conductivity of the material in each cell (W/(m·K)).                        |
| capacity_grid        | Thermal capacity of the material in each cell (kJ/(kg·K)).                          |
| fuel_grid            | Amount of combustible material in each cell (%).                                    |
| oxygen_grid          | Oxygen rate in each cell (%).                                                       |
| humidity_grid        | Humidity of the material in each cell (%).                                          |
| ignition_temp_grid   | Ignition temperature of the material in each cell (°C).                             |
| burn_rate_grid       | Burn rate of the material in each cell (kg/m²/s).                                   |
| combustion_heat_grid | Heat of combustion of the material in each cell (MJ/kg).                            |
| density_grid         | Density of the material in each cell (kg/m³).                                       |
| burned_grid          | Boolean matrix indicating whether each cell is in a "burned" state (fuel depleted). |

By using these matrices, the physics functions (described below) can perform calculations in a vectorized manner, significantly speeding up the simulation.

### Physics functions
These matrices of physical attributes are processed successively by three functions carrying out vectorization operations on them to simulate thermal reactions: `heat_conduction`, `update_ignition` and `update_combustion`.

#### Heat conduction
Simulates **heat transfer by conduction** between neighboring cells in the grid.
- **Arguments**:
  - temp_grid
  - conductivity_grid
  - capacity_grid
- **Returns**
  - Updated temp_grid

Heat conduction is the transfer of thermal energy through direct contact, from hotter regions to colder regions. The rate of heat transfer depends on:
- **Thermal conductivity (`conductivity_grid`):**  How well the material conducts heat.
- **Temperature difference (`delta_temp`):** The driving force for heat transfer.
- **Contact area (`contact_area`):** The area through which heat is exchanged between cells.
- **Distance (`distance`):** The distance between the centers of neighboring cells.
- **Time interval (`delta_time`):** The duration over which heat transfer occurs

**Simplified Formula (applied between each cell and its right/bottom neighbor):**

$Q conduction = K * (T source - T target) * A / d * Δt$

Where:

- `Q_conduction` is the amount of heat transferred.
- `K` is the thermal conductivity (from `conductivity_grid`).
- `T_source` and `T_target` are the temperatures of the source and target cells (from `temp_grid`).
- `A` is the approximate contact area between cells (`CELL_WIDTH * CELL_HEIGHT`).
- `d` is the approximate distance between cell centers (`sqrt(CELL_WIDTH^2 + CELL_HEIGHT^2)`).
- `Δt` is `delta_time`.

**Matrix Implementation Details :**

The function uses Numpy vectorized operations to:

1.  **Calculate temperature differences (`delta_temp_right`, `delta_temp_down`):**  Efficiently computes the temperature difference between each cell and its right/bottom neighbor using array slicing and subtraction.
2.  **Calculate average interface conductivity (`k_right`, `k_down`):**  Calculates the average thermal conductivity at the interface between neighboring cells, using array slicing and averaging.
3.  **Calculate heat transfer (`heat_transfer_right`, `heat_transfer_down`):** Applies the conduction formula in a vectorized manner for all horizontal and vertical cell pairs.
4.  **Update cell temperatures (`temp_grid`):**  Adjusts the temperature of each cell based on the heat gained from and lost to its neighbors, taking into account the material's thermal capacity (`capacity_grid`).  Crucially, these updates are done in a way that avoids double-counting heat exchange between cell pairs.
5.  **Clamp min/max temperature:** Ensures cell temperature remains within MIN_TEMP, MAX_TEMP range to avoid outliers

**Key Parameters:**

*   `conductivity_grid`: Material-dependent property controlling how easily heat flows through each cell.
*   `capacity_grid`: Material-dependent property controlling how much heat is needed to change the temperature of each cell.
*   `delta_time`:  Simulation time step, controlling the frequency of heat transfer updates.

#### Update ignition
Determines which cells will **ignite** (start burning) based on their temperature and material properties.
- **Arguments**:
  - temp_grid
  - ignition_temp_grid
  - humidity_grid
  - burned_grid
- **Returns**
  - is_burning_grid (boolean Numpy array)

A material ignites when its temperature reaches or exceeds its **ignition temperature**.  This ignition temperature is affected by the **humidity** of the material and the surrounding environment. Higher humidity makes ignition more difficult.

**Simplified Formula for Effective Ignition Temperature:**

$Effective Ignition Temperature = Ignition Temperature * (1 + Humidity / Humidity Effect Scale)$

Where:

- `Ignition_Temperature` is the base ignition temperature of the material (from `ignition_temp_grid`).
- `Humidity` is the material humidity rate.
- `Humidity_Effect_Scale` (`HUMIDITY_EFFECT_SCALE`) is a constant controlling the overall sensitivity of ignition temperature to humidity.

**Matrix Implementation Details :**

1.  **Calculate effective ignition temperature (`effective_ignition_temp`):** Computes the effective ignition temperature for each cell, taking into account both material and cell humidity using vectorized operations.
2.  **Determine burning cells (`is_burning_grid`):**  Creates a boolean matrix `is_burning_grid` where `True` indicates cells that meet the ignition condition: their temperature (`temperature_grid`) is greater than or equal to their effective ignition temperature, and they are not already burned (`~burned_grid`).

**Key Parameters:**

- `ignition_temp_grid`: Material-dependent property representing the base temperature at which each material ignites.
- `humidity_grid`: Material-dependent humidity, affecting ignition temperature.
- `cell_humidity_rate_grid`: Cell-specific humidity, representing environmental humidity, also affecting ignition temperature.
- `HUMIDITY_EFFECT_SCALE`: Global parameter controlling the sensitivity of ignition to humidity.

#### Update combustion
Simulates the **combustion process** for cells that are currently burning.
- **Arguments**:
  - temp_grid
  - fuel_grid
  - oxygen_grid
  - is_burning_grid
  - burn_rate_grid
  - combustion_heat_grid
  - density_grid
  - thermal_capacity_grid
- **Returns**
  - temperature_grid
  - fuel_grid
  - oxygen_grid
  - is_burning_grid
  - burned_grid

Combustion is a chemical process that:

- **Consumes fuel (`fuel_grid`):** The amount of fuel consumed depends on the **burn rate** of the material (`burn_rate_grid`) and the duration of combustion (`delta_time`).
- **Generates heat (`heat_generated`):** The amount of heat released depends on the **heat of combustion** of the material (`combustion_heat_grid`) and the amount of fuel consumed. This heat increases the cell's temperature.
- **Consumes oxygen (`oxygen_grid`):** Combustion requires oxygen. The simulation models oxygen consumption, potentially leading to oxygen depletion and self-extinguishment.
- **Stops when fuel or oxygen is depleted:** Combustion ceases when either the fuel is exhausted or the oxygen level falls below a critical threshold.

**Simplified Formulas**

- Fuel consumed = $Burn Rate * Δt * is burning grid$
- Heat generation = $Fuel Consumed * Combustion Heat$
- Temperature Increase = $Heat Generated / (Cell Mass * Thermal Capacity)$
- Oxygen Consumption = $Fuel Consumed * Oxygen Consumption Factor$

**Matrix Implementation Details :**

1.  **Calculate fuel consumed (`fuel_consumed`):** Vectorized calculation of fuel consumption based on `burn_rate_grid`, `delta_time`, and the boolean `is_burning_grid` (combustion only occurs in cells where `is_burning_grid` is `True`).
2.  **Update fuel level (`fuel_grid`):** Decreases the fuel level in burning cells and ensures it does not go below zero.
3.  **Calculate heat generated (`heat_generated`):**  Vectorized calculation of heat release based on `fuel_consumed` and `combustion_heat_grid`.
4.  **Calculate temperature increase (`delta_temp`):**  Calculates the temperature increase for each burning cell based on `heat_generated`, cell mass (approximated using `density_grid` and a unit volume), and `thermal_capacity_grid`.
5.  **Update temperature (`temperature_grid`):** Increases the temperature of burning cells, clamping it to a maximum value.
6.  **Calculate oxygen consumed (`oxygen_consumed`):** Vectorized calculation of oxygen consumption, linked to fuel consumption.
7.  **Update oxygen level (`oxygen_grid`):** Decreases the oxygen level in burning cells, ensuring it does not go below zero.
8.  **Update `is_burning_grid`:**  Updates the `is_burning_grid` boolean matrix. Combustion is stopped for cells where either the oxygen level is too low (below a threshold, e.g., 5%) or the fuel is depleted.
9.  **Update `burned_grid`:** Updates the `burned_grid` boolean matrix to mark cells as burned when combustion has ceased due to fuel depletion or lack of oxygen.

**Key Parameters:**

*   `burn_rate_grid`: Material-dependent property determining how quickly each material burns.
*   `combustion_heat_grid`: Material-dependent property representing the energy released when each material burns.
*   `density_grid`: Material-dependent density, used to estimate cell mass for temperature calculations.
*   `thermal_capacity_grid`: Material-dependent property affecting how temperature changes with heat input.
*   `delta_time`: Simulation time step.
*   `OXYGEN_CONSUMPTION_FACTOR`: Simplified ratio determining oxygen consumption relative to fuel consumption.
*   `MIN_OXYGEN_RATE`: Minimum oxygen level below which combustion cannot be sustained (currently set to 5.0%).

### Simplification and Limitations
It's important to note that this simulation employs several simplifications for computational efficiency and to focus on the core mechanisms of fire propagation. Key simplifications include:
- **2D Grid:** The simulation is currently 2-dimensional, neglecting vertical fire spread and 3D effects.


- **Homogeneous Cells:** Cells are treated as homogeneous units with uniform material properties and temperature.


- **Simplified Combustion Model:** The combustion model is a simplified representation of complex chemical processes, using a constant burn rate and heat of combustion.


- **Empirical Parameters:** Parameters were defined empirically to compensate for certain drawbacks associated with the simplifications made to the simulation. MAX_TEMP, for example, is used to prevent combustion from getting out of control.

> **Temperature limit**: In a limited, confined grid, cells located at the edges and corners have fewer “neighbors” to which to dissipate heat by conduction. In other words, they are less well “cooled” by conduction to the outside of the burning zone. In an infinite or very large grid, every cell is surrounded by neighbors, and heat can spread outwards more easily. The containment of the grid therefore reduces the cooling potential, and heat generated by combustion tends to accumulate more in a confined space. If the heat cannot escape efficiently to the outside, the overall temperature of the grate (or burning zone) will tend to rise more rapidly and potentially excessively. The current simulation only considers conduction as the heat transfer mechanism between cells, in reality, a fire loses heat to the environment via several important mechanisms that are not implemented in this model, such as thermal radiation to the atmosphere or convection to the ambient air. In the absence of these heat loss mechanisms, the heat generated by combustion is even more likely to accumulate in the grid, exacerbating thermal runaway and necessitating the use of a MAX_TEMP to artificially limit the temperature.