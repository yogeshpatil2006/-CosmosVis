"""
CosmosVis - Geospatial Utilities (utils.py)
Provides geopy-powered distance calculations, orbital physics helpers,
and spatial proximity analyses for spaceports and launch sites worldwide.
"""

import math
from typing import Dict, List, Optional, Tuple
from geopy.distance import geodesic
import pandas as pd


EARTH_EQUATORIAL_ROTATION_SPEED_MPS = 465.1  # meters per second at 0 deg latitude


def calculate_geodesic_distance(
    coord1: Tuple[float, float],
    coord2: Tuple[float, float]
) -> float:
    """
    Computes geodesic distance between two coordinate tuples (lat, lon) in kilometers
    using WGS-84 ellipsoidal geometry via geopy.
    """
    try:
        return geodesic(coord1, coord2).kilometers
    except Exception:
        # Fallback Haversine if coordinate issue
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371.0 * c


def calculate_distance_to_equator(latitude: float) -> float:
    """
    Computes the shortest geodesic surface distance from a given latitude to the Equator in km.
    """
    return geodesic((latitude, 0.0), (0.0, 0.0)).kilometers


def calculate_earth_rotation_boost(latitude: float) -> float:
    """
    Calculates the tangential rotational velocity boost provided by Earth's rotation
    at a given latitude in m/s:
    v = 465.1 * cos(latitude)
    This directly reduces required rocket delta-v for prograde orbital insertions!
    """
    rad = math.radians(abs(latitude))
    boost_mps = EARTH_EQUATORIAL_ROTATION_SPEED_MPS * math.cos(rad)
    return round(boost_mps, 1)


def find_nearest_launch_sites(
    target_coord: Tuple[float, float],
    sites_df: pd.DataFrame,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Finds the N closest orbital launch facilities from any target coordinate (lat, lon).
    Returns DataFrame with distances in km and miles, plus Earth rotation assist metrics.
    """
    results = []
    unique_sites = sites_df.drop_duplicates(subset=["Launch_Site"]).copy()

    for _, row in unique_sites.iterrows():
        site_coord = (row["Latitude"], row["Longitude"])
        dist_km = calculate_geodesic_distance(target_coord, site_coord)
        dist_miles = dist_km * 0.621371
        eq_dist = calculate_distance_to_equator(row["Latitude"])
        boost = calculate_earth_rotation_boost(row["Latitude"])

        results.append({
            "Launch_Site": row["Launch_Site"],
            "Country": row["Country"],
            "Latitude": row["Latitude"],
            "Longitude": row["Longitude"],
            "Distance_km": round(dist_km, 1),
            "Distance_miles": round(dist_miles, 1),
            "Equator_Distance_km": round(eq_dist, 1),
            "Rotation_Boost_mps": boost,
        })

    res_df = pd.DataFrame(results).sort_values("Distance_km").head(top_n).reset_index(drop=True)
    return res_df


def compute_site_pair_distance(
    site_a: str,
    site_b: str,
    sites_df: pd.DataFrame
) -> Optional[Dict[str, float]]:
    """
    Computes geodesic distance between two specified spaceports.
    """
    sub_a = sites_df[sites_df["Launch_Site"] == site_a]
    sub_b = sites_df[sites_df["Launch_Site"] == site_b]

    if sub_a.empty or sub_b.empty:
        return None

    coord_a = (sub_a.iloc[0]["Latitude"], sub_a.iloc[0]["Longitude"])
    coord_b = (sub_b.iloc[0]["Latitude"], sub_b.iloc[0]["Longitude"])

    dist_km = calculate_geodesic_distance(coord_a, coord_b)
    dist_miles = dist_km * 0.621371

    return {
        "site_a": site_a,
        "site_b": site_b,
        "distance_km": round(dist_km, 1),
        "distance_miles": round(dist_miles, 1),
    }
