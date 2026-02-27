## -------------------------- Fichier Donnees_generales_comparatives -------------------------------

import pandas as pd

df = pd.read_csv(
    "Donnees_generales_comparatives.csv",
    sep=";",
    header=None,
    dtype=str
)

df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Trouver la ligne avec le plus de valeurs non nulles → ligne des territoires
header_row = df.notna().sum(axis=1).idxmax()
header = df.iloc[header_row].astype(str)

data = df.iloc[header_row + 1:].copy()
data.columns = header

# Supprimer lignes vides ou titres
data = data[data.iloc[:, 1:].notna().any(axis=1)]

# Rendre les noms de colonnes uniques (version propre)
data.columns = pd.Index(data.columns).map(str)
data = data.loc[:, ~data.columns.duplicated()]

# Renommer première colonne
data = data.rename(columns={data.columns[0]: "indicateur"})

# Melt
long = pd.melt(
    data,
    id_vars="indicateur",
    var_name="territoire",
    value_name="valeur"
)

# Pivot
wide = (
    long
    .pivot(index="territoire", columns="indicateur", values="valeur")
    .reset_index()
)

wide = wide.rename(columns={

    "Densité de la population (nombre d'habitants au km²) en 2022": "densite_2022",
    "Décès domiciliés en 2024": "deces_2024",
    "Emploi total (salarié et non salarié) au lieu de travail en 2022": "emploi_total_2022",
    "Médiane du revenu disponible par unité de consommation en 2021, en euros": "revenu_median_2021",
    "Naissances domiciliées en 2024": "naissances_2024",
    "Nombre d'établissements fin 2023": "nb_etab_2023",
    "Nombre de ménages en 2022": "nb_menages_2022",
    "Nombre de ménages fiscaux en 2021": "nb_menages_fiscaux_2021",
    "Nombre total de logements en 2022": "nb_logements_2022",

    "Part de l'administration publique, enseignement, santé et action sociale, en %": "part_admin",
    "Part de l'agriculture, sylviculture et pêche, en %": "part_agri",
    "Part de l'industrie, en %": "part_industrie",
    "Part de la construction, en %": "part_construction",
    "Part des logements vacants en 2022, en %": "part_logements_vacants",
    "Part des ménages fiscaux imposés en 2021, en %": "part_menages_imposes",
    "Part des ménages propriétaires de leur résidence principale en 2022, en %": "part_proprietaires",
    "Part des résidences principales en 2022, en %": "part_res_principales",
    "Part des résidences secondaires (y compris les logements occasionnels) en 2022, en %": "part_res_secondaires",
    "Part des établissements de 1 à 9 salariés, en %": "part_etab_1_9",
    "Part des établissements de 10 salariés ou plus, en %": "part_etab_10_plus",
    "Part du commerce, transports et services divers, en %": "part_commerce",

    "Population en 2022": "population_2022",
    "Revenus": "revenus",
    "Superficie en 2022, en km²": "superficie_km2_2022",
    "Taux d'activité des 15 à 64 ans en 2022": "tx_activite_15_64",
    "Taux de chômage des 15 à 64 ans en 2022": "tx_chomage_15_64",
    "Taux de pauvreté en 2021, en %": "tx_pauvrete_2021",
    "Variation de l'emploi total au lieu de travail : taux annuel moyen entre 2016 et 2022, en %": "tx_var_emploi_2016_2022",
    "Variation de la population : taux annuel moyen entre 2016 et 2022, en %": "tx_var_population_2016_2022",
    "dont part de l'emploi salarié au lieu de travail en 2022, en %": "part_emploi_salarie",
    "dont variation due au solde apparent des entrées sorties : taux annuel moyen entre 2016 et 2022, en %": "tx_solde_migratoire",
    "dont variation due au solde naturel : taux annuel moyen entre 2016 et 2022, en %": "tx_solde_naturel",

})

# Nettoyage territoires
wide["territoire"] = wide["territoire"].astype(str).str.strip()

# Conversion numérique
for col in wide.columns:
    if col != "territoire":
        wide[col] = pd.to_numeric(
            wide[col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce"
        )

wide.to_csv("Donnees_clean/Donnees_generales_comparatives_clean.csv", index=False)



## -------------------------- Fichier Population_tranche_age --------------------------------------
import pandas as pd
import os

# 1. CRÉER DOSSIER + CHARGER EXCEL ORIGINAL
df_2016_raw = pd.read_excel("Population_tranche_age.xlsx", 
                           sheet_name="COM_2016", 
                           skiprows=13)

df_2022_raw = pd.read_excel("Population_tranche_age.xlsx", 
                           sheet_name="COM_2022", 
                           skiprows=13)


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
    "Acigné", "Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné",
    "Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé",
    "La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger",
    "Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères",
    "Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel","Saint-Erblon",
    "Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt",
    "Thorigné-Fouillard","Vern-sur-Seiche","Vezin-le-Coquet", "Clayes", "La Chapelle-Chaussée", 
    "Laillé", "Langan", "Miniac-sous-Bécherel"
]

