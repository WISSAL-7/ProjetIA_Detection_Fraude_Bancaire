import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="SecureShield | Détection de Fraude",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS "BLINDÉ" (CORRECTION CONTRASTE) ---
st.markdown("""
<style>
    /* Import Police */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    /* --- VARIABLES --- */
    :root {
        --primary-red: #ED1C24;
        --dark-slate: #2C3E50;
        --light-bg: #F4F6F8;
        --text-dark: #1A252F;
        --text-light: #FFFFFF;
    }

    /* --- GLOBAL RESET --- */
    /* Force le fond global en gris très clair */
    .stApp {
        background-color: var(--light-bg);
        font-family: 'Roboto', sans-serif;
    }
    
    /* Force TOUT le texte de base en noir (pour contrer le mode sombre auto) */
    p, h1, h2, h3, h4, h5, h6, li, span, div {
        color: var(--text-dark);
    }

    /* --- SIDEBAR CORRECTIONS --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #e0e0e0;
    }
    /* Force le texte des menus (Radio buttons) en noir */
    [data-testid="stSidebar"] .stRadio label p {
        color: var(--text-dark) !important;
        font-weight: 500;
        font-size: 16px;
    }
    /* Force les titres et textes dans la sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
        color: var(--text-dark) !important;
    }

    /* --- BANNIERE HERO (TEXTE BLANC) --- */
    /* Ici on veut du texte blanc sur fond sombre, on doit forcer l'inverse du global */
    .security-banner {
        background: linear-gradient(90deg, #2c3e50 0%, #1a252f 100%);
        padding: 2rem;
        color: white !important;
        margin-bottom: 2rem;
        border-left: 8px solid var(--primary-red);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .security-banner h1 {
        color: white !important; /* Force blanc */
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .security-banner p {
        color: #bdc3c7 !important; /* Gris clair pour sous-titre */
        font-size: 1.1rem;
    }

    /* --- CARTES ET METRIQUES --- */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 4px solid var(--primary-red);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    /* Chiffres des métriques */
    [data-testid="stMetricValue"] {
        color: var(--dark-slate) !important;
        font-size: 28px !important;
    }
    /* Labels des métriques */
    [data-testid="stMetricLabel"] {
        color: #7f8c8d !important;
    }

    /* --- CARD "ALERTES SYSTEME" (FOND SOMBRE) --- */
    .dark-card {
        background-color: #2C3E50;
        padding: 20px;
        border-radius: 8px;
        color: white !important;
    }
    /* On force tous les enfants de .dark-card à être blancs */
    .dark-card h4, .dark-card p, .dark-card li, .dark-card span {
        color: white !important;
    }
    .dark-card hr {
        border-color: #555;
    }

    /* --- BOUTONS --- */
    .stButton button {
        background-color: var(--primary-red) !important;
        color: white !important;
        border: none;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton button:hover {
        background-color: #c0392b !important;
        box-shadow: 0 4px 8px rgba(237, 28, 36, 0.3);
    }
    /* Le texte à l'intérieur du bouton doit être blanc */
    .stButton button p {
        color: white !important;
    }

    /* --- CHART LABELS --- */
    /* Force les textes des graphiques Streamlit/Altair en sombre */
    text {
        fill: #333 !important;
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-weight: bold;
    }

</style>
""", unsafe_allow_html=True)

# --- DONNÉES SIMULÉES ---
@st.cache_data
def load_sample_data():
    np.random.seed(42)
    n = 1000
    data = pd.DataFrame({
        'Time': np.random.uniform(0, 172792, n),
        'Amount': np.random.exponential(100, n),
        **{f'V{i}': np.random.normal(0, 1, n) for i in range(1, 15)}
    })
    return data

