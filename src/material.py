from enum import Enum
from dataclasses import dataclass

from src.physics import MAX_TEMP
from src.colors import Colors

colors = Colors()

@dataclass
class MaterialProperties:
    """
    Physical properties common to all materials.

    ignition_temp: Temperature at which the material begins to burn.
    combustion_heat: Energy released per unit mass during combustion.
    burn_rate: Speed at which the material burns once ignited (mass lost per unit time).
    thermal_conductivity: Material's ability to conduct heat.
    thermal_capacity: Amount of heat required to raise the temperature of the material.
    density: Mass per unit volume, which influences the amount of fuel available.
    humidity: Quantity of water in the material, which can retard ignition and combustion.
    emissivity: Material's capacity to emit thermal energy by radiation.
    """
    ignition_temp: float # °C
    combustion_heat: float # MJ/kg
    burn_rate: float # kg/m²/s
    thermal_conductivity: float # W(m.K)
    thermal_capacity: float # (KJ/(kg.K))
    density: float # kg/m3
    humidity: float # %
    emissivity: float # [0,1] # Not used
    color: tuple

class Material(Enum):
    """
    Listing of materials and their intrinsic physical properties.
    """
    WOOD = MaterialProperties(ignition_temp=350.0, #300-400
                              combustion_heat=17.0, #16-18
                              burn_rate=0.4, #0.35 0.04
                              thermal_conductivity=0.25, #0.8 0.25
                              thermal_capacity=1.45, #1
                              density=745.0,
                              humidity=12.0,
                              emissivity=0.9,
                              color=colors.wood)

    GRASS = MaterialProperties(ignition_temp=300.0, #250-350
                              combustion_heat=15.5, #14-17
                              burn_rate=0.5, #0.5 0.1
                              thermal_conductivity=0.07, #1.8 0.07
                              thermal_capacity=2.2, #1.2
                              density=100.0,
                              humidity=70.0, #25
                              emissivity=0.9,
                              color=colors.grass)

    FUEL = MaterialProperties(ignition_temp=250.0, #250-350
                              combustion_heat=43.0, #42-46
                              burn_rate=0.8, #0.8 0.08
                              thermal_conductivity=0.14, #0.8 0.14
                              thermal_capacity=1.9, #1
                              density=845.0,
                              humidity=0.1, #2
                              emissivity=0.9,
                              color=colors.fuel)

    WATER = MaterialProperties(ignition_temp=MAX_TEMP*2, # NO COMBUSTION
                              combustion_heat=0.0,
                              burn_rate=0.0,
                              thermal_conductivity=0.6,
                              thermal_capacity=4.18,
                              density=1000.0,
                              humidity=100.0,
                              emissivity=0.9,
                              color=colors.water)

    # -------------------------------------------------------------------
    #                    MATERIALS FOR TEST PURPOSES
    # -------------------------------------------------------------------
    _WOOD = MaterialProperties(ignition_temp=300.0,
                               combustion_heat=18.0,
                               burn_rate=0.35,
                               thermal_conductivity=0.5,  # ⬆️
                               thermal_capacity=1.0,  # ⬇️
                               density=650.0,
                               humidity=10.0,
                               emissivity=0.8,
                               color=colors.wood)