import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.pollution_cleanliness.tracker import EnvironmentMonitor, PollutionReading, CleanlinessInitiative

def test_aqi_status():
    m = EnvironmentMonitor()
    m.add_reading(PollutionReading('TestCity', '2026-04-19', 120))
    st = m.get_aqi_status('TestCity')
    assert st['aqi'] == 120
    assert 'خطير' in st['status'] or 'Unhealthy' in st['status']
    print("✅ AQI status works")

def test_summary():
    m = EnvironmentMonitor()
    m.add_reading(PollutionReading('A', '2026-04-19', 100))
    m.add_reading(PollutionReading('B', '2026-04-19', 80))
    m.add_initiative(CleanlinessInitiative('Cleanup', 'A', 'completed', 200, '2026-04-19'))
    s = m.summary()
    assert s['total_measurements'] == 2
    assert s['completed_initiatives'] == 1
    print("✅ Summary metrics work")

if __name__ == '__main__':
    test_aqi_status()
    test_summary()
    print("\n✅ All tests passed!")
