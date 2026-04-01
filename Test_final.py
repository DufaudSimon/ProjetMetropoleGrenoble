import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import unicodedata

# =================================================================
# 1. CONFIGURATION ET DESIGN PREMIUM
# =================================================================
st.set_page_config(page_title="Analytics Territoires", layout="wide")

# Injection de CSS pour améliorer la police, le relief et le style du sélecteur
st.markdown("""
    <style>
    /* Import de la police Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #2c3e50;
    }
    
    .main { background-color: #f4f7f6; }
    
    /* Style des cartes en relief */
    div[data-testid="stVerticalBlock"] > div:has(div.plot-container) {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    
    /* Style personnalisé pour les indicateurs (KPIs) */
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    /* PERSONNALISATION DU MULTISELECT (Style de ton image) */
    span[data-baseweb="tag"] {
        background-color: #ff4b4b !important; /* Fond rouge */
        border-radius: 4px !important;
        padding-right: 5px !important;
    }
    span[data-baseweb="tag"] span {
        color: #FFFFFF !important; /* Texte blanc pour lisibilité sur rouge */
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] svg {
        fill: #FFFFFF !important; /* Croix de fermeture en blanc */
    }
    </style>
    """, unsafe_allow_html=True)

# Référentiel complet des communes
METROPOLES_DEF = {
    "Grenoble": {"dep": "38", "communes": ["Bresson","Brié-et-Angonnes","Champ-sur-Drac","Champagnier","Claix","Corenc","Domène","Échirolles","Eybens","Fontaine","Fontanil-Cornillon","Gières","Grenoble","Herbeys","Jarrie","La Tronche","Le Gua","Le Pont-de-Claix","Le Sappey-en-Chartreuse","Meylan","Miribel-Lanchâtre","Mont-Saint-Martin","Montchaboud","Murianette","Notre-Dame-de-Commiers","Notre-Dame-de-Mésage","Noyarey","Poisat","Proveysieux","Quaix-en-Chartreuse","Saint-Barthélemy-de-Séchilienne","Saint-Égrève","Saint-Georges-de-Commiers","Saint-Martin-d'Hères","Saint-Martin-le-Vinoux","Saint-Paul-de-Varces","Saint-Pierre-de-Mésage","Sarcenas","Sassenage","Séchilienne","Seyssinet-Pariset","Seyssins","Varces-Allières-et-Risset","Vaulnaveys-le-Bas","Vaulnaveys-le-Haut","Venon","Veurey-Voroize","Vif","Vizille"]},
    "Rennes": {"dep": "35", "communes": ["Rennes","Cesson-Sévigné","Bruz","Saint-Jacques-de-la-Lande","Pacé"]},
    "Rouen": {"dep": "76", "communes": ["Rouen","Sotteville-lès-Rouen","Saint-Étienne-du-Rouvray","Le Grand-Quevilly"]},
    "Saint-Étienne": {"dep": "42", "communes": ["Saint-Étienne","Saint-Chamond","Firminy","Rive-de-Gier"]},
    "Montpellier": {"dep": "34", "communes": ["Montpellier","Lattes","Castelnau-le-Lez","Juvignac"]}
}

CSP_MAP = {
    "Agriculteurs": "Agriculteurs",
    "Artisans, commerçants, chefs d'entreprise": "Artisans & Chefs d'ent.",
    "Cadres et professions intellectuelles supérieures": "Cadres & Prof. Sup.",
    "Professions intermédiaires": "Prof. Intermédiaires",
    "Employés": "Employés",
    "Ouvriers": "Ouvriers"
}

# =================================================================
# 2. LOGIQUE DE CHARGEMENT DES DONNÉES
# =================================================================
def normalize(text):
    if pd.isna(text): return ""
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("utf-8").lower().strip()

@st.cache_data
def load_and_group():
    files = {2011: "Commune_2011_2554_sect_activite.xlsx", 2016: "Commune_2016_2554_sect_activite.xlsx", 2022: "Commune_2022_2554_sect_activite.xlsx"}
    all_data = []
    for year, path in files.items():
        try:
            df = pd.read_excel(path)
            if "RR" in str(df.iloc[0, 0]): df = df.drop(0).reset_index(drop=True)
            
            c_dep = [c for c in df.columns if "DÉPARTEMENT" in str(c).upper() or "DR24" in str(c).upper()][0]
            c_lib = [c for c in df.columns if "LIBELLÉ" in str(c).upper() or "LIBELLE" in str(c).upper()][0]
            
            res = pd.DataFrame({"DEP": df[c_dep].astype(str).str.zfill(2), "LIBELLE": df[c_lib].astype(str), "ANNEE": year, "LIB_NORM": df[c_lib].apply(normalize)})
            for raw, clean in CSP_MAP.items():
                cols = [c for c in df.columns if raw in str(c)]
                res[clean] = df[cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)
            all_data.append(res)
        except Exception: continue
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

df_master = load_and_group()

