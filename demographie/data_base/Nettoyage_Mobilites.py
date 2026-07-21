# ==============================================================================
# SCRIPT DE PRÉTRAITEMENT DES 3 FICHIERS DE MOBILITÉ
# PÉRIMÈTRE : FRANCE MÉTROPOLITAINE STRICTE
# ==============================================================================

import pandas as pd
import os
from pathlib import Path
import re

# ── GESTION DES CHEMINS ───────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
INPUT_DIR = SCRIPT_DIR
OUTPUT_DIR = SCRIPT_DIR.parent / "data_clean" / "mobilite"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── RÉFÉRENTIELS GÉOGRAPHIQUES ────────────────────────────────────────────────
# Génération stricte des départements de France métropolitaine (01 à 95 + 2A/2B)
DEPS_FRANCE_METRO = [str(i).zfill(2) for i in range(1, 96) if i != 20] + ["2A", "2B"]
DEPS_METROPOLES = {"38", "35", "76", "42", "34"}

COMMUNES_GRENOBLE = [
    "Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix",
    "Corenc","Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon",
    "Gières","Grenoble","Herbeys","Jarrie","La Tronche","Le Gua",
    "Le Pont-de-Claix","Le Sappey-en-Chartreuse","Meylan","Miribel-Lanchâtre",
    "Mont-Saint-Martin","Montchaboud","Murianette","Notre-Dame-de-Commiers",
    "Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux","Quaix-en-Chartreuse",
    "Saint-Barthélemy-de-Séchilienne","Saint-Égrève","Saint-Georges-de-Commiers",
    "Saint-Martin-d'Hères","Saint-Martin-le-Vinoux","Saint-Paul-de-Varces",
    "Saint-Pierre-de-Mésage","Sarcenas","Sassenage","Séchilienne",
    "Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset",
    "Vaulnaveys-le-Bas","Vaulnaveys-le-Haut","Venon","Veurey-Voroize",
    "Vif","Vizille",
]
COMMUNES_RENNES = [
    "Acigné","Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné",
    "Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré",
    "Corps-Nuds","Gévezé","La Chapelle-des-Fougeretz",
    "La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger",
    "Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou",
    "Orgères","Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes",
    "Romillé","Saint-Armel","Saint-Erblon","Saint-Gilles",
    "Saint-Grégoire","Saint-Jacques-de-la-Lande",
    "Saint-Sulpice-la-Forêt","Thorigné-Fouillard","Vern-sur-Seiche",
    "Vezin-le-Coquet","Clayes","La Chapelle-Chaussée",
    "Laillé","Langan","Miniac-sous-Bécherel",
]
COMMUNES_ROUEN = [
    "Amfreville-la-Mi-Voie","Anneville-Ambourville","Bardouville","Belbeuf",
    "Berville-sur-Seine","Bihorel","Bois-Guillaume","Bonsecours","Boos",
    "Canteleu","Caudebec-lès-Elbeuf","Cléon","Darnétal","Déville-lès-Rouen",
    "Duclair","Elbeuf","Épinay-sur-Duclair","Fontaine-sous-Préaux",
    "Franqueville-Saint-Pierre","Freneuse","Gouy","Grand-Couronne",
    "Hautot-sur-Seine","Hénouville","Houppeville","Isneauville","Jumièges",
    "La Bouille","La Londe","La Neuville-Chant-d'Oisel","Le Grand-Quevilly",
    "Le Houlme","Le Mesnil-Esnard","Le Mesnil-sous-Jumièges","Le Petit-Quevilly",
    "Le Trait","Les Authieux-sur-le-Port-Saint-Ouen","Malaunay","Maromme",
    "Mont-Saint-Aignan","Montmain","Moulineaux","Notre-Dame-de-Bondeville",
    "Oissel-sur-Seine","Orival","Petit-Couronne","Quevillon",
    "Quévreville-la-Poterie","Roncherolles-sur-le-Vivier","Rouen","Sahurs",
    "Saint-Aubin-Celloville","Saint-Aubin-Épinay","Saint-Aubin-lès-Elbeuf",
    "Saint-Étienne-du-Rouvray","Saint-Jacques-sur-Darnétal",
    "Saint-Léger-du-Bourg-Denis","Saint-Martin-de-Boscherville",
    "Saint-Martin-du-Vivier","Saint-Paër","Saint-Pierre-de-Manneville",
    "Saint-Pierre-de-Varengeville","Saint-Pierre-lès-Elbeuf",
    "Sainte-Marguerite-sur-Duclair","Sotteville-lès-Rouen",
    "Sotteville-sous-le-Val","Tourville-la-Rivière","Val-de-la-Haye",
    "Yainville","Ymare","Yville-sur-Seine",
]
COMMUNES_SAINT_ETIENNE = [
    "Aboën","Andrézieux-Bouthéon","Caloire","Cellieu","Chagnon","Chambœuf",
    "Châteauneuf","Dargoire","Doizieux","Farnay","Firminy","Fontanès",
    "Fraisses","Genilac","L'Étrat","L'Horme","La Fouillouse","La Gimond",
    "La Grand-Croix","La Ricamarie","La Talaudière","La Terrasse-sur-Dorlay",
    "La Tour-en-Jarez","La Valla-en-Gier","Le Chambon-Feugerolles","Lorette",
    "Marcenod","Pavezin","Rive-de-Gier","Roche-la-Molière",
    "Rozier-Côtes-d'Aurec","Saint-Bonnet-les-Oules","Saint-Chamond",
    "Saint-Christo-en-Jarez","Saint-Étienne","Saint-Galmier",
    "Saint-Genest-Lerpt","Saint-Héand","Saint-Jean-Bonnefonds","Saint-Joseph",
    "Saint-Martin-la-Plaine","Saint-Maurice-en-Gourgois","Saint-Nizier-de-Fornas",
    "Saint-Paul-en-Cornillon","Saint-Paul-en-Jarez","Saint-Priest-en-Jarez",
    "Saint-Romain-en-Jarez","Sainte-Croix-en-Jarez","Sorbiers","Tartaras",
    "Unieux","Valfleury","Villars",
]
COMMUNES_MONTPELLIER = [
    "Baillargues","Beaulieu","Castelnau-le-Lez","Castries","Clapiers",
    "Cournonsec","Cournonterral","Fabrègues","Grabels","Jacou","Juvignac",
    "Lattes","Lavérune","Le Crès","Montaud","Montferrier-sur-Lez",
    "Montpellier","Murviel-lès-Montpellier","Pérols","Pignan","Prades-le-Lez",
    "Restinclières","Saint-Brès","Saint-Drézéry","Saint-Geniès-des-Mourgues",
    "Saint-Georges-d'Orques","Saint-Jean-de-Védas","Saussan","Sussargues",
    "Vendargues","Villeneuve-lès-Maguelone",
]

