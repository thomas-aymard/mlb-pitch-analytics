import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="MLB Pitch Arsenal Analyzer", layout="wide")

# Fonction pour charger les données (mise en cache pour la rapidité)
@st.cache_data
def load_data():
    df = pd.read_csv('senga_2023_statcast.csv')
    # Convertir les mouvements de pieds en pouces pour une meilleure lisibilité
    df['pfx_x_in'] = df['pfx_x'] * 12 * -1 # Inversé pour la vue du receveur
    df['pfx_z_in'] = df['pfx_z'] * 12
    return df

df = load_data()

# --- SIDEBAR (Filtres) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/New_York_Mets.svg/1200px-New_York_Mets.svg.png", width=100)
st.sidebar.header("Filter Options")

# Filtre par type de lancer
pitch_types = df['pitch_name'].unique().tolist()
selected_pitches = st.sidebar.multiselect("Select Pitch Types", pitch_types, default=pitch_types)

# Filtre par batteur (Gaucher / Droitier)
batter_stands = st.sidebar.radio("Batter Stance", ["All", "Right (R)", "Left (L)"])

# Appliquer les filtres
filtered_df = df[df['pitch_name'].isin(selected_pitches)]
if batter_stands != "All":
    stance_val = "R" if batter_stands == "Right (R)" else "L"
    filtered_df = filtered_df[filtered_df['stand'] == stance_val]


# --- MAIN CONTENT ---
st.title("⚾ Kodai Senga - Pitch Arsenal Analyzer (2023)")
st.markdown("**Role:** Starting Pitcher | **Team:** New York Mets | **Throws:** Right")

st.markdown("---")

# --- AUTOMATED SCOUTING REPORT (Natural Language Generation) ---
st.header("🤖 Automated Scouting Report")

# Calculs pour le rapport
total_pitches = len(filtered_df)

if total_pitches > 0:
    # 4-Seam Fastball metrics
    fb_data = filtered_df[filtered_df['pitch_name'] == '4-Seam Fastball']
    if not fb_data.empty:
        avg_fb_velo = fb_data['release_speed'].mean()
        avg_fb_spin = fb_data['release_spin_rate'].mean()
        
        velo_eval = "elite" if avg_fb_velo >= 95 else "above-average" if avg_fb_velo >= 93 else "average"
        spin_eval = "high" if avg_fb_spin >= 2400 else "standard"
        
        fb_text = f"**Fastball Profile:** Showcases an {velo_eval} 4-Seam Fastball averaging **{avg_fb_velo:.1f} mph** with a {spin_eval} spin rate (**{avg_fb_spin:.0f} RPM**)."
    else:
        fb_text = "**Fastball Profile:** Insufficient data for selected filters."

    # Ghost Fork (Forkball) metrics
    fork_data = filtered_df[filtered_df['pitch_name'] == 'Forkball']
    if not fork_data.empty:
        fork_usage = (len(fork_data) / total_pitches) * 100
        avg_fork_drop = fork_data['pfx_z_in'].mean()
        
        fork_text = f"**Signature Pitch (Ghost Fork):** Utilized **{fork_usage:.1f}%** of the time, this devastating out-pitch features massive depth, dropping on average **{abs(avg_fork_drop):.1f} inches**."
    else:
        fork_text = "**Signature Pitch:** Forkball not present in selected filters."

    # Affichage du rapport
    st.info(f"Based on a sample of {total_pitches} pitches:\n\n- {fb_text}\n- {fork_text}")
else:
    st.warning("Please select at least one pitch type.")

st.markdown("---")

# --- VISUALIZATIONS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Pitch Movement Profile (Break)")
    st.markdown("*(Catcher's POV: Horizontal vs Vertical Break in inches)*")
    fig_movement = px.scatter(
        filtered_df, 
        x='pfx_x_in', 
        y='pfx_z_in', 
        color='pitch_name',
        hover_data=['release_speed', 'events'],
        labels={'pfx_x_in': 'Horizontal Break (in)', 'pfx_z_in': 'Vertical Break (in)', 'pitch_name': 'Pitch Type'},
        opacity=0.7
    )
    # Lignes pour représenter le point 0 (centre)
    fig_movement.add_vline(x=0, line_dash="dash", line_color="gray")
    fig_movement.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_movement, use_container_width=True)

with col2:
    st.subheader("Velocity Distribution")
    fig_velo = px.box(
        filtered_df, 
        x='pitch_name', 
        y='release_speed', 
        color='pitch_name',
        labels={'release_speed': 'Velocity (mph)', 'pitch_name': 'Pitch Type'}
    )
    st.plotly_chart(fig_velo, use_container_width=True)

# --- DATA AGGREGATION TABLE ---
st.subheader("Pitch Characteristics Summary")
summary_df = filtered_df.groupby('pitch_name').agg(
    Count=('pitch_name', 'count'),
    Avg_Velocity_mph=('release_speed', 'mean'),
    Avg_Spin_Rate_rpm=('release_spin_rate', 'mean'),
    Avg_Horz_Break_in=('pfx_x_in', 'mean'),
    Avg_Vert_Break_in=('pfx_z_in', 'mean')
).reset_index()

# Formattage pour faire propre
summary_df['Avg_Velocity_mph'] = summary_df['Avg_Velocity_mph'].round(1)
summary_df['Avg_Spin_Rate_rpm'] = summary_df['Avg_Spin_Rate_rpm'].round(0)
summary_df['Avg_Horz_Break_in'] = summary_df['Avg_Horz_Break_in'].round(1)
summary_df['Avg_Vert_Break_in'] = summary_df['Avg_Vert_Break_in'].round(1)

# Calculer le % d'utilisation
summary_df['Usage_%'] = ((summary_df['Count'] / total_pitches) * 100).round(1)
summary_df = summary_df.sort_values(by='Usage_%', ascending=False)

st.dataframe(summary_df, use_container_width=True)