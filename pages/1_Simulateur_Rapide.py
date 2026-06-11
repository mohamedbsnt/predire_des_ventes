import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Simulateur", layout="wide")

@st.cache_resource
def load_models():
    return joblib.load("rossmann_xgb_model.pkl"), joblib.load("rossmann_scaler.pkl")

model, scaler = load_models()

def predict_sales_single(df, model, scaler):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"], df["Month"], df["Day"] = df["Date"].dt.year, df["Date"].dt.month, df["Date"].dt.day
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeekDate"] = df["Date"].dt.dayofweek
    df["IsMonthStart"], df["IsMonthEnd"] = df["Date"].dt.is_month_start.astype(int), df["Date"].dt.is_month_end.astype(int)
    df = df.drop(columns=["Date"])
    df["DayOfWeek"] = df["DayOfWeekDate"] + 1

    for col in ["CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
        df[col] = df[col].fillna(0)

    cat_cols = ["StoreType", "Assortment", "StateHoliday", "PromoInterval"]
    for col in cat_cols: df[col] = df[col].astype(str)

    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    df = df.reindex(columns=model.get_booster().feature_names, fill_value=0)
    
    num_cols = scaler.feature_names_in_ if hasattr(scaler, 'feature_names_in_') else ["Store", "DayOfWeek", "Open", "Promo", "SchoolHoliday", "CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2", "Promo2SinceWeek", "Promo2SinceYear", "Year", "Month", "Day", "WeekOfYear", "DayOfWeekDate", "IsMonthStart", "IsMonthEnd"]
    df[num_cols] = scaler.transform(df[num_cols])
    return np.expm1(model.predict(df))[0]

st.title("🎯 Simulateur de Ventes")
st.markdown("Ajustez les paramètres ci-dessous pour lancer une simulation prédictive.")

with st.form("simulation_form"):
    st.subheader("1. Paramètres Principaux")
    col1, col2, col3 = st.columns(3)
    with col1:
        store_id = st.number_input("ID Magasin", value=1, min_value=1)
        date_input = st.date_input("Date ciblée")
    with col2:
        open_store = st.toggle("Magasin Ouvert", value=True)
        promo = st.toggle("Promotion active ce jour", value=False)
    with col3:
        store_type = st.selectbox("Type de magasin", ["a", "b", "c", "d"])
        assortment = st.selectbox("Assortiment", ["a", "b", "c"])

    # On cache les paramètres avancés dans un "Expander" pour une UI plus propre
    with st.expander("⚙️ Paramètres Avancés (Concurrence, Vacances...)"):
        ca1, ca2, ca3 = st.columns(3)
        with ca1:
            state_holiday = st.selectbox("Jour férié", ["0", "a", "b", "c"])
            school_holiday = st.checkbox("Vacances scolaires")
        with ca2:
            promo2 = st.toggle("Promo2 (Longue durée)", value=False)
            promo_interval = st.selectbox("Cycle Promo2", ["None", "Jan,Apr,Jul,Oct", "Feb,May,Aug,Nov", "Mar,Jun,Sept,Dec"])
            promo2_week = st.number_input("Semaine début Promo2", 0, 52, 0)
            promo2_year = st.number_input("Année début Promo2", 0, 2030, 0)
        with ca3:
            comp_distance = st.number_input("Distance concurrent (m)", value=1500.0)
            comp_month = st.number_input("Mois ouv. concurrent", 0, 12, 0)
            comp_year = st.number_input("Année ouv. concurrent", 0, 2030, 0)

    st.write("")
    submitted = st.form_submit_button("Lancer l'inférence XGBoost 🚀", type="primary", use_container_width=True)

if submitted:
    if not open_store:
        st.error("Le magasin est fermé ce jour-là.")
        st.metric("Estimation des Ventes", "0.00 €")
    else:
        df_in = pd.DataFrame([{
            "Store": store_id, "Date": date_input, "Open": 1, "Promo": int(promo), 
            "StateHoliday": state_holiday, "SchoolHoliday": int(school_holiday), 
            "StoreType": store_type, "Assortment": assortment, "CompetitionDistance": comp_distance,
            "CompetitionOpenSinceMonth": comp_month, "CompetitionOpenSinceYear": comp_year,
            "Promo2": int(promo2), "Promo2SinceWeek": promo2_week, "Promo2SinceYear": promo2_year, 
            "PromoInterval": promo_interval
        }])
        
        with st.spinner("Analyse statistique en cours..."):
            result = predict_sales_single(df_in, model, scaler)
            
        st.success("✅ Calcul terminé avec succès !")
        
        # Affichage stylisé du résultat
        res_col1, res_col2 = st.columns([1, 1])
        with res_col1:
            st.metric("Chiffre d'Affaires Estimé", f"{result:,.2f} €".replace(",", " "))
        with res_col2:
            if promo:
                st.info("💡 L'algorithme a pris en compte l'effet booster de la promotion active.")
            if school_holiday:
                st.warning("🎒 Période de vacances scolaires détectée.")