import streamlit as st
import pandas as pd
from pathlib import Path

# --- Inställningar för sidan ---
st.set_page_config(page_title="K Karaoke Låtlista", page_icon="🎤", layout="wide")

# --- Ladda in datan ---
# @st.cache_data gör att Streamlit sparar datan i minnet. 
# Då slipper den läsa in Excel-filen varje gång du trycker på en knapp!
@st.cache_data
def load_data():
    DATAPATH = Path('data')
    FILE_PATH = DATAPATH / 'Kareoke_Final.xlsx'
    
    if not FILE_PATH.exists():
        st.error(f"Kunde inte hitta filen: {FILE_PATH}")
        return pd.DataFrame()
        
    df = pd.read_excel(FILE_PATH, dtype={'ID': str})
    # Fyll i eventuella tomma fält så koden inte kraschar vid sökning
    df.fillna('Okänd', inplace=True)
    return df

df = load_data()

# --- Bygg gränssnittet ---
if not df.empty:
    st.title("🎤 K Karaoke Låtlista")
    st.markdown("Sök efter din favoritlåt eller filtrera på genre och årtionde för att hitta inspiration!")

    # Skapa tre kolumner bredvid varandra för sökfält och filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("🔍 Sök på artist eller låt", "")
        
    with col2:
        # Hämta alla unika genrer från filen och sortera i bokstavsordning
        genres = sorted(list(df['Genre'].unique()))
        selected_genres = st.multiselect("🎸 Filtrera på Genre", genres)
        
    with col3:
        # Hämta alla unika årtionden
        decades = sorted(list(df['Årtionde'].unique()))
        selected_decades = st.multiselect("🕺 Filtrera på Årtionde", decades)

    # --- Filtrera datan baserat på dina val ---
    filtered_df = df.copy()
    
    if search_query:
        # Sök i både Artist och Song (case=False gör att den struntar i stora/små bokstäver)
        mask = filtered_df['Artist'].str.contains(search_query, case=False, na=False) | \
               filtered_df['Song'].str.contains(search_query, case=False, na=False)
        filtered_df = filtered_df[mask]
        
    if selected_genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]
        
    if selected_decades:
        filtered_df = filtered_df[filtered_df['Årtionde'].isin(selected_decades)]

    # --- Visa resultatet ---
    st.markdown(f"**Hittade {len(filtered_df)} låtar:**")
    
    # Skriv ut tabellen. hide_index=True tar bort de fula radnumren längst till vänster
    st.dataframe(
        filtered_df[['ID', 'Artist', 'Song', 'Genre', 'Årtionde']], 
        use_container_width=True, 
        hide_index=True,
        height=600 # Gör tabellen lite högre så man ser många låtar direkt
    )