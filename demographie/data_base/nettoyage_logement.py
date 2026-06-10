"""
Nettoyage du fichier Logement.csv (INSEE RP - DS_RP_LOGEMENT_COMPL)
Résultat : logements_metropoles_clean.csv
  - 247 communes des 5 métropoles uniquement
  - lignes de niveau commune uniquement (GEO_OBJECT = COM)
  - colonnes : metropole, code_commune, nom_commune, annee,
               indicateur_occupation, valeur
"""

import pandas as pd
import os

# 1. PARAMÈTRES
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

# 2. CHARGEMENT
print("Chargement des fichiers…")
# Utilisation de os.path pour garantir que le script trouve les fichiers quel que soit l'endroit d'où on le lance
script_dir = os.path.dirname(os.path.abspath(__file__))
cog = pd.read_csv(os.path.join(script_dir, "v_commune_2023.csv"), sep=",", dtype=str)
df  = pd.read_csv(os.path.join(script_dir, "Logement.csv"),       sep=";", dtype={"GEO": str})

cog["COM"] = cog["COM"].str.zfill(5)
df["GEO"]  = df["GEO"].str.zfill(5)

# Uniquement les lignes de niveau commune
df = df[df["GEO_OBJECT"] == "COM"].copy()
print(f"  → {len(df):,} lignes de niveau commune dans Logement.csv")

# 3. RÉSOLUTION NOM → CODE COG (filtrée par département)
print("\nRésolution des noms vers codes COG…")

ref_rows = []
warnings  = []

for metro, noms in COMMUNES_NOMS.items():
    deps      = METRO_DEP[metro]
    cog_metro = cog[cog["DEP"].isin(deps)]

    for nom in noms:
        match = cog_metro[cog_metro["LIBELLE"].str.lower() == nom.lower()]

        if len(match) == 0:
            match = cog_metro[cog_metro["NCC"].str.lower() == nom.upper().lower()]
            if len(match) >= 1:
                warnings.append(f"[{metro}] '{nom}' trouvé via NCC → code {match.iloc[0]['COM']}")

        if len(match) == 0:
            warnings.append(f"[{metro}] ⚠ INTROUVABLE dans COG : '{nom}'")
        else:
            if len(match) > 1:
                warnings.append(f"[{metro}] '{nom}' → {len(match)} résultats, premier retenu ({match.iloc[0]['COM']})")
            ref_rows.append({
                "metropole":    metro,
                "nom_commune":  nom,
                "code_commune": match.iloc[0]["COM"],
            })

df_ref = pd.DataFrame(ref_rows)

# 4. FILTRAGE + ENRICHISSEMENT
target_codes = set(df_ref["code_commune"])
df_filtre    = df[df["GEO"].isin(target_codes)].copy()

# Jointure (inner join pour ne garder que les correspondances)
df_filtre = df_filtre.merge(
    df_ref,
    left_on="GEO",
    right_on="code_commune",
    how="inner"
)

# 5. NETTOYAGE FINAL DES COLONNES
# ATTENTION: On NE renomme PAS "GEO" en "code_commune" ici, car la jointure a déjà apporté "code_commune" !
# Cela évite le bug des colonnes en double.

# Renommer les colonnes métier
df_filtre = df_filtre.rename(columns={
    "OCC_IND":     "indicateur_occupation",
    "TIME_PERIOD": "annee",
    "OBS_VALUE":   "valeur",
})

# Ordre final (cette opération supprime automatiquement l'ancienne colonne GEO et les inutiles)
cols_order = ["metropole", "code_commune", "nom_commune",
              "annee", "indicateur_occupation", "valeur"]
df_filtre  = df_filtre[[c for c in cols_order if c in df_filtre.columns]]

# ─────────────────────────────────────────────────────────────────
# 6. RAPPORT
# ─────────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════════")
print("RAPPORT FINAL")
print("══════════════════════════════════════════════")

for metro in COMMUNES_NOMS:
    attendu = len(COMMUNES_NOMS[metro])
    
    # Extraction propre
    subset_df = df_filtre[df_filtre["metropole"] == metro]
    
    # Le nuique() refonctionne normalement car il n'y a plus de conflit de colonnes
    n_communes_log = subset_df["code_commune"].nunique()
    n_lignes = len(subset_df)
    
    ref_subset = df_ref[df_ref["metropole"] == metro]
    ref_n = ref_subset["code_commune"].nunique()
    
    statut = "✓" if n_communes_log == attendu else "⚠"
    
    print(f"   {statut} {metro:20s} | COG {ref_n:3}/{attendu} "
          f"| Logement {n_communes_log:3}/{attendu} | {n_lignes:5,} lignes")

# ─────────────────────────────────────────────────────────────────
# 7. SAUVEGARDE
# ─────────────────────────────────────────────────────────────────
# script_dir est actuellement : .../demographie/data_base
# On remonte d'un niveau pour arriver dans : .../demographie
dossier_parent = os.path.dirname(script_dir)

# On définit le nouveau dossier cible : .../demographie/data_clean/logement
dossier_cible = os.path.join(dossier_parent, "data_clean", "logement")

# CRUCIAL : On force la création du dossier (et de ses sous-dossiers) s'ils n'existent pas
os.makedirs(dossier_cible, exist_ok=True)

# On assemble le chemin final avec le nom du fichier
out = os.path.join(dossier_cible, "logements_metropoles_clean.csv")

# Sauvegarde
df_filtre.to_csv(out, index=False, encoding="utf-8-sig")

print(f"\n  Fichier sauvegardé avec succès dans :\n  {out}")
print("══════════════════════════════════════════════")