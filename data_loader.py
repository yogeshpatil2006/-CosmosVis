"""
CosmosVis - Data Loader & Preprocessing (data_loader.py)
Handles data ingestion, automated validation, cleaning, error handling,
feature engineering (Decades, Eras, Spaceports), and geopy physics enrichment.

Operates EXCLUSIVELY on authentic data uploaded by the user from the Kaggle
'Space_Corrected.csv' dataset (All Space Missions from 1957).
Zero synthetic, fake, or fallback data.
"""

import os
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from utils import calculate_distance_to_equator, calculate_earth_rotation_boost

# Mandatory columns required from the authentic Kaggle dataset
REQUIRED_COLUMNS = [
    "company name",
    "location",
    "datum",
    "detail",
    "status rocket",
    "status mission",
]


def validate_space_csv(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validates that the uploaded DataFrame contains the mandatory columns
    expected from the Kaggle 'All Space Missions from 1957' dataset.
    Returns (is_valid, error_message).
    """
    if df is None or df.empty:
        return False, "The uploaded file is empty. Please upload a valid Space Missions CSV dataset."

    # Normalize column names (strip spaces, lowercase)
    normalized_cols = {c.strip().lower(): c for c in df.columns}

    missing_cols = []
    for req in REQUIRED_COLUMNS:
        if req not in normalized_cols:
            missing_cols.append(req)

    if missing_cols:
        expected_str = ", ".join([f"'{c}'" for c in REQUIRED_COLUMNS])
        missing_str = ", ".join([f"'{c}'" for c in missing_cols])
        err = (
            f"Uploaded dataset is missing required columns: {missing_str}.\n"
            f"Expected standard Kaggle columns: {expected_str}."
        )
        return False, err

    return True, None


def get_spaceport_coords(loc_str: str) -> Tuple[float, float, str, str, bool, str]:
    """
    Maps launch locations from the Kaggle dataset to verified, official coordinates (WGS-84).
    Returns:
        (latitude, longitude, standardized_site_name, country, is_mapped, facility_type)

    Facility types:
        - 'Terrestrial Spaceport' (Fixed ground orbital launch complex)
        - 'Marine / Oceanic Platform' (Sea Launch platform, mobile barge, or naval submarine)
        - 'Unmapped Location' (Locations lacking reliable coordinate references)
    """
    l = str(loc_str).lower()

    # 1. Florida Space Coast, USA
    if "kennedy" in l or "lc-39" in l:
        return 28.5729, -80.6490, "Kennedy Space Center, FL", "USA", True, "Terrestrial Spaceport"
    elif any(k in l for k in ["cape canaveral", "slc-41", "slc-40", "slc-37", "slc-17", "slc-36", "lc-13", "lc-34", "lc-12", "lc-19", "lc-14", "lc-18", "lc-5", "lc-26", "slc-46"]):
        return 28.4889, -80.5778, "Cape Canaveral Space Force Station, FL", "USA", True, "Terrestrial Spaceport"
    
    # 2. California & Western Range, USA
    elif any(k in l for k in ["vandenberg", "slc-4e", "slc-6", "slc-2", "slc-3", "slc-8", "slc-576"]):
        return 34.7420, -120.5724, "Vandenberg Space Force Base, CA", "USA", True, "Terrestrial Spaceport"
    elif any(k in l for k in ["edwards", "mojave", "point mugu"]):
        return 35.0110, -118.1530, "Mojave Air and Space Port / Edwards, CA", "USA", True, "Terrestrial Spaceport"
    
    # 3. Virginia Mid-Atlantic, USA
    elif "wallops" in l:
        return 37.9402, -75.4664, "Wallops Flight Facility, VA", "USA", True, "Terrestrial Spaceport"
    
    # 4. Texas & New Mexico Commercial Sites, USA
    elif "boca chica" in l:
        return 25.9972, -97.1561, "Starbase, Boca Chica, TX", "USA", True, "Terrestrial Spaceport"
    elif "west texas" in l:
        return 31.4229, -104.7572, "Corn Ranch, West Texas, TX", "USA", True, "Terrestrial Spaceport"
    elif "spaceport america" in l or "new mexico" in l:
        return 32.9904, -106.9698, "Spaceport America, NM", "USA", True, "Terrestrial Spaceport"
    
    # 5. Alaska & Pacific Range, USA
    elif "pacific spaceport" in l or "alaska" in l or "kodiak" in l:
        return 57.4358, -152.3397, "Pacific Spaceport Complex, AK", "USA", True, "Terrestrial Spaceport"
    elif any(k in l for k in ["kwajalein", "omelek", "marshall islands", "reagan ballistic"]):
        return 9.0482, 167.7431, "Ronald Reagan Test Site, Kwajalein", "USA", True, "Terrestrial Spaceport"
    elif "pacific missile" in l or "kauai" in l:
        return 22.0233, -159.7833, "Pacific Missile Range Facility, Kauai, HI", "USA", True, "Terrestrial Spaceport"
    
    # 6. Kazakhstan & Russian Cosmodromes
    elif "baikonur" in l:
        return 45.9646, 63.3052, "Baikonur Cosmodrome", "Kazakhstan", True, "Terrestrial Spaceport"
    elif "plesetsk" in l:
        return 62.9256, 40.5778, "Plesetsk Cosmodrome", "Russia", True, "Terrestrial Spaceport"
    elif "kapustin yar" in l:
        return 48.5781, 45.7489, "Kapustin Yar Cosmodrome", "Russia", True, "Terrestrial Spaceport"
    elif "vostochny" in l:
        return 51.8844, 128.3340, "Vostochny Cosmodrome", "Russia", True, "Terrestrial Spaceport"
    elif "svobodny" in l:
        return 51.7944, 128.1181, "Svobodny Cosmodrome", "Russia", True, "Terrestrial Spaceport"
    elif "yasny" in l or "dombarovsky" in l:
        return 51.2069, 59.8500, "Yasny Cosmodrome", "Russia", True, "Terrestrial Spaceport"
    
    # 7. French & European Space Facilities
    elif any(k in l for k in ["guiana space", "kourou", "ela-", "els,", "elv-", "eld,"]):
        return 5.2390, -52.7680, "Guiana Space Centre, Kourou", "France", True, "Terrestrial Spaceport"
    elif "hammaguir" in l:
        return 31.0994, -3.0569, "Hammaguir Launch Site", "France", True, "Terrestrial Spaceport"
    
    # 8. China Satellite Launch Centers
    elif "jiuquan" in l:
        return 40.9606, 100.2982, "Jiuquan Satellite Launch Center", "China", True, "Terrestrial Spaceport"
    elif "taiyuan" in l:
        return 38.8491, 111.6080, "Taiyuan Satellite Launch Center", "China", True, "Terrestrial Spaceport"
    elif "xichang" in l:
        return 28.2460, 102.0281, "Xichang Satellite Launch Center", "China", True, "Terrestrial Spaceport"
    elif "wenchang" in l:
        return 19.6145, 110.9511, "Wenchang Satellite Launch Center", "China", True, "Terrestrial Spaceport"
    
    # 9. India
    elif "satish dhawan" in l or "sriharikota" in l:
        return 13.7200, 80.2300, "Satish Dhawan Space Centre (SHAR)", "India", True, "Terrestrial Spaceport"
    
    # 10. Japan
    elif "tanegashima" in l:
        return 30.4000, 130.9700, "Tanegashima Space Center", "Japan", True, "Terrestrial Spaceport"
    elif "uchinoura" in l:
        return 31.2519, 131.0822, "Uchinoura Space Center", "Japan", True, "Terrestrial Spaceport"
    
    # 11. New Zealand
    elif "mahia" in l or "m?" in l or "rocket lab" in l:
        return -39.2616, 177.8647, "Rocket Lab LC-1, Mahia Peninsula", "New Zealand", True, "Terrestrial Spaceport"
    
    # 12. Iran
    elif any(k in l for k in ["semnan", "imam khomeini"]):
        return 35.2346, 53.9210, "Semnan Space Center", "Iran", True, "Terrestrial Spaceport"
    elif "shahrud" in l:
        return 36.4278, 55.3325, "Shahrud Missile Test Site", "Iran", True, "Terrestrial Spaceport"
    
    # 13. Israel
    elif "palmachim" in l:
        return 31.8848, 34.6802, "Palmachim Airbase", "Israel", True, "Terrestrial Spaceport"
    
    # 14. Kenya (San Marco Project / Italy)
    elif "san marco" in l or "kenya" in l:
        return -2.9961, 40.2133, "San Marco Platform, Malindi", "Kenya", True, "Marine / Oceanic Platform"
    
    # 15. Australia
    elif "woomera" in l:
        return -30.9553, 136.5322, "RAAF Woomera Range Complex", "Australia", True, "Terrestrial Spaceport"
    
    # 16. North Korea
    elif "sohae" in l:
        return 39.6601, 124.7053, "Sohae Satellite Launching Station", "North Korea", True, "Terrestrial Spaceport"
    elif "tonghae" in l:
        return 40.8556, 129.6658, "Tonghae Satellite Launching Ground", "North Korea", True, "Terrestrial Spaceport"
    
    # 17. South Korea
    elif "naro" in l:
        return 34.4319, 127.5351, "Naro Space Center", "South Korea", True, "Terrestrial Spaceport"
    
    # 18. Brazil
    elif "alc" in l or "brazil" in l:
        return -2.3160, -44.3680, "Alcantara Launch Center", "Brazil", True, "Terrestrial Spaceport"
    
    # 19. Spain (Canary Islands)
    elif "gran canaria" in l or "gando" in l:
        return 27.9319, -15.3866, "Base Aerea de Gando, Gran Canaria", "Spain", True, "Terrestrial Spaceport"
    
    # 20. Mobile Marine / Submarine Launch Platforms (Explicitly Verified)
    elif "pacific ocean" in l or "odyssey" in l or "kiritimati" in l:
        # Sea Launch Odyssey equatorial position south of Hawaii
        return 0.0000, -154.0000, "Ocean Odyssey (Sea Launch)", "Multinational", True, "Marine / Oceanic Platform"
    elif "yellow sea" in l or "tai rui" in l:
        # China Mobile sea launch barge off Haiyang port in Yellow Sea
        return 36.6500, 121.2000, "Yellow Sea Mobile Barge", "China", True, "Marine / Oceanic Platform"
    elif "barents sea" in l:
        # Russian submarine Delta IV polygon in the Barents Sea off Kola Peninsula
        return 69.8000, 35.3000, "Barents Sea Submarine Area", "Russia", True, "Marine / Oceanic Platform"
    
    # 21. Explicit Unmapped / Unreliable Coordinates
    else:
        parts = [p.strip() for p in loc_str.split(",")]
        country_candidate = parts[-1] if parts else "Unknown"
        return np.nan, np.nan, f"Unmapped: {loc_str}", country_candidate, False, "Unmapped Location"


def assign_era(year: int) -> str:
    """Categorizes launch year into standardized historical space exploration eras."""
    if year < 1976:
        return "Space Race Era (1957–1975)"
    elif year < 2000:
        return "Space Shuttle & Mir Era (1976–1999)"
    elif year < 2015:
        return "Commercialization & Asian Expansion (2000–2014)"
    else:
        return "Megaconstellations & Reusable Rockets (2015–2020)"


def clean_and_enrich_kaggle_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw uploaded Kaggle Space_Corrected records without any synthetic or fake data.
    Preserves authentic values, extracts structured columns, calculates Geopy geodesics.
    """
    df = df.copy()

    # 1. Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # 2. Drop index columns if present
    drop_unnamed = [c for c in df.columns if "unnamed" in c.lower()]
    if drop_unnamed:
        df = df.drop(columns=drop_unnamed)

    # 3. Clean text mojibake in Location and Detail
    text_replacements = {
        "M? hia Peninsula": "Mahia Peninsula",
        "Alc?›ntara Launch Center": "Alcantara Launch Center",
        "Maranh?œo": "Maranhao",
    }
    for col in ["Location", "Detail"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
            for bad_str, good_str in text_replacements.items():
                df[col] = df[col].str.replace(bad_str, good_str, regex=False)

    # 4. Standardize Company Name
    if "Company Name" in df.columns:
        df["Company_Name"] = df["Company Name"].astype(str).str.strip()
    else:
        df["Company_Name"] = "Unknown Company"

    # 5. Parse Datum into DateTime, Year, Month, Decade, Era
    clean_datum = df["Datum"].astype(str).str.replace("UTC", "").str.strip()
    df["Launch_Date"] = pd.to_datetime(clean_datum, format="mixed", errors="coerce")
    
    # Drop rows where launch date is completely unparseable
    df = df.dropna(subset=["Launch_Date"]).copy()

    df["Year"] = df["Launch_Date"].dt.year.astype(int)
    df["Month"] = df["Launch_Date"].dt.month.astype(int)
    df["Decade"] = (df["Year"] // 10) * 10
    df["Decade_Label"] = df["Decade"].astype(str) + "s"
    df["Era"] = df["Year"].apply(assign_era)

    # 6. Extract Spaceport, Country, Verified Coordinates
    geo_results = [get_spaceport_coords(loc) for loc in df["Location"]]
    df["Latitude"] = [g[0] for g in geo_results]
    df["Longitude"] = [g[1] for g in geo_results]
    df["Spaceport"] = [g[2] for g in geo_results]
    df["Country"] = [g[3] for g in geo_results]
    df["Is_Mapped"] = [g[4] for g in geo_results]
    df["Facility_Type"] = [g[5] for g in geo_results]
    df["Launch_Site"] = df["Spaceport"]  # Alias for compatibility

    # 7. Split Detail into Rocket_Name and Payload_Mission
    def split_detail(detail_str):
        if "|" in str(detail_str):
            parts = str(detail_str).split("|", 1)
            return parts[0].strip(), parts[1].strip()
        return str(detail_str).strip(), "General Mission / Satellite"

    detail_splits = [split_detail(d) for d in df["Detail"]]
    df["Rocket_Name"] = [s[0] for s in detail_splits]
    df["Payload_Mission"] = [s[1] for s in detail_splits]
    df["Mission_Name"] = df["Detail"].astype(str).str.strip()

    # 8. Rocket Status: Active vs Retired
    if "Status Rocket" in df.columns:
        df["Rocket_Status"] = df["Status Rocket"].replace({
            "StatusActive": "Active",
            "StatusRetired": "Retired",
        }).fillna("Retired")
    else:
        df["Rocket_Status"] = "Unknown"

    # 9. Mission Status: Success, Failure, Partial Failure, Prelaunch Failure
    if "Status Mission" in df.columns:
        df["Mission_Status"] = df["Status Mission"].astype(str).str.strip()
    else:
        df["Mission_Status"] = "Unknown"

    df["Success_Binary"] = (df["Mission_Status"] == "Success").astype(int)

    # 10. Rocket Cost: Numeric float (in Millions USD)
    # Strictly NO synthetic imputation: rows with missing cost remain NaN!
    cost_col = None
    for cand in ["Rocket", " Rocket", "Launch_Cost"]:
        if cand in df.columns:
            cost_col = cand
            break

    if cost_col:
        clean_cost = df[cost_col].astype(str).str.replace(",", "").str.strip()
        df["Launch_Cost"] = pd.to_numeric(clean_cost, errors="coerce")
    else:
        df["Launch_Cost"] = np.nan

    df["Has_Cost_Data"] = df["Launch_Cost"].notna()

    # Cost category for available non-null cost data
    df["Cost_Category"] = pd.cut(
        df["Launch_Cost"],
        bins=[0, 30, 100, float("inf")],
        labels=["Light / Small (<$30M)", "Medium Payload ($30M–$100M)", "Heavy / Deep Space (>$100M)"]
    )

    # 11. Geopy Geodesic Physics Calculations (only for reliably mapped latitudes)
    valid_lats = [lat for lat in df["Latitude"].unique() if pd.notna(lat)]
    equator_dist_dict = {lat: calculate_distance_to_equator(lat) for lat in valid_lats}
    boost_dict = {lat: calculate_earth_rotation_boost(lat) for lat in valid_lats}

    df["Equator_Dist_km"] = df["Latitude"].map(equator_dist_dict)
    df["Earth_Rotation_Boost_mps"] = df["Latitude"].map(boost_dict)

    return df


def compute_metadata(df: pd.DataFrame) -> dict:
    """Computes operational dataset summary metadata from the cleaned real data."""
    if df.empty:
        return {
            "total_records": 0,
            "min_year": 1957,
            "max_year": 2020,
            "unique_countries": [],
            "unique_companies": [],
            "unique_spaceports": [],
            "overall_success_rate": 0.0,
            "missions_with_cost": 0,
            "median_cost": 0.0,
            "mapped_sites_count": 0,
            "unmapped_sites_count": 0,
            "unmapped_locations": [],
        }

    cost_sub = df[df["Has_Cost_Data"]]
    median_cost = round(float(cost_sub["Launch_Cost"].median()), 1) if not cost_sub.empty else 0.0

    mapped_df = df[df["Is_Mapped"]]
    unmapped_df = df[~df["Is_Mapped"]]

    return {
        "total_records": len(df),
        "min_year": int(df["Year"].min()),
        "max_year": int(df["Year"].max()),
        "unique_countries": sorted(df["Country"].unique().tolist()),
        "unique_companies": sorted(df["Company_Name"].unique().tolist()),
        "unique_spaceports": sorted(mapped_df["Spaceport"].unique().tolist()),
        "overall_success_rate": round(float(df["Success_Binary"].mean()) * 100, 2),
        "missions_with_cost": int(df["Has_Cost_Data"].sum()),
        "median_cost": median_cost,
        "mapped_sites_count": mapped_df["Spaceport"].nunique(),
        "unmapped_sites_count": unmapped_df["Location"].nunique(),
        "unmapped_locations": sorted(unmapped_df["Location"].unique().tolist()),
    }


def load_dataset_from_source(file_source) -> Tuple[Optional[pd.DataFrame], Optional[dict], Optional[str]]:
    """
    Loads dataset directly from an uploaded file object or file stream.
    Validates structure, cleans authentic data, and returns (df, metadata, error).
    No automatic fallback to any hardcoded dataset.
    """
    try:
        if file_source is None:
            return None, None, "No file provided."

        raw_df = pd.read_csv(file_source, encoding="utf-8")

        is_valid, err_msg = validate_space_csv(raw_df)
        if not is_valid:
            return None, None, err_msg

        cleaned_df = clean_and_enrich_kaggle_data(raw_df)
        metadata = compute_metadata(cleaned_df)
        return cleaned_df, metadata, None

    except Exception as e:
        return None, None, f"Error processing uploaded CSV file: {str(e)}"
