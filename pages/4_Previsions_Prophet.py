import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from prophet import Prophet
import os

st.set_page_config(page_title="Forecasting Prophet", layout="wide")

st.markdown("""
<style>
.title-text {
    color: #1E88E5;
    font-size: 2.6rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 0.5rem;
}
.subtitle-text {
    text-align: center;
    font-size: 1.05rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
}
.card-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #1E88E5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">🔮 Prédiction du Futur avec Meta Prophet</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Prévision des ventes futures à partir de l’historique d’un magasin précis.</div>', unsafe_allow_html=True)

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

with st.sidebar:
    st.header("⚙️ Paramètres de prévision")
    store_id = st.number_input("Sélectionner un magasin", 1, 1115, 1)
    horizon = st.slider("Horizon futur (jours)", 30, 365, 120, 30)
    run_prophet = st.button("Générer le futur 🚀", type="primary", use_container_width=True)

if run_prophet:
    with st.spinner("Analyse du passé..."):
        df_store = df_train[df_train['Store'] == store_id].copy()
        df_prophet = df_store[['Date', 'Sales']].rename(columns={'Date': 'ds', 'Sales': 'y'})
        df_prophet = df_prophet.sort_values('ds').dropna()

    if df_prophet.empty:
        st.warning("Aucune donnée disponible pour ce magasin.")
        st.stop()

    with st.spinner("Calcul des tendances futures (Prophet)..."):
        m = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        m.fit(df_prophet)

    with st.spinner(f"Projection sur les {horizon} prochains jours..."):
        future = m.make_future_dataframe(periods=horizon, freq='D')
        forecast = m.predict(future)

        forecast[['yhat', 'yhat_lower', 'yhat_upper']] = forecast[['yhat', 'yhat_lower', 'yhat_upper']].clip(lower=0)
        forecast_future_only = forecast.tail(horizon).copy()

    st.success("✅ Prévisions calculées avec succès !")

    total_ca = forecast_future_only['yhat'].sum()
    avg_ca = forecast_future_only['yhat'].mean()
    max_ca = forecast_future_only['yhat'].max()

    c1, c2, c3 = st.columns(3)
    c1.metric("CA total projeté", f"{total_ca:,.0f} €".replace(",", " "))
    c2.metric("Moyenne/jour", f"{avg_ca:,.0f} €".replace(",", " "))
    c3.metric("Pic prévu", f"{max_ca:,.0f} €".replace(",", " "))

    st.markdown("### 📈 Chiffre d'affaires projeté")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=forecast_future_only['ds'].tolist() + forecast_future_only['ds'].tolist()[::-1],
        y=forecast_future_only['yhat_upper'].tolist() + forecast_future_only['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0, 176, 246, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name="Marge d'incertitude"
    ))

    fig.add_trace(go.Scatter(
        x=forecast_future_only['ds'],
        y=forecast_future_only['yhat'],
        mode='lines+markers',
        line=dict(color='#1E88E5', width=3),
        marker=dict(size=4),
        name='Ventes prévues',
        hovertemplate='Date: %{x}<br>Ventes: %{y:,.0f} €<extra></extra>'
    ))

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Chiffre d'Affaires (€)",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor='lightgray'),
        xaxis=dict(showgrid=True, gridcolor='lightgray')
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🧐 Comment lire ce graphique ?"):
        st.write("- La ligne bleue représente la prévision centrale calculée par Prophet.")
        st.write("- La zone bleue claire représente l’incertitude autour de cette prévision.")
        st.write("- Les variations suivent les tendances hebdomadaires et saisonnières apprises par le modèle.")

    st.markdown("### 📑 Données de projection")

    df_display = forecast_future_only[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    df_display.columns = ['Date', 'Ventes Prévues', 'Pessimiste', 'Optimiste']
    df_display['Date'] = df_display['Date'].dt.date

    for col in ['Ventes Prévues', 'Pessimiste', 'Optimiste']:
        df_display[col] = df_display[col].round(0).astype(int)

    st.dataframe(df_display, use_container_width=True)

    st.markdown("### 🧩 Résumé des résultats")
    st.write(
        "Cette page montre comment Prophet transforme l’historique d’un magasin en projection future. "
        "Le graphique met en évidence la tendance prévue, tandis que le tableau permet de lire les valeurs jour par jour."
    )