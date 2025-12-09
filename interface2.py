import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="SecureShield | Détection IA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS (LE MÊME QUE PRÉCÉDEMMENT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    :root { --primary-red: #ED1C24; --dark-slate: #2C3E50; --light-bg: #F4F6F8; --text-dark: #1A252F; }
    .stApp { background-color: var(--light-bg); font-family: 'Roboto', sans-serif; }
    h1, h2, h3, p, li { color: var(--text-dark); }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #e0e0e0; }
    
    /* Bannière Hero */
    .security-banner {
        background: linear-gradient(90deg, #2c3e50 0%, #1a252f 100%);
        padding: 2rem; color: white !important;
        border-left: 8px solid var(--primary-red);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 2rem;
    }
    .security-banner h1 { color: white !important; margin-bottom: 0.5rem; }
    .security-banner p { color: #bdc3c7 !important; }

    /* Métriques et Cartes */
    div[data-testid="metric-container"] {
        background-color: white; padding: 15px; border-radius: 8px;
        border-left: 4px solid var(--primary-red); box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .dark-card { background-color: #2C3E50; padding: 20px; border-radius: 8px; color: white !important; }
    .dark-card h4, .dark-card li { color: white !important; }

    /* Boutons */
    .stButton button {
        background-color: var(--primary-red) !important; color: white !important;
        border: none; font-weight: bold; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES RESSOURCES RÉELLES ---
@st.cache_resource
def load_resources():
    try:
        # Chargement du modèle et du scaler exportés depuis le Notebook
        model = joblib.load('modele_fraude.joblib')
        scaler = joblib.load('scaler.joblib')
        return model, scaler
    except FileNotFoundError:
        st.error("⚠️ ERREUR CRITIQUE : Fichiers modèles introuvables. Avez-vous exécuté l'étape 1 ?")
        return None, None

@st.cache_data
def load_data():
    try:
        # On charge une partie du vrai dataset pour les stats
        df = pd.read_csv('creditcard.csv')
        # On prend un échantillon si le fichier est trop gros pour la RAM
        return df.sample(10000, random_state=42) if len(df) > 10000 else df
    except FileNotFoundError:
        return None

# Chargement
model, scaler = load_resources()
df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 60px;">🛡️</div>
            <h2 style="color: #2C3E50; margin:0;">SecureShield</h2>
            <p style="color: #7f8c8d; font-size: 12px; margin:0;">Moteur Random Forest v1.0</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVIGATION", ["Dashboard Global", "Détection Temps Réel", "Explorateur de Données"], label_visibility="collapsed")
    st.markdown("---")
    
    # Indicateur de chargement du modèle
    if model is not None:
        st.success("✅ Modèle IA chargé")
    else:
        st.error("❌ Modèle manquant")

# --- CONTENU ---

if menu == "Dashboard Global":
    st.markdown("""
    <div class="security-banner">
        <h1>Centre de Contrôle des Fraudes</h1>
        <p>Analyse basée sur votre dataset réel et le modèle Random Forest.</p>
    </div>
    """, unsafe_allow_html=True)

    if df is not None:
        # Calcul des vraies stats
        fraud_rate = (df['Class'].mean() * 100)
        total_frauds = df['Class'].sum()
        avg_fraud_amt = df[df['Class'] == 1]['Amount'].mean()

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Transactions Analysées", f"{len(df):,}")
        with k2: st.metric("Fraudes Détectées", f"{total_frauds}", "Dataset")
        with k3: st.metric("Taux de Fraude", f"{fraud_rate:.3f}%")
        with k4: st.metric("Montant Moyen (Fraude)", f"{avg_fraud_amt:.2f} €")

        st.markdown("### 📊 Distribution des Transactions")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.line_chart(df['Amount'].head(100))
            st.caption("Aperçu séquentiel des montants")
        with c2:
            st.markdown("""
            <div class="dark-card">
                <h4>📡 État du Modèle</h4>
                <hr>
                <ul>
                    <li>Algorithme : <b>Random Forest</b></li>
                    <li>Scaler : <b>RobustScaler</b></li>
                    <li>Sampling : <b>SMOTE</b></li>
                    <li>Statut : <b>Opérationnel</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Veuillez placer le fichier 'creditcard.csv' dans le dossier.")

elif menu == "Détection Temps Réel":
    st.markdown("## 🕵️ Analyseur de Transaction")
    st.markdown("Utilisez le modèle entraîné pour prédire si une transaction est frauduleuse.")

    col_input, col_result = st.columns([1, 1])

    with col_input:
        with st.form("prediction_form"):
            st.markdown("#### Paramètres de la Transaction")
            
            # Inputs Réels
            time_val = st.number_input("Temps (secondes depuis le début)", value=0.0)
            amount_val = st.number_input("Montant de la transaction (€)", value=0.0)
            
            st.markdown("#### Caractéristiques Critiques (V)")
            st.info("Ces variables (V1-V28) sont issues de la PCA. Modifiez les plus importantes (V17, V14, V12) pour voir l'impact.")
            
            # On met les sliders pour les features les plus importantes (selon votre EDA)
            v17 = st.slider("V17 (Indicateur clé)", -30.0, 10.0, 0.0)
            v14 = st.slider("V14 (Indicateur clé)", -30.0, 10.0, 0.0)
            v12 = st.slider("V12 (Indicateur clé)", -20.0, 20.0, 0.0)
            
            # Bouton caché pour simulation des autres variables
            with st.expander("Modifier les autres variables (Avancé)"):
                v4 = st.number_input("V4", value=0.0)
                v11 = st.number_input("V11", value=0.0)
            
            submit = st.form_submit_button("LANCER L'ANALYSE IA")

    with col_result:
        if submit and model is not None and scaler is not None:
            # 1. PRETRAITEMENT
            # Le scaler attend 2 colonnes : ['scaled_amount', 'scaled_time'] ou l'inverse selon votre notebook
            # On suppose ici l'ordre Amount, Time. Il faut vérifier l'ordre du fit dans le notebook.
            # Créons un array pour scaler
            to_scale = np.array([[amount_val, time_val]])
            scaled_vals = scaler.transform(to_scale)
            
            s_amount = scaled_vals[0][0]
            s_time = scaled_vals[0][1]

            # 2. CONSTRUCTION DU VECTEUR COMPLET (30 colonnes)
            # L'ordre doit être EXACTEMENT celui de X_train dans le notebook.
            # Généralement : Time, V1...V28, Amount (mais parfois déplacé)
            # Dans votre notebook (Capture 4.1), vous avez : 
            # scaled_amount, scaled_time, V1, V2 ... V28
            
            # Initialisation d'un vecteur de 0 pour les 30 features
            features = np.zeros((1, 30))
            
            # Remplissage intelligent
            # On suppose l'ordre standard du dataset transformé :
            # [scaled_amount, scaled_time, V1, V2, ..., V28] 
            # (Vérifiez X_train.columns dans votre notebook pour être sûr à 100%)
            
            features[0, 0] = s_amount
            features[0, 1] = s_time
            # On remplit les V que l'utilisateur a modifié
            # V1 est à l'index 2, V2 à l'index 3... donc Vn à l'index n+1
            features[0, 17+1] = v17 # V17
            features[0, 14+1] = v14 # V14
            features[0, 12+1] = v12 # V12
            features[0, 4+1] = v4   # V4
            features[0, 11+1] = v11 # V11

            # 3. PRÉDICTION
            prediction = model.predict(features)
            proba = model.predict_proba(features)[0][1] # Proba de la classe 1 (Fraude)

            st.markdown("#### Résultat du Modèle")
            
            if prediction[0] == 1:
                st.markdown(f"""
                <div style="background-color: #fadbd8; padding: 20px; border-radius: 8px; border: 2px solid #e74c3c; text-align: center;">
                    <h2 style="color: #c0392b !important;">🚨 FRAUDE DÉTECTÉE</h2>
                    <h1 style="color: #c0392b !important; font-size: 45px;">{proba:.1%}</h1>
                    <p style="color: #c0392b !important;">Probabilité de risque</p>
                    <hr>
                    <p style="color: #c0392b !important; font-size: 14px;">Motif principal : V17={v17}, V14={v14}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #d4efdf; padding: 20px; border-radius: 8px; border: 2px solid #27ae60; text-align: center;">
                    <h2 style="color: #27ae60 !important;">✅ TRANSACTION SÛRE</h2>
                    <h1 style="color: #27ae60 !important; font-size: 45px;">{proba:.1%}</h1>
                    <p style="color: #27ae60 !important;">Risque minime</p>
                </div>
                """, unsafe_allow_html=True)
        elif submit:
             st.error("Le modèle n'est pas chargé.")

elif menu == "Explorateur de Données":
    if df is not None:
        st.markdown("## 🔍 Données Brutes")
        st.dataframe(df.head(100), use_container_width=True)
        
        st.markdown("### Corrélations (Dataset Réel)")
        fig, ax = plt.subplots(figsize=(10, 6))
        # On prend un sous-ensemble pour la lisibilité
        cols = ['Class', 'Amount', 'V17', 'V14', 'V12', 'V10', 'V11', 'V4']
        sns.heatmap(df[cols].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
    else:
        st.warning("Pas de données chargées.")