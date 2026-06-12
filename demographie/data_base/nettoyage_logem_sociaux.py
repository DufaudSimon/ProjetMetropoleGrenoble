"""
Nettoyage du fichier data_RPLS2024_COM.csv (Répertoire des Logements Locatifs Sociaux)
Source : https://www.insee.fr/fr/statistiques/8736658
Niveau : COMMUNE (codes INSEE 5 caractères)

Les communes absentes du fichier n'ont simplement pas de parc social recensé,
ce qui est normal pour les petites communes périurbaines ou rurales.

Résultat : rpls_metropoles_clean.csv
"""

import pandas as pd
import os

# ─────────────────────────────────────────────────────────────────
# 1. PARAMÈTRES
# ─────────────────────────────────────────────────────────────────

METRO_DEP = {
    "Grenoble":      ["38"],
    "Rennes":        ["35"],
    "Rouen":         ["76"],
    "Saint-Etienne": ["42"],
    "Montpellier":   ["34"],
}

COMMUNES_NOMS = {
    "Grenoble": [
        "Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix",
        "Corenc","Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon",
        "Gières","Grenoble","Herbeys","Jarrie","La Tronche","Le Gua",
        "Le Pont-de-Claix","Le Sappey-en-Chartreuse","Meylan","Miribel-Lanchâtre",
        "Mont-Saint-Martin","Montchaboud","Murianette","Notre-Dame-de-Commiers",
        "Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux",
        "Quaix-en-Chartreuse","Saint-Barthélemy-de-Séchilienne","Saint-Égrève",
        "Saint-Georges-de-Commiers","Saint-Martin-d'Hères","Saint-Martin-le-Vinoux",
        "Saint-Paul-de-Varces","Saint-Pierre-de-Mésage","Sarcenas","Sassenage",
        "Séchilienne","Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset",
        "Vaulnaveys-le-Bas","Vaulnaveys-le-Haut","Venon","Veurey-Voroize","Vif","Vizille",
    ],
    "Rennes": [
        "Acigné","Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné",
        "Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds",
        "Gévezé","La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage",
        "Le Rheu","Le Verger","Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche",
        "Nouvoitou","Orgères","Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes",
        "Romillé","Saint-Armel","Saint-Erblon","Saint-Gilles","Saint-Grégoire",
        "Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt","Thorigné-Fouillard",
        "Vern-sur-Seiche","Vezin-le-Coquet","Clayes","La Chapelle-Chaussée",
        "Laillé","Langan","Miniac-sous-Bécherel",
    ],
    "Rouen": [
        "Amfreville-la-Mi-Voie","Anneville-Ambourville","Bardouville","Belbeuf",
        "Berville-sur-Seine","Bihorel","Bois-Guillaume","Bonsecours","Boos","Canteleu",
        "Caudebec-lès-Elbeuf","Cléon","Darnétal","Déville-lès-Rouen","Duclair","Elbeuf",
        "Épinay-sur-Duclair","Fontaine-sous-Préaux","Franqueville-Saint-Pierre","Freneuse",
        "Gouy","Grand-Couronne","Hautot-sur-Seine","Hénouville","Houppeville","Isneauville",
        "Jumièges","La Bouille","La Londe","La Neuville-Chant-d'Oisel","Le Grand-Quevilly",
        "Le Houlme","Le Mesnil-Esnard","Le Mesnil-sous-Jumièges","Le Petit-Quevilly",
        "Le Trait","Les Authieux-sur-le-Port-Saint-Ouen","Malaunay","Maromme",
        "Mont-Saint-Aignan","Montmain","Moulineaux","Notre-Dame-de-Bondeville","Oissel",
        "Orival","Petit-Couronne","Quevillon","Quévreville-la-Poterie",
        "Roncherolles-sur-le-Vivier","Rouen","Sahurs","Saint-Aubin-Celloville",
        "Saint-Aubin-Épinay","Saint-Aubin-lès-Elbeuf","Saint-Étienne-du-Rouvray",
        "Saint-Jacques-sur-Darnétal","Saint-Léger-du-Bourg-Denis",
        "Saint-Martin-de-Boscherville","Saint-Martin-du-Vivier","Saint-Paër",
        "Saint-Pierre-de-Manneville","Saint-Pierre-de-Varengeville",
        "Saint-Pierre-lès-Elbeuf","Sainte-Marguerite-sur-Duclair","Sotteville-lès-Rouen",
        "Sotteville-sous-le-Val","Tourville-la-Rivière","Val-de-la-Haye","Yainville",
        "Ymare","Yville-sur-Seine",
    ],
    "Saint-Etienne": [
        "Aboën","Andrézieux-Bouthéon","Caloire","Cellieu","Chagnon","Chambœuf",
        "Châteauneuf","Dargoire","Doizieux","Farnay","Firminy","Fontanès","Fraisses",
        "Genilac","L'Étrat","L'Horme","La Fouillouse","La Gimond","La Grand-Croix",
        "La Ricamarie","La Talaudière","La Terrasse-sur-Dorlay","La Tour-en-Jarez",
        "La Valla-en-Gier","Le Chambon-Feugerolles","Lorette","Marcenod","Pavezin",
        "Rive-de-Gier","Roche-la-Molière","Rozier-Côtes-d'Aurec","Saint-Bonnet-les-Oules",
        "Saint-Chamond","Saint-Christo-en-Jarez","Saint-Étienne","Saint-Galmier",
        "Saint-Genest-Lerpt","Saint-Héand","Saint-Jean-Bonnefonds","Saint-Joseph",
        "Saint-Martin-la-Plaine","Saint-Maurice-en-Gourgois","Saint-Nizier-de-Fornas",
        "Saint-Paul-en-Cornillon","Saint-Paul-en-Jarez","Saint-Priest-en-Jarez",
        "Saint-Romain-en-Jarez","Sainte-Croix-en-Jarez","Sorbiers","Tartaras",
        "Unieux","Valfleury","Villars",
    ],
    "Montpellier": [
        "Baillargues","Beaulieu","Castelnau-le-Lez","Castries","Clapiers","Cournonsec",
        "Cournonterral","Fabrègues","Grabels","Jacou","Juvignac","Lattes","Lavérune",
        "Le Crès","Montaud","Montferrier-sur-Lez","Montpellier","Murviel-lès-Montpellier",
        "Pérols","Pignan","Prades-le-Lez","Restinclières","Saint-Brès","Saint-Drézéry",
        "Saint-Geniès-des-Mourgues","Saint-Georges-d'Orques","Saint-Jean-de-Védas",
        "Saussan","Sussargues","Vendargues","Villeneuve-lès-Maguelone",
    ],
}

