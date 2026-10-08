import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="MLB Pitch Arsenal Analyzer | Kodai Senga",
    page_icon="⚾",
    layout="wide"
)

# --- CHARGEMENT SÉCURISÉ DES DONNÉES ---
@st.cache_data
def load_data():
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    file_path = current_dir / "senga_2023_statcast.csv"
    
    if not file_path.exists():
        st.error(f"Fichier introuvable : {file_path}. Assurez-vous que 'senga_2023_statcast.csv' est bien présent dans le répertoire.")
        st.stop()
        
    df = pd.read_csv(file_path)
    # Conversion des mouvements en pouces (Perspective du receveur)
    df['pfx_x_in'] = df['pfx_x'] * 12 * -1  # Inversion pour la vue receveur
    df['pfx_z_in'] = df['pfx_z'] * 12
    return df

df = load_data()

# --- DICTIONNAIRE BILINGUE & TEXTES PÉDAGOGIQUES ---
PITCH_DESCRIPTIONS = {
    "en": {
        "4-Seam Fastball": "Primary power pitch thrown at maximum velocity, designed to overpower hitters at the top of the strike zone.",
        "Forkball": "Senga's signature 'Ghost Fork' — mimics a fastball before dropping drastically right before the plate, making hitters swing at empty air.",
        "Cutter": "Slightly slower than a fastball with late, sharp horizontal cutting motion away from right-handed batters.",
        "Sweeper": "A modern slider variation emphasizing extreme horizontal sweeping movement across the plate.",
        "Sinker": "Heavy fastball with arm-side tailing action designed to induce weak ground balls."
    },
    "fr": {
        "4-Seam Fastball": "Balle rapide principale lancée à pleine vitesse, conçue pour déborder les frappeurs dans le haut de la zone de prise.",
        "Forkball": "Le fameux 'Ghost Fork' (fourchette fantôme) de Senga : ressemble à une balle rapide mais plonge brutalement juste avant la plaque.",
        "Cutter": "Légèrement plus lente qu'une balle rapide, avec une coupure latérale sèche et tardive qui trompe le contact du frappeur.",
        "Sweeper": "Variante moderne du slider avec une cassure horizontale très prononcée qui traverse tout le marbre.",
        "Sinker": "Balle rapide lourde et plongeante conçue pour forcer des roulants inoffensifs au sol."
    }
}

# --- SIDEBAR (PARAMÈTRES ET FILTRES) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/New_York_Mets.svg/1200px-New_York_Mets.svg.png", width=95)
st.sidebar.markdown("### Settings & Filters")

# Sélecteur de langue
lang = st.sidebar.radio("🌐 Language / Langue", ["Français 🇫🇷", "English 🇬🇧"])
is_fr = lang.startswith("Français")

# Filtre : types de lancers
available_pitches = df['pitch_name'].dropna().unique().tolist()
pitch_filter_label = "Sélectionner les lancers :" if is_fr else "Select Pitch Types:"
selected_pitches = st.sidebar.multiselect(pitch_filter_label, available_pitches, default=available_pitches)

# Filtre : posture du batteur
stance_label = "Position du frappeur :" if is_fr else "Batter Stance:"
stance_options = ["Tous", "Droitiers (R)", "Gauchers (L)"] if is_fr else ["All", "Right-Handed (R)", "Left-Handed (L)"]
selected_stance = st.sidebar.radio(stance_label, stance_options)

# Application des filtres
filtered_df = df[df['pitch_name'].isin(selected_pitches)]
if selected_stance not in ["Tous", "All"]:
    stance_val = "R" if ("Droitiers" in selected_stance or "Right" in selected_stance) else "L"
    filtered_df = filtered_df[filtered_df['stand'] == stance_val]

total_pitches = len(filtered_df)

# --- EN-TÊTE PRINCIPAL ---
if is_fr:
    st.title("⚾ Analyse de l'Arsenal de Lancers — Kodai Senga (2023)")
    st.markdown("**Lanceur partant | New York Mets (MLB)** | Saison Rookie All-Star")
    st.caption("Ce tableau de bord décortique la trajectoire, la vitesse et l'efficacité des lancers mesurés par la télémétrie radar Statcast.")
else:
    st.title("⚾ Pitch Arsenal Analyzer — Kodai Senga (2023)")
    st.markdown("**Starting Pitcher | New York Mets (MLB)** | All-Star Rookie Season")
    st.caption("This dashboard deciphers pitch movement, velocity, and effectiveness using MLB Statcast optical tracking data.")

st.markdown("---")

