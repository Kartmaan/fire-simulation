from enum import Enum
from dataclasses import dataclass

from src.colors import Colors

colors = Colors()

# Une dataclass est une classe spécialement conçue pour contenir des données.
# Le décorateur se charge de générer automatiquement les méthodes spéciales telles que __init__, __repr__, etc.
# Une dataclass met donc l'accent sur les données et la concision.
@dataclass
class MaterialProperties:
    """
    Propriétés physiques communes à tous les matériaux.

    ignition_temp : Température à laquelle le matériau commence à brûler.
    combustion_heat : Énergie libérée par unité de masse lors de la combustion.
    burn_rate : Vitesse à laquelle le matériau brûle une fois enflammé (masse perdue par unité de temps).
    thermal_conductivity : Capacité du matériau à conduire la chaleur.
    thermal_capacity : Quantité de chaleur nécessaire pour augmenter la température du matériau.
    density : Masse par unité de volume, qui influence la quantité de combustible disponible.
    humidity : Quantité d'eau dans le matériau, qui peut retarder l'ignition et la combustion.
    emissivity : Capacité du matériau à émettre de l'énergie thermique par rayonnement.
    """
    ignition_temp: float # °C
    combustion_heat: float # MJ/kg
    burn_rate: float # kg/m²/s
    thermal_conductivity: float # W(m.K)
    thermal_capacity: float # (KJ/(kg.K))
    density: float # kg/m3
    humidity: float # %
    emissivity: float # [0,1]
    color: tuple

class Material(Enum):
    """
    Enumération des matériaux et de leurs propriétés physiques intrinsèques.
    """
    WOOD = MaterialProperties(ignition_temp=300.0,
                              combustion_heat=18.0,
                              burn_rate=0.35,
                              thermal_conductivity=0.2,
                              thermal_capacity=1.8,
                              density=650.0,
                              humidity=10.0,
                              emissivity=0.8,
                              color=colors.wood)

    GRASS = MaterialProperties(ignition_temp=300.0,
                              combustion_heat=18.0,
                              burn_rate=0.5,
                              thermal_conductivity=0.2,
                              thermal_capacity=2.0,
                              density=80.0,
                              humidity=25.0,
                              emissivity=0.8,
                              color=colors.grass)

    FUEL = MaterialProperties(ignition_temp=100.0,
                              combustion_heat=40.0,
                              burn_rate=0.8,
                              thermal_conductivity=0.3,
                              thermal_capacity=1.8,
                              density=750.0,
                              humidity=2.0,
                              emissivity=0.8,
                              color=colors.fuel)