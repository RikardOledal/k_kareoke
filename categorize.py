import pandas as pd
import requests
import time
from pathlib import Path  # Importera Path från pathlib

# 1. Definiera din data-mapp
DATAPATH = Path('data')

INPUT_FILE = DATAPATH / 'Kareoke.csv'
OUTPUT_FILE = DATAPATH / 'Kareoke_Categorized.xlsx'

def get_song_info(artist, song):
    """Search iTunes API and fetch genre and year."""
    url = f"https://itunes.apple.com/search?term={artist} {song}&media=music&limit=1"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['resultCount'] > 0:
            track = data['results'][0]
            genre = track.get('primaryGenreName', 'Unknown genre')
            release_date = track.get('releaseDate', '')
            
            if release_date:
                year = int(release_date[:4])
                decade = f"{(year // 10) * 10}-tal"
            else:
                decade = 'Unknown decade'
                
            return genre, decade
    except Exception as e:
        print(f"An error occurred while searching for {artist} - {song}: {e}")
        
    return 'Unknown', 'Unknown'

def main():
    print("Reading in the file...")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8', dtype=str, on_bad_lines='skip')
    
    # För att testa skriptet snabbt, ta bort '#' på raden nedanför så kör den bara de 10 första låtarna.
    # df = df.head(200)

 # Rensa bort eventuella mellanslag i kolumnnamnen
    df.columns = df.columns.str.strip()
    
    expected_cols = ['ID', 'Artist', 'Song']
    missing_cols = [c for c in expected_cols if c not in df.columns]
    
    if missing_cols:
        print(f"ERROR: Did not find columns: {missing_cols}")
        print(f"Actual columns in file: {list(df.columns)}")
        return

    genres = []
    decades = []
    
    total_songs = len(df)
    print(f"Found {total_songs} songs. Starting to fetch data from iTunes...")
    
    for index, row in df.iterrows():
        artist = str(row['Artist'])
        song = str(row['Song'])
        
        # Logga var 10:e sökning
        if (index + 1) % 10 == 0 or index == 0:
            print(f"Söker ({index + 1}/{total_songs}): {artist} - {song}...")

        genre, decade = get_song_info(artist, song)
        genres.append(genre)
        decades.append(decade)

        time.sleep(1)
        
    # Lägg till de nya kolumnerna i tabellen
    df['Genre'] = genres
    df['Årtionde'] = decades

    unknown_df = df[df['Genre'] == 'Unknown']
    
    if not unknown_df.empty:
        UNKNOWN_FILE = DATAPATH / 'Kareoke_Unknown.csv'
        unknown_df[['ID', 'Artist', 'Song']].to_csv(UNKNOWN_FILE, index=False, sep=',', encoding='utf-8')
        print(f"Done! {len(unknown_df)} songs could not be found and were saved to {UNKNOWN_FILE}")
    else:
        print("All songs were found! No 'Unknown' file needed.")
    
    # Spara resultatet till en ny Excel-fil
    print(f"Saving the results to {OUTPUT_FILE}...")
    df.to_excel(OUTPUT_FILE, index=False)
    print("Done! You can now open your new Excel file.")

if __name__ == "__main__":
    main()