"""
Column names of the source Excel files.

The files are provided in French, so their headers stay in French; the rest of the
code refers to them through these constants.
"""

# --- MES (manufacturing execution: one row per assembly operation) ---
MES_STATION = "Poste"
MES_STEP = "Nom"
MES_REFERENCES = "Référence"          # "A511;A337;..." list of part codes
MES_PLANNED_TIME = "Temps Prévu"
MES_ACTUAL_TIME = "Temps Réel"
MES_DATE = "Date"
MES_START_TIME = "Heure Début"
MES_INCIDENT = "Aléas Industriels"
MES_ROOT_CAUSE = "Cause Potentielle"

# --- PLM (product lifecycle: one row per part) ---
PLM_CODE = "Code / Référence"
PLM_NAME = "Désignation"
PLM_SUPPLIER = "Fournisseur"
PLM_LEAD_TIME = "Délai Approvisionnement"
PLM_CRITICALITY = "Criticité"
PLM_MASS = "Masse (kg)"
PLM_UNIT_COST = "Coût achat pièce (€)"
PLM_CAD_HOURS = "Temps CAO (h)"

# --- ERP (staff: one row per operator) ---
ERP_ID = "Matricule"
ERP_FIRST_NAME = "Prénom"
ERP_LAST_NAME = "Nom"
ERP_AGE = "Âge"
ERP_QUALIFICATION = "Qualification"
ERP_CERTIFICATIONS = "Habilitations"    # "Électrique, Pneumatique"
ERP_HOME_STATION = "Poste de montage"   # "Poste N" = home team of station N
ERP_HOURLY_COST = "Coût horaire (€)"
ERP_EXPERIENCE = "Niveau d'expérience"
ERP_ROTATION = "Rotation"               # "Semaine 1: Poste 55 | Semaine 3: Poste 50"

# --- Values used in the data ---
EXPERIENCE_LEVELS = ["Expert", "Confirmé", "Débutant"]  # most to least experienced
EXPERIENCE_LABELS = {"Expert": "Expert", "Confirmé": "Confirmed", "Débutant": "Beginner"}