COMMUNES_METROPOLES = set(
    COMMUNES_GRENOBLE + COMMUNES_RENNES + COMMUNES_ROUEN
    + COMMUNES_SAINT_ETIENNE + COMMUNES_MONTPELLIER
)


# ── FONCTIONS UTILITAIRES ─────────────────────────────────────────────────────
def get_dep(code) -> str:
    """Extrait le code département (2 caractères) de manière robuste."""
    s = str(code).strip().upper()
    if pd.isna(code) or not s:
        return "XX"
    if s.startswith("2A") or s.startswith("2B"):
        return s[:2]
    if re.match(r'^\d+$', s):
        # Prend toujours les 2 premiers chiffres pour identifier le département
        return s.zfill(5)[:2]
    return "XX"

def concatener_code_insee(code_brut) -> str:
    """
    Assure la création du code INSEE à 5 caractères par concaténation stricte :
    Département (2 caractères) + Code commune municipal (3 caractères).
    """
    s = str(code_brut).strip()
    s = s.zfill(5) # Sécurisation de la longueur minimale
    dep_code = s[:2]
    com_code = s[-3:]
    return dep_code + com_code

# ==============================================================================
# 1. MIGRATIONS RÉSIDENTIELLES
# ==============================================================================
def nettoyer_migrations(df_raw, annee: int, col_flux: str) -> pd.DataFrame:
    df = df_raw.copy()

    cols_needed = ["CODGEO", "LIBGEO", "DCRAN", "L_DCRAN", col_flux]
    manquantes = [c for c in cols_needed if c not in df.columns]
    if manquantes:
        print(f"  ⚠️  {annee} — colonnes manquantes : {manquantes}")
        return pd.DataFrame()

    # Reconstruction propre par concaténation (Dep 2 + Com 3)
    df["CODGEO"] = df["CODGEO"].apply(concatener_code_insee)
    df["DCRAN"]  = df["DCRAN"].apply(concatener_code_insee)
    
    df["LIBGEO"] = df["LIBGEO"].astype(str).str.strip()
    df["L_DCRAN"] = df["L_DCRAN"].astype(str).str.strip()

    df["dep_destination"] = df["CODGEO"].apply(get_dep)
    df["dep_origine"]     = df["DCRAN"].apply(get_dep)

    df[col_flux] = pd.to_numeric(df[col_flux], errors="coerce").fillna(0)

    # 1. Filtre géographique : On ne garde QUE la France métropolitaine (élimine "XX", "99", DOM-TOM)
    mask_metro = df["dep_destination"].isin(DEPS_FRANCE_METRO) & df["dep_origine"].isin(DEPS_FRANCE_METRO)
    
    # 2. Filtre métropoles : Au moins l'une des communes est dans l'une des 5 métropoles cibles
    mask_dest = df["LIBGEO"].isin(COMMUNES_METROPOLES) & df["dep_destination"].isin(DEPS_METROPOLES)
    mask_orig = df["L_DCRAN"].isin(COMMUNES_METROPOLES) & df["dep_origine"].isin(DEPS_METROPOLES)
    
    # Application combinée
    df = df[mask_metro & (mask_dest | mask_orig)].copy()
    df["annee"] = annee

    df = df.rename(columns={
        "DCRAN":    "code_origine",
        "L_DCRAN":  "commune_origine",
        "CODGEO":   "code_destination",
        "LIBGEO":   "commune_destination",
        col_flux:   "flux",
    })

    return df[[
        "code_origine", "commune_origine", "dep_origine",
        "code_destination", "commune_destination", "dep_destination",
        "flux", "annee",
    ]]


