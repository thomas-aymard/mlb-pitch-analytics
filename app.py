import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="MLB Pitch Arsenal Analyzer | Kodai Senga 2023",
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

    # Conversion des mouvements en pouces (Perspective du receveur)
    # 1 pied = 12 pouces. Inversion de l'axe X pour reproduire la vue du receveur
    df['pfx_x_in'] = df['pfx_x'] * 12 * -1
    df['pfx_z_in'] = df['pfx_z'] * 12
    return df

df = load_data()

# --- SIDEBAR (PARAMÈTRES ET FILTRES) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/New_York_Mets.svg/1200px-New_York_Mets.svg.png", width=95)
st.sidebar.markdown("### Paramètres & Filtres" if True else "### Settings & Filters")

# Sélecteur de langue
lang = st.sidebar.radio("🌐 Langue / Language", ["Français 🇫🇷", "English 🇬🇧"])
is_fr = lang.startswith("Français")

# Précision sur la saison analysée (Fixe : 2023)
st.sidebar.info("📅 **Saison analysée :** 2023 complète (Saison Rookie All-Star avec les New York Mets)" if is_fr else "📅 **Analyzed Season:** Full 2023 (All-Star Rookie Season with the New York Mets)")

# Filtre : Types de lancers
available_pitches = df['pitch_name'].dropna().unique().tolist()
pitch_filter_label = "Lancers à afficher :" if is_fr else "Select Pitch Types:"
selected_pitches = st.sidebar.multiselect(pitch_filter_label, available_pitches, default=available_pitches)

# Filtre : Posture du frappeur
stance_label = "Frappeur adverse :" if is_fr else "Batter Stance:"
stance_options = ["Tous les frappeurs", "Droitiers uniquement (R)", "Gauchers uniquement (L)"] if is_fr else ["All Batters", "Right-Handed only (R)", "Left-Handed only (L)"]
selected_stance = st.sidebar.radio(stance_label, stance_options)

# Application des filtres
filtered_df = df[df['pitch_name'].isin(selected_pitches)]

if selected_stance not in ["Tous les frappeurs", "All Batters"]:
    stance_val = "R" if ("Droitiers" in selected_stance or "Right-Handed" in selected_stance) else "L"
    filtered_df = filtered_df[filtered_df['stand'] == stance_val]

total_pitches = len(filtered_df)

# --- EN-TÊTE PRINCIPAL ---
if is_fr:
    st.title("⚾ Analyse de l'Arsenal de Lancers — Kodai Senga")
    st.markdown("### Données officielles Statcast • **Saison Régulière 2023** (New York Mets)")
    st.caption("Étude quantitative de chaque tir déclenché par Kodai Senga lors de son année rookie en MLB.")
else:
    st.title("⚾ Pitch Arsenal Telemetry — Kodai Senga")
    st.markdown("### Official MLB Statcast Data • **Full 2023 Season** (New York Mets)")
    st.caption("Quantitative tracking of every pitch thrown by Kodai Senga during his 2023 rookie season.")

st.markdown("---")

# --- CONTEXTE ET ORIGINE DES DONNÉES ---
with st.expander("📌 Contexte du Projet & Origine des Données (Comprendre l'analyse)" if is_fr else "📌 Project Context & Data Origin (How to read this)", expanded=False):
    if is_fr:
        st.markdown("""
        - **D'où viennent ces données ?** Elles proviennent de **Statcast**, le réseau officiel de caméras optiques haute fréquence (Hawk-Eye) et de radars installés dans tous les stades de la MLB. Chaque tir est tracké en 3D à plusieurs centaines d'images par seconde.
        - **Période analysée :** L'intégralité de la **saison régulière 2023** de Kodai Senga avec les New York Mets (d'avril à octobre 2023), soit plus de 2 500 lancers réels.
        - **Objectif :** Évaluer l'efficacité de son arsenal, la séparation de vitesse entre ses tirs et l'illusion d'optique créée par son lancer signature, le *Ghost Fork*.
        """)
    else:
        st.markdown("""
        - **Data Origin:** Directly sourced from **MLB Statcast** (Hawk-Eye multi-camera tracking system deployed in all 30 MLB stadiums).
        - **Scope:** Complete **2023 Regular Season** data for Kodai Senga with the New York Mets (April to October 2023).
        - **Objective:** Quantify pitch movement profiles, velocity differential, and the tunneling synergy between his Fastball and signature Ghost Fork.
        """)