communes_a_garder = communes_grenoble + communes_rennes

# 3. FILTRE COMMUNES + DR (35/38)
df_2016 = df_2016_raw[
    (df_2016_raw['LIBELLE'].isin(communes_a_garder)) & 
    (df_2016_raw['DR24'].isin(['35', '38']))
].copy()

df_2022 = df_2022_raw[
    (df_2022_raw['LIBELLE'].isin(communes_a_garder)) & 
    (df_2022_raw['DR24'].isin(['35', '38']))
].copy()

# 4. AJOUTER ANNÉE + ARRONDIR POPULATION
df_2016['annee'] = 2016
df_2022['annee'] = 2022

# Détecter colonnes population (toutes celles avec 'ageq_rec')
cols_pop_2016 = [col for col in df_2016.columns if 'ageq_rec' in col]
cols_pop_2022 = [col for col in df_2022.columns if 'ageq_rec' in col]

# Arrondir vers entier le plus proche
df_2016[cols_pop_2016] = df_2016[cols_pop_2016].round(0).astype(int)
df_2022[cols_pop_2022] = df_2022[cols_pop_2022].round(0).astype(int)

# 5. RENUMEROTER COLONNES 2022 → MÊMES NOMS QUE 2016
rename_dict = {col2022: col2022.replace('2022', '2016') for col2022 in cols_pop_2022}
df_2022 = df_2022.rename(columns=rename_dict)

# Garder même structure : base + population 2016 + année
cols_base = ['RR', 'DR', 'CR', 'STABLE', 'DR24', 'LIBELLE']
cols_finales = cols_base + cols_pop_2016 + ['annee']

df_2016_final = df_2016[cols_finales]
df_2022_final = df_2022[cols_finales]

# 6. RENOMMER COLONNES POUR L'ANAL YSE
rename_dict_final = {
    # 0-4 ans
    'ageq_rec01s1rpop2016': 'Pop_0_4_ans_H',
    'ageq_rec01s2rpop2016': 'Pop_0_4_ans_F',
    
    # 5-9 ans
    'ageq_rec02s1rpop2016': 'Pop_5_9_ans_H',
    'ageq_rec02s2rpop2016': 'Pop_5_9_ans_F',
    
    # 10-14 ans
    'ageq_rec03s1rpop2016': 'Pop_10_14_ans_H',
    'ageq_rec03s2rpop2016': 'Pop_10_14_ans_F',
    
    # 15-19 ans
    'ageq_rec04s1rpop2016': 'Pop_15_19_ans_H',
    'ageq_rec04s2rpop2016': 'Pop_15_19_ans_F',
    
    # 20-24 ans
    'ageq_rec05s1rpop2016': 'Pop_20_24_ans_H',
    'ageq_rec05s2rpop2016': 'Pop_20_24_ans_F',
    
    # 25-29 ans
    'ageq_rec06s1rpop2016': 'Pop_25_29_ans_H',
    'ageq_rec06s2rpop2016': 'Pop_25_29_ans_F',
    
    # 30-34 ans
    'ageq_rec07s1rpop2016': 'Pop_30_34_ans_H',
    'ageq_rec07s2rpop2016': 'Pop_30_34_ans_F',
    
    # 35-39 ans
    'ageq_rec08s1rpop2016': 'Pop_35_39_ans_H',
    'ageq_rec08s2rpop2016': 'Pop_35_39_ans_F',
    
    # 40-44 ans
    'ageq_rec09s1rpop2016': 'Pop_40_44_ans_H',
    'ageq_rec09s2rpop2016': 'Pop_40_44_ans_F',
    
    # 45-49 ans
    'ageq_rec10s1rpop2016': 'Pop_45_49_ans_H',
    'ageq_rec10s2rpop2016': 'Pop_45_49_ans_F',
    
    # 50-54 ans
    'ageq_rec11s1rpop2016': 'Pop_50_54_ans_H',
    'ageq_rec11s2rpop2016': 'Pop_50_54_ans_F',
    
    # 55-59 ans
    'ageq_rec12s1rpop2016': 'Pop_55_59_ans_H',
    'ageq_rec12s2rpop2016': 'Pop_55_59_ans_F',
    
    # 60-64 ans
    'ageq_rec13s1rpop2016': 'Pop_60_64_ans_H',
    'ageq_rec13s2rpop2016': 'Pop_60_64_ans_F',
    
    # 65-69 ans
    'ageq_rec14s1rpop2016': 'Pop_65_69_ans_H',
    'ageq_rec14s2rpop2016': 'Pop_65_69_ans_F',
    
    # 70-74 ans
    'ageq_rec15s1rpop2016': 'Pop_70_74_ans_H',
    'ageq_rec15s2rpop2016': 'Pop_70_74_ans_F',
    
    # 75-79 ans
    'ageq_rec16s1rpop2016': 'Pop_75_79_ans_H',
    'ageq_rec16s2rpop2016': 'Pop_75_79_ans_F',
    
    # 80-84 ans
    'ageq_rec17s1rpop2016': 'Pop_80_84_ans_H',
    'ageq_rec17s2rpop2016': 'Pop_80_84_ans_F',
    
    # 85-89 ans
    'ageq_rec18s1rpop2016': 'Pop_85_89_ans_H',
    'ageq_rec18s2rpop2016': 'Pop_85_89_ans_F',
    
    # 90-94 ans
    'ageq_rec19s1rpop2016': 'Pop_90_94_ans_H',
    'ageq_rec19s2rpop2016': 'Pop_90_94_ans_F',
    
    # 95+ ans
    'ageq_rec20s1rpop2016': 'Pop_95+_ans_H',
    'ageq_rec20s2rpop2016': 'Pop_95+_ans_F'
}

