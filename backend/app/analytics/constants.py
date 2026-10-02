"""Palette, category orders and keyword dictionaries used by the analyses."""

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"

COLORS = {
    "surface": "#fcfcfb",
    "text": "#0b0b0b",
    "text2": "#52514e",
    "muted": "#8a8984",
    "grid": "#e8e7e3",
    "border": "#dedcd6",
    # categorical series, fixed order
    "s1": "#2a78d6",  # blue
    "s2": "#eb6834",  # orange
    "s3": "#1baf7a",  # aqua
    # sequential blue
    "seq": ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
    "seq_light": "#9ec5f4",
    "seq_dark": "#256abf",
}

# PLM criticality (source value -> English label), lowest to highest.
CRITICALITY_LABELS = {"Basse": "Low", "Moyenne": "Medium", "Haute": "High", "Critique": "Critical"}
CRITICALITY_ORDER = list(CRITICALITY_LABELS.values())
CRITICALITY_WEIGHT = {label: i + 1 for i, label in enumerate(CRITICALITY_ORDER)}
CRITICALITY_COLOR = {"Low": "#0ca30c", "Medium": "#fab219", "High": "#ec835a", "Critical": "#d03b3b"}
HIGH_CRITICALITY = ["High", "Critical"]
NO_PARTS = "No parts"

# ERP experience score by English level label.
EXPERIENCE_SCORE = {"Beginner": 1, "Confirmed": 2, "Expert": 3}

# Free-text MES incidents are grouped into families by keyword.
# Keywords stay in French because they are matched against the French source text.
INCIDENT_FAMILIES = [
    ("Shop-floor environment", ["température", "thermique", "ventilation", "climatisation", "refroidissement",
                                "surchauffe", "contamination", "pression", "vibration"]),
    ("IT systems & automation", ["logiciel", "réseau", "synchronisation", "désynchronisation",
                                 "communication", "traçabilité", "référencement", "robots",
                                 "automatis", "guidage", "protocoles"]),
    ("Quality & metrology", ["qualité", "calibration", "contrôle", "paramètres", "positionnement",
                             "placement", "adhérence", "marquage", "impression"]),
    ("Tooling & equipment wear", ["outillage", "usure", "gabarit", "serrage", "soudure",
                                  "lubrification", "déformation", "supports"]),
    ("Electrical", ["électrique", "connectique"]),
    ("Logistics & handling", ["manutention", "transport"]),
    ("Maintenance & major failures", ["maintenance", "défaillance majeure"]),
]

ROOT_CAUSE_THEMES = [
    ("Insufficient / deferred maintenance", ["maintenance", "intervalles", "planning"]),
    ("Ageing / obsolescence", ["obsolète", "obsolescence", "vieillissement", "vétusté", "fin de vie",
                               "usé", "usure", "sous-investissement", "dégradé"]),
    ("Procedures / training", ["procédure", "formation", "non respectées"]),
    ("IT systems / software", ["système d'information", "logiciel", "bugs", "programmation",
                               "mise à jour", "protocole", "interfaces", "communication", "réseau"]),
    ("Control / environment", ["régulation", "environnement", "filtration", "filtres", "climatisation",
                               "isolation", "refroidissement", "thermique", "température", "anti-vibration"]),
    ("Sensors / calibration", ["capteur", "étalonnage", "instruments", "calibration", "dérive"]),
    ("Materials / consumables", ["matériaux", "lubrifiant", "oxydation", "qualité matériaux"]),
    ("Throughput / intensive cycles", ["cycles intensifs", "cycles répétitifs", "contraintes"]),
]
OTHER = "Other"