# --- SECTION PÉDAGOGIQUE (POUR LES NON-INITIÉS) ---
with st.expander("📖 Comprendre les métriques du baseball / Understanding the Metrics"):
    if is_fr:
        st.markdown("""
        - **Vitesse (Velocity - mph) :** Vitesse de libération de la balle ($1\\text{ mph} \\approx 1.6\\text{ km/h}$). Au-dessus de $95\\text{ mph}$, c'est de l'élite mondiale.
        - **Taux de rotation (Spin Rate - RPM) :** Nombre de tours par minute. Plus le spin est élevé, plus la balle 'monte' artificiellement ou dévie brutalement.
        - **Mouvement Horizontal (Horizontal Break - pouces) :** Déviation latérale par rapport à une trajectoire droite (vue depuis le receveur).
        - **Mouvement Vertical (Vertical Break - pouces) :** Effet de portance ou de chute gravitationnelle subie par la balle avant d'atteindre le frappeur.
        """)
    else:
        st.markdown("""
        - **Release Speed (Velocity - mph) :** Ball velocity upon release ($95+\\text{ mph}$ ranks among MLB elite).
        - **Spin Rate (RPM) :** Rotations per minute. Higher spin produces greater late-breaking movement or perceived lift.
        - **Horizontal Break (inches) :** Lateral movement away from a straight line (Catcher's perspective).
        - **Vertical Break (inches) :** Perceived rise or gravity-induced drop before reaching home plate.
        """)

# --- CARTOUCHES KPI ---
if total_pitches > 0:
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Lancers analysés" if is_fr else "Pitches Analyzed", f"{total_pitches:,}")
    kpi_col2.metric("Vitesse moy." if is_fr else "Avg Velocity", f"{filtered_df['release_speed'].mean():.1f} mph")
    kpi_col3.metric("Spin Rate moyen" if is_fr else "Avg Spin Rate", f"{filtered_df['release_spin_rate'].mean():.0f} RPM")
    
    top_pitch = filtered_df['pitch_name'].value_counts().index[0]
    top_pitch_pct = (filtered_df['pitch_name'].value_counts().iloc[0] / total_pitches) * 100
    kpi_col4.metric("Lancer n°1" if is_fr else "Primary Pitch", f"{top_pitch} ({top_pitch_pct:.0f}%)")

st.markdown("---")

# --- COMMENTAIRES ET RAPPORT D'ANALYSE ADAPTATIF ---
st.subheader("📋 Rapport d'Analyse Automatisé" if is_fr else "📋 Automated Scouting Report")

if total_pitches == 0:
    st.warning("Aucune donnée disponible avec ces filtres." if is_fr else "No pitch data found with these filters.")
else:
    notes = []
    
    # 1. Analyse de la Fastball
    fb_df = filtered_df[filtered_df['pitch_name'] == '4-Seam Fastball']
    if not fb_df.empty:
        fb_velo = fb_df['release_speed'].mean()
        fb_spin = fb_df['release_spin_rate'].mean()
        if is_fr:
            qual = "d'élite (très difficile à frapper)" if fb_velo >= 95.5 else "solide et agressive"
            notes.append(f"**Balle Rapide (4-Seam Fastball) :** Vitesse moyenne de **{fb_velo:.1f} mph** avec une rotation de **{fb_spin:.0f} RPM**. Ce profil est {qual}.")
        else:
            qual = "elite level (challenging contact)" if fb_velo >= 95.5 else "above average"
            notes.append(f"**4-Seam Fastball Profile:** Registers an average velocity of **{fb_velo:.1f} mph** at **{fb_spin:.0f} RPM**, representing {qual} execution.")

    # 2. Analyse du Ghost Fork
    fork_df = filtered_df[filtered_df['pitch_name'] == 'Forkball']
    if not fork_df.empty:
        fork_pct = (len(fork_df) / total_pitches) * 100
        fork_drop = abs(fork_df['pfx_z_in'].mean())
        if is_fr:
            notes.append(f"**Lancer Signature ('Ghost Fork') :** Utilisé **{fork_pct:.1f}%** du temps dans cet échantillon. Avec une chute verticale moyenne de **{fork_drop:.1f} pouces**, ce lancer plonge brutalement sous la batte du frappeur.")
        else:
            notes.append(f"**Signature 'Ghost Fork':** Accounted for **{fork_pct:.1f}%** of pitch selection in this sample, producing **{fork_drop:.1f} inches** of downward plunge.")

    # 3. Commentaire selon la posture du frappeur (Droitier vs Gaucher)
    if selected_stance in ["Droitiers (R)", "Right-Handed (R)"]:
        notes.append("🎯 **Stratégie vs Droitiers :** Senga utilise principalement ses lancers à cassure latérale (Sweeper/Cutter) pour s'éloigner des mains du frappeur." if is_fr else "🎯 **Tactical Matchup vs RHH :** Heavy reliance on glove-side break (Sweeper/Cutter) to generate swings outside the zone.")
    elif selected_stance in ["Gauchers (L)", "Left-Handed (L)"]:
        notes.append("🎯 **Stratégie vs Gauchers :** Le Ghost Fork devient l'arme absolue pour forcer des prises sur élan dans le bas extérieur de la zone." if is_fr else "🎯 **Tactical Matchup vs LHH :** Ghost Fork serves as the ultimate wipeout weapon diving down-and-away.")

    # Affichage de la boîte d'explication
    st.info("\n\n".join(notes))