# --- SIDEBAR (Menu Gauche) ---
with st.sidebar:
    # Logo simulé (Bouclier)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 60px;">🛡️</div>
            <h2 style="color: #2C3E50; margin:0;">SecureShield</h2>
            <p style="color: #7f8c8d; font-size: 12px; margin:0;">Intelligence Financière</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    menu = st.radio(
        "NAVIGATION",
        ["Dashboard Global", "Analyse de Transaction", "Explorateur de Données", "Intelligence Visuelle"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Statut système (Design personnalisé)
    st.markdown("""
        <div style="background-color: #e8f8f5; padding: 10px; border-radius: 6px; border-left: 4px solid #2ecc71;">
            <p style="color: #27ae60 !important; font-weight: bold; margin:0; font-size: 14px;">🟢 Statut Système</p>
            <p style="color: #27ae60 !important; margin:0; font-size: 12px;">Opérationnel • v2.4.1</p>
        </div>
    """, unsafe_allow_html=True)

# --- CONTENU PRINCIPAL ---

if menu == "Dashboard Global":
    # 1. Bannière HERO (Texte forcé blanc via classe CSS .security-banner)
    st.markdown("""
    <div class="security-banner">
        <h1>Détection et analyse des fraudes</h1>
        <p>Prévenez la fraude grâce à l'IA de pointe. Protégez vos transactions en temps réel.</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Métriques (KPIs)
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("Transactions (24h)", "12,450", "+12%")
    with k2: st.metric("Menaces Bloquées", "34", "critical")
    with k3: st.metric("Précision IA", "99.2%", "+0.1%")
    with k4: st.metric("Latence API", "45ms", "-5ms")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Zone Inférieure (Graphique + Alertes)
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("#### 📉 Tendances des Menaces")
        chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['Attaques', 'Blocages'])
        # Graphique linéaire simple
        st.line_chart(chart_data)

    with col_right:
        # Carte Sombre pour les alertes (Classe .dark-card force le texte blanc)
        st.markdown("""
        <div class="dark-card">
            <h4>📡 Alertes Système</h4>
            <hr>
            <ul style="padding-left: 20px; line-height: 1.8;">
                <li>🔴 <b>13:45</b> - IP bloquée (Moscou)</li>
                <li>🟡 <b>12:30</b> - Seuil volume > 80%</li>
                <li>🟢 <b>10:00</b> - Mise à jour Modèle v2.4</li>
                <li>🟢 <b>08:00</b> - Démarrage Services</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


elif menu == "Analyse de Transaction":
    st.markdown("## 🎯 Analyse Unitaire")
    st.markdown("Entrez les paramètres du vecteur de transaction pour l'évaluation en temps réel.")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        with st.form("check_form"):
            st.markdown("#### Vecteur d'entrée")
            amt = st.number_input("Montant (€)", 0.0, 10000.0, 150.0)
            time = st.number_input("Timestamp", 0.0, 200000.0, 50000.0)
            v14 = st.slider("Feature V14 (Anonymisé)", -5.0, 5.0, -1.2)
            
            submitted = st.form_submit_button("LANCER L'ANALYSE")
            
    with c2:
        if submitted:
            # Logique simple simulée
            risk = (amt / 1000) + abs(v14)/10
            risk = min(risk, 0.99)
            
            st.markdown("#### Résultat de l'IA")
            if risk > 0.5:
                st.markdown(f"""
                <div style="background-color: #fadbd8; padding: 20px; border-radius: 8px; border: 1px solid #e74c3c; text-align: center;">
                    <h2 style="color: #c0392b !important; margin:0;">🚨 RISQUE ÉLEVÉ</h2>
                    <h1 style="color: #c0392b !important; font-size: 50px;">{risk:.1%}</h1>
                    <p style="color: #c0392b !important;">REJET RECOMMANDÉ</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #d4efdf; padding: 20px; border-radius: 8px; border: 1px solid #27ae60; text-align: center;">
                    <h2 style="color: #27ae60 !important; margin:0;">✅ SÉCURISÉ</h2>
                    <h1 style="color: #27ae60 !important; font-size: 50px;">{risk:.1%}</h1>
                    <p style="color: #27ae60 !important;">AUTORISATION VALIDÉE</p>
                </div>
                """, unsafe_allow_html=True)

elif menu == "Explorateur de Données":
    st.markdown("## 💾 Base de Données")
    df = load_sample_data()
    st.dataframe(df.head(50), use_container_width=True)

elif menu == "Intelligence Visuelle":
    st.markdown("## 📊 Visualisation Avancée")
    df = load_sample_data()
    
    tab1, tab2 = st.tabs(["Distributions", "Corrélations"])
    
    with tab1:
        st.bar_chart(df['Amount'].head(50))
    with tab2:
        fig, ax = plt.subplots()
        sns.heatmap(df.corr().iloc[:5,:5], annot=True, ax=ax, cmap="RdBu_r")
        st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #95a5a6 !important; font-size: 12px;'>© 2025 SecureShield AI Solutions - Projet IA - Detection fraude bancaire</p>", unsafe_allow_html=True)