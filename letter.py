import pandas as pd
from pathlib import Path

DATAPATH = Path('data')
# Din ursprungliga fil (som hade rätt Å, Ä, Ö)
ORIGINAL_FILE = DATAPATH / 'Kareoke.csv'
# Din fil med alla iTunes-sökningar
KATEGORISERAD_FILE = DATAPATH / 'Kareoke_Kategoriserad_Uppdaterad_v2.xlsx'
# Vår nya, perfekta slutfil
FINAL_OUTPUT = DATAPATH / 'Kareoke_Final.xlsx'

def main():
    print("Läser in originalfilen (med de snygga bokstäverna)...")
    try:
        df_orig = pd.read_csv(ORIGINAL_FILE, sep=',', dtype={'ID': str}, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        # Det är hit den hoppar och då måste vi ha on_bad_lines här också!
        df_orig = pd.read_csv(ORIGINAL_FILE, sep=',', dtype={'ID': str}, encoding='latin1', on_bad_lines='skip')

    # Rensa kolumnnamn
    df_orig.columns = df_orig.columns.str.strip()
    
    print("Läser in den kategoriserade filen (med genrerna)...")
    df_kat = pd.read_excel(KATEGORISERAD_FILE, dtype={'ID': str})

    print("Slår ihop filerna...")
    # Vi skapar en koppling mellan varje ID och dess Genre/Årtionde
    genre_dict = dict(zip(df_kat['ID'], df_kat['Genre']))
    decade_dict = dict(zip(df_kat['ID'], df_kat['Årtionde']))

    # Vi klistrar in Genren och Årtiondet på rätt ID i originalfilen
    df_orig['Genre'] = df_orig['ID'].map(genre_dict).fillna('Okänd')
    df_orig['Årtionde'] = df_orig['ID'].map(decade_dict).fillna('Okänt årtal')

    print(f"Sparar den perfekta slutfilen till {FINAL_OUTPUT}...")
    df_orig.to_excel(FINAL_OUTPUT, index=False)
    print("Klar! Allt är ihopklistrat.")

if __name__ == "__main__":
    main()