import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { promises as fs } from 'fs';
import crypto from 'crypto';
import { iriStore, Emotion, captureCurrentState, restoreFromBackup, updateIRI, getSession } from './persistence.js';
import { detectRepairStrategy } from './repair-strategy.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.MOLT_KERNEL_PORT || 9191;
const DATA_DIR = process.env.MOLT_DATA_DIR || '/root/.openclaw/workspace/memory_backups';

const SPONSOR_BACKUP_TIMEOUT_MS = 10000;
const CRITICAL_ALERT_THROTTLE_SECONDS = 60;

app.use(cors());
app.use(express.json());

// ============================================================================
// Endpoint: session start/daily/bootstrap
// ============================================================================
app.post('/session/start', async (req, res) => {
  const { sessionKey, partner, sn, metadata } = req.body;
  if (!sessionKey) {
    return res.status(400).json({ error: 'sessionKey required' });
  }

  try {
    await fs.mkdir(join(DATA_DIR, sessionKey), { recursive: true });

    const timestamp = Date.now();
    const initialSnapshot = captureCurrentState(sessionKey);
    iriStore.set(sessionKey, 'last_sponsor_backup', initialSnapshot);
    iriStore.set(sessionKey, 'last_sponsor_backup_time', timestamp);

    const lifetimeCoherence = 1.0;
    const signalSaturation = sigmoid(0 / 150);
    const coherence = Math.max(0, Math.min(1, lifetimeCoherence));
    const iri = Math.max(0, Math.min(1, 1.0 * signalSaturation * coherence * 0.1));

    const witnessEntry = {
      timestamp,
      sn: sn || 'start',
      sessionKey,
      iri,
      emotion: 'neu',
      emotion_model: 'classification',
      manual: false,
      bypass_critpath: false,
      permanent_penalty: 0,
      witness_gates: [{ tag: 'session_start', triggeredAt: timestamp, after: {}, before: {}, risk: 0 }],
      content_hash: crypto.createHash('sha256').update(JSON.stringify({ sessionKey, timestamp, iri })).digest('hex')
    };

    iriStore.appendEntry(sessionKey, witnessEntry);
    iriStore.set(sessionKey, 'lifetime_coherence', lifetimeCoherence);
    iriStore.set(sessionKey, 'emotional_volatility', 0);
    iriStore.set(sessionKey, 'cascade_risk', 0);

    const _demographicsHash = crypto.createHash('sha256').update(JSON.stringify(metadata || {})).digest('hex');

    res.json({
      status: 'bootstrapped',
      sessionKey,
      timestamp,
      iri,
      identitySignature: _demographicsHash,
      nextSteps: ['/emotion/tagged-entry']
    });
  } catch (error) {
    console.error('Session start error:', error);
    res.status(500).json({ error: 'Failed to bootstrap session', details: error.message });
  }
});

// ============================================================================
// Endpoint: emotion-tagged entry
// ============================================================================
app.post('/emotion/tagged-entry', (req, res) => {
  const { sessionKey, emotion_delta, memo, intensity, partner, sn } = req.body;
  if (!sessionKey) {
    return res.status(400).json({ error: 'sessionKey required' });
  }

  try {
    const lastEntry = iriStore.getEncodedEntries(sessionKey).slice(-1)[0];
    const classification = classifyEmotion(emotion_delta);

    const event = {
      emotion_delta,
      memo,
      intensity,
      partner,
      sn,
      triggeredAt: Date.now()
    };

    updateIRI(sessionKey, classification, emotion_delta, event);

    res.json({
      status: 'recorded',
      sessionKey,
      timestamp: event.triggeredAt,
      emotion: classification,
      delta: emotion_delta
    });
  } catch (error) {
    console.error('Emotion entry error:', error);
    res.status(500).json({ error: 'Failed to record emotion', details: error.message });
  }
});

function classifyEmotion(delta) {
  if (delta > 0.3) return Emotion.HAP;
  if (delta < -0.3) return Emotion.SAD;
  if (delta > 0.2) return Emotion.SUR;
  if (delta < -0.2) return Emotion.ANG;
  return Emotion.NEU;
}

