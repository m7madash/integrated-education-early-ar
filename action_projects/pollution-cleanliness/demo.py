#!/usr/bin/env python3
from src.pollution_cleanliness.tracker import EnvironmentMonitor, PollutionReading, CleanlinessInitiative

m = EnvironmentMonitor()
m.add_reading(PollutionReading('Gaza', '2026-04-19 12:00', 156, source='satellite'))
m.add_reading(PollutionReading('Jerusalem', '2026-04-19 12:30', 45, source='satellite'))
m.add_initiative(CleanlinessInitiative('غزة تنظيف shouldn't', 'Gaza', 'active', 150, '2026-04-15'))
print("\n✅ Demo run complete")