# 7. CONCATÉNER + RENOMMER + SAUVEGARDER
df_final = pd.concat([df_2016_final, df_2022_final], ignore_index=True)
df_final = df_final.rename(columns=rename_dict_final)

df_final.to_csv("Donnees_clean/Population_tranche_age_finale.csv", index=False)


## -------------------------- Fichier Menage_age_situation --------------------------------------
# 1. CHARGER EXCEL ORIGINAL (feuille COM)
df_raw = pd.read_excel(
    "Menage_age_situation.xlsx",
    sheet_name="COM",
    skiprows=10
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
    "Acigné", "Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné",
    "Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé",
    "La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger",
    "Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères",
    "Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel","Saint-Erblon",
    "Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt",
    "Thorigné-Fouillard","Vern-sur-Seiche","Vezin-le-Coquet", "Clayes", "La Chapelle-Chaussée", 
    "Laillé", "Langan", "Miniac-sous-Bécherel"
]

communes_a_garder = communes_grenoble + communes_rennes

# 3. FILTRE COMMUNES (par LIBGEO) + DÉPARTEMENTS 35/38 (via CODGEO)
# Dans ce fichier, la commune est LIBGEO et le code géographique est CODGEO [file:135]
df = df_raw.copy()

# Filtre communes
df = df[df["LIBGEO"].isin(communes_a_garder)]

# Filtre départements 35 (Ille-et-Vilaine) et 38 (Isère) sur les 2 premiers caractères du CODGEO [file:135]
df = df[df["CODGEO"].str[:2].isin(["35", "38"])]

# 4. DÉTECTION DES COLONNES "MÉNAGES"
# Colonnes de la feuille COM : CODGEO, LIBGEO, puis AGEMEN7xxTDM8yy [file:135]
cols_menages = [col for col in df.columns if col.startswith("AGEMEN7")]

# Arrondir vers l'entier
df[cols_menages] = df[cols_menages].round(0).astype(int)

# 5. STRUCTURE DE SORTIE (base + colonnes ménages + année)
cols_base = ["CODGEO", "LIBGEO"]
cols_finales = cols_base + cols_menages

df_final = df[cols_finales].copy()

# 6. RENOMMAGE POUR L’ANALYSE