# Correspondance des colonnes RPLS → noms lisibles
COLS_RPLS = {
    "CodGeo":       "code_commune",
    "Note":         "note_secret",          # 0 = données publiées, 1 = secret stat
    "nbLsPls":      "nb_logements_sociaux",  # Nb total de logements locatifs sociaux
    "nbLsMes":      "nb_logements_mesures",  # Nb de logements avec mesures de perf. énergétique
    "txVac":        "taux_vacance",          # Taux de vacance (%)
    "txVac3m":      "taux_vacance_3mois",    # Taux de vacance > 3 mois (%)
    "txRot":        "taux_rotation",         # Taux de rotation annuel (%)
    "txLsCol":      "part_collectif",        # Part logements collectifs (%)
    "txLsInd":      "part_individuel",       # Part logements individuels (%)
    "txLs1p":       "part_T1",              # Part T1 (%)
    "txLs2p":       "part_T2",              # Part T2 (%)
    "txLs3p":       "part_T3",              # Part T3 (%)
    "txLs4p":       "part_T4",              # Part T4 (%)
    "txLs5pp":      "part_T5plus",          # Part T5+ (%)
    "txLsm30":      "part_surf_inf30",       # Part < 30 m² (%)
    "txLs30a40":    "part_surf_30_40",       # Part 30–40 m² (%)
    "txLs40a60":    "part_surf_40_60",       # Part 40–60 m² (%)
    "txLs60a80":    "part_surf_60_80",       # Part 60–80 m² (%)
    "txLs80a100":   "part_surf_80_100",      # Part 80–100 m² (%)
    "txLs100a120":  "part_surf_100_120",     # Part 100–120 m² (%)
    "txLs120p":     "part_surf_sup120",      # Part > 120 m² (%)
    "txLsAv49":     "part_avant_1949",       # Part construits avant 1949 (%)
    "txLs49a75":    "part_1949_1975",        # Part 1949–1975 (%)
    "txLs76a88":    "part_1976_1988",        # Part 1976–1988 (%)
    "txLs89a00":    "part_1989_2000",        # Part 1989–2000 (%)
    "txLs01a13":    "part_2001_2013",        # Part 2001–2013 (%)
    "txLsAp13":     "part_apres_2013",       # Part après 2013 (%)
    "txLsPlai":     "part_PLAI",            # Part PLAI (%)
    "txLsPlusAv77": "part_HLM_avant_1977",   # Part HLM avant 1977 (%)
    "txLsPlusAp77": "part_HLM_apres_1977",   # Part HLM après 1977 (%)
    "txLsPls":      "part_PLS",             # Part PLS (%)
    "txLsPli":      "part_PLI",             # Part PLI (%)
    "moyLoy":       "loyer_moyen",           # Loyer moyen (€/m²)
    "q1Loy":        "loyer_q1",             # 1er quartile loyer (€/m²)
    "medLoy":       "loyer_median",          # Loyer médian (€/m²)
    "q3Loy":        "loyer_q3",             # 3e quartile loyer (€/m²)
}

