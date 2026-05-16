"""
Sun Position Calculator — Fajr Observer Agent

Calculates solar elevation and azimuth for verification.
Can cross-check camera observations against astronomical predictions.
"""

import math
from datetime import datetime, timezone
from typing import Tuple

def solar_position(latitude: float, longitude: float, when: datetime) -> Tuple[float, float]:
    """
    Calculate solar elevation and azimuth angles.
    Returns: (elevation_deg, azimuth_deg)
    Simplified; for production use astral or pvlib.
    """
    # Convert to UTC if timezone-aware
    if when.tzinfo:
        when_utc = when.astimezone(timezone.utc)
    else:
        when_utc = when

    # Day of year
    n = when_utc.timetuple().tm_yday

    # Approximate solar declination
    declination = 23.45 * math.sin(math.radians(360/365 * (n - 81)))

    # Hour angle
    hour = when_utc.hour + when_utc.minute/60
    hour_angle = 15 * (hour - 12)  # degrees

    # Convert lat/lon to radians
    lat_rad = math.radians(latitude)
    ha_rad = math.radians(hour_angle)
    dec_rad = math.radians(declination)

    # Elevation
    sin_elevation = math.sin(lat_rad) * math.sin(dec_rad) + \
                    math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
    elevation = math.degrees(math.asin(sin_elevation))

    # Azimuth (simplified)
    cos_azimuth = (math.sin(dec_rad) - math.sin(lat_rad) * math.sin(elevation)) / \
                  (math.cos(lat_rad) * math.cos(elevation))
    azimuth = math.degrees(math.acos(cos_azimuth))
    # Adjust for afternoon vs morning
    if hour_angle > 0:
        azimuth = 360 - azimuth

    return elevation, azimuth


def is_dawn_window(latitude: float, longitude: float, when: datetime,
                   fajr_angle: float = -18.0) -> bool:
    """
    Is the sun currently within the fajr angle (e.g., -18°)?
    Returns True if solar elevation <= fajr_angle (negative below horizon).
    """
    elev, _ = solar_position(latitude, longitude, when)
    return elev <= fajr_angle


if __name__ == "__main__":
    # Demo for Gaza
    lat, lon = 21.5, 39.0
    now = datetime.now()
    elev, az = solar_position(lat, lon, now)
    print(f"[{now.strftime('%H:%M')}] Sun elevation: {elev:.2f}°, azimuth: {az:.2f}°")
    print(f"Below -18°? {is_dawn_window(lat, lon, now, -18)}")
