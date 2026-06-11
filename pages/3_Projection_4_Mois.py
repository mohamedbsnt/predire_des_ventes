import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

st.set_page_config(page_title="Projection à 4 Mois", layout="wide")

# --- CHARGEMENT DU MODÈLE ---
@st.cache_resource
def load_models():
    return joblib.load("rossmann_xgb_model.pkl"), joblib.load("rossmann_scaler.pkl")

model, scaler = load_models()

# --- FONCTION DE PRÉDICTION BATCH ---
def predict_future_sales(df_proc, model, scaler):
    df = df_proc.copy()
    
    # 1. Extraction des variables temporelles
    df["Year"], df["Month"], df["Day"] = df["Date"].dt.year, df["Date"].dt.month, df["Date"].dt.day
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeekDate"] = df["Date"].dt.dayofweek
    df["IsMonthStart"] = df["Date"].dt.is_month_start.astype(int)
    df["IsMonthEnd"] = df["Date"].dt.is_month_end.astype(int)
    df["DayOfWeek"] = df["DayOfWeekDate"] + 1
    
    # 2. Suppression de la vraie date pour XGBoost
    df_model = df.drop(columns=["Date"])

    # 3. Valeurs par défaut
    for col in ["CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
        if col not in df_model.columns: df_model[col] = 0

    # 4. Encodage One-Hot
    cat_cols = ["StoreType", "Assortment", "StateHoliday", "PromoInterval"]
    for col in cat_cols:
        df_model[col] = df_model[col].astype(str)

    df_model = pd.get_dummies(df_model, columns=cat_cols, drop_first=True)
    df_model = df_model.reindex(columns=model.get_booster().feature_names, fill_value=0)
    
    # 5. Scaler
    num_cols = scaler.feature_names_in_ if hasattr(scaler, 'feature_names_in_') else ["Store", "DayOfWeek", "Open", "Promo", "SchoolHoliday", "CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2", "Promo2SinceWeek", "Promo2SinceYear", "Year", "Month", "Day", "WeekOfYear", "DayOfWeekDate", "IsMonthStart", "IsMonthEnd"]
    df_model[num_cols] = scaler.transform(df_model[num_cols])

    # 6. Inférence
    preds = np.expm1(model.predict(df_model))
    
    # Si le magasin est fermé (ex: dimanche), on force à 0
    preds = np.where(df['Open'] == 0, 0, preds)
    return preds

# --- INTERFACE UTILISATEUR ---
st.title("📈 Projection sur 4 Mois (Forecasting)")
st.markdown("""
Générez un calendrier virtuel sur les **120 prochains jours** pour estimer la trajectoire du chiffre d'affaires. 
Le système va automatiquement fermer le magasin les dimanches et simuler une alternance de promotions.
""")

with st.sidebar:
    st.header("⚙️ Configuration du Magasin")
    store_id = st.number_input("ID Magasin", 1, 1115, 1)
    store_type = st.selectbox("Type", ["a", "b", "c", "d"])
    assortment = st.selectbox("Assortiment", ["a", "b", "c"])
    comp_distance = st.number_input("Distance Concurrent", value=1500)
    start_date = st.date_input("Date de début de projection", datetime.today())
    run_forecast = st.button("Lancer la Projection 🚀", type="primary", use_container_width=True)

if run_forecast:
    with st.spinner("Génération du calendrier et calcul des séries temporelles..."):
        
        # 1. Création des 120 jours futurs
        dates = pd.date_range(start_date, periods=120, freq='D')
        df_future = pd.DataFrame({'Date': dates})
        
        # 2. Remplissage des variables statiques du magasin
        df_future['Store'] = store_id
        df_future['StoreType'] = store_type
        df_future['Assortment'] = assortment
        df_future['CompetitionDistance'] = comp_distance
        df_future['StateHoliday'] = "0"
        df_future['SchoolHoliday'] = 0
        df_future['Promo2'] = 0
        df_future['PromoInterval'] = "None"
        
        # 3. Remplissage logique (Règles métiers)
        # On ferme le magasin le dimanche (DayOfWeek == 6 car 0=Lundi)
        df_future['Open'] = np.where(df_future['Date'].dt.dayofweek == 6, 0, 1)
        
        # On simule une promotion 1 semaine sur 2
        df_future['Promo'] = np.where(df_future['Date'].dt.isocalendar().week % 2 == 0, 1, 0)
        # On désactive la promo le dimanche de toute façon
        df_future['Promo'] = np.where(df_future['Open'] == 0, 0, df_future['Promo'])
        
        # 4. Inférence avec le modèle
        df_future['Predicted_Sales'] = predict_future_sales(df_future, model, scaler)
        
    st.success("Projection générée avec succès !")
    
    # --- KPI GLOBAUX ---
    ca_total = df_future['Predicted_Sales'].sum()
    mois_1 = df_future.iloc[0:30]['Predicted_Sales'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("CA Total Projeté (4 mois)", f"{ca_total:,.0f} €".replace(",", " "))
    c2.metric("CA 30 Premiers Jours", f"{mois_1:,.0f} €".replace(",", " "))
    
    jours_ouverts = df_future[df_future['Open'] == 1].shape[0]
    c3.metric("Jours d'ouverture", f"{jours_ouverts} / 120")
    
    st.markdown("---")
    
    # --- GRAPHIQUE TIME SERIES ---
    st.markdown("### 📊 Courbe Prévisionnelle des Ventes")
    
    # Préparation des données pour st.line_chart
    chart_data = df_future[['Date', 'Predicted_Sales']].set_index('Date')
    
    # Affichage du graphique interactif natif de Streamlit
    st.line_chart(chart_data, height=400, color="#00E676")
    
    with st.expander("🧐 Analyse visuelle : Pourquoi ces pics et ces creux ?"):
        st.write("- **Les pics hauts** correspondent généralement aux semaines où la promotion simulée est active (Promo = 1).")
        st.write("- **Les chutes à 0** sont les dimanches, jours où le modèle a forcé l'état 'Fermé'.")
        
    # --- EXPORTATION ---
    st.markdown("### 📑 Données brutes de la projection")
    st.dataframe(df_future[['Date', 'Open', 'Promo', 'Predicted_Sales']].head(15), use_container_width=True)