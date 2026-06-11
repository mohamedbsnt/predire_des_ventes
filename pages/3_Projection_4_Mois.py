import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Projection à 4 Mois", layout="wide")

st.markdown("""
<style>
.title-box {
    color: #1E88E5;
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 0.25rem;
}
.sub-box {
    color: #6b7280;
    text-align: center;
    font-size: 1rem;
    margin-bottom: 1.25rem;
}
.card-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #1E88E5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
@media (prefers-color-scheme: dark) {
    .card-box {
        background: #1e1e1e;
        color: #ffffff;
        border-left: 5px solid #00E676;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-box">📈 Projection sur 4 Mois</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-box">Générez une trajectoire prévisionnelle sur 120 jours avec une logique métier simple, lisible et interactive.</div>', unsafe_allow_html=True)

@st.cache_resource
def load_models():
    return joblib.load("rossmann_xgb_model.pkl"), joblib.load("rossmann_scaler.pkl")

model, scaler = load_models()

expected_features = None
if hasattr(model, "feature_names_in_"):
    expected_features = list(model.feature_names_in_)
elif hasattr(model, "get_booster") and model.get_booster().feature_names:
    expected_features = list(model.get_booster().feature_names)

if expected_features is None:
    st.error("Impossible de récupérer les variables attendues par le modèle.")
    st.stop()

num_features = list(getattr(scaler, "feature_names_in_", [
    "Store", "DayOfWeek", "Open", "Promo", "SchoolHoliday",
    "CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear",
    "Promo2", "Promo2SinceWeek", "Promo2SinceYear",
    "Year", "Month", "Day", "WeekOfYear", "DayOfWeekDate",
    "IsMonthStart", "IsMonthEnd"
]))

cat_cols = ["StoreType", "Assortment", "StateHoliday", "PromoInterval"]

def predict_future_sales(df_proc, model, scaler):
    df = df_proc.copy()

    if "Date" not in df.columns:
        raise ValueError("La colonne Date est obligatoire.")

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeekDate"] = df["Date"].dt.dayofweek
    df["IsMonthStart"] = df["Date"].dt.is_month_start.astype(int)
    df["IsMonthEnd"] = df["Date"].dt.is_month_end.astype(int)
    df["DayOfWeek"] = df["DayOfWeekDate"] + 1

    df_model = df.drop(columns=["Date"])

    for col in ["CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
        if col not in df_model.columns:
            df_model[col] = 0
        df_model[col] = pd.to_numeric(df_model[col], errors="coerce").fillna(0)

    for col in ["Open", "Promo", "SchoolHoliday", "Promo2"]:
        if col not in df_model.columns:
            df_model[col] = 0
        df_model[col] = pd.to_numeric(df_model[col], errors="coerce").fillna(0).astype(int)

    for col in cat_cols:
        if col not in df_model.columns:
            df_model[col] = "unknown"
        df_model[col] = df_model[col].astype(str).fillna("unknown")

    df_model = pd.get_dummies(df_model, columns=cat_cols, drop_first=True)

    for col in num_features:
        if col not in df_model.columns:
            df_model[col] = 0

    df_model[num_features] = scaler.transform(df_model[num_features])
    df_model = df_model.reindex(columns=expected_features, fill_value=0)

    preds = np.expm1(model.predict(df_model))
    preds = np.where(df["Open"] == 0, 0, preds)
    preds = np.where(preds < 0, 0, preds)
    return preds

with st.sidebar:
    st.header("⚙️ Configuration du magasin")
    store_id = st.number_input("ID Magasin", 1, 1115, 1)
    store_type = st.selectbox("Type", ["a", "b", "c", "d"])
    assortment = st.selectbox("Assortiment", ["a", "b", "c"])
    comp_distance = st.number_input("Distance concurrent", min_value=0, value=1500, step=50)
    start_date = st.date_input("Date de début de projection", datetime.today().date(), format="YYYY/MM/DD")
    horizon_days = st.slider("Horizon de projection (jours)", min_value=30, max_value=365, value=120, step=30)
    run_forecast = st.button("Lancer la projection 🚀", type="primary", use_container_width=True)

st.markdown("### 🧭 Vue rapide")
info1, info2, info3 = st.columns(3)
info1.metric("Horizon", f"{horizon_days} jours")
info2.metric("Début", str(start_date))
info3.metric("Magasin", f"{store_id}")

if run_forecast:
    with st.spinner("Génération du calendrier et calcul des prévisions..."):
        dates = pd.date_range(pd.Timestamp(start_date), periods=horizon_days, freq='D')
        df_future = pd.DataFrame({'Date': dates})

        df_future['Store'] = store_id
        df_future['StoreType'] = store_type
        df_future['Assortment'] = assortment
        df_future['CompetitionDistance'] = comp_distance
        df_future['StateHoliday'] = '0'
        df_future['SchoolHoliday'] = 0
        df_future['Promo2'] = 0
        df_future['PromoInterval'] = 'None'

        df_future['Open'] = np.where(df_future['Date'].dt.dayofweek == 6, 0, 1)
        df_future['Promo'] = np.where(df_future['Date'].dt.isocalendar().week % 2 == 0, 1, 0)
        df_future['Promo'] = np.where(df_future['Open'] == 0, 0, df_future['Promo'])

        for col in ["CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
            df_future[col] = 0

        df_future['Predicted_Sales'] = predict_future_sales(df_future, model, scaler)

    st.success("Projection générée avec succès !")

    ca_total = df_future['Predicted_Sales'].sum()
    ca_30 = df_future.iloc[:30]['Predicted_Sales'].sum()
    jours_ouverts = int(df_future['Open'].sum())
    moyenne_jour = df_future.loc[df_future['Predicted_Sales'] > 0, 'Predicted_Sales'].mean()
    moyenne_jour = 0 if pd.isna(moyenne_jour) else moyenne_jour

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CA total projeté", f"{ca_total:,.0f} €".replace(',', ' '))
    c2.metric("CA 30 premiers jours", f"{ca_30:,.0f} €".replace(',', ' '))
    c3.metric("Jours d'ouverture", f"{jours_ouverts} / {horizon_days}")
    c4.metric("Moyenne positive", f"{moyenne_jour:,.0f} €".replace(',', ' '))

    st.markdown("### 📊 Courbe prévisionnelle des ventes")
    chart_data = df_future[['Date', 'Predicted_Sales']].copy()
    fig = px.line(
        chart_data,
        x='Date',
        y='Predicted_Sales',
        markers=True,
        title='Projection des ventes sur la période',
        template='plotly_white'
    )
    fig.update_layout(xaxis_title='Date', yaxis_title='Ventes prévues (€)', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🧐 Comment lire la courbe ?"):
        st.write("- Les pics correspondent aux périodes de promotion simulée.")
        st.write("- Les valeurs à zéro représentent les dimanches, définis comme jours fermés.")
        st.write("- La trajectoire montre l'effet combiné du calendrier, de l'ouverture et de la promotion.")

    st.markdown("### 📑 Données de projection")
    view = df_future[['Date', 'Open', 'Promo', 'Predicted_Sales']].copy()
    view['Date'] = view['Date'].dt.date
    st.dataframe(view, use_container_width=True)