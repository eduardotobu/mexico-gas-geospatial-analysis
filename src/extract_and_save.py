import logging
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional, Union

# Setup basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MX_TZ = ZoneInfo("America/Mexico_City")

# 1. Define URLs and File Paths
PRICES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/prices"
PLACES_URL = "https://publicacionexterna.azurewebsites.net/publicaciones/places"
INTERIM_DIR = "data/interim"

def fetch_and_parse_xml(url: str) -> ET.Element:
    """Fetches XML from a URL and returns the root element."""
    logger.debug(f"Fetching XML data from {url}...")
    response = requests.get(url)
    response.raise_for_status() 
    return ET.fromstring(response.content)

def merge_and_clean_gas_data(
    df: pd.DataFrame,
    df_places: pd.DataFrame,
    extraction_date: str,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Merges gas prices data with gas station location data and appends an extraction date.

    Args:
        df (pd.DataFrame): The primary DataFrame containing gas prices. Must have a 'place_id' column.
        df_places (pd.DataFrame): The secondary DataFrame containing place locations. Must have a 'place_id' column.
        extraction_date (str): The formatted date string to append as a new 'date' column.
        inplace (bool, optional): Whether to modify the primary DataFrame in place. Defaults to False.

    Returns:
        pd.DataFrame: The merged and cleaned DataFrame containing both price and location data.

    Raises:
        ValueError: If 'place_id' is missing from either of the input DataFrames.
        Exception: If an unexpected error occurs during processing.

    Example:
        >>> df_prices = pd.DataFrame({'place_id': ['1'], 'gas_type': ['regular'], 'price': ['20.5']})
        >>> df_places = pd.DataFrame({'place_id': ['1'], 'name': ['Station A'], 'latitude': ['25.0'], 'longitude': ['-100.0']})
        >>> merged_df = merge_and_clean_gas_data(df_prices, df_places, '2026-05-23')
        >>> list(merged_df.columns)
        ['place_id', 'gas_type', 'price', 'name', 'latitude', 'longitude', 'date']
    """
    
    # 1. Fail fast input validation
    if 'place_id' not in df.columns:
        raise ValueError("The primary DataFrame 'df' must contain a 'place_id' column.")
    if 'place_id' not in df_places.columns:
        raise ValueError("The secondary DataFrame 'df_places' must contain a 'place_id' column.")

    # 2. Inplace logic
    if not inplace:
        df = df.copy()

    logger.debug("Starting processing...")

    try:
        # 3. Core logic
        # Inner join so we only keep stations where we have BOTH the location and the price
        df = pd.merge(df, df_places, on='place_id', how='inner')
        
        # Add a timestamp column so we can track inflation over time
        df['date'] = extraction_date
        
        logger.info("Processing complete. Dataframes successfully merged.")

    except Exception as e:
        logger.exception("Unexpected error occurred.")
        raise e

    return df

def main() -> None:
    now = datetime.now(MX_TZ)
    today_str = now.strftime('%Y-%m-%d')
    logger.info(f"Starting extraction for {today_str} (Mexico City time)...")
    
    try:
        # 2. Fetch the data
        prices_root = fetch_and_parse_xml(PRICES_URL)
        places_root = fetch_and_parse_xml(PLACES_URL)
        
        # 3. Parse Locations (Latitude and Longitude)
        places_data: List[Dict[str, Optional[str]]] = []
        for place in places_root.findall('.//place'):
            place_id = place.attrib.get('place_id')
            name = place.find('name').text if place.find('name') is not None else None
            cre_id = place.find('cre_id').text if place.find('cre_id') is not None else None
            location = place.find('location')
            
            if location is not None:
                x = location.find('x').text if location.find('x') is not None else None
                y = location.find('y').text if location.find('y') is not None else None
                places_data.append({
                    'place_id': place_id, 
                    'name': name, 
                    'cre_id': cre_id, 
                    'longitude': x, 
                    'latitude': y
                })
                
        df_places = pd.DataFrame(places_data)

        # 4. Parse Prices
        prices_data: List[Dict[str, Optional[str]]] = []
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

        # 5. Merge and Clean Data using the templated function
        df_master = merge_and_clean_gas_data(
            df=df_prices, 
            df_places=df_places, 
            extraction_date=today_str,
            inplace=False
        )

        # 6. Save to Parquet (one file per day)
        os.makedirs(INTERIM_DIR, exist_ok=True)
        output_file = os.path.join(INTERIM_DIR, f"gas_prices_{today_str}.parquet")
        df_master.to_parquet(output_file, index=False)
        
        logger.info(f"Success! {len(df_master)} records saved to {output_file}.")
        
    except Exception as e:
        logger.exception("The data extraction pipeline failed.")
        raise e

if __name__ == "__main__":
    main()