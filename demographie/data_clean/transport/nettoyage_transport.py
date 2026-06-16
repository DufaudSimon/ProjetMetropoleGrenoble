"""
Nettoyage des fichiers Transport_sexe_lieudetravail_clean_2020/2021.csv

Transforme le format large (60 colonnes ILTRx_SEXEy_TRANS_zzz) en format
long exploitable directement par l'application.

ILTR1-5 : Commune de résidence / Autre commune du département /
            Autre département de la région / Autre région métropolitaine /
            Hors France métropolitaine
SEXE1/2 : Hommes / Femmes
TRANS 191-196 : Pas de transport / Marche à pied / Deux-roues / Autre /
                  Voiture, camion, fourgonnette / Transport en commun

Résultat : transport_metropoles_clean.csv
"""

import pandas as pd

DEP_TO_METRO = {
    "38": "Grenoble", "35": "Rennes", "76": "Rouen",
    "42": "Saint-Étienne", "34": "Montpellier",
}

LIEU_TRAVAIL_LABELS = {
    "ILTR1": "Commune de résidence",
    "ILTR2": "Autre commune du département",
    "ILTR3": "Autre département de la région",
    "ILTR4": "Autre région de France métropolitaine",
    "ILTR5": "Hors France métropolitaine",
}

SEXE_LABELS = {"SEXE1": "Hommes", "SEXE2": "Femmes"}

MODE_LABELS = {
    "191": "Pas de transport",
    "192": "Marche à pied",
    "193": "Deux-roues",
    "194": "Autre",
    "195": "Voiture, camion, fourgonnette",
    "196": "Transport en commun",
}


def nettoyer_transport(path, annee):
    df = pd.read_csv(path, dtype={"CODGEO": str})
    df = df.drop(columns=["FiltreCom"], errors="ignore")
    df["metropole"] = df["CODGEO"].str[:2].map(DEP_TO_METRO)

    value_cols = [c for c in df.columns if c.startswith("ILTR")]
    df_long = df.melt(
        id_vars=["CODGEO", "LIBGEO", "metropole"],
        value_vars=value_cols,
        var_name="cle", value_name="valeur",
    )

    parts = df_long["cle"].str.split("_", expand=True)
    df_long["lieu_travail"]   = parts[0].map(LIEU_TRAVAIL_LABELS)
    df_long["sexe"]           = parts[1].map(SEXE_LABELS)
    df_long["mode_transport"] = parts[3].map(MODE_LABELS)
    df_long["annee"] = annee

    df_long = df_long.rename(columns={"CODGEO": "code_commune", "LIBGEO": "nom_commune"})
    return df_long[[
        "metropole", "code_commune", "nom_commune", "annee",
        "lieu_travail", "sexe", "mode_transport", "valeur",
    ]]


df_2020 = nettoyer_transport("Transport_sexe_lieudetravail_clean_2020.csv", 2020)
df_2021 = nettoyer_transport("Transport_sexe_lieudetravail_clean_2021.csv", 2021)
df_final = pd.concat([df_2020, df_2021], ignore_index=True)

print("══════════════════════════════════════════════")
print(f"Communes par métropole : {df_final.groupby('metropole')['code_commune'].nunique().to_dict()}")
print(f"Années : {sorted(df_final['annee'].unique())}")
print(f"Lignes totales : {len(df_final):,}")
tot = df_final[df_final["annee"] == 2020].groupby("mode_transport")["valeur"].sum()
print("\nRépartition modale 2020 (contrôle) :")
print((tot / tot.sum() * 100).round(1).sort_values(ascending=False))
print("══════════════════════════════════════════════")

df_final.to_csv("transport_metropoles_clean.csv", index=False, encoding="utf-8-sig")
print("✓ Fichier sauvegardé : transport_metropoles_clean.csv")