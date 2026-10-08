import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="MLB Pitch Arsenal Analyzer",
    page_icon="⚾",
    layout="wide"
)

# --- CHARGEMENT SÉCURISÉ DES DONNÉES ---
@st.cache_data
def load_data():
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    file_path = current_dir / "senga_2023_statcast.csv"
    
    if not file_path.exists():
        st.error(f"Fichier introuvable : {file_path}. Exécutez d'abord data_fetcher.py.")
        st.stop()
        
    df = pd.read_csv(file_path)
    
    # Traitement des dates pour le filtre des saisons
    if 'game_date' in df.columns:
        df['game_date'] = pd.to_datetime(df['game_date'])
        df['season'] = df['game_date'].dt.year
    else:
        df['season'] = 2023 # Valeur par défaut si la colonne manque

    # Conversion des mouvements en pouces (Perspective du receveur)
    df['pfx_x_in'] = df['pfx_x'] * 12 * -1  # Inversion pour la vue receveur
    df['pfx_z_in'] = df['pfx_z'] * 12
    return df

df = load_data()

# --- SIDEBAR (PARAMÈTRES ET FILTRES) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/New_York_Mets.svg/1200px-New_York_Mets.svg.png", width=95)
st.sidebar.markdown("### Settings & Filters")

# Sélecteur de langue
lang = st.sidebar.radio("🌐 Language / Langue", ["Français 🇫🇷", "English 🇬🇧"])
is_fr = lang.startswith("Français")

# Filtre : Saison
available_seasons = sorted(df['season'].dropna().unique().tolist(), reverse=True)
season_label = "Saison :" if is_fr else "Season:"
selected_seasons = st.sidebar.multiselect(season_label, available_seasons, default=available_seasons)

# Filtre : Types de lancers
available_pitches = df['pitch_name'].dropna().unique().tolist()
pitch_filter_label = "Sélectionner les lancers :" if is_fr else "Select Pitch Types:"
selected_pitches = st.sidebar.multiselect(pitch_filter_label, available_pitches, default=available_pitches)

# Filtre : Posture du batteur
stance_label = "Position du frappeur :" if is_fr else "Batter Stance:"
stance_options = ["Tous", "Droitiers (R)", "Gauchers (L)"] if is_fr else ["All", "Right-Handed (R)", "Left-Handed (L)"]
selected_stance = st.sidebar.radio(stance_label, stance_options)

# Application des filtres
filtered_df = df[df['season'].isin(selected_seasons)]
filtered_df = filtered_df[filtered_df['pitch_name'].isin(selected_pitches)]

if selected_stance not in ["Tous", "All"]:
    stance_val = "R" if ("Droitiers" in selected_stance or "Right" in selected_stance) else "L"
    filtered_df = filtered_df[filtered_df['stand'] == stance_val]

total_pitches = len(filtered_df)

# --- EN-TÊTE PRINCIPAL ---
if is_fr:
    st.title("⚾ Analyse de la Télémétrie des Lancers (MLB)")
    st.markdown("**Profil Analysé : Kodai Senga | Lanceur Partant | New York Mets**")
else:
    st.title("⚾ Pitching Telemetry & Arsenal Analyzer (MLB)")
    st.markdown("**Analyzed Profile: Kodai Senga | Starting Pitcher | New York Mets**")

st.markdown("---")

# --- CONTEXTE ET ORIGINE DES DONNÉES (PÉDAGOGIE) ---
with st.expander("📌 Contexte du Projet & Origine des Données (À lire)" if is_fr else "📌 Project Context & Data Origin (Read First)", expanded=True):
    if is_fr:
        st.write("""
        **Pourquoi cette application ?**  
        Dans le baseball moderne, l'évaluation d'un joueur ne se fait plus à l'œil nu. Les équipes (comme les New York Mets) utilisent la Data Science pour décortiquer la biomécanique et la physique de chaque lancer. Cette application reproduit un outil de *Scouting* (recrutement) analytique.

        **D'où viennent ces données ?**  
        Les données proviennent de **Statcast**, le système de suivi optique (technologie Hawk-Eye) installé dans tous les stades de la Major League Baseball (MLB). À chaque lancer, des dizaines de caméras à très haute vitesse capturent la trajectoire 3D de la balle.  
        Ces données réelles ont été extraites via l'API publique de la MLB en utilisant le script Python `pybaseball`.

        **Que cherchons-nous à analyser ?**
        - **Vitesse (Velocity) :** La force brute du lanceur. Une balle à 95+ mph (153 km/h) laisse moins de 0.4 seconde au frappeur pour réagir.
        - **Rotation (Spin Rate) :** Mesuré en RPM (tours par minute). Une balle qui tourne vite "résiste" à la gravité et donne l'illusion de monter, ou au contraire plonge violemment.
        - **Mouvement (Break) :** La déviation de la balle par rapport à une trajectoire parfaitement droite. C'est ce qui fait rater la balle au batteur.
        """)
    else:
        st.write("""
        **Why this application?**  
        In modern baseball, player evaluation relies heavily on Data Science to dissect the physics of every pitch. This application simulates a front-office analytical scouting tool.

        **Where does the data come from?**  
        Data is sourced directly from **MLB Statcast**, the Hawk-Eye optical tracking system installed in all MLB stadiums. It captures the exact 3D trajectory, spin, and velocity of every pitch. The dataset was queried via the `pybaseball` Python API.

        **What are we analyzing?**
        - **Velocity:** Raw power. A 95+ mph fastball gives the hitter less than 0.4 seconds to react.
        - **Spin Rate (RPM):** A high spin rate helps a fastball resist gravity (creating a "rising" illusion) or gives breaking balls a sharp, late bite.
        - **Movement (Break):** The horizontal and vertical deviation from a perfectly straight trajectory.
        """)