# =================================================================
# 3. FILTRES DÉROULANTS (SIDEBAR)
# =================================================================
with st.sidebar:
    st.markdown("## 🔍 Paramètres d'analyse")
    st.markdown("---")
    
    sel_annee = st.selectbox("📅 Choisir l'année", sorted(df_master["ANNEE"].unique(), reverse=True))
    mode = st.selectbox("🎯 Niveau d'analyse", ["Comparatif Communes (Isère)", "Comparatif Métropoles"])
    
    df_y = df_master[df_master["ANNEE"] == sel_annee]
    
    if mode == "Comparatif Communes (Isère)":
        clist = sorted(METROPOLES_DEF["Grenoble"]["communes"])
        ent_a = st.selectbox("Commune A (Référence)", clist, index=clist.index("Grenoble"))
        ent_b = st.selectbox("Commune B (Comparaison)", clist, index=clist.index("Saint-Martin-d'Hères"))
        target_a = df_y[(df_y["DEP"] == "38") & (df_y["LIB_NORM"] == normalize(ent_a))]
        target_b = df_y[(df_y["DEP"] == "38") & (df_y["LIB_NORM"] == normalize(ent_b))]
    else:
        met_list = list(METROPOLES_DEF.keys())
        ent_a = st.selectbox("Métropole A", met_list, index=0)
        ent_b = st.selectbox("Métropole B", met_list, index=4)
        def get_agg(name):
            m = METROPOLES_DEF[name]
            return df_y[(df_y["DEP"] == m["dep"]) & (df_y["LIB_NORM"].isin([normalize(c) for c in m["communes"]]))].sum(numeric_only=True).to_frame().T
        target_a, target_b = get_agg(ent_a), get_agg(ent_b)

    st.markdown("---")
    
    # LA LISTE DÉROULANTE MULTI-SÉLECTION
    csp_options = list(CSP_MAP.values())
    sel_csp = st.multiselect(
        "📂 Catégories CSP à afficher", 
        options=csp_options, 
        default=csp_options,
        placeholder="Sélectionnez les CSP..."
    )

    # Sécurité : Arrêter le script proprement si aucune CSP n'est cochée
    if not sel_csp:
        st.warning("⚠️ Veuillez sélectionner au moins une catégorie dans la liste pour afficher les graphiques.")
        st.stop()

# =================================================================
# 4. DASHBOARD ET VISUALISATIONS COMPARATIVES
# =================================================================
if not target_a.empty and not target_b.empty:
    val_a = target_a[sel_csp].sum(axis=1).values[0]
    val_b = target_b[sel_csp].sum(axis=1).values[0]

    st.title(f"📊 {ent_a} vs {ent_b} • {sel_annee}")
    
    # --- INDICATEURS (KPIs) ---
    st.markdown("### Indicateurs Clés")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='kpi-card'><small>ACTIFS {ent_a.upper()}</small><br><b>{int(val_a):,}</b></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='kpi-card'><small>ACTIFS {ent_b.upper()}</small><br><b>{int(val_b):,}</b></div>", unsafe_allow_html=True)
    with k3:
        diff = val_a - val_b
        st.markdown(f"<div class='kpi-card' style='border-left-color:#e67e22'><small>ÉCART BRUT</small><br><b>{int(diff):+,}</b></div>", unsafe_allow_html=True)
    with k4:
        ratio = (val_a / val_b) if val_b != 0 else 0
        st.markdown(f"<div class='kpi-card' style='border-left-color:#2ecc71'><small>INDICE DE MASSE</small><br><b>{ratio:.2f}x</b></div>", unsafe_allow_html=True)

    st.divider()

    # --- GRAPHIQUES ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Distribution par CSP (Volume)")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=sel_csp, y=target_a[sel_csp].iloc[0], name=ent_a, marker_color='#3498db'))
        fig_bar.add_trace(go.Bar(x=sel_csp, y=target_b[sel_csp].iloc[0], name=ent_b, marker_color='#e67e22'))
        fig_bar.update_layout(barmode='group', template='plotly_white', height=400, margin=dict(t=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Profil Social Relatif (%)")
        pct_a = (target_a[sel_csp].iloc[0] / val_a * 100) if val_a != 0 else 0
        pct_b = (target_b[sel_csp].iloc[0] / val_b * 100) if val_b != 0 else 0
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=pct_a, theta=sel_csp, fill='toself', name=ent_a, line_color='#3498db'))
        fig_radar.add_trace(go.Scatterpolar(r=pct_b, theta=sel_csp, fill='toself', name=ent_b, line_color='#e67e22'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(max(pct_a), max(pct_b), 1)+5])), template='plotly_white', height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- ANALYSE DE SPÉCIALISATION ---
    st.subheader("🎯 Analyse de Spécialisation")
    st.info("Ce graphique montre si une ville est plus 'spécialisée' qu'une autre. Un score au-dessus de 100% signifie que la catégorie est plus présente chez A que chez B.")
    
    spec_index = (pct_a / pct_b * 100).fillna(100)
    fig_spec = px.bar(x=sel_csp, y=spec_index, labels={'x':'Catégorie', 'y':'Indice de spécificité (%)'},
                      color=spec_index, color_continuous_scale='RdYlGn')
    fig_spec.add_hline(y=100, line_dash="dash", line_color="black")
    st.plotly_chart(fig_spec, use_container_width=True)

    # --- TABLEAU DÉTAILLÉ ---
    with st.expander("📄 Voir le tableau de données complet"):
        st.write("Détails des effectifs agrégés (Emplois + Chômage) :")
        table_df = pd.DataFrame({
            "Catégorie CSP": sel_csp,
            f"{ent_a} (Effectif)": target_a[sel_csp].iloc[0].values,
            f"{ent_b} (Effectif)": target_b[sel_csp].iloc[0].values,
            "Différence": target_a[sel_csp].iloc[0].values - target_b[sel_csp].iloc[0].values
        })
        st.table(table_df.style.format(precision=0))

else:
    st.error("⚠️ Données non trouvées pour cette sélection. Veuillez vérifier les fichiers Excel.")