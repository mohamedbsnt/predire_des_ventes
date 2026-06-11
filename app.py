import streamlit as st

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
# st.set_page_config doit toujours être la TOUTE PREMIÈRE ligne de Streamlit
st.set_page_config(
    page_title="Rossmann Analytics",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INJECTION DU CSS PERSONNALISÉ
# ==========================================
st.markdown("""
<style>
    /* Style pour le grand titre */
    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #1E88E5, #00E676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
    
    /* Style pour le sous-titre */
    .hero-subtitle {
        text-align: center;
        font-size: 1.5rem;
        color: #7f8c8d;
        margin-bottom: 3rem;
    }
    
    /* Style pour les "Cartes" de fonctionnalité */
    .feature-card {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        border-left: 6px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 100%;
        transition: transform 0.2s ease-in-out;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    /* Support du mode sombre pour les cartes */
    @media (prefers-color-scheme: dark) {
        .feature-card {
            background-color: #1e1e1e;
            border-left: 6px solid #00E676;
            color: #ffffff;
        }
        .hero-subtitle {
            color: #b0b0b0;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. EN-TÊTE (HERO BANNER)
# ==========================================
st.markdown('<p class="hero-title">Rossmann Analytics 🏪</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Plateforme d\'Intelligence Artificielle pour la Prévision des Ventes</p>', unsafe_allow_html=True)

st.write("---")

# ==========================================
# 4. KPI GLOBAUX DU PROJET
# ==========================================
st.markdown("### 📊 Chiffres Clés du Projet")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Magasins gérés", value="1 115", delta="Dans 7 pays")
col2.metric(label="Modèle", value="XGBoost", delta="Gradient Boosting", delta_color="off")
col3.metric(label="Précision (RMSE)", value="Excellente", delta="Validation")
col4.metric(label="Temps d'inférence", value="< 0.1s", delta="Ultra-rapide", delta_color="inverse")

st.write("---")

# ==========================================
# 5. PRÉSENTATION DES MODULES (CARTES)
# ==========================================
st.markdown("### 🚀 Découvrez nos outils de prédiction")
st.write("Naviguez via le menu latéral à gauche (dossier `pages/`) pour accéder aux différents modules de l'application.")
st.write("") # Petit espacement

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Simulateur Unitaire</h3>
        <p>Ajustez les paramètres d'un magasin précis (date, promotions, vacances, concurrence) et observez l'impact immédiat sur le chiffre d'affaires.</p>
        <br>
        <i>Idéal pour : Responsables de magasins et Marketing.</i>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown("""
    <div class="feature-card">
        <h3>📂 Analyse par Lot</h3>
        <p>Uploadez un fichier CSV (ex: test.csv) de plusieurs milliers de lignes. Le modèle prédira l'ensemble des ventes instantanément avec possibilité d'exporter les résultats.</p>
        <br>
        <i>Idéal pour : Analystes de données (Data Analysts).</i>
    </div>
    """, unsafe_allow_html=True)

with colC:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Projection sur 4 mois</h3>
        <p>Générez automatiquement un calendrier prévisionnel des 120 prochains jours pour observer la tendance des ventes via un graphique temporel complet.</p>
        <br>
        <i>Idéal pour : Directeurs Régionaux (Forecasting).</i>
    </div>
    """, unsafe_allow_html=True)

st.write("<br><br>", unsafe_allow_html=True)

# ==========================================
# 6. EXPLICATIONS TECHNIQUES
# ==========================================
with st.expander("ℹ️ Comment fonctionne l'Intelligence Artificielle en arrière-plan ?"):
    st.write("""
    **Pipeline Technique :**
    1. **Les données :** Historiques fournis par Rossmann (magasins, promotions, distances des concurrents...).
    2. **Le nettoyage :** Imputation des valeurs manquantes, création de variables temporelles (semaine, jour de la semaine...).
    3. **L'entraînement :** Le modèle **XGBoost Regressor** (eXtreme Gradient Boosting) a été entraîné pour trouver les corrélations mathématiques.
    4. **La prédiction :** Les pages de cette application chargent le modèle (`.pkl`) pour réaliser de l'inférence statistique locale sans jamais avoir à ré-entraîner l'algorithme.
    """)