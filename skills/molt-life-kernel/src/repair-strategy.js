import { iriStore } from './persistence.js';

/**
 * Detects the optimal repair strategy based on context.
 *
 * Strategies:
 * - immediate: Use last stable backup
 * - diagnostic: Run analysis, flag for human review
 * - delegate: Complex issue, require human sponsorship
 */
export function detectRepairStrategy(context) {
  const {
    coherenceIndex = 1.0,
    openssPeak = 0,
    lastStableState
  } = context;

  // Check for coherence collapse (coherence < 0)
  if (coherenceIndex < 0) {
    if (lastStableState) {
      return {
        strategy: 'immediate',
        confidence: 0.9,
        actions: ['restore_backup', 'recompute_iri']
      };
    }
    // No backup available - human must intervene
    return {
      strategy: 'delegate',
      confidence: 1.0,
      actions: ['human_intervention_required', 'manual_context_review']
    };
  }

  // Check for emotional cascade risk (high openss_peak indicates multiple stressors)
  if (openssPeak >= 3) {
    return {
      strategy: 'diagnostic',
      confidence: 0.8,
      actions: ['analyze_cascade_pattern', 'identify_stress_triggers', 'recommend_modulation']
    };
  }

  // Check for witness signature gaps (missing witness gates on recent entries)
  const lastEntries = iriStore.getEncodedEntries(context.sessionKey).slice(-5);
  const missingWitness = lastEntries.some(e => !e.witness_gates || e.witness_gates.length === 0);
  if (missingWitness) {
    return {
      strategy: 'delegate',
      confidence: 0.7,
      actions: ['human_verification_required', 'witness_gate_audit']
    };
  }

  // Check backup recency
  const lastBackupTime = iriStore.get(context.sessionKey, 'last_sponsor_backup_time') || 0;
  const backupAgeHours = (Date.now() - lastBackupTime) / (1000 * 60 * 60);
  if (backupAgeHours > 24) {
    return {
      strategy: 'diagnostic',
      confidence: 0.6,
      actions: ['stale_backup_alert', 'recommend_fresh_backup', 'coherence_recalc']
    };
  }

  // Default: system is healthy, but repair was manually triggered
  return {
    strategy: 'diagnostic',
    confidence: 0.5,
    actions: ['full_health_check', 'coherence_audit', 'witness_integrity_check']
  };
}

/**
 * Weighted decision matrix for repair routing
 */
export function selectRepairPath(context) {
  let score = {
    immediate: 0,
    diagnostic: 0,
    delegate: 0
  };

  if (context.coherenceIndex !== undefined) {
    if (context.coherenceIndex < 0) {
      score.immediate += 2;
    } else if (context.coherenceIndex < 0.3) {
      score.diagnostic += 1;
    }
  }

  if (context.lastStableState) {
    score.immediate += 1;
  } else {
    score.delegate += 1;
  }

  if (context.openssPeak === 0) {
    score.immediate += 2;
  }

  const storeHealth = 'ok';
  if (storeHealth === 'degraded') {
    score.delegate += 2;
  } else if (storeHealth === 'down') {
    score.delegate += 3;
  }

  const maxScore = Math.max(score.immediate, score.diagnostic, score.delegate);
  if (maxScore === score.immediate) return 'immediate';
  if (maxScore === score.diagnostic) return 'diagnostic';
  return 'delegate';
}

/**
 * Get recommended repair action string from strategy.
 */
export function getRepairAction(strategy) {
  return `strategy:${strategy.strategy} conf:${strategy.confidence.toFixed(2)} actions:${strategy.actions.join(',')}`;
}