rename_dict_final = {
    "AGEMEN700TDM8100": "Menages_moins20ans_pers_seule",
    "AGEMEN720TDM8100": "Menages_20_24ans_pers_seule",
    "AGEMEN725TDM8100": "Menages_25_39ans_pers_seule",
    "AGEMEN740TDM8100": "Menages_40_54ans_pers_seule",
    "AGEMEN755TDM8100": "Menages_55_64ans_pers_seule",
    "AGEMEN765TDM8100": "Menages_65_79ans_pers_seule",
    "AGEMEN780TDM8100": "Menages_plus80ans_pers_seule",

    "AGEMEN700TDM8200": "Menages_moins20ans_cpl_sans_enf",
    "AGEMEN720TDM8200": "Menages_20_24ans_cpl_sans_enf",
    "AGEMEN725TDM8200": "Menages_25_39ans_cpl_sans_enf",
    "AGEMEN740TDM8200": "Menages_40_54ans_cpl_sans_enf",
    "AGEMEN755TDM8200": "Menages_55_64ans_cpl_sans_enf",
    "AGEMEN765TDM8200": "Menages_65_79ans_cpl_sans_enf",
    "AGEMEN780TDM8200": "Menages_plus80ans_cpl_sans_enf",

    "AGEMEN700TDM8300": "Menages_moins20ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",
    "AGEMEN720TDM8300": "Menages_20_24ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",
    "AGEMEN725TDM8300": "Menages_25_39ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",
    "AGEMEN740TDM8300": "Menages_40_54ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",
    "AGEMEN755TDM8300": "Menages_55_64ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",
    "AGEMEN765TDM8300": "Menages_65_79ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",
    "AGEMEN780TDM8300": "Menages_plus80ans_cpl_1enf_ou_plus_dun_des_deux_membres_du_cpl",

    "AGEMEN700TDM8310": "Menages_moins20ans_cpl_avec_enfant_du_couple",
    "AGEMEN720TDM8310": "Menages_20_24ans_cpl_avec_enfant_du_couple",
    "AGEMEN725TDM8310": "Menages_25_39ans_cpl_avec_enfant_du_couple",
    "AGEMEN740TDM8310": "Menages_40_54ans_cpl_avec_enfant_du_couple",
    "AGEMEN755TDM8310": "Menages_55_64ans_cpl_avec_enfant_du_couple",
    "AGEMEN765TDM8310": "Menages_65_79ans_cpl_avec_enfant_du_couple",
    "AGEMEN780TDM8310": "Menages_plus80ans_cpl_avec_enfant_du_couple",

    "AGEMEN700TDM8410": "Menages_moins20ans_fam_monoparentale_pere_enf",
    "AGEMEN720TDM8410": "Menages_20_24ans_fam_monoparentale_pere_enf",
    "AGEMEN725TDM8410": "Menages_25_39ans_fam_monoparentale_pere_enf",
    "AGEMEN740TDM8410": "Menages_40_54ans_fam_monoparentale_pere_enf",
    "AGEMEN755TDM8410": "Menages_55_64ans_fam_monoparentale_pere_enf",
    "AGEMEN765TDM8410": "Menages_65_79ans_fam_monoparentale_pere_enf",
    "AGEMEN780TDM8410": "Menages_plus80ans_fam_monoparentale_pere_enf",

    "AGEMEN700TDM8420": "Menages_moins20ans_fam_monoparentale_mere_enf",
    "AGEMEN720TDM8420": "Menages_20_24ans_fam_monoparentale_mere_enf",
    "AGEMEN725TDM8420": "Menages_25_39ans_fam_monoparentale_mere_enf",
    "AGEMEN740TDM8420": "Menages_40_54ans_fam_monoparentale_mere_enf",
    "AGEMEN755TDM8420": "Menages_55_64ans_fam_monoparentale_mere_enf",
    "AGEMEN765TDM8420": "Menages_65_79ans_fam_monoparentale_mere_enf",
    "AGEMEN780TDM8420": "Menages_plus80ans_fam_monoparentale_mere_enf",

    "AGEMEN700TDM8500": "Menages_moins20ans_autre_menage",
    "AGEMEN720TDM8500": "Menages_20_24ans_autre_menage",
    "AGEMEN725TDM8500": "Menages_25_39ans_autre_menage",
    "AGEMEN740TDM8500": "Menages_40_54ans_autre_menage",
    "AGEMEN755TDM8500": "Menages_55_64ans_autre_menage",
    "AGEMEN765TDM8500": "Menages_65_79ans_autre_menage",
    "AGEMEN780TDM8500": "Menages_plus80ans_autre_menage"

}

df_final = df_final.rename(columns=rename_dict_final)

# 8. SAUVEGARDER
df_final.to_csv("Donnees_clean/Menage_age_situation_final.csv", index=False)


## -------------------------- Fichier Menage_csp_nbpers --------------------------------------

# 1. CHARGER EXCEL ORIGINAL (feuille COM)
df_raw = pd.read_excel(
    "Menages_csp_nbpers.xlsx",
    sheet_name="COM",
    skiprows=10
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
    "Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé",
    "La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger",
    "Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères",
    "Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel",
    "Saint-Erblon","Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande",
    "Saint-Sulpice-la-Forêt","Thorigné-Fouillard","Vern-sur-Seiche",
    "Vezin-le-Coquet","Clayes","La Chapelle-Chaussée",
    "Laillé","Langan","Miniac-sous-Bécherel"
]

communes_a_garder = communes_grenoble + communes_rennes

# 3. FILTRE COMMUNES + DÉPARTEMENTS
df = df_raw.copy()

df = df[df["LIBGEO"].isin(communes_a_garder)]
df = df[df["CODGEO"].astype(str).str[:2].isin(["35", "38"])]

# 4. DÉTECTION DES COLONNES "CSP x NOMBRE DE PERSONNES"
# (dans ce fichier les colonnes commencent généralement par MEN...)
cols_menages = [col for col in df.columns if col.startswith("MEN")]