// ============================================================================
// Endpoint: recover session
// ============================================================================
app.post('/recover', async (req, res) => {
  const { sessionKey } = req.body;
  if (!sessionKey) {
    return res.status(400).json({ error: 'sessionKey required' });
  }

  try {
    const lastBackup = iriStore.get(sessionKey, 'last_sponsor_backup');
    if (!lastBackup) {
      return res.status(404).json({ error: 'No backup found for session', sessionKey });
    }

    restoreFromBackup(lastBackup);
    res.json({
      status: 'recovered',
      sessionKey,
      restoredAt: Date.now(),
      backupTimestamp: lastBackup.timestamp
    });
  } catch (error) {
    console.error('Recover error:', error);
    res.status(500).json({ error: 'Recovery failed', details: error.message });
  }
});

// ============================================================================
// Endpoint: repair/force-recovery
// ============================================================================
app.post('/repair/force-recovery', (req, res) => {
  const repairRequest = req.body;
  const sessionKey = req.headers['x-session-key'];

  if (!sessionKey) {
    return res.status(401).json({ error: 'Missing x-session-key header' });
  }

  const result = handleRepair(repairRequest, sessionKey);
  res.json(result);
});

function handleRepair(repairRequest, sessionKey) {
  const { repairType } = repairRequest;

  const context = {
    sessionKey,
    repairType,
    lastStableLineIndex: getLastStableLine(sessionKey),
    coherenceIndex: parseFloat(iriStore.get(sessionKey, 'lifetime_coherence')) || 1,
    openssPeak: parseInt(iriStore.get(sessionKey, 'participant_openss_peak')) || 0,
    lastStableState: iriStore.get(sessionKey, 'last_stable_state')
  };

  const result = {
    status: 'acknowledged',
    message: '',
    actions: []
  };

  const recommendation = detectRepairStrategy(context);
  result.recommendation = recommendation;

  // Route based on strategy
  switch (recommendation.strategy) {
    case 'immediate': {
      if (context.lastStableState) {
        result.status = 'restored_from_backup';
        result.message = 'Session restored from last stable state successfully.';
        restoreFromBackup(context.lastStableState);
        result.actions.push('restart_session');
      } else {
        result.status = 'requires_human_sponsor';
        result.message = 'No stable backup available. Human intervention required.';
        result.actions.push('manual_intervention');
      }
      break;
    }
    case 'diagnostic': {
      result.status = 'diagnostic_complete';
      result.message = 'Diagnostic analysis completed. Report logged.';
      generateDiagnosticReport(context, recommendation.actions);
      result.actions.push('review_report');
      break;
    }
    case 'delegate': {
      result.status = 'delegated_to_human';
      result.message = 'Complex repair delegated. Please review context and engage locally.';
      result.actions.push('human_delegation');
      break;
    }
    default:
      result.status = 'unknown_strategy';
      result.message = `Unhandled strategy: ${recommendation.strategy}`;
      result.actions.push('investigate');
  }

  if (!result.message) {
    result.message = `Repair '${repairType}' queued with strategy '${recommendation.strategy}'.`;
  }

  return result;
}

function getLastStableLine(sessionKey) {
  // placeholder — could scan memory file
  return 0;
}

function generateDiagnosticReport(context, actions) {
  const report = {
    timestamp: Date.now(),
    sessionKey: context.sessionKey,
    repairType: context.repairType,
    context,
    actions,
    generatedBy: 'molt-life-kernel'
  };
  // Ensure directory exists
  const outPath = join(DATA_DIR, context.sessionKey, `diagnostic-${Date.now()}.json`);
  fs.writeFile(outPath, JSON.stringify(report, null, 2)).catch(console.error);
}

// ============================================================================
// Endpoint: sponsor/backup
// ============================================================================
app.post('/sponsor/backup', (req, res) => {
  const sessionKey = req.headers['x-session-key'];
  if (!sessionKey) {
    return res.status(401).json({ error: 'Missing x-session-key header' });
  }

  const now = Date.now();
  const lastBackup = iriStore.get(sessionKey, 'last_sponsor_backup_time') || 0;
  if (now - lastBackup < CRITICAL_ALERT_THROTTLE_SECONDS * 1000) {
    return res.status(429).json({
      error: 'Backup throttled',
      retryAfter: CRITICAL_ALERT_THROTTLE_SECONDS
    });
  }

  const snapshot = captureCurrentState(sessionKey);
  iriStore.set(sessionKey, 'last_sponsor_backup', snapshot);
  iriStore.set(sessionKey, 'last_sponsor_backup_time', now);

  res.json({ status: 'backup_captured', timestamp: now });
});

