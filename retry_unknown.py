import pandas as pd
import requests
import time
from pathlib import Path

DATAPATH = Path('data')
UNKNOWN_FILE = DATAPATH / 'Kareoke_Unknown.csv'
MASTER_FILE = DATAPATH / 'Kareoke_Categorized.xlsx'
OUTPUT_FILE = DATAPATH / 'Kareoke_Kategoriserad_Uppdaterad.xlsx'

def get_song_info(artist, song):
    url = f"https://itunes.apple.com/search?term={artist} {song}&media=music&limit=1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data['resultCount'] > 0:
            track = data['results'][0]
            genre = track.get('primaryGenreName', 'Okänd genre')
            release_date = track.get('releaseDate', '')
            decade = f"{(int(release_date[:4]) // 10) * 10}-tal" if release_date else 'Okänt årtal'
            return genre, decade
    except:
        pass
    return 'Okänd', 'Okänd'

def main():
    if not UNKNOWN_FILE.exists() or not MASTER_FILE.exists():
        print("Hittade inte filerna. Se till att både Unknown.csv och Master.xlsx finns i /data")
        return

    # 1. Läs in filerna
    print("Läser in filer...")
    df_master = pd.read_excel(MASTER_FILE, dtype={'ID': str})
    df_unknown = pd.read_csv(UNKNOWN_FILE, dtype=str)

    # 2. Kör sökningar på Unknown-låtarna
    print(f"Försöker igen med {len(df_unknown)} låtar...")
    
    for index, row in df_unknown.iterrows():
        artist = str(row['Artist'])
        song = str(row['Song'])
        id_val = str(row['ID'])
        
        print(f"Söker ({index+1}/{len(df_unknown)}): {artist} - {song}...")
        genre, decade = get_song_info(artist, song)
        
        if genre != 'Okänd':
            # Uppdatera master-filen där ID matchar
            mask = df_master['ID'] == id_val
            df_master.loc[mask, 'Genre'] = genre
            df_master.loc[mask, 'Årtionde'] = decade
            print(f"  -> Hittades! ({genre})")
        
        time.sleep(1)

    # 3. Spara den uppdaterade master-filen
    df_master.to_excel(OUTPUT_FILE, index=False)
    print(f"\nKlar! Uppdaterad lista sparad som {OUTPUT_FILE}")

if __name__ == "__main__":
    main()