# =============================================================================
# APPLICATION STREAMLIT - DÉMOGRAPHIE DES MÉTROPOLES FRANÇAISES
# Grenoble · Rennes · Saint-Étienne · Rouen · Montpellier
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path
import unicodedata

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Démographie & Environnement · Métropoles",
    page_icon="Logo-métro.jpg",
    layout="wide",
)

if "page" not in st.session_state:
    st.session_state.page = "home"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

div[data-testid="metric-container"] {
    background: #F7FBF8; border: 1px solid #C8E6D4;
    border-radius: 10px; padding: 14px 18px;
}
div[data-testid="metric-container"] label {
    color: #4A7C59 !important; font-size: 0.75rem;
    font-weight: 600; text-transform: uppercase; letter-spacing:.05em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem; color: #1C3A27; font-weight: 700;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: #EEF4F0; border-radius: 10px; padding: 5px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; padding: 8px 20px;
    font-size: 0.87rem; font-weight: 600; color: #4A7C59;
}
.stTabs [aria-selected="true"] { background: #2D6A4F !important; color: white !important; }
.section-header {
    font-size: 1.15rem; font-weight: 700; color: #1C3A27;
    border-bottom: 2px solid #2D6A4F; padding-bottom: 5px; margin-bottom: 16px;
}
.source-note { font-size: 0.72rem; color: #88A898; margin-top: -12px; margin-bottom: 18px; }

/* ── Bandeau filtres haut de page ── */
.filter-bar {
    background: #F0F7F3;
    border: 1px solid #C8E6D4;
    border-radius: 12px;
    padding: 16px 20px 12px 20px;
    margin-bottom: 20px;
}
.filter-bar-title {
    font-size: 0.72rem; font-weight: 700; color: #4A7C59;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 10px;
}

/* Cartes KPI CSP */
.kpi-card {
    background-color: white; padding: 20px 25px; border-radius: 12px;
    border-left: 6px solid #2D6A4F; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    text-align: center; margin-bottom: 10px;
}
.kpi-label { font-size: 12px; font-weight: 700; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 28px; font-weight: 800; color: #1C3A27; margin: 5px 0; }
.kpi-subtitle { font-size: 11px; color: #95a5a6; }

/* Cartes KPI mobilités */
.kpi-card-mob {
    background-color: white; padding: 20px; border-radius: 12px;
    border-top: 5px solid #2D6A4F; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    text-align: center; margin-bottom: 10px;
}

/* ── Boutons de navigation sidebar (même style que le bouton Accueil) ── */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex; flex-direction: column; gap: 6px;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: #F0F7F3;
    border: 1px solid #C8E6D4;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
    font-weight: 600;
    font-size: 0.88rem;
    color: #2D6A4F;
    width: 100%;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: #DDF0E8;
    border-color: #2D6A4F;
    box-shadow: 0 2px 8px rgba(45,106,79,0.15);
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"][aria-checked="true"] {
    background: #2D6A4F !important;
    border-color: #2D6A4F !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(45,106,79,0.25);
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] span[data-testid="stMarkdownContainer"] p {
    margin: 0; font-weight: 600;
}
/* Masquer le rond radio natif */
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[data-testid="stWidgetLabel"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}

/* Badges de thématiques */
.theme-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.badge-demo { background: #E6FFFA; color: #2D6A4F; }
.badge-solid { background: #FFF5F5; color: #C45B2A; }
.badge-env { background: #E8F5E9; color: #1B5E20; } /* Style Environnement */
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 2. CONSTANTES
# ──────────────────────────────────────────────────────────────────────────────
COMMUNES = {
    "Grenoble": [
        "Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix","Corenc",
        "Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon","Gières","Grenoble",
        "Herbeys","Jarrie","La Tronche","Le Gua","Le Pont-de-Claix","Le Sappey-en-Chartreuse",
        "Meylan","Miribel-Lanchâtre","Mont-Saint-Martin","Montchaboud","Murianette",
        "Notre-Dame-de-Commiers","Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux",
        "Quaix-en-Chartreuse","Saint-Barthélemy-de-Séchilienne","Saint-Égrève",
        "Saint-Georges-de-Commiers","Saint-Martin-d'Hères","Saint-Martin-le-Vinoux",
        "Saint-Paul-de-Varces","Saint-Pierre-de-Mésage","Sarcenas","Sassenage","Séchilienne",
        "Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset","Vaulnaveys-le-Bas",
        "Vaulnaveys-le-Haut","Venon","Veurey-Voroize","Vif","Vizille",
    ],
    "Rennes": [
        "Acigné","Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné","Chantepie",
        "Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé",
        "La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger",
        "Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères","Pacé",
        "Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel","Saint-Erblon",
        "Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt",
        "Thorigné-Fouillard","Vern-sur-Seiche","Vezin-le-Coquet","Clayes",
        "La Chapelle-Chaussée","Laillé","Langan","Miniac-sous-Bécherel",
    ],
    "Rouen": [
        "Amfreville-la-Mi-Voie","Anneville-Ambourville","Bardouville","Belbeuf","Berville-sur-Seine",
        "Bihorel","Bois-Guillaume","Bonsecours","Boos","Canteleu","Caudebec-lès-Elbeuf","Cléon",
        "Darnétal","Déville-lès-Rouen","Duclair","Elbeuf","Épinay-sur-Duclair",
        "Fontaine-sous-Préaux","Franqueville-Saint-Pierre","Freneuse","Gouy","Grand-Couronne",
        "Hautot-sur-Seine","Hénouville","Houppeville","Isneauville","Jumièges","La Bouille",
        "La Londe","La Neuville-Chant-d'Oisel","Le Grand-Quevilly","Le Houlme","Le Mesnil-Esnard",
        "Le Mesnil-sous-Jumièges","Le Petit-Quevilly","Le Trait",
        "Les Authieux-sur-le-Port-Saint-Ouen","Malaunay","Maromme","Mont-Saint-Aignan","Montmain",
        "Moulineaux","Notre-Dame-de-Bondeville","Oissel-sur-Seine","Orival","Petit-Couronne",
        "Quevillon","Quévreville-la-Poterie","Roncherolles-sur-le-Vivier","Rouen","Sahurs",
        "Saint-Aubin-Celloville","Saint-Aubin-Épinay","Saint-Aubin-lès-Elbeuf",
        "Saint-Étienne-du-Rouvray","Saint-Jacques-sur-Darnétal","Saint-Léger-du-Bourg-Denis",
        "Saint-Martin-de-Boscherville","Saint-Martin-du-Vivier","Saint-Paër",
        "Saint-Pierre-de-Manneville","Saint-Pierre-de-Varengeville","Saint-Pierre-lès-Elbeuf",
        "Sainte-Marguerite-sur-Duclair","Sotteville-lès-Rouen","Sotteville-sous-le-Val",
        "Tourville-la-Rivière","Val-de-la-Haye","Yainville","Ymare","Yville-sur-Seine",
    ],
    "Saint-Étienne": [
        "Aboën","Andrézieux-Bouthéon","Caloire","Cellieu","Chagnon","Chambœuf","Châteauneuf",
        "Dargoire","Doizieux","Farnay","Firminy","Fontanès","Fraisses","Genilac","L'Étrat",
        "L'Horme","La Fouillouse","La Gimond","La Grand-Croix","La Ricamarie","La Talaudière",
        "La Terrasse-sur-Dorlay","La Tour-en-Jarez","La Valla-en-Gier","Le Chambon-Feugerolles",
        "Lorette","Marcenod","Pavezin","Rive-de-Gier","Roche-la-Molière","Rozier-Côtes-d'Aurec",
        "Saint-Bonnet-les-Oules","Saint-Chamond","Saint-Christo-en-Jarez","Saint-Étienne",
        "Saint-Galmier","Saint-Genest-Lerpt","Saint-Héand","Saint-Jean-Bonnefonds","Saint-Joseph",
        "Saint-Martin-la-Plaine","Saint-Maurice-en-Gourgois","Saint-Nizier-de-Fornas",
        "Saint-Paul-en-Cornillon","Saint-Paul-en-Jarez","Saint-Priest-en-Jarez",
        "Saint-Romain-en-Jarez","Sainte-Croix-en-Jarez","Sorbiers","Tartaras",
        "Unieux","Valfleury","Villars",
    ],
    "Montpellier": [
        "Baillargues","Beaulieu","Castelnau-le-Lez","Castries","Clapiers","Cournonsec",
        "Cournonterral","Fabrègues","Grabels","Jacou","Juvignac","Lattes","Lavérune","Le Crès",
        "Montaud","Montferrier-sur-Lez","Montpellier","Murviel-lès-Montpellier","Pérols","Pignan",
        "Prades-le-Lez","Restinclières","Saint-Brès","Saint-Drézéry","Saint-Geniès-des-Mourgues",
        "Saint-Georges-d'Orques","Saint-Jean-de-Védas","Saussan","Sussargues","Vendargues",
        "Villeneuve-lès-Maguelone",
    ],
}

COMMUNE_VERS_METRO = {c: m for m, lst in COMMUNES.items() for c in lst}

NOM_EPCI = {
    "Grenoble":      "EPCI : Grenoble-Alpes-Métropole (200040715)",
    "Rennes":        "EPCI : Rennes Métropole (243500139)",
    "Rouen":         "EPCI : Rouen Normandie (200023414)",
    "Saint-Étienne": "EPCI : Saint-Etienne Métropole (244200770)",
    "Montpellier":   "EPCI : Montpellier Méditerranée Métropole (243400017)",
}
DR24_MAP = {"Grenoble": 38, "Rennes": 35, "Rouen": 76, "Saint-Étienne": 42, "Montpellier": 34}

# ── Palettes harmonisées ──────────────────────────────────────────────────────
PALETTE_METRO   = px.colors.sequential.Greys[2:]
PALETTE_COMMUNE = px.colors.sequential.Greens_r

COULEURS = {
    "Montpellier": "#77818C",
    "Saint-Étienne": "#A2A6AE",
    "Grenoble": "#3D4550",
    "Rennes": "#C5C9CE",
    "Rouen": "#E8E8EB",
}

TOUTES = list(COMMUNES.keys())

# Sélection partagée des métropoles entre tous les onglets
if "shared_metros" not in st.session_state:
    st.session_state.shared_metros = list(TOUTES)

# Clés widget par thématique (permet de conserver les métropoles sélectionnées par exemple)
METRO_KEYS_DEMO = [
    ("sel_t1",   TOUTES),
    ("age_metros", TOUTES),
    ("mob_metros", TOUTES),
    ("transp_metros", TOUTES),
    ("men_metros", TOUTES),
    ("log_metros", TOUTES),
    ("csp_metros", TOUTES),
]

# None plutôt que TOUTES car sources diverses et parfois l'écriture est différente donc on garde leur liste propre 
METRO_KEYS_SOLID = [
    ("caf_agglos",         None),
    ("eff_metros",         None),
    ("sante_metros_multi", None),
    ("part_metros",        None),
]
METRO_KEYS_ENV = [
    ("env_air_metros",     TOUTES),
    ("env_verts_metros",   TOUTES),
    ("env_dechets_metros", TOUTES),
]

# Cette partie initialise la "sauveegarde" des filtre pour permettre à l'utilisateur que le filtre sélectionné resté sélectionné au clic suivant
if "shared_metros_demo" not in st.session_state:
    st.session_state.shared_metros_demo = list(TOUTES)
if "shared_metros_solid" not in st.session_state:
    st.session_state.shared_metros_solid = list(TOUTES)
if "shared_metros_env" not in st.session_state:
    st.session_state.shared_metros_env = list(TOUTES)

# C'est le cerveau de la synchronisation. Lorsqu'un utilisateur modifie les métropoles dans un graphique, cette fonction récupère ce nouveau choix, 
# le sauvegarde dans la mémoire globale centrale (shared_key), puis parcourt tous les autres graphiques de la thématique pour forcer leurs filtres à s'aligner instantanément.
def _propagate(key, widget_keys, shared_key):
    new_val = list(st.session_state[key])
    st.session_state[shared_key] = new_val
    for wkey, options in widget_keys:
        if wkey == key:
            continue
        if options is not None:
            filtered = [m for m in new_val if m in options]
            st.session_state[wkey] = filtered if filtered else list(options)
        else:
            st.session_state[wkey] = new_val

# Ce sont les interrupteurs branchés sur le paramètre on_change= de vos menus déroulants (st.multiselect).
# Dès qu'un utilisateur clique sur un filtre, la fonction de la thématique correspondante se réveille et ordonne à _propagate de lancer la synchronisation avec la bonne liste de widgets.
def sync_metros_demo(key):
    _propagate(key, METRO_KEYS_DEMO, "shared_metros_demo")

def sync_metros_solid(key):
    _propagate(key, METRO_KEYS_SOLID, "shared_metros_solid")

def sync_metros_env(key):
    _propagate(key, METRO_KEYS_ENV, "shared_metros_env")

# Elles servent à définir ce que le menu déroulant doit afficher par défaut à l'écran (default=...).
# Au lieu de recocher bêtement toutes les métropoles à chaque fois, elles vont lire la mémoire globale pour pré-remplir le filtre avec la toute dernière sélection de l'utilisateur, garantissant ainsi que l'affichage reste identique d'un onglet à l'autre.
def shared_default_demo(options):
    current = st.session_state.get("shared_metros_demo", list(TOUTES))
    filtered = [m for m in current if m in options]
    return filtered if filtered else list(options)

def shared_default_solid(options):
    current = st.session_state.get("shared_metros_solid", list(TOUTES))
    filtered = [m for m in current if m in options]
    return filtered if filtered else list(options)

def shared_default_env(options):
    current = st.session_state.get("shared_metros_env", list(TOUTES))
    filtered = [m for m in current if m in options]
    return filtered if filtered else list(options)

# Sélection partagée des COMMUNES entre onglets
COMMUNES_GRENOBLE = sorted(COMMUNES["Grenoble"])

# Même principe que pour les métropoles
COMMUNE_KEYS_DEMO = [
    ("pop_communes", COMMUNES_GRENOBLE),
    ("age_communes", COMMUNES_GRENOBLE),
    ("mob_communes", COMMUNES_GRENOBLE),
    ("transp_communes", COMMUNES_GRENOBLE),
    ("men_communes", COMMUNES_GRENOBLE),
    ("log_communes", COMMUNES_GRENOBLE),
    ("csp_communes", COMMUNES_GRENOBLE),
]
COMMUNE_KEYS_SOLID = [
    ("caf_communes",      None),
    ("eff_communes",      None),
    ("sante_communes_t1", None),
    ("part_communes",     None),
]
COMMUNE_KEYS_ENV = [
    ("env_air_communes",     COMMUNES_GRENOBLE),
    ("env_verts_communes",   COMMUNES_GRENOBLE),
    ("env_dechets_communes", COMMUNES_GRENOBLE),
]

_DEFAULT_COMMUNES = [
    c for c in [
        "Échirolles",
        "Saint-Martin-d'Hères",
        "Fontaine",
        "Meylan",
        "Grenoble",
    ]
    if c in COMMUNES_GRENOBLE
]

if "shared_communes_demo" not in st.session_state:
    st.session_state.shared_communes_demo = _DEFAULT_COMMUNES[:]
if "shared_communes_solid" not in st.session_state:
    st.session_state.shared_communes_solid = _DEFAULT_COMMUNES[:]
if "shared_communes_env" not in st.session_state:
    st.session_state.shared_communes_env = _DEFAULT_COMMUNES[:]

def _propagate_communes(key, widget_keys, shared_key):
    new_val = list(st.session_state[key])
    st.session_state[shared_key] = new_val
    for wkey, options in widget_keys:
        if wkey == key:
            continue
        if options is not None:
            filtered = [c for c in new_val if c in options]
            st.session_state[wkey] = filtered if filtered else list(options[:2])
        else:
            st.session_state[wkey] = new_val

def sync_communes_demo(key):
    _propagate_communes(key, COMMUNE_KEYS_DEMO, "shared_communes_demo")

def sync_communes_solid(key):
    raw_val = list(st.session_state[key])
    ref_val = [source_to_ref(v) for v in raw_val]
    st.session_state["shared_communes_solid"] = ref_val
    for wkey, _ in COMMUNE_KEYS_SOLID:
        if wkey == key:
            continue
        st.session_state[wkey] = ref_val

def sync_communes_env(key):
    _propagate_communes(key, COMMUNE_KEYS_ENV, "shared_communes_env")

def shared_default_communes_demo(options):
    current = st.session_state.get("shared_communes_demo", _DEFAULT_COMMUNES)
    filtered = [c for c in current if c in options]
    return filtered if filtered else list(options[:2])

def shared_default_communes_solid(options, widget_key=None):
    current_refs = st.session_state.get("shared_communes_solid", _DEFAULT_COMMUNES)
    normalized_current = [source_to_ref(v) for v in current_refs]
    result = refs_to_source_list(normalized_current, options)
    if not result:
        result = list(options[:5]) if len(options) >= 5 else list(options)
    if widget_key is not None:
        st.session_state[widget_key] = result
    return result

def shared_default_communes_env(options):
    current = st.session_state.get("shared_communes_env", _DEFAULT_COMMUNES)
    filtered = [c for c in current if c in options]
    return filtered if filtered else list(options[:2])

# Définition des départements de nos métropoles nécessaire pour de bons chargements, code commune à 3 chiffres à concaténer avec le département parfois
DEP_MAP = {
    "Grenoble": "38", "Rennes": "35", "Rouen": "76",
    "Saint-Étienne": "42", "Montpellier": "34",
}

CSP_MAP_NEW = {
    "Agriculteurs": "Agriculteurs", "Artisans": "Artisans & Chefs",
    "Cadres": "Cadres & Prof. Sup.", "Professions intermédiaires": "Prof. Intermédiaires",
    "Employés": "Employés", "Ouvriers": "Ouvriers",
}

DIP_MAP = {
    "Aucun diplôme":                      "Sans diplôme",
    "de niveau CEP":                       "CEP",
    "de niveau BEPC":                      "BEPC",
    "de niveau CAP-BEP":                   "CAP-BEP",
    "de niveau bac":                       "Baccalauréat",
    "universitaire de 1er cycle":          "Bac+2",
    "universitaire de 2":                  "Bac+3 et +",
}

LABEL_TRANCHE = {
    "01":"0-4","02":"5-9","03":"10-14","04":"15-19","05":"20-24",
    "06":"25-29","07":"30-34","08":"35-39","09":"40-44","10":"45-49",
    "11":"50-54","12":"55-59","13":"60-64","14":"65-69","15":"70-74",
    "16":"75-79","17":"80-84","18":"85-89","19":"90-94","20":"95+",
}
TRANCHES_JEUNES  = ["01","02","03","04"]
TRANCHES_ACTIFS  = ["05","06","07","08","09","10","11","12","13"]
TRANCHES_SENIORS = ["14","15","16","17","18","19","20"]

# ──────────────────────────────────────────────────────────────────────────────
# 3. CHARGEMENT
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = Path("demographie/data_clean")

@st.cache_data
def charger_generales():
    p = DATA_DIR / "population" / "Donnees_generales_comparatives_clean.csv"
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def charger_pop_age():
    p = DATA_DIR / "population" / "Population_tranche_age_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["metropole"] = df["LIBELLE"].map(COMMUNE_VERS_METRO)
    return df

@st.cache_data
def charger_men_age():
    p = DATA_DIR / "menages" / "Menage_age_situation_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["metropole"] = df["LIBGEO"].map(COMMUNE_VERS_METRO)
    return df

@st.cache_data
def charger_men_csp():
    p = DATA_DIR / "menages" / "Menages_csp_nbpers_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["metropole"] = df["LIBGEO"].map(COMMUNE_VERS_METRO)
    return df

@st.cache_data
def charger_log():
    # 1. Utilisation du bon dossier et du bon nom de fichier pour le logement
    p = DATA_DIR / "logement" / "logements_metropoles_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    if "metropole" in df.columns:
        df["metropole"] = df["metropole"].replace("Saint-Etienne", "Saint-Étienne")
    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce").fillna(0).astype(int)
    return df

@st.cache_data
def charger_log_social():
    p = DATA_DIR / "logement" / "rpls_metropoles_clean.csv"

    if not p.exists():
        return None

    # Séparateur forcé : le fichier est un CSV standard (virgules),
    # ne JAMAIS utiliser sep=None ici (le sniffer peut échouer et
    # renvoyer une seule colonne contenant tout l'en-tête).
    df = pd.read_csv(p, sep=",", encoding="utf-8-sig")

    df.columns = df.columns.str.strip()

    if "metropole" in df.columns:
        df["metropole"] = df["metropole"].replace("Saint-Etienne", "Saint-Étienne")

    return df

@st.cache_data
def charger_mobilites():
    p_res  = DATA_DIR / "mobilite" / "Migrations_resid_clean.csv"
    p_prof = DATA_DIR / "mobilite" / "Mobilite_profess_clean.csv"
    p_scol = DATA_DIR / "mobilite" / "Mobilite_scolaire_clean.csv"

    def safe_load(p):
        if not p.exists():
            return None
        df = pd.read_csv(p)
        df["flux"] = pd.to_numeric(df.get("flux", 0), errors="coerce").fillna(0)
        return df

    return safe_load(p_res), safe_load(p_prof), safe_load(p_scol)

@st.cache_data
def charger_transport():
    p = DATA_DIR / "transport" / "transport_metropoles_clean.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p, sep=",", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    if "metropole" in df.columns:
        df["metropole"] = df["metropole"].replace("Saint-Etienne", "Saint-Étienne")
    return df

df_transport = charger_transport()

@st.cache_data
def charger_caf():
    paths = [
        Path("solidarite&citoyennete/data_clean/solidarite/CAF_5_Metropoles.csv"),
        Path("CAF_5_Metropoles.csv"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_csv(p, sep=";", low_memory=False)
            break
    if df is None:
        return None
    if "Date_Ref" in df.columns and "Annee" not in df.columns:
        df["Annee"] = pd.to_datetime(df["Date_Ref"], errors="coerce").dt.year
    return df

@st.cache_data
def charger_effectifs():
    paths = [
        Path("solidarite&citoyennete/data_clean/education/education_filtre.csv"),
        Path("education_filtre.csv"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_csv(p, low_memory=False)
            break
    if df is None:
        return None
    DEP_METRO = {
        "Isère":          "Grenoble",
        "Ille-et-Vilaine":"Rennes",
        "Seine-Maritime": "Rouen",
        "Loire":          "Saint-Étienne",
        "Hérault":        "Montpellier",
    }
    df["metropole"] = df["Libelle_departement"].map(DEP_METRO)
    df["Nombre_d_eleves"] = pd.to_numeric(df["Nombre_d_eleves"], errors="coerce").fillna(0)
    df["Nom_commune"] = df["Nom_commune"].str.replace("Saint-Etienne", "Saint-Étienne", regex=False)
    df["Statut_public_prive"] = df["Statut_public_prive"].astype(str).str.strip()
    return df

@st.cache_data
def charger_filo():
    paths = [
        Path("solidarite&citoyennete/data_clean/revenus&pauvrete/BASE_TD_FILO_IRIS_2021_DEC.xlsx"),
        Path("BASE_TD_FILO_IRIS_2021_DEC.xlsx"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_excel(p, sheet_name="IRIS_DEC", header=5)
            break
    if df is None:
        return None
    num_cols = [c for c in df.columns if c.startswith("DEC_")]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "."), errors="coerce")
    df["DEP"] = df["COM"].astype(str).str.zfill(5).str[:2]
    DEP_METRO = {"38": "Grenoble", "35": "Rennes", "76": "Rouen",
                 "42": "Saint-Étienne", "34": "Montpellier"}
    df["metropole"] = df["DEP"].map(DEP_METRO)
    df = df[df["metropole"].notna()].copy()
    return df


EAU_DIR = Path("environnement/data_clean/eau")
_METROS_EAU = {34: "Montpellier", 38: "Grenoble", 42: "Saint-Étienne", 76: "Rouen"}
_POP_COL    = "Pop de l'entité de gestion sans double compte"

@st.cache_data
def charger_artificialisation():
    paths = [
        Path("environnement/data_clean/artificialisation_des_sols_clean.csv"),
        Path("artificialisation_des_sols_clean.csv"),
    ]
    df = None
    for p in paths:
        if p.exists():
            df = pd.read_csv(p, sep=",", encoding="utf-8-sig")
            break
    if df is None:
        return None
 
    df.columns = df.columns.str.strip()
    df["nom"] = df["nom"].astype(str).str.strip()
 
    df["metropole"] = df["metropole"].replace("Saint-Etienne", "Saint-Étienne")
 
    # Conversions m² → hectares (plus lisibles à l'échelle communale)
    df["surface_artif_1_ha"] = df["surface_artif_1"] / 10_000
    df["surface_artif_2_ha"] = df["surface_artif_2"] / 10_000
    df["commune_surface_ha"] = df["commune_surface"] / 10_000
    df["flux_surface_ha"]    = df["flux_surface_1_2"] / 10_000
 
    # Durée de la période d'observation (différente selon la métropole :
    # 2018→2021 pour Grenoble et Montpellier, 2017→2020 pour Rennes, 2019→2022 pour
    # Saint-Étienne et Rouen, toujours 3 ans, mais pas calée sur les mêmes années).
    df["duree_periode"]    = (df["millesimes_2"] - df["millesimes_1"]).replace(0, np.nan)
    df["rythme_annuel_ha"] = df["flux_surface_ha"] / df["duree_periode"]
 
    return df

@st.cache_data
def charger_qualite_air():
    p = Path("environnement/data_clean/ind_atmo_clean.csv")
    if not p.exists():
        return None
    df = pd.read_csv(p, sep=",", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    if "metropole" in df.columns:
        df["metropole"] = df["metropole"].replace("Saint-Etienne", "Saint-Étienne")
    # Conversion de la date de prévision en objet date (tri chronologique, affichage)
    if "date_ech" in df.columns:
        df["date_ech"] = pd.to_datetime(df["date_ech"]).dt.date
    return df

def _agg_eau(df: pd.DataFrame, ind_cols: list[str]) -> pd.DataFrame:
    """
    Filtre sur les 4 métropoles, convertit les colonnes numériques,
    et agrège par métropole (moyenne pondérée par population desservie).
    Saint-Étienne ayant plusieurs entités de gestion, l'agrégation est nécessaire.
    """
    df = df[df["DPT du siège de la coll."].isin(_METROS_EAU.keys())].copy()
    df["metropole"] = df["DPT du siège de la coll."].map(_METROS_EAU)
    df[_POP_COL] = pd.to_numeric(df.get(_POP_COL, pd.Series(0, index=df.index)),
                                  errors="coerce").fillna(0)
    avail = [c for c in ind_cols if c in df.columns]
    for c in avail:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "."),
                               errors="coerce")
    rows = []
    for metro, grp in df.groupby("metropole"):
        row = {"metropole": metro, "population": int(grp[_POP_COL].sum())}
        for c in avail:
            valid = grp[[c, _POP_COL]].dropna(subset=[c])
            if len(valid) > 0 and valid[_POP_COL].sum() > 0:
                row[c] = (valid[c] * valid[_POP_COL]).sum() / valid[_POP_COL].sum()
            else:
                row[c] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)

@st.cache_data
def charger_eau():
    """
    Charge et agrège les 4 fichiers SISPEA 2020 pour les 4 métropoles disponibles.
    Retourne (df_aep, df_ac, df_anc, df_tar) ou None si fichier absent.
    """
    def safe(path, ind_cols):
        p = EAU_DIR / path
        if not p.exists():
            return None
        return _agg_eau(pd.read_csv(p), ind_cols)

    def safe_tar(path):
        p = EAU_DIR / path
        if not p.exists():
            return None
        df = pd.read_csv(p)
        df = df[df["DPT du siège de la coll."].isin(_METROS_EAU.keys())].copy()
        df["metropole"] = df["DPT du siège de la coll."].map(_METROS_EAU)
        # Convertir toutes les colonnes numériques (prix avec virgule décimale)
        for c in df.columns:
            if c not in ["metropole", "Nom collectivité",
                          "Nom de l'entité de gestion", "Type collectivité",
                          "Statut", "Mode de gestion"]:
                df[c] = pd.to_numeric(
                    df[c].astype(str).str.replace(",", "."), errors="coerce"
                )
        return df

    # ── Eau potable ──────────────────────────────────────────────────────────
    IND_AEP = [
        "D101.0",   # Abonnés desservis
        "D102.0",   # Prix TTC eau potable à 120 m³ (€/m³)
        "P103.2B",  # Conformité eau distribuée (% analyses conformes)
        "P105.3",   # Pertes en réseau (m³/km/j)
        "P108.3",   # Protection ressource : captages avec arrêté (%)
        "P152.1",   # Taux de conformité microbiologique (%)
        "VP.056",   # Volume mis en distribution (m³/an)
        "VP.020",   # Rendement réseau (%)
    ]
    df_aep = safe("Eau_potable_2020-Entites_de_gestion.csv", IND_AEP)

    # ── Assainissement collectif ──────────────────────────────────────────────
    IND_AC = [
        "D201.0",   # Abonnés assainissement collectif
        "D202.0",   # Charge en DBO5 traitée (kg/j)
        "P203.3",   # Taux de collecte des effluents (%)
        "P204.3",   # Conformité des équipements d'épuration (%)
        "P205.3",   # Conformité de la performance d'épuration (%)
        "P206.3",   # Conformité des boues (%)
        "P255.3",   # Taux de dépollution (% DBO5 éliminée)
        "VP.268",   # Volume traité en station (m³/an)
    ]
    df_ac = safe("Assainissement_collectif_2020-Entites_de_gestion.csv", IND_AC)

    # ── Assainissement non collectif ─────────────────────────────────────────
    IND_ANC = [
        "D301.0",   # Nb installations ANC recensées
        "D302.0",   # Taux de conformité des installations ANC (%)
        "P301.3",   # Taux de réhabilitation des installations ANC (%)
        "VP.181",   # Population desservie par l'ANC
        "VP.167",   # Nb installations contrôlées dans l'année
        "VP.166",   # Nb installations ANC recensées non conformes
    ]
    df_anc = safe("Assainissement_noncollectif_2020-Entites_de_gestion.csv", IND_ANC)

    # ── Tarif ────────────────────────────────────────────────────────────────
    df_tar = safe_tar("Tarif_eau_2020-Detail_tarifaire.csv")

    return df_aep, df_ac, df_anc, df_tar
    
# Supprime les accents, convertit le texte en minuscules et enlève les espaces en trop au début et à la fin.
# Cela évite que l'application ne plante ou ignore une catégorie à cause d'une majuscule ou d'un accent oublié.
# (ex: Ouvriers et ouvriers deviennent identiques).
def normalize_name(text):
    if pd.isna(text):
        return ""
    return (unicodedata.normalize("NFKD", str(text))
            .encode("ascii", "ignore").decode("utf-8").lower().strip())

normalize_csp_name = normalize_name

# Fait la même chose que la précédente, mais spécifiquement pour les noms de villes en remplaçant en plus les tirets (-) et les apostrophes (') par des espaces.
# Ainsi, Saint-Martin-d'Hères et saint martin d heres deviennent exactement la même chaîne de caractères, ce qui rend les comparaisons infaillibles.
def norm_commune(text):
    if pd.isna(text):
        return ""
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("utf-8")
    s = s.lower().replace("-", " ").replace("'", " ").replace("'", " ")
    return " ".join(s.split())

# C'est un dictionnaire de traduction. Il associe la version ultra-simplifiée (sans accent, sans tiret) d'une commune de Grenoble à son orthographe officielle exacte.
# (ex: {echirolles: Échirolles}).
_NORM_TO_REF = {norm_commune(c): c for c in COMMUNES["Grenoble"]}

# Reçoit un nom de commune brute d'un fichier, le simplifie, et l'utilise pour récupérer son orthographe officielle propre grâce au dictionnaire
def source_to_ref(name):
    return _NORM_TO_REF.get(norm_commune(name), name)

# Fait le chemin inverse. Il prend un nom officiel propre (ex: Échirolles) et cherche comment il est écrit dans une liste d'options provenant d'un autre fichier (qui écrit peut-être ECHIROLLES en majuscules).
def ref_to_source(ref_name, source_options):
    norm_ref = norm_commune(ref_name)
    for opt in source_options:
        if norm_commune(opt) == norm_ref:
            return opt
    return None

# Fait exactement la même chose que ref_to_source, mais pour toute une liste de communes en même temps. 
# C'est indispensable pour synchroniser nos filtres multi-sélection entre des onglets qui n'utilisent pas la même source de données.
def refs_to_source_list(ref_names, source_options):
    result = []
    for r in ref_names:
        match = ref_to_source(r, source_options)
        if match is not None:
            result.append(match)
    return result

# C'est une fonction ultra-puissante pour charger et fusionner nos fichiers (CSV ou Excel) sur plusieurs années.
# Elle lit automatiquement le bon format (Excel ou CSV).
# Elle supprime les lignes de commentaires inutiles de l'INSEE (comme les lignes contenant RR).
# Elle cherche et détecte toute seule les colonnes de Département et de Libellé, peu importe comment elles sont nommées dans le fichier original (DEP, DEPARTEMENT, etc.).
# Elle applique notre dictionnaire de correspondance (mapping_dict) pour convertir les données en nombres, remplacer les cases vides par 0, et additionner automatiquement les colonnes si nécessaire, avant de tout fusionner en un seul tableau propre.

@st.cache_data
def load_generic_data(file_paths_dict, mapping_dict):
    all_data = []
    for year, path in file_paths_dict.items():
        p = Path(path)
        if not p.exists():
            continue
        try:
            df = pd.read_excel(p) if p.suffix.lower() in [".xlsx", ".xls"] else pd.read_csv(p, sep=None, engine="python", low_memory=False)
            if not df.empty and "RR" in str(df.iloc[0, 0]):
                df = df.drop(0).reset_index(drop=True)
            c_dep = [c for c in df.columns if any(x in str(c).upper() for x in ["DÉPARTEMENT", "DR24", "DEP"])][0]
            c_lib = [c for c in df.columns if any(x in str(c).upper() for x in ["LIBELLÉ", "LIBELLE"])][0]
            res = pd.DataFrame({
                "DEP": df[c_dep].astype(str).str.zfill(2),
                "NOM": df[c_lib].astype(str),
                "ANNEE": int(year),
                "LIB_NORM": df[c_lib].apply(normalize_name),
            })
            for raw, clean in mapping_dict.items():
                cols = [c for c in df.columns if raw.lower() in str(c).lower()]
                res[clean] = df[cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
            all_data.append(res)
        except Exception:
            continue
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# ── Chargement ───────────────────────────────────────────────────────────────
df_gen     = charger_generales()
df_pop     = charger_pop_age()
df_men_age = charger_men_age()
df_men_csp = charger_men_csp()
df_log     = charger_log()
df_social  = charger_log_social()
df_caf     = charger_caf()
df_eff     = charger_effectifs()
df_filo    = charger_filo()
df_res, df_prof, df_scol = charger_mobilites()
df_artif = charger_artificialisation()
df_air = charger_qualite_air()
df_aep_eau, df_ac_eau, df_anc_eau, df_tar_eau = charger_eau()

FILES_CSP = {
    2011: "demographie/data_clean/population_2554/Commune_2011_2554_sect_activite.xlsx",
    2016: "demographie/data_clean/population_2554/Commune_2016_2554_sect_activite.xlsx",
    2022: "demographie/data_clean/population_2554/Commune_2022_2554_sect_activite.xlsx",
}
FILES_DIP = {
    2011: "demographie/data_clean/population_2554/Commune_2011_2554_niveau_diplome.xlsx",
    2022: "demographie/data_clean/population_2554/Commune_2022_2554_niveau_diplome.xlsx",
}
df_csp_new = load_generic_data(FILES_CSP, CSP_MAP_NEW)
df_dip_new = load_generic_data(FILES_DIP, DIP_MAP)

# ──────────────────────────────────────────────────────────────────────────────
# 4. UTILITAIRES
# ──────────────────────────────────────────────────────────────────────────────

# Formate le format des valeurs numériques, N/D si vide ou pas de données ou un problème, si 1million : 1.0 M et ajoute un espace entre les milliers
def fmt(v, suffix="", dec=0):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/D"
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f} M{suffix}"
    if abs(v) >= 1_000:
        return f"{int(round(v)):,}{suffix}".replace(",", "\u202f")
    return f"{v:.{dec}f}{suffix}"

# Récupère la ligne complète du DataFrame df_gen correspondant à l'EPCI d'une métropole donnée (via le mapping NOM_EPCI). Retourne None si la métropole ou les données sont absentes.
def get_epci_row(metro):
    if df_gen is None or metro not in NOM_EPCI:
        return None
    rows = df_gen[df_gen["territoire"] == NOM_EPCI[metro]]
    return rows.iloc[0] if not rows.empty else None

# Variante ciblée de la précédente : retourne directement la valeur d'une seule colonne pour une métropole (ex: epci_val("Grenoble", "population_2022")).
def epci_val(metro, col):
    if df_gen is None:
        return np.nan
    nom = NOM_EPCI.get(metro)
    if not nom:
        return np.nan
    rows = df_gen[df_gen["territoire"] == nom]
    if rows.empty:
        return np.nan
    v = rows.iloc[0].get(col, np.nan)
    return float(v) if pd.notna(v) else np.nan

# Calcule la population totale d'une métropole pour une année donnée, en sommant toutes les colonnes de tranches d'âge
def pop_from_age(metro, annee):
    if df_pop is None:
        return np.nan
    dr = DR24_MAP.get(metro)
    sub = df_pop[(df_pop["DR24"] == dr) & (df_pop["annee"] == annee)]
    age_cols = [c for c in sub.columns if "ageq_rec" in c]
    if sub.empty or not age_cols:
        return np.nan
    return float(sub[age_cols].sum().sum())

# Renvoient la liste triée des colonnes "Hommes" (suffixe s1) ou "Femmes" (suffixe s2) parmi les colonnes de tranches d'âge.
def cols_h(df):
    return sorted([c for c in df.columns if "ageq_rec" in c and "s1" in c])

def cols_f(df):
    return sorted([c for c in df.columns if "ageq_rec" in c and "s2" in c])

# Extrait le code de tranche d'âge à 2 chiffres d'un nom de colonne (regex sur ageq_recXX) et le traduit en libellé lisible via LABEL_TRANCHE (ex: "20-24 ans").
def label_col(col):
    import re
    m = re.search(r"ageq_rec(\d{2})", col)
    return LABEL_TRANCHE.get(m.group(1), col) if m else col

# Additionne la population de plusieurs tranches d'âge (hommes + femmes) sur un sous-ensemble de données, avec filtre optionnel par année. Sert à calculer des agrégats comme "moins de 25 ans" ou "65 ans et plus".
def somme_tranches(df_src, tranches, annee=None):
    if annee is not None:
        df_src = df_src[df_src["annee"] == annee]
    total = 0
    for t in tranches:
        for sx in ["s1", "s2"]:
            col = f"ageq_rec{t}{sx}rpop2016"
            if col in df_src.columns:
                total += df_src[col].sum()
    return total

#  Applique l'habillage graphique standard à toute figure Plotly : thème clair, fonds transparents, police "Sora", marges harmonisées.
def style(fig, marge_t=20):
    fig.update_layout(template="plotly_white", plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                      margin=dict(t=marge_t, b=20, l=10, r=10))
    return fig

# Fonction pour avoir des hachures sur la métropole de Grenoble (hachures parfois faites sans cette fonction).
def apply_grenoble_hatch(fig, grenoble_key="Grenoble", active=True):
    """Ajoute des hachures rouges (/) sur les barres Grenoble - uniquement si active=True."""
    if not active:
        return fig
    for trace in fig.data:
        if not hasattr(trace, 'type') or trace.type != "bar":
            continue
        if grenoble_key in str(trace.name):
            trace.marker.pattern = dict(shape="/", fgcolor="#FF584D", size=20, solidity=0.3)
        elif trace.orientation == "h" and trace.y is not None:
            shapes = ["/" if grenoble_key in str(v) else "" for v in trace.y]
            if "/" in shapes:
                trace.marker.pattern = dict(shape=shapes, fgcolor="#FF584D", size=20, solidity=0.3)
        elif trace.x is not None:
            shapes = ["/" if grenoble_key in str(v) else "" for v in trace.x]
            if "/" in shapes:
                trace.marker.pattern = dict(shape=shapes, fgcolor="#FF584D", size=20, solidity=0.3)
    return fig

# Deux helpers d'affichage pour le bandeau de filtres : le premier affiche le titre de section ("Filtres - Population globale"...), le second affiche un label de ligne stylé (ex: "Niveau géographique").
def filter_bar(label="Filtres"):
    st.markdown(f'<div class="filter-bar-title">{label}</div>', unsafe_allow_html=True)

def filter_row_label(text):
    st.markdown(
        f"<div style='padding-top:8px; font-weight:600; font-size:14px; color:#1C3A27;'>{text}</div>",
        unsafe_allow_html=True,
    )

# Carte KPI générique avec bordure gauche colorée, utilisée comme alternative compacte aux cartes HTML que nous reconstruisons à la main dans chaque onglet (render_kpi_card_log, render_kpi_card_social...). Celle-ci n'a qu'une seule métrique (pas de grille 2×2), donc plus adaptée à des KPI simples.
def kpi_card_left(title, value, subtitle="", accent="#1a7a4a"):
    st.markdown(f"""
    <div style='
        display: flex;
        flex-direction: row;
        align-items: stretch;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background: #fff;
        min-height: 80px;
        border-left: 6px solid {accent};
    '>
        <div style='padding: 10px 16px; display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size:11px; font-weight:700; letter-spacing:0.08em; color:#666; text-transform:uppercase;'>{title}</div>
            <div style='font-size:24px; font-weight:bold; color:#111;'>{value}</div>
            <div style='color:#1a7a4a; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;'>{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 5. EN-TÊTE
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#1C3A27;font-size:2rem;margin-bottom:2px'>Observatoire de la métropole de Grenoble : Profils internes et rayonnement métropolitain</h1>"
    "<p style='color:#5A8A6A;margin-bottom:20px'>Analyses intercommunales et intermétropoles</p>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# 6. PAGE D'ACCUEIL
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown("""
    <style>
    .hero-accueil {
        background: linear-gradient(135deg, #1C3A27 0%, #2D6A4F 60%, #40916C 100%);
        border-radius: 16px; padding: 0; overflow: hidden;
        margin-bottom: 28px; position: relative;
    }
    .hero-inner {
        display: flex; align-items: stretch; min-height: 220px;
    }
    .hero-img-col {
        flex: 1; min-width: 0; position: relative; overflow: hidden;
    }
    .hero-img-col img {
        width: 100%; height: 100%; object-fit: cover;
        object-position: center; filter: saturate(0.75) brightness(0.85);
        display: block;
    }
    .hero-img-overlay {
        position: absolute; inset: 0;
        background: linear-gradient(to right, #1C3A27 0%, rgba(28,58,39,0) 100%);
    }
    .hero-text-col {
        flex: 0 0 420px; padding: 36px 36px 36px 40px;
        display: flex; flex-direction: column; justify-content: center;
        position: relative; z-index: 2;
    }
    .hero-badge {
        display: inline-block; background: rgba(149,213,178,0.2);
        color: #95D5B2; font-size: 11px; font-weight: 700;
        letter-spacing: 0.1em; text-transform: uppercase;
        padding: 4px 14px; border-radius: 20px;
        border: 1px solid rgba(149,213,178,0.35); margin-bottom: 14px; width: fit-content;
    }
    .hero-title {
        font-size: 28px; font-weight: 700; color: #fff; line-height: 1.25; margin-bottom: 10px;
    }
    .hero-subtitle { font-size: 13px; color: #95D5B2; font-weight: 400; line-height: 1.6; }

    .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
    .stat-box {
        background: #F0F7F3; border: 1px solid #C8E6D4; border-radius: 10px;
        padding: 14px 10px; text-align: center;
    }
    .stat-num { font-size: 24px; font-weight: 700; color: #1C3A27; }
    .stat-lbl { font-size: 11px; color: #4A7C59; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; }

    .cards-grid-bottom { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 16px; }
    
    .info-card {
        background: white; border: 1px solid #C8E6D4; border-radius: 12px;
        padding: 22px; border-left: 5px solid #2D6A4F;
    }
    
    .info-card.blue { 
        border-left: 6px solid #111184; 
        border-color: #111184;
        box-shadow: 0 4px 12px rgba(42, 92, 154, 0.08);
    }
    .info-card.blue .info-card-title { color: #111184; font-size: 14px; }
    .info-card.blue .info-card-body { 
        font-size: 16px;
        font-weight: 400;
        line-height: 1.6;
        color: #1a1a1a;
    }

    .info-card.orange { border-left-color: #C45B2A; }
    .info-card.darkgreen { border-left-color: #1B5E20; }
    
    .info-card-title {
        font-size: 12px; font-weight: 700; color: #2D6A4F; text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 12px;
    }
    .info-card.orange .info-card-title { color: #C45B2A; }
    .info-card.darkgreen .info-card-title { color: #1B5E20; }
    
    .info-card-body { font-size: 13px; color: #2c2c2c; line-height: 1.7; text-align: justify; }
    
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
    .tag-green {
        font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px;
        background: #EEF4F0; color: #2D6A4F; border: 1px solid #C8E6D4;
    }
    .tag-orange {
        font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px;
        background: #FEF3ED; color: #C45B2A; border: 1px solid #F5C4B3;
    }
    .tag-darkgreen {
        font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px;
        background: #E8F5E9; color: #1B5E20; border: 1px solid #C8E6D4;
    }
    
    .cta-wrapper { margin-top: 20px; }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #2D6A4F !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        padding: 14px 28px !important; font-size: 15px !important;
        font-weight: 700 !important; width: 100% !important;
        transition: background 0.2s !important;
    }
    </style>
    """, unsafe_allow_html=True)

    img_path = Path("grenoble-1600x900.jpg")
    img_col_html = ""
    if img_path.exists():
        import base64
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_col_html = f'<div class="hero-img-col"><img src="data:image/jpeg;base64,{img_b64}"/><div class="hero-img-overlay"></div></div>'

    st.markdown(f"""
    <div class="hero-accueil">
        <div class="hero-inner">
            <div class="hero-text-col">
                <div class="hero-badge">Outil d'aide à la décision</div>
                <div class="hero-title">Différentes dynamiques<br>et enjeux territoriaux</div>
                <div class="hero-subtitle">
                    Grenoble · Rennes · Rouen<br>Saint-Étienne · Montpellier
                </div>
            </div>
            {img_col_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-row">
        <div class="stat-box"><div class="stat-num">5</div><div class="stat-lbl">Métropoles</div></div>
        <div class="stat-box"><div class="stat-num">49</div><div class="stat-lbl">Communes</div></div>
        <div class="stat-box"><div class="stat-num">3</div><div class="stat-lbl">Thématiques</div></div>
        <div class="stat-box"><div class="stat-num">En cours</div><div class="stat-lbl">Environnement</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card blue">
        <div class="info-card-title"> Objectif</div>
        <div class="info-card-body">
            Analyser les données de démographie, de solidarité & citoyenneté ainsi que d'environnement afin de produire une analyse complète pour chaque Commune de Grenoble-Alpes Métropole. 
            Cette étude vise à permettre la comparaison des communes entre elles, ainsi qu'à situer la métropole de Grenoble par rapport à celles de Rouen, Saint-Étienne, Rennes et Montpellier (métropoles relativement comparables en termes de population, de superficie et de densité). 
            Elle est également destinée à accompagner les nouveaux élus dans la compréhension des dynamiques territoriales.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cards-grid-bottom">
        <div class="info-card">
            <div class="info-card-title"> Démographie</div>
            <div class="info-card-body">
                Analyse de la population, de la structure par âge, des ménage, des logements, des transports, des mobilités résidentielles, professionnelles et scolaires.
            </div>
            <div class="tag-row">
                <span class="tag-green">Population</span>
                <span class="tag-green">Âges</span>
                <span class="tag-green">Mobilités</span>
                <span class="tag-green">Transports</span>
                <span class="tag-green">Ménages</span>
                <span class="tag-green">Logements</span>
                <span class="tag-green">Actifs</span>
            </div>
        </div>
        <div class="info-card orange">
            <div class="info-card-title"> Solidarité & citoyenneté</div>
            <div class="info-card-body">
                Étude des allocations CAF, des indicateurs éducatifs et de santé, ainsi que de la participation citoyenne.
            </div>
            <div class="tag-row">
                <span class="tag-orange">Solidarité</span>
                <span class="tag-orange">Education</span>
                <span class="tag-orange">Santé</span>
                <span class="tag-orange">Participation</span>
            </div>
        </div>
        <div class="info-card darkgreen">
            <div class="info-card-title"> Environnement & Transition</div>
            <div class="info-card-body">
                Suivi de la qualité de l'air, de la présence de la biodiversité, des espaces verts et de la gestion locale des déchets.
            </div>
            <div class="tag-row">
                <span class="tag-darkgreen">Qualité de l'air</span>
                <span class="tag-darkgreen">Espaces Verts</span>
                <span class="tag-darkgreen">Déchets</span>
                <span class="tag-darkgreen">Transition</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cta-wrapper">', unsafe_allow_html=True)
    if st.button("→   Accéder à l'application", type="primary"):
        st.session_state.page = "app"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 7. SIDEBAR + NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #1B4332 !important;
        }
        div[data-testid="stRadio"] > div {
            gap: 8px;
        }
        div[data-testid="stRadio"] label {
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 12px 16px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            transition: all 0.3s ease-in-out !important;
            cursor: pointer !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #FFFFFF !important;
            transform: translateX(5px) !important;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.2) !important;
            border: 1px solid #95D5B2 !important;
        }
        div[data-testid="stRadio"] label p {
            color: #1B4332 !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin: 0 !important;
        }
        div[data-testid="stRadio"] input:checked + div label {
            background-color: #95D5B2 !important;
            border: 1px solid #FFFFFF !important;
        }
        .nav-header {
            font-size: 11px;
            font-weight: 800;
            color: #95D5B2;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            padding: 20px 0 10px 5px;
            font-family: 'Sora', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:10px 8px 20px 8px;border-bottom:1px solid rgba(149,213,178,0.2);">
        <div style="width:38px;height:38px;background:#2D6A4F;border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="#95D5B2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 22V12h6v10" stroke="#95D5B2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div>
            <div style="font-size:14px;font-weight:700;color:#FFFFFF;line-height:1.2;">Métropole Grenoble</div>
            <div style="font-size:10px;color:#95D5B2;opacity:0.8;">Tableau de bord interactif</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("Retour à l'Accueil", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    st.markdown('<div class="nav-header">Menu Principal</div>', unsafe_allow_html=True)
    
    vue = st.radio(
        "Navigation",
        ["Description", "Démographie", "Solidarité et citoyenneté", "Environnement"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <div style="font-size:12px; font-weight:600; color:#95D5B2;">Grenoble-Alpes Métropole</div>
        <div style="font-size:10px; color:rgba(255,255,255,0.4); margin-top:10px;">
            Équipe Projet :<br>
            S. Dufaud  • J. Ben-Hadj-Salem <br>
            H. Unaldi • M. Desjobert--Mutelet
        </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 8. PAGES
# ──────────────────────────────────────────────────────────────────────────────

# ==============================================================================
# PAGE DESCRIPTION
# ==============================================================================
if vue == "Description":
    st.markdown("""
        <style>
        .main-intro {
            background: white;
            padding: 25px;
            border-radius: 15px;
            border-left: 8px solid #2D6A4F;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }
        .modern-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 1em;
            font-family: 'Sora', sans-serif;
            border-radius: 12px 12px 0 0;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        .modern-table thead tr {
            background-color: #2D6A4F;
            color: #ffffff;
            text-align: left;
            font-weight: bold;
        }
        .modern-table th, .modern-table td {
            padding: 12px 15px;
        }
        .modern-table tbody tr {
            border-bottom: 1px solid #dddddd;
            background-color: white;
        }
        .modern-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        .modern-table tbody tr:last-of-type {
            border-bottom: 2px solid #2D6A4F;
        }
        .badge-count {
            background-color: #e7f3ef;
            color: #2D6A4F;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
        }
        .feature-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #E0E0E0;
            height: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="main-intro">
            <p style="font-size: 1.1rem; color: #1C3A27; margin: 0;">
                Cette application presents des analyses comparatives sur <b>5 métropoles françaises et 49 communes de la métropole de Grenoble</b> à partir des données de l'INSEE, la CAF, Data.gouv et OSM France. 
                Chaque page dispose de ses propres filtres en haut de page, adaptés aux données présentées. 
                Selon les onglets, il est possible de filtrer par métropole, par commune, par année ou par thématique.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#1C3A27; margin-bottom:10px;">Périmètre d\'analyse</p>', unsafe_allow_html=True)
    
    table_html = """
    <table class="modern-table">
        <thead>
            <tr>
                <th>Métropole</th>
                <th>Nombre de communes</th>
                <th>Département</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Grenoble-Alpes Métropole</td><td><span class="badge-count">49</span></td><td>Isère (38)</td></tr>
            <tr><td>Rennes Métropole</td><td><span class="badge-count">43</span></td><td>Ille-et-Vilaine (35)</td></tr>
            <tr><td>Rouen Normandie Métropole</td><td><span class="badge-count">71</span></td><td>Seine-Maritime (76)</td></tr>
            <tr><td>Saint-Étienne Métropole</td><td><span class="badge-count">53</span></td><td>Loire (42)</td></tr>
            <tr><td>Montpellier Méditerranée Métropole</td><td><span class="badge-count">31</span></td><td>Hérault (34)</td></tr>
        </tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#2D6A4F; border-bottom: 2px solid #2D6A4F;"> Thématique 1 : Démographie</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Population</div><div class="card-title"><b> Population globale</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Découvrez ici le nombre total d'habitants. Cela permet de voir la densité de population et de comparer les métropoles et communes entre elles.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Foyers</div><div class="card-title"><b> Ménages</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">On regarde ici comment vivent les gens chez eux. Cela montre s'il y a beaucoup de familles ou de personnes seules, et combien il y a d'habitants par logement.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Transports</div><div class="card-title"><b> Transport domicile-travail</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">On observe ici les déplacements domicile-travail des actifs (15 ans ou plus). Cela permet de comprendre où les habitants travaillent et quels moyens de transport ils utilisent pour se rendre à leur emploi.</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Âges</div><div class="card-title"><b> Structure par âge</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Est-ce que la ville est plutôt jeune ou vieille ? Cette partie montre le nombre d'enfants, de travailleurs et de retraités pour chaque endroit étudié.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Travail</div><div class="card-title"><b> Population active</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Ici, on s’intéresse aux 25-54 ans en activité. On analyse leurs métiers et leur niveau d'études ou leurs diplômes.</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Mobilités</div><div class="card-title"><b> Mobilités</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;"><b>Toutes les mobilités :</b> On étudie les déplacements des habitants. Cela comprend les nouveaux arrivants, les trajets domicile-travail et les déplacements pour l'école.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-demo">Habitation</div><div class="card-title"><b>Logement</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Cette section fournit une vue d’ensemble de l’occupation des résidences principales et des principaux indicateurs liés aux logements sociaux.</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#C45B2A; border-bottom: 2px solid #C45B2A;"> Thématique 2 : Solidarité & Citoyenneté</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Aide</div><div class="card-title"><b> Solidarité</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Retrouvez ici les aides versées aux familles par la CAF. Cela permet de voir les zones où les gens ont le plus besoin de soutien financier.</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Vote</div><div class="card-title"><b> Participation</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">On regarde ici si les habitants votent beaucoup aux élections locales. C'est un bon moyen de voir si les gens s'intéressent à la vie de leur commune.</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">École</div><div class="card-title"><b> Éducation</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Analyse des établissements du premier et du second degré, publics et privés, afin d’observer leur répartition et leurs caractéristiques.</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-solid">Soin</div><div class="card-title"><b> Santé</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Cette page liste les établissements de santés disponibles. Cela sert à voir si l'on peut se soigner facilement près de chez soi dans chaque quartier.</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:1.5rem; font-weight:700; color:#1B5E20; border-bottom: 2px solid #1B5E20;"> Thématique 3 : Environnement & Transition</p>', unsafe_allow_html=True)
    
    env1, env2, env3 = st.columns(3)
    with env1:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-env">Air</div><div class="card-title"><b> Qualité de l'air</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Suivi des indices de pollution atmosphérique.</div></div>""", unsafe_allow_html=True)
    with env2:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-env">Nature</div><div class="card-title"><b> Espaces verts & Biodiversité</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Analyse</div></div>""", unsafe_allow_html=True)
    with env3:
        st.markdown("""<div class="feature-card"><div class="theme-badge badge-env">Transition</div><div class="card-title"><b> Déchets & Énergie</b></div>
        <div class="card-body" style="font-size:0.9rem; color:#555;">Analyse.</div></div>""", unsafe_allow_html=True)

    st.stop()   

# ==============================================================================
# PAGE DÉMOGRAPHIE
# ==============================================================================

if vue == "Démographie":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏙️   Population globale",
        "👥   Structure par âge",
        "🚌   Mobilités",
        "🚆   Transports",
        "🏠   Ménages",
        "🏢   Logements",
        "📊   Population active 25-54 ans",
    ])

# ==============================================================================
# ONGLET 1 - POPULATION GLOBALE
# ==============================================================================
if vue == "Démographie":
    with tab1:
        st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> INSEE -
                <a href='https://www.insee.fr/fr/statistiques/1405599?geo=EPCI-200040715+EPCI-243500139' target='_blank' style='color: #1C3A27;'>Accéder aux données</a>
            </div>""", unsafe_allow_html=True)

        def commune_val(commune, col):
            if df_gen is None:
                return np.nan
            comm_norm = normalize_name(commune)
            geo = df_gen["territoire"].astype(str).str.extract(
                r"^(Commune|EPCI)\s*:\s*(.*?)\s*\(\d+\)\s*$"
            )
            mask = (geo[0] == "Commune") & (geo[1].apply(normalize_name) == comm_norm)
            rows = df_gen[mask]
            if rows.empty:
                return np.nan
            v = rows.iloc[0].get(col, np.nan)
            return float(v) if pd.notna(v) else np.nan

        with st.container():
            filter_bar("Filtres - Population globale")
            col_geo_label, col_geo_options = st.columns([1, 3])
            with col_geo_label:
                filter_row_label("Niveau géographique")
            with col_geo_options:
                mode_pop = st.radio(
                    "",
                    ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                    key="pop_mode", horizontal=True, label_visibility="collapsed"
                )
            if mode_pop == "Comparaison Métropoles":
                sel = st.multiselect("Métropoles à comparer", TOUTES, default=shared_default_demo(TOUTES), key="sel_t1", on_change=sync_metros_demo, args=("sel_t1",))
            else:
                sel_communes_pop = st.multiselect(
                    "Communes de Grenoble-Alpes Métropole", sorted(COMMUNES["Grenoble"]),
                    default=shared_default_communes_demo(sorted(COMMUNES["Grenoble"])), key="pop_communes",
                    on_change=sync_communes_demo, args=("pop_communes",),
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

        # ════════════════════════════════════════════════════════════════════
        # VUE COMMUNES
        # ════════════════════════════════════════════════════════════════════
        if mode_pop == "Comparaison communes Grenoble-Alpes Métropole":
            if not sel_communes_pop:
                st.warning("Sélectionnez au moins une commune.")
                st.stop()

            def commune_kpi_color(i, n):
                pal = PALETTE_COMMUNE
                idx = int(i / max(n - 1, 1) * (len(pal) - 1))
                return pal[idx]

            st.markdown("##### Population en 2022 - Echelle communale")
            kpi_cols = st.columns(len(sel_communes_pop))
            for i, comm in enumerate(sel_communes_pop):
                pop22  = commune_val(comm, "population_2022")
                tx_var = commune_val(comm, "tx_var_population_2016_2022")
                delta_str   = f"{tx_var:+.1f}%/an" if not np.isnan(tx_var) else "N/D"
                color_delta = "#2D6A4F" if not np.isnan(tx_var) and tx_var >= 0 else ("#C45B2A" if not np.isnan(tx_var) else "#888")
                kpi_color_c = commune_kpi_color(i, len(sel_communes_pop))
                html_card = f"""
                <div style='display:flex;flex-direction:column;justify-content:center;border-radius:8px;
                    overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;min-height:80px;
                    border-left:6px solid {kpi_color_c};padding:12px 16px;margin-bottom:10px;'>
                    <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{comm}</div>
                    <div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>{fmt(pop22)}</div>
                    <div style='font-size:12px;font-weight:700;'>
                        <span style='color:{color_delta};'>Var_2016_2022: {delta_str}</span>
                    </div>
                </div>"""
                with kpi_cols[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphiques 1 : Population & Densité ──────────────────────────
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader(
                    "Population des communes en 2022 (habitants)",
                    help="Nombre d'habitants recensés par l'INSEE au RP 2022. Permet de comparer directement le volume de population de chaque territoire sélectionné."
                )
                data_comm = [{"Commune": c, "Population": commune_val(c, "population_2022")}
                             for c in sel_communes_pop]
                df_comm22 = pd.DataFrame(data_comm).dropna(subset=["Population"]).sort_values("Population", ascending=False)
                if not df_comm22.empty:
                    fig_pop_c = px.bar(
                        df_comm22, x="Commune", y="Population",
                        color="Commune", color_discrete_sequence=PALETTE_COMMUNE, text="Population",
                    )
                    fig_pop_c.update_traces(
                        texttemplate="%{text:,.0f}", textposition="outside", showlegend=False,
                        hovertemplate="<b>Commune : %{x}</b><br>Population 2022 : %{y:,.0f}<extra></extra>",
                    )
                    fig_pop_c.update_layout(showlegend=False, xaxis_title="Echelle Communale",
                                            yaxis_title="Habitants", yaxis=dict(tickformat=",d"), height=500)
                    st.plotly_chart(style(fig_pop_c), use_container_width=True)

            with r1c2:
                st.subheader(
                    "Densité (hab/km²) vs Superficie (km²)",
                    help="Croise deux dimensions : la superficie du territoire (axe horizontal) et sa densité de population (axe vertical). La taille de la bulle est proportionnelle à la population totale. Un territoire en haut à gauche = petit mais très dense (profil urbain). Un territoire en bas à droite = grand mais peu peuplé (profil rural ou périurbain)."
                )
                data_dens_c = []
                for i, c in enumerate(sel_communes_pop):
                    d = commune_val(c, "densite_2022")
                    s = commune_val(c, "superficie_km2_2022")
                    p = commune_val(c, "population_2022")
                    if not any(np.isnan(v) for v in [d, s, p]):
                        data_dens_c.append({"Commune": c, "Densité (hab/km²)": d,
                                            "Superficie (km²)": s, "Population": p})
                df_dens_c = pd.DataFrame(data_dens_c)
                if not df_dens_c.empty:
                    fig_dens_c = px.scatter(df_dens_c, x="Superficie (km²)", y="Densité (hab/km²)",
                                            size="Population", color="Commune", text="Commune",
                                            color_discrete_sequence=PALETTE_COMMUNE, size_max=55, height=500)
                    fig_dens_c.update_traces(textposition="top center", textfont_size=10,
                                             hovertemplate="<b>Commune : %{text}</b><br>Superficie : %{x:.2f} km²<br>Densité : %{y:.2f} hab/km²<extra></extra>")
                    fig_dens_c.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_dens_c), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Population totale (barres)** : une barre plus haute signifie simplement plus d'habitants. "
                    "Ce graphique permet de situer l'échelle de chaque territoire et de dimensionner les besoins en services publics (écoles, transports, logements).\n\n"
                    "**Densité vs Superficie (nuage de points)** : la position verticale indique la pression démographique par km². "
                    "Un territoire dense et petit (en haut à gauche) a un profil urbain concentré. "
                    "Un territoire peu dense et grand (en bas à droite) a un profil périurbain ou rural. "
                    "La taille de la bulle permet de ne pas confondre densité et population totale : une commune peut être grande en superficie mais peu peuplée, et pourtant avoir une forte densité dans son centre."
                )

            st.markdown("---")

            # ── Graphiques 2 : Soldes ─────────────────────────────────────────
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader(
                    "Soldes naturel et migratoire (%/an, 2016-2022)",
                    help="Décompose la variation démographique en deux composantes annuelles moyennes sur 2016-2022 :\n• Solde naturel = (naissances − décès) / population\n• Solde migratoire = (arrivées − départs) / population\n• Variation totale = somme des deux\nUn solde positif = le territoire gagne des habitants par ce canal."
                )
                rows_comp_c = []
                for comm in sel_communes_pop:
                    sn  = commune_val(comm, "tx_solde_naturel")
                    sm  = commune_val(comm, "tx_solde_migratoire")
                    tot = commune_val(comm, "tx_var_population_2016_2022")
                    if not all(np.isnan(v) for v in [sn, sm, tot]):
                        rows_comp_c.append({"Commune": comm, "Solde naturel": sn,
                                            "Solde migratoire": sm, "Variation totale": tot})
                if rows_comp_c:
                    df_comp_c = pd.DataFrame(rows_comp_c).melt(
                        id_vars="Commune", var_name="Composante", value_name="Taux (%/an)"
                    ).dropna()
                    color_map = {
                        "Solde naturel": PALETTE_COMMUNE[0],
                        "Solde migratoire": PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.4)],
                        "Variation totale": PALETTE_COMMUNE[-3],
                    }
                    fig_comp_c = px.bar(df_comp_c, x="Commune", y="Taux (%/an)", color="Composante",
                                        barmode="group", color_discrete_map=color_map, height=500)
                    for trace in fig_comp_c.data:
                        trace.hovertemplate = "<b>Commune : %{x}</b><br>" + trace.name + " : %{y:.1f} %/an<extra></extra>"
                    fig_comp_c.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    fig_comp_c.update_layout(
                        xaxis_title="Echelle communale", yaxis_title="Taux (%/an)",
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        xaxis_tickangle=-20)
                    st.plotly_chart(style(fig_comp_c), use_container_width=True)
                else:
                    st.info("Données de soldes non disponibles pour ces communes.")

            with r2c2:
                st.subheader(
                    "Naissances & Décès en 2024 (pour 1 000 habitants)",
                    help="Compare les taux vitaux rapportés à 1 000 habitants :\n• Barres foncées = taux de natalité\n• Barres claires = taux de mortalité\n• Losange = accroissement naturel (naissances − décès)\nUn losange au-dessus de zéro indique que les naissances dépassent les décès sur ce territoire."
                )
                rows_vit_c = []
                for comm in sel_communes_pop:
                    nais = commune_val(comm, "naissances_2024")
                    decs = commune_val(comm, "deces_2024")
                    pop  = commune_val(comm, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]) and pop > 0:
                        rows_vit_c.append({"Commune": comm,
                                           "Naissances": round(nais / pop * 1000, 2),
                                           "Décès":      round(decs / pop * 1000, 2),
                                           "Accroissement": round((nais - decs) / pop * 1000, 2)})
                if rows_vit_c:
                    df_vit_c = pd.DataFrame(rows_vit_c)
                    comms_vit = df_vit_c["Commune"].tolist()
                    col_nais = PALETTE_COMMUNE[0]
                    col_decs = PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.4)]
                    col_accr = PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.7)]
                    fig_vit_c = go.Figure()
                    fig_vit_c.add_trace(go.Bar(
                        x=comms_vit, y=df_vit_c["Naissances"], name="Naissances / 1 000 hab",
                        marker_color=col_nais,
                        hovertemplate="<b>Commune : %{x}</b><br>Naissances : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit_c.add_trace(go.Bar(
                        x=comms_vit, y=df_vit_c["Décès"], name="Décès / 1 000 hab",
                        marker_color=col_decs,
                        hovertemplate="<b>Commune : %{x}</b><br>Décès : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit_c.add_trace(go.Scatter(
                        x=comms_vit, y=df_vit_c["Accroissement"], mode="markers+text",
                        name="Accroissement naturel",
                        marker=dict(symbol="diamond", size=12, color=col_accr, line=dict(color="white", width=1.5)),
                        text=[f"{v:+.2f}" for v in df_vit_c["Accroissement"]],
                        textposition="top center", textfont=dict(size=9, color="#1B4332"),
                        hovertemplate="<b>Commune : %{x}</b><br>Accroissement naturel : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit_c.update_layout(
                        barmode="group",
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        xaxis_title="Echelle communale", yaxis_title="Pour 1 000 habitants", height=500)
                    st.plotly_chart(style(fig_vit_c), use_container_width=True)
                else:
                    st.info("Données de naissances/décès non disponibles pour ces communes.")

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Soldes naturel et migratoire** : ce graphique montre d'où vient l'évolution de la population. "
                    "Le **solde naturel** compare les naissances et les décès. "
                    "Le **solde migratoire** montre si le territoire gagne ou perd des habitants.\n\n"
                    "**Naissances & Décès** : ce graphique compare les taux pour 1 000 habitants. "
                    "Au-dessus de 0, les naissances sont plus nombreuses que les décès. "
                    "Quand les décès dépassent les naissances, cela traduit un vieillissement de la population."
                )

            st.markdown("---")

            # ── Graphiques 3 : Niveau de vie ──────────────────────────────────
            r3c1, r3c2 = st.columns(2)
            with r3c1:
                st.subheader(
                    "Taux de chômage et taux de pauvreté (%)",
                    help="Le **taux de chômage** (15-64 ans) est la part des actifs sans emploi. Le **taux de pauvreté** est la part de la population dont le revenu est inférieur à 60% du revenu médian national. Ces deux indicateurs mesurent les fragilités sociales d'un territoire : un taux de chômage élevé pèse sur le revenu des ménages et fait mécaniquement augmenter le taux de pauvreté."
                )
                rows_social_c = []
                for comm in sel_communes_pop:
                    tc   = commune_val(comm, "tx_chomage_15_64")
                    pauv = commune_val(comm, "tx_pauvrete_2021")
                    rows_social_c.append({"Commune": comm,
                                          "Taux de chômage (%)": tc if not np.isnan(tc) else None,
                                          "Taux de pauvreté (%)": pauv if not np.isnan(pauv) else None})
                df_social_c = pd.DataFrame(rows_social_c)
                df_social_melt_c = df_social_c.melt(
                    id_vars="Commune", var_name="Indicateur", value_name="Taux (%)"
                ).dropna()

                if not df_social_melt_c.empty:
                    color_social_c = {
                        "Taux de chômage (%)": PALETTE_COMMUNE[0],
                        "Taux de pauvreté (%)": PALETTE_COMMUNE[int(len(PALETTE_COMMUNE) * 0.5)],
                    }
                    fig_social_c = px.bar(
                        df_social_melt_c, x="Commune", y="Taux (%)", color="Indicateur",
                        barmode="group", color_discrete_map=color_social_c,
                        text="Taux (%)", height=500,
                    )
                    fig_social_c.update_traces(
                        texttemplate="%{text:.1f}%", textposition="outside",
                        hovertemplate="<b>Commune : %{x}</b><br>%{fullData.name} : %{y:.1f}%<extra></extra>",
                    )
                    fig_social_c.update_layout(
                        xaxis_title="Echelle communale", yaxis_title="Taux (%)",
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        xaxis_tickangle=-20,
                    )
                    st.plotly_chart(style(fig_social_c), use_container_width=True)
                else:
                    st.info("Données sociales non disponibles pour ces communes.")

            with r3c2:
                st.subheader(
                    "Revenu médian vs Taux de pauvreté",
                    help="Chaque bulle représente une commune. L'axe horizontal indique le revenu médian annuel par unité de consommation (en €) ; l'axe vertical indique le taux de pauvreté (%). La taille de la bulle est proportionnelle à la population. On s'attend à une relation inverse : plus le revenu médian est élevé, plus le taux de pauvreté est faible. Un point qui s'écarte de cette tendance signale une situation atypique (ex : forte inégalité interne, population très hétérogène)."
                )
                data_rev_c = []
                for c in sel_communes_pop:
                    rev  = commune_val(c, "revenu_median_2021")
                    pauv = commune_val(c, "tx_pauvrete_2021")
                    pop  = commune_val(c, "population_2022")
                    if not any(np.isnan(v) for v in [rev, pauv, pop]):
                        data_rev_c.append({"Commune": c, "Revenu médian (€)": rev,
                                           "Taux de pauvreté (%)": pauv, "Population": pop})
                df_rev_c = pd.DataFrame(data_rev_c)
                if not df_rev_c.empty:
                    fig_rev_c = px.scatter(
                        df_rev_c, x="Revenu médian (€)", y="Taux de pauvreté (%)",
                        size="Population", color="Commune", text="Commune",
                        color_discrete_sequence=PALETTE_COMMUNE, size_max=55, height=500,
                    )
                    fig_rev_c.update_traces(
                        textposition="top center", textfont_size=10,
                        hovertemplate="<b>%{text}</b><br>Revenu médian : %{x:,.0f} €<br>Taux de pauvreté : %{y:.1f}%<br>Population : %{marker.size:,.0f}<extra></extra>",
                    )
                    fig_rev_c.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_rev_c), use_container_width=True)
                else:
                    st.info("Données de revenu non disponibles pour ces communes.")

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Taux de chômage et taux de pauvreté (barres groupées)** : comparer ces deux indicateurs côte à côte permet de distinguer les territoires en difficulté économique structurelle (chômage et pauvreté élevés simultanément) "
                    "de ceux où la pauvreté est présente malgré un faible chômage. \n\n"
                    "**Revenu médian vs Taux de pauvreté (nuage de points)** : ce graphique révèle la relation entre niveau de vie et précarité. "
                    "En règle générale, les deux indicateurs évoluent en sens inverse : plus le revenu médian est élevé, moins il y a de pauvreté. "
                    "Un territoire situé au-dessus de la tendance (pauvreté élevée malgré un revenu médian correct) présente souvent de fortes inégalités internes. "
                    "La taille des bulles permet de pondérer visuellement l'importance démographique de chaque commune dans l'analyse."
                )

            st.markdown("---")
            st.markdown("#### Tableau récapitulatif - indicateurs clés")
            lignes_tab_c = []
            for comm in sel_communes_pop:
                pop22 = commune_val(comm, "population_2022")
                dens  = commune_val(comm, "densite_2022")
                rev   = commune_val(comm, "revenu_median_2021")
                pauv  = commune_val(comm, "tx_pauvrete_2021")
                tc    = commune_val(comm, "tx_chomage_15_64")
                lignes_tab_c.append({"Commune": comm, "Population 2022": fmt(pop22),
                                     "Densité (hab/km²)": fmt(dens), "Revenu médian": fmt(rev, " €"),
                                     "Taux pauvreté": f"{pauv:.1f}%" if not np.isnan(pauv) else "N/D",
                                     "Taux chômage": f"{tc:.1f}%" if not np.isnan(tc) else "N/D"})
            st.dataframe(pd.DataFrame(lignes_tab_c).set_index("Commune"), use_container_width=True)

        # ════════════════════════════════════════════════════════════════════
        # VUE COMPARAISON MÉTROPOLES
        # ════════════════════════════════════════════════════════════════════
        else:
            if not sel:
                st.warning("Sélectionnez au moins une métropole.")
                st.stop()

            st.markdown("##### Population en 2022 - Echelle métropolitaine")
            kpi_cols = st.columns(len(sel))
            for i, m in enumerate(sel):
                pop22  = epci_val(m, "population_2022")
                tx_var = epci_val(m, "tx_var_population_2016_2022")
                delta_str   = f"{tx_var:+.1f}%/an" if not np.isnan(tx_var) else "N/D"
                color_delta = "#2D6A4F" if not np.isnan(tx_var) and tx_var >= 0 else ("#C45B2A" if not np.isnan(tx_var) else "#888")
                kpi_color = COULEURS.get(m, "#888888")
                html_card = f"""
                <div style='display:flex;flex-direction:column;justify-content:center;border-radius:8px;
                    overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;min-height:80px;
                    border-left:6px solid {kpi_color};padding:12px 16px;margin-bottom:10px;'>
                    <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{m}</div>
                    <div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>{fmt(pop22)}</div>
                    <div style='font-size:12px;font-weight:700;'>
                        <span style='color:{color_delta};'>Var_2016_2022: {delta_str}</span>
                    </div>
                </div>"""
                with kpi_cols[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphiques 1 : Population & Densité ──────────────────────────
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.subheader(
                    "Population des métropoles en 2022 (habitants)",
                    help="Nombre d'habitants recensés par l'INSEE au RP 2022. Permet de comparer directement le volume de population de chaque territoire sélectionné."
                )
                data_pop_df = [{"Métropole": m, "Population": epci_val(m, "population_2022")} for m in sel]
                df_pop22 = pd.DataFrame(data_pop_df).dropna().sort_values("Population", ascending=False)
                if not df_pop22.empty:
                    fig_pop = px.bar(df_pop22, x="Métropole", y="Population", color="Métropole",
                                     color_discrete_map=COULEURS, text="Population")
                    fig_pop.update_traces(
                        texttemplate="%{text:,.0f}", textposition="outside", showlegend=False,
                        hovertemplate="<b>Métropole : %{x}</b><br>Population 2022 : %{y:,.0f}<extra></extra>",
                    )
                    for trace in fig_pop.data:
                        if "Grenoble" in trace.name:
                            trace.marker.pattern.shape = "/"
                            trace.marker.pattern.fgcolor = "#FF584D"
                            trace.marker.pattern.size = 20
                            trace.marker.pattern.solidity = 0.20
                    fig_pop.update_layout(showlegend=False, xaxis_title="Echelle métropolitaine",
                                          yaxis_title="Habitants", yaxis=dict(tickformat=",d"), height=500)
                    st.plotly_chart(style(fig_pop), use_container_width=True)

            with r1c2:
                st.subheader(
                    "Densité (hab/km²) vs Superficie (km²)",
                    help="Croise deux dimensions : la superficie du territoire (axe horizontal) et sa densité de population (axe vertical). La taille de la bulle est proportionnelle à la population totale. Un territoire en haut à gauche = petit mais très dense (profil urbain). Un territoire en bas à droite = grand mais peu peuplé (profil rural ou périurbain)."
                )
                data_dens = []
                for m in sel:
                    d = epci_val(m, "densite_2022")
                    s = epci_val(m, "superficie_km2_2022")
                    p = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [d, s, p]):
                        data_dens.append({"Métropole": m, "Densité (hab/km²)": d,
                                          "Superficie (km²)": s, "Population": p})
                df_dens = pd.DataFrame(data_dens)
                if not df_dens.empty:
                    fig_dens = px.scatter(df_dens, x="Superficie (km²)", y="Densité (hab/km²)",
                                          size="Population", color="Métropole",
                                          color_discrete_map=COULEURS, text="Métropole",
                                          size_max=55, height=500)
                    fig_dens.update_traces(
                        textposition="top center", textfont_size=11,
                        hovertemplate="<b>Métropole : %{text}</b><br>Superficie : %{x:.2f} km²<br>Densité : %{y:.2f} hab/km²<extra></extra>",
                    )
                    for trace in fig_dens.data:
                        if "Grenoble" in trace.name:
                            trace.marker.line = dict(width=6, color="#FF584D")
                    fig_dens.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_dens), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Population totale (barres)** : une barre plus haute signifie simplement plus d'habitants. "
                    "Ce graphique permet de situer l'échelle de chaque territoire et de dimensionner les besoins en services publics (écoles, transports, logements).\n\n"
                    "**Densité vs Superficie (nuage de points)** : la position verticale indique la pression démographique par km². "
                    "Un territoire dense et petit (en haut à gauche) a un profil urbain concentré. "
                    "Un territoire peu dense et grand (en bas à droite) a un profil périurbain ou rural. "
                    "La taille de la bulle permet de ne pas confondre densité et population totale : une métropole peut être grande en superficie mais peu peuplée, et pourtant avoir une forte densité dans son centre."
                )

            st.markdown("---")

            # ── Graphiques 2 : Soldes ─────────────────────────────────────────
            r2c1, r2c2 = st.columns(2)
            with r2c1:
                st.subheader(
                    "Soldes naturel et migratoire (%/an, 2016-2022)",
                    help="Décompose la variation démographique en deux composantes annuelles moyennes sur 2016-2022 :\n• Solde naturel = (naissances − décès) / population\n• Solde migratoire = (arrivées − départs) / population\n• Variation totale = somme des deux\nUn solde positif = le territoire gagne des habitants par ce canal."
                )
                rows_comp = []
                for m in sel:
                    sn  = epci_val(m, "tx_solde_naturel")
                    sm  = epci_val(m, "tx_solde_migratoire")
                    tot = epci_val(m, "tx_var_population_2016_2022")
                    if not all(np.isnan(v) for v in [sn, sm, tot]):
                        rows_comp.append({"Métropole": m, "Solde naturel": sn,
                                          "Solde migratoire": sm, "Variation totale": tot})
                if rows_comp:
                    df_comp = pd.DataFrame(rows_comp).melt(
                        id_vars="Métropole", var_name="Composante", value_name="Taux (%/an)"
                    ).dropna()
                    n_comp_m = len(df_comp["Composante"].unique())
                    comp_colors_m = [PALETTE_METRO[int(i * (len(PALETTE_METRO)-1) / max(n_comp_m-1,1))]
                                     for i in range(n_comp_m)]
                    fig_comp = px.bar(df_comp, x="Métropole", y="Taux (%/an)", color="Composante",
                                      barmode="group", color_discrete_sequence=comp_colors_m, height=500)
                    for trace in fig_comp.data:
                        trace.hovertemplate = "<b>Métropole : %{x}</b><br>" + trace.name + " : %{y:.1f} %/an<extra></extra>"
                    fig_comp.add_hline(y=0, line_dash="dot", line_color="#AAAAAA")
                    metros_comp = list(dict.fromkeys(df_comp["Métropole"].tolist()))
                    if "Grenoble" in metros_comp:
                        g_pos = metros_comp.index("Grenoble")
                        fig_comp.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                           fillcolor="rgba(255,88,77,0.10)",
                                           line_color="#FF584D", line_width=1.5, line_dash="dash", layer="below")
                    fig_comp.update_layout(
                        xaxis_title="Echelle métropolitaine", yaxis_title="Taux (%/an)",
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
                    st.plotly_chart(style(fig_comp), use_container_width=True)

            with r2c2:
                st.subheader(
                    "Naissances & Décès en 2024 (pour 1 000 habitants)",
                    help="Compare les taux vitaux rapportés à 1 000 habitants :\n• Barres foncées = taux de natalité\n• Barres claires = taux de mortalité\n• Losange rouge = accroissement naturel (naissances − décès)\nUn losange au-dessus de zéro indique que les naissances dépassent les décès. La zone rouge identifie Grenoble."
                )
                rows_vit = []
                for m in sel:
                    nais = epci_val(m, "naissances_2024")
                    decs = epci_val(m, "deces_2024")
                    pop  = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [nais, decs, pop]):
                        rows_vit.append({"Métropole": m,
                                         "Naissances": round(nais / pop * 1000, 2),
                                         "Décès":      round(decs / pop * 1000, 2),
                                         "Accroissement": round((nais - decs) / pop * 1000, 2)})
                df_vit = pd.DataFrame(rows_vit)
                if not df_vit.empty:
                    metros_vit = df_vit["Métropole"].tolist()
                    col_nais_m = PALETTE_METRO[int(len(PALETTE_METRO) * 0.3)]
                    col_decs_m = PALETTE_METRO[int(len(PALETTE_METRO) * 0.7)]
                    fig_vit = go.Figure()
                    fig_vit.add_trace(go.Bar(
                        x=metros_vit, y=df_vit["Naissances"], name="Naissances / 1 000 hab",
                        marker_color=col_nais_m,
                        hovertemplate="<b>Métropole : %{x}</b><br>Naissances : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.add_trace(go.Bar(
                        x=metros_vit, y=df_vit["Décès"], name="Décès / 1 000 hab",
                        marker_color=col_decs_m,
                        hovertemplate="<b>Métropole : %{x}</b><br>Décès : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    fig_vit.add_trace(go.Scatter(
                        x=metros_vit, y=df_vit["Accroissement"], mode="markers+text",
                        name="Accroissement naturel",
                        marker=dict(symbol="diamond", size=12, color="#FF584D", line=dict(color="white", width=1.5)),
                        text=[f"{v:+.2f}" for v in df_vit["Accroissement"]],
                        textposition="top center", textfont=dict(size=9, color="#8B2E2E"),
                        hovertemplate="<b>Métropole : %{x}</b><br>Accroissement naturel : %{y:.2f} / 1 000 hab<extra></extra>",
                    ))
                    if "Grenoble" in metros_vit:
                        g_pos = metros_vit.index("Grenoble")
                        fig_vit.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                          fillcolor="rgba(255,88,77,0.10)",
                                          line_color="#FF584D", line_width=1.5, line_dash="dash", layer="below")
                    fig_vit.update_layout(
                        barmode="group",
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        xaxis_title="Echelle métropolitaine", yaxis_title="Pour 1 000 habitants", height=500)
                    st.plotly_chart(style(fig_vit), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Soldes naturel et migratoire** : ce graphique montre d'où vient l'évolution de la population. "
                    "Le **solde naturel** compare les naissances et les décès. "
                    "Le **solde migratoire** montre si le territoire gagne ou perd des habitants.\n\n"
                    "**Naissances & Décès** : ce graphique compare les taux pour 1 000 habitants. "
                    "Au-dessus de 0, les naissances sont plus nombreuses que les décès. "
                    "Quand les décès dépassent les naissances, cela traduit un vieillissement de la population."
                )

            st.markdown("---")

            # ── Graphiques 3 : Niveau de vie ──────────────────────────────────
            r3c1, r3c2 = st.columns(2)
            with r3c1:
                st.subheader(
                    "Taux de chômage et taux de pauvreté (%)",
                    help="Le **taux de chômage** (15-64 ans) est la part des actifs sans emploi. Le **taux de pauvreté** est la part de la population dont le revenu est inférieur à 60% du revenu médian national. Ces deux indicateurs mesurent les fragilités sociales d'un territoire : un taux de chômage élevé pèse sur le revenu des ménages et fait mécaniquement augmenter le taux de pauvreté."
                )
                rows_social = []
                for m in sel:
                    tc   = epci_val(m, "tx_chomage_15_64")
                    pauv = epci_val(m, "tx_pauvrete_2021")
                    rows_social.append({"Métropole": m,
                                        "Taux de chômage (%)": tc if not np.isnan(tc) else None,
                                        "Taux de pauvreté (%)": pauv if not np.isnan(pauv) else None})
                df_niveau_vie = pd.DataFrame(rows_social)
                df_niveau_vie_melt = df_niveau_vie.melt(
                    id_vars="Métropole", var_name="Indicateur", value_name="Taux (%)"
                ).dropna()

                if not df_niveau_vie_melt.empty:
                    # Barres groupées par métropole, teinte selon indicateur
                    col_chomage = PALETTE_METRO[int(len(PALETTE_METRO) * 0.2)]
                    col_pauvrete = PALETTE_METRO[int(len(PALETTE_METRO) * 0.7)]
                    color_social = {
                        "Taux de chômage (%)":  col_chomage,
                        "Taux de pauvreté (%)": col_pauvrete,
                    }
                    fig_social = px.bar(
                        df_niveau_vie_melt, x="Métropole", y="Taux (%)", color="Indicateur",
                        barmode="group", color_discrete_map=color_social,
                        text="Taux (%)", height=500,
                    )
                    fig_social.update_traces(
                        texttemplate="%{text:.1f}%", textposition="outside",
                        hovertemplate="<b>Métropole : %{x}</b><br>%{fullData.name} : %{y:.1f}%<extra></extra>",
                    )

                    metros_social = list(dict.fromkeys(df_niveau_vie_melt["Métropole"].tolist()))
                    if "Grenoble" in metros_social:
                        g_pos = metros_social.index("Grenoble")
                        fig_social.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                             fillcolor="rgba(255,88,77,0.10)",
                                             line_color="#FF584D", line_width=1.5,
                                             line_dash="dash", layer="below")
                    fig_social.update_layout(
                        xaxis_title="Echelle métropolitaine", yaxis_title="Taux (%)",
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                    )
                    st.plotly_chart(style(fig_social), use_container_width=True)
                else:
                    st.info("Données sociales non disponibles pour les métropoles sélectionnées.")

            with r3c2:
                st.subheader(
                    "Revenu médian vs Taux de pauvreté",
                    help="Chaque bulle représente une métropole. L'axe horizontal indique le revenu médian annuel par unité de consommation (en €) ; l'axe vertical indique le taux de pauvreté (%). La taille de la bulle est proportionnelle à la population. On s'attend à une relation inverse : plus le revenu médian est élevé, plus le taux de pauvreté est faible. Un point qui s'écarte de cette tendance signale une situation atypique (forte inégalité interne, population très hétérogène)."
                )
                data_rev = []
                for m in sel:
                    rev  = epci_val(m, "revenu_median_2021")
                    pauv = epci_val(m, "tx_pauvrete_2021")
                    pop  = epci_val(m, "population_2022")
                    if not any(np.isnan(v) for v in [rev, pauv, pop]):
                        data_rev.append({"Métropole": m, "Revenu médian (€)": rev,
                                         "Taux de pauvreté (%)": pauv, "Population": pop})
                df_rev = pd.DataFrame(data_rev)
                if not df_rev.empty:
                    fig_rev = px.scatter(
                        df_rev, x="Revenu médian (€)", y="Taux de pauvreté (%)",
                        size="Population", color="Métropole", text="Métropole",
                        color_discrete_map=COULEURS, size_max=55, height=500,
                    )
                    fig_rev.update_traces(
                        textposition="top center", textfont_size=11,
                        hovertemplate="<b>%{text}</b><br>Revenu médian : %{x:,.0f} €<br>Taux de pauvreté : %{y:.1f}%<br>Population : %{marker.size:,.0f}<extra></extra>",
                    )
                    # Bordure Grenoble sur la bulle
                    for trace in fig_rev.data:
                        if "Grenoble" in trace.name:
                            trace.marker.line = dict(width=6, color="#FF584D")
                    fig_rev.update_layout(showlegend=False)
                    st.plotly_chart(style(fig_rev), use_container_width=True)
                else:
                    st.info("Données de revenu non disponibles pour les métropoles sélectionnées.")

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Taux de chômage et taux de pauvreté (barres groupées)** : comparer ces deux indicateurs côte à côte permet de distinguer les territoires en difficulté économique structurelle (chômage et pauvreté élevés simultanément) "
                    "de ceux où la pauvreté est présente malgré un faible chômage.\n\n"
                    "**Revenu médian vs Taux de pauvreté (nuage de points)** : ce graphique révèle la relation entre niveau de vie et précarité. "
                    "En règle générale, les deux indicateurs évoluent en sens inverse : plus le revenu médian est élevé, moins il y a de pauvreté. "
                    "Un territoire situé au-dessus de la tendance générale (pauvreté élevée malgré un revenu médian correct) présente souvent de fortes inégalités internes. "
                    "La taille des bulles permet de pondérer visuellement l'importance démographique de chaque métropole dans l'analyse."
                )

            st.markdown("---")
            st.markdown("#### Tableau récapitulatif - indicateurs clés")
            lignes_tab = []
            for m in sel:
                tx_v  = epci_val(m, "tx_var_population_2016_2022")
                tc    = epci_val(m, "tx_chomage_15_64")
                rev   = epci_val(m, "revenu_median_2021")
                pauv  = epci_val(m, "tx_pauvrete_2021")
                dens  = epci_val(m, "densite_2022")
                lignes_tab.append({
                    "Métropole": m,
                    "Population 2022": fmt(epci_val(m, "population_2022")),
                    "Densité (hab/km²)": fmt(dens),
                    "Var. pop./an": f"{tx_v:+.1f}%" if not np.isnan(tx_v) else "N/D",
                    "Solde naturel/an": f"{epci_val(m,'tx_solde_naturel'):+.1f}%" if not np.isnan(epci_val(m,'tx_solde_naturel')) else "N/D",
                    "Solde migrat./an": f"{epci_val(m,'tx_solde_migratoire'):+.1f}%" if not np.isnan(epci_val(m,'tx_solde_migratoire')) else "N/D",
                    "Taux chômage": f"{tc:.1f}%" if not np.isnan(tc) else "N/D",
                    "Revenu médian": fmt(rev, " €"),
                    "Taux pauvreté": f"{pauv:.1f}%" if not np.isnan(pauv) else "N/D",
                    "Nb. ménages": fmt(epci_val(m, "nb_menages_2022")),
                    "Nombre d'emplois": fmt(epci_val(m, "emploi_total_2022")),
                })
            df_tab = pd.DataFrame(lignes_tab).set_index("Métropole")
            st.dataframe(df_tab, use_container_width=True)

# ==============================================================================
# ONGLET 2 - STRUCTURE PAR ÂGE
# ==============================================================================
if vue == "Démographie":
    with tab2:

        if df_pop is None:
            st.info("📂 Fichier `Population_tranche_age_clean.csv` introuvable.")
        else:
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> INSEE -
                <a href='https://www.insee.fr/fr/statistiques/1893204' target='_blank' style='color: #1C3A27;'>Accéder aux données</a>
            </div>""", unsafe_allow_html=True)

            annees_dispo = sorted(df_pop["annee"].dropna().unique().astype(int).tolist())
            ch_all = cols_h(df_pop)
            cf_all = cols_f(df_pop)

            TRANCHES_M25 = ["01","02","03","04","05"]
            TRANCHES_ACT = ["06","07","08","09","10","11","12","13"]
            TRANCHES_SEN = ["14","15","16","17","18","19","20"]

            MIDPOINTS = {
                "01": 2,  "02": 7,  "03": 12, "04": 17, "05": 22,
                "06": 27, "07": 32, "08": 37, "09": 42, "10": 47,
                "11": 52, "12": 57, "13": 62, "14": 67, "15": 72,
                "16": 77, "17": 82, "18": 87, "19": 92, "20": 97,
            }

            def pop_tranches(df_src, tranches):
                total = 0
                for t in tranches:
                    for sx in ["s1", "s2"]:
                        col = f"ageq_rec{t}{sx}rpop2016"
                        if col in df_src.columns:
                            total += pd.to_numeric(df_src[col], errors="coerce").fillna(0).sum()
                return float(total)

            def pop_totale_df(df_src):
                age_cols = [c for c in df_src.columns if "ageq_rec" in c]
                return pd.to_numeric(df_src[age_cols].stack(), errors="coerce").sum()

            def calc_age_median(df_src):
                vals = []
                for i in range(1, 21):
                    t = f"{i:02d}"
                    tot_t = 0
                    for sx in ["s1", "s2"]:
                        col = f"ageq_rec{t}{sx}rpop2016"
                        if col in df_src.columns:
                            tot_t += pd.to_numeric(df_src[col], errors="coerce").fillna(0).sum()
                    vals.append((MIDPOINTS[t], float(tot_t)))
                total = sum(v for _, v in vals)
                if total == 0:
                    return np.nan
                cumul = 0
                for i, (mid, v) in enumerate(vals):
                    cumul += v
                    if cumul >= total / 2:
                        prev_cumul = cumul - v
                        prev_mid   = vals[i-1][0] if i > 0 else 0
                        frac       = (total / 2 - prev_cumul) / v if v > 0 else 0.5
                        return prev_mid + frac * (mid - prev_mid)
                return vals[-1][0]

            def get_pyr_data_pct(df_src):
                labels = [LABEL_TRANCHE.get(f"{i:02d}", f"{i:02d}") for i in range(1, 21)]
                total  = pop_totale_df(df_src)
                vals_h, vals_f = [], []
                for i in range(1, 21):
                    t      = f"{i:02d}"
                    ch_col = f"ageq_rec{t}s1rpop2016"
                    cf_col = f"ageq_rec{t}s2rpop2016"
                    h  = pd.to_numeric(df_src[ch_col], errors="coerce").fillna(0).sum() if ch_col in df_src.columns else 0
                    f_ = pd.to_numeric(df_src[cf_col], errors="coerce").fillna(0).sum() if cf_col in df_src.columns else 0
                    vals_h.append(h  / total * 100 if total > 0 else 0)
                    vals_f.append(f_ / total * 100 if total > 0 else 0)
                return vals_h, vals_f, labels

            def build_pyramide_pct(df_src, label_entity, color_h, color_f, x_max=None):
                vals_h, vals_f, labels = get_pyr_data_pct(df_src)
                if x_max is None:
                    x_max = max(max(vals_h, default=0), max(vals_f, default=0)) * 1.15
                n_ticks   = 3
                tick_step = round(x_max / n_ticks, 1)
                tick_vals = [-tick_step * k for k in range(n_ticks, 0, -1)] + [0] + [tick_step * k for k in range(1, n_ticks + 1)]
                tick_text = [f"{abs(v):.1f}%" for v in tick_vals]
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=labels, x=vals_h, base=[-v for v in vals_h],
                    name="Hommes", orientation="h", marker_color=color_h,
                    customdata=vals_h,
                    hovertemplate="<b>Hommes</b><br>Tranche : %{y}<br>Part : %{customdata:.2f}%<extra></extra>"
                ))
                fig.add_trace(go.Bar(
                    y=labels, x=vals_f,
                    name="Femmes", orientation="h", marker_color=color_f,
                    hovertemplate="<b>Femmes</b><br>Tranche : %{y}<br>Part : %{x:.2f}%<extra></extra>"
                ))
                fig.add_vline(x=0, line_width=1, line_color="#888", line_dash="solid")
                fig.update_layout(
                    barmode="overlay", bargap=0.05,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5, font_size=10),
                    yaxis=dict(title="", tickfont_size=9, showgrid=False),
                    xaxis=dict(
                        title="% de la population",
                        range=[-x_max, x_max],
                        tickvals=tick_vals, ticktext=tick_text,
                        tickfont_size=9, showgrid=True, gridcolor="#eee", zeroline=False,
                    ),
                    title=dict(text=f"<b>{label_entity}</b>", font_size=12, x=0.5, xanchor="center"),
                    height=500, margin=dict(t=40, b=65, l=60, r=10),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                )
                return fig

            def render_kpi_card(label, pct_m25, pct_act, pct_sen, dep_idx, age_med, border_color, dashed=False):
                border_style = (
                    f"border: 2px dashed {border_color}; border-left: 6px solid {border_color};"
                    if dashed else
                    f"border-left: 6px solid {border_color};"
                )
                st.markdown(f"""
                <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                    background:#fff;{border_style}margin-bottom:12px;padding:12px 16px;'>
                    <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px;
                        border-bottom:1px solid #eee;padding-bottom:5px;'>{label}</div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>&lt; 25 ans</div>
                            <div style='font-size:18px;font-weight:800;color:#2D6A4F;'>{f"{pct_m25:.1f}%" if not np.isnan(pct_m25) else "N/D"}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>65 ans +</div>
                            <div style='font-size:18px;font-weight:800;color:#2D6A4F;'>{f"{pct_sen:.1f}%" if not np.isnan(pct_sen) else "N/D"}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Âge médian</div>
                            <div style='font-size:18px;font-weight:800;color:#555;'>{f"{age_med:.1f} ans" if not np.isnan(age_med) else "N/D"}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Indice dép.</div>
                            <div style='font-size:18px;font-weight:800;color:#555;'>{f"{dep_idx:.0f}" if not np.isnan(dep_idx) else "N/D"}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            def build_overlay_chart(territories, df_filtered_fn, color_fn, is_grenoble_fn=None, legend_key="Territoire"):
                rows_ov = []
                for terr in territories:
                    df_t = df_filtered_fn(terr)
                    tot  = pop_totale_df(df_t)
                    if tot == 0:
                        continue
                    for i in range(1, 21):
                        t       = f"{i:02d}"
                        label   = LABEL_TRANCHE.get(t, t)
                        total_t = 0
                        for sx in ["s1", "s2"]:
                            col = f"ageq_rec{t}{sx}rpop2016"
                            if col in df_t.columns:
                                total_t += pd.to_numeric(df_t[col], errors="coerce").fillna(0).sum()
                        rows_ov.append({legend_key: terr, "Tranche": label, "Part (%)": total_t / tot * 100, "Ordre": i})
                df_ov = pd.DataFrame(rows_ov)
                if df_ov.empty:
                    return None
                df_ov = df_ov.sort_values("Ordre")
                fig_ov = go.Figure()
                for terr in territories:
                    df_t_ov    = df_ov[df_ov[legend_key] == terr]
                    is_gren    = is_grenoble_fn(terr) if is_grenoble_fn else False
                    line_color = color_fn(terr, is_gren)
                    fig_ov.add_trace(go.Scatter(
                        x=df_t_ov["Part (%)"],
                        y=df_t_ov["Tranche"],
                        mode="lines+markers",
                        name=terr,
                        line=dict(color=line_color, dash="dash" if is_gren else "solid", width=2.5 if is_gren else 1.8),
                        marker=dict(size=7 if is_gren else 5, color=line_color, symbol="diamond" if is_gren else "circle"),
                        hovertemplate=f"<b>{terr}</b><br>Tranche : %{{y}}<br>Part : %{{x:.2f}}%<extra></extra>",
                    ))
                fig_ov.update_layout(
                    xaxis=dict(title="% de la population totale", ticksuffix="%", showgrid=True, gridcolor="#eee"),
                    yaxis=dict(title="Tranche d'âge", showgrid=False, tickfont_size=9),
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                    height=520, margin=dict(t=20, b=40, l=60, r=160),
                    hovermode="y unified",
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                )
                return fig_ov

            with st.container():
                filter_bar("Filtres - Structure par âge")
                fa1, fa2 = st.columns([1, 3])
                with fa1:
                    filter_row_label("Niveau géographique")
                with fa2:
                    mode_age = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                        key="age_mode", horizontal=True, label_visibility="collapsed")
                if mode_age == "Comparaison Métropoles":
                    sel_metros_age = st.multiselect("Métropoles à comparer", TOUTES, default=shared_default_demo(TOUTES), key="age_metros", on_change=sync_metros_demo, args=("age_metros",))
                else:
                    sel_communes_age = st.multiselect("Communes de Grenoble-Alpes Métropole",
                                                      sorted(COMMUNES["Grenoble"]),
                                                      default=shared_default_communes_demo(sorted(COMMUNES["Grenoble"])),
                                                      key="age_communes",
                                                      on_change=sync_communes_demo, args=("age_communes",))
                annee_age = st.selectbox("Année", annees_dispo, index=len(annees_dispo)-1, key="an_age")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            # ── VUE MÉTROPOLES ────────────────────────────────────────────────
            if mode_age == "Comparaison Métropoles":
                if not sel_metros_age:
                    st.warning("Sélectionnez au moins une métropole.")
                    st.stop()

                st.subheader(f"Indicateurs clés en {annee_age} - Echelle métropolitaine",
                             help="Synthèse des grands groupes d'âge, âge médian estimé et indice de dépendance.")
                kpi_cols = st.columns(len(sel_metros_age))
                for i, m in enumerate(sel_metros_age):
                    df_m    = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                    tot     = pop_totale_df(df_m)
                    p_m25   = pop_tranches(df_m, TRANCHES_M25)
                    p_act   = pop_tranches(df_m, TRANCHES_ACT)
                    p_sen   = pop_tranches(df_m, TRANCHES_SEN)
                    pct_m25 = p_m25 / tot * 100 if tot > 0 else np.nan
                    pct_act = p_act / tot * 100 if tot > 0 else np.nan
                    pct_sen = p_sen / tot * 100 if tot > 0 else np.nan
                    dep_idx = (p_m25 + p_sen) / p_act * 100 if p_act > 0 else np.nan
                    age_med = calc_age_median(df_m)
                    with kpi_cols[i]:
                        render_kpi_card(m, pct_m25, pct_act, pct_sen, dep_idx, age_med,
                                        border_color=COULEURS.get(m, "#888888"))

                with st.expander("Définitions des indicateurs"):
                    st.markdown(
                        "**Âge médian** : âge qui divise la population en deux moitiés égales. "
                        "Estimé par interpolation à partir des tranches quinquennales.  \n"
                        "**Indice de dépendance** : (< 25 ans + ≥ 65 ans) / (25-64 ans) × 100. "
                        "Plus il est élevé, plus les actifs portent une part importante de population non active.  \n"
                    )

                st.markdown("---")

                # ── Pyramides métropoles ────────────────────
                st.subheader("Pyramides des âges des métropoles comparées",
                             help="Toutes les pyramides partagent le même axe X (%) pour une comparaison visuelle directe, "
                                  "quelle que soit la taille de la métropole.")

                n_m            = len(sel_metros_age)
                metro_colors_h = [PALETTE_METRO[int(i * (len(PALETTE_METRO)-1) / max(n_m-1,1))] for i in range(n_m)]
                metro_colors_f = [PALETTE_METRO[max(0, int(i * (len(PALETTE_METRO)-1) / max(n_m-1,1)) - 2)] for i in range(n_m)]
                metro_h_map    = {m: metro_colors_h[i] for i, m in enumerate(sel_metros_age)}
                metro_f_map    = {m: metro_colors_f[i] for i, m in enumerate(sel_metros_age)}

                all_maxes = []
                for m in sel_metros_age:
                    df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                    vh, vf, _ = get_pyr_data_pct(df_m)
                    all_maxes.append(max(max(vh, default=0), max(vf, default=0)))
                shared_x_max = max(all_maxes) * 1.18 if all_maxes else 5.0

                ncols    = min(n_m, 3)
                rows_pyr = [sel_metros_age[i:i+ncols] for i in range(0, n_m, ncols)]
                for row in rows_pyr:
                    cols = st.columns(len(row))
                    for j, m in enumerate(row):
                        df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)]
                        fig  = build_pyramide_pct(df_m, m, metro_h_map[m], metro_f_map[m], x_max=shared_x_max)
                        if m == "Grenoble":
                            for trace in fig.data:
                                if trace.type == "bar":
                                    trace.marker.pattern.shape    = "/"
                                    trace.marker.pattern.fgcolor  = "#FF584D"
                                    trace.marker.pattern.size     = 20
                                    trace.marker.pattern.solidity = 0.3
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter les pyramides ?"):
                    st.write(
                        "Axe X identique pour toutes les pyramides → comparaison visuelle directe. "
                        "Base large = beaucoup de jeunes. Sommet large = fort vieillissement. "
                        "Forme en 'toupie' (ventre 25-55 ans) = dominance de la population active.\n\n"
                        "Grenoble est mise en valeur par des hachures rouges (/) sur ses barres."
                    )

                st.markdown("---")

                # ── Profils superposés métropoles ─────────────────────────────
                st.subheader("Répartition des métropoles par tranches d’âges",
                             help="Distribution totale (H+F) de chaque métropole en % de la population totale par tranche d'âge. "
                                  "L'affichage en % neutralise l'effet taille pour une comparaison directe.")

                fig_ov_m = build_overlay_chart(
                    territories    = sel_metros_age,
                    df_filtered_fn = lambda m: df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == annee_age)],
                    color_fn       = lambda m, is_g: "#FF584D" if is_g else COULEURS.get(m, "#888"),
                    is_grenoble_fn = lambda m: m == "Grenoble",
                    legend_key     = "Territoire",
                )
                if fig_ov_m:
                    fig_ov_m.update_layout(
                        legend_title_text="Métropole")
                    st.plotly_chart(style(fig_ov_m, 20), use_container_width=True)

                with st.expander("💡 Comment lire ce graphique ?"):
                    st.write(
                        "Chaque courbe montre la 'silhouette démographique' d'une métropole. "
                        "Grenoble est en pointillés rouges avec des marqueurs losange. "
                        "Les pics sur 20-34 ans caractérisent les villes étudiantes ou attractives pour les jeunes actifs. "
                        "Les courbes décalées vers les 65+ signalent un vieillissement plus marqué."
                    )

                st.markdown("---")

                # ── Évolution temporelle métropoles ───────────────────────────
                st.subheader("Évolution des groupes d'âge (2011 → 2022)",
                             help="Part des moins de 25 ans et des 65+ dans la population totale sur les trois recensements.")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Part des moins de 25 ans (%)")
                    rows_ev = []
                    for m in sel_metros_age:
                        for an in annees_dispo:
                            df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == an)]
                            tot  = pop_totale_df(df_m)
                            p    = pop_tranches(df_m, TRANCHES_M25)
                            if tot > 0:
                                rows_ev.append({"Métropole": m, "Année": str(int(an)), "Part (%)": p/tot*100})
                    df_ev = pd.DataFrame(rows_ev)
                    if not df_ev.empty:
                        fig_ev1 = px.line(df_ev, x="Année", y="Part (%)", color="Métropole",
                                          markers=True, color_discrete_map=COULEURS)
                        fig_ev1.update_layout(xaxis=dict(type="category"))
                        fig_ev1.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        for trace in fig_ev1.data:
                            if "Grenoble" in trace.name:
                                trace.line.dash = "dash"; trace.line.color = "#FF584D"; trace.line.width = 2.5
                                if trace.marker: trace.marker.color = "#FF584D"; trace.marker.symbol = "diamond"; trace.marker.size = 8
                        st.plotly_chart(style(fig_ev1), use_container_width=True)
                with c2:
                    st.markdown("##### Part des 65 ans et + (%)")
                    rows_ev2 = []
                    for m in sel_metros_age:
                        for an in annees_dispo:
                            df_m = df_pop[(df_pop["metropole"] == m) & (df_pop["annee"] == an)]
                            tot  = pop_totale_df(df_m)
                            p    = pop_tranches(df_m, TRANCHES_SEN)
                            if tot > 0:
                                rows_ev2.append({"Métropole": m, "Année": str(int(an)), "Part (%)": p/tot*100})
                    df_ev2 = pd.DataFrame(rows_ev2)
                    if not df_ev2.empty:
                        fig_ev2 = px.line(df_ev2, x="Année", y="Part (%)", color="Métropole",
                                          markers=True, color_discrete_map=COULEURS)
                        fig_ev2.update_layout(xaxis=dict(type="category"))
                        fig_ev2.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        for trace in fig_ev2.data:
                            if "Grenoble" in trace.name:
                                trace.line.dash = "dash"; trace.line.color = "#FF584D"; trace.line.width = 2.5
                                if trace.marker: trace.marker.color = "#FF584D"; trace.marker.symbol = "diamond"; trace.marker.size = 8
                        st.plotly_chart(style(fig_ev2), use_container_width=True)

                with st.expander("💡 Comment interpréter ces courbes d'évolution ?"):
                    st.write(
                        "Évolution de la composition par âge entre 2011 et 2022. "
                        "Les ordonnées ne commencent pas à 0 - l'objectif est d'observer la tendance.\n\n"
                        "Grenoble est en pointillés rouges avec des marqueurs losange."
                    )

            # ── VUE COMMUNES ──────────────────────────────────────────────────
            else:
                communes_age = sel_communes_age if sel_communes_age else []
                if not communes_age:
                    st.info("Sélectionnez au moins une commune.")
                    st.stop()

                n_comm_age   = len(communes_age)
                comm_palette = PALETTE_COMMUNE[:n_comm_age] if n_comm_age <= len(PALETTE_COMMUNE) else PALETTE_COMMUNE

                # ── KPI enrichis communes ─────────────────────────────────────
                st.subheader(f"Indicateurs clés en {annee_age} - Echelle communale",
                             help="Synthèse des grands groupes d'âge, âge médian estimé et indice de dépendance pour chaque commune sélectionnée.")
                kpi_cols = st.columns(n_comm_age)
                for i, comm in enumerate(communes_age):
                    df_c    = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                    tot     = pop_totale_df(df_c)
                    p_m25   = pop_tranches(df_c, TRANCHES_M25)
                    p_act   = pop_tranches(df_c, TRANCHES_ACT)
                    p_sen   = pop_tranches(df_c, TRANCHES_SEN)
                    pct_m25 = p_m25 / tot * 100 if tot > 0 else np.nan
                    pct_act = p_act / tot * 100 if tot > 0 else np.nan
                    pct_sen = p_sen / tot * 100 if tot > 0 else np.nan
                    dep_idx = (p_m25 + p_sen) / p_act * 100 if p_act > 0 else np.nan
                    age_med = calc_age_median(df_c)
                    with kpi_cols[i]:
                        render_kpi_card(comm, pct_m25, pct_act, pct_sen, dep_idx, age_med,
                                        border_color=comm_palette[i % len(comm_palette)],
                                        dashed=False)

                with st.expander("Définitions des indicateurs"):
                    st.markdown(
                        "**Âge médian** : âge qui divise la population en deux moitiés égales. "
                        "Estimé par interpolation à partir des tranches quinquennales.  \n"
                        "**Indice de dépendance** : (< 25 ans + ≥ 65 ans) / (25-64 ans) × 100.  \n"
                    )

                st.markdown("---")

                # ── Pyramides communes ──────────────────────
                st.subheader("Pyramides des âges des communes comparées",
                             help="Toutes les pyramides partagent le même axe X (%) pour une comparaison visuelle directe, "
                                  "quelle que soit la taille de chaque commune.")

                all_maxes_c = []
                for comm in communes_age:
                    df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                    vh, vf, _ = get_pyr_data_pct(df_c)
                    all_maxes_c.append(max(max(vh, default=0), max(vf, default=0)))
                shared_x_max_c = max(all_maxes_c) * 1.18 if all_maxes_c else 5.0

                ncols      = min(n_comm_age, 3)
                rows_pyr_c = [communes_age[i:i+ncols] for i in range(0, n_comm_age, ncols)]
                for row in rows_pyr_c:
                    cols = st.columns(len(row))
                    for j, comm in enumerate(row):
                        df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == annee_age)]
                        fig  = build_pyramide_pct(df_c, comm, "#2D6A4F", "#74C69D", x_max=shared_x_max_c)
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter les pyramides ?"):
                    st.write(
                        "Axe X identique pour toutes les communes → comparaison visuelle directe, "
                        "indépendamment de la taille de chaque commune. "
                        "Base large = beaucoup de jeunes. Sommet large = fort vieillissement. "
                        "Forme en 'toupie' (ventre 25-55 ans) = dominance de la population active.\n\n"
                    )

                st.markdown("---")

                # ── Profils superposés communes ───────────────────────────────
                st.subheader("Répartition des communes par tranches d'âges",
                             help="Distribution totale (H+F) de chaque commune en % de sa population totale par tranche d'âge. "
                                  "L'affichage en % neutralise l'effet taille pour comparer des communes de tailles très différentes.")

                fig_ov_c = build_overlay_chart(
                    territories    = communes_age,
                    df_filtered_fn = lambda c: df_pop[(df_pop["LIBELLE"] == c) & (df_pop["annee"] == annee_age)],
                    color_fn       = lambda c, is_g: comm_palette[communes_age.index(c) % len(comm_palette)],
                    is_grenoble_fn = None,
                    legend_key     = "Territoire",
                )
                if fig_ov_c:
                    st.plotly_chart(style(fig_ov_c, 20), use_container_width=True)

                with st.expander("💡 Comment lire ce graphique ?"):
                    st.write(
                        "Chaque courbe montre la 'silhouette démographique' d'une commune en % de sa population totale. "
                        "Cela permet de comparer des communes de tailles très différentes sur un pied d'égalité. "
                        "Les pics sur les 20-34 ans révèlent des communes attractives pour les jeunes. "
                        "Les profils étalés vers 65+ indiquent un vieillissement plus marqué."
                    )

                st.markdown("---")

                # ── Évolution temporelle communes ─────────────────────────────
                st.subheader("Évolution des groupes d'âge (2011 → 2022)",
                             help="Part des moins de 25 ans et des 65+ dans la population totale sur les trois recensements.")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Part des moins de 25 ans (%)")
                    rows_evc = []
                    for comm in communes_age:
                        for an in annees_dispo:
                            df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == an)]
                            tot  = pop_totale_df(df_c)
                            p    = pop_tranches(df_c, TRANCHES_M25)
                            if tot > 0:
                                rows_evc.append({"Commune": comm, "Année": str(int(an)), "Part (%)": p/tot*100})
                    df_evc = pd.DataFrame(rows_evc)
                    if not df_evc.empty:
                        fig_evc1 = px.line(df_evc, x="Année", y="Part (%)", color="Commune",
                                           markers=True, color_discrete_sequence=PALETTE_COMMUNE)
                        fig_evc1.update_layout(xaxis=dict(type="category"))
                        fig_evc1.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        st.plotly_chart(style(fig_evc1), use_container_width=True)
                with c2:
                    st.markdown("##### Part des 65 ans et + (%)")
                    rows_evc2 = []
                    for comm in communes_age:
                        for an in annees_dispo:
                            df_c = df_pop[(df_pop["LIBELLE"] == comm) & (df_pop["annee"] == an)]
                            tot  = pop_totale_df(df_c)
                            p    = pop_tranches(df_c, TRANCHES_SEN)
                            if tot > 0:
                                rows_evc2.append({"Commune": comm, "Année": str(int(an)), "Part (%)": p/tot*100})
                    df_evc2 = pd.DataFrame(rows_evc2)
                    if not df_evc2.empty:
                        fig_evc2 = px.line(df_evc2, x="Année", y="Part (%)", color="Commune",
                                           markers=True, color_discrete_sequence=PALETTE_COMMUNE)
                        fig_evc2.update_layout(xaxis=dict(type="category"))
                        fig_evc2.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Année : %{x}<br>Part : %{y:.2f}%<extra></extra>")
                        st.plotly_chart(style(fig_evc2), use_container_width=True)

                with st.expander("💡 Comment interpréter ces courbes d'évolution ?"):
                    st.write(
                        "Évolution de la composition par âge de chaque commune entre 2011 et 2022. "
                        "Les ordonnées ne commencent pas à 0 - l'objectif est d'observer la tendance.\n\n"
                    )

# ==============================================================================
# ONGLET 3 - MOBILITÉS 
# ==============================================================================

if vue == "Démographie":
    with tab3:

        data_ok = any(df is not None for df in [df_res, df_prof, df_scol])
        if not data_ok:
            st.info("📂 Fichiers de mobilité manquants.")
        else:
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px;
                        border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 14px;'>
                <strong>Source :</strong> INSEE<br><br>
                🏠 <b>Migrations résidentielles</b> : mesure l'origine et la destination des habitants ayant déménagé au cours de l'année. L'analyse sépare les flux de proximité (internes à la métropole) des flux d'échanges nationaux (entrants et sortants de la métropole).
                <a href='https://www.insee.fr/fr/statistiques/8582988' target='_blank'
                   style='color:#1C3A27;font-size:0.85em;'>Données INSEE</a><br><br>
                💼 <b>Trajets domicile-travail</b> : représente les déplacements quotidiens de la population active. Elle comptabilise les actifs stables (travaillant dans leur territoire de résidence) et les flux alternants (actifs entrants et sortants d'autres métropoles).
                <a href='https://www.insee.fr/fr/statistiques/8582949' target='_blank'
                   style='color:#1C3A27;font-size:0.85em;'>Données INSEE</a><br><br>
                🎓 <b>Mobilités scolaires</b> : analyse les déplacements quotidiens des élèves et étudiants (de la maternelle au supérieur) entre leur domicile et leur lieu d'études.<br> 
                        Les données comptabilisent la totalité de la population scolarisée en isolant les jeunes qui étudient dans leur propre commune de résidence des flux alternants (élèves venant de territoires extérieurs et élèves locaux se déplaçant hors de la métropole).
                <a href='https://www.insee.fr/fr/statistiques/8582969' target='_blank'
                   style='color:#1C3A27;font-size:0.85em;'>Données INSEE</a>
            </div>""", unsafe_allow_html=True)

            with st.container():
                filter_bar("Filtres - Mobilités")
                col_geo_label, col_geo_options = st.columns([1, 3])
                with col_geo_label:
                    filter_row_label("Niveau géographique")
                with col_geo_options:
                    mode_mob = st.radio(
                        "",
                        ["Comparaison Métropoles",
                         "Comparaison communes Grenoble-Alpes Métropole"],
                        key="mob_mode", horizontal=True, label_visibility="collapsed",
                    )

                if mode_mob == "Comparaison communes Grenoble-Alpes Métropole":
                    sel_communes_mob = st.multiselect(
                        "Communes de Grenoble-Alpes Métropole",
                        sorted(COMMUNES["Grenoble"]),
                        default=shared_default_communes_demo(sorted(COMMUNES["Grenoble"])),
                        key="mob_communes",
                        on_change=sync_communes_demo, args=("mob_communes",),
                    )
                    targets = sel_communes_mob
                else:
                    sel_metros_mob = st.multiselect(
                        "Métropoles à comparer", TOUTES,
                        default=shared_default_demo(TOUTES),
                        key="mob_metros",
                        on_change=sync_metros_demo, args=("mob_metros",),
                    )
                    targets = sel_metros_mob

                mob_col1, mob_col2 = st.columns(2)
                with mob_col1:
                    theme_mob = st.selectbox(
                        "Thématique d'analyse",
                        ["🏠 Migrations Résidentielles",
                         "💼 Trajets domicile-travail",
                         "🎓 Mobilité Scolaire"],
                        key="mob_theme",
                    )

            # ── Paramètres selon thématique ───────────────────────────────────
            if "Migrations" in theme_mob:
                current_mob_df     = df_res
                col_orig, col_dest = "commune_origine", "commune_destination"
                label_in           = "Arrivées"
                label_out          = "Départs"
                label_int          = "Déménagements internes"
                help_kpi  = "Solde migratoire = arrivées depuis l'extérieur − départs vers l'extérieur."
                help_ext  = "Flux de personnes entre cette métropole et le reste du territoire français."
                help_int  = "Personnes ayant déménagé entre deux communes de la même métropole."
                
                # ✍️ MODIFIEZ VOS INTERPRÉTATIONS DE GRAPHIQUES ICI :
                interpret_vol = (
                    f"**{label_in}** (barres pleines) : flux provenant de l'extérieur de la métropole.\n\n"
                    f"**{label_out}** (barres transparentes) : flux partant vers l'extérieur de la métropole.\n\n"
                    f"Les flux entre communes de la même métropole sont exclus. Le solde = entrées − sorties est affiché dans les KPI."
                )
                interpret_int = (
                    f"**Volume interne** : nombre de {label_int.lower()}. "
                    f"Ces flux ne participent pas au solde net mais révèlent la cohésion fonctionnelle de la métropole.\n\n"
                    f"**Autonomie territoriale** : part des flux internes par rapport aux flux vers l'extérieur. "
                    f"Une métropole à 80 %+ d'autonomie est très auto-suffisante."
                )

            elif "domicile" in theme_mob:
                current_mob_df     = df_prof
                col_orig, col_dest = "commune_residence", "commune_travail"
                label_in           = "Actifs entrants"
                label_out          = "Actifs sortants"
                label_int          = "Actifs travaillant dans leur métropole"
                help_kpi  = "Solde = actifs venant travailler ici − actifs partant travailler ailleurs."
                help_ext  = "Flux d'actifs entre cette métropole et d'autres territoires."
                help_int  = "Actifs dont le domicile ET le lieu de travail sont dans la même métropole."
                
                # ✍️ MODIFIEZ VOS INTERPRÉTATIONS DE GRAPHIQUES ICI :
                interpret_vol = (
                    f"**{label_in}** (barres pleines) : actifs résidant à l'extérieur mais venant travailler ici.\n\n"
                    f"**{label_out}** (barres transparentes) : actifs résidant ici mais partant travailler à l'extérieur.\n\n"
                    f"Ce graphique illustre l'attractivité économique et les besoins en infrastructures de transport."
                )
                interpret_int = (
                    f"**Volume interne** : nombre de {label_int.lower()}.\n\n"
                    f"**Autonomie territoriale** : indique la capacité du territoire à fournir des emplois à ses propres habitants. "
                    f"Un taux élevé limite les déplacements interurbains quotidiens."
                )

            else:
                current_mob_df     = df_scol
                col_orig, col_dest = "commune_origine", "commune_destination"
                label_in           = "Élèves entrants"
                label_out          = "Élèves sortants"
                label_int          = "Élèves scolarisés dans leur métropole"
                help_kpi  = "Solde = élèves venant étudier ici − élèves partant étudier ailleurs."
                help_ext  = "Flux d'élèves entre cette métropole et d'autres territoires."
                help_int  = "Élèves dont le domicile ET l'établissement sont dans la même métropole."
                
                interpret_vol = (
                    f"**{label_in}** (barres pleines) : élèves ou étudiants habitant ailleurs mais scolarisés ici.\n\n"
                    f"**{label_out}** (barres transparentes) : élèves ou étudiants du territoire effectuant leurs études à l'extérieur.\n\n"
                    f"Met en évidence le rayonnement des pôles scolaires et universitaires."
                )
                interpret_int = (
                    f"**Volume interne** : nombre de {label_int.lower()}.\n\n"
                    f"**Autonomie scolaire** : mesure la part des jeunes qui réalisent leur scolarité au sein de leur propre territoire."
                )

            if current_mob_df is None:
                st.info("📂 Fichier de mobilité manquant pour cette thématique.")
            else:
                annees_mob = sorted(
                    current_mob_df["annee"].dropna().unique().astype(int), reverse=True
                )
                with mob_col2:
                    sel_annee_mob = st.selectbox("Année", annees_mob, key="mob_annee")

                # Filtre année
                df_yr = current_mob_df[current_mob_df["annee"] == sel_annee_mob].copy()
                
                # Exclure origine == destination UNIQUEMENT pour les migrations
                if "Migrations" in theme_mob:
                    df_yr = df_yr[df_yr[col_orig] != df_yr[col_dest]]

                # ── Construction des entités par noms de communes ─────────────
                entities_mob = []
                for target in targets:
                    if mode_mob == "Comparaison communes Grenoble-Alpes Métropole":
                        coms_set = {target}
                    else:
                        coms_set = set(COMMUNES.get(target, []))

                    f_in  = int(df_yr[
                        df_yr[col_dest].isin(coms_set)
                        & ~df_yr[col_orig].isin(coms_set)
                    ]["flux"].sum())
                    f_out = int(df_yr[
                        df_yr[col_orig].isin(coms_set)
                        & ~df_yr[col_dest].isin(coms_set)
                    ]["flux"].sum())
                    f_int = int(df_yr[
                        df_yr[col_orig].isin(coms_set)
                        & df_yr[col_dest].isin(coms_set)
                    ]["flux"].sum())

                    entities_mob.append({
                        "name":    target,
                        "in":      f_in,
                        "out":     f_out,
                        "interne": f_int,
                        "solde":   f_in - f_out,
                        "coms":    coms_set,
                    })

                df_plot_mob = pd.DataFrame(entities_mob)
                noms_mob    = df_plot_mob["name"].tolist()
                n_mob       = len(df_plot_mob)

                if df_plot_mob.empty or n_mob == 0:
                    st.info("Aucune donnée pour la sélection.")
                else:
                    # ── Couleurs ──────────────────────────────────────────────
                    if mode_mob == "Comparaison communes Grenoble-Alpes Métropole":
                        bar_colors = [
                            PALETTE_COMMUNE[int(i * (len(PALETTE_COMMUNE)-1) / max(n_mob-1, 1))]
                            for i in range(n_mob)
                        ]
                    else:
                        bar_colors = [COULEURS.get(n, "#888888") for n in noms_mob]

                    # Encadré Grenoble
                    greno_vrect = None
                    if "Grenoble" in noms_mob and mode_mob == "Comparaison Métropoles":
                        g_pos = noms_mob.index("Grenoble")
                        greno_vrect = dict(
                            x0=g_pos - 0.45, x1=g_pos + 0.45,
                            fillcolor="rgba(255,88,77,0.10)",
                            line_color="#FF584D", line_width=1.5,
                            line_dash="dash", layer="below",
                        )
                    
                    # ── Fonction flexible pour styliser les barres ────────────────────────────
                    def bar_marker(name, color, hachures=False):
                        marker_dict = dict(color=color)
                        if hachures and name == "Grenoble" and mode_mob == "Comparaison Métropoles":
                            marker_dict["pattern"] = dict(
                                shape="/", fgcolor="#FF584D", fillmode="overlay", solidity=0.3, size=20
                            )
                        return marker_dict

                    # ══════════════════════════════════════════════════════════
                    # KPI : Solde + volumes IN/OUT
                    # ══════════════════════════════════════════════════════════
                    st.markdown(
                        f"#### Bilan - {theme_mob} ({sel_annee_mob})",
                        help=help_kpi,
                    )
                    kpi_cols = st.columns(n_mob)
                    for i, row in df_plot_mob.iterrows():
                        color_solde   = "#006400" if row["solde"] >= 0 else "#8B0000"
                        kpi_mob_color = bar_colors[i]
                        solde_fmt = f"{row['solde']:+,d}".replace(",", "\u202f")
                        in_fmt    = f"{row['in']:,}".replace(",", "\u202f")
                        out_fmt   = f"{row['out']:,}".replace(",", "\u202f")
                        with kpi_cols[i]:
                            st.markdown(f"""
                            <div style='display:flex;flex-direction:row;align-items:stretch;
                                border-radius:8px;overflow:hidden;
                                box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
                                min-height:90px;border-left:6px solid {kpi_mob_color};'>
                                <div style='padding:10px 16px;display:flex;flex-direction:column;
                                    justify-content:center;'>
                                    <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;
                                        color:#666;text-transform:uppercase;'>{row['name']}</div>
                                    <div style='font-size:26px;font-weight:bold;
                                        color:{color_solde};'>{solde_fmt}</div>
                                    <div style='font-size:10px;color:#555;margin-top:2px;'>
                                        SOLDE &nbsp;·&nbsp;
                                        <span style='color:#1B4332;'>▲ {in_fmt}</span>
                                        &nbsp;entrées &nbsp;·&nbsp;
                                        <span style='color:#8B0000;'>▼ {out_fmt}</span>
                                        &nbsp;sorties
                                    </div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                    st.markdown("---")

                    # ══════════════════════════════════════════════════════════
                    # SECTION 1 : ÉCHANGES EXTERNES
                    # ══════════════════════════════════════════════════════════
                    st.subheader("Échanges avec l'extérieur", help=help_ext)

                    # ── Graphique A : Volume IN / OUT ─────────────────────────
                    fig_vol = go.Figure()
                    COLOR_ARRIVEES = PALETTE_METRO[0]
                    COLOR_DEPARTS = PALETTE_METRO[-1]
                    for i, row in df_plot_mob.iterrows():
                        c = bar_colors[i]
                        fig_vol.add_trace(go.Bar(
                            x=[row["name"]], y=[row["in"]],
                            name=label_in,
                            marker=bar_marker(row["name"], COLOR_ARRIVEES, hachures=False),
                            legendgroup="in", showlegend=(i == 0),
                            offsetgroup="in",
                            hovertemplate=(
                                f"<b>{row['name']}</b><br>"
                                f"{label_in} : %{{y:,.0f}}<extra></extra>"
                            ),
                        ))
                        fig_vol.add_trace(go.Bar(
                            x=[row["name"]], y=[row["out"]],
                            name=label_out,
                            marker=dict(color=COLOR_DEPARTS, opacity=0.45),
                            legendgroup="out", showlegend=(i == 0),
                            offsetgroup="out",
                            hovertemplate=(
                                f"<b>{row['name']}</b><br>"
                                f"{label_out} : %{{y:,.0f}}<extra></extra>"
                            ),
                        ))
                    if greno_vrect:
                        fig_vol.add_vrect(**greno_vrect)
                    fig_vol.update_layout(
                        barmode="group", height=340,
                        margin=dict(t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                    xanchor="left", x=0),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(gridcolor="#E8F5EE", title="Flux"),
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)

                    with st.expander("💡 Interpréter le graphique volumes"):
                        st.write(interpret_vol)  # Utilisation de votre variable paramétrée

                    # ── Graphique B : Top 5 provenances + Top 5 destinations ──
                    st.markdown("##### Top 5 provenances et destinations par territoire")

                    n_cols_top = min(n_mob, 5)
                    rows_top   = (n_mob + n_cols_top - 1) // n_cols_top

                    for row_idx in range(rows_top):
                        cols_top = st.columns(n_cols_top)
                        for col_idx in range(n_cols_top):
                            t_idx = row_idx * n_cols_top + col_idx
                            if t_idx >= n_mob:
                                break
                            target   = targets[t_idx]
                            tc       = bar_colors[t_idx]
                            coms_set = entities_mob[t_idx]["coms"]

                            with cols_top[col_idx]:
                                is_greno = (
                                    target == "Grenoble"
                                    and mode_mob == "Comparaison Métropoles"
                                )
                                border_style = (
                                    "border:2px dashed #FF584D;border-radius:8px;"
                                    "padding:8px;margin-bottom:6px;"
                                    if is_greno else
                                    f"border-left:4px solid {tc};padding-left:8px;"
                                    "margin-bottom:6px;"
                                )
                                st.markdown(
                                    f"<div style='{border_style}'>"
                                    f"<b style='color:{tc};font-size:13px;'>{target}</b>"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )

                                # Flux entrants externes
                                df_in_t = df_yr[
                                    df_yr[col_dest].isin(coms_set)
                                    & ~df_yr[col_orig].isin(coms_set)
                                ]
                                # Flux sortants externes
                                df_out_t = df_yr[
                                    df_yr[col_orig].isin(coms_set)
                                    & ~df_yr[col_dest].isin(coms_set)
                                ]

                                top5_in  = (
                                    df_in_t.groupby(col_orig)["flux"].sum()
                                    .nlargest(5).reset_index()
                                )
                                top5_out = (
                                    df_out_t.groupby(col_dest)["flux"].sum()
                                    .nlargest(5).reset_index()
                                )

                                # Top 5 provenances
                                st.markdown(
                                    f"<div style='font-size:11px;font-weight:700;"
                                    f"color:#1B4332;margin-top:4px;'>"
                                    f"▲ Top 5 {label_in}</div>",
                                    unsafe_allow_html=True,
                                )
                                if top5_in.empty:
                                    st.caption("Aucune donnée")
                                else:
                                    max_in_val = top5_in["flux"].max()
                                    for rank, r in enumerate(top5_in.itertuples(), 1):
                                        nom   = getattr(r, col_orig)
                                        val   = f"{int(r.flux):,}".replace(",", "\u202f")
                                        width = int(r.flux / max_in_val * 100)
                                        st.markdown(
                                            f"<div style='display:flex;align-items:center;"
                                            f"gap:6px;margin:3px 0;font-size:11px;'>"
                                            f"<span style='color:#888;min-width:14px;"
                                            f"font-weight:600;'>{rank}.</span>"
                                            f"<div style='flex:1;background:#e8f5ee;"
                                            f"border-radius:3px;overflow:hidden;height:14px;'>"
                                            f"<div style='width:{width}%;background:{tc};"
                                            f"height:100%;border-radius:3px;'></div></div>"
                                            f"<span style='min-width:85px;max-width:85px;"
                                            f"overflow:hidden;text-overflow:ellipsis;"
                                            f"white-space:nowrap;' title='{nom}'>{nom}</span>"
                                            f"<span style='color:#1B4332;font-weight:700;"
                                            f"min-width:42px;text-align:right;'>{val}</span>"
                                            f"</div>",
                                            unsafe_allow_html=True,
                                        )

                                # Top 5 destinations
                                st.markdown(
                                    f"<div style='font-size:11px;font-weight:700;"
                                    f"color:#8B0000;margin-top:10px;'>"
                                    f"▼ Top 5 {label_out}</div>",
                                    unsafe_allow_html=True,
                                )
                                if top5_out.empty:
                                    st.caption("Aucune donnée")
                                else:
                                    max_out_val = top5_out["flux"].max()
                                    for rank, r in enumerate(top5_out.itertuples(), 1):
                                        nom   = getattr(r, col_dest)
                                        val   = f"{int(r.flux):,}".replace(",", "\u202f")
                                        width = int(r.flux / max_out_val * 100)
                                        st.markdown(
                                            f"<div style='display:flex;align-items:center;"
                                            f"gap:6px;margin:3px 0;font-size:11px;'>"
                                            f"<span style='color:#888;min-width:14px;"
                                            f"font-weight:600;'>{rank}.</span>"
                                            f"<div style='flex:1;background:#fce8e8;"
                                            f"border-radius:3px;overflow:hidden;height:14px;'>"
                                            f"<div style='width:{width}%;background:#8B0000;"
                                            f"height:100%;border-radius:3px;opacity:0.7;'>"
                                            f"</div></div>"
                                            f"<span style='min-width:85px;max-width:85px;"
                                            f"overflow:hidden;text-overflow:ellipsis;"
                                            f"white-space:nowrap;' title='{nom}'>{nom}</span>"
                                            f"<span style='color:#8B0000;font-weight:700;"
                                            f"min-width:42px;text-align:right;'>{val}</span>"
                                            f"</div>",
                                            unsafe_allow_html=True,
                                        )

                    st.markdown("---")

                    # ══════════════════════════════════════════════════════════
                    # SECTION 2 : FLUX INTERNES
                    # ══════════════════════════════════════════════════════════
                    if df_plot_mob["interne"].sum() > 0:
                        st.subheader("Mobilité intra-métropolitaine", help=help_int)

                        ci1, ci2 = st.columns(2)

                        with ci1:
                            st.markdown(
                                "##### Volume des flux internes",
                                help=(
                                    f"{help_int}\n\n"
                                    "Un volume élevé traduit une forte densité fonctionnelle : "
                                    "les résidents se déplacent beaucoup mais restent dans "
                                    "la métropole."
                                ),
                            )
                            fig_int = go.Figure()
                            for i, row in df_plot_mob.iterrows():
                                fig_int.add_trace(go.Bar(
                                    x=[row["name"]], y=[row["interne"]],
                                    name=row["name"],
                                    marker=bar_marker(row["name"], bar_colors[i], hachures=True),
                                    showlegend=False,
                                    hovertemplate=(
                                        f"<b>{row['name']}</b><br>"
                                        f"Flux internes : %{{y:,.0f}}<extra></extra>"
                                    ),
                                ))
                            fig_int.update_layout(
                                height=320, margin=dict(t=10, b=10),
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font_family="Sora",
                                xaxis=dict(showgrid=False),
                                yaxis=dict(gridcolor="#E8F5EE", title="Flux internes"),
                            )
                            st.plotly_chart(fig_int, use_container_width=True)

                        # Affichage du graphique d'Autonomie Territoriale UNIQUEMENT si ce n'est pas "Migrations"
                        if "Migrations" not in theme_mob:
                            with ci2:
                                st.markdown(
                                    "##### Autonomie territoriale (%)",
                                    help=(
                                        "Part des flux internes dans l'ensemble des flux du territoire "
                                        "(internes + sortants externes). "
                                        "Un taux élevé = territoire autonome, ses résidents restent "
                                        "sur place pour travailler/étudier/se loger. "
                                        "Un taux faible = forte dépendance aux territoires voisins."
                                    ),
                                )
                                df_plot_mob["total_all"] = (
                                    df_plot_mob["interne"] + df_plot_mob["out"]
                                )
                                df_plot_mob["pct_int"] = (
                                    df_plot_mob["interne"] / df_plot_mob["total_all"] * 100
                                ).fillna(0)
                                df_plot_mob["pct_ext"] = 100 - df_plot_mob["pct_int"]

                                COLOR_INTERNE = PALETTE_METRO[0]
                                COLOR_EXTERNE = PALETTE_METRO[4]

                                fig_auto = go.Figure()

                                fig_auto.add_trace(go.Bar(
                                    x=noms_mob,
                                    y=df_plot_mob["pct_int"],
                                    name="Internes (%)",
                                    marker=dict(color=COLOR_INTERNE),
                                    text=[f"{v:.0f}%" for v in df_plot_mob["pct_int"]],
                                    textposition="inside",
                                    textfont=dict(color="#333", size=10),
                                    hovertemplate="<b>%{x}</b><br>Internes : %{y:.1f} %<extra></extra>",
                                ))

                                fig_auto.add_trace(go.Bar(
                                    x=noms_mob,
                                    y=df_plot_mob["pct_ext"],
                                    name="Externes (%)",
                                    marker=dict(color=COLOR_EXTERNE),
                                    text=[f"{v:.0f}%" for v in df_plot_mob["pct_ext"]],
                                    textposition="inside",
                                    textfont=dict(color="white", size=10),
                                    hovertemplate="<b>%{x}</b><br>Externes : %{y:.1f} %<extra></extra>",
                                ))
                                
                                if greno_vrect:
                                    fig_auto.add_vrect(**greno_vrect)
                                fig_auto.update_layout(
                                    barmode="stack",
                                    height=320, margin=dict(t=10, b=10),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    font_family="Sora",
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                                xanchor="left", x=0),
                                    xaxis=dict(showgrid=False),
                                    yaxis=dict(
                                        gridcolor="#E8F5EE",
                                        title="Part des flux (%)",
                                        range=[0, 100],
                                    ),
                                )
                                st.plotly_chart(fig_auto, use_container_width=True)

                        with st.expander("💡 Interpréter les flux internes"):
                            st.write(interpret_int)  # Utilisation de votre variable paramétrée

# ==============================================================================
# ONGLET 4 - TRANSPORT DOMICILE-TRAVAIL
# ==============================================================================

if vue == "Démographie":
    with tab4:

        if df_transport is None:
            st.info("📂 Fichier `transport_metropoles_clean.csv` introuvable.")
        else:
            # ── Encart Source ──────────────────────────────────────────────
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> INSEE -
                <a href='https://www.insee.fr/fr/statistiques/7632973' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br><br>
                <strong>Note sur les données :</strong> Il s'agit de mobilités professionnelles des actifs (<strong>15 ans et plus</strong>), millésimes 2020 et 2021.
                Ces données représentent le croisement du mode de transport principal pour se rendre au travail, du lieu de travail
                (commune de résidence, autre commune, autre département…) et du sexe des actifs occupés.      
            </div>""", unsafe_allow_html=True)

            # ── Palettes ───────────────────────────────────────────────────
            MODES_ORDER = [
                "Voiture, camion, fourgonnette", "Transport en commun",
                "Marche à pied", "Deux-roues", "Pas de transport", "Autre",
            ]
            COULEURS_MODE_METRO = {
                "Voiture, camion, fourgonnette": "#3A3D44",
                "Transport en commun":           "#7A7E87",
                "Marche à pied":                 "#A2A6AE",
                "Deux-roues":                     "#C8CACF",
                "Pas de transport":               "#DDE0E3",
                "Autre":                          "#E8E8EB",
            }
            COULEURS_MODE_COMMUNE = {
                "Voiture, camion, fourgonnette": "#1B4332",
                "Transport en commun":           "#2D6A4F",
                "Marche à pied":                 "#40916C",
                "Deux-roues":                     "#74C69D",
                "Pas de transport":               "#95D5B2",
                "Autre":                          "#D8F3DC",
            }

            # ── Fonctions de calcul ───────────────────────────────────────
            def get_modal_split(df_src, annee, filter_col=None, filter_val=None):
                """Répartition modale (%). Filtre optionnel sur une colonne (ex: lieu_travail)."""
                df_y = df_src[df_src["annee"] == annee]
                if filter_col is not None:
                    df_y = df_y[df_y[filter_col] == filter_val]
                sums = df_y.groupby("mode_transport")["valeur"].sum()
                total = sums.sum()
                if total == 0:
                    return {m: 0.0 for m in MODES_ORDER}, 0
                return {m: sums.get(m, 0.0) / total * 100 for m in MODES_ORDER}, total

            def get_part_local(df_src, annee):
                """Part des actifs travaillant dans leur commune de résidence (%)."""
                df_y = df_src[df_src["annee"] == annee]
                total = df_y["valeur"].sum()
                local = df_y[df_y["lieu_travail"] == "Commune de résidence"]["valeur"].sum()
                return (local / total * 100) if total > 0 else 0.0

            def render_kpi_card_transport(label, total_actifs, split, border_color):
                tot_str = f"{int(total_actifs):,}".replace(",", "\u202f") if total_actifs > 0 else "N/D"
                pct_voiture = split.get("Voiture, camion, fourgonnette", 0)
                pct_tc      = split.get("Transport en commun", 0)
                pct_actif   = split.get("Marche à pied", 0) + split.get("Deux-roues", 0)
                st.markdown(f"""
                <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:6px solid {border_color}; background:#fff; margin-bottom:12px; padding:12px 16px;'>
                    <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:5px;'>{label}</div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
                        <div style='text-align:center;' title='Personnes ayant un emploi, résidant sur le territoire'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Actifs occupés</div>
                            <div style='font-size:15px;font-weight:800;color:#555;'>{tot_str}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Voiture</div>
                            <div style='font-size:15px;font-weight:800;color:#3A3D44;'>{pct_voiture:.2f}%</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Transport en commun</div>
                            <div style='font-size:15px;font-weight:800;color:#1565C0;'>{pct_tc:.2f}%</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Mobilités actives</div>
                            <div style='font-size:15px;font-weight:800;color:#2E7D32;'>{pct_actif:.2f}%</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── Bandeau filtres ────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Transport domicile-travail")
                fa1, fa2 = st.columns([1, 3])
                with fa1:
                    filter_row_label("Niveau géographique")
                with fa2:
                    mode_transp = st.radio(
                        "",
                        ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                        key="transp_mode", horizontal=True, label_visibility="collapsed",
                    )

                if mode_transp == "Comparaison Métropoles":
                    sel_metros_transp = st.multiselect(
                        "Métropoles à comparer", TOUTES, default=shared_default_demo(TOUTES),
                        key="transp_metros", on_change=sync_metros_demo, args=("transp_metros",),
                    )
                    targets_transp = sel_metros_transp
                else:
                    communes_dispo = sorted(COMMUNES["Grenoble"])
                    sel_communes_transp = st.multiselect(
                        "Communes de Grenoble-Alpes Métropole", communes_dispo,
                        default=shared_default_communes_demo(communes_dispo),
                        key="transp_communes", on_change=sync_communes_demo, args=("transp_communes",),
                    )
                    targets_transp = sel_communes_transp

                annees_transp = sorted(df_transport["annee"].dropna().unique().astype(int).tolist())
                annee_transp = st.selectbox(
                    "Année d'analyse", annees_transp, index=len(annees_transp) - 1, key="an_transp",
                    help="Pilote les KPI et l'ensemble des graphiques de cet onglet.",
                )

            st.markdown("---")

            if not targets_transp:
                st.warning("Sélectionnez au moins un territoire.")
                st.stop()

            n_targets = len(targets_transp)

            # ── Couleurs / mise en évidence Grenoble ───────────────────────
            if mode_transp == "Comparaison Métropoles":
                bar_colors = [COULEURS.get(t, "#888888") for t in targets_transp]
                couleurs_mode = COULEURS_MODE_METRO
            else:
                bar_colors = [PALETTE_COMMUNE[i % len(PALETTE_COMMUNE)] for i in range(n_targets)]
                couleurs_mode = COULEURS_MODE_COMMUNE

            greno_vrect = None
            if "Grenoble" in targets_transp and mode_transp == "Comparaison Métropoles":
                g_pos = targets_transp.index("Grenoble")
                greno_vrect = dict(
                    x0=g_pos - 0.45, x1=g_pos + 0.45,
                    fillcolor="rgba(255,88,77,0.10)",
                    line_color="#FF584D", line_width=1.5,
                    line_dash="dash", layer="below",
                )

            def df_filter_transp(t):
                if mode_transp == "Comparaison Métropoles":
                    return df_transport[(df_transport["metropole"] == t)]
                return df_transport[
                    (df_transport["nom_commune"] == t) & (df_transport["metropole"] == "Grenoble")
                ]

            # ── KPI ───────────────────────────────────────────────────────
            st.subheader(
                f"Indicateurs de mobilité domicile-travail en {annee_transp}",
                help=(
                    "**Actifs occupés** : personnes ayant un emploi (en activité professionnelle), "
                    "par opposition aux chômeurs et aux inactifs. Cet indicateur compte les actifs "
                    "résidant sur le territoire, quel que soit leur lieu de travail.\n\n"
                    "**Voiture / Transport en commun** : part du mode de transport principal déclaré "
                    "pour le trajet domicile-travail.\n\n"
                    "**Mobilités actives** : somme de la marche à pied et des deux-roues (vélo, "
                    "scooter, moto)."
                ),
            )
            kpi_cols = st.columns(n_targets)
            splits_by_target = {}
            for i, t in enumerate(targets_transp):
                df_t = df_filter_transp(t)
                split_t, total_t = get_modal_split(df_t, annee_transp)
                splits_by_target[t] = split_t
                with kpi_cols[i]:
                    render_kpi_card_transport(t, total_t, split_t, border_color=bar_colors[i])

            st.markdown("---")

            # ══════════════════════════════════════════════════════════════
            # GRAPHIQUE 1 : Répartition modale empilée
            # ══════════════════════════════════════════════════════════════
            st.subheader(
                "Répartition modale des trajets domicile-travail",
                help=(
                    "Part de chaque mode de transport principal utilisé par les actifs occupés pour se "
                    "rendre au travail (base 100% par territoire). La voiture reste partout majoritaire, "
                    "mais sa part varie selon le développement des réseaux de transport en commun et des "
                    "aménagements cyclables. " +
                    ("Grenoble est encadrée en rouge." if mode_transp == "Comparaison Métropoles" else "")
                ),
            )
            rows_modal = []
            for t in targets_transp:
                for mode in MODES_ORDER:
                    rows_modal.append({"Territoire": t, "Mode": mode, "Part (%)": splits_by_target[t][mode]})
            df_modal = pd.DataFrame(rows_modal)

            fig_modal = px.bar(
                df_modal, x="Territoire", y="Part (%)", color="Mode",
                barmode="stack", text_auto=".2f",
                color_discrete_map=couleurs_mode,
                category_orders={"Mode": MODES_ORDER}, height=420,
            )
            fig_modal.update_traces(
                textposition="inside", textfont_size=9,
                hovertemplate="<b>%{x}</b><br>%{fullData.name} : %{y:.2f}%<extra></extra>",
            )
            if greno_vrect:
                fig_modal.add_vrect(**greno_vrect)
            fig_modal.update_layout(
                legend=dict(orientation="h", y=1.15, title=""),
                yaxis_title="Part des actifs occupés (%)", xaxis_title="", margin=dict(t=20),
            )
            st.plotly_chart(style(fig_modal), use_container_width=True)

            with st.expander("💡 Comment interpréter ce graphique ?"):
                st.write(
                    "Ce graphique en barres empilées décompose, pour chaque territoire, la part des actifs "
                    "utilisant chaque mode de transport pour se rendre au travail. La part de voiture "
                    "(barre la plus foncée en vue métropoles) reflète à la fois la qualité du réseau de "
                    "transport en commun, le relief, l'étalement urbain et la disponibilité de pistes "
                    "cyclables. Un territoire avec une part de transport en commun ou de mobilités actives "
                    "élevée traduit généralement une politique de mobilité durable plus avancée et/ou un "
                    "tissu urbain plus dense, favorable aux déplacements courts."
                )

            st.markdown("---")

            # ══════════════════════════════════════════════════════════════
            # GRAPHIQUE 2 : Autonomie locale de l'emploi + modal des trajets de proximité
            # ══════════════════════════════════════════════════════════════
            st.subheader(
                "Trajets de proximité : autonomie locale et choix modal",
                help=(
                    "Sur les longs trajets, la voiture s'impose presque partout faute d'alternative - "
                    "les territoires se ressemblent alors beaucoup. C'est sur les trajets de proximité "
                    "(travailler dans sa propre commune) que les différences d'infrastructures "
                    "(pistes cyclables, marchabilité, réseau urbain) se révèlent vraiment."
                ),
            )

            gp1, gp2 = st.columns(2)

            with gp1:
                st.markdown(
                    "##### Part des actifs travaillant dans leur commune",
                    help=(
                        "Part des actifs occupés dont le lieu de travail est situé dans leur commune de "
                        "résidence. Un taux élevé signifie que le territoire offre suffisamment d'emplois "
                        "locaux pour limiter les déplacements pendulaires longue distance."
                    ),
                )
                rows_local = []
                for i, t in enumerate(targets_transp):
                    df_t = df_filter_transp(t)
                    pct_local = get_part_local(df_t, annee_transp)
                    rows_local.append({"Territoire": t, "Part (%)": pct_local})
                df_local = pd.DataFrame(rows_local)

                fig_local = go.Figure()
                for i, row in df_local.iterrows():
                    is_greno = (row["Territoire"] == "Grenoble" and mode_transp == "Comparaison Métropoles")
                    marker = dict(color=bar_colors[i])
                    if is_greno:
                        marker["pattern"] = dict(shape="/", fgcolor="#FF584D", fillmode="overlay", solidity=0.3, size=20)
                    fig_local.add_trace(go.Bar(
                        x=[row["Territoire"]], y=[row["Part (%)"]],
                        marker=marker, showlegend=False,
                        text=[f"{row['Part (%)']:.2f}%"], textposition="outside",
                        hovertemplate=f"<b>{row['Territoire']}</b><br>Travaille localement : %{{y:.2f}}%<extra></extra>",
                    ))
                fig_local.update_layout(
                    height=340, margin=dict(t=20, b=10),
                    yaxis=dict(title="Part des actifs (%)", gridcolor="#eee"),
                    xaxis=dict(showgrid=False),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(style(fig_local), use_container_width=True)

            with gp2:
                st.markdown(
                    "##### Choix modal pour ces trajets de proximité",
                    help=(
                        "Répartition modale calculée uniquement parmi les actifs qui travaillent dans "
                        "leur commune de résidence. Sur ces courtes distances, la voiture n'a plus de "
                        "réel avantage en temps de trajet : sa part résiduelle ici reflète directement "
                        "la qualité des aménagements piétons et cyclables du territoire."
                    ),
                )
                rows_local_modal = []
                for t in targets_transp:
                    df_t = df_filter_transp(t)
                    split_local, _ = get_modal_split(df_t, annee_transp, filter_col="lieu_travail", filter_val="Commune de résidence")
                    for mode in MODES_ORDER:
                        rows_local_modal.append({"Territoire": t, "Mode": mode, "Part (%)": split_local[mode]})
                df_local_modal = pd.DataFrame(rows_local_modal)

                fig_local_modal = px.bar(
                    df_local_modal, x="Territoire", y="Part (%)", color="Mode",
                    barmode="stack", text_auto=".2f",
                    color_discrete_map=couleurs_mode,
                    category_orders={"Mode": MODES_ORDER}, height=340,
                )
                fig_local_modal.update_traces(
                    textposition="inside", textfont_size=8,
                    hovertemplate="<b>%{x}</b><br>%{fullData.name} : %{y:.2f}%<extra></extra>",
                )
                if greno_vrect:
                    fig_local_modal.add_vrect(**greno_vrect)
                fig_local_modal.update_layout(
                    legend=dict(orientation="h", y=1.22, title="", font_size=9),
                    yaxis_title="Part (%)", xaxis_title="", margin=dict(t=20, b=10),
                )
                st.plotly_chart(style(fig_local_modal), use_container_width=True)

            with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                st.write(
                    "**Part des actifs travaillant dans leur commune (gauche)** : un taux élevé traduit "
                    "un bassin d'emploi local dynamique, qui réduit mécaniquement la dépendance aux "
                    "déplacements longue distance. Un taux faible signale une commune plutôt résidentielle, "
                    "dont les habitants doivent se déplacer ailleurs pour travailler.\n\n"
                    "**Choix modal pour ces trajets (droite)** : contrairement à la répartition modale "
                    "globale (graphique 1, où la distance moyenne masque les écarts d'infrastructures), "
                    "ce graphique isole les trajets de proximité - ceux où la voiture n'apporte plus de "
                    "gain de temps significatif. Les écarts de part de marche et de vélo entre territoires "
                    "deviennent ici beaucoup plus parlants : ils révèlent la qualité réelle de "
                    "l'aménagement cyclable et piéton, indépendamment de la géographie ou de l'étalement "
                    "urbain qui dominent le graphique global." +
                    (" Les hachures et la zone rouge identifient Grenoble." if mode_transp == "Comparaison Métropoles" else "")
                )
                
# ==============================================================================
# ONGLET 5 - MÉNAGES
# ==============================================================================
if vue == "Démographie":
    with tab5:

        data_men_ok = (df_men_age is not None) and (df_men_csp is not None)
        if not data_men_ok:
            st.info("📂 Fichiers de données sur les ménages introuvables.")
        else:
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> INSEE -
                <a href='https://www.insee.fr/fr/statistiques/8582448' target='_blank' style='color: #1C3A27;'>Accéder aux données</a>
            </div>""", unsafe_allow_html=True)

            TYPE_GROUPES = {
                "Personne seule":        lambda cols: [c for c in cols if "pers_seule" in c],
                "Couple sans enfant":    lambda cols: [c for c in cols if "cpl_sans_enf" in c],
                "Couple avec enfant(s)": lambda cols: [c for c in cols if "cpl_avec_enfant" in c or "cpl_1enf" in c],
                "Famille monoparentale": lambda cols: [c for c in cols if "fam_monoparentale" in c],
                "Autre ménage":          lambda cols: [c for c in cols if "autre_menage" in c],
            }
            CSP_GROUPES = {
                "Agriculteurs":               ["agriculteurs"],
                "Artisans / Commerçants /\nChefs d'entreprise": ["artisans", "commercants", "chef_entreprise"],
                "Cadres & Prof.\nintellectuelles sup.": [
                    "professions_liberales", "cadre_admin_fonction_pub", "prof_scientifique_sup",
                    "info_art_spectacle", "cadre_commercial", "ingenieur_cadre_tech"],
                "Professions\nintermédiaires": [
                    "prof_enseignement", "prof_inter_sante_social", "prof_inter_fonction_pub",
                    "prof_inter_admin_com", "technicien", "agent_maitrise"],
                "Employés": ["emp_fonction_pub", "securite_defense", "emp_admin_entreprise",
                             "emp_commerce", "service_particulier"],
                "Ouvriers": ["ouvrier_qualif_indus", "ouvrier_qualif_artisanal", "conducteur_transport",
                             "cariste_magasinier", "ouvrier_peu_qualif_indus", "ouvrier_peu_qualif_artisanal",
                             "ouvrier_agricole"],
                "Retraités /\nInactifs": ["retraites_inactifs", "chomeur_jamais_travaille"],
            }
            TAILLES = {
                "1 pers.": (1, "1pers"), "2 pers.": (2, "2pers"), "3 pers.": (3, "3pers"),
                "4 pers.": (4, "4pers"), "5 pers.": (5, "5pers"), "6 pers. et +": (6, "6pers_ouplus"),
            }

            def somme_colonnes(df_ent, mots_cles):
                cols = [c for c in df_ent.columns if any(k in c for k in mots_cles)]
                return df_ent[cols].sum().sum() if cols else 0

            def nb_menages_depuis_age(df_ent_age):
                cols_men = [c for c in df_ent_age.columns
                            if c.startswith("Menages_") and c not in ("CODGEO", "LIBGEO")]
                return int(df_ent_age[cols_men].sum().sum()) if cols_men else 0

            def get_population_menages(ent):
                if mode_men == "Comparaison Métropoles":
                    return epci_val(ent, "population_2022")
                else:
                    if df_gen is None:
                        return np.nan
                    comm_norm = normalize_name(ent)
                    geo = df_gen["territoire"].astype(str).str.extract(
                        r"^(Commune|EPCI)\s*:\s*(.*?)\s*\(\d+\)\s*$")
                    mask = (geo[0] == "Commune") & (geo[1].apply(normalize_name) == comm_norm)
                    rows_g = df_gen[mask]
                    if rows_g.empty:
                        return np.nan
                    v = rows_g.iloc[0].get("population_2022", np.nan)
                    return float(v) if pd.notna(v) else np.nan

            def distrib_taille(df_ent_csp):
                rows = []
                for label, (nb_pers, slug) in TAILLES.items():
                    cols = [c for c in df_ent_csp.columns if slug in c]
                    nb = df_ent_csp[cols].sum().sum() if cols else 0
                    rows.append({"Taille": label, "Ménages": int(nb)})
                df_t = pd.DataFrame(rows)
                total = df_t["Ménages"].sum()
                df_t["Part (%)"] = df_t["Ménages"] / total * 100 if total > 0 else 0
                return df_t

            def render_kpi_card(title, value, subtitle, accent_color="#1a7a4a"):
                return f"""
                <div style='display:flex;flex-direction:row;align-items:stretch;border-radius:8px;
                    overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
                    min-height:80px;border-left:6px solid {accent_color};margin-bottom:10px;'>
                    <div style='padding:10px 16px;display:flex;flex-direction:column;
                        justify-content:center;width:100%;'>
                        <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;
                            color:#666;text-transform:uppercase;'>{title}</div>
                        <div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>{value}</div>
                        <div style='color:{accent_color};font-size:11px;font-weight:700;
                            text-transform:uppercase;letter-spacing:0.05em;'>{subtitle}</div>
                    </div>
                </div>"""

            with st.container():
                filter_bar("Filtres - Ménages")
                col_geo_label, col_geo_options = st.columns([1, 3])
                with col_geo_label:
                    st.markdown("<div style='padding-top:8px;font-weight:600;font-size:14px;'>Niveau géographique</div>",
                                unsafe_allow_html=True)
                with col_geo_options:
                    mode_men = st.radio("",
                        ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                        key="men_mode", horizontal=True, label_visibility="collapsed")
                if mode_men == "Comparaison communes Grenoble-Alpes Métropole":
                    sel_communes_men = st.multiselect("Communes de Grenoble-Alpes Métropole",
                                                      sorted(COMMUNES["Grenoble"]),
                                                      default=shared_default_communes_demo(sorted(COMMUNES["Grenoble"])),
                                                      key="men_communes",
                                                      on_change=sync_communes_demo, args=("men_communes",))
                    selection_men = sel_communes_men
                else:
                    sel_metros_men = st.multiselect("Métropoles à comparer", TOUTES, default=shared_default_demo(TOUTES),
                                                    key="men_metros", on_change=sync_metros_demo, args=("men_metros",))
                    selection_men = sel_metros_men

                theme_men = st.selectbox("Thématique d'analyse",
                    ["👨‍👩‍👧 Type & taille de ménage", "🧑‍💼 CSP du chef de ménage"], key="theme_men",
                    help="**Type & taille** : Composition familiale et taille des foyers.\n\n**CSP** : Catégorie socio-professionnelle de la personne de référence du foyer (chef de ménage).")

            st.markdown("---")

            if not selection_men:
                st.warning("⚠️ Sélectionnez au moins un territoire.")
                st.stop()

            def get_df_age(ent):
                if mode_men == "Comparaison Métropoles":
                    return df_men_age[df_men_age["metropole"] == ent]
                return df_men_age[df_men_age["LIBGEO"] == ent]

            def get_df_csp(ent):
                if mode_men == "Comparaison Métropoles":
                    return df_men_csp[df_men_csp["metropole"] == ent]
                return df_men_csp[df_men_csp["LIBGEO"] == ent]

            COLORS_COMM_MEN = ["#081C15","#1B4332","#2D6A4F","#40916C","#52B788",
                               "#74C69D","#95D5B2","#B7E4C7","#D8F3DC"]

            if mode_men == "Comparaison Métropoles":
                COLOR_MAP_ENT = {e: COULEURS.get(e, "#888888") for e in selection_men}
                COLOR_SEQ_ENT = [COULEURS.get(e, "#888888") for e in selection_men]
            else:
                COLOR_MAP_ENT = {e: COLORS_COMM_MEN[i % len(COLORS_COMM_MEN)]
                                 for i, e in enumerate(selection_men)}
                COLOR_SEQ_ENT = [COLORS_COMM_MEN[i % len(COLORS_COMM_MEN)]
                                 for i in range(len(selection_men))]

            PALETTE_TYPE = ["#3A3D44", "#7A7E87", "#A2A6AE", "#C8CACF", "#E8E8EB"]
            PALETTE_CSP_GREY = ["#3A3D44", "#555A62", "#7A7E87", "#9EA2A8",
                                 "#C8CACF", "#DFE0E2", "#E8E8EB"]

            # ════════════════════════════════════════════════════════════════
            # THÈME 1 - TYPE & TAILLE DE MÉNAGE
            # ════════════════════════════════════════════════════════════════
            if "Type" in theme_men:
                cols_age = [c for c in df_men_age.columns if c.startswith("Menages_")]

                st.markdown(
                    "#### Aperçu global des ménages",
                    help="**Nombre de ménages** : total des foyers ordinaires recensés (RP 2022), calculé en sommant toutes les colonnes du fichier Menage_age_situation.\n\n"
                         "**Personnes par ménage** : ratio Population 2022 / Nombre de ménages. La moyenne nationale est d'environ 2,2 personnes par ménage en France. Un ratio élevé (> 2,5) indique un territoire avec beaucoup de familles avec enfants."
                )
                kpi_cols = st.columns(len(selection_men))
                for i, ent in enumerate(selection_men):
                    df_age_ent = get_df_age(ent)
                    nb_men = nb_menages_depuis_age(df_age_ent)
                    pop = get_population_menages(ent)
                    ratio_str = f"{pop / nb_men:.2f} pers./ménage" if nb_men > 0 and not np.isnan(pop) else "N/D"
                    with kpi_cols[i]:
                        st.markdown(render_kpi_card(ent, fmt(nb_men), ratio_str, COLOR_SEQ_ENT[i]),
                                    unsafe_allow_html=True)

                st.markdown("---")

                st.markdown(
                    "##### Distribution par taille de ménage (%)",
                    help="Répartition des ménages selon leur nombre de personnes, calculée depuis le fichier CSP×taille (colonnes Menages_Npers_*). En France : ~37% de personnes seules (1 pers.), ~33% de couples sans enfant (2 pers.). Une forte part de 4 pers. et plus caractérise un territoire à profil familial."
                )
                rows_taille = []
                for ent in selection_men:
                    df_t = distrib_taille(get_df_csp(ent))
                    df_t["Territoire"] = ent
                    rows_taille.append(df_t)
                df_taille_all = pd.concat(rows_taille, ignore_index=True) if rows_taille else pd.DataFrame()

                if not df_taille_all.empty:
                    fig_taille = px.bar(
                        df_taille_all, x="Taille", y="Part (%)", color="Territoire",
                        barmode="group", text_auto=".1f",
                        color_discrete_map=COLOR_MAP_ENT,
                        category_orders={"Taille": list(TAILLES.keys())}, height=380,
                    )
                    fig_taille.update_traces(textposition="outside", textfont_size=9)
                    
                    # Application des hachures UNIQUEMENT sur Grenoble si comparaison Métropoles
                    for trace in fig_taille.data:
                        if trace.name == "Grenoble" and mode_men == "Comparaison Métropoles":
                            trace.marker.pattern = dict(shape="/", fgcolor="#FF584D", solidity=0.3, size=20)

                    fig_taille.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                             xaxis_title="Taille du ménage",
                                             yaxis_title="Part des ménages (%)", margin=dict(t=20))
                    st.plotly_chart(style(fig_taille), use_container_width=True)

                st.markdown("---")

                c1, c2 = st.columns(2)
                rows_type = []
                for ent in selection_men:
                    df_age_ent = get_df_age(ent)
                    nb_total = df_age_ent[cols_age].sum().sum()
                    for nom, fn in TYPE_GROUPES.items():
                        cols_grp = fn(cols_age)
                        val = df_age_ent[cols_grp].sum().sum() if cols_grp else 0
                        rows_type.append({"Territoire": ent, "Type de ménage": nom,
                                          "Nombre": int(val),
                                          "Part (%)": val / nb_total * 100 if nb_total > 0 else 0})
                df_type = pd.DataFrame(rows_type)

                with c1:
                    st.markdown(
                        "##### Composition des ménages - volume",
                        help="Nombre absolu de foyers par type de composition familiale (personne seule, couple sans enfant, couple avec enfant(s), famille monoparentale, autre). Utile pour dimensionner les besoins réels en logements adaptés (studios, T3/T4, etc.) et en équipements (crèches, écoles)."
                    )
                    if not df_type.empty:
                        fig_vol = px.bar(df_type, x="Type de ménage", y="Nombre", color="Territoire",
                                         barmode="group", color_discrete_map=COLOR_MAP_ENT, height=400)
                        
                        # Application des hachures UNIQUEMENT sur Grenoble si comparaison Métropoles
                        for trace in fig_vol.data:
                            if trace.name == "Grenoble" and mode_men == "Comparaison Métropoles":
                                trace.marker.pattern = dict(shape="/", fgcolor="#FF584D", solidity=0.3, size=20)

                        fig_vol.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                             xaxis_title="", yaxis_title="Nombre de ménages",
                                             xaxis_tickangle=-15, margin=dict(t=20))
                        st.plotly_chart(style(fig_vol), use_container_width=True)

                with c2:
                    st.markdown(
                        "##### Composition des ménages - structure (%)",
                        help="Répartition en pourcentage (base 100% par territoire). Neutralise l'effet de taille pour comparer la 'sociologie' de territoires de populations très différentes. Une forte part de personnes seules caractérise les centres-villes étudiants ou vieillissants. Une forte part de couples avec enfants indique un profil périurbain ou résidentiel familial."
                    )
                    if not df_type.empty:
                        fig_pct = px.bar(df_type, x="Part (%)", y="Territoire", color="Type de ménage",
                                         orientation="h", barmode="stack", text_auto=".1f",
                                         color_discrete_sequence=PALETTE_TYPE, height=400)
                        fig_pct.update_traces(textposition="inside", textfont_size=9)
                        territoires_pct = list(dict.fromkeys(df_type["Territoire"].tolist()))
                        
                        # Graphique concerné par l'encadré en pointillé -> PAS de hachures
                        if "Grenoble" in territoires_pct and mode_men == "Comparaison Métropoles":
                            g_pos = territoires_pct.index("Grenoble")
                            fig_pct.add_hrect(y0=g_pos - 0.45, y1=g_pos + 0.45,
                                              fillcolor="rgba(255,88,77,0.10)",
                                                  line_color="#FF584D", line_width=1.5, line_dash="dash", layer="below")
                        fig_pct.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                             xaxis_title="Part des ménages (%)",
                                             yaxis_title="", margin=dict(t=20))
                        st.plotly_chart(style(fig_pct), use_container_width=True)

                with st.expander("💡 Comment interpréter ces graphiques ?"):
                    st.write(
                            "**Distribution par taille** : montre si le territoire a des petits foyers (1-2 pers.) ou des familles (4+ pers.). "
                            "En France, moyenne = **2,2 personnes/ménage**. "
                            "Beaucoup de 1 personne = profil urbain/vieillissant. Beaucoup de 4+ = profil familial.\n\n"
                            "**Volume** : besoins absolus en logements de chaque taille.\n\n"
                            "**Structure %** : compare la 'sociologie' des territoires en neutralisant la taille totale."
                        )

            # ════════════════════════════════════════════════════════════════
            # THÈME 2 - CSP DU CHEF DE MÉNAGE
            # ════════════════════════════════════════════════════════════════
            else:
                cols_csp = [c for c in df_men_csp.columns if c.startswith("Menages_")]

                rows_csp, kpi_csp = [], []
                for ent in selection_men:
                    df_age_ent  = get_df_age(ent)
                    df_csp_ent  = get_df_csp(ent)
                    nb_total_csp = df_csp_ent[cols_csp].sum().sum()
                    nb_men = nb_menages_depuis_age(df_age_ent)
                    pop = get_population_menages(ent)
                    best_grp, best_val = "N/D", 0
                    for nom_grp, mots in CSP_GROUPES.items():
                        val = somme_colonnes(df_csp_ent, mots)
                        pct = val / nb_total_csp * 100 if nb_total_csp > 0 else 0
                        rows_csp.append({"Territoire": ent, "CSP": nom_grp,
                                         "Nombre": int(val), "Part (%)": round(pct, 1)})
                        if val > best_val:
                            best_val = val
                            best_grp = nom_grp.replace("\n", " ")
                    kpi_csp.append({"ent": ent, "total": nb_men, "dominante": best_grp})
                df_csp_all = pd.DataFrame(rows_csp)

                st.markdown(
                    "#### Profil socio-professionnel des ménages",
                    help="La CSP affichée est celle de la **personne de référence du foyer** (chef de ménage), généralement la personne la plus âgée ou celle avec le revenu le plus élevé. Source : INSEE RP 2022, fichier Ménages × CSP × nombre de personnes.\n\n"
                         "**Nombre de ménages** : total des foyers recensés dans le territoire.\n\n"
                         "**CSP dominante** : la catégorie socio-professionnelle qui rassemble le plus grand nombre de ménages."
                )
                kpi_cols = st.columns(len(kpi_csp))
                for i, d in enumerate(kpi_csp):
                    with kpi_cols[i]:
                        st.markdown(render_kpi_card(d["ent"], fmt(d["total"]),
                                                    f"Majorité : {d['dominante']}",
                                                    COLOR_SEQ_ENT[i]), unsafe_allow_html=True)

                st.markdown("---")

                st.markdown(
                    "##### Structure socio-professionnelle des ménages (%)",
                    help="Répartition des ménages par grande catégorie socio-professionnelle (base 100% par territoire). Permet de comparer le profil social de territoires de tailles très différentes sur un pied d'égalité. Un écart important sur la part des cadres indique souvent un pôle d'attractivité économique ou une zone résidentielle favorisée."
                )
                if not df_csp_all.empty:
                    ordre_csp = list(CSP_GROUPES.keys())
                    n_csp = len(ordre_csp)
                    grey_csp = [f"#{v:02x}{v:02x}{v:02x}" for v in
                                [int(0x3A + (0xE8 - 0x3A) * i / (n_csp - 1)) for i in range(n_csp)]]
                    fig_pct_csp = px.bar(df_csp_all, x="Territoire", y="Part (%)", color="CSP",
                                         barmode="stack", text_auto=".1f",
                                         color_discrete_sequence=grey_csp,
                                         category_orders={"CSP": ordre_csp}, height=420)
                    fig_pct_csp.update_traces(textposition="inside", textfont_size=9)
                    territoires_csp = list(dict.fromkeys(df_csp_all["Territoire"].tolist()))
                    
                    # Graphique concerné par l'encadré en pointillé -> PAS de hachures
                    if "Grenoble" in territoires_csp and mode_men == "Comparaison Métropoles":
                        g_pos = territoires_csp.index("Grenoble")
                        fig_pct_csp.add_vrect(x0=g_pos - 0.45, x1=g_pos + 0.45,
                                              fillcolor="rgba(255,88,77,0.10)",
                                              line_color="#FF584D", line_width=1.5, line_dash="dash", layer="below")
                    fig_pct_csp.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                             yaxis_title="Part des ménages (%)",
                                             xaxis_title="", margin=dict(t=20))
                    st.plotly_chart(style(fig_pct_csp), use_container_width=True)

                st.markdown("---")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        "##### Volume par CSP (nombre de ménages)",
                        help="Nombre absolu de ménages par catégorie socio-professionnelle. Utile pour estimer les besoins en services publics : un grand nombre de ménages de retraités implique des besoins accrus en Ehpad, soins à domicile et transports adaptés ; un grand nombre de cadres signale un besoin en logements de qualité et en services haut de gamme."
                    )
                    if not df_csp_all.empty:
                        fig_vol_csp = px.bar(df_csp_all, x="Nombre", y="CSP", color="Territoire",
                                             orientation="h", barmode="group",
                                             color_discrete_map=COLOR_MAP_ENT,
                                             category_orders={"CSP": list(CSP_GROUPES.keys())}, height=420)
                        
                        # Application des hachures UNIQUEMENT sur Grenoble si comparaison Métropoles
                        for trace in fig_vol_csp.data:
                            if trace.name == "Grenoble" and mode_men == "Comparaison Métropoles":
                                trace.marker.pattern = dict(shape="/", fgcolor="#FF584D", solidity=0.30, size=20)

                        fig_vol_csp.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                                  xaxis_title="Nombre de ménages",
                                                  yaxis_title="", margin=dict(t=20))
                        st.plotly_chart(style(fig_vol_csp), use_container_width=True)

                with c2:
                    st.markdown(
                        "##### Taille moyenne des ménages par CSP",
                        help="Compare la taille moyenne des foyers selon la CSP du chef de ménage. Calcul : Σ(nb_ménages_Npers × N) / Σ(nb_ménages_Npers) pour chaque CSP. Les ménages de cadres et professions intermédiaires ont souvent plus d'enfants que les ménages d'employés, qui vivent davantage seuls ou en couple. Les retraités ont les ménages les plus petits."
                    )
                    rows_taille_csp = []
                    for ent in selection_men:
                        df_csp_ent = get_df_csp(ent)
                        for nom_grp, mots in CSP_GROUPES.items():
                            total_m, total_p = 0, 0
                            for label, (nb_pers, slug) in TAILLES.items():
                                cols_filtre = [c for c in df_csp_ent.columns
                                               if slug in c and any(k in c for k in mots)]
                                nb = df_csp_ent[cols_filtre].sum().sum() if cols_filtre else 0
                                total_m += nb
                                total_p += nb * nb_pers
                            taille_grp = total_p / total_m if total_m > 0 else np.nan
                            if not np.isnan(taille_grp):
                                rows_taille_csp.append({"Territoire": ent,
                                                        "CSP": nom_grp.replace("\n", " "),
                                                        "Taille moyenne": round(taille_grp, 2)})
                    df_taille_csp = pd.DataFrame(rows_taille_csp)
                    if not df_taille_csp.empty:
                        fig_taille_csp = px.bar(df_taille_csp, x="Taille moyenne", y="CSP", color="Territoire",
                                                orientation="h", barmode="group",
                                                color_discrete_map=COLOR_MAP_ENT,
                                                height=420, text_auto=".2f")
                        fig_taille_csp.update_traces(textposition="outside", textfont_size=9)
                        
                        # Application des hachures UNIQUEMENT sur Grenoble si comparaison Métropoles
                        for trace in fig_taille_csp.data:
                            if trace.name == "Grenoble" and mode_men == "Comparaison Métropoles":
                                trace.marker.pattern = dict(shape="/", fgcolor="#FF584D", solidity=0.30, size=20)

                        fig_taille_csp.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, title=""),
                                                     xaxis_title="Personnes par ménage (moyenne)",
                                                     yaxis_title="", margin=dict(t=20),
                                                     xaxis=dict(range=[0, 5]))
                        st.plotly_chart(style(fig_taille_csp), use_container_width=True)

                with st.expander("💡 Guide d'interprétation des CSP"):
                    st.write(
                        "La **catégorie socio-professionnelle (CSP)** affichée est celle de la **personne de référence du ménage** (d’après la nomenclature PCS 2020 de l’INSEE). "
                        "Les 7 grandes catégories regroupent les 30+ sous-catégories de la profession de cette personne.\n\n"
                        
                        "- **Cadres & Prof. sup.** : emplois à haut niveau de qualification et de revenus, souvent associés à des ménages bi‑actifs et plus aisés.\n"
                        "- **Prof. intermédiaires** : ingénieurs, enseignants, techniciens, cadres moyens - cœur du tissu urbain et des services publics.\n"
                        "- **Employés** : agents de service, de bureau, de la fonction publique, sécurité ; souvent des ménages plus petits.\n"
                        "- **Ouvriers** : ouvriers, conducteurs, ouvriers agricoles, souvent dans des ménages plus nombreux.\n"
                        "- **Retraités / Inactifs** : retraités et chômeurs longue durée, en général majoritaires dans les communes vieillissantes.\n\n"
                        
                        "La **taille moyenne par CSP** renvoie à des modes de vie typiques : ouvriers et agriculteurs ont souvent plus d’enfants, "
                        "tandis que retraités et employés vivent plus souvent seuls ou en couple sans enfant. "
                        "Comparer ces tailles entre territoires pour une même CSP met en évidence des différences sociales locales."
                    )
# ==============================================================================
# ONGLET 6 - LOGEMENT
# ==============================================================================


if vue == "Démographie":
    with tab6:

        if df_log is None and df_social is None:
            st.info("📂 Fichiers `logements_metropoles_clean.csv` et `rpls_metropoles_clean.csv` introuvables.")
        else:
            # ── Normalisation défensive du nom "Saint-Étienne" ────────────────
            # (les deux fichiers sources utilisent parfois "Saint-Etienne" sans accent)
            if df_log is not None and "metropole" in df_log.columns:
                df_log = df_log.copy()
                df_log["metropole"] = df_log["metropole"].replace({"Saint-Etienne": "Saint-Étienne"})
            if df_social is not None and "metropole" in df_social.columns:
                df_social = df_social.copy()
                df_social["metropole"] = df_social["metropole"].replace({"Saint-Etienne": "Saint-Étienne"})

            # ── Encart Sources ─────────────────────────────────────────────
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Sources :</strong> INSEE<br><br>
                🏠 <b>Résidences principales (indice de peuplement):</b> recensements 2011 / 2016 / 2022 :
                <a href='https://catalogue-donnees.insee.fr/fr/catalogue/recherche/DS_RP_LOGEMENT_COMPL' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br><br>
                🏢 <b>Logements sociaux (RPLS):</b> millésime unique 2024 :
                <a href='https://www.insee.fr/fr/statistiques/8736658' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br><br>
                <em>Les deux sources portant sur des années différentes, elles sont présentées dans deux thématiques distinctes.</em>
            </div>""", unsafe_allow_html=True)

            # ─────────────────────────────────────────────────────────────
            # PALETTES DE COULEURS - fonction générique gris/vert
            # ─────────────────────────────────────────────────────────────
            def build_grey_or_green_palette(categories, mode):
                """
                Génère une palette de N nuances pour styliser une variable
                catégorielle (niveaux d'occupation, dispositifs de financement,
                tranches d'ancienneté...) :
                - nuances de GRIS en vue "Comparaison Métropoles"
                - nuances de VERT en vue "Comparaison communes..."

                Les couleurs sont échantillonnées de façon égale le long de
                l'échelle, de la plus foncée à la plus claire, dans l'ordre
                de la liste `categories` fournie. Retourne un dict
                {catégorie: couleur_hex}.
                """
                GREY_SCALE  = ["#2B2E33", "#3A3D44", "#555A62", "#7A7E87",
                               "#9EA2A8", "#C8CACF", "#DDE0E3", "#E8E8EB"]
                GREEN_SCALE = ["#081C15", "#1B4332", "#2D6A4F", "#40916C",
                               "#52B788", "#74C69D", "#95D5B2", "#B7E4C7", "#D8F3DC"]
                scale = GREY_SCALE if mode == "Comparaison Métropoles" else GREEN_SCALE
                n = len(categories)
                return {
                    cat: scale[int(i * (len(scale) - 1) / max(n - 1, 1))]
                    for i, cat in enumerate(categories)
                }

            # Texte d'aide réutilisé sur plusieurs graphiques du thème 1
            HELP_INDICE = (
                "L'indice de peuplement de l'INSEE mesure l'adéquation entre la taille du logement "
                "et la composition du ménage qui y réside.\n\n"
                "Il compare :\n"
                "- Le nombre de pièces réelles du logement.\n"
                "- Le nombre de pièces théoriquement nécessaires.\n\n"
            )

            # ═════════════════════════════════════════════════════════════
            # DÉFINITIONS - THÈME 1 : RÉSIDENCES PRINCIPALES (PEUPLEMENT)
            # ═════════════════════════════════════════════════════════════

            def get_log_data_pct(df_src, annee):
                """
                Calcule, pour un sous-ensemble de données (déjà filtré sur un
                territoire), la répartition en % des 6 niveaux d'occupation
                officiels INSEE pour une année donnée.

                Retourne :
                - vals   : liste des % (dans l'ordre des 6 niveaux)
                - labels : liste des libellés correspondants
                - total_rp : nombre total de résidences principales (volume brut)
                - kpis   : dict agrégé {norme, surocc, sousocc} en %
                """
                df_year = df_src[df_src["annee"] == annee]
                sums = df_year.groupby("indicateur_occupation")["valeur"].sum()
                total_rp = sums.sum()

                # Correspondance code technique INSEE -> libellé lisible
                labels_codes = [
                    ("VSEV_UNDER_OCC", "Sous-occupation très accentuée"),
                    ("SEV_UNDER_OCC", "Sous-occupation accentuée"),
                    ("MOD_UNDER_OCC", "Sous-occupation modérée"),
                    ("STD_OCC", "Occupation dans la norme"),
                    ("MOD_OVER_OCC", "Suroccupation modérée"),
                    ("SEV_OVER_OCC", "Suroccupation accentuée"),
                ]

                vals, labels = [], []
                kpis = {"norme": 0.0, "surocc": 0.0, "sousocc": 0.0}

                for code, label in labels_codes:
                    val_abs = sums.get(code, 0.0)
                    pct = (val_abs / total_rp * 100) if total_rp > 0 else 0.0
                    vals.append(pct)
                    labels.append(label)
                    # Agrégation en 3 grandes masses pour les KPI / graphique macro
                    if code == "STD_OCC":
                        kpis["norme"] += pct
                    elif "OVER" in code:
                        kpis["surocc"] += pct
                    elif "UNDER" in code:
                        kpis["sousocc"] += pct

                return vals, labels, total_rp, kpis

            def build_macro_stacked_chart(territories, df_filtered_fn, annee,
                                           group_name="Territoire", highlight_grenoble=False,
                                           couleurs_macro=None):
                """
                Construit le graphique "Équilibre macro-synthétique des parcs" :
                une barre horizontale empilée par territoire, regroupant les
                6 niveaux d'occupation en 3 grandes masses (sous-occupation,
                norme, suroccupation).

                Paramètre couleurs_macro : dict {catégorie: couleur} fourni par
                l'appelant (gris en vue Métropoles, vert en vue Communes).

                Paramètre highlight_grenoble : si True (vue Métropoles), encadre
                la ligne de Grenoble avec un rectangle rouge pointillé. Comme ce
                graphique est en orientation horizontale (territoires sur l'axe Y),
                on utilise un add_hrect (et non vrect) pour cibler la bonne ligne.
                """
                data_list = []
                for t in territories:
                    df_t = df_filtered_fn(t)
                    _, _, tot, kpis = get_log_data_pct(df_t, annee)
                    if tot > 0:
                        data_list.append({
                            group_name: t,
                            "Sous-occupation globale": kpis["sousocc"],
                            "Dans la norme": kpis["norme"],
                            "Suroccupation globale": kpis["surocc"],
                        })
                df_macro = pd.DataFrame(data_list)
                if df_macro.empty:
                    return None

                # Une trace par grande masse (empilées horizontalement)
                fig = go.Figure()
                for cat in ["Sous-occupation globale", "Dans la norme", "Suroccupation globale"]:
                    fig.add_trace(go.Bar(
                        name=cat, y=df_macro[group_name], x=df_macro[cat], orientation="h",
                        marker_color=couleurs_macro[cat],
                        hovertemplate=f"<b>%{{y}}</b><br>{cat} : <b>%{{x:.1f}}%</b><extra></extra>",
                    ))

                # Mise en évidence de Grenoble : on retrouve sa position dans
                # l'ordre RÉEL des barres affichées (après filtrage des tot=0),
                # puis on dessine un rectangle horizontal (hrect) centré sur sa ligne.
                if highlight_grenoble and "Grenoble" in df_macro[group_name].tolist():
                    g_pos = df_macro[group_name].tolist().index("Grenoble")
                    fig.add_hrect(
                        y0=g_pos - 0.4, y1=g_pos + 0.4,
                        fillcolor="rgba(255,88,77,0.10)",
                        line_color="#FF584D", line_width=1.5,
                        line_dash="dash", layer="below",
                    )

                fig.update_layout(
                    barmode="stack",
                    xaxis=dict(title="Pourcentage du parc (%)", range=[0, 100], showgrid=True, gridcolor="#eee"),
                    yaxis=dict(title=""),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    height=130 + (len(territories) * 38),
                    margin=dict(t=10, b=40, l=120, r=20),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                )
                return fig

            def build_bar_log_pct(df_src, label_entity, annee, x_max=None, highlight=False, couleurs_occupation=None):
                """
                Construit le graphique "Profils détaillés par niveau d'occupation"
                pour UN territoire : une barre horizontale listant les 6 niveaux
                d'occupation (un petit multiple est généré par territoire dans
                la boucle d'affichage).

                Paramètre couleurs_occupation : dict {catégorie: couleur} fourni
                par l'appelant (gris en vue Métropoles, vert en vue Communes).

                Paramètre highlight : si True (territoire = Grenoble en vue
                Métropoles), encadre l'intégralité du panneau avec un vrect
                rouge pointillé couvrant toute la largeur du graphique.
                """
                vals, labels, _, _ = get_log_data_pct(df_src, annee)
                if x_max is None:
                    x_max = max(vals) * 1.15 if vals else 100
                colors_list = [couleurs_occupation.get(lbl, "#888") for lbl in labels]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=labels, x=vals, orientation="h", marker=dict(color=colors_list),
                    hovertemplate=f"<b>{label_entity}</b><br>%{{y}}<br>Part : %{{x:.2f}}%<extra></extra>",
                ))

                # Encadrement de tout le panneau (et non d'une seule barre) :
                # comme chaque figure ne contient qu'un seul territoire, le vrect
                # couvre x0=0 à x1=x_max pour entourer visuellement tout le graphique.
                if highlight:
                    fig.add_vrect(
                        x0=0, x1=x_max,
                        fillcolor="rgba(255,88,77,0.06)",
                        line_color="#FF584D", line_width=2,
                        line_dash="dash", layer="below",
                    )

                fig.update_layout(
                    xaxis=dict(title="% des résidences principales", range=[0, x_max], showgrid=True, gridcolor="#eee"),
                    yaxis=dict(title="", tickfont_size=10, categoryorder="array", categoryarray=labels),
                    title=dict(text=f"<b>{label_entity}</b>", font_size=12, x=0.5, xanchor="center"),
                    height=280, margin=dict(t=40, b=40, l=150, r=20),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                )
                return fig

            def render_kpi_card_peuplement(label, tot_rp, kpis, border_color):
                """Affiche la carte KPI (HTML) du thème 1 : volume RP + les 3 grandes masses."""
                tot_str = f"{int(tot_rp):,}".replace(",", "\u202f") if tot_rp > 0 else "N/D"
                st.markdown(f"""
                <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:6px solid {border_color}; background:#fff; margin-bottom:12px; padding:12px 16px;'>
                    <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:5px;'>{label}</div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Total RP</div>
                            <div style='font-size:15px;font-weight:800;color:#555;'>{tot_str}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Dans la norme</div>
                            <div style='font-size:15px;font-weight:800;color:#757575;'>{kpis['norme']:.1f}%</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Suroccupation</div>
                            <div style='font-size:15px;font-weight:800;color:#E65100;'>{kpis['surocc']:.1f}%</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Sous-occupation</div>
                            <div style='font-size:15px;font-weight:800;color:#1E88E5;'>{kpis['sousocc']:.1f}%</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ═════════════════════════════════════════════════════════════
            # DÉFINITIONS - THÈME 2 : LOGEMENTS SOCIAUX (RPLS)
            # ═════════════════════════════════════════════════════════════

            def get_social_metrics(df_s, filter_col, filter_val):
                """
                Agrège les indicateurs RPLS pour un territoire (métropole ou
                commune), en pondérant chaque commune par son nombre de
                logements sociaux (moyenne pondérée plutôt que moyenne simple,
                pour ne pas sur-représenter les petites communes).

                Retourne None si le territoire n'a aucun parc social recensé.
                """
                df_sub = df_s[df_s[filter_col] == filter_val]
                if df_sub.empty:
                    return None

                weights = df_sub["nb_logements_sociaux"]
                w_sum = weights.sum()

                def wavg(col):
                    """Moyenne pondérée par nb_logements_sociaux (repli sur moyenne simple si poids nul)."""
                    if w_sum == 0:
                        return df_sub[col].mean()
                    return (df_sub[col] * weights).sum() / w_sum

                return {
                    "nb_soc":              w_sum,
                    "n_communes":          len(df_sub),
                    "taux_vacance":        wavg("taux_vacance"),
                    "taux_rotation":       wavg("taux_rotation"),
                    "loyer_median":        wavg("loyer_median"),
                    "loyer_q1":            wavg("loyer_q1"),
                    "loyer_q3":            wavg("loyer_q3"),
                    "part_T1":             wavg("part_T1"),
                    "part_T2":             wavg("part_T2"),
                    "part_T3":             wavg("part_T3"),
                    "part_T4":             wavg("part_T4"),
                    "part_T5plus":         wavg("part_T5plus"),
                    "part_PLAI":           wavg("part_PLAI"),
                    "part_HLM_avant_1977": wavg("part_HLM_avant_1977"),
                    "part_HLM_apres_1977": wavg("part_HLM_apres_1977"),
                    "part_PLS":            wavg("part_PLS"),
                    "part_PLI":            wavg("part_PLI"),
                    "part_avant_1949":     wavg("part_avant_1949"),
                    "part_1949_1975":      wavg("part_1949_1975"),
                    "part_1976_1988":      wavg("part_1976_1988"),
                    "part_1989_2000":      wavg("part_1989_2000"),
                    "part_2001_2013":      wavg("part_2001_2013"),
                    "part_apres_2013":     wavg("part_apres_2013"),
                }

            def get_total_rp(df_log_src, filter_col, filter_val, annee_ref):
                """Renvoie le total des résidences principales (df_log) pour servir de dénominateur au taux de logement social."""
                df_sub = df_log_src[
                    (df_log_src[filter_col] == filter_val) & (df_log_src["annee"] == annee_ref)
                ]
                return df_sub["valeur"].sum()

            def render_kpi_card_social(label, stats, total_rp, border_color):
                """Affiche la carte KPI (HTML) du thème 2 : volume social, taux, loyer médian, vacance."""
                if stats is None:
                    # Cas commune/métropole sans aucun parc social recensé dans le RPLS
                    st.markdown(f"""
                    <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                        border-left:6px solid {border_color}; background:#fff;
                        margin-bottom:12px; padding:12px 16px;min-height:120px;
                        display:flex;flex-direction:column;justify-content:center;'>
                        <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px;'>{label}</div>
                        <div style='font-size:12px;color:#888;'>Aucun parc social recensé</div>
                    </div>""", unsafe_allow_html=True)
                    return

                nb_soc_str = f"{int(stats['nb_soc']):,}".replace(",", "\u202f")
                taux_soc   = (stats["nb_soc"] / total_rp * 100) if total_rp > 0 else float("nan")
                taux_soc_str = f"{taux_soc:.1f}%" if total_rp > 0 else "N/D"
                loyer_str  = f"{stats['loyer_median']:.2f} €/m²" if pd.notna(stats["loyer_median"]) else "N/D"
                vacance_str = f"{stats['taux_vacance']:.1f}%" if pd.notna(stats["taux_vacance"]) else "N/D"

                st.markdown(f"""
                <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:6px solid {border_color}; background:#fff; margin-bottom:12px; padding:12px 16px;'>
                    <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:5px;'>{label}</div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
                        <div style='text-align:center;' title='Nombre de logements sociaux (RPLS 2024)'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Logements sociaux</div>
                            <div style='font-size:15px;font-weight:800;color:#555;'>{nb_soc_str}</div>
                        </div>
                        <div style='text-align:center;' title='Part du parc social parmi les résidences principales (RP 2022)'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Taux Log. Social</div>
                            <div style='font-size:15px;font-weight:800;color:#2E7D32;'>{taux_soc_str}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Loyer médian</div>
                            <div style='font-size:15px;font-weight:800;color:#1565C0;'>{loyer_str}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Taux vacance</div>
                            <div style='font-size:15px;font-weight:800;color:#C62828;'>{vacance_str}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ─────────────────────────────────────────────────────────────
            # BANDEAU FILTRES
            # ─────────────────────────────────────────────────────────────
            # Filtre 1 : niveau géographique (Métropoles vs communes Grenoble)
            # Filtre 2 : sélection des territoires à comparer
            # Filtre 3 : thématique d'analyse (Résidences principales / Logements sociaux)
            # Filtre 4 : année (uniquement pertinent pour le thème "Résidences principales")
            with st.container():
                filter_bar("Filtres - Logement")
                fa1, fa2 = st.columns([1, 3])
                with fa1:
                    filter_row_label("Niveau géographique")
                with fa2:
                    mode_log = st.radio(
                        "",
                        ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                        key="log_mode", horizontal=True, label_visibility="collapsed",
                    )

                if mode_log == "Comparaison Métropoles":
                    sel_metros_log = st.multiselect(
                        "Métropoles à comparer", TOUTES, default=shared_default_demo(TOUTES),
                        key="log_metros", on_change=sync_metros_demo, args=("log_metros",),
                    )
                    targets_log = sel_metros_log
                else:
                    communes_dispo = sorted(COMMUNES["Grenoble"])
                    sel_communes_log = st.multiselect(
                        "Communes de Grenoble-Alpes Métropole", communes_dispo,
                        default=shared_default_communes_demo(communes_dispo),
                        key="log_communes", on_change=sync_communes_demo, args=("log_communes",),
                    )
                    targets_log = sel_communes_log

                fb1, fb2 = st.columns(2)
                with fb1:
                    theme_log = st.selectbox(
                        "Thématique d'analyse",
                        ["🏠 Résidences principales (Indice de peuplement)",
                         "🏢 Logements sociaux (Parc locatif social)"],
                        key="log_theme",
                        help=(
                            "**Résidences principales** : indice de peuplement INSEE "
                            "(adéquation taille du logement / composition du ménage), "
                            "millésimes 2011/2016/2022.\n\n"
                            "**Logements sociaux** : parc locatif social (RPLS), "
                            "millésime unique 2024 (typologie, financement, ancienneté, loyers)."
                        ),
                    )

                annees_dispo = sorted(df_log["annee"].dropna().unique().astype(int).tolist()) if df_log is not None else []
                annee_ref    = max(annees_dispo) if annees_dispo else None

                # Le sélecteur d'année n'a de sens que pour le thème 1
                # (le RPLS n'a qu'un seul millésime, 2024)
                if "Résidences principales" in theme_log:
                    with fb2:
                        annee_log = st.selectbox(
                            "Année d'analyse", annees_dispo,
                            index=len(annees_dispo) - 1, key="an_log",
                        )
                else:
                    with fb2:
                        st.markdown(
                            "<div style='padding-top:28px;font-size:13px;color:#666;'>"
                            "📅 Données RPLS - millésime unique <b>2024</b></div>",
                            unsafe_allow_html=True,
                        )

            st.markdown("---")

            if not targets_log:
                st.warning("Sélectionnez au moins un territoire.")
                st.stop()

            # ─────────────────────────────────────────────────────────────
            # Couleurs / mise en évidence Grenoble
            # ─────────────────────────────────────────────────────────────
            # bar_colors : une couleur par territoire (gris/COULEURS en vue
            # Métropoles, dégradé vert PALETTE_COMMUNE en vue Communes).
            # greno_vrect : rectangle rouge pointillé utilisé pour les
            # graphiques à AXE X catégoriel (territoires alignés sur x),
            # comme fig_fin / fig_age dans le thème 2 plus bas.
            n_targets = len(targets_log)
            if mode_log == "Comparaison Métropoles":
                bar_colors = [COULEURS.get(t, "#888888") for t in targets_log]
            else:
                bar_colors = [PALETTE_COMMUNE[i % len(PALETTE_COMMUNE)] for i in range(n_targets)]

            greno_vrect = None
            if "Grenoble" in targets_log and mode_log == "Comparaison Métropoles":
                g_pos = targets_log.index("Grenoble")
                greno_vrect = dict(
                    x0=g_pos - 0.45, x1=g_pos + 0.45,
                    fillcolor="rgba(255,88,77,0.10)",
                    line_color="#FF584D", line_width=1.5,
                    line_dash="dash", layer="below",
                )

            # Booléen pratique : passé à build_macro_stacked_chart (hrect interne)
            # et à build_bar_log_pct (vrect interne, calculé territoire par territoire)
            highlight_grenoble_actif = (mode_log == "Comparaison Métropoles")

            # ── Palettes catégorielles dynamiques (gris Métropoles / vert Communes) ──
            # Calculées ICI, après lecture de mode_log, et utilisées par les
            # fonctions de graphiques définies plus haut (closures résolues à
            # l'appel, pas à la définition).
            OCCUPATION_ORDER = [
                "Suroccupation accentuée", "Suroccupation modérée",
                "Occupation dans la norme", "Sous-occupation modérée",
                "Sous-occupation accentuée", "Sous-occupation très accentuée"]
            MACRO_ORDER = ["Suroccupation globale", "Dans la norme", "Sous-occupation globale"]

            COULEURS_OCCUPATION = build_grey_or_green_palette(OCCUPATION_ORDER, mode_log)
            COULEURS_MACRO      = build_grey_or_green_palette(MACRO_ORDER, mode_log)

            # ═════════════════════════════════════════════════════════════
            # THÈME 1 - RÉSIDENCES PRINCIPALES (INDICE DE PEUPLEMENT)
            # ═════════════════════════════════════════════════════════════
            if "Résidences principales" in theme_log:

                if df_log is None:
                    st.info("📂 Fichier `logements_metropoles_clean.csv` introuvable.")
                    st.stop()

                # Fonction de filtrage du dataframe selon le mode (métropole/commune)
                if mode_log == "Comparaison Métropoles":
                    def df_filter_peuplement(t):
                        return df_log[(df_log["metropole"] == t) & (df_log["annee"] == annee_log)]
                else:
                    def df_filter_peuplement(t):
                        return df_log[
                            (df_log["nom_commune"] == t) &
                            (df_log["metropole"] == "Grenoble") &
                            (df_log["annee"] == annee_log)
                        ]

                group_label = "Métropole" if mode_log == "Comparaison Métropoles" else "Commune"

                # ── KPI ──────────────────────────────────────────────────
                st.subheader(f"Indicateurs synthétiques de peuplement en {annee_log}")
                kpi_cols = st.columns(n_targets)
                for i, t in enumerate(targets_log):
                    df_t = df_filter_peuplement(t)
                    _, _, tot, kpis_t = get_log_data_pct(df_t, annee_log)
                    with kpi_cols[i]:
                        render_kpi_card_peuplement(t, tot, kpis_t, border_color=bar_colors[i])

                st.markdown("---")

                # ── GRAPH 1 : MACRO STACKED ────────────────────────────────
                # Mise en évidence Grenoble : hrect interne à la fonction
                # (highlight_grenoble=True déclenche add_hrect sur sa ligne)
                st.subheader(
                    "Équilibre macro-synthétique des parcs",
                    help=HELP_INDICE + "\n\nCe graphique regroupe les indices en 3 grandes masses (Sous-occupation, Norme, Suroccupation).",
                )
                fig_macro = build_macro_stacked_chart(
                    territories=targets_log,
                    df_filtered_fn=df_filter_peuplement,
                    annee=annee_log,
                    group_name=group_label,
                    highlight_grenoble=highlight_grenoble_actif,
                    couleurs_macro=COULEURS_MACRO,
                )
                if fig_macro:
                    st.plotly_chart(style(fig_macro), use_container_width=True)
                else:
                    st.info("Aucune donnée disponible pour cette sélection et cette année.")

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.markdown(
                        "**Comprendre les grandes masses de peuplement :**\n\n"
                        "- **Sous-occupation globale** (nuance la plus foncée) : reflète souvent des "
                        "territoires à forte proportion de maisons individuelles ou marqués par le "
                        "vieillissement démographique (ex : couples de retraités restés seuls dans la "
                        "grande maison familiale après le départ des enfants).\n\n"
                        "- **Dans la norme** (nuance intermédiaire) : le nombre de pièces correspond aux "
                        "besoins théoriques du ménage - situation d'équilibre.\n\n"
                        "- **Suroccupation globale** (nuance la plus claire) : révèle des zones de fortes "
                        "tensions immobilières ou des spécificités de peuplement (parcs denses, forte "
                        "présence d'étudiants en petits studios ou de familles nombreuses contraintes de "
                        "vivre dans des espaces trop exigus). " +
                        ("La ligne rouge encadre Grenoble." if mode_log == "Comparaison Métropoles" else "")
                    )

                st.markdown("---")

                # ── GRAPH 2 : PROFILS DÉTAILLÉS ────────────────────────────
                # Petit multiple : une figure par territoire. Mise en évidence
                # Grenoble : vrect interne à build_bar_log_pct (highlight=True)
                # qui encadre tout le panneau.
                st.subheader(
                    "Profils détaillés par niveau d'occupation",
                    help="Décomposition fine selon la nomenclature officielle de l'INSEE en 6 niveaux.",
                )
                all_maxes = []
                for t in targets_log:
                    df_t = df_filter_peuplement(t)
                    vals, _, _, _ = get_log_data_pct(df_t, annee_log)
                    if vals:
                        all_maxes.append(max(vals))
                # Échelle X partagée entre tous les petits multiples pour
                # permettre une comparaison visuelle directe des hauteurs de barres
                shared_x_max = max(all_maxes) * 1.10 if all_maxes else 100

                ncols = min(n_targets, 3)
                rows_pyr = [targets_log[i:i + ncols] for i in range(0, n_targets, ncols)]
                for row in rows_pyr:
                    cols = st.columns(len(row))
                    for j, t in enumerate(row):
                        df_t = df_filter_peuplement(t)
                        is_greno = (t == "Grenoble" and highlight_grenoble_actif)
                        fig = build_bar_log_pct(
                            df_t, t, annee_log, x_max=shared_x_max, highlight=is_greno,
                            couleurs_occupation=COULEURS_OCCUPATION,
                        )
                        with cols[j]:
                            st.plotly_chart(style(fig, 30), use_container_width=True)

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.markdown("""
                    | Code Indicateur | Signification officielle | Explication & Exemple |
                    | :--- | :--- | :--- |
                    | **VSEV_UNDER_OCC** | Sous-occupation très accentuée | Le logement est beaucoup plus grand que nécessaire (ex : 1 personne seule dans un T5). |
                    | **SEV_UNDER_OCC** | Sous-occupation accentuée | Au moins 2 pièces de plus que le besoin théorique (ex : couple dans un T4+). |
                    | **MOD_UNDER_OCC** | Sous-occupation modérée | Une pièce excédentaire par rapport à la norme (ex : couple seul dans un T3). |
                    | **STD_OCC** | Occupation dans la norme | Le nombre de pièces correspond exactement aux besoins (ex : couple seul dans un T2). |
                    | **MOD_OVER_OCC** | Suroccupation modérée | Il manque une pièce (ex : couple avec deux enfants dans un T3). |
                    | **SEV_OVER_OCC** | Suroccupation accentuée | Alerte critique : plusieurs pièces manquantes par rapport aux besoins du ménage. |
                    """)

            # ═════════════════════════════════════════════════════════════
            # THÈME 2 - LOGEMENTS SOCIAUX (RPLS 2024)
            # ═════════════════════════════════════════════════════════════
            else:

                if df_social is None:
                    st.info("📂 Fichier `rpls_metropoles_clean.csv` introuvable.")
                    st.stop()

                # ── Garde-fou : vérifie que le fichier a été correctement parsé ─────
                # (protège contre un échec du sniffer pandas qui renverrait un
                # DataFrame à une seule colonne contenant tout l'en-tête)
                required_cols = {"metropole", "nom_commune", "nb_logements_sociaux"}
                if not required_cols.issubset(df_social.columns):
                    st.error(
                        "⚠️ Le fichier `rpls_metropoles_clean.csv` n'a pas été lu correctement "
                        f"(colonnes trouvées : {df_social.columns.tolist()}). "
                        "Vérifiez que `charger_log_social()` utilise `sep=\",\"` et non `sep=None`."
                    )
                    st.stop()

                if mode_log == "Comparaison Métropoles":
                    filter_col_social = "metropole"
                else:
                    df_social_view = df_social[df_social["metropole"] == "Grenoble"]

                # Collecte des stats agrégées RPLS + dénominateur RP par territoire
                stats_by_target = {}
                rp_by_target = {}
                for t in targets_log:
                    if mode_log == "Comparaison Métropoles":
                        stats_by_target[t] = get_social_metrics(df_social, "metropole", t)
                        rp_by_target[t] = get_total_rp(df_log, "metropole", t, annee_ref) if df_log is not None else 0
                    else:
                        stats_by_target[t] = get_social_metrics(df_social_view, "nom_commune", t)
                        rp_by_target[t] = get_total_rp(df_log, "nom_commune", t, annee_ref) if df_log is not None else 0

                # Territoires avec / sans données RPLS exploitables
                entities_with_data = [t for t in targets_log if stats_by_target[t] is not None]
                entities_no_data   = [t for t in targets_log if stats_by_target[t] is None]

                # ── KPI ──────────────────────────────────────────────────
                st.subheader(
                    "Indicateurs du parc locatif social (RPLS 2024)",
                    help=(
                        "**Logements sociaux** : nombre total de logements locatifs sociaux recensés.\n\n"
                        "**Taux Log. Social** : part du parc social parmi les résidences principales "
                        f"(référence : RP {annee_ref}).\n\n"
                        "**Loyer médian** : loyer médian au m² du parc social.\n\n"
                        "**Taux vacance** : part de logements sociaux vacants (tous types confondus)."
                    ),
                )
                kpi_cols = st.columns(n_targets)
                for i, t in enumerate(targets_log):
                    with kpi_cols[i]:
                        render_kpi_card_social(t, stats_by_target[t], rp_by_target.get(t, 0), border_color=bar_colors[i])

                if entities_no_data:
                    st.caption(
                        "ℹ️ Aucun parc social recensé (RPLS) pour : " + ", ".join(entities_no_data)
                    )

                if not entities_with_data:
                    st.warning("Aucune donnée RPLS disponible pour cette sélection.")
                    st.stop()

                st.markdown("---")

                # ── GRAPH 1 / 2 : Taux logement social + Typologie ─────────
                gc1, gc2 = st.columns(2)

                with gc1:
                    st.subheader(
                        "Taux de logement social",
                        help=(
                            "Part du parc locatif social (RPLS 2024) parmi l'ensemble des résidences "
                            f"principales du territoire (RP {annee_ref}, INSEE). "
                            "Un taux élevé indique une offre sociale importante au regard du parc total. "
                            "La loi SRU fixe un objectif de 20 à 25 % selon les communes concernées."
                        ),
                    )
                    rows_taux = []
                    for t in entities_with_data:
                        rp = rp_by_target.get(t, 0)
                        nb_soc = stats_by_target[t]["nb_soc"]
                        taux = (nb_soc / rp * 100) if rp > 0 else None
                        if taux is not None:
                            rows_taux.append({"Territoire": t, "Taux (%)": taux})
                    df_taux = pd.DataFrame(rows_taux)

                    if not df_taux.empty:
                        fig_taux = go.Figure()
                        for i, t in enumerate(targets_log):
                            if t not in df_taux["Territoire"].values:
                                continue
                            val = df_taux.loc[df_taux["Territoire"] == t, "Taux (%)"].iloc[0]
                            marker = dict(color=bar_colors[i])
                            # Hachures conservées ici (couleurs de territoire, non concerné par la modification)
                            if t == "Grenoble" and mode_log == "Comparaison Métropoles":
                                marker["pattern"] = dict(
                                    shape="/", fgcolor="#FF584D", fillmode="overlay",
                                    solidity=0.3, size=20,
                                )
                            fig_taux.add_trace(go.Bar(
                                x=[t], y=[val], marker=marker, showlegend=False,
                                text=[f"{val:.1f}%"], textposition="outside",
                                hovertemplate=f"<b>{t}</b><br>Taux logement social : %{{y:.1f}}%<extra></extra>",
                            ))
                        fig_taux.add_hline(y=20, line_dash="dot", line_color="#888",
                                           annotation_text="Seuil SRU 20%", annotation_position="top left")
                        fig_taux.update_layout(
                            height=340, margin=dict(t=20, b=10),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            yaxis=dict(title="% des résidences principales", gridcolor="#eee"),
                            xaxis=dict(showgrid=False),
                        )
                        st.plotly_chart(style(fig_taux), use_container_width=True)
                    else:
                        st.info("Données insuffisantes pour calculer le taux de logement social.")

                with gc2:
                    st.subheader(
                        "Typologie du parc social (T1 à T5+)",
                        help=(
                            "Répartition du parc locatif social selon le nombre de pièces. "
                            "Une forte part de petits logements (T1/T2) indique un parc adapté aux "
                            "personnes seules ou aux étudiants. Une forte part de T4/T5+ indique un "
                            "parc orienté vers les familles nombreuses."
                        ),
                    )
                    categories = ["T1", "T2", "T3", "T4", "T5+"]
                    code_map = {"T1": "part_T1", "T2": "part_T2", "T3": "part_T3",
                                "T4": "part_T4", "T5+": "part_T5plus"}
                    fig_typo = go.Figure()
                    for i, t in enumerate(targets_log):
                        st_t = stats_by_target[t]
                        if st_t is None:
                            continue
                        y_vals = [st_t[code_map[c]] for c in categories]
                        marker = dict(color=bar_colors[i])
                        # Hachures conservées ici (couleurs de territoire, non concerné par la modification)
                        if t == "Grenoble" and mode_log == "Comparaison Métropoles":
                            marker["pattern"] = dict(
                                shape="/", fgcolor="#FF584D", fillmode="overlay",
                                solidity=0.3, size=20,
                            )
                        fig_typo.add_trace(go.Bar(
                            name=t, x=categories, y=y_vals, marker=marker,
                            hovertemplate=f"<b>{t}</b><br>%{{x}} : %{{y:.1f}}%<extra></extra>",
                        ))
                    fig_typo.update_layout(
                        barmode="group", height=340, margin=dict(t=20, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(title="Taille du logement", showgrid=False),
                        yaxis=dict(title="Part du parc social (%)", gridcolor="#eee"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    )
                    st.plotly_chart(style(fig_typo), use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.markdown(
                        "**Taux de logement social** : ce graphique rapporte le volume de logements "
                        "sociaux (RPLS 2024) au total des résidences principales du territoire "
                        f"(RP {annee_ref}). La ligne pointillée à 20 % correspond au seuil de référence "
                        "fixé par la loi SRU pour de nombreuses communes en zone tendue. Un taux supérieur "
                        "à ce seuil traduit une offre sociale importante, un taux inférieur peut signaler "
                        "un déficit relatif d'offre abordable.\n\n"
                        "**Typologie du parc social** : la répartition T1 à T5+ renseigne sur l'adéquation "
                        "entre l'offre sociale et les besoins de la population. Un parc concentré sur les "
                        "petites typologies (T1/T2) répond bien aux besoins des personnes seules, jeunes "
                        "actifs ou étudiants, mais peut être insuffisant pour les familles nombreuses qui "
                        "se reportent alors sur le parc privé. " +
                        ("Les hachures rouges identifient Grenoble." if mode_log == "Comparaison Métropoles" else "")
                    )

                st.markdown("---")

                # ── GRAPH 3 / 4 : Financement + Ancienneté ──────────────────
                # Couleurs catégorielles dynamiques (gris en vue Métropoles,
                # vert en vue Communes), générées par build_grey_or_green_palette.
                FIN_ORDER = ["PLAI", "HLM avant 1977", "HLM après 1977", "PLS", "PLI"]
                FIN_CODE_MAP = {
                    "PLAI": "part_PLAI",
                    "HLM avant 1977": "part_HLM_avant_1977",
                    "HLM après 1977": "part_HLM_apres_1977",
                    "PLS": "part_PLS",
                    "PLI": "part_PLI",
                }
                fin_colors = build_grey_or_green_palette(FIN_ORDER, mode_log)

                AGE_ORDER = ["Avant 1949", "1949-1975", "1976-1988", "1989-2000", "2001-2013", "Après 2013"]
                AGE_CODE_MAP = {
                    "Avant 1949": "part_avant_1949",
                    "1949-1975": "part_1949_1975",
                    "1976-1988": "part_1976_1988",
                    "1989-2000": "part_1989_2000",
                    "2001-2013": "part_2001_2013",
                    "Après 2013": "part_apres_2013",
                }
                age_colors = build_grey_or_green_palette(AGE_ORDER, mode_log)

                gc3, gc4 = st.columns(2)

                with gc3:
                    st.subheader(
                        "Financement du parc social (%)",
                        help=(
                            "Répartition du parc social par dispositif de financement (base 100%) :\n"
                            "- **PLAI** (Prêt Locatif Aidé d'Intégration) : loyers les plus bas, destinés aux "
                            "ménages très modestes.\n"
                            "- **HLM avant/après 1977** : financement historique (HBM/HLM ordinaire), "
                            "loyers intermédiaires.\n"
                            "- **PLS** (Prêt Locatif Social) : loyers plus élevés, plafonds de ressources "
                            "plus larges.\n"
                            "- **PLI** (Prêt Locatif Intermédiaire) : destiné aux classes moyennes, loyers "
                            "proches du marché.\n\n"
                            "Une forte part de PLAI signale un parc orienté vers l'accueil des ménages les "
                            "plus modestes."
                        ),
                    )
                    fig_fin = go.Figure()
                    for cat in FIN_ORDER:
                        y_vals, x_vals = [], []
                        for t in targets_log:
                            st_t = stats_by_target[t]
                            if st_t is None:
                                continue
                            x_vals.append(t)
                            y_vals.append(st_t[FIN_CODE_MAP[cat]])
                        fig_fin.add_trace(go.Bar(
                            name=cat, x=x_vals, y=y_vals, marker_color=fin_colors[cat],
                            hovertemplate=f"<b>%{{x}}</b><br>{cat} : %{{y:.1f}}%<extra></extra>",
                        ))
                    # Encadrement vertical Grenoble (graphique vertical x=territoire,
                    # le greno_vrect calculé plus haut s'applique directement)
                    if greno_vrect:
                        fig_fin.add_vrect(**greno_vrect)
                    fig_fin.update_layout(
                        barmode="stack", height=340, margin=dict(t=20, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(title="Part du parc social (%)", range=[0, 100], gridcolor="#eee"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font_size=10),
                    )
                    st.plotly_chart(style(fig_fin), use_container_width=True)

                with gc4:
                    st.subheader(
                        "Ancienneté du parc social (%)",
                        help=(
                            "Répartition du parc social par période de construction (base 100%). "
                            "Un parc ancien (avant 1949 / 1949-1975) peut nécessiter davantage de "
                            "rénovation énergétique. Une forte part de constructions récentes "
                            "(après 2013) indique un parc renouvelé et un effort de production "
                            "continu de logements sociaux."
                        ),
                    )
                    fig_age = go.Figure()
                    for cat in AGE_ORDER:
                        y_vals, x_vals = [], []
                        for t in targets_log:
                            st_t = stats_by_target[t]
                            if st_t is None:
                                continue
                            x_vals.append(t)
                            y_vals.append(st_t[AGE_CODE_MAP[cat]])
                        fig_age.add_trace(go.Bar(
                            name=cat, x=x_vals, y=y_vals, marker_color=age_colors[cat],
                            hovertemplate=f"<b>%{{x}}</b><br>{cat} : %{{y:.1f}}%<extra></extra>",
                        ))
                    if greno_vrect:
                        fig_age.add_vrect(**greno_vrect)
                    fig_age.update_layout(
                        barmode="stack", height=340, margin=dict(t=20, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(title="Part du parc social (%)", range=[0, 100], gridcolor="#eee"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font_size=10),
                    )
                    st.plotly_chart(style(fig_age), use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.markdown(
                        "**Financement du parc social** : chaque dispositif correspond à un public et un "
                        "niveau de loyer différents. Un territoire avec une forte proportion de PLAI "
                        "accueille proportionnellement plus de ménages très modestes, tandis qu'un "
                        "territoire avec davantage de PLS/PLI propose des loyers sociaux plus proches "
                        "du marché privé, ciblant les classes moyennes.\n\n"
                        "**Ancienneté du parc** : un parc ancien (avant 1975) représente souvent un enjeu "
                        "de rénovation thermique et de confort, mais aussi un patrimoine bien situé en "
                        "centre-ville. Un parc récent (après 2001) traduit une politique de construction "
                        "neuve active, mais peut être plus excentré. Comparer l'ancienneté avec le taux de "
                        "vacance (KPI) permet d'identifier si le parc ancien est davantage délaissé par les "
                        "demandeurs. " +
                        ("Les zones rouges identifient Grenoble." if mode_log == "Comparaison Métropoles" else "")
                    )

                st.markdown("---")

                # ── GRAPH 5 : Loyers ────────────────────────────────────────
                # (couleurs = bar_colors, couleurs de territoire - non concerné
                # par la modification, déjà gris/vert selon mode_log)
                st.subheader(
                    "Loyers du parc social (€/m²)",
                    help=(
                        "Loyer médian (point) et intervalle interquartile (barre verticale, du 1er au "
                        "3e quartile) du parc social, en €/m² de surface habitable. "
                        "Plus l'intervalle est large, plus les loyers sont hétérogènes au sein du "
                        "territoire (mélange de logements anciens à loyers historiquement bas et de "
                        "constructions récentes à loyers plus élevés)."
                    ),
                )
                fig_loy = go.Figure()
                for i, t in enumerate(targets_log):
                    st_t = stats_by_target[t]
                    if st_t is None:
                        continue
                    q1, med, q3 = st_t["loyer_q1"], st_t["loyer_median"], st_t["loyer_q3"]
                    marker_color = bar_colors[i]
                    fig_loy.add_trace(go.Scatter(
                        x=[t], y=[med],
                        mode="markers",
                        marker=dict(symbol="diamond", size=14, color=marker_color,
                                    line=dict(color="white", width=1.5)),
                        error_y=dict(
                            type="data",
                            symmetric=False,
                            array=[q3 - med],
                            arrayminus=[med - q1],
                            color=marker_color, thickness=2, width=6,
                        ),
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{t}</b><br>"
                            f"Loyer médian : {med:.2f} €/m²<br>"
                            f"1er quartile : {q1:.2f} €/m²<br>"
                            f"3e quartile : {q3:.2f} €/m²<extra></extra>"
                        ),
                    ))
                if greno_vrect:
                    fig_loy.add_vrect(**greno_vrect)
                fig_loy.update_layout(
                    height=320, margin=dict(t=20, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(title="Loyer (€/m²)", gridcolor="#eee"),
                )
                st.plotly_chart(style(fig_loy), use_container_width=True)

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.markdown(
                        "Chaque losange représente le **loyer médian** du parc social du territoire : "
                        "la moitié des logements sociaux ont un loyer inférieur à cette valeur, l'autre "
                        "moitié un loyer supérieur. La barre verticale représente l'**écart interquartile** "
                        "(du 1er au 3e quartile) : elle contient 50% des loyers du parc.\n\n"
                        "Un loyer médian élevé combiné à un faible taux de vacance (voir KPI) traduit "
                        "généralement un marché du logement tendu, où même le parc social, censé être "
                        "abordable, atteint des niveaux de loyer relativement élevés. Une grande "
                        "dispersion (barre longue) indique une forte hétérogénéité du parc, mêlant "
                        "logements anciens à bas loyer et constructions récentes plus chères." +
                        (" Le losange rouge identifie Grenoble." if mode_log == "Comparaison Métropoles" else "")
                    )

# ==============================================================================
# ONGLET 7 - Population active 25-54 ans 
# ==============================================================================


_DIP_FRAGS_ORDERED = [
    ("Aucun diplôme",             "Sans diplôme"),
    ("de niveau CEP",              "CEP"),
    ("de niveau BEPC",             "BEPC"),
    ("de niveau CAP-BEP",          "CAP-BEP"),
    ("de niveau bac",              "Baccalauréat"),
    ("universitaire de 1er cycle", "Bac+2"),
    ("universitaire de 2",         "Bac+3 et +"),
]
_CSP_FRAGS_ORDERED = [
    ("Agriculteurs",                "Agriculteurs"),
    ("Artisans",                    "Artisans & Chefs"),
    ("Cadres",                      "Cadres & Prof. Sup."),
    ("Professions interm",          "Prof. Intermédiaires"),
    ("Employ",                      "Employés"),
    ("Ouvriers",                    "Ouvriers"),
]

@st.cache_data
def _load_raw_dip(year):
    """Charge le fichier brut diplôme pour une année donnée."""
    path = FILES_DIP.get(year)
    if path is None:
        return pd.DataFrame()
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    try:
        df = pd.read_excel(p) if p.suffix.lower() in [".xlsx", ".xls"] else pd.read_csv(p, sep=None, engine="python", low_memory=False)
        if not df.empty and "RR" in str(df.iloc[0, 0]):
            df = df.drop(0).reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()


def _build_heatmap_matrix(df_raw, row_filter_col, row_filter_vals):
    """
    Construit une matrice (CSP × Diplôme) en % ligne pour les lignes filtrées.
    row_filter_col : colonne sur laquelle filtrer (LIB_NORM ou DEP)
    row_filter_vals : liste de valeurs à conserver
    Retourne un DataFrame (CSP en index, Diplôme en colonnes), valeurs = % ligne.
    """
    if df_raw.empty:
        return pd.DataFrame()

    # Identifier colonnes dep et lib
    cols = df_raw.columns.tolist()
    c_dep = next((c for c in cols if any(x in str(c).upper() for x in ["DÉPARTEMENT", "DR24", "DEP"])), None)
    c_lib = next((c for c in cols if any(x in str(c).upper() for x in ["LIBELLÉ", "LIBELLE"])), None)
    if c_dep is None or c_lib is None:
        return pd.DataFrame()

    df_raw = df_raw.copy()
    df_raw["_dep"]     = df_raw[c_dep].astype(str).str.zfill(2)
    df_raw["_lib_norm"] = df_raw[c_lib].apply(normalize_name)

    if row_filter_col == "DEP":
        subset = df_raw[df_raw["_dep"].isin(row_filter_vals)]
    else:
        subset = df_raw[df_raw["_lib_norm"].isin(row_filter_vals)]

    if subset.empty:
        return pd.DataFrame()

    matrix = {}
    for csp_frag, csp_label in _CSP_FRAGS_ORDERED:
        row_vals = {}
        for dip_frag, dip_label in _DIP_FRAGS_ORDERED:
            matching = [
                c for c in cols
                if csp_frag.lower() in str(c).lower()
                and dip_frag.lower() in str(c).lower()
            ]
            val = subset[matching].apply(pd.to_numeric, errors="coerce").fillna(0).sum().sum() if matching else 0
            row_vals[dip_label] = val
        matrix[csp_label] = row_vals

    df_mat = pd.DataFrame(matrix).T  # CSP en lignes, Diplôme en colonnes
    # Ordre colonnes
    dip_labels = [d for _, d in _DIP_FRAGS_ORDERED]
    df_mat = df_mat[[d for d in dip_labels if d in df_mat.columns]]
    # Convertir en % ligne (part de chaque diplôme dans la CSP)
    row_totals = df_mat.sum(axis=1)
    df_pct = df_mat.div(row_totals, axis=0).multiply(100).fillna(0)
    return df_pct


# ── Onglet 7 ──────────────────────────────────────────────────────────────────

if vue == "Démographie":
    with tab7:

        if df_csp_new.empty or "ANNEE" not in df_csp_new.columns:
            st.info("📂 Données CSP/Diplôme non trouvées. Vérifiez les fichiers.")
        else:
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px;
                        border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> INSEE -
                <a href='https://www.insee.fr/fr/statistiques/1893185' target='_blank'
                   style='color: #1C3A27;'>Accéder aux données</a><br><br>
                <strong>Note sur les données :</strong> Ces chiffres sont issus des recensements
                de l'INSEE. Ils recensent la <b>population active de 25 à 54 ans</b>, le cœur
                stable du marché du travail.
                Quand vous comparez deux territoires, un graphique d'indice de spécialisation
                s'affiche en plus.
            </div>""", unsafe_allow_html=True)

            with st.container():
                filter_bar("Filtres - Profil des actifs (25-54 ans)")
                csp_geo_l, csp_geo_r = st.columns([1, 3])
                with csp_geo_l:
                    filter_row_label("Niveau géographique")
                with csp_geo_r:
                    mode_analyse = st.radio(
                        "",
                        ["Comparaison Métropoles",
                         "Comparaison communes Grenoble-Alpes Métropole"],
                        key="csp_mode", horizontal=True, label_visibility="collapsed",
                    )
                csp_row1_c1, csp_row1_c2 = st.columns(2)
                with csp_row1_c1:
                    theme_analyse = st.selectbox(
                        "Thématique",
                        ["Secteurs d'activité (CSP)", "Niveau de diplôme"],
                        key="csp_theme",
                        help=(
                            "**Secteurs d'activité (CSP)** : répartition des actifs 25-54 ans "
                            "par catégorie socio-professionnelle.\n\n"
                            "**Niveau de diplôme** : répartition des actifs 25-54 ans par "
                            "niveau d'études atteint, avec une heatmap croisant CSP et diplôme."
                        ),
                    )

                is_diplome = (theme_analyse == "Niveau de diplôme")
                current_df_csp  = df_dip_new if is_diplome else df_csp_new
                current_map_csp = DIP_MAP    if is_diplome else CSP_MAP_NEW

                annees_csp = (
                    sorted(current_df_csp["ANNEE"].dropna().unique(), reverse=True)
                    if not current_df_csp.empty else []
                )
                with csp_row1_c2:
                    sel_annee_csp = (
                        st.selectbox(
                            "Année", annees_csp, key="csp_annee",
                            help="Année du recensement INSEE. Données diplôme disponibles : 2011 et 2022.",
                        )
                        if annees_csp else None
                    )

                if mode_analyse == "Comparaison communes Grenoble-Alpes Métropole":
                    clist = sorted(COMMUNES["Grenoble"])
                    sel_communes_csp = st.multiselect(
                        "Communes de Grenoble-Alpes Métropole", clist,
                        default=shared_default_communes_demo(clist), key="csp_communes",
                        help="Sélectionnez les communes à analyser.",
                        on_change=sync_communes_demo, args=("csp_communes",),
                    )
                    entities_names = sel_communes_csp
                else:
                    sel_metros_csp = st.multiselect(
                        "Métropoles", TOUTES, default=shared_default_demo(TOUTES),
                        key="csp_metros", help="Sélectionnez les métropoles à comparer.",
                        on_change=sync_metros_demo, args=("csp_metros",),
                    )
                    entities_names = sel_metros_csp

                sel_cats = st.multiselect(
                    "Catégories à afficher",
                    options=list(current_map_csp.values()),
                    default=list(current_map_csp.values()),
                    key="csp_cats",
                    help=(
                        "Filtrez les catégories pour simplifier la lecture. "
                        "Désélectionner une catégorie la retire des graphiques de volume."
                        + (" La heatmap affiche toujours toutes les CSP et tous les diplômes." if is_diplome else "")
                    ),
                )

            COLORS_COMM_CSP5 = [
                "#081C15", "#1B4332", "#2D6A4F", "#40916C", "#52B788",
                "#74C69D", "#95D5B2", "#B7E4C7", "#D8F3DC",
            ]

            if sel_annee_csp:
                df_year_csp = current_df_csp[current_df_csp["ANNEE"] == sel_annee_csp]
                entities_csp = []

                for name in entities_names:
                    if mode_analyse == "Comparaison communes Grenoble-Alpes Métropole":
                        subset = df_year_csp[
                            (df_year_csp["LIB_NORM"] == normalize_name(name))
                            & (df_year_csp["DEP"] == "38")
                        ]
                        if not subset.empty:
                            entities_csp.append({"name": name, "data": subset.iloc[0]})
                    else:
                        dep   = DEP_MAP[name]
                        norms = [normalize_name(c) for c in COMMUNES[name]]
                        subset = df_year_csp[
                            (df_year_csp["DEP"] == dep)
                            & (df_year_csp["LIB_NORM"].isin(norms))
                        ]
                        if not subset.empty:
                            agg = subset[list(current_map_csp.values())].sum()
                            entities_csp.append({"name": name, "data": agg})

                if entities_csp and sel_cats:
                    st.markdown("---")

                    # ── KPI ──────────────────────────────────────────────────
                    kpi_cols_csp = st.columns(len(entities_csp))
                    for i, entity in enumerate(entities_csp):
                        total_actifs = entity["data"][sel_cats].sum()
                        val_formatee = f"{int(total_actifs):,d}".replace(",", "\u202f")

                        if mode_analyse == "Comparaison Métropoles":
                            kpi_color5 = COULEURS.get(entity["name"], "#888888")
                        else:
                            kpi_color5 = COLORS_COMM_CSP5[i % len(COLORS_COMM_CSP5)]

                        with kpi_cols_csp[i]:
                            st.markdown(f"""
                            <div style='display:flex;flex-direction:row;align-items:stretch;
                                border-radius:8px;overflow:hidden;
                                box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
                                min-height:80px;border-left:6px solid {kpi_color5};'>
                                <div style='padding:10px 16px;display:flex;flex-direction:column;
                                    justify-content:center;'>
                                    <div style='font-size:11px;font-weight:700;
                                        letter-spacing:0.08em;color:#666;
                                        text-transform:uppercase;'>{entity['name']}</div>
                                    <div style='font-size:24px;font-weight:bold;
                                        color:#111;'>{val_formatee}</div>
                                    <div style='color:{kpi_color5};font-size:11px;font-weight:700;
                                        text-transform:uppercase;
                                        letter-spacing:0.05em;'>Actifs 25-54 ans</div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                    st.markdown("---")

                    if is_diplome:
                        st.subheader(
                            "Répartition des effectifs par niveau de diplôme",
                            help=(
                                "Nombre réel d'actifs 25-54 ans par niveau de diplôme. "
                                "Chaque groupe de barres correspond à un niveau, "
                                "chaque couleur à un territoire."
                            ),
                        )
                    else:
                        st.subheader(
                            "Répartition des effectifs par catégorie socio-professionnelle",
                            help="Nombre réel d'actifs 25-54 ans par catégorie socio-professionnelle.",
                        )

                    fig_bar_csp = go.Figure()
                    for i, ent in enumerate(entities_csp):
                        if mode_analyse == "Comparaison Métropoles":
                            bar_color = COULEURS.get(ent["name"], "#888888")
                        else:
                            bar_color = COLORS_COMM_CSP5[i % len(COLORS_COMM_CSP5)]

                        if ent["name"] == "Grenoble" and mode_analyse == "Comparaison Métropoles":
                            marker_dict = dict(
                                color=bar_color,
                                line=dict(color=bar_color, width=1),
                                pattern=dict(
                                    shape="/", fgcolor="#FF584D",
                                    fillmode="overlay", solidity=0.3, size=20,
                                ),
                            )
                        else:
                            marker_dict = dict(color=bar_color)

                        fig_bar_csp.add_trace(go.Bar(
                            x=sel_cats,
                            y=ent["data"][sel_cats],
                            name=ent["name"],
                            marker=marker_dict,
                            hovertemplate=(
                                "<b>Territoire : " + ent["name"] + "</b><br>"
                                "%{x} : %{y:.2s}<extra></extra>"
                            ),
                        ))
                    fig_bar_csp.update_layout(
                        barmode="group",
                        height=400,
                        margin=dict(t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(tickangle=-20),
                        yaxis=dict(gridcolor="#E8F5EE"),
                        legend=dict(
                            orientation="v", yanchor="middle", y=0.5,
                            xanchor="left", x=1.02, title="",
                        ),
                    )
                    st.plotly_chart(fig_bar_csp, use_container_width=True)

                    if not is_diplome:
                        # ── Radar CSP ─────────────────────────────────────────
                        st.markdown("---")
                        st.subheader(
                            "Profil structurel (%)",
                            help=(
                                "Part relative (%) de chaque CSP dans la population active "
                                "du territoire (base 100 %). Neutralise l'effet de taille "
                                "pour comparer les structures entre territoires."
                            ),
                        )
                        fig_radar_csp = go.Figure()
                        for i, ent in enumerate(entities_csp):
                            v   = ent["data"][sel_cats]
                            pct = (v / v.sum() * 100).fillna(0)

                            if mode_analyse == "Comparaison Métropoles":
                                radar_color = COULEURS.get(ent["name"], "#888888")
                            else:
                                radar_color = COLORS_COMM_CSP5[i % len(COLORS_COMM_CSP5)]

                            if ent["name"] == "Grenoble" and mode_analyse == "Comparaison Métropoles":
                                fill_color = "rgba(255, 88, 77, 0.12)"
                                line_dict  = dict(color="#FF584D", width=4, dash="dash")
                            else:
                                r, g, b = [int(radar_color.lstrip("#")[j:j+2], 16) for j in (0, 2, 4)]
                                fill_color = f"rgba({r},{g},{b},0.08)"
                                line_dict  = dict(color=radar_color, width=2, dash="solid")

                            fig_radar_csp.add_trace(go.Scatterpolar(
                                r=list(pct) + [pct.iloc[0]],
                                theta=sel_cats + [sel_cats[0]],
                                fill="toself",
                                fillcolor=fill_color,
                                name=ent["name"],
                                line=line_dict,
                                hovertemplate=(
                                    "<b>Territoire : " + ent["name"] + "</b><br>"
                                    "%{theta} : %{r:.2f} %<extra></extra>"
                                ),
                            ))
                        fig_radar_csp.update_layout(
                            height=450,
                            margin=dict(t=50, b=50),
                            paper_bgcolor="rgba(0,0,0,0)",
                            font_family="Sora",
                            polar=dict(
                                bgcolor="rgba(0,0,0,0)",
                                radialaxis=dict(gridcolor="#E8F5EE"),
                                angularaxis=dict(gridcolor="#E8F5EE"),
                            ),
                            legend=dict(
                                orientation="v", yanchor="middle", y=0.5,
                                xanchor="left", x=1.02, title="",
                            ),
                        )
                        st.plotly_chart(fig_radar_csp, use_container_width=True)

                        with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                            st.write(
                                "**Volume (barres groupées)** : effectifs réels par catégorie. "
                                "Utile pour estimer les besoins en services publics "
                                "(logements, transports, formations).\n\n"
                                "**Radar (%)** : part relative de chaque CSP dans la population active. "
                                "Compare les profils socio-professionnels en neutralisant la taille "
                                "des territoires. La surface rouge désigne Grenoble."
                            )

                    else:
                        # ── Heatmap CSP × Diplôme ─────────────────────────────
                        st.markdown("---")
                        st.subheader(
                            "Répartition des diplômes par catégorie socio-professionnelle (%)",
                            help=(
                                "Pour chaque CSP (ligne) et chaque territoire, la heatmap montre "
                                "la part (%) de chaque niveau de diplôme parmi les actifs de cette CSP. "
                                "La lecture se fait ligne par ligne : chaque ligne somme à 100 %. "
                                "Une case très foncée indique que ce diplôme est fortement représenté "
                                "dans cette CSP."
                            ),
                        )

                        # Charger le fichier brut pour l'année sélectionnée
                        df_raw_dip = _load_raw_dip(sel_annee_csp)

                        if df_raw_dip.empty:
                            st.info("Données brutes non disponibles pour cette année.")
                        else:
                            # Une heatmap par territoire, disposées en colonnes (max 3 par ligne)
                            n_ent    = len(entities_csp)
                            n_cols_h = min(n_ent, 3)
                            heat_cols = st.columns(n_cols_h)

                            for idx, ent in enumerate(entities_csp):
                                col_idx = idx % n_cols_h

                                # Construire la matrice pour ce territoire
                                if mode_analyse == "Comparaison communes Grenoble-Alpes Métropole":
                                    df_mat = _build_heatmap_matrix(
                                        df_raw_dip,
                                        row_filter_col="LIB_NORM",
                                        row_filter_vals=[normalize_name(ent["name"])],
                                    )
                                else:
                                    dep   = DEP_MAP[ent["name"]]
                                    norms = [normalize_name(c) for c in COMMUNES[ent["name"]]]
                                    df_mat = _build_heatmap_matrix(
                                        df_raw_dip,
                                        row_filter_col="DEP",
                                        row_filter_vals=[dep],
                                    )

                                if df_mat.empty:
                                    with heat_cols[col_idx]:
                                        st.warning(f"Pas de données pour {ent['name']}.")
                                    continue

                                # Couleur de titre = couleur du territoire
                                if mode_analyse == "Comparaison Métropoles":
                                    title_color = COULEURS.get(ent["name"], "#888888")
                                else:
                                    title_color = COLORS_COMM_CSP5[idx % len(COLORS_COMM_CSP5)]

                                # Annotations texte dans les cellules
                                annotations_heat = []
                                for r_i, csp_name in enumerate(df_mat.index):
                                    for c_i, dip_name in enumerate(df_mat.columns):
                                        val = df_mat.loc[csp_name, dip_name]
                                        annotations_heat.append(dict(
                                            x=c_i, y=r_i,
                                            text=f"{val:.1f}%",
                                            showarrow=False,
                                            font=dict(
                                                size=9,
                                                color="white" if val > 35 else "#333",
                                                family="Sora",
                                            ),
                                            xref="x", yref="y",
                                        ))

                                fig_heat = go.Figure(go.Heatmap(
                                    z=df_mat.values,
                                    x=list(df_mat.columns),
                                    y=list(df_mat.index),
                                    colorscale=[
                                        [0.0,  "#F8FBF9"],
                                        [0.25, "#B7E4C7"],
                                        [0.5,  "#52B788"],
                                        [0.75, "#2D6A4F"],
                                        [1.0,  "#1B4332"],
                                    ],
                                    zmin=0,
                                    zmax=100,
                                    showscale=(idx == len(entities_csp) - 1),
                                    colorbar=dict(
                                        title="%",
                                        thickness=12,
                                        len=0.8,
                                        tickfont=dict(size=9, family="Sora"),
                                    ),
                                    hovertemplate=(
                                        "<b>" + ent["name"] + "</b><br>"
                                        "CSP : %{y}<br>"
                                        "Diplôme : %{x}<br>"
                                        "Part : <b>%{z:.1f} %</b><extra></extra>"
                                    ),
                                ))

                                fig_heat.update_layout(
                                    title=dict(
                                        text=f"<b style='color:{title_color}'>{ent['name']}</b>",
                                        font=dict(size=13, family="Sora"),
                                        x=0.01,
                                    ),
                                    height=320,
                                    margin=dict(t=40, b=10, l=10, r=10),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    font_family="Sora",
                                    xaxis=dict(
                                        tickangle=-30,
                                        tickfont=dict(size=9),
                                        side="bottom",
                                    ),
                                    yaxis=dict(
                                        tickfont=dict(size=9),
                                        autorange="reversed",
                                    ),
                                    annotations=annotations_heat,
                                )

                                with heat_cols[col_idx]:
                                    st.plotly_chart(fig_heat, use_container_width=True)

                        with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                            st.write(
                                "**Volume (barres groupées)** : effectifs réels par niveau de diplôme. "
                                "Utile pour estimer les besoins absolus en formation ou en reconversion.\n\n"
                                "**Heatmap CSP × Diplôme** : chaque ligne correspond à une catégorie "
                                "socio-professionnelle, chaque colonne à un niveau de diplôme. "
                                "La valeur dans chaque case est la **part (%) de ce diplôme parmi "
                                "les actifs de cette CSP**. La lecture se fait ligne par ligne "
                                "(chaque ligne somme à 100 %).\n\n"
                                "Plus la case est foncée, plus ce diplôme est concentré dans cette CSP. "
                                "Par exemple, une case très foncée en 'Cadres & Prof. Sup.' / 'Bac+3 et +' "
                                "indique que l'immense majorité des cadres sont diplômés du supérieur long. "
                                "À l'inverse, une case foncée en 'Ouvriers' / 'Sans diplôme' ou 'CAP-BEP' "
                                "révèle une forte concentration des peu qualifiés dans cette CSP.\n\n"
                                "Une heatmap est affichée par territoire sélectionné, ce qui permet "
                                "de comparer visuellement les structures CSP × Diplôme entre métropoles.\n\n"
                                "⚠️ *Note INSEE* : depuis 2022, le cycle universitaire est distingué en "
                                "court (Bac+2) et long (Bac+3 et +). Pour les recensements antérieurs, "
                                "ces deux niveaux sont regroupés dans **Bac+3 et +**."
                            )

                    # ── Indice de spécialisation (2 territoires uniquement) ──
                    if len(entities_csp) == 2:
                        t1_name = entities_names[0]
                        t2_name = entities_names[1]
                        st.markdown("---")
                        st.markdown(
                            f"### Guide de lecture : Spécialisation du Territoire 1 "
                            f"({t1_name}) face au Territoire 2 ({t2_name})"
                        )
                        st.markdown(f"""
                        <div style='background-color:#f8f9fa;padding:18px;border-radius:8px;
                                    border:1px solid #e0e0e0;margin-bottom:20px;'>
                            <h5 style='margin-top:0;'>💡 Comment lire ce graphique et ce tableau ?</h5>
                            <p style='font-size:14px;'>L'indice compare si une catégorie est plus ou
                            moins présente en <b>proportion</b> dans le Territoire 1 par rapport au
                            Territoire 2.</p>
                            <ul style='font-size:14px;'>
                                <li><b>Indice &gt; 100 :</b> La catégorie est
                                    <b>surreprésentée</b> dans le Territoire 1 ({t1_name}).</li>
                                <li><b>Indice = 100 :</b> Équilibre parfait.</li>
                                <li><b>Indice &lt; 100 :</b> La catégorie est
                                    <b>sous-représentée</b> dans le Territoire 1.</li>
                            </ul>
                        </div>""", unsafe_allow_html=True)

                        v1, v2     = entities_csp[0]["data"][sel_cats], entities_csp[1]["data"][sel_cats]
                        t1_total, t2_total = v1.sum(), v2.sum()
                        with np.errstate(divide="ignore", invalid="ignore"):
                            raw  = ((v1 / t1_total) / (v2 / t2_total) * 100).astype(float)
                            spec = pd.Series(
                                np.where(np.isfinite(raw.values), raw.values, np.nan),
                                index=raw.index,
                            )
                        spec_plot = spec.fillna(0)
                        fig_spec  = px.bar(
                            x=sel_cats, y=spec_plot,
                            color=spec_plot, color_continuous_scale="RdYlGn",
                            title=f"Spécialisation : {t1_name} / {t2_name}",
                        )
                        fig_spec.add_hline(y=100, line_dash="dash", line_color="black")
                        fig_spec.update_layout(
                            height=450,
                            coloraxis_showscale=False,
                            yaxis_title="Indice (Base 100)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_family="Sora",
                            xaxis=dict(tickangle=-20),
                        )
                        st.plotly_chart(fig_spec, use_container_width=True)

                        with st.expander(
                            "Voir le tableau récapitulatif (Effectifs et Indice)",
                            expanded=True,
                        ):
                            table_df = pd.DataFrame({
                                "Catégorie": sel_cats,
                                f"{t1_name} (T1 - Eff.)": [
                                    f"{int(v1[c]):,d}".replace(",", "\u202f")
                                    for c in sel_cats
                                ],
                                f"{t2_name} (T2 - Eff.)": [
                                    f"{int(v2[c]):,d}".replace(",", "\u202f")
                                    for c in sel_cats
                                ],
                                "Indice spécialisation": [
                                    str(int(spec[c])) if pd.notna(spec[c]) else "N/D"
                                    for c in sel_cats
                                ],
                            })
                            st.dataframe(table_df.set_index("Catégorie"), use_container_width=True)
                            
# ==============================================================================
# SOLIDARITÉ & CITOYENNETÉ
# ==============================================================================
if vue == "Solidarité et citoyenneté":
    s1, s2, s3, s4 = st.tabs(["🤝 Solidarité", "🎓 Éducation", "🏥 Santé", "🗳️ Participation citoyenne"])

    def render_solidarite_kpi(title, value, subtitle, border_color="#1e5631"):
        return f"""
        <div style='display:flex;flex-direction:row;align-items:stretch;border-radius:8px;
            overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);background:#fff;
            min-height:80px;border-left:6px solid {border_color};margin-bottom:10px;'>
            <div style='padding:10px 16px;display:flex;flex-direction:column;justify-content:center;width:100%;'>
                <div style='font-size:11px;font-weight:700;letter-spacing:0.08em;color:#666;text-transform:uppercase;'>{title}</div>
                <div style='font-size:24px;font-weight:bold;color:#111;margin:2px 0;'>{value}</div>
                <div style='color:{border_color};font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;'>{subtitle}</div>
            </div>
        </div>"""

    def render_metro_kpi_card(metro_name, val_principal, label_principal, val_secondaire, label_secondaire, border_color, dashed=False):
        border_style = (
            f"border:2px dashed {border_color};border-left:6px solid {border_color};"
            if dashed else f"border-left:6px solid {border_color};"
        )
        return f"""
        <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);
            background:#fff;{border_style}margin-bottom:12px;padding:12px 16px;'>
            <div style='font-size:12px;font-weight:700;color:#1C3A27;margin-bottom:8px;
                border-bottom:1px solid #eee;padding-bottom:4px;'>{metro_name}</div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
                <div style='text-align:center;'>
                    <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>{label_principal}</div>
                    <div style='font-size:17px;font-weight:800;color:#2D6A4F;'>{val_principal}</div>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>{label_secondaire}</div>
                    <div style='font-size:17px;font-weight:800;color:#555;'>{val_secondaire}</div>
                </div>
            </div>
        </div>"""

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 1 - SOLIDARITÉ (CAF)
    # ──────────────────────────────────────────────────────────────────────────
    with s1:
        if df_caf is None or df_caf.empty:
            st.info("📂 Fichier `CAF_5_Metropoles.csv` introuvable.")
        else:
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> CAF -
                <a href='https://data.caf.fr/explore/dataset/ndur_s_qf_400_com_f/table/' target='_blank' style='color: #1C3A27;'>Accéder aux données</a>
            </div>""", unsafe_allow_html=True)

            # ── Attention : biais taille ──────────────────────────────────────
            st.markdown("""
            <div style='background-color: #fff8e1; padding: 13px 16px; border-radius: 10px;
                border-left: 5px solid #f0a500; margin-bottom: 18px; font-size: 0.88em;'>
                ⚠️ <strong>Attention - biais de taille :</strong> les volumes (foyers aidés, personnes concernées,
                montants versés) dépendent directement de la taille de la métropole. Une agglomération plus grande
                comptera mécaniquement plus de bénéficiaires, même si sa proportion d'habitants aidés est similaire
                aux autres. Pour contextualiser ces chiffres, consultez l'onglet <strong>Ménages</strong> qui donne
                un ordre de grandeur du nombre de ménages par territoire.
            </div>""", unsafe_allow_html=True)

            required_cols = {"Annee", "Agglomeration"}
            if not required_cols.issubset(set(df_caf.columns)):
                st.error("Colonnes Annee / Agglomeration manquantes.")
            else:
                ALL_METRIC_LABELS = {
                    "Nombre foyers NDUR":       "Foyers aidés (toutes aides)",
                    "Nombre personnes NDUR":    "Personnes concernées (toutes aides)",
                    "Montant total NDUR":        "Montant total versé (€)",
                    "Nombre foyers NDURPAJE":   "Foyers aidés - Jeunes enfants",
                    "Nombre personnes NDURPAJE":"Personnes concernées - Jeunes enfants",
                    "Montant total NDURPAJE":    "Montant versé - Jeunes enfants (€)",
                    "Nombre foyers NDUREJ":     "Foyers aidés - Enfance & jeunesse",
                    "Nombre personnes NDUREJ":  "Personnes concernées - Enfance & jeunesse",
                    "Montant total NDUREJ":      "Montant versé - Enfance & jeunesse (€)",
                    "Nombre foyers NDURAL":     "Foyers aidés - Logement",
                    "Nombre personnes NDURAL":  "Personnes concernées - Logement",
                    "Montant total NDURAL":      "Montant versé - Logement (€)",
                    "Nombre foyers NDURINS":    "Foyers aidés - Insertion",
                    "Nombre personnes NDURINS": "Personnes concernées - Insertion",
                    "Montant total NDURINS":     "Montant versé - Insertion (€)",
                }
                available_metrics = {k: v for k, v in ALL_METRIC_LABELS.items() if k in df_caf.columns}
                if not available_metrics:
                    st.warning("Aucune mesure CAF trouvée.")
                else:
                    for col in available_metrics:
                        df_caf[col] = pd.to_numeric(df_caf[col], errors="coerce").fillna(0)
                    years_caf  = sorted(df_caf["Annee"].dropna().unique())
                    agglos_caf = sorted(df_caf["Agglomeration"].dropna().unique())
                    gre_agglo  = next((a for a in agglos_caf if "Grenoble" in a), "Grenoble Alpes Métropole")

                    with st.container():
                        filter_bar("Filtres - Solidarité CAF")
                        f1, f2 = st.columns([1, 3])
                        with f1:
                            filter_row_label("Niveau géographique")
                        with f2:
                            mode_caf = st.radio(
                                "", ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                                key="caf_mode", horizontal=True, label_visibility="collapsed"
                            )
                        if mode_caf == "Comparaison Métropoles":
                            sel_entites_caf = st.multiselect(
                                "Métropoles à comparer", agglos_caf,
                                default=shared_default_solid(agglos_caf),
                                key="caf_agglos", on_change=sync_metros_solid, args=("caf_agglos",)
                            )
                        else:
                            communes_gre_caf = (
                                sorted(df_caf[df_caf["Agglomeration"] == gre_agglo]["Nom_Commune"].dropna().unique())
                                if "Nom_Commune" in df_caf.columns else []
                            )
                            sel_entites_caf = st.multiselect(
                                "Communes de Grenoble-Alpes Métropole", communes_gre_caf,
                                default=shared_default_communes_solid(communes_gre_caf, "caf_communes"),
                                key="caf_communes", on_change=sync_communes_solid, args=("caf_communes",)
                            )
                        MEASURE_TYPES = {
                            "Nombre foyers":    "Foyers aidés",
                            "Nombre personnes": "Personnes concernées",
                            "Montant total":    "Montant versé (€)",
                        }
                        AID_CATEGORIES = {
                            "NDUR":     "Toutes aides",
                            "NDURPAJE": "Jeunes enfants (PAJE)",
                            "NDUREJ":   "Enfance & jeunesse",
                            "NDURAL":   "Logement",
                            "NDURINS":  "Insertion",
                        }
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            measure_label  = st.selectbox("Mesure", list(MEASURE_TYPES.values()), index=0, key="caf_measure")
                            measure_prefix = next(k for k, v in MEASURE_TYPES.items() if v == measure_label)
                        with c2:
                            available_cats = {s: l for s, l in AID_CATEGORIES.items() if f"{measure_prefix} {s}" in available_metrics}
                            cat_label      = st.selectbox("Catégorie d'aide", list(available_cats.values()), index=0, key="caf_cat")
                            cat_suffix     = next(k for k, v in available_cats.items() if v == cat_label)
                            metric_key     = f"{measure_prefix} {cat_suffix}"
                        with c3:
                            year_caf = st.selectbox("Année", years_caf, index=len(years_caf)-1, key="caf_year")
                        st.markdown('</div>', unsafe_allow_html=True)

                    geo_col  = "Agglomeration" if mode_caf == "Comparaison Métropoles" else "Nom_Commune"
                    is_metro = (mode_caf == "Comparaison Métropoles")

                    df_fil = df_caf[df_caf["Annee"] == year_caf]
                    if is_metro:
                        df_fil = df_fil[df_fil["Agglomeration"].isin(sel_entites_caf)]
                    else:
                        df_fil = df_fil[
                            (df_fil["Agglomeration"] == gre_agglo) &
                            (df_fil["Nom_Commune"].isin(sel_entites_caf))
                        ]

                    st.markdown("---")

                    if df_fil.empty or not sel_entites_caf:
                        st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
                    else:
                        # Bloc de rendu structuré : en fonction du filtre (métropole vs communes),
                        # on affiche d'abord la section correspondante, puis l'ensemble des KPIs/graphes.
                        if is_metro:
                            st.markdown("##### Partie Métropole")
                        else:
                            st.markdown("##### Partie Commune")
                        label_metric = available_metrics[metric_key]
                        suffix_euro  = " €" if "Montant" in metric_key else ""

                        # ── KPI globaux ───────────────────────────────────────
                        total_val  = df_fil[metric_key].sum()
                        nb_entites = df_fil[geo_col].nunique()
                        moy_entite = total_val / nb_entites if nb_entites > 0 else 0
                        max_entite = df_fil.groupby(geo_col)[metric_key].sum().idxmax()

                        st.markdown(f"#### Synthèse des allocations - {year_caf}")
                        k1, k2, k3, k4 = st.columns(4)
                        kpi_border_color = "#666" if is_metro else "#1e5631"
                        with k1:
                            st.markdown(render_solidarite_kpi(
                                f"Total {year_caf}", fmt(total_val, suffix=suffix_euro),
                                label_metric, kpi_border_color), unsafe_allow_html=True)
                        with k2:
                            st.markdown(render_solidarite_kpi(
                                "Périmètre", fmt(nb_entites),
                                "Unités comparées", kpi_border_color), unsafe_allow_html=True)
                        with k3:
                            st.markdown(render_solidarite_kpi(
                                "Moyenne / territoire", fmt(moy_entite, suffix=suffix_euro),
                                label_metric, kpi_border_color), unsafe_allow_html=True)
                        with k4:
                            st.markdown(render_solidarite_kpi(
                                "Top territoire", max_entite,
                                "Volume le plus élevé", kpi_border_color), unsafe_allow_html=True)

                        # ── KPI par métropole ─────────────────────────────────
                        if is_metro and len(sel_entites_caf) > 0:
                            st.markdown("#### Indicateurs par métropole")
                            df_by_metro = df_fil.groupby(geo_col, as_index=False)[metric_key].sum()

                            # Variation vs année précédente
                            prev_year = year_caf - 1 if (year_caf - 1) in years_caf else None
                            df_prev   = None
                            if prev_year:
                                df_prev_fil = df_caf[
                                    (df_caf["Annee"] == prev_year) &
                                    (df_caf["Agglomeration"].isin(sel_entites_caf))
                                ]
                                df_prev = (
                                    df_prev_fil.groupby(geo_col, as_index=False)[metric_key]
                                    .sum().set_index(geo_col)[metric_key]
                                )

                            kpi_metro_cols = st.columns(len(sel_entites_caf))
                            for idx_m, agglo in enumerate(sel_entites_caf):
                                val_m     = df_by_metro[df_by_metro[geo_col] == agglo][metric_key].sum()
                                metro_key = next((m for m in COULEURS.keys() if m in agglo), agglo)
                                is_gren   = ("Grenoble" in agglo)

                                # ▶ Grenoble : bordure rouge pointillée comme les graphiques
                                col_m = "#FF584D" if is_gren else COULEURS.get(metro_key, "#888888")

                                if df_prev is not None and agglo in df_prev.index:
                                    val_prev  = df_prev[agglo]
                                    delta_pct = ((val_m - val_prev) / val_prev * 100) if val_prev > 0 else 0
                                    delta_str = f"{delta_pct:+.1f}% vs {prev_year}"
                                else:
                                    delta_str = "-"

                                with kpi_metro_cols[idx_m]:
                                    st.markdown(
                                        render_metro_kpi_card(
                                            metro_name       = agglo,
                                            val_principal    = fmt(val_m, suffix=suffix_euro),
                                            label_principal  = (label_metric[:20] + "…"
                                                                if len(label_metric) > 20 else label_metric),
                                            val_secondaire   = delta_str,
                                            label_secondaire = "Évolution annuelle",
                                            border_color     = col_m,
                                            dashed           = is_gren,
                                        ),
                                        unsafe_allow_html=True
                                    )

                        st.markdown("---")

                        PALETTE_METRO_CAF   = px.colors.sequential.Greys[2:]
                        PALETTE_COMMUNE_CAF = px.colors.sequential.Greens_r
                        color_seq_caf       = PALETTE_METRO_CAF if is_metro else PALETTE_COMMUNE_CAF

                        if is_metro:
                            df_fil["Metropole_Key"] = df_fil["Agglomeration"].apply(
                                lambda x: next((m for m in COULEURS.keys() if m in x), x)
                            )

                        # ── Ligne 1 : QF distribution + Comparaison aides ─────
                        c1, c2 = st.columns(2)

                        with c1:
                            st.markdown(
                                f"##### Répartition par quotient familial ({year_caf})",
                                help="Répartition des bénéficiaires selon leur tranche de revenus (Quotient Familial CAF)."
                            )
                            if "Quotient familial" in df_fil.columns:
                                qf_order = [
                                    "Moins de 400 euros", "Entre 400 et 799 euros",
                                    "Entre 800 et 1199 euros", "Entre 1200 et 1599 euros",
                                    "Entre 1600 et 1999 euros", "Entre 2000 et 3999 euros",
                                    "4000 euros ou plus", "Inconnu",
                                ]
                                qf_data = df_fil.groupby(
                                    [geo_col, "Quotient familial"], as_index=False
                                )[metric_key].sum()
                                qf_data["QF_ord"] = pd.Categorical(
                                    qf_data["Quotient familial"], categories=qf_order, ordered=True
                                )
                                order_x  = (
                                    qf_data.groupby(geo_col)[metric_key]
                                    .sum().sort_values(ascending=False).index.tolist()
                                )
                                y_max_qf = qf_data.groupby(geo_col)[metric_key].sum().max()

                                if is_metro:
                                    n_t   = len(qf_order)
                                    greys = [
                                        f"#{v:02x}{v:02x}{v:02x}"
                                        for v in [int(0x77 + (220 - 0x77) * i / max(n_t-1, 1))
                                                  for i in range(n_t)]
                                    ]
                                    qf_color_map = {t: greys[j] for j, t in enumerate(qf_order)}
                                    fig_qf = px.bar(
                                        qf_data.sort_values("QF_ord"), x=geo_col, y=metric_key,
                                        color="Quotient familial", color_discrete_map=qf_color_map,
                                        barmode="stack",
                                        labels={geo_col: "", metric_key: label_metric}, height=360
                                    )
                                    grenoble_agglo = next(
                                        (a for a in qf_data[geo_col].unique() if "Grenoble" in a), None
                                    )
                                    if grenoble_agglo and grenoble_agglo in order_x:
                                        g_pos_qf = order_x.index(grenoble_agglo)
                                        fig_qf.add_vrect(
                                            x0=g_pos_qf - 0.45, x1=g_pos_qf + 0.45,
                                            fillcolor="rgba(255,88,77,0.10)",
                                            line_color="#FF584D", line_width=1.5,
                                            line_dash="dash", layer="below"
                                        )
                                else:
                                    fig_qf = px.bar(
                                        qf_data.sort_values("QF_ord"), x=geo_col, y=metric_key,
                                        color="Quotient familial",
                                        color_discrete_sequence=color_seq_caf,
                                        barmode="stack",
                                        labels={geo_col: "", metric_key: label_metric}, height=360
                                    )

                                for trace in fig_qf.data:
                                    n = len(trace.y) if trace.y is not None else 0
                                    trace.customdata = [[trace.name]] * n
                                    trace.hovertemplate = (
                                        "<b>%{x}</b><br>Tranche : <b>%{customdata[0]}</b><br>"
                                        + label_metric + " : <b>%{y:,.0f}</b><extra></extra>"
                                    )
                                fig_qf.update_layout(
                                    separators=", ",
                                    yaxis=dict(range=[0, y_max_qf * 1.1]),
                                    xaxis=dict(
                                        categoryorder="array", categoryarray=order_x,
                                        tickangle=-30, title=""
                                    ),
                                    legend=dict(
                                        orientation="v", yanchor="middle", y=0.5,
                                        xanchor="left", x=1.02, title="Tranche"
                                    ),
                                    margin=dict(t=30, r=40, b=80)
                                )
                                st.plotly_chart(style(fig_qf, 30), use_container_width=True)

                        with c2:
                            st.markdown(
                                f"##### Comparaison toutes catégories d'aides ({year_caf})",
                                help="Permet de comparer en un seul coup d'œil la répartition de chaque aide entre les territoires."
                            )
                            AIDES_COMP = {
                                "Insertion":          f"{measure_prefix} NDURINS",
                                "Logement":           f"{measure_prefix} NDURAL",
                                "Jeunes enfants":     f"{measure_prefix} NDURPAJE",
                                "Enfance & Jeunesse": f"{measure_prefix} NDUREJ",
                            }
                            aides_disp = {lab: col for lab, col in AIDES_COMP.items() if col in df_fil.columns}
                            if aides_disp:
                                bcomp = df_fil.groupby(geo_col, as_index=False)[list(aides_disp.values())].sum()
                                if is_metro:
                                    bcomp["Metropole_Key"] = bcomp[geo_col].apply(
                                        lambda x: next((m for m in COULEURS.keys() if m in x), x)
                                    )
                                bcomp = bcomp.rename(columns={v: k for k, v in aides_disp.items()})
                                bcomp_long = bcomp.melt(
                                    id_vars=[geo_col] + (["Metropole_Key"] if is_metro else []),
                                    value_vars=list(aides_disp.keys()),
                                    var_name="Catégorie", value_name="Valeur"
                                )
                                color_group_comp = "Metropole_Key" if is_metro else geo_col
                                color_map_comp   = COULEURS if is_metro else None
                                fig_comp = px.bar(
                                    bcomp_long, x="Valeur", y="Catégorie",
                                    color=color_group_comp,
                                    color_discrete_map=color_map_comp,
                                    color_discrete_sequence=color_seq_caf,
                                    barmode="group", orientation="h", text_auto=",.0f",
                                    labels={
                                        "Valeur": label_metric,
                                        "Catégorie": "",
                                        color_group_comp: "Territoire"
                                    },
                                    height=360
                                )
                                fig_comp.update_traces(
                                    hovertemplate="<b>%{y}</b><br>%{fullData.name} : <b>%{x:,.0f}</b><extra></extra>"
                                )
                                fig_comp.update_layout(
                                    separators=", ",
                                    legend=dict(
                                        orientation="v", yanchor="middle", y=0.5,
                                        xanchor="left", x=1.02
                                    ),
                                    margin=dict(t=30, b=30, l=120),
                                    yaxis={"categoryorder": "total ascending"}
                                )
                                if is_metro:
                                    apply_grenoble_hatch(fig_comp)
                                st.plotly_chart(style(fig_comp, 30), use_container_width=True)

                        st.markdown("---")

                        # ── Ligne 2 : Évolution temporelle + Structure ─────────
                        c3, c4 = st.columns(2)

                        with c3:
                            st.markdown(
                                f"##### Évolution temporelle - {label_metric}",
                                help="Évolution de l'indicateur sélectionné sur toutes les années disponibles."
                            )
                            df_evol = df_caf.copy()
                            if is_metro:
                                df_evol = df_evol[df_evol["Agglomeration"].isin(sel_entites_caf)]
                                df_evol["Metropole_Key"] = df_evol["Agglomeration"].apply(
                                    lambda x: next((m for m in COULEURS.keys() if m in x), x)
                                )
                                df_evol_agg = df_evol.groupby(
                                    ["Annee", "Metropole_Key"], as_index=False
                                )[metric_key].sum()
                                fig_evol = px.line(
                                    df_evol_agg, x="Annee", y=metric_key, color="Metropole_Key",
                                    markers=True, color_discrete_map=COULEURS,
                                    labels={
                                        "Annee": "Année", metric_key: label_metric,
                                        "Metropole_Key": "Métropole"
                                    },
                                    height=360
                                )
                                for trace in fig_evol.data:
                                    if "Grenoble" in trace.name:
                                        trace.line.dash  = "dash"
                                        trace.line.color = "#FF584D"
                                        trace.line.width = 2.5
                                        if trace.marker:
                                            trace.marker.color  = "#FF584D"
                                            trace.marker.symbol = "diamond"
                                            trace.marker.size   = 8
                            else:
                                if "Nom_Commune" in df_evol.columns:
                                    df_evol = df_evol[
                                        (df_evol["Agglomeration"] == gre_agglo) &
                                        (df_evol["Nom_Commune"].isin(sel_entites_caf))
                                    ]
                                df_evol_agg = df_evol.groupby(
                                    ["Annee", "Nom_Commune"], as_index=False
                                )[metric_key].sum()
                                fig_evol = px.line(
                                    df_evol_agg, x="Annee", y=metric_key, color="Nom_Commune",
                                    markers=True, color_discrete_sequence=PALETTE_COMMUNE_CAF,
                                    labels={
                                        "Annee": "Année", metric_key: label_metric,
                                        "Nom_Commune": "Commune"
                                    },
                                    height=360
                                )
                            fig_evol.update_traces(
                                hovertemplate=(
                                    "<b>%{fullData.name}</b><br>Année : %{x}<br>"
                                    + label_metric + " : %{y:,.0f}<extra></extra>"
                                )
                            )
                            fig_evol.update_layout(
                                legend=dict(
                                    orientation="v", yanchor="middle", y=0.5,
                                    xanchor="left", x=1.02
                                ),
                                margin=dict(t=30, r=40, b=30)
                            )
                            st.plotly_chart(style(fig_evol, 30), use_container_width=True)

                        with c4:
                            st.markdown(
                                f"##### Structure détaillée de la solidarité ({year_caf})",
                                help="Répartition en % du total par grande catégorie d'allocation."
                            )
                            INDICATEURS_GLOBAUX = [
                                "Nombre foyers NDUR",
                                "Nombre personnes NDUR",
                                "Montant total NDUR",
                            ]
                            if metric_key in INDICATEURS_GLOBAUX:
                                current_root = metric_key.split("NDUR")[0]
                                aides_struct = {
                                    "Insertion (RSA, AAH…)": current_root + "NDURINS",
                                    "Logement (APL, ALS…)":  current_root + "NDURAL",
                                    "Jeunes enfants (PAJE)":  current_root + "NDURPAJE",
                                    "Enfance & Jeunesse":     current_root + "NDUREJ",
                                }
                                aides_d = {
                                    lab: col for lab, col in aides_struct.items()
                                    if col in df_fil.columns
                                }
                                if aides_d:
                                    tot_struct  = df_fil[list(aides_d.values())].sum().sum()
                                    rows_struct = [
                                        {
                                            "Catégorie": lab,
                                            "Valeur":    df_fil[col].sum(),
                                            "Part":      df_fil[col].sum() / tot_struct * 100
                                                         if tot_struct > 0 else 0,
                                        }
                                        for lab, col in aides_d.items()
                                    ]
                                    df_struct   = pd.DataFrame(rows_struct)
                                    grey_struct = ["#444444", "#777777", "#aaaaaa", "#cccccc"]
                                    fig_struct  = px.bar(
                                        df_struct, x="Part", y="Catégorie", orientation="h",
                                        color="Catégorie", color_discrete_sequence=grey_struct,
                                        text=df_struct["Part"].apply(lambda v: f"{v:.1f}%"),
                                        labels={"Part": "% du total", "Catégorie": ""},
                                        height=360
                                    )
                                    fig_struct.update_traces(
                                        textposition="outside",
                                        hovertemplate="<b>%{y}</b><br>Part : <b>%{text}</b><extra></extra>"
                                    )
                                    fig_struct.update_layout(
                                        showlegend=False,
                                        xaxis=dict(range=[0, 60], title="% du total"),
                                        yaxis={"categoryorder": "total ascending"},
                                        margin=dict(t=30, b=30, l=10, r=60)
                                    )
                                    st.plotly_chart(style(fig_struct, 30), use_container_width=True)
                            else:
                                st.info("Sélectionnez 'Toutes aides' pour voir la structure détaillée.")

                        st.markdown("---")
                        with st.expander("Note méthodologique"):
                            st.markdown("""
                            - **Foyers aidés** : ménages percevant au moins une aide CAF  
                            - **Personnes concernées** : individus vivant dans ces foyers  
                            - **Montants (€)** : total des aides versées  
                            - **Quotient familial** : niveau de vie du foyer (revenus / parts)
                            - **Logement** : APL, ALS, ALF - **Insertion** : RSA, AAH, prime d'activité  
                            - **Jeunes enfants (PAJE)** : naissance, garde, petite enfance  
                            - **Enfance & jeunesse** : allocations familiales, rentrée scolaire
                            """)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 2 - ÉDUCATION
    # ──────────────────────────────────────────────────────────────────────────
    with s2:
        if df_eff is None or df_eff.empty:
            st.info("Fichier `education_filtre.csv` introuvable.")
        else:
            st.markdown("""
                <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> data.education.gouv -
                <a href='https://data.education.gouv.fr/explore/assets/fr-en-annuaire-education/view/' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br><br>
                <strong>Note :</strong> Données issues de l'Annuaire de l'Éducation nationale (2019). Les chiffres couvrent uniquement le premier et second degré et sont à considérer comme un ordre de grandeur.
                </div>""", unsafe_allow_html=True)

            df_eff_w   = df_eff.copy()
            metros_eff = sorted(df_eff_w["metropole"].dropna().unique())

            LABEL_NATURE = {
                "ECOLE MATERNELLE":                        "Maternelle",
                "ECOLE DE NIVEAU ELEMENTAIRE":             "Élémentaire",
                "ECOLE ELEMENTAIRE D APPLICATION":         "Élém. application",
                "ECOLE DE NIVEAU ELEMENTAIRE SPECIALISEE": "Élém. spécialisée",
                "COLLEGE":                                 "Collège",
                "LYCEE D ENSEIGNEMENT GENERAL":            "Lycée Général",
                "LYCEE ENSEIGNT GENERAL ET TECHNOLOGIQUE": "Lycée Général et Technologique",
                "LYCEE PROFESSIONNEL":                     "Lycée Pro",
                "LYCEE POLYVALENT":                        "Lycée Polyvalent",
                "SECTION D ENSEIGNEMENT PROFESSIONNEL":    "SEP",
                "ETABLISSEMENT REGIONAL D'ENSEIGNT ADAPTE":"EREA",
            }
            TYPES_ETABLISSEMENTS = list(LABEL_NATURE.keys())

            with st.container():
                filter_bar("Filtres - Établissements scolaires")
                f1, f2 = st.columns([1, 3])
                with f1:
                    filter_row_label("Niveau géographique")
                with f2:
                    mode_eff = st.radio(
                        "", ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                        key="eff_mode", horizontal=True, label_visibility="collapsed"
                    )
                if mode_eff == "Comparaison Métropoles":
                    sel_entites_eff = st.multiselect("Métropoles à comparer", metros_eff, default=shared_default_solid(metros_eff), key="eff_metros", on_change=sync_metros_solid, args=("eff_metros",))
                else:
                    communes_gre_eff = sorted(df_eff_w[df_eff_w["metropole"] == "Grenoble"]["Nom_commune"].dropna().unique())
                    sel_entites_eff  = st.multiselect("Communes de Grenoble-Alpes Métropole", communes_gre_eff, default=shared_default_communes_solid(communes_gre_eff, "eff_communes"), key="eff_communes", on_change=sync_communes_solid, args=("eff_communes",))
                natures_dispo  = sorted(df_eff_w["libelle_nature"].dropna().unique())
                c1, c2 = st.columns([1, 1])
                with c1:
                    natures_connues = [n for n in TYPES_ETABLISSEMENTS if n in natures_dispo]
                    sel_nature = st.multiselect("Type d'établissement", natures_connues, default=natures_connues, format_func=lambda n: LABEL_NATURE.get(n, n), key="eff_nature")
                    if not sel_nature:
                        sel_nature = natures_connues
                with c2:
                    sel_secteur = st.selectbox("Secteur", ["Tous", "Public", "Privé"], key="eff_secteur")
                st.markdown('</div>', unsafe_allow_html=True)

            geo_col  = "metropole" if mode_eff == "Comparaison Métropoles" else "Nom_commune"
            is_metro = (mode_eff == "Comparaison Métropoles")

            df_e = df_eff_w.copy()
            df_e = df_e[df_e["libelle_nature"].isin(sel_nature)]
            if sel_secteur != "Tous":
                df_e = df_e[df_e["Statut_public_prive"] == sel_secteur]
            if is_metro:
                df_e = df_e[df_e["metropole"].isin(sel_entites_eff)]
            else:
                df_e = df_e[(df_e["metropole"] == "Grenoble") & (df_e["Nom_commune"].isin(sel_entites_eff))]

            st.markdown("---")

            if df_e.empty or not sel_entites_eff:
                st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
            else:
                # Bloc de rendu structuré : titres clairs pour faciliter la personnalisation
                # (métropoles vs communes) sans changer le contenu des graphes.
                if is_metro:
                    st.markdown("##### Partie Métropole")
                else:
                    st.markdown("##### Partie Commune")
                total_etab   = len(df_e)
                total_eleves = int(df_e["Nombre_d_eleves"].sum())
                nb_rep       = int(df_e["Appartenance_Education_Prioritaire"].isin(["REP", "REP+"]).sum())
                kpi_border_color = "#666" if is_metro else "#1e5631"

                PALETTE_METRO_EFF   = px.colors.sequential.Greys[2:]
                PALETTE_COMMUNE_EFF = px.colors.sequential.Greens_r
                color_map_eff = COULEURS if is_metro else None
                color_seq_eff = PALETTE_METRO_EFF if is_metro else PALETTE_COMMUNE_EFF

                st.markdown("#### Synthèse des établissements scolaires")
                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown(render_solidarite_kpi("Établissements", fmt(total_etab), "Établissements recensés", kpi_border_color), unsafe_allow_html=True)
                with k2:
                    st.markdown(render_solidarite_kpi("Élèves", fmt(total_eleves), "Élèves inscrits (total)", kpi_border_color), unsafe_allow_html=True)
                with k3:
                    st.markdown(render_solidarite_kpi("Éducation Prioritaire", fmt(nb_rep), "Établissements REP / REP+", kpi_border_color), unsafe_allow_html=True)

                st.markdown("---")

                # ── Ligne 1 : Volume élèves + Nombre établissements ───────────
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Volume d'élèves", help="Nombre total d'élèves inscrits selon les filtres sélectionnés.")
                    by_entite = df_e.groupby(geo_col, as_index=False)["Nombre_d_eleves"].sum().sort_values("Nombre_d_eleves", ascending=False)
                    by_entite["text_display"] = by_entite["Nombre_d_eleves"].apply(fmt)
                    y_max_vol = by_entite["Nombre_d_eleves"].max()
                    fig_bar = px.bar(by_entite, x=geo_col, y="Nombre_d_eleves", color=geo_col,
                                     color_discrete_map=color_map_eff, color_discrete_sequence=color_seq_eff,
                                     text="text_display", labels={geo_col: "", "Nombre_d_eleves": "Élèves"}, height=360)
                    fig_bar.update_traces(textposition="inside", hovertemplate="<b>%{x}</b><br>Élèves : <b>%{text}</b><extra></extra>")
                    fig_bar.update_layout(showlegend=False, yaxis=dict(range=[0, y_max_vol * 1.15]),
                                          xaxis=dict(categoryorder="array", categoryarray=by_entite[geo_col].tolist()))
                    if is_metro:
                        apply_grenoble_hatch(fig_bar)
                    st.plotly_chart(style(fig_bar, 40), use_container_width=True)

                with c2:
                    st.markdown("##### Nombre d'établissements", help="Nombre d'établissements recensés selon les filtres sélectionnés.")
                    by_etab = df_e.groupby(geo_col, as_index=False).size().rename(columns={"size": "nb_etab"}).sort_values("nb_etab", ascending=False)
                    by_etab["text_display"] = by_etab["nb_etab"].apply(fmt)
                    y_max_etab = by_etab["nb_etab"].max()
                    fig_etab = px.bar(by_etab, x=geo_col, y="nb_etab", color=geo_col,
                                      color_discrete_map=color_map_eff, color_discrete_sequence=color_seq_eff,
                                      text="text_display", labels={geo_col: "", "nb_etab": "Établissements"}, height=360)
                    fig_etab.update_traces(textposition="inside", hovertemplate="<b>%{x}</b><br>Établissements : <b>%{text}</b><extra></extra>")
                    fig_etab.update_layout(showlegend=False, yaxis=dict(range=[0, y_max_etab * 1.15]),
                                           xaxis=dict(categoryorder="array", categoryarray=by_etab[geo_col].tolist()))
                    if is_metro:
                        apply_grenoble_hatch(fig_etab)
                    st.plotly_chart(style(fig_etab, 40), use_container_width=True)

                st.markdown("---")

                # ── Ligne 2 : REP + Taux de services spécialisés ──────────────
                c3, c4 = st.columns(2)

                with c3:
                    st.markdown("##### Établissements en éducation prioritaire",
                                help="Nombre d'établissements classés REP ou REP+ par territoire.")
                    df_rep = df_e[df_e["Appartenance_Education_Prioritaire"].isin(["REP", "REP+"])].copy()
                    df_rep["libelle_rep"] = df_rep["Appartenance_Education_Prioritaire"]
                    if df_rep.empty:
                        st.info("Aucun établissement en éducation prioritaire dans la sélection.")
                    else:
                        rep_agg   = df_rep.groupby([geo_col, "libelle_rep"], as_index=False).size().rename(columns={"size": "nb_etab"})
                        order_rep = rep_agg.groupby(geo_col)["nb_etab"].sum().sort_values(ascending=False).index.tolist()
                        y_max_rep = rep_agg.groupby(geo_col)["nb_etab"].sum().max()
                        rep_color_map = {"REP": "#888888", "REP+": "#444444"} if is_metro else {"REP": "#52B788", "REP+": "#1B4332"}
                        fig_rep = px.bar(rep_agg, x=geo_col, y="nb_etab", color="libelle_rep", barmode="stack",
                                         color_discrete_map=rep_color_map, text="nb_etab",
                                         labels={geo_col: "", "nb_etab": "Établissements", "libelle_rep": "Réseau"}, height=380)
                        fig_rep.update_traces(marker_line_width=0, hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>")
                        fig_rep.update_layout(
                            yaxis=dict(range=[0, y_max_rep * 1.15]),
                            xaxis=dict(categoryorder="array", categoryarray=order_rep),
                            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                        )
                        if is_metro:
                            gren_rep = next((a for a in order_rep if "Grenoble" in str(a)), None)
                            if gren_rep:
                                g_pos_rep = order_rep.index(gren_rep)
                                fig_rep.add_vrect(x0=g_pos_rep - 0.45, x1=g_pos_rep + 0.45,
                                                  fillcolor="rgba(255,88,77,0.10)",
                                                  line_color="#FF584D", line_width=1.5, line_dash="dash", layer="below")
                        st.plotly_chart(style(fig_rep, 40), use_container_width=True)

                with c4:
                    st.markdown("##### Taux d'établissements avec services spécialisés",
                                help="Pour 100 établissements du territoire, combien disposent de restauration, d'hébergement ou d'une ULIS.")
                    services_cols = {"Restauration": "Restauration", "Hebergement": "Hébergement", "ULIS": "ULIS"}
                    total_by_ent  = df_e.groupby(geo_col).size().rename("total")
                    rows_svc_rate = []
                    for col_svc, label_svc in services_cols.items():
                        if col_svc in df_e.columns:
                            with_svc = df_e.groupby(geo_col)[col_svc].apply(
                                lambda s: int((pd.to_numeric(s, errors="coerce").fillna(0) > 0).sum())
                            )
                            rate_svc = (with_svc / total_by_ent * 100).fillna(0).reset_index()
                            rate_svc.columns = [geo_col, "Taux (%)"]
                            rate_svc["Service"] = label_svc
                            rows_svc_rate.append(rate_svc)
                    if rows_svc_rate:
                        svc_rate = pd.concat(rows_svc_rate, ignore_index=True)
                        entites_ok = svc_rate.groupby(geo_col)["Taux (%)"].sum()
                        entites_ok = entites_ok[entites_ok > 0].index
                        svc_rate   = svc_rate[svc_rate[geo_col].isin(entites_ok)]
                        order_svc  = df_e.groupby(geo_col).size().sort_values(ascending=False).index.tolist()
                        order_svc  = [e for e in order_svc if e in entites_ok]
                        svc_color_map = {"Restauration": "#aaaaaa", "Hébergement": "#777777", "ULIS": "#444444"} if is_metro else {"Restauration": "#74C69D", "Hébergement": "#2D6A4F", "ULIS": "#1B4332"}
                        fig_svc = px.bar(
                            svc_rate, x=geo_col, y="Taux (%)", color="Service", barmode="group",
                            color_discrete_map=svc_color_map,
                            text=svc_rate["Taux (%)"].apply(lambda v: f"{v:.1f}%"),
                            labels={geo_col: "", "Taux (%)": "% des établissements", "Service": "Service"},
                            height=380
                        )
                        fig_svc.update_traces(textposition="inside", hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>")
                        fig_svc.update_layout(
                            yaxis=dict(range=[0, 110], title="% des établissements"),
                            xaxis=dict(categoryorder="array", categoryarray=order_svc),
                            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                        )
                        if is_metro:
                            gren_svc = next((a for a in order_svc if "Grenoble" in str(a)), None)
                            if gren_svc:
                                g_pos_svc = order_svc.index(gren_svc)
                                fig_svc.add_vrect(x0=g_pos_svc - 0.45, x1=g_pos_svc + 0.45,
                                                  fillcolor="rgba(255,88,77,0.10)",
                                                  line_color="#FF584D", line_width=1.5, line_dash="dash", layer="below")
                        st.plotly_chart(style(fig_svc, 40), use_container_width=True)
                    else:
                        st.info("Colonnes de services non disponibles.")

                st.markdown("---")

                with st.expander("Note méthodologique"):
                    st.markdown("""
                    - **SEP** : Section d'Enseignement Professionnel rattachée à un lycée général ou technologique.
                    - **EREA** : Établissement Régional d'Enseignement Adapté pour élèves en situation de handicap.
                    - **REP / REP+** : Réseau d'Éducation Prioritaire (renforcé), zones à forte difficulté sociale.
                    - **ULIS** : Unité Localisée pour l'Inclusion Scolaire.
                    - **Taux de services** : % des établissements du territoire disposant du service (pour 100 établissements).
                    """)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 3 - SANTÉ
    # ──────────────────────────────────────────────────────────────────────────
    with s3:
        import json
        GEOJSON_PATH          = Path("solidarite&citoyennete/data_clean/sante/Etablissements_santé_filtre.geojson")
        GEOJSON_METROS_PATH   = Path("solidarite&citoyennete/data_clean/sante/contour_metropole.geojson")
        GEOJSON_COMMUNES_PATH = Path("solidarite&citoyennete/data_clean/sante/contour_communes.geojson")

        @st.cache_data
        def charger_sante():
            with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            rows = []
            for feat in data["features"]:
                p      = feat["properties"]
                coords = feat["geometry"]["coordinates"]
                rows.append({
                    "type_etab": p.get("type_etablissement", ""),
                    "nom":       p.get("nom_etablissement") or "-",
                    "commune":   p.get("DCOE_L_LIB", p.get("commune", "")),
                    "metropole": p.get("METROPOLE",  p.get("Métropole", p.get("metropole", ""))),
                    "lon": coords[0], "lat": coords[1],
                })
            return pd.DataFrame(rows)

        @st.cache_data
        def charger_geojson_metros():
            if not GEOJSON_METROS_PATH.exists(): return None
            with open(GEOJSON_METROS_PATH, "r", encoding="utf-8") as f: return json.load(f)

        @st.cache_data
        def charger_geojson_communes():
            if not GEOJSON_COMMUNES_PATH.exists(): return None
            with open(GEOJSON_COMMUNES_PATH, "r", encoding="utf-8") as f: return json.load(f)

        # Population de référence pour calcul pour 1 000 habitants
        # Utilise df_pop si disponible (dernière année), sinon fallback
        POP_METRO_FALLBACK = {
            "Grenoble": 450000, "Montpellier": 490000,
            "Rennes": 460000, "Rouen": 500000, "Saint-Étienne": 400000,
        }

        @st.cache_data
        def get_pop_metro(df_pop_src):
            if df_pop_src is None: return POP_METRO_FALLBACK
            last_year = df_pop_src["annee"].max()
            df_last = df_pop_src[df_pop_src["annee"] == last_year]
            age_cols = [c for c in df_last.columns if "ageq_rec" in c]
            result   = {}
            for metro in df_last["metropole"].dropna().unique():
                sub = df_last[df_last["metropole"] == metro]
                result[metro] = float(pd.to_numeric(sub[age_cols].stack(), errors="coerce").sum())
            return result if result else POP_METRO_FALLBACK

        st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong>
                <a href='https://smartregionidf.opendatasoft.com/explore/dataset/osm-france-healthcare/table/' target='_blank' style='color: #1C3A27;'>Accéder aux données</a>
            </div>""", unsafe_allow_html=True)

        df_sante       = charger_sante()
        geojson_metros = charger_geojson_metros()
        geojson_communes = charger_geojson_communes()

        TYPE_LABELS = {"pharmacy":"Pharmacie","doctors":"Médecins / Soins","dentist":"Dentiste",
                       "hospital":"Hôpital","nursing_home":"EHPAD / M. retraite","clinic":"Clinique / C. santé"}
        TYPE_COLORS = {"pharmacy":"#264653","doctors":"#2a9d8f","dentist":"#e9c46a",
                       "hospital":"#f4a261","nursing_home":"#e76f51","clinic":"#5DC26E"}
        metros_sante = sorted(df_sante["metropole"].dropna().unique())
        types_sante  = sorted(df_sante["type_etab"].dropna().unique())

        with st.container():
            filter_bar("Filtres - Établissements de santé")
            fs1, fs2 = st.columns([1, 3])
            with fs1: filter_row_label("Niveau géographique")
            with fs2:
                mode_sante = st.radio("", ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                                      key="sante_mode", horizontal=True, label_visibility="collapsed")
            if mode_sante == "Comparaison Métropoles":
                sel_metros_sante = st.multiselect("Métropoles à comparer", metros_sante,
                                                   default=shared_default_solid(metros_sante),
                                                   key="sante_metros_multi", on_change=sync_metros_solid, args=("sante_metros_multi",))
            else:
                communes_sante_dispo = sorted(df_sante[df_sante["metropole"] == "Grenoble"]["commune"].dropna().unique())
                sel_communes_sante   = st.multiselect("Communes de Grenoble-Alpes Métropole", communes_sante_dispo,
                                                       default=shared_default_communes_solid(communes_sante_dispo, "sante_communes_t1"),
                                                       key="sante_communes_t1", on_change=sync_communes_solid, args=("sante_communes_t1",))
            sel_types_sante = st.multiselect("Type d'établissement", options=types_sante, default=types_sante,
                                              format_func=lambda t: TYPE_LABELS.get(t, t), key="sante_types_t1")
            st.markdown('</div>', unsafe_allow_html=True)

        if mode_sante == "Comparaison Métropoles":
            df_sf = df_sante[(df_sante["metropole"].isin(sel_metros_sante)) & (df_sante["type_etab"].isin(sel_types_sante))].copy()
            kpi_border_color = "#666"
        else:
            df_sf = df_sante[(df_sante["metropole"] == "Grenoble") & (df_sante["commune"].isin(sel_communes_sante)) & (df_sante["type_etab"].isin(sel_types_sante))].copy()
            kpi_border_color = "#1e5631"

        st.markdown("---")
        if mode_sante == "Comparaison Métropoles":
            # Métropoles : KPIs + carte + graphes (tout le rendu ci-dessous)
            st.markdown("##### Partie Métropole")
        else:
            # Communes (Grenoble-Alpes Métropole) : même structure, rendu séparé
            st.markdown("##### Partie Commune")
        st.markdown("#### Synthèse de l'offre de soins")
        sk1, sk2, sk3, sk4, sk5 = st.columns(5)
        with sk1: st.markdown(render_solidarite_kpi("Total", fmt(len(df_sf)), "Établissements", kpi_border_color), unsafe_allow_html=True)
        with sk2: st.markdown(render_solidarite_kpi("Pharmacies", fmt(len(df_sf[df_sf["type_etab"] == "pharmacy"])), "Officines", kpi_border_color), unsafe_allow_html=True)
        with sk3: st.markdown(render_solidarite_kpi("Médecins", fmt(len(df_sf[df_sf["type_etab"] == "doctors"])), "Cabinets", kpi_border_color), unsafe_allow_html=True)
        with sk4: st.markdown(render_solidarite_kpi("Hôpitaux", fmt(len(df_sf[df_sf["type_etab"] == "hospital"])), "Centres hospitaliers", kpi_border_color), unsafe_allow_html=True)
        with sk5: st.markdown(render_solidarite_kpi("Périmètre", fmt(df_sf["commune"].nunique()), "Communes", kpi_border_color), unsafe_allow_html=True)

        st.markdown("---")

        import math
        def bbox_from_features(features):
            lons, lats = [], []
            for feat in features:
                geom = feat.get("geometry", {}); t = geom.get("type", "")
                if t == "Point": lons.append(geom["coordinates"][0]); lats.append(geom["coordinates"][1])
                elif t == "Polygon":
                    for ring in geom["coordinates"]:
                        for c in ring: lons.append(c[0]); lats.append(c[1])
                elif t == "MultiPolygon":
                    for poly in geom["coordinates"]:
                        for ring in poly:
                            for c in ring: lons.append(c[0]); lats.append(c[1])
            if not lons: return None
            return min(lats), max(lats), min(lons), max(lons)

        def zoom_from_bbox(bbox, map_width_px=1200, map_height_px=480, margin=1.3):
            lat_min, lat_max, lon_min, lon_max = bbox
            span_lat = max((lat_max - lat_min) * margin, 0.01)
            span_lon = max((lon_max - lon_min) * margin, 0.01)
            zoom_lon = math.log2(360 / span_lon) + math.log2(map_width_px / 256)
            zoom_lat = math.log2(180 / span_lat) + math.log2(map_height_px / 256)
            return round(min(zoom_lon, zoom_lat) - 0.5, 1)

        if mode_sante == "Comparaison Métropoles" and geojson_metros and sel_metros_sante:
            feats_zoom = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") in sel_metros_sante]
        elif mode_sante == "Comparaison communes Grenoble-Alpes Métropole" and geojson_communes and sel_communes_sante:
            feats_zoom = [f for f in geojson_communes["features"] if f["properties"].get("DCOE_L_LIB") in sel_communes_sante]
        else:
            feats_zoom = []

        bbox = bbox_from_features(feats_zoom)
        if bbox:
            lat_min, lat_max, lon_min, lon_max = bbox
            lat_c, lon_c, zoom_level = (lat_min+lat_max)/2, (lon_min+lon_max)/2, zoom_from_bbox(bbox)
        elif not df_sf.empty:
            bbox_pts = bbox_from_features([{"geometry": {"type": "Point", "coordinates": [r.lon, r.lat]}} for _, r in df_sf.iterrows()])
            lat_c, lon_c, zoom_level = (bbox_pts[0]+bbox_pts[1])/2, (bbox_pts[2]+bbox_pts[3])/2, zoom_from_bbox(bbox_pts)
        else:
            lat_c, lon_c, zoom_level = 46.5, 2.5, 5

        mapbox_layers = []
        if mode_sante == "Comparaison Métropoles" and geojson_metros:
            feats_f = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") in sel_metros_sante]
            if feats_f: mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_f}, "type": "line", "color": "#2D6A4F", "line": {"width": 2}, "opacity": 0.8})
        elif mode_sante == "Comparaison communes Grenoble-Alpes Métropole":
            if geojson_communes:
                feats_c = [f for f in geojson_communes["features"] if f["properties"].get("DCOE_L_LIB") in sel_communes_sante]
                if feats_c: mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_c}, "type": "line", "color": "#40916C", "line": {"width": 1.5}, "opacity": 0.9})
            if geojson_metros:
                feats_g = [f for f in geojson_metros["features"] if f["properties"].get("METROPOLE") == "Grenoble"]
                if feats_g: mapbox_layers.append({"source": {"type": "FeatureCollection", "features": feats_g}, "type": "line", "color": "#1B4332", "line": {"width": 2.5}, "opacity": 0.6})

        st.markdown("##### Carte de l'offre de santé", help="Localisation des établissements extraits via OpenStreetMap.")
        if df_sf.empty:
            st.info("Aucun établissement pour ces filtres.")
        else:
            fig_map = px.scatter_mapbox(
                df_sf, lat="lat", lon="lon", color="type_etab",
                color_discrete_map=TYPE_COLORS, hover_name="nom",
                hover_data={"commune": True, "metropole": True, "type_etab": False, "lat": False, "lon": False},
                labels={"type_etab": "Type", "commune": "Commune", "metropole": "Métropole"},
                height=480, mapbox_style="carto-positron"
            )
            for trace in fig_map.data:
                trace.name = TYPE_LABELS.get(trace.name, trace.name)
                trace.hovertemplate = "<b>%{hovertext}</b><br>Commune : <b>%{customdata[0]}</b><br>Métropole : <b>%{customdata[1]}</b><extra></extra>"
            fig_map.update_layout(
                mapbox_zoom=zoom_level, mapbox_center={"lat": lat_c, "lon": lon_c},
                mapbox_layers=mapbox_layers,
                legend=dict(title="Type", orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
                            bgcolor="rgba(255,255,255,0.85)", bordercolor="#C8E6D4", borderwidth=1, font=dict(size=11)),
                margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", font_family="Sora"
            )
            st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")
        extra1, extra2 = st.columns(2)

        with extra1:
            if mode_sante == "Comparaison Métropoles":
                st.markdown("##### Offre de soins par métropole et type", help="Nombre absolu d'établissements identifiés par type de soin.")
                df_pivot = df_sf.groupby(["metropole", "type_etab"]).size().reset_index(name="count")
                df_pivot["text_display"] = df_pivot["count"].apply(fmt)
                y_max_stack = df_pivot.groupby("metropole")["count"].sum().max()
                order_stack = df_pivot.groupby("metropole")["count"].sum().sort_values(ascending=False).index.tolist()
                fig_stack = px.bar(df_pivot, x="metropole", y="count", color="type_etab",
                                   color_discrete_map=TYPE_COLORS, text="text_display",
                                   labels={"metropole": "", "count": "Nombre", "type_etab": "Type"}, height=360, barmode="stack")
                fig_stack.update_traces(textposition="inside", textfont_size=10,
                                        hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>")
                for trace in fig_stack.data: trace.name = TYPE_LABELS.get(trace.name, trace.name)
                if "Grenoble" in order_stack:
                    g_pos_sante = order_stack.index("Grenoble")
                    fig_stack.add_vrect(x0=g_pos_sante - 0.45, x1=g_pos_sante + 0.45,
                                       fillcolor="rgba(255,88,77,0.10)", line_color="#FF584D",
                                       line_width=1.5, line_dash="dash", layer="below")
                fig_stack.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                    yaxis=dict(range=[0, y_max_stack * 1.1]),
                    xaxis=dict(tickangle=-30, categoryorder="array", categoryarray=order_stack),
                    legend=dict(title="Type", orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10))
                )
                st.plotly_chart(style(fig_stack, 40), use_container_width=True)
            else:
                st.markdown("##### Densité par commune", help="Nombre absolu d'établissements identifiés par commune.")
                df_comm = df_sf.groupby(["commune", "type_etab"]).size().reset_index(name="count")
                df_comm["text_display"] = df_comm["count"].apply(fmt)
                y_max_comm  = df_comm.groupby("commune")["count"].sum().max()
                order_comm  = df_comm.groupby("commune")["count"].sum().sort_values(ascending=False).index.tolist()
                fig_comm = px.bar(df_comm, x="commune", y="count", color="type_etab",
                                  color_discrete_map=TYPE_COLORS, text="text_display",
                                  labels={"commune": "", "count": "Nombre", "type_etab": "Type"}, height=360, barmode="stack")
                fig_comm.update_traces(textposition="inside", textfont_size=10,
                                       hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>")
                for trace in fig_comm.data: trace.name = TYPE_LABELS.get(trace.name, trace.name)
                fig_comm.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                    yaxis=dict(range=[0, y_max_comm * 1.1]),
                    xaxis=dict(tickangle=-30, categoryorder="array", categoryarray=order_comm),
                    legend=dict(title="Type", orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=10))
                )
                st.plotly_chart(style(fig_comm, 40), use_container_width=True)

        with extra2:
            if mode_sante == "Comparaison Métropoles":
                st.markdown("##### Établissements pour 1 000 habitants",
                            help="Nombre d'établissements de santé rapporté à 1 000 habitants, pour une comparaison indépendante de la taille des métropoles.")
                pop_dict = get_pop_metro(df_pop)
                rows_rate = []
                for metro in sel_metros_sante:
                    pop_m = pop_dict.get(metro, None)
                    if pop_m and pop_m > 0:
                        for t_etab in sel_types_sante:
                            nb = len(df_sf[(df_sf["metropole"] == metro) & (df_sf["type_etab"] == t_etab)])
                            rows_rate.append({
                                "Métropole": metro,
                                "Type":      TYPE_LABELS.get(t_etab, t_etab),
                                "Pour 1 000 hab.": round(nb / pop_m * 1000, 3),
                            })
                if rows_rate:
                    df_rate = pd.DataFrame(rows_rate)
                    is_gren_fn = lambda m: m == "Grenoble"
                    fig_rate = go.Figure()
                    for metro in sel_metros_sante:
                        df_m_r    = df_rate[df_rate["Métropole"] == metro]
                        is_gren   = is_gren_fn(metro)
                        bar_color = COULEURS.get(metro, "#888")
                        fig_rate.add_trace(go.Bar(
                            x=df_m_r["Type"], y=df_m_r["Pour 1 000 hab."],
                            name=metro,
                            marker_color=bar_color,
                            hovertemplate=f"<b>{metro}</b><br>%{{x}}<br>Pour 1 000 hab. : <b>%{{y:.3f}}</b><extra></extra>",
                        ))
                        if is_gren:
                            fig_rate.data[-1].marker.pattern.shape    = "/"
                            fig_rate.data[-1].marker.pattern.fgcolor  = "#FF584D"
                            fig_rate.data[-1].marker.pattern.size     = 20
                            fig_rate.data[-1].marker.pattern.solidity = 0.3
                    fig_rate.update_layout(
                        barmode="group",
                        xaxis=dict(title="", tickangle=-30),
                        yaxis=dict(title="Établissements / 1 000 hab.", showgrid=True, gridcolor="#eee"),
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        height=360, margin=dict(t=30, b=80, r=40),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                    )
                    st.plotly_chart(style(fig_rate, 30), use_container_width=True)
                    st.markdown(
                        "<p style='font-size:11px;color:#888;'>"
                        "Population de référence issue des recensements INSEE (dernière année disponible)."
                        "</p>", unsafe_allow_html=True
                    )
                else:
                    st.info("Données de population insuffisantes pour calculer les ratios.")
            else:
                st.markdown("##### Part de chaque type d'établissement", help="Répartition relative de l'offre de soins sur les communes sélectionnées.")
                pie_data = df_sf.groupby("type_etab").size().reset_index(name="count")
                pie_data["label"] = pie_data["type_etab"].map(lambda t: TYPE_LABELS.get(t, t))
                fig_pie = px.pie(pie_data, names="label", values="count", color="type_etab",
                                 color_discrete_map=TYPE_COLORS, height=360, hole=0.4)
                fig_pie.update_traces(textposition="inside", textinfo="percent+label", pull=[0.03]*len(pie_data),
                                      hovertemplate="<b>%{label}</b><br>Établissements : <b>%{value:,.0f}</b><br>Part : <b>%{percent}</b><extra></extra>")
                fig_pie.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font_family="Sora", margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)

    # ──────────────────────────────────────────────────────────────────────────
    # ONGLET 4 - PARTICIPATION CITOYENNE
    # ──────────────────────────────────────────────────────────────────────────
    with s4:
        @st.cache_data
        def charger_elections():
            df_muni_2014 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/elections_2014_2020.csv")
            df_muni_2014 = df_muni_2014[df_muni_2014["Année"] == 2014].copy()
            df_muni_2014["Type d'élection"] = "Municipales"
            df_muni_2020 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/elections_2014_2020.csv")
            df_muni_2020 = df_muni_2020[df_muni_2020["Année"] == 2020].copy()
            df_muni_2020["Type d'élection"] = "Municipales"
            df_muni_2026 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/municipales_2026.csv")
            df_muni_2026["Type d'élection"] = "Municipales"
            df_muni_2026["Libellé de la commune"] = df_muni_2026["Libellé de la commune"].replace("Oissel-sur-Seine", "Oissel")
            df_p17 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/presidentielle_2017.csv")
            df_p17["Type d'élection"] = "Présidentielles"
            df_p22 = pd.read_csv("solidarite&citoyennete/data_clean/participation_citoyenne/presidentielle_2022.csv")
            df_p22["Type d'élection"] = "Présidentielles"
            return pd.concat([df_muni_2014, df_muni_2020, df_muni_2026, df_p17, df_p22], ignore_index=True)

        df_elec = charger_elections()
        DEP_METRO_ELEC = {
            "Isère": "Grenoble", "Ille-et-Vilaine": "Rennes",
            "Seine-Maritime": "Rouen", "Loire": "Saint-Étienne", "Hérault": "Montpellier"
        }
        df_elec["metropole"]       = df_elec["Libellé du département"].map(DEP_METRO_ELEC)
        df_elec["% Participation"] = 100 - df_elec["% Abs/Ins"]

        tours_elec  = sorted(df_elec["Numéro de tour"].dropna().unique().astype(int))
        metros_elec = sorted(df_elec["metropole"].dropna().unique())

        st.markdown("""
            <div style='background-color: #f1f8f5; padding: 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 14px;'>
                <strong>Sources :</strong> data.gouv.fr<br>
                <b>Présidentielle 2022</b> :
                    1er tour : <a href='https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-1er-tour' target='_blank' style='color: #1C3A27;'>Accéder aux données</a> -
                    2ème tour : <a href='https://www.data.gouv.fr/datasets/election-presidentielle-des-10-et-24-avril-2022-resultats-definitifs-du-2nd-tour' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br>
                <b>Municipales 2026</b> :
                    1er tour : <a href='https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-premier-tour' target='_blank' style='color: #1C3A27;'>Accéder aux données</a> -
                    2ème tour : <a href='https://www.data.gouv.fr/datasets/elections-municipales-2026-resultats-du-second-tour' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br><br>
                <strong>Note :</strong> Les élections municipales de 2020 se sont tenues en pleine crise sanitaire COVID-19,
                ce qui a fortement impacté la participation. Les taux sont donc exceptionnellement bas
                et ne reflètent pas le comportement électoral habituel.
            </div>""", unsafe_allow_html=True)

        with st.container():
            filter_bar("Filtres - Participation citoyenne")
            ft1, ft2 = st.columns([1, 3])
            with ft1:
                filter_row_label("Type d'élection")
            with ft2:
                type_election = st.radio(
                    "", ["Municipales", "Présidentielles"],
                    key="part_type_election", horizontal=True, label_visibility="collapsed"
                )
            df_elec_type = df_elec[df_elec["Type d'élection"] == type_election]
            annees_elec  = sorted(df_elec_type["Année"].dropna().unique().astype(int))

            fp1, fp2 = st.columns([1, 3])
            with fp1:
                filter_row_label("Niveau géographique")
            with fp2:
                mode_part = st.radio(
                    "", ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                    key="part_mode", horizontal=True, label_visibility="collapsed"
                )

            if mode_part == "Comparaison communes Grenoble-Alpes Métropole":
                communes_elec_dispo = sorted(
                    df_elec_type[df_elec_type["metropole"] == "Grenoble"]["Libellé de la commune"]
                    .dropna().unique()
                )
                sel_communes_part = st.multiselect(
                    "Communes de Grenoble-Alpes Métropole", communes_elec_dispo,
                    default=shared_default_communes_solid(communes_elec_dispo, "part_communes"),
                    key="part_communes", on_change=sync_communes_solid, args=("part_communes",)
                )
            else:
                sel_metros_part = st.multiselect(
                    "Métropoles à comparer", metros_elec,
                    default=shared_default_solid(metros_elec),
                    key="part_metros", on_change=sync_metros_solid, args=("part_metros",)
                )

            fc1, fc2 = st.columns(2)
            with fc1:
                label_annee    = "Année (Municipales)" if type_election == "Municipales" else "Année (Présidentielles)"
                sel_annee_part = st.selectbox(label_annee, annees_elec, index=len(annees_elec)-1, key="part_annee")
            with fc2:
                sel_tour_part  = st.selectbox("Tour", tours_elec, format_func=lambda t: f"Tour {t}", key="part_tour")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Sections distinctes par niveau géographique (métropole / commune) ─
        mode_part_metro = (mode_part == "Comparaison Métropoles")

        df_elec_f = df_elec_type[
            (df_elec_type["Année"] == sel_annee_part) &
            (df_elec_type["Numéro de tour"] == sel_tour_part)
        ]

        if mode_part_metro:
            df_elec_f = df_elec_f[df_elec_f["metropole"].isin(sel_metros_part)]
            df_agg    = df_elec_f.groupby("metropole", as_index=False).agg(
                Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum"),
                Abstentions=("Abstentions", "sum"),
                Non_Exprimes=("Non-Exprimés", "sum"),
                Exprimes=("Exprimés", "sum")
            )
            kpi_border_color = "#666"
        else:
            df_elec_f = df_elec_f[df_elec_f["Libellé de la commune"].isin(sel_communes_part)]
            df_agg    = df_elec_f.groupby("Libellé de la commune", as_index=False).agg(
                Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum"),
                Abstentions=("Abstentions", "sum"),
                Non_Exprimes=("Non-Exprimés", "sum"),
                Exprimes=("Exprimés", "sum")
            )
            df_agg = df_agg.rename(columns={"Libellé de la commune": "metropole"})
            kpi_border_color = "#1e5631"

        df_agg["% Participation"] = (df_agg["Votants"]     / df_agg["Inscrits"] * 100).round(2)
        df_agg["% Abstention"]    = (df_agg["Abstentions"] / df_agg["Inscrits"] * 100).round(2)
        df_agg["% Non-Exprimés"]  = (df_agg["Non_Exprimes"] / df_agg["Votants"] * 100).round(2)
        df_agg["% Exprimés"]      = (df_agg["Exprimes"]    / df_agg["Votants"]  * 100).round(2)

        st.markdown("---")

        if not df_agg.empty:
            total_inscrits    = int(df_agg["Inscrits"].sum())
            total_votants     = int(df_agg["Votants"].sum())
            total_non_exp     = int(df_agg["Non_Exprimes"].sum())
            total_abstentions = int(df_agg["Abstentions"].sum())
            taux_part_global  = round(total_votants     / total_inscrits * 100, 1) if total_inscrits else 0
            taux_abs_global   = round(total_abstentions / total_inscrits * 100, 1) if total_inscrits else 0
            taux_non_exp_gl   = round(total_non_exp     / total_votants  * 100, 1) if total_votants  else 0

            st.markdown(f"#### Bilan Électoral - {type_election} {sel_annee_part} (Tour {sel_tour_part})")
            kpi_cols = st.columns(4)
            with kpi_cols[0]:
                st.markdown(render_solidarite_kpi("Inscrits",      fmt(total_inscrits),    "Listes électorales",     kpi_border_color), unsafe_allow_html=True)
            with kpi_cols[1]:
                st.markdown(render_solidarite_kpi("Participation", f"{taux_part_global} %", "Votants / Inscrits",    kpi_border_color), unsafe_allow_html=True)
            with kpi_cols[2]:
                st.markdown(render_solidarite_kpi("Abstention",    f"{taux_abs_global} %",  "Absents / Inscrits",    kpi_border_color), unsafe_allow_html=True)
            with kpi_cols[3]:
                st.markdown(render_solidarite_kpi("Blancs & Nuls", f"{taux_non_exp_gl} %",  "Non-exprimés / Votants",kpi_border_color), unsafe_allow_html=True)

        st.markdown("---")

        if df_agg.empty:
            st.warning("⚠️ Aucune donnée pour les filtres sélectionnés.")
        else:
            # ════════════════════════════════════════════════════════════════════
            # VUE METROPOLES
            # ════════════════════════════════════════════════════════════════════
            if mode_part_metro:
                # VUE METROPOLES : KPIs/graphes dédiés (éditer ici n'impacte pas la vue communes)
                c1, c2 = st.columns(2)

                with c1:
                    # Participation : taux de participation (votants / inscrits)
                    st.markdown("##### Taux de participation",
                                help="Votants / Inscrits × 100. Inclut les votes blancs et nuls.")
                    df_part_sorted = df_agg.sort_values("% Participation", ascending=True)
                    df_part_sorted["text_display"] = df_part_sorted["% Participation"].apply(lambda v: f"{v:.1f} %")
                    fig_part = px.bar(
                        df_part_sorted, x="% Participation", y="metropole", orientation="h",
                        color="metropole", color_discrete_map=COULEURS, text="text_display",
                        labels={"metropole": "", "% Participation": "Participation (%)"}, height=380
                    )
                    fig_part.update_traces(
                        textposition="outside",
                        hovertemplate="<b>%{y}</b><br>Participation : <b>%{text}</b><extra></extra>"
                    )
                    fig_part.update_layout(
                        showlegend=False, xaxis_range=[0, 100],
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                        margin=dict(l=10, r=40, t=40, b=10)
                    )
                    apply_grenoble_hatch(fig_part, active=True)
                    st.plotly_chart(style(fig_part, 40), use_container_width=True)

                with c2:
                    # Qualité du vote : exprimés vs non-exprimés
                    st.markdown("##### Qualité du vote",
                                help="Parmi les votants : proportion de votes valides (Exprimés) vs blancs/nuls (Non-Exprimés).")
                    df_qual = df_agg[["metropole", "% Exprimés", "% Non-Exprimés"]].melt(
                        id_vars="metropole", var_name="Type", value_name="Taux"
                    )
                    df_qual["text_display"] = df_qual["Taux"].apply(lambda v: f"{v:.1f} %")
                    order_qual = df_agg.sort_values("% Exprimés", ascending=False)["metropole"].tolist()
                    fig_qual = px.bar(
                        df_qual, x="metropole", y="Taux", color="Type", barmode="stack",
                        color_discrete_map={"% Exprimés": "#555555", "% Non-Exprimés": "#aaaaaa"},
                        text="text_display", labels={"metropole": "", "Taux": "%", "Type": ""}, height=380
                    )
                    fig_qual.update_traces(
                        hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                    )
                    if "Grenoble" in order_qual:
                        g_pos_qual = order_qual.index("Grenoble")
                        fig_qual.add_vrect(
                            x0=g_pos_qual - 0.45, x1=g_pos_qual + 0.45,
                            fillcolor="rgba(255,88,77,0.10)", line_color="#FF584D",
                            line_width=1.5, line_dash="dash", layer="below"
                        )
                    fig_qual.update_layout(
                        yaxis_range=[0, 100],
                        xaxis=dict(categoryorder="array", categoryarray=order_qual),
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", yaxis=dict(gridcolor="#E8F5EE"),
                        margin=dict(l=10, r=10, t=40, b=10)
                    )
                    st.plotly_chart(style(fig_qual, 40), use_container_width=True)

            # ════════════════════════════════════════════════════════════════════
            # VUE COMMUNES
            # ════════════════════════════════════════════════════════════════════
            else:
                # VUE COMMUNES : KPIs/graphes dédiés (sélection des communes Grenoble-Alpes Métropole)
                c1, c2 = st.columns(2)

                with c1:
                    # Participation : taux de participation (votants / inscrits)
                    st.markdown("##### Taux de participation",
                                help="Votants / Inscrits × 100. Inclut les votes blancs et nuls.")
                    df_part_sorted = df_agg.sort_values("% Participation", ascending=True)
                    df_part_sorted["text_display"] = df_part_sorted["% Participation"].apply(lambda v: f"{v:.1f} %")
                    fig_part = px.bar(
                        df_part_sorted, x="% Participation", y="metropole", orientation="h",
                        color="metropole", color_discrete_sequence=px.colors.sequential.Greens_r,
                        text="text_display", labels={"metropole": "", "% Participation": "Participation (%)"}, height=380
                    )
                    fig_part.update_traces(
                        textposition="outside",
                        hovertemplate="<b>%{y}</b><br>Participation : <b>%{text}</b><extra></extra>"
                    )
                    fig_part.update_layout(
                        showlegend=False, xaxis_range=[0, 100],
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                        margin=dict(l=10, r=40, t=40, b=10)
                    )
                    apply_grenoble_hatch(fig_part, active=False)
                    st.plotly_chart(style(fig_part, 40), use_container_width=True)

                with c2:
                    # Qualité du vote : exprimés vs non-exprimés
                    st.markdown("##### Qualité du vote",
                                help="Parmi les votants : proportion de votes valides (Exprimés) vs blancs/nuls (Non-Exprimés).")
                    df_qual = df_agg[["metropole", "% Exprimés", "% Non-Exprimés"]].melt(
                        id_vars="metropole", var_name="Type", value_name="Taux"
                    )
                    df_qual["text_display"] = df_qual["Taux"].apply(lambda v: f"{v:.1f} %")
                    order_qual = df_agg.sort_values("% Exprimés", ascending=False)["metropole"].tolist()
                    fig_qual = px.bar(
                        df_qual, x="metropole", y="Taux", color="Type", barmode="stack",
                        color_discrete_map={"% Exprimés": "#2D6A4F", "% Non-Exprimés": "#95D5B2"},
                        text="text_display", labels={"metropole": "", "Taux": "%", "Type": ""}, height=380
                    )
                    fig_qual.update_traces(
                        hovertemplate="<b>%{x}</b><br>%{fullData.name} : <b>%{text}</b><extra></extra>"
                    )
                    fig_qual.update_layout(
                        yaxis_range=[0, 100],
                        xaxis=dict(categoryorder="array", categoryarray=order_qual),
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora", yaxis=dict(gridcolor="#E8F5EE"),
                        margin=dict(l=10, r=10, t=40, b=10)
                    )
                    st.plotly_chart(style(fig_qual, 40), use_container_width=True)

            st.markdown("---")

            # ── Évolution de la participation ─────────────────────────────────
            if type_election == "Municipales":
                annee_debut, annee_fin = 2014, 2026
                elections_label = f"Municipales {annee_debut} → {annee_fin} · Tour {sel_tour_part}"
                help_evolution  = f"Variation en points de pourcentage entre les municipales {annee_debut} et {annee_fin} (tour {sel_tour_part})."
            else:
                annee_debut, annee_fin = 2017, 2022
                elections_label = f"Présidentielles {annee_debut} → {annee_fin} · Tour {sel_tour_part}"
                help_evolution  = f"Variation en points de pourcentage entre les présidentielles {annee_debut} et {annee_fin} (tour {sel_tour_part})."

            st.markdown(
                f"##### Évolution de la participation - *{elections_label}*",
                help=help_evolution
            )
            st.markdown(
                f"<p style='font-size:11px;color:#888;margin-top:-10px;margin-bottom:10px;'>"
                f"📋 Élections : <b>{type_election}</b> · Périmètre : <b>"
                f"{'Comparaison Métropoles' if mode_part_metro else 'Communes Grenoble-Alpes Métropole'}</b> · "
                f"Tour <b>{sel_tour_part}</b> · Variation entre <b>{annee_debut}</b> et <b>{annee_fin}</b>"
                f"</p>",
                unsafe_allow_html=True
            )

            df_delta_base = df_elec_type[df_elec_type["Numéro de tour"] == sel_tour_part].copy()
            if mode_part_metro:
                df_delta_base = df_delta_base[df_delta_base["metropole"].isin(sel_metros_part)]
                grp_col = "metropole"
            else:
                df_delta_base = df_delta_base[df_delta_base["Libellé de la commune"].isin(sel_communes_part)]
                grp_col = "Libellé de la commune"

            df_delta_agg = df_delta_base.groupby(["Année", grp_col], as_index=False).agg(
                Inscrits=("Inscrits", "sum"), Votants=("Votants", "sum")
            )
            df_delta_agg["% Participation"] = (
                df_delta_agg["Votants"] / df_delta_agg["Inscrits"] * 100
            ).round(2)

            df_debut = df_delta_agg[df_delta_agg["Année"] == annee_debut].set_index(grp_col)["% Participation"]
            df_fin   = df_delta_agg[df_delta_agg["Année"] == annee_fin].set_index(grp_col)["% Participation"]
            df_delta = (df_fin - df_debut).dropna().reset_index()
            df_delta.columns    = ["entite", "Δ Participation (pts)"]
            df_delta            = df_delta.sort_values("Δ Participation (pts)")
            df_delta["couleur"] = df_delta["Δ Participation (pts)"].apply(
                lambda v: "#e76f51" if v < 0 else "#2D6A4F"
            )
            df_delta["text_display"] = df_delta["Δ Participation (pts)"].apply(
                lambda v: f"{v:+.1f} pts"
            )

            if not df_delta.empty:
                fig_delta = px.bar(
                    df_delta, x="Δ Participation (pts)", y="entite", orientation="h",
                    color="couleur", color_discrete_map="identity",
                    text="text_display",
                    labels={"entite": "", "Δ Participation (pts)": f"Variation (pts) {annee_debut}→{annee_fin}"},
                    height=max(300, len(df_delta) * 50)
                )
                fig_delta.update_traces(
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Variation : <b>%{text}</b><extra></extra>"
                )
                fig_delta.add_vline(x=0, line_dash="dash", line_color="#888", line_width=1)

                if mode_part_metro:
                    entites_delta = df_delta["entite"].tolist()
                    if "Grenoble" in entites_delta:
                        g_pos_delta = entites_delta.index("Grenoble")
                        fig_delta.add_hrect(
                            y0=g_pos_delta - 0.45, y1=g_pos_delta + 0.45,
                            fillcolor="rgba(255,88,77,0.10)", line_color="#FF584D",
                            line_width=1.5, line_dash="dash", layer="below"
                        )
                fig_delta.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora", xaxis=dict(gridcolor="#E8F5EE"),
                    margin=dict(l=10, r=60, t=40, b=10)
                )
                # Hachures uniquement en mode métropoles
                apply_grenoble_hatch(fig_delta, active=mode_part_metro)
                st.plotly_chart(style(fig_delta), use_container_width=True)
            else:
                st.info("Données insuffisantes pour calculer la variation.")

            st.markdown("---")

            # ── Fiche méthodologique ──────────────────────────────────────────
            with st.expander("Fiche méthodologique - Définitions et calculs des indicateurs"):
                st.markdown(f"""
**Périmètre des données**

Les données proviennent des résultats officiels publiés sur data.gouv.fr.
Chaque ligne correspond aux résultats agrégés d'une commune pour un tour donné.
En mode *Comparaison Métropoles*, les résultats de toutes les communes du département
de référence sont sommés pour reconstituer un indicateur métropolitain.

---

**Indicateurs affichés**

| Indicateur | Formule | Interprétation |
|---|---|---|
| **Taux de participation** | Votants ÷ Inscrits × 100 | Part des électeurs inscrits ayant effectivement voté (bulletins blancs et nuls inclus) |
| **Taux d'abstention** | Abstentions ÷ Inscrits × 100 | Part des inscrits n'ayant pas voté - complément du taux de participation |
| **Blancs & Nuls** | Non-exprimés ÷ Votants × 100 | Parmi ceux qui se sont déplacés, part des votes non comptabilisés dans les suffrages exprimés |
| **Exprimés** | Exprimés ÷ Votants × 100 | Parmi ceux qui se sont déplacés, part des votes valides (hors blancs et nuls) |
| **Évolution (pts)** | Participation {annee_fin} − Participation {annee_debut} | Variation en points de pourcentage entre les deux scrutins de même nature et de même tour |

---

**Note sur les municipales 2020**

Le 1er tour des municipales 2020 s'est tenu le 15 mars 2020, en pleine première vague de Covid-19.
Le 2nd tour a été repoussé au 28 juin 2020. La participation a chuté de manière exceptionnelle
(−16 pts en moyenne nationale par rapport à 2014). Ces chiffres ne reflètent pas
le comportement électoral structurel des territoires et doivent être interprétés avec précaution.
                """)

# ==============================================================================
# PAGE ENVIRONNEMENT
# ==============================================================================
if vue == "Environnement":
    tab_env1, tab_env2, tab_env3, tab_env4 = st.tabs([
        "🏗️  Artificialisation des sols",
        "🍃  Qualité de l'air",
        "💧  Assainissement",
        "♻️  Déchets & Transition",
    ])

    
    # ==============================================================================
    # ONGLET 1 - ARTIFICIALISATION DES SOLS 
    # ==============================================================================

    with tab_env1:
        if df_artif is None:
            st.info("📂 Fichier `artificialisation_des_sols_clean.csv` introuvable.")
        else:
            st.markdown("""
            <div style='background-color:#f1f8f5;padding:10px 15px;border-radius:10px;
                        border-left:5px solid #1C3A27;margin-bottom:20px;font-size:0.85em;'>
                <strong>Source :</strong> data.gouv.fr - 
                <a href='https://www.data.gouv.fr/datasets/artificialisation-des-sols-donnees-par-region-departement-scot-commune-et-epci'
                   target='_blank' style='color:#1C3A27;'>Accéder aux données</a><br><br>
                <strong>Note :</strong> L'artificialisation correspond au solde entre surfaces
                artificialisées et désartificialisées sur une période de <b>3 ans</b>, calculé à
                partir de l'OCSGE (Occupation du Sol à Grande Échelle). Les millésimes varient
                selon les territoires (premiers : 2016–2019 ; seconds : 2019–2022).
            </div>""", unsafe_allow_html=True)

            # ── Conversion m² → ha ────────────────────────────────────────────
            df_artif = df_artif.copy()
            for col_m2, col_ha in [
                ("surface_artif_1", "surface_artif_1_ha"),
                ("surface_artif_2", "surface_artif_2_ha"),
                ("flux_surface_1_2", "flux_surface_ha"),
                ("commune_surface",  "commune_surface_ha"),
            ]:
                df_artif[col_ha] = df_artif[col_m2] / 10_000
            df_artif["duree_periode"] = df_artif["millesimes_2"] - df_artif["millesimes_1"]

            # ── Filtres ───────────────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Artificialisation des sols")
                fz1, fz2 = st.columns([1, 3])
                with fz1:
                    filter_row_label("Niveau géographique")
                with fz2:
                    mode_artif = st.radio(
                        "",
                        ["Comparaison Métropoles",
                         "Comparaison communes Grenoble-Alpes Métropole"],
                        key="env_artif_mode", horizontal=True,
                        label_visibility="collapsed", # Permet d'être sur la même ligne que Niveau géographique
                    )

                if mode_artif == "Comparaison Métropoles":
                    sel_metros_artif = st.multiselect(
                        "Métropoles à comparer", TOUTES,
                        default=shared_default_env(TOUTES),
                        key="env_artif_metros",
                        on_change=sync_metros_env, args=("env_artif_metros",),
                    )
                    targets_artif = sel_metros_artif
                else:
                    communes_artif_dispo = sorted(COMMUNES["Grenoble"])
                    sel_communes_artif = st.multiselect(
                        "Communes de Grenoble-Alpes Métropole",
                        communes_artif_dispo,
                        default=shared_default_communes_env(communes_artif_dispo),
                        key="env_artif_communes",
                        on_change=sync_communes_env, args=("env_artif_communes",),
                    )
                    targets_artif = sel_communes_artif

            st.markdown("---")

            if not targets_artif:
                st.warning("Sélectionnez au moins un territoire.")
                st.stop()

            mode_artif_metro = (mode_artif == "Comparaison Métropoles")

            # ── Agrégation ────────────────────────────────────────────────────
            if mode_artif_metro:
                df_f = df_artif[df_artif["metropole"].isin(targets_artif)]
                df_agg = df_f.groupby("metropole", as_index=False).agg(
                    surface_artif_1_ha=("surface_artif_1_ha", "sum"),
                    surface_artif_2_ha=("surface_artif_2_ha", "sum"),
                    commune_surface_ha=("commune_surface_ha", "sum"),
                    flux_surface_ha=("flux_surface_ha", "sum"),
                    duree_periode=("duree_periode", "mean"),
                    millesime_1=("millesimes_1", "min"),
                    millesime_2=("millesimes_2", "max"),
                ).rename(columns={"metropole": "territoire"})
            else:
                df_f = df_artif[
                    (df_artif["metropole"] == "Grenoble")
                    & (df_artif["nom"].isin(targets_artif))
                ]
                df_agg = df_f.rename(columns={
                    "nom": "territoire",
                    "millesimes_1": "millesime_1",
                    "millesimes_2": "millesime_2",
                })[[
                    "territoire", "surface_artif_1_ha", "surface_artif_2_ha",
                    "commune_surface_ha", "flux_surface_ha", "duree_periode",
                    "millesime_1", "millesime_2",
                ]].copy()

            if df_agg.empty:
                st.warning("Aucune donnée disponible pour cette sélection.")
                st.stop()

            # Indicateurs dérivés
            df_agg["pct_artif_1"] = df_agg["surface_artif_1_ha"] / df_agg["commune_surface_ha"] * 100
            df_agg["pct_artif_2"] = df_agg["surface_artif_2_ha"] / df_agg["commune_surface_ha"] * 100
            df_agg["pct_naturel"] = 100 - df_agg["pct_artif_2"]
            df_agg["surf_naturel_ha"] = df_agg["commune_surface_ha"] - df_agg["surface_artif_2_ha"]
            df_agg["evol_ha"] = df_agg["flux_surface_ha"]
            df_agg["rythme_ha_an"] = df_agg["flux_surface_ha"] / df_agg["duree_periode"]

            # Ordre utilisateur
            df_agg["territoire"] = pd.Categorical(
                df_agg["territoire"], categories=targets_artif, ordered=True
            )
            df_agg = df_agg.sort_values("territoire").reset_index(drop=True)
            df_agg["territoire"] = df_agg["territoire"].astype(str)

            n_targets  = len(df_agg)
            bar_colors = (
                [COULEURS.get(t, "#888888") for t in df_agg["territoire"]]
                if mode_artif_metro
                else [PALETTE_COMMUNE[i % len(PALETTE_COMMUNE)] for i in range(n_targets)]
            )

            # ══════════════════════════════════════════════════════════════════
            # VUE MÉTROPOLES
            # ══════════════════════════════════════════════════════════════════
            if mode_artif_metro:

                # ── KPI ───────────────────────────────────────────────────────
                st.subheader("Indicateurs synthétiques")
                kpi_cols = st.columns(n_targets)
                for i, row in df_agg.iterrows():
                    c          = bar_colors[i]
                    evol_color = "#C62828" if row["evol_ha"] >= 0 else "#1565C0"
                    evol_sign  = "+" if row["evol_ha"] >= 0 else ""
                    periode    = f"{int(row['millesime_1'])} → {int(row['millesime_2'])}"
                    with kpi_cols[i]:
                        st.markdown(f"""
                        <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                            border-left:6px solid {c};background:#fff;
                            margin-bottom:12px;padding:12px 16px;'>
                            <div style='font-size:13px;font-weight:700;color:#1C3A27;
                                margin-bottom:2px;border-bottom:1px solid #eee;
                                padding-bottom:5px;'>{row['territoire']}</div>
                            <div style='font-size:9px;color:#999;margin-bottom:8px;'>
                                Période {periode}</div>
                            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Sol artificialisé</div>
                                    <div style='font-size:18px;font-weight:800;color:#E65100;'>
                                        {row['pct_artif_2']:.1f}%</div>
                                    <div style='font-size:10px;color:#999;'>
                                        {row['surface_artif_2_ha']:,.0f} ha</div>
                                </div>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Espace naturel/agri.</div>
                                    <div style='font-size:18px;font-weight:800;color:#2E7D32;'>
                                        {row['pct_naturel']:.1f}%</div>
                                    <div style='font-size:10px;color:#999;'>
                                        {row['surf_naturel_ha']:,.0f} ha</div>
                                </div>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Surface consommée</div>
                                    <div style='font-size:15px;font-weight:800;
                                        color:{evol_color};'>
                                        {evol_sign}{row['evol_ha']:.1f} ha</div>
                                    <div style='font-size:10px;color:#999;'>sur 3 ans</div>
                                </div>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Rythme annuel</div>
                                    <div style='font-size:15px;font-weight:800;color:#7B1FA2;'>
                                        {row['rythme_ha_an']:.1f} ha/an</div>
                                    <div style='font-size:10px;color:#999;'>objectif : −50 % d'ici 2031</div>
                                </div>
                            </div>
                            <div style='margin-top:8px;font-size:9px;color:#aaa;text-align:center;'>
                                Surface totale métropole : {row['commune_surface_ha']:,.0f} ha
                            </div>
                        </div>""", unsafe_allow_html=True)

                st.markdown("---")

                # ── Graphique 1 : Surfaces absolues empilées (horizontal) ─────
                st.subheader(
                    "Surfaces absolues par métropole (ha)",
                    help=(
                        "Décomposition de la surface totale de chaque métropole en sol artificialisé (couleur du territoire) et espace naturel/agricole/forestier (vert clair). "
                        "Permet de comparer les tailles absolues, pas seulement les pourcentages : une métropole avec un faible taux mais un grand territoire peut avoir plus d'hectares artificialisés en valeur absolue qu'une plus petite métropole plus dense."
                    ),
                )
                df_surf = df_agg.sort_values("commune_surface_ha", ascending=True)
                fig_surf = go.Figure()
                fig_surf.add_trace(go.Bar(
                    y=df_surf["territoire"],
                    x=df_surf["surface_artif_2_ha"],
                    name="Sol artificialisé",
                    orientation="h",
                    marker=dict(
                        color=[COULEURS.get(t, "#888888") for t in df_surf["territoire"]],
                    ),
                    text=df_surf["surface_artif_2_ha"].apply(
                        lambda v: f"{v:,.0f} ha"
                    ),
                    textposition="inside",
                    textfont=dict(color="white", size=9, family="Sora"),
                    hovertemplate=(
                        "<b>%{y}</b><br>Artificialisé : %{x:,.0f} ha<extra></extra>"
                    ),
                ))
                fig_surf.add_trace(go.Bar(
                    y=df_surf["territoire"],
                    x=df_surf["surf_naturel_ha"],
                    name="Naturel / Agricole / Forestier",
                    orientation="h",
                    marker_color="#B7E4C7",
                    text=df_surf["surf_naturel_ha"].apply(
                        lambda v: f"{v:,.0f} ha"
                    ),
                    textposition="inside",
                    textfont=dict(color="#1B4332", size=9, family="Sora"),
                    hovertemplate=(
                        "<b>%{y}</b><br>Naturel : %{x:,.0f} ha<extra></extra>"
                    ),
                ))
                fig_surf.update_layout(
                    barmode="stack",
                    height=130 + n_targets * 45,
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    ),
                    xaxis=dict(title="Surface (ha)", gridcolor="#E8F5EE"),
                    yaxis=dict(title=""),
                )
                apply_grenoble_hatch(fig_surf, active=True)
                st.plotly_chart(style(fig_surf), use_container_width=True)

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.write(
                        "Les barres empilées montrent la surface totale de chaque métropole décomposée en sol artificialisé et espace naturel/agricole/forestier (vert clair). "
                    )

                st.markdown("---")

                # ── Graphique 2 : Ha consommés + Rythme annuel ────────────────
                st.subheader(
                    "Consommation d'espace sur la période",
                    help=(
                        "Surface nette artificialisée sur les 3 ans d'observation (ha), et rythme annuel moyen (ha/an). "
                        "L'objectif ZAN (loi Climat et Résilience 2021) impose à chaque territoire de réduire son rythme de consommation de 50 % d'ici 2031."
                    ),
                )
                gc1, gc2 = st.columns(2)

                with gc1:
                    st.markdown(
                        "##### Hectares consommés sur 3 ans",
                        help=(
                            "Surface nette artificialisée sur la période d'observation. "
                        ),
                    )
                    df_evol = df_agg.sort_values("evol_ha", ascending=True)
                    # Couleurs du territoire (pas rouge/bleu selon signe)
                    fig_evol_ha = go.Figure()
                    for _, row in df_evol.iterrows():
                        fig_evol_ha.add_trace(go.Bar(
                            y=[row["territoire"]],
                            x=[row["evol_ha"]],
                            orientation="h",
                            name=row["territoire"],
                            marker=dict(color=COULEURS.get(row["territoire"], "#888888")),
                            showlegend=False,
                            text=[f"{'+'if row['evol_ha']>=0 else ''}{row['evol_ha']:.1f} ha"],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=(
                                f"<b>{row['territoire']}</b><br>"
                                f"Consommé : {row['evol_ha']:.1f} ha<extra></extra>"
                            ),
                        ))
                    fig_evol_ha.add_vline(x=0, line_color="#999", line_width=1)
                    apply_grenoble_hatch(fig_evol_ha, active=True)
                    fig_evol_ha.update_layout(
                        height=130 + n_targets * 45,
                        margin=dict(t=10, b=10, l=10, r=80),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(title="Ha consommés (3 ans)", gridcolor="#E8F5EE"),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_evol_ha), use_container_width=True)

                with gc2:
                    st.markdown(
                        "##### Rythme annuel de consommation (ha/an)",
                        help=(
                            "Surface consommée en moyenne chaque année = ha sur 3 ans ÷ 3. "
                        ),
                    )
                    df_rythme = df_agg.sort_values("rythme_ha_an", ascending=True)
                    fig_rythme = go.Figure()
                    for _, row in df_rythme.iterrows():
                        fig_rythme.add_trace(go.Bar(
                            y=[row["territoire"]],
                            x=[row["rythme_ha_an"]],
                            orientation="h",
                            name=row["territoire"],
                            marker=dict(color=COULEURS.get(row["territoire"], "#888888")),
                            showlegend=False,
                            text=[f"{row['rythme_ha_an']:.1f} ha/an"],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=(
                                f"<b>{row['territoire']}</b><br>"
                                f"Rythme : {row['rythme_ha_an']:.1f} ha/an<extra></extra>"
                            ),
                        ))
                    apply_grenoble_hatch(fig_rythme, active=True)
                    fig_rythme.update_layout(
                        height=130 + n_targets * 45,
                        margin=dict(t=10, b=10, l=10, r=80),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(title="Ha/an", gridcolor="#E8F5EE"),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_rythme), use_container_width=True)

                with st.expander("💡 Comment interpréter ces graphiques ?"):
                    st.write(
                        "**Ha consommés** : surface nette gagnée par l'artificialisation sur les 3 ans. "
                        "**Rythme annuel** : ha consommés ÷ 3 ans. "
                    )

                st.markdown("---")

                # ── Graphique 3 : Trajectoire slope chart ─────────────────────
                st.subheader(
                    "Trajectoire du taux d'artificialisation",
                    help=(
                        "Évolution du taux d'artificialisation entre le premier et le second millésime d'observation (intervalle : 3 ans). "
                        "Une pente ascendante marque une poursuite de l'artificialisation. Les millésimes varient selon les territoires - l'axe X est indicatif, non comparatif."
                    ),
                )
                fig_traj = go.Figure()
                for i, row in df_agg.iterrows():
                    is_g = row["territoire"] == "Grenoble"
                    fig_traj.add_trace(go.Scatter(
                        x=[str(int(row["millesime_1"])), str(int(row["millesime_2"]))],
                        y=[row["pct_artif_1"], row["pct_artif_2"]],
                        mode="lines+markers+text",
                        name=row["territoire"],
                        line=dict(
                            color="#FF584D" if is_g else bar_colors[i], # Si métro de Grenoble en rouge sinon on garde les couleurs de base
                            width=2,
                            dash="dash" if is_g else "solid", # Si métro de Grenoble en pointillé sinon en trait plein
                        ),
                        marker=dict(
                            size=10,
                            color="#FF584D" if is_g else bar_colors[i],
                        ),
                        text=[
                            f"  {row['pct_artif_1']:.1f}%",
                            f"  {row['pct_artif_2']:.1f}%",
                        ],
                        textposition="middle right",
                        textfont=dict(
                            size=9,
                            color="#FF584D" if is_g else bar_colors[i],
                            family="Sora",
                        ),
                        hovertemplate=(
                            f"<b>{row['territoire']}</b><br>"
                            f"%{{x}} : %{{y:.2f}}%<extra></extra>"
                        ),
                    ))
                fig_traj.update_layout(
                    height=400, margin=dict(t=20, b=10, r=60),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    xaxis=dict(
                        title="Millésime d'observation",
                        showgrid=False, type="category",
                    ),
                    yaxis=dict(
                        title="Taux d'artificialisation (%)",
                        gridcolor="#E8F5EE",
                    ),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="center", x=0.5, font_size=10,
                    ),
                )
                st.plotly_chart(style(fig_traj), use_container_width=True)

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.write(
                        "Chaque ligne relie le taux d'artificialisation d'une métropole entre le premier et le second millésime (intervalle : 3 ans). "
                        "La pente traduit l'intensité de la dynamique d'artificialisation. Grenoble apparaît en pointillé rouge pour la distinguer. "
                        "Les évolutions sont généralement faibles (quelques dixièmes de %) sur 3 ans. Les millésimes diffèrent selon les territoires, l'axe X est indicatif, pas strictement comparable."
                    )

            # ══════════════════════════════════════════════════════════════════
            # VUE COMMUNES (Grenoble-Alpes Métropole)
            # ══════════════════════════════════════════════════════════════════
            else:

                # ── KPI par commune ───────────────────────────────────────────────

                st.subheader("Indicateurs par commune")
                kpi_cols_c = st.columns(min(n_targets, 4))    
                for i, row in df_agg.iterrows():
                    c          = bar_colors[i]
                    evol_color = "#C62828" if row["evol_ha"] >= 0 else "#1565C0"
                    evol_sign  = "+" if row["evol_ha"] >= 0 else ""
                    periode    = f"{int(row['millesime_1'])} → {int(row['millesime_2'])}"
                    with kpi_cols_c[i % min(n_targets, 4)]:
                        st.markdown(f"""
                        <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                            border-left:6px solid {c};background:#fff;
                            margin-bottom:12px;padding:12px 16px;'>
                            <div style='font-size:13px;font-weight:700;color:#1C3A27;
                                margin-bottom:2px;border-bottom:1px solid #eee;
                                padding-bottom:5px;'>{row['territoire']}</div>
                            <div style='font-size:9px;color:#999;margin-bottom:8px;'>
                                Période {periode}</div>
                            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Sol artificialisé</div>
                                    <div style='font-size:18px;font-weight:800;color:#E65100;'>
                                        {row['pct_artif_2']:.1f}%</div>
                                    <div style='font-size:10px;color:#999;'>
                                        {row['surface_artif_2_ha']:,.0f} ha</div>
                                </div>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Espace naturel/agri.</div>
                                    <div style='font-size:18px;font-weight:800;color:#2E7D32;'>
                                        {row['pct_naturel']:.1f}%</div>
                                    <div style='font-size:10px;color:#999;'>
                                        {row['surf_naturel_ha']:,.0f} ha</div>
                                </div>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Surface consommée</div>
                                    <div style='font-size:15px;font-weight:800;
                                        color:{evol_color};'>
                                        {evol_sign}{row['evol_ha']:.1f} ha</div>
                                    <div style='font-size:10px;color:#999;'>sur 3 ans</div>
                                </div>
                                <div style='text-align:center;'>
                                    <div style='font-size:9px;font-weight:700;color:#666;
                                        text-transform:uppercase;'>Rythme annuel</div>
                                    <div style='font-size:15px;font-weight:800;color:#7B1FA2;'>
                                        {row['rythme_ha_an']:.1f} ha/an</div>
                                    <div style='font-size:10px;color:#999;'>objectif : −50 % d'ici 2031</div>
                                </div>
                            </div>
                            <div style='margin-top:8px;font-size:9px;color:#aaa;text-align:center;'>
                                Surface totale commune : {row['commune_surface_ha']:,.0f} ha
                            </div>
                        </div>""", unsafe_allow_html=True)
                st.markdown("---")

                # ── Graphique C1 : Taux artif + Part naturelle ────────────────
                gc1, gc2 = st.columns(2)

                with gc1:
                    st.subheader(
                        "Taux d'artificialisation par commune (%)",
                        help=(
                            "Part du territoire communal couverte par des sols artificialisés au millésime le plus récent. "
                            "Les communes très urbanisées (centres-villes, zones industrielles) dépassent souvent 50–70 %. "
                            "Les communes périphériques restent en dessous de 20 %."
                        ),
                    )
                    df_s1 = df_agg.sort_values("pct_artif_2", ascending=True)
                    fig_c1 = px.bar(
                        df_s1, x="pct_artif_2", y="territoire",
                        orientation="h",
                        color="territoire",
                        color_discrete_sequence=PALETTE_COMMUNE,
                        text=df_s1["pct_artif_2"].apply(lambda v: f"{v:.1f}%"),
                        labels={"territoire": "", "pct_artif_2": "Taux (%)"},
                        height=130 + n_targets * 35,
                    )
                    fig_c1.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{y}</b><br>Artificialisé : %{text}<extra></extra>"
                        ),
                    )
                    fig_c1.update_layout(
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=60),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(title="Taux (%)", gridcolor="#E8F5EE", range=[0, 115]),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_c1), use_container_width=True)

                with gc2:
                    st.subheader(
                        "Part naturelle / agricole par commune (%)",
                        help=(
                            "Inverse du taux d'artificialisation : part du territoire couverte par des espaces naturels, agricoles ou forestiers (ENAF). "
                            "Une commune périurbaine ou de grande superficie conserve généralement une part naturelle plus élevée."
                        ),
                    )
                    df_s2 = df_agg.sort_values("pct_naturel", ascending=True)
                    fig_c2 = px.bar(
                        df_s2, x="pct_naturel", y="territoire",
                        orientation="h",
                        color="territoire",
                        color_discrete_sequence=PALETTE_COMMUNE,
                        text=df_s2["pct_naturel"].apply(lambda v: f"{v:.1f}%"),
                        labels={"territoire": "", "pct_naturel": "Part naturelle (%)"},
                        height=130 + n_targets * 35,
                    )
                    fig_c2.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        marker_color="#52B788",
                        hovertemplate=(
                            "<b>%{y}</b><br>Naturel/Agri. : %{text}<extra></extra>"
                        ),
                    )
                    fig_c2.update_layout(
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=60),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(title="Part naturelle (%)", gridcolor="#E8F5EE",
                                   range=[0, 115]),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_c2), use_container_width=True)

                with st.expander("💡 Comment interpréter ces graphiques ?"):
                    st.write(
                        "**Taux d'artificialisation** : part du territoire communal couverte par des sols artificialisés. Les communes-centres (Grenoble, Échirolles) sont très artificialisées.\n\n"
                        "**Part naturelle** : espaces non artificialisés. Ces deux graphiques sont symétriques (naturel = 100 % − artificialisé) mais permettent de lire directement l'indicateur selon la question posée."
                    )

                st.markdown("---")

                # ── Graphique C2 : Surfaces absolues + Ha consommés ───────────
                gc3, gc4 = st.columns(2)

                with gc3:
                    st.subheader(
                        "Surfaces absolues par commune (ha)",
                        help=(
                            "Décomposition de la surface totale de chaque commune en sol artificialisé et espace naturel/agricole/forestier. "
                            "Permet de contextualiser les % : deux communes avec le même taux peuvent avoir des surfaces très différentes selon leur superficie."
                        ),
                    )
                    df_s3 = df_agg.sort_values("commune_surface_ha", ascending=True)
                    fig_c3 = go.Figure()
                    fig_c3.add_trace(go.Bar(
                        y=df_s3["territoire"],
                        x=df_s3["surface_artif_2_ha"],
                        name="Artificialisé",
                        orientation="h",
                        marker_color=PALETTE_COMMUNE[2],
                        text=df_s3["surface_artif_2_ha"].apply(lambda v: f"{v:.0f}"),
                        textposition="inside",
                        textfont=dict(color="white", size=8, family="Sora"),
                        hovertemplate=(
                            "<b>%{y}</b><br>Artificialisé : %{x:.0f} ha<extra></extra>"
                        ),
                    ))
                    fig_c3.add_trace(go.Bar(
                        y=df_s3["territoire"],
                        x=df_s3["surf_naturel_ha"],
                        name="Naturel / Agricole / Forestier",
                        orientation="h",
                        marker_color="#B7E4C7",
                        text=df_s3["surf_naturel_ha"].apply(lambda v: f"{v:.0f}"),
                        textposition="inside",
                        textfont=dict(color="#1B4332", size=8, family="Sora"),
                        hovertemplate=(
                            "<b>%{y}</b><br>Naturel : %{x:.0f} ha<extra></extra>"
                        ),
                    ))
                    fig_c3.update_layout(
                        barmode="stack",
                        height=130 + n_targets * 35,
                        margin=dict(t=10, b=10, l=10, r=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        legend=dict(
                            orientation="h", y=1.05, x=0, font_size=9,
                        ),
                        xaxis=dict(title="Surface (ha)", gridcolor="#E8F5EE"),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_c3), use_container_width=True)

                with gc4:
                    st.subheader(
                        "Surface consommée sur la période (ha)",
                        help=(
                            "Hectares nets artificialisés sur les 3 ans d'observation. "
                            "Une valeur négative indique une renaturation nette (démolition, "
                            "végétalisation), cas très rare mais possible (Gières ou Vizille par exemple)."
                        ),
                    )
                    df_s4 = df_agg.sort_values("evol_ha", ascending=True)
                    fig_c4 = px.bar(
                        df_s4, x="evol_ha", y="territoire",
                        orientation="h",
                        color="territoire",
                        color_discrete_sequence=PALETTE_COMMUNE,
                        text=df_s4["evol_ha"].apply(
                            lambda v: f"{'+'if v>=0 else ''}{v:.2f} ha"
                        ),
                        labels={"territoire": "", "evol_ha": "Ha (3 ans)"},
                        height=130 + n_targets * 35,
                    )
                    fig_c4.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{y}</b><br>Consommé : %{text}<extra></extra>"
                        ),
                    )
                    fig_c4.add_vline(x=0, line_color="#999", line_width=1)
                    fig_c4.update_layout(
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=80),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(title="Ha (3 ans)", gridcolor="#E8F5EE"),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_c4), use_container_width=True)

                with st.expander("💡 Comment interpréter ces graphiques ?"):
                    st.write(
                        "**Surfaces absolues** : les barres empilées montrant les hectares artificialisés et naturels de chaque commune. "
                        "Contextualise les taux : une commune avec 60 % d'artificialisation mais une petite superficie impacte moins le territoire qu'une grande commune à 30 %.\n\n"
                        "**Surface consommée** : variation nette en hectares sur 3 ans. "
                        "Pour les communes, les valeurs sont souvent faibles (quelques ha) mais révèlent les dynamiques locales. Une valeur négative (bleu) indique une renaturation rare mais possible (Gières ou Vizille par exemple)."
                    )

                # ── Graphique C3 : Classement si > 3 communes ─────────────────
                if n_targets > 3:
                    st.markdown("---")
                    st.subheader(
                        "Classement des communes par rythme de consommation (ha/an)",
                        help=(
                            "Communes triées par rythme annuel de consommation d'espace (ha/an = ha sur 3 ans ÷ 3). "
                            "Permet de repérer rapidement les communes les plus actives en matière d'artificialisation au sein de la métropole grenobloise."
                        ),
                    )
                    df_rank = df_agg.sort_values("rythme_ha_an", ascending=True)
                    fig_rank = px.bar(
                        df_rank, x="rythme_ha_an", y="territoire",
                        orientation="h",
                        color="territoire",
                        color_discrete_sequence=PALETTE_COMMUNE,
                        text=df_rank["rythme_ha_an"].apply(lambda v: f"{v:.2f} ha/an"),
                        labels={"territoire": "", "rythme_ha_an": "Ha/an"},
                        height=130 + n_targets * 30,
                    )
                    fig_rank.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{y}</b><br>Rythme : %{text}<extra></extra>"
                        ),
                    )
                    fig_rank.update_layout(
                        showlegend=False,
                        margin=dict(t=10, b=10, l=10, r=80),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Sora",
                        xaxis=dict(title="Rythme annuel (ha/an)", gridcolor="#E8F5EE"),
                        yaxis=dict(title=""),
                    )
                    st.plotly_chart(style(fig_rank), use_container_width=True)

    # ==============================================================================
    # ONGLET 2 - QUALITÉ DE L'AIR
    # ==============================================================================
    # Données journalières (prévision J / J+1 / J+2), pas de série historique
    with tab_env2:
        if df_air is None:
            st.info("📂 Fichier `ind_atmo_clean.csv` introuvable.")
        else:
            # ── Encart Source ──────────────────────────────────────────────
            st.markdown("""
            <div style='background-color: #f1f8f5; padding: 10px 15px; border-radius: 10px; border-left: 5px solid #1C3A27; margin-bottom: 20px; font-size: 0.85em;'>
                <strong>Source :</strong> Fédération Atmo France (réseau des AASQA, agréées par le Ministère de la Transition écologique) -
                <a href='https://www.data.gouv.fr/datasets/indice-de-la-qualite-de-lair-quotidien-par-commune-indice-atmo' target='_blank' style='color: #1C3A27;'>Accéder aux données</a><br>
                Indice ATMO réglementaire calculé à partir de 5 polluants (NO₂, O₃, PM10, PM2.5, SO₂) : la valeur retenue
                pour chaque polluant est la plus défavorable des prévisions du jour.<br>
                <em>⚠️ Couverture actuelle limitée à 3 métropoles : Grenoble, Rouen et Saint-Étienne (Rennes et Montpellier non disponibles dans ce flux).</em>
            </div>""", unsafe_allow_html=True)

            # ─────────────────────────────────────────────────────────────
            # CONSTANTES & PALETTES
            # ─────────────────────────────────────────────────────────────
            # Ordre officiel de sévérité de l'indice ATMO (du meilleur au pire)
            QUALITE_ORDER = ["Bon", "Moyen", "Dégradé", "Mauvais", "Très mauvais", "Extrêmement mauvais"]

            # Couleurs officielles ATMO récupérées directement depuis les données
            # (colonne coul_qual) plutôt que recodées à la main : garantit la
            # cohérence avec le code couleur réglementaire national.
            QUALITE_COULEURS = (
                df_air.drop_duplicates("lib_qual")
                .set_index("lib_qual")["coul_qual"].to_dict()
            )

            # Sous-indices polluants : code technique -> libellé lisible
            POLLUANTS = {
                "code_no2":  "NO₂ (dioxyde d'azote)",
                "code_o3":   "O₃ (ozone)",
                "code_pm10": "PM10 (particules < 10µm)",
                "code_pm25": "PM2.5 (particules < 2.5µm)",
                "code_so2":  "SO₂ (dioxyde de soufre)",
            }

            # ─────────────────────────────────────────────────────────────
            # FONCTIONS DE CALCUL (pures, partagées entre les deux vues)
            # ─────────────────────────────────────────────────────────────
            def get_quality_distribution(df_sub):
                """Répartition (%) des communes par catégorie de qualité, sur les catégories réellement présentes."""
                n = len(df_sub)
                if n == 0:
                    return pd.DataFrame(columns=["Catégorie", "Part (%)", "Nombre"])
                counts = df_sub["lib_qual"].value_counts()
                cats_presentes = [c for c in QUALITE_ORDER if c in counts.index]
                return pd.DataFrame({
                    "Catégorie": cats_presentes,
                    "Part (%)": [counts[c] / n * 100 for c in cats_presentes],
                    "Nombre": [counts[c] for c in cats_presentes],
                })

            def get_kpi_air(df_sub):
                """Indicateurs synthétiques pour la carte KPI d'un territoire. Retourne None si aucune donnée."""
                n = len(df_sub)
                if n == 0:
                    return None
                dominante = df_sub["lib_qual"].mode().iloc[0]
                pct_degrade = (df_sub["lib_qual"].isin(["Dégradé", "Mauvais", "Très mauvais", "Extrêmement mauvais"]).sum() / n * 100)
                return {
                    "n_communes": n,
                    "dominante": dominante,
                    "couleur_dominante": QUALITE_COULEURS.get(dominante, "#888"),
                    "pct_degrade": pct_degrade,
                }

            def get_pollutant_scores(df_sub):
                """Score moyen (1=Bon ... 6=Extrêmement mauvais) par polluant pour un territoire. None si vide."""
                if df_sub.empty:
                    return None
                return {label: df_sub[code].mean() for code, label in POLLUANTS.items()}

            def render_kpi_card_air(label, kpis, border_color):
                """Carte KPI HTML, identique au style des autres onglets."""
                if kpis is None:
                    st.markdown(f"""
                    <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                        border-left:6px solid {border_color}; background:#fff;
                        margin-bottom:12px; padding:12px 16px;min-height:100px;
                        display:flex;flex-direction:column;justify-content:center;'>
                        <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px;'>{label}</div>
                        <div style='font-size:12px;color:#888;'>Aucune donnée disponible</div>
                    </div>""", unsafe_allow_html=True)
                    return
                st.markdown(f"""
                <div style='border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:6px solid {border_color}; background:#fff; margin-bottom:12px; padding:12px 16px;'>
                    <div style='font-size:13px;font-weight:700;color:#1C3A27;margin-bottom:8px; border-bottom:1px solid #eee; padding-bottom:5px;'>{label}</div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Communes</div>
                            <div style='font-size:15px;font-weight:800;color:#555;'>{kpis['n_communes']}</div>
                        </div>
                        <div style='text-align:center;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Qualité dominante</div>
                            <div style='font-size:13px;font-weight:800;color:{kpis["couleur_dominante"]};'>{kpis['dominante']}</div>
                        </div>
                        <div style='text-align:center;grid-column:span 2;'>
                            <div style='font-size:9px;font-weight:700;color:#666;text-transform:uppercase;'>Communes en air dégradé ou pire</div>
                            <div style='font-size:15px;font-weight:800;color:#C62828;'>{kpis['pct_degrade']:.2f}%</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ─────────────────────────────────────────────────────────────
            # BANDEAU FILTRES
            # ─────────────────────────────────────────────────────────────
            with st.container():
                filter_bar("Filtres - Qualité de l'air")
                fa1, fa2 = st.columns([1, 3])
                with fa1:
                    filter_row_label("Niveau géographique")
                with fa2:
                    mode_air = st.radio(
                        "",
                        ["Comparaison Métropoles", "Comparaison communes Grenoble-Alpes Métropole"],
                        key="air_mode", horizontal=True, label_visibility="collapsed",
                    )

                # Filtre aligné sur les autres onglets : les 5 métropoles sont
                # proposées et la sélection est partagée entre onglets
                # (shared_default_demo / sync_metros_demo), même si seules
                # Grenoble, Rouen et Saint-Étienne ont des données dans ce flux.
                if mode_air == "Comparaison Métropoles":
                    sel_metros_air = st.multiselect(
                        "Métropoles à comparer", TOUTES, default=shared_default_demo(TOUTES),
                        key="air_metros", on_change=sync_metros_demo, args=("air_metros",),
                        help="Seules Grenoble, Rouen et Saint-Étienne disposent de données de qualité de l'air dans ce flux.",
                    )
                    targets_air = sel_metros_air
                else:
                    communes_dispo = sorted(df_air[df_air["metropole"] == "Grenoble"]["nom_commune"].unique().tolist())
                    sel_communes_air = st.multiselect(
                        "Communes de Grenoble-Alpes Métropole", communes_dispo,
                        default=shared_default_communes_demo(communes_dispo), key="air_communes",
                        on_change=sync_communes_demo, args=("air_communes",),
                    )
                    targets_air = sel_communes_air

                dates_dispo = sorted(df_air["date_ech"].unique())
                labels_jours = {0: "Aujourd'hui (J)", 1: "Demain (J+1)", 2: "Après-demain (J+2)"}
                date_labels = {d: f"{labels_jours.get(i, f'J+{i}')} - {d.strftime('%d/%m/%Y')}" for i, d in enumerate(dates_dispo)}
                date_air = st.selectbox(
                    "Jour de prévision", dates_dispo, format_func=lambda d: date_labels[d],
                    index=0, key="an_air",
                    help="L'indice ATMO est une prévision journalière (J, J+1, J+2) : pas de série historique sur ce flux.",
                )

            st.markdown("---")

            if not targets_air:
                st.warning("Sélectionnez au moins un territoire.")
                st.stop()

            df_jour = df_air[df_air["date_ech"] == date_air]

            # ═════════════════════════════════════════════════════════════
            # VUE MÉTROPOLES
            # ═════════════════════════════════════════════════════════════
            if mode_air == "Comparaison Métropoles":

                bar_colors = [COULEURS.get(t, "#888888") for t in targets_air]
                color_by_target = dict(zip(targets_air, bar_colors))
                greno_vrect = None
                if "Grenoble" in targets_air:
                    g_pos = targets_air.index("Grenoble")
                    greno_vrect = dict(
                        x0=g_pos - 0.45, x1=g_pos + 0.45,
                        fillcolor="rgba(255,88,77,0.10)",
                        line_color="#FF584D", line_width=1.5,
                        line_dash="dash", layer="below",
                    )

                # Territoires avec / sans données dans ce flux Atmo
                entities_with_data = [t for t in targets_air if not df_jour[df_jour["metropole"] == t].empty]
                entities_no_data   = [t for t in targets_air if t not in entities_with_data]

                # ── KPI ──────────────────────────────────────────────────
                st.subheader(
                    f"Indicateurs de qualité de l'air - {date_labels[date_air]}",
                    help=(
                        "**Qualité dominante** : catégorie ATMO la plus fréquente parmi les communes du territoire.\n\n"
                        "**Communes en air dégradé ou pire** : part des communes classées Dégradé, Mauvais, "
                        "Très mauvais ou Extrêmement mauvais (donc hors Bon/Moyen)."
                    ),
                )
                kpi_cols = st.columns(len(targets_air))
                for i, t in enumerate(targets_air):
                    kpis_t = get_kpi_air(df_jour[df_jour["metropole"] == t])
                    with kpi_cols[i]:
                        render_kpi_card_air(t, kpis_t, border_color=bar_colors[i])

                if entities_no_data:
                    st.caption(
                        "ℹ️ Aucune donnée de qualité de l'air disponible (flux Atmo non couvert) pour : "
                        + ", ".join(entities_no_data)
                    )

                if not entities_with_data:
                    st.warning("Aucune donnée de qualité de l'air disponible pour cette sélection.")
                    st.stop()

                st.markdown("---")

                # ── RÉPARTITION + ÉVOLUTION ─────────────────────────────
                gc1, gc2 = st.columns(2)

                with gc1:
                    st.subheader(
                        "Répartition des communes par catégorie",
                        help=(
                            "Part des communes de chaque territoire classées dans chaque catégorie ATMO "
                            f"(base 100%), pour le jour sélectionné ({date_labels[date_air]}). "
                            "Couleurs officielles ATMO."
                        ),
                    )
                    rows_dist = []
                    for t in entities_with_data:
                        dist_t = get_quality_distribution(df_jour[df_jour["metropole"] == t])
                        dist_t["Territoire"] = t
                        rows_dist.append(dist_t)
                    df_dist = pd.concat(rows_dist, ignore_index=True) if rows_dist else pd.DataFrame()

                    if not df_dist.empty:
                        cats_order = [c for c in QUALITE_ORDER if c in df_dist["Catégorie"].unique()]
                        fig_dist = px.bar(
                            df_dist, x="Territoire", y="Part (%)", color="Catégorie",
                            barmode="stack", text_auto=".2f",
                            color_discrete_map=QUALITE_COULEURS,
                            category_orders={"Catégorie": cats_order}, height=380,
                        )
                        fig_dist.update_traces(
                            textposition="inside", textfont_size=9,
                            hovertemplate="<b>%{x}</b><br>%{fullData.name} : %{y:.2f}%<extra></extra>",
                        )
                        if greno_vrect:
                            fig_dist.add_vrect(**greno_vrect)
                        fig_dist.update_layout(
                            legend=dict(orientation="h", y=1.18, title=""),
                            yaxis_title="Part des communes (%)", xaxis_title="", margin=dict(t=20),
                        )
                        st.plotly_chart(style(fig_dist), use_container_width=True)

                with gc2:
                    st.subheader(
                        "Évolution sur les 3 jours de prévision",
                        help=(
                            "Part des communes en air dégradé ou pire (Dégradé, Mauvais, Très mauvais, "
                            "Extrêmement mauvais) pour chacun des 3 jours de prévision disponibles "
                            "(J, J+1, J+2). Ce graphique reste indépendant du sélecteur de jour ci-dessus."
                        ),
                    )
                    fig_evo = go.Figure()
                    for t in entities_with_data:
                        y_vals = []
                        for d in dates_dispo:
                            df_td = df_air[(df_air["metropole"] == t) & (df_air["date_ech"] == d)]
                            kpis_td = get_kpi_air(df_td)
                            y_vals.append(kpis_td["pct_degrade"] if kpis_td else None)
                        is_greno = (t == "Grenoble")
                        fig_evo.add_trace(go.Scatter(
                            x=[date_labels[d].split(" - ")[0] for d in dates_dispo], y=y_vals,
                            mode="lines+markers", name=t,
                            line=dict(color=color_by_target[t], width=3.5 if is_greno else 2,
                                    dash="dash" if is_greno else "solid"),
                            marker=dict(size=11 if is_greno else 8,
                                        symbol="diamond" if is_greno else "circle",
                                        line=dict(color="#FF584D", width=2) if is_greno else dict(width=0)),
                            hovertemplate=f"<b>{t}</b><br>%{{x}} : %{{y:.2f}}%<extra></extra>",
                        ))
                    fig_evo.update_layout(
                        height=380, margin=dict(t=20, b=10),
                        legend=dict(orientation="h", y=1.18, title="", font_size=10),
                        xaxis=dict(title=""),
                        yaxis=dict(title="Communes en air dégradé ou pire (%)", gridcolor="#eee"),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(style(fig_evo), use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write(
                        "**Répartition par catégorie** : permet de comparer d'un coup d'œil la proportion de "
                        "communes touchées par une pollution significative dans chaque territoire, le même jour. "
                        "Une barre majoritairement jaune/rouge indique un épisode de pollution généralisé sur "
                        "le territoire plutôt que localisé.\n\n"
                        "**Évolution sur 3 jours** : suit la tendance à court terme. Une courbe montante "
                        "annonce une dégradation prévue (souvent liée à un épisode anticyclonique stable qui "
                        "favorise l'accumulation des polluants), une courbe descendante annonce une amélioration "
                        "(typiquement après le passage d'un système pluvieux/venteux qui disperse la pollution). "
                        "La ligne en tirets rouges identifie Grenoble."
                    )

                st.markdown("---")

                # ── POLLUANT PRÉPONDÉRANT ───────────────────────────────
                st.subheader(
                    "Polluant prépondérant par territoire",
                    help=(
                        "Score moyen (1 = Bon à 6 = Extrêmement mauvais) de chaque polluant pour le jour "
                        f"sélectionné ({date_labels[date_air]}). Le polluant avec le score le plus élevé est "
                        "celui qui dégrade le plus l'indice global, puisque l'indice ATMO retient toujours le "
                        "maximum des 5 sous-indices."
                    ),
                )
                rows_poll = []
                for t in entities_with_data:
                    scores_t = get_pollutant_scores(df_jour[df_jour["metropole"] == t])
                    if scores_t is None:
                        continue
                    for poll, score in scores_t.items():
                        rows_poll.append({"Territoire": t, "Polluant": poll, "Score moyen": score})
                df_poll = pd.DataFrame(rows_poll)

                if not df_poll.empty:
                    fig_poll = px.bar(
                        df_poll, x="Polluant", y="Score moyen", color="Territoire",
                        barmode="group", color_discrete_map=COULEURS, height=380,
                    )
                    fig_poll.update_traces(
                        hovertemplate="<b>%{fullData.name}</b><br>%{x} : %{y:.2f}<extra></extra>",
                    )
                    for trace in fig_poll.data:
                        if trace.name == "Grenoble":
                            trace.marker.pattern = dict(shape="/", fgcolor="#FF584D", fillmode="overlay", solidity=0.3, size=18)
                    fig_poll.update_layout(
                        legend=dict(orientation="h", y=1.18, title=""),
                        yaxis=dict(title="Score moyen (1=Bon, 6=Extrêmement mauvais)", range=[0, 6]),
                        xaxis_title="", margin=dict(t=20),
                    )
                    st.plotly_chart(style(fig_poll), use_container_width=True)

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.write(
                        "Ce graphique décompose l'indice global par polluant, ce qui permet d'identifier la "
                        "source de pollution dominante sur chaque territoire. **L'ozone (O₃)** est un polluant "
                        "secondaire qui se forme par réaction photochimique sous l'effet du soleil et de la "
                        "chaleur : il domine généralement en période estivale, y compris loin de toute source "
                        "directe. **Le NO₂** est principalement émis par le trafic routier et concentré en zone "
                        "urbaine dense. **Les particules PM10/PM2.5** proviennent du chauffage, du trafic et de "
                        "l'agriculture, avec des pics fréquents en hiver. **Le SO₂**, d'origine essentiellement "
                        "industrielle, reste généralement faible sur ces territoires. Les hachures rouges "
                        "identifient Grenoble."
                    )

            # ═════════════════════════════════════════════════════════════
            # VUE COMMUNES (Grenoble-Alpes Métropole)
            # ═════════════════════════════════════════════════════════════
            else:

                n_comm = len(targets_air)
                comm_palette = [PALETTE_COMMUNE[i % len(PALETTE_COMMUNE)] for i in range(n_comm)]

                # ── KPI ──────────────────────────────────────────────────
                st.subheader(
                    f"Indicateurs de qualité de l'air - {date_labels[date_air]}",
                    help=(
                        "**Qualité dominante** : catégorie ATMO de la commune (une seule valeur par commune).\n\n"
                        "**Communes en air dégradé ou pire** : ici, 0% ou 100% puisqu'il s'agit d'une commune "
                        "unique - l'indicateur prend tout son sens dans la vue Métropoles."
                    ),
                )
                kpi_cols = st.columns(n_comm)
                for i, comm in enumerate(targets_air):
                    kpis_c = get_kpi_air(df_jour[df_jour["nom_commune"] == comm])
                    with kpi_cols[i]:
                        render_kpi_card_air(comm, kpis_c, border_color=comm_palette[i])

                st.markdown("---")

                # ── RÉPARTITION + ÉVOLUTION ─────────────────────────────
                gc1, gc2 = st.columns(2)

                with gc1:
                    st.subheader(
                        "Catégorie de qualité par commune",
                        help=(
                            f"Catégorie ATMO de chaque commune sélectionnée pour le jour choisi "
                            f"({date_labels[date_air]}). Couleurs officielles ATMO."
                        ),
                    )
                    rows_cat_c = []
                    for comm in targets_air:
                        df_c = df_jour[df_jour["nom_commune"] == comm]
                        if not df_c.empty:
                            rows_cat_c.append({
                                "Commune": comm,
                                "Catégorie": df_c["lib_qual"].iloc[0],
                                "Score": df_c["code_qual"].iloc[0],
                            })
                    df_cat_c = pd.DataFrame(rows_cat_c)

                    if not df_cat_c.empty:
                        fig_cat_c = px.bar(
                            df_cat_c, x="Commune", y="Score", color="Catégorie",
                            color_discrete_map=QUALITE_COULEURS, height=380,
                            category_orders={"Catégorie": [c for c in QUALITE_ORDER if c in df_cat_c["Catégorie"].unique()]},
                        )
                        fig_cat_c.update_traces(
                            hovertemplate="<b>%{x}</b><br>%{fullData.name} (score %{y})<extra></extra>",
                        )
                        fig_cat_c.update_layout(
                            legend=dict(orientation="h", y=1.18, title=""),
                            yaxis=dict(title="Score ATMO (1=Bon, 6=Extrêmement mauvais)", range=[0, 6]),
                            xaxis_title="", xaxis_tickangle=-25, margin=dict(t=20),
                        )
                        st.plotly_chart(style(fig_cat_c), use_container_width=True)

                with gc2:
                    st.subheader(
                        "Évolution sur les 3 jours de prévision",
                        help=(
                            "Score ATMO (1 = Bon à 6 = Extrêmement mauvais) de chaque commune pour chacun des "
                            "3 jours de prévision disponibles (J, J+1, J+2). Indépendant du sélecteur de jour "
                            "ci-dessus."
                        ),
                    )
                    fig_evo_c = go.Figure()
                    for i, comm in enumerate(targets_air):
                        y_vals = []
                        for d in dates_dispo:
                            df_cd = df_air[(df_air["nom_commune"] == comm) & (df_air["date_ech"] == d)]
                            y_vals.append(df_cd["code_qual"].iloc[0] if not df_cd.empty else None)
                        fig_evo_c.add_trace(go.Scatter(
                            x=[date_labels[d].split(" - ")[0] for d in dates_dispo], y=y_vals,
                            mode="lines+markers", name=comm,
                            line=dict(color=comm_palette[i], width=2),
                            marker=dict(size=8),
                            hovertemplate=f"<b>{comm}</b><br>%{{x}} : score %{{y}}<extra></extra>",
                        ))
                    fig_evo_c.update_layout(
                        height=380, margin=dict(t=20, b=10),
                        legend=dict(orientation="h", y=1.18, title="", font_size=10),
                        xaxis=dict(title=""),
                        yaxis=dict(title="Score ATMO (1=Bon, 6=Extrêmement mauvais)", range=[0, 6], gridcolor="#eee"),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(style(fig_evo_c), use_container_width=True)

                with st.expander("💡 Comment interpréter ces deux graphiques ?"):
                    st.write(
                        "**Catégorie par commune** : permet de repérer les communes les plus exposées un jour "
                        "donné, par exemple celles situées en fond de cuvette versus celles en altitude.\n\n"
                        "**Évolution sur 3 jours** : une trajectoire commune à toutes les courbes (même direction, "
                        "pentes similaires) indique un phénomène météorologique affectant l'ensemble du bassin "
                        "grenoblois. Des trajectoires divergentes entre communes voisines signalent un effet "
                        "très localisé (proximité d'un axe routier, micro-relief)."
                    )

                st.markdown("---")

                # ── POLLUANT PRÉPONDÉRANT ───────────────────────────────
                st.subheader(
                    "Polluant prépondérant par commune",
                    help=(
                        "Score (1 = Bon à 6 = Extrêmement mauvais) de chaque polluant pour le jour sélectionné "
                        f"({date_labels[date_air]}). Le polluant au score le plus élevé est celui qui détermine "
                        "l'indice global de la commune (l'indice ATMO retient toujours le maximum des 5 sous-indices)."
                    ),
                )
                rows_poll_c = []
                for comm in targets_air:
                    df_c = df_jour[df_jour["nom_commune"] == comm]
                    if df_c.empty:
                        continue
                    for code, label in POLLUANTS.items():
                        rows_poll_c.append({"Commune": comm, "Polluant": label, "Score": df_c[code].iloc[0]})
                df_poll_c = pd.DataFrame(rows_poll_c)

                if not df_poll_c.empty:
                    fig_poll_c = px.bar(
                        df_poll_c, x="Polluant", y="Score", color="Commune",
                        barmode="group", color_discrete_sequence=comm_palette, height=380,
                    )
                    fig_poll_c.update_traces(
                        hovertemplate="<b>%{fullData.name}</b><br>%{x} : %{y:.2f}<extra></extra>",
                    )
                    fig_poll_c.update_layout(
                        legend=dict(orientation="h", y=1.18, title=""),
                        yaxis=dict(title="Score (1=Bon, 6=Extrêmement mauvais)", range=[0, 6]),
                        xaxis_title="", margin=dict(t=20),
                    )
                    st.plotly_chart(style(fig_poll_c), use_container_width=True)

                with st.expander("💡 Comment interpréter ce graphique ?"):
                    st.write(
                        "Ce graphique décompose l'indice global par polluant pour chaque commune. **L'ozone "
                        "(O₃)** domine généralement en été (réaction photochimique sous l'effet du soleil et de "
                        "la chaleur), parfois plus marqué en altitude qu'en fond de vallée. **Le NO₂** reflète "
                        "directement la densité du trafic routier local. **Les particules PM10/PM2.5** "
                        "augmentent en hiver avec le chauffage, et stagnent davantage dans les communes "
                        "encaissées de la cuvette grenobloise. Comparer les profils entre communes voisines "
                        "aide à identifier si la pollution est plutôt liée au trafic, au chauffage ou à un "
                        "phénomène régional (ozone)."
                    )
    
    # ==============================================================================
    # ONGLET EAU & ASSAINISSEMENT — CODE COMPLET
    # Remplace le bloc "with tab_env3:" dans app.py
    # ==============================================================================

    with tab_env3:

        st.markdown("""
        <div style='background-color:#f1f8f5;padding:10px 15px;border-radius:10px;
                    border-left:5px solid #1C3A27;margin-bottom:20px;font-size:0.85em;'>
            <strong>Source :</strong> SISPEA - Système d'Information sur les Services Publics
            d'Eau et d'Assainissement :
            <a href='https://www.services.eaufrance.fr/pro/telechargement#donnees-services'
               target='_blank' style='color:#1C3A27;'>Accéder aux données</a>
            &nbsp;·&nbsp; Données 2020.<br><br>
            <strong>Note sur les données :</strong>
            Les indicateurs portent sur les services publics d'<b>eau potable (AEP)</b>,
            d'<b>assainissement collectif (AC)</b> et d'<b>assainissement non collectif (ANC)</b>.
            Saint-Étienne dispose de plusieurs entités de gestion communales : les indicateurs
            sont agrégés en moyenne pondérée par la population desservie.<br><br>
            Certains indicateurs (collecte, dépollution) peuvent dépasser 100 %. C'est normal,
            les eaux de pluie parasites s'infiltrant dans les réseaux diluent les effluents,
            augmentant le volume traité sans augmenter la charge polluante réelle.<br><br>
            <span style='color:#C62828;font-weight:700;'>⚠️ Rennes Métropole non disponible :</span>
            la compétence eau y est organisée via des syndicats intercommunaux dont les périmètres
            ne correspondent pas à la métropole.
        </div>""", unsafe_allow_html=True)

        # ── Filtres ────────────────────────────────────────────────────────────
        with st.container():
            filter_bar("Filtres - Eau & Assainissement")
            fw1, fw2 = st.columns([1, 3])
            with fw1:
                filter_row_label("Thématique")
            with fw2:
                theme_eau = st.selectbox(
                    "",
                    ["💧 Eau potable (AEP)",
                     "🚿 Assainissement collectif (AC)",
                     "🏡 Assainissement non collectif (ANC)",
                     "💶 Détail tarifaire"],
                    key="env_eau_theme",
                    label_visibility="collapsed",
                )

            METROS_EAU_4 = ["Grenoble", "Montpellier", "Saint-Étienne", "Rouen"]
            sel_metros_eau = st.multiselect(
                "Métropoles à comparer", METROS_EAU_4, default=METROS_EAU_4,
                key="env_eau_metros",
                help="Rennes Métropole n'est pas disponible dans SISPEA pour ces compétences.",
            )

        st.markdown("---")

        if not sel_metros_eau:
            st.warning("Sélectionnez au moins une métropole.")
            st.stop()

        eau_colors = [COULEURS.get(m, "#888888") for m in sel_metros_eau]
        n_eau = len(sel_metros_eau)

        # ── Helpers ────────────────────────────────────────────────────────────
        def get_val(df, metro, col):
            if df is None or col not in df.columns:
                return np.nan
            row = df[df["metropole"] == metro]
            return float(row[col].values[0]) if len(row) > 0 else np.nan

        def fv(v, dec=1, suf=""):
            """Format valeur — retourne N/D si nan."""
            if pd.isna(v):
                return "N/D"
            if dec == 0:
                return f"{int(round(v)):,}".replace(",", "\u202f") + suf
            return f"{v:.{dec}f}{suf}"

        def bar_h_eau(metros, x_vals, colors, title_x, fmt_fn=None):
            """Barres horizontales triées, couleur territoire, hachures Grenoble."""
            rows = [{"t": m, "v": v, "c": c}
                    for m, v, c in zip(metros, x_vals, colors)]
            df_b = pd.DataFrame(rows).dropna(subset=["v"])
            df_b = df_b.sort_values("v", ascending=True)
            if df_b.empty:
                return go.Figure()
            fig = go.Figure()
            for _, r in df_b.iterrows():
                is_g = r["t"] == "Grenoble"
                txt  = fmt_fn(r["v"]) if fmt_fn else f"{r['v']:.1f}"
                mkr  = dict(color=r["c"])
                if is_g:
                    mkr["pattern"] = dict(shape="/", fgcolor="#FF584D",
                                          fillmode="overlay", solidity=0.3, size=20)
                fig.add_trace(go.Bar(
                    y=[r["t"]], x=[r["v"]], orientation="h",
                    name=r["t"], marker=mkr, showlegend=False,
                    text=[txt], textposition="outside", cliponaxis=False,
                    hovertemplate="<b>" + r["t"] + "</b><br>"
                                  + title_x + " : " + txt + "<extra></extra>",
                ))
            fig.update_layout(
                height=120 + len(df_b) * 52,
                margin=dict(t=10, b=10, l=10, r=90),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_family="Sora",
                xaxis=dict(title=title_x, gridcolor="#E8F5EE"),
                yaxis=dict(title=""),
            )
            return fig

        def lollipop_eau(metros, x_vals, colors, title_x, fmt_fn=None,
                         ref_line=None, ref_label=""):
            """Lollipop chart horizontal — plus original que les barres."""
            rows = [{"t": m, "v": v, "c": c}
                    for m, v, c in zip(metros, x_vals, colors)]
            df_b = pd.DataFrame(rows).dropna(subset=["v"])
            df_b = df_b.sort_values("v", ascending=True).reset_index(drop=True)
            if df_b.empty:
                return go.Figure()
            fig = go.Figure()
            # Lignes horizontales (tiges)
            for _, r in df_b.iterrows():
                is_g = r["t"] == "Grenoble"
                fig.add_shape(
                    type="line",
                    x0=0, x1=r["v"], y0=r["t"], y1=r["t"],
                    line=dict(color=r["c"], width=3 if is_g else 2,
                              dash="dot" if is_g else "solid"),
                )
            # Points (têtes)
            txt_list = [fmt_fn(r["v"]) if fmt_fn else f"{r['v']:.1f}"
                        for _, r in df_b.iterrows()]
            fig.add_trace(go.Scatter(
                x=df_b["v"], y=df_b["t"],
                mode="markers+text",
                marker=dict(
                    size=[16 if t == "Grenoble" else 12 for t in df_b["t"]],
                    color=df_b["c"].tolist(),
                    line=dict(
                        color=["#FF584D" if t == "Grenoble" else "white"
                               for t in df_b["t"]],
                        width=[3 if t == "Grenoble" else 1.5 for t in df_b["t"]],
                    ),
                    symbol=["diamond" if t == "Grenoble" else "circle"
                            for t in df_b["t"]],
                ),
                text=txt_list,
                textposition="middle right",
                textfont=dict(size=10, family="Sora"),
                showlegend=False,
                hovertemplate=[
                    "<b>" + r["t"] + "</b><br>" + title_x + " : " + txt_list[i]
                    + "<extra></extra>"
                    for i, (_, r) in enumerate(df_b.iterrows())
                ],
            ))
            if ref_line is not None:
                fig.add_vline(x=ref_line, line_dash="dot",
                              line_color="#888", line_width=1.5)
                fig.add_annotation(
                    x=ref_line, y=len(df_b) - 0.3,
                    text=ref_label, showarrow=False,
                    font=dict(size=9, color="#888", family="Sora"),
                    xanchor="left", xshift=4,
                )
            fig.update_layout(
                height=120 + len(df_b) * 52,
                margin=dict(t=10, b=10, l=10, r=110),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_family="Sora",
                xaxis=dict(title=title_x, gridcolor="#E8F5EE", range=[0, None]),
                yaxis=dict(title="", showgrid=False),
            )
            return fig

        def radar_eau(metros, cols, labels, df_data, colors):
            """Radar multi-métropoles normalisé 0-100 sur les valeurs du panel."""
            fig = go.Figure()
            vals_norm = {}
            for col in cols:
                raw = [get_val(df_data, m, col) for m in metros]
                clean = [v for v in raw if pd.notna(v)]
                if not clean:
                    vals_norm[col] = [0.0] * len(metros)
                    continue
                mn, mx = min(clean), max(clean)
                vals_norm[col] = [
                    (v - mn) / (mx - mn) * 100 if pd.notna(v) and mx != mn
                    else (50.0 if pd.notna(v) else 0.0)
                    for v in raw
                ]
            for i, (m, c) in enumerate(zip(metros, colors)):
                is_g = m == "Grenoble"
                r_vals = [vals_norm[col][i] for col in cols]
                r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
                fig.add_trace(go.Scatterpolar(
                    r=r_vals + [r_vals[0]],
                    theta=labels + [labels[0]],
                    fill="toself",
                    fillcolor=f"rgba({r},{g},{b},0.10)",
                    name=m,
                    line=dict(color="#FF584D" if is_g else c,
                              width=3 if is_g else 2,
                              dash="dot" if is_g else "solid"),
                    hovertemplate="<b>" + m + "</b><br>%{theta}<extra></extra>",
                ))
            fig.update_layout(
                height=380, margin=dict(t=50, b=40),
                paper_bgcolor="rgba(0,0,0,0)", font_family="Sora",
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(gridcolor="#E8F5EE", range=[0, 110],
                                   tickfont=dict(size=8), showticklabels=False),
                    angularaxis=dict(gridcolor="#E8F5EE"),
                ),
                legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                            font=dict(size=10)),
            )
            return fig

        def scatter_eau(metros, x_vals, y_vals, colors, xlabel, ylabel):
            """Scatter avec bulles et annotations."""
            fig = go.Figure()
            for m, xv, yv, c in zip(metros, x_vals, y_vals, colors):
                if pd.isna(xv) or pd.isna(yv):
                    continue
                is_g = m == "Grenoble"
                fig.add_trace(go.Scatter(
                    x=[xv], y=[yv], mode="markers+text",
                    name=m, text=[m], textposition="top center",
                    textfont=dict(size=10, color="#FF584D" if is_g else c,
                                  family="Sora"),
                    marker=dict(
                        size=20, color=c,
                        line=dict(color="#FF584D" if is_g else "white",
                                  width=3 if is_g else 1.5),
                        symbol="diamond" if is_g else "circle",
                    ),
                    hovertemplate=(
                        "<b>" + m + "</b><br>"
                        + xlabel + " : %{x:.2f}<br>"
                        + ylabel + " : %{y:.1f}<extra></extra>"
                    ),
                ))
            fig.update_layout(
                height=360, margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_family="Sora", showlegend=False,
                xaxis=dict(title=xlabel, gridcolor="#E8F5EE"),
                yaxis=dict(title=ylabel, gridcolor="#E8F5EE"),
            )
            return fig

        # ══════════════════════════════════════════════════════════════════════
        # 💧 EAU POTABLE (AEP)
        # ══════════════════════════════════════════════════════════════════════
        if "Eau potable" in theme_eau:

            if df_aep_eau is None:
                st.info("📂 Fichier eau potable introuvable.")
                st.stop()

            df_sel = df_aep_eau[df_aep_eau["metropole"].isin(sel_metros_eau)].copy()

            # ── KPI — pattern identique aux autres onglets ────────────────────
            st.subheader("Indicateurs clés — Eau potable 2020")
            kpi_cols_aep = st.columns(n_eau)
            for i, m in enumerate(sel_metros_eau):
                kpi_color = eau_colors[i]
                abo    = get_val(df_sel, m, "D101.0")
                prix   = get_val(df_sel, m, "D102.0")
                conf   = get_val(df_sel, m, "P103.2B")
                rendmt = get_val(df_sel, m, "VP.020")
                abo_str    = fv(abo, 0)
                prix_str   = fv(prix, 2, " €/m³")
                conf_str   = fv(conf, 0, "%")
                rendmt_str = fv(rendmt, 0, "%")
                html_card = (
                    "<div style='display:flex;flex-direction:column;justify-content:center;"
                    "border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);"
                    "background:#fff;min-height:80px;"
                    f"border-left:6px solid {kpi_color};padding:12px 16px;margin-bottom:10px;'>"
                    f"<div style='font-size:11px;font-weight:700;letter-spacing:0.08em;"
                    f"color:#666;text-transform:uppercase;'>{m}</div>"
                    f"<div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>"
                    f"{abo_str}</div>"
                    f"<div style='font-size:11px;font-weight:700;color:{kpi_color};"
                    f"text-transform:uppercase;letter-spacing:0.05em;'>abonnés AEP</div>"
                    f"<div style='margin-top:6px;font-size:11px;color:#555;'>"
                    f"Prix TTC 120m³ : <b style='color:#E65100;'>{prix_str}</b><br>"
                    f"Conformité : <b style='color:#2E7D32;'>{conf_str}</b>"
                    f"&nbsp;&nbsp;·&nbsp;&nbsp;"
                    f"Rendement : <b style='color:#7B1FA2;'>{rendmt_str}</b>"
                    f"</div></div>"
                )
                with kpi_cols_aep[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphique 1 : Lollipop Prix + Lollipop Rendement ─────────────
            g1, g2 = st.columns(2)
            with g1:
                st.subheader(
                    "Prix de l'eau TTC à 120 m³ (€/m³)",
                    help=(
                        "D102.0 : référence nationale SISPEA. Inclut part eau + "
                        "redevances agence de l'eau + TVA. "
                        "Pour Saint-Étienne : moyenne pondérée par population."
                    ),
                )
                x = [get_val(df_sel, m, "D102.0") for m in sel_metros_eau]
                st.plotly_chart(style(lollipop_eau(sel_metros_eau, x, eau_colors,
                    "€/m³ TTC", fmt_fn=lambda v: f"{v:.2f} €")),
                    use_container_width=True)

            with g2:
                st.subheader(
                    "Rendement du réseau (%)",
                    help=(
                        "VP.020 : volume consommé / volume distribué × 100. "
                        "< 70 % = réseau très fuiteux. Objectif : 85 %."
                    ),
                )
                x = [get_val(df_sel, m, "VP.020") for m in sel_metros_eau]
                st.plotly_chart(style(lollipop_eau(sel_metros_eau, x, eau_colors,
                    "%", fmt_fn=lambda v: f"{v:.0f}%",
                    ref_line=85, ref_label="Objectif 85 %")),
                    use_container_width=True)

            with st.expander("💡 Interpréter ces graphiques"):
                st.write(
                    "**Prix de l'eau** : la forme en lollipop met en évidence l'écart "
                    "entre les métropoles. Montpellier et Grenoble bénéficient de "
                    "ressources abondantes (Rhône, massif alpin) qui limitent les coûts "
                    "de production.\n\n"
                    "**Rendement réseau** : la ligne pointillée indique l'objectif "
                    "réglementaire de 85 %. Un rendement inférieur signale des fuites "
                    "importantes — coûteuses et contraires à l'objectif de sobriété hydrique. "
                    "Grenoble apparaît en losange rouge avec tige pointillée."
                )

            st.markdown("---")

            # ── Graphique 2 : Radar qualité eau ──────────────────────────────
            st.subheader(
                "Radar de performance — Eau potable",
                help=(
                    "Comparaison normalisée (0 = moins bonne valeur du panel, "
                    "100 = meilleure valeur) sur 4 indicateurs de qualité. "
                    "Plus la surface est étendue, plus la métropole est performante."
                ),
            )
            st.plotly_chart(style(radar_eau(
                sel_metros_eau,
                ["P103.2B", "VP.020", "P108.3", "P152.1"],
                ["Conformité eau\n(%)", "Rendement\nréseau (%)",
                 "Protection\ncaptages (%)", "Conformité\nmicrobiologique (%)"],
                df_sel, eau_colors,
            )), use_container_width=True)

            with st.expander("💡 Interpréter le radar"):
                st.write(
                    "Les axes sont normalisés : 100 = meilleure valeur du panel, "
                    "0 = moins bonne. Ce graphique montre la position relative de "
                    "chaque métropole — pas les valeurs absolues. "
                    "Grenoble apparaît en pointillé rouge.\n\n"
                    "**P103.2B** : conformité analyses eau distribuée (ARS).\n"
                    "**VP.020** : rendement réseau (moins de fuites = mieux).\n"
                    "**P108.3** : captages avec arrêté de protection.\n"
                    "**P152.1** : conformité microbiologique spécifique."
                )

            st.markdown("---")

            # ── Graphique 3 : Scatter Prix vs Rendement ───────────────────────
            g3, g4 = st.columns(2)
            with g3:
                st.subheader(
                    "Prix vs Rendement réseau",
                    help=(
                        "Un réseau efficace (haut rendement = moins d'eau perdue) "
                        "devrait se traduire par un coût moindre. Ce scatter met en "
                        "regard performance technique et coût pour l'abonné."
                    ),
                )
                x_sc = [get_val(df_sel, m, "D102.0") for m in sel_metros_eau]
                y_sc = [get_val(df_sel, m, "VP.020") for m in sel_metros_eau]
                st.plotly_chart(style(scatter_eau(
                    sel_metros_eau, x_sc, y_sc, eau_colors,
                    "Prix TTC (€/m³)", "Rendement réseau (%)"
                )), use_container_width=True)

            with g4:
                st.subheader(
                    "Pertes réseau et protection captages",
                    help=(
                        "P105.3 : pertes par fuite (m³/km/j). "
                        "P108.3 : % captages protégés. "
                        "Deux dimensions complémentaires de la sobriété hydrique."
                    ),
                )
                x_sc2 = [get_val(df_sel, m, "P105.3") for m in sel_metros_eau]
                y_sc2 = [get_val(df_sel, m, "P108.3") for m in sel_metros_eau]
                st.plotly_chart(style(scatter_eau(
                    sel_metros_eau, x_sc2, y_sc2, eau_colors,
                    "Pertes réseau (m³/km/j)", "Protection captages (%)"
                )), use_container_width=True)

            with st.expander("💡 Interpréter ces graphiques"):
                st.write(
                    "**Prix vs Rendement** : idéalement, un territoire doit se "
                    "positionner en bas à droite (prix faible, rendement élevé). "
                    "Un territoire en haut à gauche a un réseau inefficace ET cher.\n\n"
                    "**Pertes vs Protection captages** : un territoire avec peu de "
                    "pertes ET des captages bien protégés est doublement engagé dans "
                    "la préservation de la ressource en eau."
                )

        # ══════════════════════════════════════════════════════════════════════
        # 🚿 ASSAINISSEMENT COLLECTIF (AC)
        # ══════════════════════════════════════════════════════════════════════
        elif "collectif" in theme_eau:

            if df_ac_eau is None:
                st.info("📂 Fichier assainissement collectif introuvable.")
                st.stop()

            df_sel = df_ac_eau[df_ac_eau["metropole"].isin(sel_metros_eau)].copy()

            # ── KPI ──────────────────────────────────────────────────────────
            st.subheader("Indicateurs clés — Assainissement collectif 2020")
            kpi_cols_ac = st.columns(n_eau)
            for i, m in enumerate(sel_metros_eau):
                kpi_color = eau_colors[i]
                abo  = get_val(df_sel, m, "D201.0")
                dbo  = get_val(df_sel, m, "D202.0")
                coll = get_val(df_sel, m, "P203.3")
                depo = get_val(df_sel, m, "P255.3")
                abo_str  = fv(abo, 0)
                dbo_str  = fv(dbo, 0, " kg/j")
                coll_str = fv(coll, 0, "%")
                depo_str = fv(depo, 0, "%")
                html_card = (
                    "<div style='display:flex;flex-direction:column;justify-content:center;"
                    "border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);"
                    "background:#fff;min-height:80px;"
                    f"border-left:6px solid {kpi_color};padding:12px 16px;margin-bottom:10px;'>"
                    f"<div style='font-size:11px;font-weight:700;letter-spacing:0.08em;"
                    f"color:#666;text-transform:uppercase;'>{m}</div>"
                    f"<div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>"
                    f"{abo_str}</div>"
                    f"<div style='font-size:11px;font-weight:700;color:{kpi_color};"
                    f"text-transform:uppercase;letter-spacing:0.05em;'>abonnés AC</div>"
                    f"<div style='margin-top:6px;font-size:11px;color:#555;'>"
                    f"Charge DBO5 : <b style='color:#E65100;'>{dbo_str}</b><br>"
                    f"Collecte : <b style='color:#2E7D32;'>{coll_str}</b>"
                    f"&nbsp;&nbsp;·&nbsp;&nbsp;"
                    f"Dépollution : <b style='color:#7B1FA2;'>{depo_str}</b>"
                    f"</div></div>"
                )
                with kpi_cols_ac[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphique 1 : Radar conformité AC ────────────────────────────
            st.subheader(
                "Radar de conformité — Assainissement collectif",
                help=(
                    "Comparaison normalisée (0-100) des 4 indicateurs de conformité. "
                    "Les axes ne représentent pas les valeurs absolues mais les "
                    "positions relatives entre métropoles."
                ),
            )
            st.plotly_chart(style(radar_eau(
                sel_metros_eau,
                ["P204.3", "P205.3", "P203.3", "P206.3"],
                ["Équipements\nSTEP (%)", "Performance\népuration (%)",
                 "Collecte\neffluents (%)", "Boues\nconformes (%)"],
                df_sel, eau_colors,
            )), use_container_width=True)

            with st.expander("💡 Interpréter le radar"):
                st.write(
                    "**P204.3** : équipements STEP aux normes (directive ERU 1991).\n"
                    "**P205.3** : objectifs de traitement atteints.\n"
                    "**P203.3** : effluents bien acheminés vers les STEP.\n"
                    "**P206.3** : boues valorisées réglementairement.\n\n"
                    "Des valeurs > 100 % pour P203.3 et P255.3 sont normales : "
                    "les eaux parasites de pluie s'infiltrent dans les réseaux, "
                    "diluant les effluents sans augmenter la charge polluante réelle."
                )

            st.markdown("---")

            # ── Graphique 2 : Lollipop conformité + barres dépollution ────────
            g1, g2 = st.columns(2)
            with g1:
                st.subheader(
                    "Conformité équipements et performance épuration",
                    help="P204.3 et P205.3 : les deux indicateurs de conformité réglementaire des STEP.",
                )
                # Grouped lollipop : P204 et P205 côte à côte
                fig_conf = go.Figure()
                for j, (col, label, offset) in enumerate([
                    ("P204.3", "Équipements", -0.2),
                    ("P205.3", "Performance", 0.2),
                ]):
                    x_c = [get_val(df_sel, m, col) for m in sel_metros_eau]
                    rows = [{"t": m, "v": v, "c": c, "off": offset}
                            for m, v, c in zip(sel_metros_eau, x_c, eau_colors)]
                    df_c = pd.DataFrame(rows).dropna(subset=["v"])
                    for _, r in df_c.iterrows():
                        is_g = r["t"] == "Grenoble"
                        fig_conf.add_shape(
                            type="line",
                            x0=0, x1=r["v"],
                            y0=r["t"], y1=r["t"],
                            line=dict(color=r["c"],
                                      width=3 if is_g else 1.5,
                                      dash="dot" if is_g else "solid"),
                        )
                    fig_conf.add_trace(go.Scatter(
                        x=df_c["v"], y=df_c["t"],
                        mode="markers", name=label,
                        marker=dict(
                            size=[14 if t == "Grenoble" else 10 for t in df_c["t"]],
                            color=df_c["c"].tolist(),
                            symbol=["diamond" if t == "Grenoble" else
                                    ("circle" if j == 0 else "square")
                                    for t in df_c["t"]],
                            line=dict(
                                color=["#FF584D" if t == "Grenoble" else "white"
                                       for t in df_c["t"]],
                                width=[2 if t == "Grenoble" else 1 for t in df_c["t"]],
                            ),
                        ),
                        hovertemplate=[
                            "<b>" + t + "</b><br>" + label + " : "
                            + fv(v, 1, "%") + "<extra></extra>"
                            for t, v in zip(df_c["t"], df_c["v"])
                        ],
                    ))
                fig_conf.update_layout(
                    height=120 + n_eau * 52,
                    margin=dict(t=10, b=10, l=10, r=20),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    xaxis=dict(title="%", gridcolor="#E8F5EE"),
                    yaxis=dict(title="", showgrid=False),
                    legend=dict(orientation="h", y=1.1, x=0),
                )
                st.plotly_chart(style(fig_conf), use_container_width=True)

            with g2:
                st.subheader(
                    "Taux de dépollution (%)",
                    help=(
                        "P255.3 : % DBO5 éliminée. Peut dépasser 100 % en raison "
                        "de la dilution des effluents par les eaux parasites de pluie."
                    ),
                )
                x = [get_val(df_sel, m, "P255.3") for m in sel_metros_eau]
                st.plotly_chart(style(bar_h_eau(sel_metros_eau, x, eau_colors,
                    "% DBO5 éliminée", fmt_fn=lambda v: f"{v:.0f}%")),
                    use_container_width=True)

            with st.expander("💡 Interpréter ces graphiques"):
                st.write(
                    "**Lollipop double** : les cercles = équipements (P204.3), "
                    "les carrés = performance (P205.3). Une STEP peut être conforme "
                    "en équipements mais sous-performante lors de pics de charge.\n\n"
                    "**Dépollution (P255.3)** : peut dépasser 100 % — c'est normal. "
                    "Les eaux de pluie s'infiltrant dans les réseaux diluent les "
                    "effluents : le volume traité augmente mais la charge polluante "
                    "entrante reste identique, ce qui fait monter mécaniquement le taux."
                )

            st.markdown("---")

            # ── Graphique 3 : Scatter abonnés vs DBO5 ─────────────────────────
            st.subheader(
                "Volume d'activité : abonnés vs charge polluante (DBO5)",
                help=(
                    "Un écart important entre abonnés et charge DBO5 peut révéler "
                    "la présence d'activités industrielles (forte charge / abonné) "
                    "ou d'infiltrations parasites importantes (charge diluée)."
                ),
            )
            x_ac = [get_val(df_sel, m, "D201.0") for m in sel_metros_eau]
            y_ac = [get_val(df_sel, m, "D202.0") for m in sel_metros_eau]
            st.plotly_chart(style(scatter_eau(
                sel_metros_eau, x_ac, y_ac, eau_colors,
                "Abonnés AC", "Charge DBO5 (kg/j)"
            )), use_container_width=True)

            with st.expander("💡 Interpréter ce graphique"):
                st.write(
                    "La relation entre abonnés et charge DBO5 devrait être linéaire "
                    "(plus d'abonnés = plus de pollution à traiter). Un point au-dessus "
                    "de la tendance signale une charge industrielle importante. "
                    "Un point en dessous peut indiquer un grand nombre d'infiltrations "
                    "parasites (eaux claires) qui diluent les effluents."
                )

        # ══════════════════════════════════════════════════════════════════════
        # 🏡 ASSAINISSEMENT NON COLLECTIF (ANC)
        # ══════════════════════════════════════════════════════════════════════
        elif "non collectif" in theme_eau:

            if df_anc_eau is None:
                st.info("📂 Fichier assainissement non collectif introuvable.")
                st.stop()

            df_sel = df_anc_eau[df_anc_eau["metropole"].isin(sel_metros_eau)].copy()
            for col_anc in ["D301.0", "D302.0", "P301.3", "VP.181", "VP.167", "VP.166"]:
                if col_anc in df_sel.columns:
                    df_sel[col_anc] = pd.to_numeric(
                        df_sel[col_anc].astype(str).str.replace(",", "."),
                        errors="coerce")

            # ── KPI ──────────────────────────────────────────────────────────
            st.subheader("Indicateurs clés — Assainissement non collectif 2020")
            kpi_cols_anc = st.columns(n_eau)
            for i, m in enumerate(sel_metros_eau):
                kpi_color = eau_colors[i]
                nb    = get_val(df_sel, m, "D301.0")
                conf  = get_val(df_sel, m, "D302.0")
                rehab = get_val(df_sel, m, "P301.3")
                nc    = get_val(df_sel, m, "VP.166")
                nb_str    = fv(nb, 0)
                conf_str  = fv(conf, 0, "%")
                rehab_str = fv(rehab, 1, "%")
                nc_str    = fv(nc, 0)
                html_card = (
                    "<div style='display:flex;flex-direction:column;justify-content:center;"
                    "border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);"
                    "background:#fff;min-height:80px;"
                    f"border-left:6px solid {kpi_color};padding:12px 16px;margin-bottom:10px;'>"
                    f"<div style='font-size:11px;font-weight:700;letter-spacing:0.08em;"
                    f"color:#666;text-transform:uppercase;'>{m}</div>"
                    f"<div style='font-size:24px;font-weight:bold;color:#111;margin:4px 0;'>"
                    f"{nb_str}</div>"
                    f"<div style='font-size:11px;font-weight:700;color:{kpi_color};"
                    f"text-transform:uppercase;letter-spacing:0.05em;'>installations ANC</div>"
                    f"<div style='margin-top:6px;font-size:11px;color:#555;'>"
                    f"Conformité : <b style='color:#2E7D32;'>{conf_str}</b>"
                    f"&nbsp;&nbsp;·&nbsp;&nbsp;"
                    f"Réhabilitation : <b style='color:#E65100;'>{rehab_str}</b><br>"
                    f"Non conformes : <b style='color:#C62828;'>{nc_str}</b>"
                    f"</div></div>"
                )
                with kpi_cols_anc[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphique 1 : Barres installations + lollipop conformité ─────
            g1, g2 = st.columns(2)
            with g1:
                st.subheader(
                    "Installations ANC recensées",
                    help="D301.0 : nombre total de dispositifs ANC recensés sur le territoire.",
                )
                x = [get_val(df_sel, m, "D301.0") for m in sel_metros_eau]
                st.plotly_chart(style(bar_h_eau(sel_metros_eau, x, eau_colors,
                    "installations",
                    fmt_fn=lambda v: f"{int(v):,}".replace(",", "\u202f"))),
                    use_container_width=True)

            with g2:
                st.subheader(
                    "Taux de conformité ANC (%)",
                    help=(
                        "D302.0 : part des installations conformes au dernier contrôle SPANC. "
                        "Une installation non conforme présente un risque sanitaire "
                        "ou environnemental (pollution des nappes, cours d'eau)."
                    ),
                )
                x = [get_val(df_sel, m, "D302.0") for m in sel_metros_eau]
                st.plotly_chart(style(lollipop_eau(sel_metros_eau, x, eau_colors,
                    "% conformes", fmt_fn=lambda v: f"{v:.0f}%")),
                    use_container_width=True)

            with st.expander("💡 Interpréter ces graphiques"):
                st.write(
                    "L'ANC concerne les habitations hors réseau collectif. "
                    "Le SPANC contrôle et conseille les propriétaires.\n\n"
                    "Un nombre élevé d'installations ne signifie pas que la métropole "
                    "est moins performante en assainissement collectif : cela reflète "
                    "souvent un territoire plus rural ou étendu."
                )

            st.markdown("---")

            # ── Graphique 2 : Scatter conformité vs réhabilitation ────────────
            st.subheader(
                "Conformité vs taux de réhabilitation — Trajectoire ANC",
                help=(
                    "Un territoire avec un faible taux de conformité mais un taux "
                    "de réhabilitation élevé est en bonne trajectoire. "
                    "À l'inverse, faible conformité + faible réhabilitation "
                    "signale un parc dégradé sans politique active de mise aux normes."
                ),
            )
            x_anc = [get_val(df_sel, m, "D302.0") for m in sel_metros_eau]
            y_anc = [get_val(df_sel, m, "P301.3") for m in sel_metros_eau]
            fig_anc = scatter_eau(sel_metros_eau, x_anc, y_anc, eau_colors,
                                  "Taux de conformité (%)", "Taux de réhabilitation (%)")
            # Quadrant annotations
            x_clean = [v for v in x_anc if pd.notna(v)]
            y_clean = [v for v in y_anc if pd.notna(v)]
            if x_clean and y_clean:
                xm = (min(x_clean) + max(x_clean)) / 2
                ym = (min(y_clean) + max(y_clean)) / 2
                for qx, qy, label, col_q in [
                    (xm * 0.5,   ym * 1.5,   "Bon taux réhab.\nconformité à améliorer", "#2E7D32"),
                    (xm * 1.5,   ym * 1.5,   "Situation\nidéale", "#1565C0"),
                    (xm * 0.5,   ym * 0.5,   "Situation\ncritique", "#C62828"),
                    (xm * 1.5,   ym * 0.5,   "Bonne conformité\nréhab. à renforcer", "#E65100"),
                ]:
                    fig_anc.add_annotation(
                        x=qx, y=qy, text=label, showarrow=False,
                        font=dict(size=8, color=col_q, family="Sora"),
                        opacity=0.5,
                    )
            st.plotly_chart(style(fig_anc), use_container_width=True)

        # ══════════════════════════════════════════════════════════════════════
        # 💶 DÉTAIL TARIFAIRE
        # ══════════════════════════════════════════════════════════════════════
        else:

            if df_tar_eau is None:
                st.info("📂 Fichier tarifaire introuvable.")
                st.stop()

            df_sel_tar = df_tar_eau[df_tar_eau["metropole"].isin(sel_metros_eau)].copy()
            pop_col_tar = "Pop de l'entité de gestion sans double compte"

            st.markdown("""
            <div style='background:#fff8e1;padding:10px 14px;border-radius:8px;
                        border-left:4px solid #F9A825;font-size:0.85em;margin-bottom:16px;'>
                <b>Structure de la facture d'eau :</b> prix volumique HT + abonnement
                + redevances agence de l'eau + TVA (5,5 % eau potable, 10 % assainissement).
                Pour Saint-Étienne, chaque commune a un tarif propre :
                les valeurs sont des moyennes pondérées par le nombre d'abonnés.
            </div>""", unsafe_allow_html=True)

            def agg_tar(metro, col):
                sub = df_sel_tar[df_sel_tar["metropole"] == metro].copy()
                if sub.empty or col not in sub.columns:
                    return np.nan
                sub[col] = pd.to_numeric(
                    sub[col].astype(str).str.replace(",", "."), errors="coerce")
                sub[pop_col_tar] = pd.to_numeric(
                    sub[pop_col_tar], errors="coerce").fillna(0)
                valid = sub[[col, pop_col_tar]].dropna(subset=[col])
                if len(valid) == 0:
                    return np.nan
                tot = valid[pop_col_tar].sum()
                return float((valid[col] * valid[pop_col_tar]).sum() / tot
                             if tot > 0 else valid[col].mean())

            # ── KPI tarifaires ────────────────────────────────────────────────
            st.subheader("Indicateurs tarifaires — Eau 2020")
            kpi_cols_tar = st.columns(n_eau)
            for i, m in enumerate(sel_metros_eau):
                kpi_color = eau_colors[i]
                d102   = agg_tar(m, "D102.0")
                p_eau  = agg_tar(m, "VP.179")
                p_fix  = agg_tar(m, "VP.178")
                p_rdev = agg_tar(m, "VP.216")
                d102_str  = fv(d102, 2, " €/m³")
                p_eau_str = fv(p_eau, 2, " €/m³")
                p_fix_str = fv(p_fix, 0, " €/an")
                rdv_str   = fv(p_rdev, 3, " €/m³")
                html_card = (
                    "<div style='display:flex;flex-direction:column;justify-content:center;"
                    "border-radius:8px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);"
                    "background:#fff;min-height:80px;"
                    f"border-left:6px solid {kpi_color};padding:12px 16px;margin-bottom:10px;'>"
                    f"<div style='font-size:11px;font-weight:700;letter-spacing:0.08em;"
                    f"color:#666;text-transform:uppercase;'>{m}</div>"
                    f"<div style='font-size:24px;font-weight:bold;color:#E65100;margin:4px 0;'>"
                    f"{d102_str}</div>"
                    f"<div style='font-size:11px;font-weight:700;color:{kpi_color};"
                    f"text-transform:uppercase;letter-spacing:0.05em;'>prix TTC tout compris</div>"
                    f"<div style='margin-top:6px;font-size:11px;color:#555;'>"
                    f"Part volumique HT : <b style='color:#1565C0;'>{p_eau_str}</b><br>"
                    f"Abonnement : <b style='color:#2E7D32;'>{p_fix_str}</b>"
                    f"&nbsp;&nbsp;·&nbsp;&nbsp;"
                    f"Redevance agence : <b style='color:#7B1FA2;'>{rdv_str}</b>"
                    f"</div></div>"
                )
                with kpi_cols_tar[i]:
                    st.markdown(html_card, unsafe_allow_html=True)

            st.markdown("---")

            # ── Graphique 1 : Décomposition facture (stacked bar horizontal) ──
            st.subheader(
                "Décomposition de la facture eau potable (€/m³)",
                help=(
                    "Visualisation des composantes du prix : part volumique collectivité, "
                    "redevance agence de l'eau, TVA. L'abonnement n'est pas inclus car "
                    "il est annuel et non volumique."
                ),
            )
            comp_data = []
            for m in sel_metros_eau:
                p_vol  = agg_tar(m, "VP.179")
                p_rdev = agg_tar(m, "VP.216")
                p_tva  = agg_tar(m, "VP.213")
                if not any(pd.isna(v) for v in [p_vol, p_rdev]):
                    tva_val = (p_vol + p_rdev) * (p_tva / 100) if pd.notna(p_tva) else 0
                    comp_data.append({
                        "m": m,
                        "Vol. collectivité HT": p_vol if pd.notna(p_vol) else 0,
                        "Redevance agence": p_rdev if pd.notna(p_rdev) else 0,
                        "TVA": tva_val,
                    })

            if comp_data:
                df_comp = pd.DataFrame(comp_data)
                fig_comp = go.Figure()
                composantes = [
                    ("Vol. collectivité HT", "#1565C0"),
                    ("Redevance agence",     "#7B1FA2"),
                    ("TVA",                  "#AAAAAA"),
                ]
                for comp_name, comp_color in composantes:
                    fig_comp.add_trace(go.Bar(
                        y=df_comp["m"], x=df_comp[comp_name],
                        name=comp_name, orientation="h",
                        marker_color=comp_color,
                        hovertemplate=(
                            "<b>%{y}</b><br>" + comp_name
                            + " : %{x:.3f} €/m³<extra></extra>"
                        ),
                    ))
                apply_grenoble_hatch(fig_comp, active=True)
                fig_comp.update_layout(
                    barmode="stack",
                    height=120 + n_eau * 52,
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_family="Sora",
                    xaxis=dict(title="€/m³", gridcolor="#E8F5EE"),
                    yaxis=dict(title=""),
                    legend=dict(orientation="h", y=1.08, x=0),
                )
                st.plotly_chart(style(fig_comp), use_container_width=True)

            st.markdown("---")

            # ── Graphique 2 : Lollipop prix volumique + scatter fixe vs vol ───
            g1, g2 = st.columns(2)
            with g1:
                st.subheader(
                    "Prix volumique eau potable HT (€/m³)",
                    help=(
                        "VP.179 : prix hors taxes du m³, part collectivité "
                        "(hors abonnement, redevances, TVA). "
                        "Principal levier pour inciter à la sobriété hydrique."
                    ),
                )
                x = [agg_tar(m, "VP.179") for m in sel_metros_eau]
                st.plotly_chart(style(lollipop_eau(sel_metros_eau, x, eau_colors,
                    "€/m³ HT", fmt_fn=lambda v: f"{v:.2f} €")),
                    use_container_width=True)

            with g2:
                st.subheader(
                    "Abonnement annuel vs prix volumique",
                    help=(
                        "Une part fixe élevée (abonnement) signifie qu'une grande "
                        "partie de la facture est indépendante de la consommation — "
                        "ce qui peut freiner les efforts de sobriété hydrique. "
                        "Idéal : abonnement bas + prix volumique modéré."
                    ),
                )
                x_t = [agg_tar(m, "VP.179") for m in sel_metros_eau]
                y_t = [agg_tar(m, "VP.178") for m in sel_metros_eau]
                st.plotly_chart(style(scatter_eau(
                    sel_metros_eau, x_t, y_t, eau_colors,
                    "Prix volumique HT (€/m³)", "Abonnement annuel (€/an)"
                )), use_container_width=True)

            with st.expander("💡 Comprendre la structure du tarif de l'eau"):
                st.write(
                    "**Prix volumique (VP.179)** : coût du m³ hors taxes, part "
                    "collectivité. Montpellier et Grenoble sont les moins chères grâce "
                    "à des ressources abondantes.\n\n"
                    "**Abonnement (VP.178)** : forfait annuel indépendant de la "
                    "consommation. Un abonnement élevé pénalise les petits consommateurs "
                    "et dilue l'effet incitatif du prix volumique.\n\n"
                    "**TVA** : 5,5 % pour l'eau potable, 10 % pour l'assainissement.\n\n"
                    "**Redevance agence (VP.216)** : contribution au financement des "
                    "travaux dans le bassin versant — Rhône-Méditerranée (Grenoble, "
                    "Montpellier), Seine-Normandie (Rouen), Loire-Bretagne (Saint-Étienne)."
                )

    # # ── Onglet 4 : Déchets & Transition ──────────────────────────────────────
    # with tab_env4:
    #     filter_bar("Filtres - Déchets & Transition")
    #     f_col5, f_col6 = st.columns(2)
    #     with f_col5:
    #         metros_dech = st.multiselect(
    #             "Sélectionner les métropoles :", TOUTES,
    #             default=shared_default_env(TOUTES), key="env_dechets_metros", on_change=sync_metros_env, args=("env_dechets_metros",)
    #         )
    #     with f_col6:
    #         communes_dech = st.multiselect(
    #             "Sélectionner les communes (Grenoble) :", COMMUNES_GRENOBLE,
    #             default=shared_default_communes_env(COMMUNES_GRENOBLE), key="env_dechets_communes", on_change=sync_communes_env, args=("env_dechets_communes",)
    #         )
    #     st.markdown('</div>', unsafe_allow_html=True)
        
    #     st.info("Données en cours de traitement. Intégrez vos graphiques de production de déchets ménagers et de tri sélectif ici.")