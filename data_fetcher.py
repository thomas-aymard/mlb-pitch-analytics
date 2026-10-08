import pandas as pd
from pybaseball import statcast_pitcher
from pybaseball import playerid_lookup

print("Recherche de l'ID MLB de Kodai Senga...")
senga_lookup = playerid_lookup('senga', 'kodai')
senga_id = senga_lookup['key_mlbam'].values[0]

print(f"ID trouvé : {senga_id}. Téléchargement des données Statcast pour 2023...")
# On prend la saison 2023 complète (sa saison All-Star avec les Mets)
df_senga = statcast_pitcher('2023-03-30', '2023-10-01', senga_id)

print(f"Données téléchargées : {len(df_senga)} lancers trouvés.")

# Nettoyage de base : supprimer les lancers sans nom ou sans vitesse
df_senga = df_senga.dropna(subset=['pitch_name', 'release_speed'])

# Sauvegarde en CSV
df_senga.to_csv('senga_2023_statcast.csv', index=False)
print("Fichier 'senga_2023_statcast.csv' sauvegardé avec succès ! Vous pouvez maintenant lancer l'app Streamlit.")