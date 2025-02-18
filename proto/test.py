import numpy as np

def choisir_evenement(probabilites):
  """Choisit un événement aléatoire en fonction des probabilités données.

  Args:
    probabilites: Un dictionnaire où les clés sont les événements et les valeurs sont leurs probabilités.

  Returns:
    L'événement choisi.
  """

  # Générer un nombre aléatoire entre 0 et 1
  nombre_aleatoire = np.random.random()

  # Calculer les seuils cumulatifs de probabilité
  seuil_cumulatif = 0
  for evenement, probabilite in probabilites.items():
    seuil_cumulatif += probabilite
    if nombre_aleatoire < seuil_cumulatif:
      return evenement

# Définir les probabilités des événements
probabilites = {
    "A": 0.5,
    "B": 0.45,
    "C": 0.05
}

# Choisir un événement aléatoire
evenement_choisi = choisir_evenement(probabilites)

# Afficher l'événement choisi
print(f"L'événement choisi est : {evenement_choisi}")