# --- CARTOUCHES KPI ---
if total_pitches > 0:
    st.markdown("### 📈 Métriques Globales de l'Échantillon" if is_fr else "### 📈 Sample Global Metrics")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Lancers analysés" if is_fr else "Pitches Analyzed", f"{total_pitches:,}")
    kpi_col2.metric("Vitesse moy." if is_fr else "Avg Velocity", f"{filtered_df['release_speed'].mean():.1f} mph")
    kpi_col3.metric("Spin Rate moyen" if is_fr else "Avg Spin Rate", f"{filtered_df['release_spin_rate'].mean():.0f} RPM")
    
    top_pitch = filtered_df['pitch_name'].value_counts().index[0]
    top_pitch_pct = (filtered_df['pitch_name'].value_counts().iloc[0] / total_pitches) * 100
    kpi_col4.metric("Lancer n°1" if is_fr else "Primary Pitch", f"{top_pitch} ({top_pitch_pct:.0f}%)")

st.markdown("---")

# --- RAPPORT D'ANALYSE ADAPTATIF ---
st.subheader("🤖 Conclusion Analytique Automatisée" if is_fr else "🤖 Automated Analytical Conclusion")

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
            qual = "L'élite de la ligue." if fb_velo >= 95.5 else "Une vitesse solide pour la MLB."
            notes.append(f"🔥 **Balle Rapide (4-Seam Fastball) :** S'établit à une moyenne de **{fb_velo:.1f} mph**. *Pourquoi c'est important ?* {qual} Combiné à une rotation de **{fb_spin:.0f} RPM**, cela crée un effet de portance qui trompe l'œil du frappeur.")
        else:
            qual = "Elite MLB level." if fb_velo >= 95.5 else "Solid MLB velocity."
            notes.append(f"🔥 **4-Seam Fastball:** Sits at an average of **{fb_velo:.1f} mph**. *Why it matters:* {qual} Combined with a spin rate of **{fb_spin:.0f} RPM**, it generates 'riding' action that induces swings-and-misses.")

    # 2. Analyse du Ghost Fork
    fork_df = filtered_df[filtered_df['pitch_name'] == 'Forkball']
    if not fork_df.empty:
        fork_pct = (len(fork_df) / total_pitches) * 100
        fork_drop = abs(fork_df['pfx_z_in'].mean())
        if is_fr:
            notes.append(f"👻 **Lancer Signature ('Ghost Fork') :** Utilisé **{fork_pct:.1f}%** du temps. *Pourquoi c'est dévastateur ?* La balle chute brutalement de **{fork_drop:.1f} pouces** vers le sol. Le frappeur s'élance pensant frapper une balle rapide, mais la balle 'disparaît' sous sa batte.")
        else:
            notes.append(f"👻 **Signature Pitch ('Ghost Fork'):** Used **{fork_pct:.1f}%** of the time. *Why it's devastating:* The pitch drops completely off the table by **{fork_drop:.1f} inches**. Hitters swing expecting a fastball, but the ball 'disappears' under the barrel.")

    # 3. Stratégie Situationnelle
    if selected_stance in ["Droitiers (R)", "Right-Handed (R)"]:
        notes.append("🎯 **Stratégie (vs Droitiers) :** Face aux droitiers, on observe une forte utilisation de l'axe horizontal. Les lancers fuient vers l'extérieur pour éviter le 'cœur' du marbre." if is_fr else "🎯 **Strategy (vs RHH):** Against righties, there is a clear emphasis on horizontal tunneling, forcing the batter to reach for outside pitches.")
    elif selected_stance in ["Gauchers (L)", "Left-Handed (L)"]:
        notes.append("🎯 **Stratégie (vs Gauchers) :** Face aux gauchers, l'axe vertical est privilégié. Le lanceur cherche à faire plonger la balle sur les pieds du frappeur." if is_fr else "🎯 **Strategy (vs LHH):** Against lefties, vertical separation is heavily utilized, burying breaking pitches in the dirt to generate strikeouts.")

    st.success("\n\n".join(notes))

st.markdown("---")

# --- VISUALISATIONS INTERACTIVES ---
if total_pitches > 0:
    col_left, col_right = st.columns(2)

    with col_left:
        chart_title_1 = "Trajectoires & Déviations (Vue du Receveur)" if is_fr else "Pitch Movement Profile (Catcher's POV)"
        st.subheader(chart_title_1)
        st.caption("Le centre (0,0) représente une ligne droite parfaite. Les points montrent la cassure finale de la balle." if is_fr else "Center (0,0) is a perfectly straight line. Points indicate the final breaking movement.")
        
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
        chart_title_2 = "Constance de la Vitesse (mph)" if is_fr else "Velocity Consistency (mph)"
        st.subheader(chart_title_2)
        st.caption("Un bon lanceur doit avoir des plages de vitesse bien séparées pour brouiller les pistes." if is_fr else "Elite pitchers maintain distinct velocity bands to disrupt the batter's timing.")
        
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
st.subheader("📊 Données Brutes Agrégees" if is_fr else "📊 Aggregated Raw Data")

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

    if is_fr:
        table_df.columns = ["Type de lancer", "Total lancers", "Vitesse moy. (mph)", "Rotation moy. (RPM)", "Déviation Horiz. (in)", "Déviation Vert. (in)", "Utilisation (%)"]
    else:
        table_df.columns = ["Pitch Type", "Count", "Avg Velocity (mph)", "Avg Spin (RPM)", "Horizontal Break (in)", "Vertical Break (in)", "Usage (%)"]

    st.dataframe(table_df, use_container_width=True)
