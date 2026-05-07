/**
 * Calculator Agent — Astronomical fallback (only if visual unavailable)
 * Uses standard prayer time calculations (not the primary source)
 */

const SunCalc = require('suncalc');

class CalculatorAgent {
  constructor(config) {
    this.location = config.location;
  }

  /**
   * Calculate prayer times as fallback
   * @param {string} prayer
   * @returns {Object} {time: Date, method: 'calculated', confidence: 0.5}
   */
  calculate(prayer) {
    const { latitude, longitude, timezone } = this.location;

    // Get sun position for today
    const times = SunCalc.getTimes(new Date(), latitude, longitude);

    // Approximate mapping (mujtahid approximation — NOT authoritative)
    // Primary source remains visual hadith signs
    let calcTime;
    switch(prayer) {
      case 'fajr':
        // Fajr ~ 1.5° before sunrise (approximate)
        calcTime = this.offsetTime(times.sunrise, -90); // 90 min before
        break;
      case 'dhuhr':
        calcTime = times.solarNoon;
        break;
      case 'asr':
        // Asr ~ shadow length = object (Shafi) or 2x (Hanafi)
        calcTime = this.offsetTime(times.solarNoon, 180); // ~3h after noon
        break;
      case 'maghrib':
        calcTime = times.sunset;
        break;
      case 'isha':
        // Isha ~ 1.5h after maghrib (approximate)
        calcTime = this.offsetTime(times.sunset, 90);
        break;
    }

    return {
      time: calcTime,
      method: 'calculated',
      confidence: 0.5, // lower than visual
      note: 'Fallback only; primary source is visual hadith signs'
    };
  }

  offsetTime(base, minutes) {
    return new Date(base.getTime() + minutes * 60 * 1000);
  }
}

module.exports = CalculatorAgent;
