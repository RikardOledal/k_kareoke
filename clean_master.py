import pandas as pd
import requests
import time
from pathlib import Path

DATAPATH = Path('data')
# Filen du vill läsa in:
INPUT_FILE = DATAPATH / 'Kareoke_Kategoriserad_Uppdaterad.xlsx'
# Filen vi sparar resultatet till (v2 så vi inte skriver över originalet av misstag):
OUTPUT_FILE = DATAPATH / 'Kareoke_Kategoriserad_Uppdaterad_v2.xlsx'

def get_song_info(artist, song):
    # 1. GRÄDDFILEN: Hantera specialkategorier direkt
    artist_lower = str(artist).lower()
    
    if 'jul' in artist_lower or 'christmas' in str(song).lower():
        return 'Julmusik', 'Okänt årtal'
    if 'finsk' in artist_lower:
        return 'Finsk musik', 'Okänt årtal'
    if 'barnvisor' in artist_lower or 'disney' in artist_lower:
        return 'Barn/Familj', 'Okänt årtal'
    if 'svenska hits' in artist_lower:
        return 'Svensk Pop', 'Okänt årtal'

    # 2. TVÄTTMASKINEN: Rensa bort tecken som stör iTunes
    # Vi gör om dem till strängar först för säkerhets skull
    clean_artist = str(artist)
    clean_song = str(song)

    # Ta bort "feat.", "ft." och liknande (iTunes hittar ofta bättre på bara huvudartisten)
    if ' feat' in clean_artist.lower():
        clean_artist = clean_artist.lower().split(' feat')[0]
    elif ' ft' in clean_artist.lower():
        clean_artist = clean_artist.lower().split(' ft')[0]

    # Byt ut problematiska tecken mot mellanslag, och ta bort apostrofer helt
    for char in [',', '.', '-', '&', '/', '(', ')']:
        clean_artist = clean_artist.replace(char, ' ')
        clean_song = clean_song.replace(char, ' ')
    
    clean_artist = clean_artist.replace("'", "").replace('´', '').replace('`', '')
    clean_song = clean_song.replace("'", "").replace('´', '').replace('`', '')

    # Bygg söksträngen och ta bort eventuella dubbla mellanslag
    search_term = f"{clean_artist} {clean_song}".replace('  ', ' ').strip()
    
    # 3. FRÅGA ITUNES
    url = f"https://itunes.apple.com/search?term={search_term}&media=music&limit=1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data['resultCount'] > 0:
            track = data['results'][0]
            genre = track.get('primaryGenreName', 'Okänd genre')
            release_date = track.get('releaseDate', '')
            decade = f"{(int(release_date[:4]) // 10) * 10}-tal" if release_date else 'Okänt årtal'
            return genre, decade
    except Exception as e:
        pass
    
    return 'Okänd', 'Okänd'

def main():
    if not INPUT_FILE.exists():
        print(f"FEL: Hittade inte filen {INPUT_FILE}")
        return

    print(f"Läser in {INPUT_FILE}...")
    # Läs in och se till att ID förblir text
    df = pd.read_excel(INPUT_FILE, dtype={'ID': str})
    
    # Skapa ett "filter" som letar efter rader där Genre är 'Okänd' 
    # ELLER där Årtionde innehåller ordet 'Okän' (täcker in 'Okänd' och 'Okänt årtal')
    mask = (df['Genre'] == 'Unknown') | (df['Årtionde'].astype(str).str.contains('Unknown', na=True))
    
    # Plocka ut bara de rader som fastnade i filtret
    df_missing = df[mask]
    total_missing = len(df_missing)
    
    if total_missing == 0:
        print("Grattis! Alla låtar har redan en Genre och ett Årtionde. Inget behöver uppdateras.")
        return
        
    print(f"Hittade {total_missing} låtar som saknar data. Börjar söka...")
    
    count = 0
    # iterrows() på df_missing ger oss samma 'index' som i huvudfilen (df)
    for index, row in df_missing.iterrows():
        count += 1
        artist = str(row.get('Artist', ''))
        # Kollar både 'Song' och 'Låt' ifall namnet ändrats
        song = str(row.get('Song', row.get('Låt', ''))) 
        
        print(f"Söker ({count}/{total_missing}): {artist} - {song}...")
        
        genre, decade = get_song_info(artist, song)
        
        # Om vi hittar den nu, uppdatera huvudtabellen (df) på exakt det indexet
        if genre != 'Okänd' and genre != 'Okänd genre':
            df.at[index, 'Genre'] = genre
            df.at[index, 'Årtionde'] = decade
            print(f"  -> Hittades! Lade till: {genre}, {decade}")
        
        time.sleep(1)

    print(f"\nSparar den uppdaterade listan till {OUTPUT_FILE}...")
    df.to_excel(OUTPUT_FILE, index=False)
    print("Klar! Nu kan du kolla in v2-filen.")

if __name__ == "__main__":
    main()