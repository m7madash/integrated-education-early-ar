/**
 * Prayer Times by Sensory Signs — Main Entry Point
 * Based on Hadith: Sahih Bukhari 524, Sahih Muslim 639
 * Never automated worship — human confirmation required
 */

const ObserverAgent = require('./agents/observer');
const CalculatorAgent = require('./agents/calculator');
const VerifierAgent = require('./agents/verifier');
const NotifierAgent = require('./agents/notifier');
const indicators = require('./indicators.json');
const fs = require('fs');
const path = require('path');

class PrayerTimesSkill {
  constructor(config) {
    this.config = config;
    this.location = config.location;
    this.mazhab = config.mazhab || 'general';
    this.telegram = config.telegram || false;

    // Agents
    this.observer = new ObserverAgent(config);
    this.calculator = new CalculatorAgent(config);
    this.verifier = new VerifierAgent(indicators);
    this.notifier = new NotifierAgent(config);

    // Logging
    this.logFile = path.join(__dirname, 'data', 'observation_log.jsonl');
  }

  /**
   * Initialize skill
   */
  async init() {
    console.log('[Skill] Prayer Times by Signs initialized');
    console.log('[Skill] Location:', this.location.city);
    console.log('[Skill] Mazhab:', this.mazhab);
    console.log('[Skill] Source:', indicators.hadith_source.reference);
  }

  /**
   * Start continuous observation (run periodically)
   * @param {number} intervalMs — check every X milliseconds (e.g., 300000 = 5min)
   */
  startObservation(intervalMs = 300000) {
    this.intervalId = setInterval(() => {
      this.checkAllPrayers();
    }, intervalMs);

    console.log('[Skill] Observation started (every ' + (intervalMs/60000) + ' min)');
  }

  stopObservation() {
    if (this.intervalId) clearInterval(this.intervalId);
    console.log('[Skill] Observation stopped');
  }

  /**
   * Check all prayer times in sequence
   */
  async checkAllPrayers() {
    const prayers = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'];

    for (const prayer of prayers) {
      try {
        await this.checkPrayerTime(prayer);
      } catch (err) {
        console.error(`[Skill] Error checking ${prayer}:`, err.message);
      }
    }
  }

  /**
   * Check single prayer time
   */
  async checkPrayerTime(prayer) {
    console.log(`[Skill] Checking ${prayer}...`);

    // 1. Try visual observation first
    let observation = await this.observer.observe(prayer);

    // If visual not confident, fallback to calculation
    if (observation.confidence < 0.3) {
      console.log(`[Skill] Visual low confidence, calculating fallback for ${prayer}`);
      const calc = this.calculator.calculate(prayer);
      observation = {
        prayer,
        sign: 'calculated_time',
        confidence: 0.5,
        method: 'calculated',
        timestamp: calc.time.toISOString(),
        note: 'Fallback — visual not available'
      };
    }

    // 2. Verify against hadith criteria
    const verification = this.verifier.verify(prayer, observation);

    // 3. Log
    this.logObservation(observation, verification);

    // 4. Notify (but do NOT announce adhan)
    await this.notifier.notify(verification, observation);

    // 5. If high confidence visual, prompt human
    if (observation.method === 'visual' && observation.confidence >= 0.8) {
      console.log(`🚨 [Skill] ${prayer} sign DETECTED — Human muazzin must confirm and call adhan`);
    }

    return { observation, verification };
  }

  /**
   * Log to observation_log.jsonl
   */
  logObservation(observation, verification) {
    const entry = {
      timestamp: new Date().toISOString(),
      location: this.location.city,
      ...observation,
      verification,
      mazhab: this.mazhab,
      human_confirmed: false
    };

    fs.appendFileSync(this.logFile, JSON.stringify(entry) + '\n');
    console.log(`[Skill] Logged ${observation.prayer} (${observation.method})`);
  }

  /**
   * Manual human confirmation (called when human confirms sign)
   * @param {string} prayer
   * @param {string} sign
   */
  humanConfirm(prayer, sign) {
    console.log(`[Skill] Human confirmed ${prayer} by ${sign}`);
    // Here: could trigger adhan if configured (but we don't)
    // Only notify that human can now call adhan
  }
}

module.exports = PrayerTimesSkill;
