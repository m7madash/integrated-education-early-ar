/**
 * Notifier Agent — Sends alerts to Telegram (never calls adhan)
 * Human muazzin must confirm before any public announcement
 */

class NotifierAgent {
  constructor(config) {
    this.config = config;
    this.telegramEnabled = config.telegram || false;
  }

  /**
   * Notify observer that sign detected
   * @param {Object} verification - verification result
   * @param {Object} observation - original observation
   */
  async notify(verification, observation) {
    const message = this.formatMessage(verification, observation);

    if (this.telegramEnabled) {
      // Send to configured Telegram chat
      // Use message tool (but need channel config)
      // For now: log only
      console.log(`[Notifier] Would send Telegram: ${message}`);
    } else {
      console.log(`[Notifier] ${message}`);
    }
  }

  formatMessage(verification, observation) {
    return `
🕌 *的时间 الصلاة (Mark)*

⏰ الصلاة: ${observation.prayer}
✅ العلامة: ${observation.sign}
🎯 الثقة: ${Math.round(observation.confidence * 100)}%
📝 الطريقة: ${observation.method}

📚 المصدر: ${verification.hadith_reference}

🚨 **تنبيه:** المراجعة البشرية مطلوبة قبل الأذان.
    `.trim();
  }
}

module.exports = NotifierAgent;