# --- CARTOUCHES KPI ---
if total_pitches > 0:
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total tirs analysés (2023)" if is_fr else "Total 2023 Pitches", f"{total_pitches:,}")
    kpi_col2.metric("Vitesse moyenne" if is_fr else "Avg Velocity", f"{filtered_df['release_speed'].mean():.1f} mph")
    kpi_col3.metric("Taux de rotation moyen" if is_fr else "Avg Spin Rate", f"{filtered_df['release_spin_rate'].mean():.0f} RPM")
    
    top_pitch = filtered_df['pitch_name'].value_counts().index[0]
    top_pitch_pct = (filtered_df['pitch_name'].value_counts().iloc[0] / total_pitches) * 100
    kpi_col4.metric("Lancer principal" if is_fr else "Primary Pitch", f"{top_pitch} ({top_pitch_pct:.0f}%)")

st.markdown("---")

# --- COMMENTAIRES SYNTHÉTIQUES ---
st.subheader("📋 Rapport de Scouting Automatisé (Saison 2023)" if is_fr else "📋 Automated 2023 Scouting Report")

if total_pitches == 0:
    st.warning("Aucune donnée disponible avec cette combinaison de filtres." if is_fr else "No pitch records match the selected filters.")
else:
    notes = []
    
    fb_df = filtered_df[filtered_df['pitch_name'] == '4-Seam Fastball']
    if not fb_df.empty:
        fb_velo = fb_df['release_speed'].mean()
        fb_spin = fb_df['release_spin_rate'].mean()
        if is_fr:
            notes.append(f"🔥 **Balle Rapide (4-Seam Fastball) :** Vitesse moyenne de **{fb_velo:.1f} mph** avec une rotation de **{fb_spin:.0f} RPM**. Ce lancer reste en haut de zone et sert de référence de vitesse pour masquer ses tirs à effets.")
        else:
            notes.append(f"🔥 **4-Seam Fastball:** Averages **{fb_velo:.1f} mph** at **{fb_spin:.0f} RPM**, setting the upper velocity ceiling to mask off-speed pitches.")

    fork_df = filtered_df[filtered_df['pitch_name'] == 'Forkball']
    if not fork_df.empty:
        fork_pct = (len(fork_df) / total_pitches) * 100
        fork_drop = abs(fork_df['pfx_z_in'].mean())
        if is_fr:
            notes.append(f"👻 **Ghost Fork (Lancer signature) :** Représente **{fork_pct:.1f}%** de ses lancers. Avec **{fork_drop:.1f} pouces** de chute verticale, ce tir plonge au dernier moment sous la batte sans casser latéralement.")
        else:
            notes.append(f"👻 **Signature Ghost Fork:** Represents **{fork_pct:.1f}%** of pitch usage, creating **{fork_drop:.1f} inches** of late vertical drop with minimal horizontal fade.")

    if selected_stance in ["Droitiers uniquement (R)", "Right-Handed only (R)"]:
        notes.append("🎯 **Approche vs Droitiers :** Utilisation accentuée du Cutter et du Sweeper pour fuir vers l'extérieur du marbre (glove-side)." if is_fr else "🎯 **Matchup vs RHH:** Heavy usage of glove-side breakers (Cutter / Sweeper) sweeping away from righties.")
    elif selected_stance in ["Gauchers uniquement (L)", "Left-Handed only (L)"]:
        notes.append("🎯 **Approche vs Gauchers :** Le Ghost Fork et la Fastball dominent pour attaquer la ligne verticale et générer des retraits au bâton." if is_fr else "🎯 **Matchup vs LHH:** Vertical tunneling dominates with Fastball up and Ghost Fork down in the dirt.")

    st.success("\n\n".join(notes))

st.markdown("---")