# ─────────────────────────────────────────────────────────────────
# 2. CHARGEMENT
# ─────────────────────────────────────────────────────────────────
print("Chargement des fichiers…")
script_dir = os.path.dirname(os.path.abspath(__file__))
cog  = pd.read_csv("v_commune_2023.csv",       sep=",", dtype=str)
rpls = pd.read_csv("data_RPLS2024_COM.csv",    sep=";", dtype=str)

cog["COM"]    = cog["COM"].str.zfill(5)
rpls["CodGeo"] = rpls["CodGeo"].str.zfill(5)

print(f"  → RPLS : {len(rpls):,} communes au niveau national")

# ─────────────────────────────────────────────────────────────────
# 3. RÉSOLUTION NOM → CODE COG (filtrée par département)
# ─────────────────────────────────────────────────────────────────
print("Résolution des noms vers codes COG…")

ref_rows, warnings = [], []
for metro, noms in COMMUNES_NOMS.items():
    cog_m = cog[cog["DEP"].isin(METRO_DEP[metro])]
    for nom in noms:
        m = cog_m[cog_m["LIBELLE"].str.lower() == nom.lower()]
        if len(m) == 0:
            m = cog_m[cog_m["NCC"].str.lower() == nom.upper().lower()]
            if len(m) >= 1:
                warnings.append(f"[{metro}] '{nom}' résolu via NCC → {m.iloc[0]['COM']}")
        if len(m) == 0:
            warnings.append(f"[{metro}] ⚠ INTROUVABLE dans COG : '{nom}'")
        else:
            ref_rows.append({
                "metropole":    metro,
                "nom_commune":  nom,
                "code_commune": m.iloc[0]["COM"],
            })

df_ref       = pd.DataFrame(ref_rows)
target_codes = set(df_ref["code_commune"])

# ─────────────────────────────────────────────────────────────────
# 4. FILTRAGE + ENRICHISSEMENT
# ─────────────────────────────────────────────────────────────────
df_filtre = rpls[rpls["CodGeo"].isin(target_codes)].copy()
df_filtre = df_filtre.merge(df_ref, left_on="CodGeo", right_on="code_commune", how="left")

# Suppression de la colonne code_commune dupliquée issue du merge
df_filtre = df_filtre.drop(columns=["code_commune"], errors="ignore")
df_filtre = df_filtre.rename(columns={"CodGeo": "code_commune"})

