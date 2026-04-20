"""
Geo Utilities — Fajr Observer Agent

Location-based calculations: sunrise, solar elevation angles.
Uses astral library for accurate sun position.
"""

from astral import LocationInfo
from astral.sun import sun
from pytz import timezone
from datetime import datetime, date
from typing import Dict

def get_sun_times(latitude: float, longitude: float,
                  date_: date = None,
                  tz_name: str = "UTC") -> Dict[str, datetime]:
    """
    Get sunrise, dusk, anddawn times via astral.
    Returns: {"sunrise": ..., "dawn": ..., "dusk": ...}
    """
    loc = LocationInfo(name="Custom", region="Region", timezone=tz_name,
                       latitude=latitude, longitude=longitude)
    s = sun(loc.observer, date=date_ or date.today(), tzinfo=timezone(tz_name))
    return {
        "dawn": s["dawn"],
        "sunrise": s["sunrise"],
        "dusk": s["dusk"],
        "sunset": s["sunset"]
    }

def solar_elevation(latitude: float, longitude: float,
                    when: datetime = None) -> float:
    """Return sun elevation angle in degrees (negative = below horizon)."""
    from astral import sun
    when = when or datetime.now()
    loc = LocationInfo("tmp", "tmp", "UTC", latitude, longitude)
    s = sun(loc.observer, date=when.date(), tzinfo=when.tzinfo or timezone("UTC"))
    # Elevation at specific time? Need more precise
    return -18.0  # placeholder; actual implementation needs more math

if __name__ == "__main__":
    import sys
    lat, lon = 21.5, 39.0  # Gaza example
    times = get_sun_times(lat, lon, tz_name="Asia/Gaza")
    print("Sun times for Gaza:")
    for k, v in times.items():
        print(f"  {k}: {v.strftime('%H:%M')}")