# ==============================================================================
# 2. MOBILITÉ PROFESSIONNELLE
# ==============================================================================
def nettoyer_mobilite_travail(df_raw, annee: int, col_flux: str) -> pd.DataFrame:
    df = df_raw.copy()

    cols_needed = ["CODGEO", "LIBGEO", "DCLT", "L_DCLT", col_flux]
    manquantes = [c for c in cols_needed if c not in df.columns]
    if manquantes:
        return pd.DataFrame()

    df["CODGEO"] = df["CODGEO"].apply(concatener_code_insee)
    df["DCLT"]   = df["DCLT"].apply(concatener_code_insee)
    df["LIBGEO"] = df["LIBGEO"].astype(str).str.strip()
    df["L_DCLT"] = df["L_DCLT"].astype(str).str.strip()

    df["dep_residence"] = df["CODGEO"].apply(get_dep)
    df["dep_travail"]   = df["DCLT"].apply(get_dep)

    df[col_flux] = pd.to_numeric(df[col_flux], errors="coerce").fillna(0)

    mask_metro = df["dep_residence"].isin(DEPS_FRANCE_METRO) & df["dep_travail"].isin(DEPS_FRANCE_METRO)
    mask_res   = df["LIBGEO"].isin(COMMUNES_METROPOLES) & df["dep_residence"].isin(DEPS_METROPOLES)
    mask_trav  = df["L_DCLT"].isin(COMMUNES_METROPOLES) & df["dep_travail"].isin(DEPS_METROPOLES)
    
    df = df[mask_metro & (mask_res | mask_trav)].copy()
    df["annee"] = annee

    df = df.rename(columns={
        "CODGEO":  "code_residence",
        "LIBGEO":  "commune_residence",
        "DCLT":    "code_travail",
        "L_DCLT":  "commune_travail",
        col_flux:  "flux",
    })

    return df[[
        "code_residence", "commune_residence", "dep_residence",
        "code_travail", "commune_travail", "dep_travail",
        "flux", "annee",
    ]]


# ==============================================================================
# 3. MOBILITÉ SCOLAIRE
# ==============================================================================
def nettoyer_mobilite_scolaire(df_raw, annee: int, col_flux: str) -> pd.DataFrame:
    df = df_raw.copy()

    cols_needed = ["CODGEO", "LIBGEO", "DCETU", "L_DCETU", col_flux]
    manquantes = [c for c in cols_needed if c not in df.columns]
    if manquantes:
        return pd.DataFrame()

    df["CODGEO"] = df["CODGEO"].apply(concatener_code_insee)
    df["DCETU"]  = df["DCETU"].apply(concatener_code_insee)
    df["LIBGEO"] = df["LIBGEO"].astype(str).str.strip()
    df["L_DCETU"] = df["L_DCETU"].astype(str).str.strip()

    df["dep_origine"]     = df["CODGEO"].apply(get_dep)
    df["dep_destination"] = df["DCETU"].apply(get_dep)

    df[col_flux] = pd.to_numeric(df[col_flux], errors="coerce").fillna(0)

    mask_metro = df["dep_origine"].isin(DEPS_FRANCE_METRO) & df["dep_destination"].isin(DEPS_FRANCE_METRO)
    mask_orig  = df["LIBGEO"].isin(COMMUNES_METROPOLES) & df["dep_origine"].isin(DEPS_METROPOLES)
    mask_dest  = df["L_DCETU"].isin(COMMUNES_METROPOLES) & df["dep_destination"].isin(DEPS_METROPOLES)
    
    df = df[mask_metro & (mask_orig | mask_dest)].copy()
    df["annee"] = annee

    df = df.rename(columns={
        "CODGEO":   "code_origine",
        "LIBGEO":   "commune_origine",
        "DCETU":    "code_destination",
        "L_DCETU":  "commune_destination",
        col_flux:   "flux",
    })

    return df[[
        "code_origine", "commune_origine", "dep_origine",
        "code_destination", "commune_destination", "dep_destination",
        "flux", "annee",
    ]]


