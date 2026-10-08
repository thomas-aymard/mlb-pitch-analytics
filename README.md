# ⚾ MLB Pitch Arsenal Analyzer (Statcast)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://thomas-aymard-mlb-analytics.streamlit.app/)

**Live Dashboard:** [thomas-aymard-mlb-analytics.streamlit.app](https://thomas-aymard-mlb-analytics.streamlit.app/)

An interactive web application built with **Python (Streamlit, Pandas, Plotly)** that analyzes MLB pitch tracking data (Statcast). 

This project was developed to demonstrate how raw pitching telemetry data can be processed, visualized, and transformed into actionable, automated scouting insights. The current dataset focuses on New York Mets starting pitcher **Kodai Senga's 2023 All-Star rookie season**.

## 🎯 Key Features
- **Automated Scouting Report:** Utilizes Pandas to calculate statistical thresholds (Velocity, Spin Rate, Usage %) and dynamically generates a situational text-based scouting summary.
- **Pitch Movement Profiling:** An interactive Plotly scatter plot mapping horizontal vs. vertical pitch break (from the catcher's perspective), illustrating pitch tunneling and aerodynamic deviation.
- **Velocity Distribution:** Boxplots evaluating velocity consistency, separation, and tiers across the pitcher's arsenal.
- **Interactive Matchup Filtering:** Filter telemetry data dynamically by pitch type and opposing batter stance (Right-Handed / Left-Handed) to uncover situational strategies.

## 🛠️ Technologies Used
- **Data Extraction:** `pybaseball` (MLB Statcast API wrapper)
- **Data Engineering:** `pandas` & `numpy` (Data manipulation, cleaning, and aggregation)
- **Data Visualization:** `plotly` (Interactive charts)
- **Deployment:** `streamlit` (Web application framework)

## 🚀 How to Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/thomas-aymard/mlb-pitch-analytics.git](https://github.com/thomas-aymard/mlb-pitch-analytics.git)
