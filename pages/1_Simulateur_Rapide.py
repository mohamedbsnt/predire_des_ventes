import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Simulateur", layout="wide")

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

st.markdown('<div class="title-box">🎯 Simulateur de Ventes</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-box">Ajustez les paramètres du magasin et lancez une estimation instantanée du chiffre d’affaires.</div>', unsafe_allow_html=True)

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

def predict_sales_single(df, model, scaler):
    df = df.copy()

    if "Date" not in df.columns:
        raise ValueError("La colonne Date est obligatoire.")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if df["Date"].isna().any():
        raise ValueError("La date saisie est invalide.")

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeekDate"] = df["Date"].dt.dayofweek
    df["IsMonthStart"] = df["Date"].dt.is_month_start.astype(int)
    df["IsMonthEnd"] = df["Date"].dt.is_month_end.astype(int)
    df["DayOfWeek"] = df["DayOfWeekDate"] + 1
    df = df.drop(columns=["Date"])

    for col in ["CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["Open", "Promo", "SchoolHoliday", "Promo2"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in cat_cols:
        if col not in df.columns:
            df[col] = "unknown"
        df[col] = df[col].astype(str).fillna("unknown")

    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    for col in num_features:
        if col not in df.columns:
            df[col] = 0

    df[num_features] = scaler.transform(df[num_features])
    df = df.reindex(columns=expected_features, fill_value=0)

    pred = np.expm1(model.predict(df))[0]
    return float(max(pred, 0))

st.markdown("### 🧾 Paramètres de simulation")
with st.form("simulation_form"):
    st.subheader("1. Paramètres principaux")
    col1, col2, col3 = st.columns(3)
    with col1:
        store_id = st.number_input("ID Magasin", min_value=1, max_value=1115, value=1)
        date_input = st.date_input("Date ciblée")
    with col2:
        open_store = st.toggle("Magasin ouvert", value=True)
        promo = st.toggle("Promotion active ce jour", value=False)
    with col3:
        store_type = st.selectbox("Type de magasin", ["a", "b", "c", "d"])
        assortment = st.selectbox("Assortiment", ["a", "b", "c"])

    with st.expander("⚙️ Paramètres avancés", expanded=False):
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            state_holiday = st.selectbox("Jour férié", ["0", "a", "b", "c"])
            school_holiday = st.checkbox("Vacances scolaires")
        with ca2:
            promo2 = st.toggle("Promo2 (longue durée)", value=False)
            promo_interval = st.selectbox("Cycle Promo2", ["None", "Jan,Apr,Jul,Oct", "Feb,May,Aug,Nov", "Mar,Jun,Sep,Dec"])
            promo2_week = st.number_input("Semaine début Promo2", min_value=0, max_value=52, value=0)
            promo2_year = st.number_input("Année début Promo2", min_value=0, max_value=2030, value=0)
        with ca3:
            comp_distance = st.number_input("Distance concurrent (m)", min_value=0.0, value=1500.0, step=50.0)
            comp_month = st.number_input("Mois ouverture concurrent", min_value=0, max_value=12, value=0)
            comp_year = st.number_input("Année ouverture concurrent", min_value=0, max_value=2030, value=0)

    submitted = st.form_submit_button("Lancer l'inférence XGBoost 🚀", type="primary", use_container_width=True)

if submitted:
    if not open_store:
        st.error("Le magasin est fermé ce jour-là.")
        st.metric("Estimation des ventes", "0.00 €")
    else:
        df_in = pd.DataFrame([{
            "Store": store_id,
            "Date": date_input,
            "Open": 1,
            "Promo": int(promo),
            "StateHoliday": state_holiday,
            "SchoolHoliday": int(school_holiday),
            "StoreType": store_type,
            "Assortment": assortment,
            "CompetitionDistance": comp_distance,
            "CompetitionOpenSinceMonth": comp_month,
            "CompetitionOpenSinceYear": comp_year,
            "Promo2": int(promo2),
            "Promo2SinceWeek": promo2_week,
            "Promo2SinceYear": promo2_year,
            "PromoInterval": promo_interval
        }])

        with st.spinner("Analyse statistique en cours..."):
            try:
                result = predict_sales_single(df_in, model, scaler)
            except Exception as e:
                st.error(f"Erreur pendant la prédiction : {e}")
                st.stop()

        st.success("✅ Calcul terminé avec succès !")

        res_col1, res_col2 = st.columns([1, 1])
        with res_col1:
            st.metric("Chiffre d'affaires estimé", f"{result:,.2f} €".replace(",", " "))
        with res_col2:
            st.markdown("### 🧠 Lecture rapide")
            if promo:
                st.info("La promotion active a été prise en compte par le modèle.")
            else:
                st.write("Aucune promotion active n'a été activée.")
            if school_holiday:
                st.warning("Vacances scolaires détectées.")
            if promo2:
                st.write("Promo2 activée avec cycle long.")