# Nettoyage numérique
df[cols_menages] = (
    df[cols_menages]
    .replace("..", 0)
    .fillna(0)
    .round(0)
    .astype(int)
)

# 5. STRUCTURE DE SORTIE
cols_base = ["CODGEO", "LIBGEO"]
cols_finales = cols_base + cols_menages

df_final = df[cols_finales].copy()

# 6. RENOMMAGE AUTOMATIQUE PLUS LISIBLE
# Exemple : MEN1P_CSP1 → Menages_1_personne_agriculteurs

rename_dict_final = {
# 1 PERSONNE
"NPERC1_STAT_CS110_210": "Menages_1pers_agriculteurs",
"NPERC1_STAT_CS121_221": "Menages_1pers_artisans",
"NPERC1_STAT_CS122_222": "Menages_1pers_commercants",
"NPERC1_STAT_CS123_223": "Menages_1pers_chef_entreprise_10plus",
"NPERC1_STAT_CS131_231": "Menages_1pers_professions_liberales",
"NPERC1_STAT_CS133_233": "Menages_1pers_cadre_admin_fonction_pub",
"NPERC1_STAT_CS134_234": "Menages_1pers_prof_scientifique_sup",
"NPERC1_STAT_CS135_235": "Menages_1pers_info_art_spectacle",
"NPERC1_STAT_CS137_237": "Menages_1pers_cadre_commercial",
"NPERC1_STAT_CS138_238": "Menages_1pers_ingenieur_cadre_tech",
"NPERC1_STAT_CS142_242": "Menages_1pers_prof_enseignement",
"NPERC1_STAT_CS143_243": "Menages_1pers_prof_inter_sante_social",
"NPERC1_STAT_CS144_244": "Menages_1pers_religieux",
"NPERC1_STAT_CS145_245": "Menages_1pers_prof_inter_fonction_pub",
"NPERC1_STAT_CS146_246": "Menages_1pers_prof_inter_admin_com",
"NPERC1_STAT_CS147_247": "Menages_1pers_technicien",
"NPERC1_STAT_CS148_248": "Menages_1pers_agent_maitrise",
"NPERC1_STAT_CS152_252": "Menages_1pers_emp_fonction_pub",
"NPERC1_STAT_CS153_253": "Menages_1pers_securite_defense",
"NPERC1_STAT_CS154_254": "Menages_1pers_emp_admin_entreprise",
"NPERC1_STAT_CS155_255": "Menages_1pers_emp_commerce",
"NPERC1_STAT_CS156_256": "Menages_1pers_service_particulier",
"NPERC1_STAT_CS162_262": "Menages_1pers_ouvrier_qualif_indus",
"NPERC1_STAT_CS163_263": "Menages_1pers_ouvrier_qualif_artisanal",
"NPERC1_STAT_CS164_264": "Menages_1pers_conducteur_transport",
"NPERC1_STAT_CS165_265": "Menages_1pers_cariste_magasinier",
"NPERC1_STAT_CS167_267": "Menages_1pers_ouvrier_peu_qualif_indus",
"NPERC1_STAT_CS168_268": "Menages_1pers_ouvrier_peu_qualif_artisanal",
"NPERC1_STAT_CS169_269": "Menages_1pers_ouvrier_agricole",
"NPERC1_STAT_CS200": "Menages_1pers_chomeur_jamais_travaille",
"NPERC1_STAT_CS400": "Menages_1pers_retraites_inactifs",


# 2 PERSONNES
"NPERC2_STAT_CS110_210": "Menages_2pers_agriculteurs",
"NPERC2_STAT_CS121_221": "Menages_2pers_artisans",
"NPERC2_STAT_CS122_222": "Menages_2pers_commercants",
"NPERC2_STAT_CS123_223": "Menages_2pers_chef_entreprise_10plus",
"NPERC2_STAT_CS131_231": "Menages_2pers_professions_liberales",
"NPERC2_STAT_CS133_233": "Menages_2pers_cadre_admin_fonction_pub",
"NPERC2_STAT_CS134_234": "Menages_2pers_prof_scientifique_sup",
"NPERC2_STAT_CS135_235": "Menages_2pers_info_art_spectacle",
"NPERC2_STAT_CS137_237": "Menages_2pers_cadre_commercial",
"NPERC2_STAT_CS138_238": "Menages_2pers_ingenieur_cadre_tech",
"NPERC2_STAT_CS142_242": "Menages_2pers_prof_enseignement",
"NPERC2_STAT_CS143_243": "Menages_2pers_prof_inter_sante_social",
"NPERC2_STAT_CS144_244": "Menages_2pers_religieux",
"NPERC2_STAT_CS145_245": "Menages_2pers_prof_inter_fonction_pub",
"NPERC2_STAT_CS146_246": "Menages_2pers_prof_inter_admin_com",
"NPERC2_STAT_CS147_247": "Menages_2pers_technicien",
"NPERC2_STAT_CS148_248": "Menages_2pers_agent_maitrise",
"NPERC2_STAT_CS152_252": "Menages_2pers_emp_fonction_pub",
"NPERC2_STAT_CS153_253": "Menages_2pers_securite_defense",
"NPERC2_STAT_CS154_254": "Menages_2pers_emp_admin_entreprise",
"NPERC2_STAT_CS155_255": "Menages_2pers_emp_commerce",
"NPERC2_STAT_CS156_256": "Menages_2pers_service_particulier",
"NPERC2_STAT_CS162_262": "Menages_2pers_ouvrier_qualif_indus",
"NPERC2_STAT_CS163_263": "Menages_2pers_ouvrier_qualif_artisanal",
"NPERC2_STAT_CS164_264": "Menages_2pers_conducteur_transport",
"NPERC2_STAT_CS165_265": "Menages_2pers_cariste_magasinier",
"NPERC2_STAT_CS167_267": "Menages_2pers_ouvrier_peu_qualif_indus",
"NPERC2_STAT_CS168_268": "Menages_2pers_ouvrier_peu_qualif_artisanal",
"NPERC2_STAT_CS169_269": "Menages_2pers_ouvrier_agricole",
"NPERC2_STAT_CS200": "Menages_2pers_chomeur_jamais_travaille",
"NPERC2_STAT_CS400": "Menages_2pers_retraites_inactifs",

# 3 PERSONNES
"NPERC3_STAT_CS110_210": "Menages_3pers_agriculteurs",
"NPERC3_STAT_CS121_221": "Menages_3pers_artisans",
"NPERC3_STAT_CS122_222": "Menages_3pers_commercants",
"NPERC3_STAT_CS123_223": "Menages_3pers_chef_entreprise_10plus",
"NPERC3_STAT_CS131_231": "Menages_3pers_professions_liberales",
"NPERC3_STAT_CS133_233": "Menages_3pers_cadre_admin_fonction_pub",
"NPERC3_STAT_CS134_234": "Menages_3pers_prof_scientifique_sup",
"NPERC3_STAT_CS135_235": "Menages_3pers_info_art_spectacle",
"NPERC3_STAT_CS137_237": "Menages_3pers_cadre_commercial",
"NPERC3_STAT_CS138_238": "Menages_3pers_ingenieur_cadre_tech",
"NPERC3_STAT_CS142_242": "Menages_3pers_prof_enseignement",
"NPERC3_STAT_CS143_243": "Menages_3pers_prof_inter_sante_social",
"NPERC3_STAT_CS144_244": "Menages_3pers_religieux",
"NPERC3_STAT_CS145_245": "Menages_3pers_prof_inter_fonction_pub",
"NPERC3_STAT_CS146_246": "Menages_3pers_prof_inter_admin_com",
"NPERC3_STAT_CS147_247": "Menages_3pers_technicien",
"NPERC3_STAT_CS148_248": "Menages_3pers_agent_maitrise",
"NPERC3_STAT_CS152_252": "Menages_3pers_emp_fonction_pub",
"NPERC3_STAT_CS153_253": "Menages_3pers_securite_defense",
"NPERC3_STAT_CS154_254": "Menages_3pers_emp_admin_entreprise",
"NPERC3_STAT_CS155_255": "Menages_3pers_emp_commerce",
"NPERC3_STAT_CS156_256": "Menages_3pers_service_particulier",
"NPERC3_STAT_CS162_262": "Menages_3pers_ouvrier_qualif_indus",
"NPERC3_STAT_CS163_263": "Menages_3pers_ouvrier_qualif_artisanal",
"NPERC3_STAT_CS164_264": "Menages_3pers_conducteur_transport",
"NPERC3_STAT_CS165_265": "Menages_3pers_cariste_magasinier",
"NPERC3_STAT_CS167_267": "Menages_3pers_ouvrier_peu_qualif_indus",
"NPERC3_STAT_CS168_268": "Menages_3pers_ouvrier_peu_qualif_artisanal",
"NPERC3_STAT_CS169_269": "Menages_3pers_ouvrier_agricole",
"NPERC3_STAT_CS200": "Menages_3pers_chomeur_jamais_travaille",
"NPERC3_STAT_CS400": "Menages_3pers_retraites_inactifs",

# 4 PERSONNES
"NPERC4_STAT_CS110_210": "Menages_4pers_agriculteurs",
"NPERC4_STAT_CS121_221": "Menages_4pers_artisans",
"NPERC4_STAT_CS122_222": "Menages_4pers_commercants",
"NPERC4_STAT_CS123_223": "Menages_4pers_chef_entreprise_10plus",
"NPERC4_STAT_CS131_231": "Menages_4pers_professions_liberales",
"NPERC4_STAT_CS133_233": "Menages_4pers_cadre_admin_fonction_pub",
"NPERC4_STAT_CS134_234": "Menages_4pers_prof_scientifique_sup",
"NPERC4_STAT_CS135_235": "Menages_4pers_info_art_spectacle",
"NPERC4_STAT_CS137_237": "Menages_4pers_cadre_commercial",
"NPERC4_STAT_CS138_238": "Menages_4pers_ingenieur_cadre_tech",
"NPERC4_STAT_CS142_242": "Menages_4pers_prof_enseignement",
"NPERC4_STAT_CS143_243": "Menages_4pers_prof_inter_sante_social",
"NPERC4_STAT_CS144_244": "Menages_4pers_religieux",
"NPERC4_STAT_CS145_245": "Menages_4pers_prof_inter_fonction_pub",
"NPERC4_STAT_CS146_246": "Menages_4pers_prof_inter_admin_com",
"NPERC4_STAT_CS147_247": "Menages_4pers_technicien",
"NPERC4_STAT_CS148_248": "Menages_4pers_agent_maitrise",
"NPERC4_STAT_CS152_252": "Menages_4pers_emp_fonction_pub",
"NPERC4_STAT_CS153_253": "Menages_4pers_securite_defense",
"NPERC4_STAT_CS154_254": "Menages_4pers_emp_admin_entreprise",
"NPERC4_STAT_CS155_255": "Menages_4pers_emp_commerce",
"NPERC4_STAT_CS156_256": "Menages_4pers_service_particulier",
"NPERC4_STAT_CS162_262": "Menages_4pers_ouvrier_qualif_indus",
"NPERC4_STAT_CS163_263": "Menages_4pers_ouvrier_qualif_artisanal",
"NPERC4_STAT_CS164_264": "Menages_4pers_conducteur_transport",
"NPERC4_STAT_CS165_265": "Menages_4pers_cariste_magasinier",
"NPERC4_STAT_CS167_267": "Menages_4pers_ouvrier_peu_qualif_indus",
"NPERC4_STAT_CS168_268": "Menages_4pers_ouvrier_peu_qualif_artisanal",
"NPERC4_STAT_CS169_269": "Menages_4pers_ouvrier_agricole",
"NPERC4_STAT_CS200": "Menages_4pers_chomeur_jamais_travaille",
"NPERC4_STAT_CS400": "Menages_4pers_retraites_inactifs",

# 5 PERSONNES
"NPERC5_STAT_CS110_210": "Menages_5pers_agriculteurs",
"NPERC5_STAT_CS121_221": "Menages_5pers_artisans",
"NPERC5_STAT_CS122_222": "Menages_5pers_commercants",
"NPERC5_STAT_CS123_223": "Menages_5pers_chef_entreprise_10plus",
"NPERC5_STAT_CS131_231": "Menages_5pers_professions_liberales",
"NPERC5_STAT_CS133_233": "Menages_5pers_cadre_admin_fonction_pub",
"NPERC5_STAT_CS134_234": "Menages_5pers_prof_scientifique_sup",
"NPERC5_STAT_CS135_235": "Menages_5pers_info_art_spectacle",
"NPERC5_STAT_CS137_237": "Menages_5pers_cadre_commercial",
"NPERC5_STAT_CS138_238": "Menages_5pers_ingenieur_cadre_tech",
"NPERC5_STAT_CS142_242": "Menages_5pers_prof_enseignement",
"NPERC5_STAT_CS143_243": "Menages_5pers_prof_inter_sante_social",
"NPERC5_STAT_CS144_244": "Menages_5pers_religieux",
"NPERC5_STAT_CS145_245": "Menages_5pers_prof_inter_fonction_pub",
"NPERC5_STAT_CS146_246": "Menages_5pers_prof_inter_admin_com",
"NPERC5_STAT_CS147_247": "Menages_5pers_technicien",
"NPERC5_STAT_CS148_248": "Menages_5pers_agent_maitrise",
"NPERC5_STAT_CS152_252": "Menages_5pers_emp_fonction_pub",
"NPERC5_STAT_CS153_253": "Menages_5pers_securite_defense",
"NPERC5_STAT_CS154_254": "Menages_5pers_emp_admin_entreprise",
"NPERC5_STAT_CS155_255": "Menages_5pers_emp_commerce",
"NPERC5_STAT_CS156_256": "Menages_5pers_service_particulier",
"NPERC5_STAT_CS162_262": "Menages_5pers_ouvrier_qualif_indus",
"NPERC5_STAT_CS163_263": "Menages_5pers_ouvrier_qualif_artisanal",
"NPERC5_STAT_CS164_264": "Menages_5pers_conducteur_transport",
"NPERC5_STAT_CS165_265": "Menages_5pers_cariste_magasinier",
"NPERC5_STAT_CS167_267": "Menages_5pers_ouvrier_peu_qualif_indus",
"NPERC5_STAT_CS168_268": "Menages_5pers_ouvrier_peu_qualif_artisanal",
"NPERC5_STAT_CS169_269": "Menages_5pers_ouvrier_agricole",
"NPERC5_STAT_CS200": "Menages_5pers_chomeur_jamais_travaille",
"NPERC5_STAT_CS400": "Menages_5pers_retraites_inactifs",

# 6 PERSONNES OU PLUS
"NPERC6_STAT_CS110_210": "Menages_6pers_ouplus_agriculteurs",
"NPERC6_STAT_CS121_221": "Menages_6pers_ouplus_artisans",
"NPERC6_STAT_CS122_222": "Menages_6pers_ouplus_commercants",
"NPERC6_STAT_CS123_223": "Menages_6pers_ouplus_chef_entreprise_10plus",
"NPERC6_STAT_CS131_231": "Menages_6pers_ouplus_professions_liberales",
"NPERC6_STAT_CS133_233": "Menages_6pers_ouplus_cadre_admin_fonction_pub",
"NPERC6_STAT_CS134_234": "Menages_6pers_ouplus_prof_scientifique_sup",
"NPERC6_STAT_CS135_235": "Menages_6pers_ouplus_info_art_spectacle",
"NPERC6_STAT_CS137_237": "Menages_6pers_ouplus_cadre_commercial",
"NPERC6_STAT_CS138_238": "Menages_6pers_ouplus_ingenieur_cadre_tech",
"NPERC6_STAT_CS142_242": "Menages_6pers_ouplus_prof_enseignement",
"NPERC6_STAT_CS143_243": "Menages_6pers_ouplus_prof_inter_sante_social",
"NPERC6_STAT_CS144_244": "Menages_6pers_ouplus_religieux",
"NPERC6_STAT_CS145_245": "Menages_6pers_ouplus_prof_inter_fonction_pub",
"NPERC6_STAT_CS146_246": "Menages_6pers_ouplus_prof_inter_admin_com",
"NPERC6_STAT_CS147_247": "Menages_6pers_ouplus_technicien",
"NPERC6_STAT_CS148_248": "Menages_6pers_ouplus_agent_maitrise",
"NPERC6_STAT_CS152_252": "Menages_6pers_ouplus_emp_fonction_pub",
"NPERC6_STAT_CS153_253": "Menages_6pers_ouplus_securite_defense",
"NPERC6_STAT_CS154_254": "Menages_6pers_ouplus_emp_admin_entreprise",
"NPERC6_STAT_CS155_255": "Menages_6pers_ouplus_emp_commerce",
"NPERC6_STAT_CS156_256": "Menages_6pers_ouplus_service_particulier",
"NPERC6_STAT_CS162_262": "Menages_6pers_ouplus_ouvrier_qualif_indus",
"NPERC6_STAT_CS163_263": "Menages_6pers_ouplus_ouvrier_qualif_artisanal",
"NPERC6_STAT_CS164_264": "Menages_6pers_ouplus_conducteur_transport",
"NPERC6_STAT_CS165_265": "Menages_6pers_ouplus_cariste_magasinier",
"NPERC6_STAT_CS167_267": "Menages_6pers_ouplus_ouvrier_peu_qualif_indus",
"NPERC6_STAT_CS168_268": "Menages_6pers_ouplus_ouvrier_peu_qualif_artisanal",
"NPERC6_STAT_CS169_269": "Menages_6pers_ouplus_ouvrier_agricole",
"NPERC6_STAT_CS200": "Menages_6pers_ouplus_chomeur_jamais_travaille",
"NPERC6_STAT_CS400": "Menages_6pers_ouplus_retraites_inactifs",

}

df_final = df_final.rename(columns=rename_dict)

# 7. SAUVEGARDE
df_final.to_csv("Donnees_clean/Menages_csp_nbpers_final.csv",index=False)


## -------------------------- Fichier Mobilite_profess.csv --------------------------------------
# 1. CHARGER LE FICHIER ORIGINAL
df_raw = pd.read_csv(
    "Mobilite_profess.csv",
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
    "Donnees_clean/Mobilite_professionnelle_clean.csv",
    index=False
)

## -------------------------- Fichier Mobilite_scolaire.csv --------------------------------------
# 1. CHARGER LE FICHIER ORIGINAL
df_raw = pd.read_csv(
    "Mobilite_scolaire.csv",
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
    "Donnees_clean/Mobilite_scolaire_clean.csv",
    index=False
)