# ==============================================================================
# EXÉCUTION & STATS 
# ==============================================================================
def log_stats(df, nom, col_orig_dep, col_dest_dep):
    if df.empty:
        print(f"  ❌ DataFrame vide pour {nom}")
        return
    print(f"\n  📊 {nom} — {len(df):,} lignes")
    for metro, dep in [("Grenoble","38"),("Montpellier","34"),
                       ("Rennes","35"),("Saint-Étienne","42"),("Rouen","76")]:
        yr = df[df["annee"] == df["annee"].max()]
        f_out = yr[(yr[col_orig_dep] == dep) & (yr[col_dest_dep] != dep)]["flux"].sum()
        f_in  = yr[(yr[col_dest_dep] == dep) & (yr[col_orig_dep] != dep)]["flux"].sum()
        f_int = yr[(yr[col_orig_dep] == dep) & (yr[col_dest_dep] == dep)]["flux"].sum()
        solde = f_in - f_out
        print(f"     {metro:<16} IN={f_in:>8,.0f}  OUT={f_out:>8,.0f}  INT={f_int:>8,.0f}  SOLDE={solde:>+9,.0f}")


if __name__ == "__main__":

    print("=" * 65)
    print(f"Lecture des données depuis : {INPUT_DIR}")
    print(f"Sauvegarde prévue dans   : {OUTPUT_DIR}")
    print("=" * 65)

    print("\n▶ MIGRATIONS RÉSIDENTIELLES")
    try:
        df_res_2019 = pd.read_csv(INPUT_DIR / "Migrations_resid_2019.csv", sep=";", low_memory=False)
        df_res_2022 = pd.read_csv(INPUT_DIR / "Migrations_resid_2022.csv", sep=";", low_memory=False)
        df_res_c19 = nettoyer_migrations(df_res_2019, 2019, "NBFLUX_C19_POP01P")
        df_res_c22 = nettoyer_migrations(df_res_2022, 2022, "NBFLUX_C22_POP01P")
        df_res_final = pd.concat([df_res_c19, df_res_c22], ignore_index=True)
        log_stats(df_res_final, "Migrations résid.", "dep_origine", "dep_destination")
        df_res_final.to_csv(OUTPUT_DIR / "Migrations_resid_clean.csv", index=False)
    except FileNotFoundError as e:
        print(f"  ❌ {e}")

    print("\n▶ MOBILITÉ PROFESSIONNELLE")
    try:
        df_prof_2019 = pd.read_csv(INPUT_DIR / "Mobilite_profess_2019.csv", sep=";", low_memory=False)
        df_prof_2022 = pd.read_csv(INPUT_DIR / "Mobilite_profess_2022.csv", sep=";", low_memory=False)
        df_prof_c19 = nettoyer_mobilite_travail(df_prof_2019, 2019, "NBFLUX_C19_ACTOCC15P")
        df_prof_c22 = nettoyer_mobilite_travail(df_prof_2022, 2022, "NBFLUX_C22_ACTOCC15P")
        df_prof_final = pd.concat([df_prof_c19, df_prof_c22], ignore_index=True)
        log_stats(df_prof_final, "Mobilité prof.", "dep_residence", "dep_travail")
        df_prof_final.to_csv(OUTPUT_DIR / "Mobilite_profess_clean.csv", index=False)
    except FileNotFoundError as e:
        print(f"  ❌ {e}")

    print("\n▶ MOBILITÉ SCOLAIRE")
    try:
        df_scol_2019 = pd.read_csv(INPUT_DIR / "Mobilite_scolaire_2019.csv", sep=";", low_memory=False)
        df_scol_2022 = pd.read_csv(INPUT_DIR / "Mobilite_scolaire_2022.csv", sep=";", low_memory=False)
        df_scol_c19 = nettoyer_mobilite_scolaire(df_scol_2019, 2019, "NBFLUX_C19_SCOL02P")
        df_scol_c22 = nettoyer_mobilite_scolaire(df_scol_2022, 2022, "NBFLUX_C22_SCOL02P")
        df_scol_final = pd.concat([df_scol_c19, df_scol_c22], ignore_index=True)
        log_stats(df_scol_final, "Mobilité scol.", "dep_origine", "dep_destination")
        df_scol_final.to_csv(OUTPUT_DIR / "Mobilite_scolaire_clean.csv", index=False)
    except FileNotFoundError as e:
        print(f"  ❌ {e}")

    print("\n" + "=" * 65)
    print("TERMINÉ. Filtre géographique métropolitain strict appliqué.")
    print("=" * 65)