import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px

st.set_page_config(page_title="Analyse par Lot", layout="wide")

st.markdown("""
<style>
.title-box {
    color: #1E88E5;
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 0.4rem;
}
.sub-box {
    color: #6b7280;
    font-size: 1rem;
    text-align: center;
    margin-bottom: 1.4rem;
}
.card-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #1E88E5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    height: 100%;
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

st.markdown('<div class="title-box">📂 Analyse par lot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-box">Importez un fichier CSV pour générer des prévisions, visualiser les résultats et exporter le rapport final.</div>', unsafe_allow_html=True)

@st.cache_resource
def load_models():
    model = joblib.load("rossmann_xgb_model.pkl")
    scaler = joblib.load("rossmann_scaler.pkl")
    return model, scaler

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

def predict_sales_batch(df, model, scaler):
    df_proc = df.copy()

    if "Date" not in df_proc.columns:
        raise ValueError("La colonne Date est obligatoire.")

    df_proc["Date"] = pd.to_datetime(df_proc["Date"], errors="coerce")
    if df_proc["Date"].isna().any():
        raise ValueError("Certaines dates sont invalides dans le fichier.")

    df_proc["Year"] = df_proc["Date"].dt.year
    df_proc["Month"] = df_proc["Date"].dt.month
    df_proc["Day"] = df_proc["Date"].dt.day
    df_proc["WeekOfYear"] = df_proc["Date"].dt.isocalendar().week.astype(int)
    df_proc["DayOfWeekDate"] = df_proc["Date"].dt.dayofweek
    df_proc["IsMonthStart"] = df_proc["Date"].dt.is_month_start.astype(int)
    df_proc["IsMonthEnd"] = df_proc["Date"].dt.is_month_end.astype(int)
    df_proc = df_proc.drop(columns=["Date"])

    if "DayOfWeek" not in df_proc.columns:
        df_proc["DayOfWeek"] = df_proc["DayOfWeekDate"] + 1

    for col in ["CompetitionDistance", "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2SinceWeek", "Promo2SinceYear"]:
        if col in df_proc.columns:
            df_proc[col] = pd.to_numeric(df_proc[col], errors="coerce").fillna(0)

    for col in ["Open", "Promo", "SchoolHoliday", "Promo2"]:
        if col in df_proc.columns:
            df_proc[col] = pd.to_numeric(df_proc[col], errors="coerce").fillna(0).astype(int)

    for col in cat_cols:
        if col in df_proc.columns:
            df_proc[col] = df_proc[col].astype(str).fillna("unknown")

    df_proc = pd.get_dummies(df_proc, columns=[c for c in cat_cols if c in df_proc.columns], drop_first=True)

    for col in num_features:
        if col not in df_proc.columns:
            df_proc[col] = 0

    df_proc[num_features] = scaler.transform(df_proc[num_features])
    df_proc = df_proc.reindex(columns=expected_features, fill_value=0)

    preds = model.predict(df_proc)
    preds = np.expm1(preds) if np.nanmax(preds) < 50 else preds
    preds = np.where(preds < 0, 0, preds)
    return preds

uploaded_file = st.file_uploader("Glissez votre fichier CSV ici", type=["csv"])

if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file, dtype={"StateHoliday": str})
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")
        st.stop()

    st.success(f"Fichier chargé avec succès : {uploaded_file.name}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Lignes importées", f"{len(df_raw)}")
    c2.metric("Colonnes détectées", f"{df_raw.shape[1]}")
    c3.metric("Magasins uniques", f"{df_raw['Store'].nunique() if 'Store' in df_raw.columns else 0}")

    with st.expander("👁️ Aperçu des données importées", expanded=True):
        st.dataframe(df_raw.head(20), use_container_width=True)

    if st.button("Lancer les prédictions massives 🧠", type="primary", use_container_width=True):
        with st.spinner("Modélisation en cours..."):
            try:
                preds = predict_sales_batch(df_raw, model, scaler)
            except Exception as e:
                st.error(f"Erreur pendant la prédiction : {e}")
                st.stop()

            df_result = df_raw.copy()
            if "Open" in df_result.columns:
                df_result["Predicted_Sales"] = np.where(df_result["Open"].fillna(1) == 0, 0, np.round(preds, 2))
            else:
                df_result["Predicted_Sales"] = np.round(preds, 2)

        st.success("✅ Modélisation terminée !")

        st.markdown("### 📊 Synthèse des prévisions")
        k1, k2, k3, k4 = st.columns(4)

        total_ca = df_result["Predicted_Sales"].sum()
        mean_ca = df_result.loc[df_result["Predicted_Sales"] > 0, "Predicted_Sales"].mean()
        mean_ca = 0 if pd.isna(mean_ca) else mean_ca
        jours_ouverts = int((df_result["Open"] == 1).sum()) if "Open" in df_result.columns else len(df_result)
        magasins = df_result["Store"].nunique() if "Store" in df_result.columns else 0

        k1.metric("CA total projeté", f"{total_ca:,.0f} €".replace(",", " "))
        k2.metric("Moyenne positive", f"{mean_ca:,.0f} €".replace(",", " "))
        k3.metric("Jours ouverts", f"{jours_ouverts}")
        k4.metric("Magasins analysés", f"{magasins}")

        if "Date" in df_result.columns:
            st.markdown("#### Tendance des ventes projetées")
            trend = df_result.copy()
            trend["Date"] = pd.to_datetime(trend["Date"], errors="coerce")
            trend = trend.dropna(subset=["Date"])
            trend = trend.groupby("Date", as_index=False)["Predicted_Sales"].sum()

            fig = px.line(
                trend,
                x="Date",
                y="Predicted_Sales",
                markers=True,
                title="Évolution des ventes prévues"
            )
            fig.update_layout(
                template="plotly_white",
                xaxis_title="Date",
                yaxis_title="Ventes prévues (€)"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📑 Détail des résultats")
        cols_to_show = [c for c in ["Store", "Date", "Open", "Promo", "Predicted_Sales"] if c in df_result.columns]
        st.dataframe(df_result[cols_to_show].head(100), use_container_width=True)

        st.download_button(
            label="📥 Télécharger le rapport complet (CSV)",
            data=df_result.to_csv(index=False).encode("utf-8"),
            file_name="rossmann_predictions_batch.csv",
            mime="text/csv",
            use_container_width=True
        )