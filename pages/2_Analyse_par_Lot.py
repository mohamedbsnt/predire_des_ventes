import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Analyse par Lot", layout="wide")

@st.cache_resource
def load_models():
    return joblib.load("rossmann_xgb_model.pkl"), joblib.load("rossmann_scaler.pkl")

model, scaler = load_models()

def predict_sales_batch(df, model, scaler):
    df_proc = df.copy()
    df_proc["Date"] = pd.to_datetime(df_proc["Date"])
    df_proc["Year"], df_proc["Month"], df_proc["Day"] = df_proc["Date"].dt.year, df_proc["Date"].dt.month, df_proc["Date"].dt.day
    df_proc["WeekOfYear"] = df_proc["Date"].dt.isocalendar().week.astype(int)
    df_proc["DayOfWeekDate"] = df_proc["Date"].dt.dayofweek
    df_proc["IsMonthStart"], df_proc["IsMonthEnd"] = df_proc["Date"].dt.is_month_start.astype(int), df_proc["Date"].dt.is_month_end.astype(int)
    df_proc = df_proc.drop(columns=["Date"])
    
    if "DayOfWeek" not in df_proc.columns: df_proc["DayOfWeek"] = df_proc["DayOfWeekDate"] + 1
    for col in ["CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
        if col in df_proc.columns: df_proc[col] = df_proc[col].fillna(0)

    cat_cols = ["StoreType", "Assortment", "StateHoliday", "PromoInterval"]
    for col in cat_cols:
        if col in df_proc.columns: df_proc[col] = df_proc[col].astype(str)

    df_proc = pd.get_dummies(df_proc, columns=[c for c in cat_cols if c in df_proc.columns], drop_first=True)
    df_proc = df_proc.reindex(columns=model.get_booster().feature_names, fill_value=0)
    
    num_cols = scaler.feature_names_in_ if hasattr(scaler, 'feature_names_in_') else ["Store", "DayOfWeek", "Open", "Promo", "SchoolHoliday", "CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2", "Promo2SinceWeek", "Promo2SinceYear", "Year", "Month", "Day", "WeekOfYear", "DayOfWeekDate", "IsMonthStart", "IsMonthEnd"]
    df_proc[num_cols] = scaler.transform(df_proc[num_cols])

    return np.expm1(model.predict(df_proc))

st.title("📂 Inférence Statistique sur Fichier (Batch)")
st.markdown("Importez vos données d'exploitation (ex: `test.csv`) pour obtenir des prévisions et une visualisation globale.")

uploaded_file = st.file_uploader("Glissez votre fichier CSV ici", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, dtype={'StateHoliday': str})
    
    with st.expander("👁️ Voir un aperçu des données importées"):
        st.dataframe(df_raw.head(), use_container_width=True)
    
    if st.button("Lancer les Prédictions Massives 🧠", type="primary"):
        with st.spinner("Modélisation en cours... Cela peut prendre quelques secondes."):
            preds = predict_sales_batch(df_raw, model, scaler)
            
            if 'Open' in df_raw.columns:
                preds = np.where(df_raw['Open'] == 0, 0, preds)
                
            df_result = df_raw.copy()
            df_result['Predicted_Sales'] = np.round(preds, 2)
            
        st.success("✅ Modélisation terminée !")
        
        # --- DASHBOARD VISUEL ---
        st.markdown("### 📊 Synthèse des Prévisions")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CA Total Projeté", f"{df_result['Predicted_Sales'].sum():,.0f} €".replace(",", " "))
        c2.metric("Moyenne par Magasin/Jour", f"{df_result[df_result['Predicted_Sales']>0]['Predicted_Sales'].mean():,.0f} €".replace(",", " "))
        
        jours_ouverts = len(df_result[df_result.get('Open', 1) == 1])
        c3.metric("Jours d'ouverture analysés", f"{jours_ouverts}")
        
        # Graphique interactif si la colonne Date existe
        if "Date" in df_result.columns:
            st.markdown("#### Tendance des ventes projetées")
            # Agréger par date pour le graphique
            trend = df_result.groupby("Date")["Predicted_Sales"].sum().reset_index()
            trend["Date"] = pd.to_datetime(trend["Date"])
            trend = trend.set_index("Date")
            st.line_chart(trend)

        st.markdown("### 📑 Détail des résultats")
        st.dataframe(df_result[['Store', 'Date', 'Predicted_Sales']].head(50), use_container_width=True)
        
        st.download_button(
            label="📥 Télécharger le rapport complet (CSV)",
            data=df_result.to_csv(index=False).encode('utf-8'),
            file_name="rossmann_predictions_batch.csv",
            mime="text/csv",
            use_container_width=True
        )