# --- GRAPHIQUES ET EXPLICATIONS DÉTAILLÉES ---
if total_pitches > 0:
    col_left, col_right = st.columns(2)

    # 1. GRAPHIQUE GAUCHE : DÉVIATIONS & TRAJECTOIRES
    with col_left:
        st.subheader("1. Trajectoires & Déviations (Vue Receveur)" if is_fr else "1. Pitch Break Profile (Catcher's POV)")
        
        fig_break = px.scatter(
            filtered_df,
            x='pfx_x_in',
            y='pfx_z_in',
            color='pitch_name',
            hover_data=['release_speed', 'release_spin_rate'],
            labels={
                'pfx_x_in': 'Déviation horizontale (pouces)' if is_fr else 'Horizontal Break (in)',
                'pfx_z_in': 'Déviation verticale (pouces)' if is_fr else 'Vertical Break (in)',
                'pitch_name': 'Type de tir' if is_fr else 'Pitch Type'
            },
            opacity=0.65
        )
        fig_break.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_break.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_break, use_container_width=True)

        # COMMENTAIRE DÉTAILLÉ DU GRAPHIQUE 1
        with st.container():
            if is_fr:
                st.markdown("""
                **💡 Comment lire et comprendre ce graphique ?**
                * **Le point central (0, 0) :** Représente une trajectoire théorique parfaitement rectiligne sans aucune déviation aérodynamique.
                * **En haut à droite (Bleu foncé - 4-Seam Fastball) :** Ces balles restent au-dessus de +15 pouces verticalement. Ce n'est pas qu'elles montent contre la gravité, mais leur forte rotation les maintient hautes dans l'air, donnant l'illusion qu'elles "flottent".
                * **Au milieu bas (Bleu clair - Forkball / Ghost Fork) :** Les points tombent près de l'axe vertical 0 mais descendent vers 0 à -5 pouces. C'est l'arme absolue de Senga : elle part avec le même axe que la Fastball mais chute de près de 15 pouces plus bas à l'arrivée.
                * **À gauche (Rouge/Rose - Cutter & Sweeper) :** Ces lancers partent vers des valeurs négatives en X (déviation latérale gauche), s'éloignant des droitiers pour tromper leur zone de frappe.
                """)
            else:
                st.markdown("""
                **💡 How to interpret this movement chart:**
                * **Center Intersection (0, 0):** Represents zero aerodynamic break (pure straight trajectory).
                * **Top Right Cluster (4-Seam Fastball):** Positive vertical break (+15+ in) reflects elite backspin and perceived 'rise' at the top of the strike zone.
                * **Bottom Center (Ghost Fork):** Mirrors the Fastball's horizontal path but drops 15+ inches lower vertically, creating devastating pitch tunneling.
                * **Left Side (Cutter & Sweeper):** Negative horizontal coordinates show sharp glove-side break moving away from right-handed hitters.
                """)

    # 2. GRAPHIQUE DROITE : CONSTANCE DES VITESSES
    with col_right:
        st.subheader("2. Constance & Écarts de Vitesse (mph)" if is_fr else "2. Velocity Consistency & Tiers (mph)")
        
        fig_box = px.box(
            filtered_df,
            x='pitch_name',
            y='release_speed',
            color='pitch_name',
            labels={
                'release_speed': 'Vitesse au lâcher (mph)' if is_fr else 'Release Speed (mph)',
                'pitch_name': 'Type de tir' if is_fr else 'Pitch Type'
            }
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # COMMENTAIRE DÉTAILLÉ DU GRAPHIQUE 2
        with st.container():
            if is_fr:
                st.markdown("""
                **💡 Comment lire et comprendre ce graphique ?**
                * **La séparation des paliers :** Un lanceur d'élite doit créer au moins 10 à 15 mph d'écart entre sa balle la plus rapide et ses lancers à effet pour dérégler le timing du frappeur.
                * **Palier Rapide (95-99 mph) :** La 4-Seam Fastball domine nettement avec une boîte très resserrée autour de 96 mph, gage d'une grande répétabilité mécanique.
                * **Palier Intermédiaire (83-91 mph) :** Le Cutter et le Forkball gravitent entre 83 et 92 mph. Le frappeur s'élance sur le tempo d'une rapide mais frappe trop tôt.
                * **Palier Ralenti (70-78 mph) :** Le Sweeper et la Curveball descendent sous les 75 mph. Cet écart de près de 25 mph avec sa balle rapide détruit le timing des frappeurs de MLB.
                """)
            else:
                st.markdown("""
                **💡 How to interpret this velocity boxplot:**
                * **Velocity Separation:** Elite starters disrupt hitter timing by creating noticeable velocity tiers across their arsenal.
                * **Tier 1 - Power (95–99 mph):** Tight boxplot distribution on the 4-Seam Fastball shows high mechanical repeatability at elite speed.
                * **Tier 2 - Deception (83–91 mph):** The Forkball and Cutter operate in the mid-80s, forcing early swings from batters expecting 96+ mph.
                * **Tier 3 - Off-Speed (70–78 mph):** Curveball and Sweeper dip into the mid-70s, creating an extreme 20+ mph differential against his fastball.
                """)

# --- TABLEAU RÉCAPITULATIF FINAL ---
st.markdown("---")
st.subheader("📊 Données Statistiques Complètes de la Saison 2023" if is_fr else "📊 Complete 2023 Season Statistical Breakdown")

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
        table_df.columns = ["Type de tir", "Nombre de lancers (2023)", "Vitesse moy. (mph)", "Rotation moy. (RPM)", "Cassure Horiz. (pouces)", "Cassure Vert. (pouces)", "Taux d'utilisation (%)"]
    else:
        table_df.columns = ["Pitch Type", "2023 Pitch Count", "Avg Velocity (mph)", "Avg Spin (RPM)", "Horizontal Break (in)", "Vertical Break (in)", "Usage (%)"]

    st.dataframe(table_df, use_container_width=True)
