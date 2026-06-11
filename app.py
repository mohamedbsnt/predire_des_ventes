import streamlit as st

st.set_page_config(
    page_title="Rossmann Analytics",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.hero-title {
    font-size: 4.3rem;
    font-weight: 900;
    background: linear-gradient(45deg, #1E88E5, #00E676);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.4rem;
    margin-top: 1rem;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.3rem;
    color: #7f8c8d;
    margin-bottom: 2rem;
}
.hero-banner {
    background: linear-gradient(135deg, rgba(30,136,229,0.10), rgba(0,230,118,0.10));
    border-radius: 20px;
    padding: 1.2rem 1rem;
    border: 1px solid rgba(30,136,229,0.15);
    margin-bottom: 1.5rem;
}
.feature-card {
    background-color: #f8f9fa;
    padding: 1.6rem;
    border-radius: 14px;
    border-left: 6px solid #1E88E5;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    height: 100%;
    transition: transform 0.2s ease-in-out;
}
.feature-card:hover {
    transform: translateY(-4px);
}
.feature-card h3 {
    margin-top: 0;
    margin-bottom: 0.6rem;
}
.feature-card p {
    margin-bottom: 0.5rem;
}
.stat-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
@media (prefers-color-scheme: dark) {
    .feature-card {
        background-color: #1e1e1e;
        border-left: 6px solid #00E676;
        color: #ffffff;
    }
    .hero-subtitle {
        color: #b0b0b0;
    }
    .stat-box {
        background: #111827;
        border-color: #374151;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-banner">', unsafe_allow_html=True)
st.markdown('<p class="hero-title">Rossmann Analytics 🏪</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Plateforme d\'Intelligence Artificielle pour la Prévision des Ventes</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### 📊 Vue globale du projet")
metric_cols = st.columns(4, gap="small")
metric_cols[0].metric("Magasins gérés", "1 115", "7 pays")
metric_cols[1].metric("Modèle principal", "XGBoost", "Gradient Boosting")
metric_cols[2].metric("Série temporelle", "Prophet", "Projection future")
metric_cols[3].metric("Inférence", "< 0.1 s", "Rapide")

st.markdown("---")

left, right = st.columns([1.3, 1], gap="large")

with left:
    st.markdown("### 🚀 Découvrez les outils")
    st.write("Naviguez via le menu latéral pour accéder aux différents modules de l'application.")

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Simulateur unitaire</h3>
            <p>Ajustez les paramètres d'un magasin précis et observez l'impact immédiat sur le chiffre d'affaires.</p>
            <p><i>Idéal pour : responsables de magasins et marketing.</i></p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
            <h3>📂 Analyse par lot</h3>
            <p>Importez un fichier CSV, lancez les prédictions massives et exportez les résultats.</p>
            <p><i>Idéal pour : analystes de données.</i></p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
            <h3>📈 Projection future</h3>
            <p>Générez un calendrier prévisionnel sur 120 jours et visualisez la tendance des ventes.</p>
            <p><i>Idéal pour : directeurs régionaux.</i></p>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown("### 🧠 Résultats obtenus")
    st.markdown("""
    <div class="stat-box">
        <p><strong>• Analyse historique</strong> : compréhension des ventes par magasin, date, promotion et ouverture.</p>
        <p><strong>• Modélisation</strong> : comparaison entre XGBoost et Prophet pour mieux gérer précision et projection.</p>
        <p><strong>• Visualisation</strong> : graphiques interactifs pour lire les prévisions et leur incertitude.</p>
        <p><strong>• Export</strong> : génération de fichiers CSV exploitables pour l'analyse métier.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.info("Cette vue d'accueil résume le projet et donne accès aux pages principales.")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Architecture", "Méthode", "Utilisation"])

with tab1:
    st.write("L'application est organisée en plusieurs pages Streamlit reliées au projet Rossmann.")
    st.write("Chaque module remplit une fonction précise : simuler, prédire par lot, projeter dans le futur.")

with tab2:
    st.write("Les données sont nettoyées, enrichies et envoyées au modèle avant l'affichage des résultats.")
    st.write("Le projet combine apprentissage supervisé et série temporelle pour une vision plus complète.")

with tab3:
    st.write("Utilisez la barre latérale pour naviguer entre les pages et lancer les prédictions.")
    st.write("Les résultats peuvent ensuite être analysés dans les tableaux, KPI et graphiques du dashboard.")

st.markdown("---")

with st.expander("ℹ️ Comment fonctionne l'intelligence artificielle en arrière-plan ?"):
    st.write("""
**Pipeline technique :**
1. Les données historiques sont chargées et préparées.
2. Les variables temporelles et commerciales sont nettoyées et transformées.
3. Le modèle XGBoost chargé depuis un fichier `.pkl` réalise l'inférence.
4. Les pages de l'application affichent les résultats sous forme de tableau et de graphiques.
""")