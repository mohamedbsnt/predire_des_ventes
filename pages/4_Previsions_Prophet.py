import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
import os

st.set_page_config(page_title="Forecasting Prophet", layout="wide")

st.markdown("""
<style>
    .title-text { color: #1E88E5; font-size: 2.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title-text">🔮 Prédiction du Futur avec Meta Prophet</p>', unsafe_allow_html=True)
st.write("Ce module isole l'historique et génère un graphique interactif **strictement focalisé sur l'avenir**.")

# ==========================================
# 1. CHARGEMENT DE L'HISTORIQUE (TRAIN.CSV)
# ==========================================
@st.cache_data
def load_historical_data():
    file_path = "train.csv"
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path, usecols=['Store', 'Date', 'Sales', 'Open'])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df_train = load_historical_data()

if df_train is None:
    st.error("❌ Fichier `train.csv` introuvable. Placez-le à la racine du projet.")
    st.stop()

# ==========================================
# 2. CONFIGURATION UI
# ==========================================
with st.sidebar:
    st.header("⚙️ Paramètres de Prévision")
    store_id = st.number_input("Sélectionner un Magasin", 1, 1115, 1)
    horizon = st.slider("Horizon de prédiction du futur (Jours)", min_value=30, max_value=365, value=120, step=30)
    run_prophet = st.button("Générer le Futur 🚀", type="primary", use_container_width=True)

# ==========================================
# 3. ENTRAÎNEMENT & PRÉDICTION
# ==========================================
if run_prophet:
    with st.spinner("Analyse du passé..."):
        df_store = df_train[df_train['Store'] == store_id].copy()
        df_prophet = df_store[['Date', 'Sales']].rename(columns={'Date': 'ds', 'Sales': 'y'})
        df_prophet = df_prophet.sort_values('ds')
        
    with st.spinner("Calcul des tendances futures (Prophet)..."):
        m = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        m.fit(df_prophet)
        
    with st.spinner(f"Projection sur les {horizon} prochains jours..."):
        # make_future_dataframe génère (Passé + Futur)
        future = m.make_future_dataframe(periods=horizon, freq='D')
        forecast = m.predict(future)
        
        # On empêche les valeurs négatives
        forecast['yhat'] = np.where(forecast['yhat'] < 0, 0, forecast['yhat'])
        forecast['yhat_lower'] = np.where(forecast['yhat_lower'] < 0, 0, forecast['yhat_lower'])
        
        # 🎯 FILTRE CRUCIAL : On ne garde QUE LE FUTUR
        # forecast a (historique + horizon), on prend juste les (horizon) dernières lignes
        forecast_future_only = forecast.tail(horizon).copy()
    
    st.success("✅ Prévisions calculées avec succès !")
    
    # ==========================================
    # 4. GRAPHIQUE INTERACTIF (PLOTLY) - FUTUR UNIQUEMENT
    # ==========================================
    st.markdown(f"### 📈 Chiffre d'Affaires Projeté (Prochains {horizon} jours)")
    
    # Création du graphique Plotly
    fig = go.Figure()

    # Zone de confiance (Bande bleu clair)
    fig.add_trace(go.Scatter(
        x=forecast_future_only['ds'].tolist() + forecast_future_only['ds'].tolist()[::-1],
        y=forecast_future_only['yhat_upper'].tolist() + forecast_future_only['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0, 176, 246, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='Marge d\'incertitude'
    ))

    # Ligne principale de prédiction (Ligne bleue épaisse)
    fig.add_trace(go.Scatter(
        x=forecast_future_only['ds'],
        y=forecast_future_only['yhat'],
        mode='lines+markers',
        line=dict(color='#1E88E5', width=3),
        marker=dict(size=4),
        name='Ventes Prévues',
        hovertemplate='Date: %{x}<br>Ventes: %{y:,.0f} €<extra></extra>'
    ))

    # Mise en forme du graphique
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Chiffre d'Affaires (€)",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=True, gridcolor='lightgray')),
        xaxis=(dict(showgrid=True, gridcolor='lightgray'))
    )

    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🧐 Comment lire ce graphique ?"):
        st.write("- **La ligne bleue** représente la prédiction exacte calculée par l'algorithme.")
        st.write("- **La zone ombrée** représente l'intervalle de confiance (Prophet estime que les ventes réelles ont 80% de chances de tomber dans cette zone).")
        st.write("- Les chutes brutales à zéro représentent les dimanches (jours de fermeture appris par le modèle).")

    # ==========================================
    # 5. TABLEAU DE DONNÉES DU FUTUR
    # ==========================================
    st.markdown("### 📑 Données de projection")
    
    # Formatage propre du tableau pour l'utilisateur
    df_display = forecast_future_only[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    df_display.columns = ['Date', 'Ventes Prévues', 'Pessimiste', 'Optimiste']
    df_display['Date'] = df_display['Date'].dt.date
    
    # Arrondir à l'entier
    for col in ['Ventes Prévues', 'Pessimiste', 'Optimiste']:
        df_display[col] = df_display[col].round(0).astype(int)
        
    st.dataframe(df_display, use_container_width=True)