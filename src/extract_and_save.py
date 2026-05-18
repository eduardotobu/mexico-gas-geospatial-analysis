import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime

# 1. Define URLs and File Paths
PRICES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/prices"
PLACES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/places"
DATA_FILE = "data/historical_gas_prices.csv"

def fetch_and_parse_xml(url):
    """Fetches XML from a URL and returns the root element."""
    response = requests.get(url)
    response.raise_for_status() # Raises an error if the download fails
    return ET.fromstring(response.content)

def main():
    print(f"Starting extraction for {datetime.now().strftime('%Y-%m-%d')}...")
    
    # 2. Fetch the data
    prices_root = fetch_and_parse_xml(PRICES_URL)
    places_root = fetch_and_parse_xml(PLACES_URL)
    
    # 3. Parse Locations (Latitude and Longitude)
    # Note: CRE XML structure uses 'place' tags. You may need to inspect the exact 
    # XML tree to adjust these tags if the CRE changes their schema.
    places_data = []
    for place in places_root.findall('.//place'):
        place_id = place.attrib.get('place_id')
        location = place.find('location')
        if location is not None:
            x = location.find('x').text if location.find('x') is not None else None
            y = location.find('y').text if location.find('y') is not None else None
            places_data.append({'place_id': place_id, 'longitude': x, 'latitude': y})
            
    df_places = pd.DataFrame(places_data)

    # 4. Parse Prices
    prices_data = []
    for place in prices_root.findall('.//place'):
        place_id = place.attrib.get('place_id')
        for gas_price in place.findall('gas_price'):
            gas_type = gas_price.attrib.get('type')
            price = gas_price.text
            prices_data.append({
                'place_id': place_id, 
                'gas_type': gas_type, 
                'price': price
            })
            
    df_prices = pd.DataFrame(prices_data)

    # 5. Merge and Clean Data
    # Inner join so we only keep stations where we have BOTH the location and the price
    df_master = pd.merge(df_prices, df_places, on='place_id', how='inner')
    
    # Add a timestamp column so we can track inflation over time
    df_master['date_extracted'] = datetime.now().strftime('%Y-%m-%d')

    # 6. Save to CSV (Append Mode)
    # If the file exists, append without headers. If it doesn't, create it with headers.
    file_exists = os.path.isfile(DATA_FILE)
    df_master.to_csv(DATA_FILE, mode='a', index=False, header=not file_exists)
    
    print(f"Success! {len(df_master)} records appended to {DATA_FILE}.")

if __name__ == "__main__":
    main()