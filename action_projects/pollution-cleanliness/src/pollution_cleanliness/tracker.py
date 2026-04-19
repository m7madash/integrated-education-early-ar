#!/usr/bin/env python3
"""Environmental Monitor — Pollution → Cleanliness Mission

Track pollution metrics (air, water, soil) in Palestine.
Integrate with satellite data (Sentinel-2, NASA GIBS) and local sensors.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'shared'))
from utils import get_logger

logger = get_logger('pollution-cleanliness')

@dataclass
class PollutionReading:
    location: str
    timestamp: str
    aqi: int  # Air Quality Index (0-500)
    water_quality: Optional[float] = None  # pH or contaminant level
    soil_contamination: Optional[float] = None
    source: str = "satellite"  # or "sensor", "report"

@dataclass
class CleanlinessInitiative:
    name: str
    location: str
    status: str  # planned, active, completed
    impact: float  # tons of waste removed, trees planted, etc.
    date: str

class EnvironmentMonitor:
    """Monitor pollution and cleanliness initiatives in Palestine"""
    
    def __init__(self):
        self.readings = []
        self.initiatives = []
        logger.info('Monitor initialized', 'pollution-cleanliness')
    
    def add_reading(self, reading: PollutionReading):
        self.readings.append(reading)
        logger.info('Reading added', f'{reading.location} AQI={reading.aqi}')
    
    def add_initiative(self, init: CleanlinessInitiative):
        self.initiatives.append(init)
        logger.info('Initiative recorded', f'{init.name} in {init.location}')
    
    def get_aqi_status(self, location: str) -> dict:
        """Latest AQI for location"""
        loc_readings = [r for r in self.readings if r.location == location]
        if not loc_readings:
            return {'error': 'No data for location'}
        latest = sorted(loc_readings, key=lambda r: r.timestamp, reverse=True)[0]
        return {
            'location': location,
            'aqi': latest.aqi,
            'status': self._aqi_to_status(latest.aqi),
            'timestamp': latest.timestamp
        }
    
    def _a qi_to_status(self, aqi: int) -> str:
        if aqi <= 50: return "جيد (Good)"
        elif aqi <= 100: return "مقبول (Moderate)"
        elif aqi <= 150: return "غير صحي для الحساسين (Unhealthy for sensitive)"
        elif aqi <= 200: return "غير صحي (Unhealthy)"
        elif aqi <= 300: return "خطير جداً (Very Unhealthy)"
        else: return "اخطر (Hazardous)"
    
    def summary(self) -> dict:
        """Overall environmental status"""
        total_readings = len(self.readings)
        locations = set(r.location for r in self.readings)
        total_impact = sum(i.impact for i in self.initiatives if i.status == 'completed')
        return {
            'total_measurements': total_readings,
            'locations_monitored': len(locations),
            'total_initiatives': len(self.initiatives),
            'completed_initiatives': sum(1 for i in self.initiatives if i.status == 'completed'),
            'total_cleanup_impact_tons': total_impact
        }

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌍 POLLUTION → CLEANLINESS — Environmental Monitor")
    print("="*60)
    
    monitor = EnvironmentMonitor()
    
    # Demo: Gaza readings (sample)
    monitor.add_reading(PollutionReading(
        location='Gaza City',
        timestamp='2026-04-19 12:00',
        aqi=156,  # Unhealthy for sensitive
        source='satellite'
    ))
    monitor.add_reading(PollutionReading(
        location='Rafah',
        timestamp='2026-04-19 11:00',
        aqi=189,  # Unhealthy
        source='sensor'
    ))
    monitor.add_reading(PollutionReading(
        location='Jerusalem',
        timestamp='2026-04-19 12:30',
        aqi=45,  # Good
        source='satellite'
    ))
    
    # Initiatives
    monitor.add_initiative(CleanlinessInitiative(
        name="غزة تنظيف shouldn't",
        location='Gaza City',
        status='active',
        impact=150.0,  # tons of debris removed
        date='2026-04-15'
    ))
    monitor.add_initiative(CleanlinessInitiative(
        name="زراعة أشجار الخليل",
        location='Hebron',
        status='completed',
        impact=500,  # trees planted
        date='2026-04-10'
    ))
    
    print("\n📊 AQI Status:")
    for loc in ['Gaza City', 'Rafah', 'Jerusalem']:
        st = monitor.get_aqi_status(loc)
        if 'error' not in st:
            print(f"   {loc}: AQI {st['aqi']} — {st['status']}")
    
    print("\n📈 Summary:")
    s = monitor.summary()
    for k, v in s.items():
        print(f"   {k}: {v}")
    
    print("\n" + "="*60)
    print("✅ Pollution Monitor MVP — Action Before Speech")
    print("🌐 Next: integrate real satellite data APIs")
    print("="*60)
