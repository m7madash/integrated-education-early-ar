/**
 * Verifier Agent — Cross-checks observations against hadith criteria
 * Ensures sign matches description from indicators.json
 */

class VerifierAgent {
  constructor(indicators) {
    this.indicators = indicators;
  }

  /**
   * Verify an observation against hadith-based sign
   * @param {string} prayer
   * @param {Object} observation { sign, confidence, method }
   * @returns {Object} verification result
   */
  verify(prayer, observation) {
    const prayer Indicators = this.indicators.prayers[prayer];
    if (!prayerIndicators) {
      return { valid: false, reason: 'Unknown prayer' };
    }

    // Check if observed sign matches expected sign
    const expectedStart = prayerIndicators.start_sign.description;
    // In full impl: compare observation.sign against expected descriptors

    // For now, accept any observation with confidence > 0.6
    const isValid = observation.confidence >= 0.6;

    return {
      valid: isValid,
      confidence: observation.confidence,
      method: observation.method,
      required_verification: 'human_muazzin',
      hadith_reference: this.indicators.hadith_source.reference
    };
  }
}

module.exports = VerifierAgent;