# ─────────────────────────────────────────────────────────────────
# 5. CONVERSION DES VIRGULES EN POINTS (format numérique français)
# ─────────────────────────────────────────────────────────────────
cols_numeriques = [c for c in rpls.columns if c not in ("CodGeo", "Note")]
for col in cols_numeriques:
    if col in df_filtre.columns:
        df_filtre[col] = (
            df_filtre[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .replace("nan", pd.NA)
        )
        df_filtre[col] = pd.to_numeric(df_filtre[col], errors="coerce")

# ─────────────────────────────────────────────────────────────────
# 6. RENOMMAGE DES COLONNES
# ─────────────────────────────────────────────────────────────────
rename_map = {old: new for old, new in COLS_RPLS.items()
              if old in df_filtre.columns and old != "CodGeo"}
df_filtre = df_filtre.rename(columns=rename_map)

# Ordre : identifiants en tête, puis métriques
id_cols   = ["metropole", "code_commune", "nom_commune", "note_secret"]
data_cols = [c for c in df_filtre.columns if c not in id_cols]
df_filtre = df_filtre[[c for c in id_cols if c in df_filtre.columns] + data_cols]

# ─────────────────────────────────────────────────────────────────
# 7. RAPPORT
# ─────────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════════════════════")
print("RAPPORT FINAL")
print("══════════════════════════════════════════════════════════")
print(f"{'Métropole':<22} {'COG':>8} {'RPLS':>8} {'Absentes (pas de parc social)'}")
print("-" * 90)

for metro in COMMUNES_NOMS:
    att       = len(COMMUNES_NOMS[metro])
    ref_n     = int(df_ref[df_ref["metropole"] == metro]["code_commune"].nunique())
    dans_rpls = int(df_filtre[df_filtre["metropole"] == metro]["code_commune"].nunique())
    absents   = df_ref[
        (df_ref["metropole"] == metro) &
        (~df_ref["code_commune"].isin(df_filtre["code_commune"]))
    ]["nom_commune"].tolist()
    statut = "✓" if dans_rpls > 0 else "⚠"
    print(f"  {statut} {metro:<20} {ref_n:>3}/{att:<3}   {dans_rpls:>3}/{att:<3}   "
          f"{len(absents)} communes sans parc social")
    if absents:
        # Affiche par groupes de 5 pour lisibilité
        for i in range(0, len(absents), 5):
            prefix = "      → " if i == 0 else "        "
            print(prefix + ", ".join(absents[i:i+5]))

total_att  = sum(len(v) for v in COMMUNES_NOMS.values())
total_rpls = int(df_filtre["code_commune"].nunique())
print("-" * 90)
print(f"  TOTAL : {total_rpls}/{total_att} communes avec parc social | {len(df_filtre)} lignes")
print(f"  Colonnes : {df_filtre.shape[1]} ({df_filtre.columns.tolist()[:5]} …)")

if warnings:
    print("\nAVERTISSEMENTS COG :")
    for w in warnings:
        print(f"  {w}")

# ─────────────────────────────────────────────────────────────────
# 8. SAUVEGARDE
# ─────────────────────────────────────────────────────────────────
# script_dir est actuellement : .../demographie/data_base
# On remonte d'un niveau pour arriver dans : .../demographie
dossier_parent = os.path.dirname(script_dir)

# On définit le nouveau dossier cible : .../demographie/data_clean/logement
dossier_cible = os.path.join(dossier_parent, "data_clean", "logement")

# CRUCIAL : On force la création du dossier (et de ses sous-dossiers) s'ils n'existent pas
os.makedirs(dossier_cible, exist_ok=True)

# On assemble le chemin final avec le nom du fichier
out = os.path.join(dossier_cible, "rpls_metropoles_clean.csv")

# Sauvegarde
df_filtre.to_csv(out, index=False, encoding="utf-8-sig")

print(f"\n  Fichier sauvegardé avec succès dans :\n  {out}")
print("══════════════════════════════════════════════")