st.markdown("---")

# --- VISUALISATIONS INTERACTIVES ---
if total_pitches > 0:
    col_left, col_right = st.columns(2)

    with col_left:
        chart_title_1 = "Profil de Déviation des Lancers (Vue Receveur)" if is_fr else "Pitch Break Profile (Catcher's POV)"
        st.subheader(chart_title_1)
        st.caption("Chaque point représente un lancer. Plus un point est loin du centre (0,0), plus la balle a cassé en vol." if is_fr else "Points further from (0,0) indicate sharper late-breaking aerodynamic movement.")
        
        fig_break = px.scatter(
            filtered_df,
            x='pfx_x_in',
            y='pfx_z_in',
            color='pitch_name',
            hover_data=['release_speed', 'release_spin_rate'],
            labels={
                'pfx_x_in': 'Déviation horizontale (pouces)' if is_fr else 'Horizontal Break (in)',
                'pfx_z_in': 'Déviation verticale (pouces)' if is_fr else 'Vertical Break (in)',
                'pitch_name': 'Lancer' if is_fr else 'Pitch Type'
            },
            opacity=0.65
        )
        fig_break.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_break.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_break, use_container_width=True)

    with col_right:
        chart_title_2 = "Distribution des Vitesses (mph)" if is_fr else "Velocity Distribution (mph)"
        st.subheader(chart_title_2)
        st.caption("Comparaison de la régularité et des plages de vitesse selon le type de lancer." if is_fr else "Evaluates velocity separation and consistency across different pitch types.")
        
        fig_box = px.box(
            filtered_df,
            x='pitch_name',
            y='release_speed',
            color='pitch_name',
            labels={
                'release_speed': 'Vitesse (mph)' if is_fr else 'Velocity (mph)',
                'pitch_name': 'Lancer' if is_fr else 'Pitch Type'
            }
        )
        st.plotly_chart(fig_box, use_container_width=True)

# --- TABLEAU DÉTAILLÉ DE L'ARSENAL ---
st.subheader("📊 Tableau Synthétique de l'Arsenal" if is_fr else "📊 Pitch Characteristics Table")

if total_pitches > 0:
    table_df = filtered_df.groupby('pitch_name').agg(
        Count=('pitch_name', 'count'),
        Avg_Velocity=('release_speed', 'mean'),
        Avg_Spin=('release_spin_rate', 'mean'),
        Avg_Horz_Break=('pfx_x_in', 'mean'),
        Avg_Vert_Break=('pfx_z_in', 'mean')
    ).reset_index()

    table_df['Usage_%'] = ((table_df['Count'] / total_pitches) * 100).round(1)
    table_df['Avg_Velocity'] = table_df['Avg_Velocity'].round(1)
    table_df['Avg_Spin'] = table_df['Avg_Spin'].round(0)
    table_df['Avg_Horz_Break'] = table_df['Avg_Horz_Break'].round(1)
    table_df['Avg_Vert_Break'] = table_df['Avg_Vert_Break'].round(1)

    table_df = table_df.sort_values(by='Usage_%', ascending=False)

    # Renommage selon la langue
    if is_fr:
        table_df.columns = ["Type de lancer", "Total lancers", "Vitesse moy. (mph)", "Rotation moy. (RPM)", "Déviation Horiz. (in)", "Déviation Vert. (in)", "Utilisation (%)"]
    else:
        table_df.columns = ["Pitch Type", "Count", "Avg Velocity (mph)", "Avg Spin (RPM)", "Horizontal Break (in)", "Vertical Break (in)", "Usage (%)"]

    st.dataframe(table_df, use_container_width=True)
