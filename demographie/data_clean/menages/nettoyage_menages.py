import pandas as pd

## -------------------------- Fichier Mobilite_profess.csv --------------------------------------
# 1. CHARGER LE FICHIER ORIGINAL
df_raw = pd.read_csv(
    "demographie/data_base/Mobilite_profess.csv",
    sep=";",
    low_memory=False
)

# 2. COMMUNES À GARDER (Grenoble + Rennes)
communes_grenoble = [
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
    "Vif","Vizille"
]

communes_rennes = [
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
    "Laillé","Langan","Miniac-sous-Bécherel"
]

communes_a_garder = communes_grenoble + communes_rennes

# 3. FILTRE COMMUNES + DÉPARTEMENTS
df = df_raw.copy()

df = df[df["LIBGEO"].isin(communes_a_garder)]
df = df[df["CODGEO"].astype(str).str[:2].isin(["35", "38"])]

# 4. NETTOYAGE NUMÉRIQUE
df["NBFLUX_C22_ACTOCC15P"] = (
    df["NBFLUX_C22_ACTOCC15P"]
    .fillna(0)
    .astype(float)
    .round(2)
)

# 5. STRUCTURE DE SORTIE
cols_finales = [
    "CODGEO",
    "LIBGEO",
    "DCLT",
    "L_DCLT",
    "NBFLUX_C22_ACTOCC15P"
]

df_final = df[cols_finales].copy()

# 6. RENOMMAGE DES COLONNES (LISIBLE)
df_final = df_final.rename(columns={
    "CODGEO": "Code_commune_residence",
    "LIBGEO": "Commune_residence",
    "DCLT": "Code_lieu_travail",
    "L_DCLT": "Lieu_travail",
    "NBFLUX_C22_ACTOCC15P": "Actifs_occupes_flux_domicile_travail"
})

# 7. SAUVEGARDE
df_final.to_csv(
    "demographie/data_clean/menages/Mobilite_professionnelle.csv",
    index=False
)

## -------------------------- Fichier Mobilite_scolaire.csv --------------------------------------
# 1. CHARGER LE FICHIER ORIGINAL
df_raw = pd.read_csv(
    "demographie/data_base/Mobilite_scolaire.csv",
    sep=";",
    low_memory=False
)

# 2. COMMUNES À GARDER (Grenoble + Rennes)
communes_grenoble = [
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
    "Vif","Vizille"
]

communes_rennes = [
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
    "Laillé","Langan","Miniac-sous-Bécherel"
]

communes_a_garder = communes_grenoble + communes_rennes

# 3. FILTRE COMMUNES + DÉPARTEMENTS
df = df_raw.copy()

df = df[df["LIBGEO"].isin(communes_a_garder)]
df = df[df["CODGEO"].astype(str).str[:2].isin(["35", "38"])]

# 4. NETTOYAGE NUMÉRIQUE
df["NBFLUX_C22_SCOL02P"] = (
    df["NBFLUX_C22_SCOL02P"]
    .fillna(0)
    .astype(float)
    .round(2)
)

# 5. STRUCTURE DE SORTIE
cols_finales = [
    "CODGEO",
    "LIBGEO",
    "DCETU",
    "L_DCETU",
    "NBFLUX_C22_SCOL02P"
]

df_final = df[cols_finales].copy()

# 6. RENOMMAGE DES COLONNES (LISIBLE)
df_final = df_final.rename(columns={
    "CODGEO": "Code_commune_residence",
    "LIBGEO": "Commune_residence",
    "DCETU": "Code_lieu_etudes",
    "L_DCETU": "Lieu_etudes",
    "NBFLUX_C22_SCOL02P": "Eleves_etudiants_flux_domicile_etudes"
})

# 7. SAUVEGARDE
df_final.to_csv(
    "demographie/data_clean/menages/Mobilite_scolaire.csv",
    index=False
)

## -------------------------- Fichier Mobilite_migration.csv --------------------------------------

# 1. CHARGER LE FICHIER ORIGINAL
df_raw = pd.read_csv(
    "demographie/data_base/Migrations_resid.csv",
    sep=";",
    low_memory=False
)

# 2. COMMUNES À GARDER (Grenoble + Rennes)
communes_grenoble = [
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
    "Vif","Vizille"
]

communes_rennes = [
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
    "Laillé","Langan","Miniac-sous-Bécherel"
]

communes_a_garder = communes_grenoble + communes_rennes

# 3. FILTRE SUR COMMUNES DE RÉSIDENCE
df = df_raw.copy()

df = df[df["LIBGEO"].isin(communes_a_garder)]
df = df[df["CODGEO"].astype(str).str[:2].isin(["35", "38"])]

# 4. NETTOYAGE NUMÉRIQUE (arrondi à 2 décimales)
df["NBFLUX_C22_POP01P"] = (
    df["NBFLUX_C22_POP01P"]
    .fillna(0)
    .astype(float)
    .round(2)
)

# 5. STRUCTURE DE SORTIE
cols_finales = [
    "CODGEO",
    "LIBGEO",
    "DCRAN",
    "L_DCRAN",
    "NBFLUX_C22_POP01P"
]

df_final = df[cols_finales].copy()

# 6. RENOMMAGE DES COLONNES
df_final = df_final.rename(columns={
    "CODGEO": "Code_commune_arrivee",
    "LIBGEO": "Commune_arrivee",
    "DCRAN": "Code_commune_depart",
    "L_DCRAN": "Commune_depart",
    "NBFLUX_C22_POP01P": "Flux_migrants_1an_ou_plus"
})

# 7. SAUVEGARDE
df_final.to_csv(
    "demographie/data_clean/menages/Migration_residentielle.csv",
    index=False
)

