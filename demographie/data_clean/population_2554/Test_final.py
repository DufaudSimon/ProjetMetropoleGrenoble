import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import unicodedata

# =================================================================
# 1. CONFIGURATION ET DESIGN (CSS FINALISÉ)
# =================================================================
st.set_page_config(page_title="Analytics Territoires", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Application de la police sur les zones de contenu sans casser les icônes système */
    .main .block-container, div[data-testid="stSidebar"] {
        font-family: 'Inter', sans-serif;
        color: #2c3e50;
    }
    
    /* Design des onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 8px 8px 0px 0px;
        padding: 10px 20px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; color: white !important; }

    /* Cartes KPI - Barre bleue à gauche et texte aligné à gauche */
    .kpi-card {
        background-color: white; 
        padding: 20px 25px; 
        border-radius: 12px;
        border-left: 6px solid #3498db; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-label { font-size: 12px; font-weight: 700; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 28px; font-weight: 800; color: #2c3e50; margin: 5px 0; }
    .kpi-subtitle { font-size: 11px; color: #95a5a6; }
    
    /* Conteneurs de graphes */
    div[data-testid="stVerticalBlock"] > div:has(div.plot-container) {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. RÉFÉRENTIELS ET MAPPINGS
# =================================================================
METROPOLES_DEF = {
    "Grenoble": {"dep": "38", "communes": ["Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix","Corenc","Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon","Gières","Grenoble","Herbeys","Jarrie","La Tronche","Le Gua","Le Pont-de-Claix","Le Sappey-en-Chartreuse","Meylan","Miribel-Lanchâtre","Mont-Saint-Martin","Montchaboud","Murianette","Notre-Dame-de-Commiers","Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux","Quaix-en-Chartreuse","Saint-Barthélemy-de-Séchilienne","Saint-Égrève","Saint-Georges-de-Commiers","Saint-Martin-d'Hères","Saint-Martin-le-Vinoux","Saint-Paul-de-Varces","Saint-Pierre-de-Mésage","Sarcenas","Sassenage","Séchilienne","Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset","Vaulnaveys-le-Bas","Vaulnaveys-le-Haut","Venon","Veurey-Voroize","Vif","Vizille"]},
    "Rennes": {"dep": "35", "communes": ["Acigné","Bécherel","Betton","Bourgbarré","Brécé","Bruz","Cesson-Sévigné","Chantepie","Chartres-de-Bretagne","Chavagne","Chevaigné","Cintré","Corps-Nuds","Gévezé","La Chapelle-des-Fougeretz","La Chapelle-Thouarault","L'Hermitage","Le Rheu","Le Verger","Montgermont","Mordelles","Noyal-Châtillon-sur-Seiche","Nouvoitou","Orgères","Pacé","Parthenay-de-Bretagne","Pont-Péan","Rennes","Romillé","Saint-Armel","Saint-Erblon","Saint-Gilles","Saint-Grégoire","Saint-Jacques-de-la-Lande","Saint-Sulpice-la-Forêt","Thorigné-Fouillard","Vern-sur-Seiche","Vezin-le-Coquet","Clayes","La Chapelle-Chaussée","Laillé","Langan","Miniac-sous-Bécherel"]},
    "Rouen": {"dep": "76", "communes": ["Amfreville-la-Mi-Voie","Anneville-Ambourville","Bardouville","Belbeuf","Berville-sur-Seine","Bihorel","Bois-Guillaume","Bonsecours","Boos","Canteleu","Caudebec-lès-Elbeuf","Cléon","Darnétal","Déville-lès-Rouen","Duclair","Elbeuf","Épinay-sur-Duclair","Fontaine-sous-Préaux","Franqueville-Saint-Pierre","Freneuse","Gouy","Grand-Couronne","Hautot-sur-Seine","Hénouville","Houppeville","Isneauville","Jumièges","La Bouille","La Londe","La Neuville-Chant-d'Oisel","Le Grand-Quevilly","Le Houlme","Le Mesnil-Esnard","Le Mesnil-sous-Jumièges","Le Petit-Quevilly","Le Trait","Les Authieux-sur-le-Port-Saint-Ouen","Malaunay","Maromme","Mont-Saint-Aignan","Montmain","Moulineaux","Notre-Dame-de-Bondeville","Oissel","Orival","Petit-Couronne","Quevillon","Quévreville-la-Poterie","Roncherolles-sur-le-Vivier","Rouen","Sahurs","Saint-Aubin-Celloville","Saint-Aubin-Épinay","Saint-Aubin-lès-Elbeuf","Saint-Étienne-du-Rouvray","Saint-Jacques-sur-Darnétal","Saint-Léger-du-Bourg-Denis","Saint-Martin-de-Boscherville","Saint-Martin-du-Vivier","Saint-Paër","Saint-Pierre-de-Manneville","Saint-Pierre-de-Varengeville","Saint-Pierre-lès-Elbeuf","Sainte-Marguerite-sur-Duclair","Sotteville-lès-Rouen","Sotteville-sous-le-Val","Tourville-la-Rivière","Val-de-la-Haye","Yainville","Ymare","Yville-sur-Seine"]},
    "Saint-Étienne": {"dep": "42", "communes": ["Aboën","Andrézieux-Bouthéon","Caloire","Cellieu","Chagnon","Chambœuf","Châteauneuf","Dargoire","Doizieux","Farnay","Firminy","Fontanès","Fraisses","Genilac","L'Étrat","L'Horme","La Fouillouse","La Gimond","La Grand-Croix","La Ricamarie","La Talaudière","La Terrasse-sur-Dorlay","La Tour-en-Jarez","La Valla-en-Gier","Le Chambon-Feugerolles","Lorette","Marcenod","Pavezin","Rive-de-Gier","Roche-la-Molière","Rozier-Côtes-d'Aurec","Saint-Bonnet-les-Oules","Saint-Chamond","Saint-Christo-en-Jarez","Saint-Étienne","Saint-Galmier","Saint-Genest-Lerpt","Saint-Héand","Saint-Jean-Bonnefonds","Saint-Joseph","Saint-Martin-la-Plaine","Saint-Maurice-en-Gourgois","Saint-Nizier-de-Fornas","Saint-Paul-en-Cornillon","Saint-Paul-en-Jarez","Saint-Priest-en-Jarez","Saint-Romain-en-Jarez","Sainte-Croix-en-Jarez","Sorbiers","Tartaras","Unieux","Valfleury","Villars"]},
    "Montpellier": {"dep": "34", "communes": ["Baillargues","Beaulieu","Castelnau-le-Lez","Castries","Clapiers","Cournonsec","Cournonterral","Fabrègues","Grabels","Jacou","Juvignac","Lattes","Lavérune","Le Crès","Montaud","Montferrier-sur-Lez","Montpellier","Murviel-lès-Montpellier","Pérols","Pignan","Prades-le-Lez","Restinclières","Saint-Brès","Saint-Drézéry","Saint-Geniès-des-Mourgues","Saint-Georges-d'Orques","Saint-Jean-de-Védas","Saussan","Sussargues","Vendargues","Villeneuve-lès-Maguelone"]}
}

CSP_MAP = {"Agriculteurs": "Agriculteurs", "Artisans": "Artisans & Chefs", "Cadres": "Cadres & Prof. Sup.", 
           "Professions intermédiaires": "Prof. Intermédiaires", "Employés": "Employés", "Ouvriers": "Ouvriers"}

DIP_MAP = {"Aucun diplôme": "Sans diplôme", "niveau CEP": "CEP", "niveau BEPC": "BEPC", "niveau CAP-BEP": "CAP-BEP", 
           "bac général ou technique": "Baccalauréat", "universitaire de 1er cycle": "Bac + 2", 
           "universitaire de 2ème": "Bac + 3/4", "universitaire de 3ème": "Supérieur (Bac+5+)"}

# =================================================================
# 3. LOGIQUE DE DONNÉES
# =================================================================
def normalize(text):
    if pd.isna(text): return ""
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("utf-8").lower().strip()

@st.cache_data
def load_generic_data(file_paths, mapping_dict):
    all_data = []
    for year, path in file_paths.items():
        try:
            df = pd.read_excel(path)
            if "RR" in str(df.iloc[0, 0]): df = df.drop(0).reset_index(drop=True)
            c_dep = [c for c in df.columns if any(x in str(c).upper() for x in ["DÉPARTEMENT", "DR24", "DEP"])][0]
            c_lib = [c for c in df.columns if any(x in str(c).upper() for x in ["LIBELLÉ", "LIBELLE"])][0]
            res = pd.DataFrame({"DEP": df[c_dep].astype(str).str.zfill(2), "NOM": df[c_lib].astype(str), 
                                "ANNEE": int(year), "LIB_NORM": df[c_lib].apply(normalize)})
            for raw, clean in mapping_dict.items():
                cols = [c for c in df.columns if raw.lower() in str(c).lower()]
                res[clean] = df[cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)
            all_data.append(res)
        except: continue
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Chargement
files_csp = {2011: "Commune_2011_2554_sect_activite.xlsx", 2016: "Commune_2016_2554_sect_activite.xlsx", 2022: "Commune_2022_2554_sect_activite.xlsx"}
files_dip = {2011: "Commune_2011_2554_niveau_diplome.xlsx", 2022: "Commune_2022_2554_niveau_diplome.xlsx"}

df_csp = load_generic_data(files_csp, CSP_MAP)
df_dip = load_generic_data(files_dip, DIP_MAP)

# =================================================================
# 4. SIDEBAR
# =================================================================
with st.sidebar:
    st.header("⚙️ Paramètres")
    theme_analyse = st.selectbox("Thématique", ["Secteurs d'activité (CSP)", "Niveau de diplôme"])
    current_df = df_csp if theme_analyse == "Secteurs d'activité (CSP)" else df_dip
    current_map = CSP_MAP if theme_analyse == "Secteurs d'activité (CSP)" else DIP_MAP
    
    sel_annee = st.selectbox("Année", sorted(current_df["ANNEE"].unique(), reverse=True))
    mode_analyse = st.radio("Comparaison", ["Par Communes (Grenoble)", "Par Métropoles"])
    
    entities_to_plot = []
    if mode_analyse == "Par Communes (Grenoble)":
        sel_list = st.multiselect("Communes", sorted(METROPOLES_DEF["Grenoble"]["communes"]), default=["Grenoble"])
        for name in sel_list:
            subset = current_df[(current_df["ANNEE"] == sel_annee) & (current_df["LIB_NORM"] == normalize(name)) & (current_df["DEP"] == "38")]
            if not subset.empty: entities_to_plot.append({"name": name, "data": subset.iloc[0]})
    else:
        sel_list = st.multiselect("Métropoles", list(METROPOLES_DEF.keys()), default=["Grenoble", "Rouen"])
        for m_name in sel_list:
            m_info = METROPOLES_DEF[m_name]
            subset = current_df[(current_df["ANNEE"] == sel_annee) & (current_df["DEP"] == m_info["dep"]) & (current_df["LIB_NORM"].isin([normalize(c) for c in m_info["communes"]]))]
            if not subset.empty: entities_to_plot.append({"name": m_name, "data": subset[list(current_map.values())].sum()})

    sel_cats = st.multiselect("Catégories", options=list(current_map.values()), default=list(current_map.values()))

# =================================================================
# 5. CORPS PRINCIPAL
# =================================================================
st.title(f"🔍 Analyse : {theme_analyse}")

tab_analyse, tab_methode = st.tabs(["📊 Tableaux de bord", "📖 Méthodologie & Aide"])

# --- ONGLET ANALYSE ---
with tab_analyse:
    if entities_to_plot and sel_cats:
        # Ligne de KPIs (Barre bleue à gauche)
        cols_kpi = st.columns(len(entities_to_plot))
        for i, entity in enumerate(entities_to_plot):
            total = entity["data"][sel_cats].sum()
            with cols_kpi[i]:
                st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-label'>{entity['name']}</div>
                    <div class='kpi-value'>{int(total):,}</div>
                    <div class='kpi-subtitle'>Actifs (25-54 ans)</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Graphes principaux
        c1, c2 = st.columns(2)
        with c1:
            fig_bar = go.Figure()
            for ent in entities_to_plot: fig_bar.add_trace(go.Bar(x=sel_cats, y=ent["data"][sel_cats], name=ent["name"]))
            fig_bar.update_layout(title="Répartition en volume", barmode='group', height=400, margin=dict(t=40, b=0), template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            fig_radar = go.Figure()
            for ent in entities_to_plot:
                v = ent["data"][sel_cats]
                pct = (v / v.sum() * 100).fillna(0)
                fig_radar.add_trace(go.Scatterpolar(r=pct, theta=sel_cats, fill='toself', name=ent["name"]))
            fig_radar.update_layout(title="Profil structurel (en %)", polar=dict(radialaxis=dict(visible=True, range=[0, max(pct)*1.2 if not pct.empty else 100])), height=400, margin=dict(t=40, b=0))
            st.plotly_chart(fig_radar, use_container_width=True)

        # Indice de spécialisation
        if len(entities_to_plot) == 2:
            st.markdown("### 🎯 Analyse Comparative")
            
            # Utilisation d'un titre simple pour l'expander pour éviter le bug visuel
            with st.expander("Aide : Comprendre l'indice de spécialisation"):
                st.write(f"""
                L'indice compare la structure de la **{entities_to_plot[0]['name']}** par rapport à la **{entities_to_plot[1]['name']}**.
                - **100** : La catégorie est présente de la même manière dans les deux zones.
                - **Supérieur à 100** : La catégorie est **sur-représentée** dans la première zone.
                - **Inférieur à 100** : La catégorie est **sous-représentée** dans la première zone.
                """)
            
            v1, v2 = entities_to_plot[0]["data"][sel_cats], entities_to_plot[1]["data"][sel_cats]
            spec = ((v1 / v1.sum()) / (v2 / v2.sum()) * 100).fillna(100)
            fig_spec = px.bar(x=sel_cats, y=spec, color=spec, color_continuous_scale='RdYlBu_r', range_color=[50, 150],
                              labels={'y': 'Indice (Base 100)', 'x': ''}, title=f"Spécialisation : {entities_to_plot[0]['name']} / {entities_to_plot[1]['name']}")
            fig_spec.add_hline(y=100, line_dash="dash", line_color="black")
            st.plotly_chart(fig_spec, use_container_width=True)
    else:
        st.warning("Veuillez sélectionner des entités et des catégories dans le menu de gauche.")

# --- ONGLET MÉTHODOLOGIE ---
with tab_methode:
    st.header("Note méthodologique")
    st.subheader("1. Population étudiée")
    st.write("Analyse sur la population active de 25 à 54 ans (Cœur de cible).")
    st.subheader("2. Source des données")
    st.write("Données issues des recensements Insee (2011, 2016, 2022).")