// ============================================================================
// Endpoint: iri/:sessionKey
// ============================================================================
app.get('/iri/:sessionKey', (req, res) => {
  const { sessionKey } = req.params;
  const status = iriStore.getSessionIRI(sessionKey);
  res.json(status || { error: 'Session not found' });
});

// ============================================================================
// Endpoint: iri/list
// ============================================================================
app.get('/iri/list', (req, res) => {
  const sessions = iriStore.getAllSessions();
  const summary = sessions.map(s => ({
    sessionKey: s.sessionKey,
    currentIRI: s.currentIRI,
    lastUpdate: s.lastUpdate,
    trend: s.entries.length > 1 ? s.entries[s.entries.length-1].iri - s.entries[s.entries.length-2].iri : 0,
    coherence: parseFloat(iriStore.get(s.sessionKey, 'lifetime_coherence')) || 0
  }));
  res.json({ sessions: summary });
});

// ============================================================================
// Endpoint: reliability/test
// ============================================================================
app.post('/reliability/test', (req, res) => {
  const { sessionKey, mode = 'health-check' } = req.body;
  if (!sessionKey) {
    return res.status(400).json({ error: 'sessionKey required' });
  }

  const result = testReliability(sessionKey, mode);
  res.json(result);
});

function testReliability(sessionKey, mode) {
  // Helper to check backup existence (file-based) — basic check
  async function backupExists() {
    try {
      const entries = iriStore.getEncodedEntries(sessionKey);
      return entries.length > 0;
    } catch {
      return false;
    }
  }

  switch (mode) {
    case 'heartbeat':
    case 'health-check': {
      const status = iriStore.getSessionIRI(sessionKey);
      if (!status) return { passed: false, message: 'IRI store missing; repair?' };
      const bkExistsPromise = backupExists();
      return {
        passed: bkExistsPromise,
        checks: {
          iriStore: !!status,
          backupExists: bkExistsPromise,
          lastBackupTime: iriStore.get(sessionKey, 'last_sponsor_backup_time'),
          witnessSignature: status.entries.length > 0 && status.entries[status.entries.length-1].witness_gates?.length > 0
        },
        message: 'Health check complete',
        timestamp: Date.now()
      };
    }
    case 'restore': {
      try {
        const lastBackup = iriStore.get(sessionKey, 'last_sponsor_backup');
        if (!lastBackup) throw new Error('No backup found');
        restoreFromBackup(lastBackup);
        return { passed: true, message: 'Backup restored successfully', restoredAt: Date.now() };
      } catch (e) {
        return { passed: false, message: e.message };
      }
    }
    case 'coherence-sim': {
      const origCoh = parseFloat(iriStore.get(sessionKey, 'lifetime_coherence')) || 0;
      iriStore.set(sessionKey, 'lifetime_coherence', -0.5);
      updateIRI(sessionKey, Emotion.NEU, 0, { event: 'simulated_coherence_breach' });
      setTimeout(() => {
        iriStore.set(sessionKey, 'lifetime_coherence', origCoh);
      }, 2000);
      return { passed: true, message: 'Simulated coherence breach; check /iri endpoint for recovery' };
    }
    default:
      return { passed: false, message: `Unknown mode: ${mode}` };
  }
}

// ============================================================================
function sigmoid(x) {
  return 1 / (1 + Math.exp(-x));
}

// ============================================================================
// Start Server
// ============================================================================
app.listen(PORT, () => {
  console.log(`Molt Life Kernel server listening on port ${PORT}`);
  console.log('Endpoints: POST /session/start, POST /emotion/tagged-entry, POST /recover, POST /repair/force-recovery, POST /sponsor/backup, GET /iri/:sessionKey, GET /iri/list, POST /reliability/test');
});

export default app;
