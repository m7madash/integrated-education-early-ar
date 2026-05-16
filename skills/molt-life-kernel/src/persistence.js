/**
 * persistence.js — Core IRI v6 implementation (plain JavaScript)
 */

import crypto from 'crypto';
import fs from 'fs/promises';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ============================================================================
// Configuration & Constants
// ============================================================================
const DATA_DIR = process.env.MOLT_DATA_DIR || '/root/.openclaw/workspace/memory_backups';
const ENTROPY_BASE = 150;

export const Emotion = {
  HAP: 'hap',
  SAD: 'sad',
  ANG: 'ang',
  FEA: 'fea',
  DIS: 'dis',
  SUR: 'sur',
  NEU: 'neu'
};

// ============================================================================
// IRI Entry & Session Store
// ============================================================================

// In-memory IRI entry factory
function createIRIEntry({ timestamp, sn, sessionKey, iri, emotion, tags = [], witness_gates = [], ...rest }) {
  return {
    timestamp,
    sn,
    sessionKey,
    iri,
    emotion,
    emotion_model: 'classification',
    manual: false,
    bypass_critpath: false,
    permanent_penalty: 0,
    content_hash: '',
    tags,
    witness_gates,
    ...rest
  };
}

// IRISession class (runtime only)
class IRISession {
  constructor(sessionKey) {
    this.sessionKey = sessionKey;
    this.entries = [];
    this.lastUpdate = 0;
    this.currentIRI = 0.15;
    this._lifetimeCoherence = 1.0;
    this._emotionalVolatility = 0;
    this._cascadeRisk = 0;
    this._lastStableState = undefined;
    this._lastBackupTime = 0;
    // Load from disk async
    this.loadFromDisk().catch(() => {});
  }

  async loadFromDisk() {
    try {
      const path = join(DATA_DIR, `${this.sessionKey}.json`);
      const data = await fs.readFile(path, 'utf8');
      const parsed = JSON.parse(data);
      this.entries = parsed.entries || [];
      this.currentIRI = parsed.currentIRI || 0.15;
      this._lifetimeCoherence = parsed.lifetimeCoherence || 1.0;
      this._emotionalVolatility = parsed.emotionalVolatility || 0;
      this._cascadeRisk = parsed.cascadeRisk || 0;
      this._lastStableState = parsed.lastStableState;
      this.lastUpdate = parsed.lastUpdate || Date.now();
    } catch (e) {
      // no file — fresh session
    }
  }

  async saveToDisk() {
    const path = join(DATA_DIR, `${this.sessionKey}.json`);
    const data = {
      entries: this.entries,
      currentIRI: this.currentIRI,
      lifetimeCoherence: this._lifetimeCoherence,
      emotionalVolatility: this._emotionalVolatility,
      cascadeRisk: this._cascadeRisk,
      lastStableState: this._lastStableState,
      lastUpdate: this.lastUpdate
    };
    await fs.mkdir(dirname(path), { recursive: true });
    await fs.writeFile(path, JSON.stringify(data, null, 2));
  }
}

const sessions = new Map();

function getSession(sessionKey) {
  if (!sessions.has(sessionKey)) {
    const s = new IRISession(sessionKey);
    sessions.set(sessionKey, s);
  }
  return sessions.get(sessionKey);
}

// ============================================================================
// Persistence Store API
// ============================================================================
const iriStore = {
  set(sessionKey, key, value) {
    const session = getSession(sessionKey);
    session[key] = value;
    session.saveToDisk().catch(console.error);
  },

  get(sessionKey, key) {
    const session = getSession(sessionKey);
    return session[key];
  },

  getEncodedEntries(sessionKey) {
    return getSession(sessionKey).entries;
  },

  appendEntry(sessionKey, entry) {
    const session = getSession(sessionKey);
    session.entries.push(entry);
    session.currentIRI = entry.iri;
    session.lastUpdate = entry.timestamp;
    session.saveToDisk().catch(console.error);
    return session;
  },

  getSessionIRI(sessionKey) {
    const session = getSession(sessionKey);
    const entries = session.entries;
    if (entries.length === 0) return null;
    const last30 = entries.slice(-30);
    const recent30Avg = last30.reduce((sum, e) => sum + e.iri, 0) / last30.length;
    return {
      sessionKey,
      currentIRI: session.currentIRI,
      lastUpdate: session.lastUpdate,
      entries,
      coherence: {
        lifetime: session._lifetimeCoherence,
        recent30: recent30Avg
      },
      participant: {
        openss_peak: 0,
        total_openss: 0
      },
      stability: {
        emotionalVolatility: session._emotionalVolatility,
        cascadeRisk: session._cascadeRisk
      }
    };
  },

  getAllSessions() {
    const result = [];
    for (const [key, session] of sessions.entries()) {
      result.push({
        sessionKey: key,
        currentIRI: session.currentIRI,
        lastUpdate: session.lastUpdate,
        entries: session.entries
      });
    }
    return result;
  },

  getEnvelope(sessionKey) {
    return this.get(sessionKey, '_envelope');
  },

  setEnvelope(sessionKey, envelope) {
    this.set(sessionKey, '_envelope', envelope);
  }
};

// ============================================================================
// Helper Functions
// ============================================================================
function sigmoid(x) {
  return 1 / (1 + Math.exp(-x));
}

function stableStringify(obj) {
  return JSON.stringify(obj, Object.keys(obj).sort());
}

function classifyEmotion(delta) {
  if (delta > 0.3) return Emotion.HAP;
  if (delta < -0.3) return Emotion.SAD;
  if (delta > 0.2) return Emotion.SUR;
  if (delta < -0.2) return Emotion.ANG;
  return Emotion.NEU;
}

function updateCoherence(session, net) {
  const old = session._lifetimeCoherence;
  if (net < 0) {
    session._consecutiveCoherenceBrev = (session._consecutiveCoherenceBrev || 0) + 1;
    const decay = 0.05 * (1 + session._consecutiveCoherenceBrev * 0.2);
    session._lifetimeCoherence = Math.max(-1, old - decay);
  } else if (net > 0) {
    session._lifetimeCoherence = Math.min(1, old + 0.02);
    session._consecutiveCoherenceBrev = 0;
  }
}

function detectCascadeRisk(session, net) {
  let cascadeRisk = session._cascadeRisk || 0;
  if (net < -0.5) {
    cascadeRisk = Math.min(1, cascadeRisk + 0.15);
  } else if (net > 0.3) {
    cascadeRisk = Math.max(0, cascadeRisk - 0.1);
  }
  session._cascadeRisk = cascadeRisk;
  return cascadeRisk;
}

function extractActiveTags(memo, intensity, emotion) {
  const tags = [];
  const ml = memo ? memo.toLowerCase() : '';
  if (ml.includes('error') || ml.includes('fail') || ml.includes('exception')) tags.push('error_signal');
  if (ml.includes('fix') || ml.includes('repair') || ml.includes('recover')) tags.push('repair_signal');
  if (ml.includes('?') || ml.includes('how can') || ml.includes('what')) tags.push('inquiry');

  if (intensity >= 0.7) tags.push('high_intensity');
  else if (intensity <= 0.3) tags.push('low_intensity');

  if (emotion === Emotion.HAP) tags.push('positive_affect');
  else if (emotion === Emotion.SAD || emotion === Emotion.ANG) tags.push('negative_affect');

  return tags;
}

// In updateIRI, after computing activeTags, attach them as boolean flags on event
// (used later for signal_saturation / behaviour_modulation)
function tagEvent(event, tags) {
  for (const tag of tags) {
    event[tag] = true;
  }
}

// ============================================================================
// Core Functions
// ============================================================================
/**
 * Computes new IRI and records an entry.
 */
export function updateIRI(sessionKey, emotion, delta, event) {
  const session = getSession(sessionKey);
  const timestamp = event.triggeredAt || Date.now();

  // Active tags (mutate event for storage convenience)
  const activeTags = extractActiveTags(event.memo, event.intensity, emotion);
  for (const tag of activeTags) {
    event[tag] = true;
  }

  // Update coherence
  updateCoherence(session, delta);

  // Cascade
  const cascadeRisk = detectCascadeRisk(session, delta);
  let finalDelta = delta;
  let finalEmotion = emotion;
  if (cascadeRisk > 0.7) {
    finalDelta = delta * 0.5;
    if (finalDelta < 0) finalEmotion = Emotion.NEU;
  }

  // Deduplicate
  const contentHashInput = stableStringify({
    memo: event.memo,
    emotion: finalEmotion,
    delta_emo: finalDelta,
    intensity: event.intensity,
    partner: event.partner,
    sn: event.sn
  });
  const contentHash = crypto.createHash('sha256').update(contentHashInput).digest('hex');

  const lastEntry = session.entries[session.entries.length - 1];
  if (lastEntry && lastEntry.content_hash === contentHash) {
    console.warn(`[coherence] Duplicate event skipped (session ${sessionKey})`);
    return session.currentIRI;
  }

  // Coherence drift
  const coherenceIndex = session._lifetimeCoherence;
  let coherenceDrift = 0;
  if (coherenceIndex < 0) {
    coherenceDrift = 1;
    console.log(`[coherence breach] IRI=${session.currentIRI.toFixed(3)} coherence=${coherenceIndex.toFixed(3)} — recovery_required`);
  }

  // Compute IRI v6
  const max_productivity = 1.0;
  const signal_saturation = sigmoid(activeTags.length / ENTROPY_BASE);
  const coherence = Math.max(0, Math.min(1, coherenceIndex));
  const iri = Math.max(0, Math.min(1, max_productivity * signal_saturation * coherence * 0.1));

  // Witness gates
  const witness_gates = [];
  if (cascadeRisk > 0.7) {
    witness_gates.push({
      tag: 'emotional_cascade_mitigation',
      triggeredAt: timestamp,
      after: { delta: finalDelta, emotion: finalEmotion },
      before: { delta, emotion },
      risk: cascadeRisk
    });
  }
  if (coherenceDrift) {
    witness_gates.push({
      tag: 'coherence_collapse_detected',
      triggeredAt: timestamp,
      after: { coherenceIndex },
      before: { coherenceIndex: session._lifetimeCoherence },
      risk: 1
    });
  }

  // Memory UID
  const memory_uid = event.memo ? crypto.createHash('sha256').update(event.memo).digest('hex').slice(0,16) : undefined;

  const record = {
    timestamp,
    sn: event.sn,
    sessionKey,
    iri,
    emotion: finalEmotion,
    emotion_model: 'classification',
    manual: false,
    bypass_critpath: false,
    permanent_penalty: 0,
    content_hash: contentHash,
    emotion_delta: finalDelta,
    emotion_delta_confidence: 1.0,
    confidence: 0.9,
    coherence_contribution: coherenceIndex,
    memory_uid,
    memory_penalty: 0.2,
    partner: event.partner,
    witness_gates,
    tags: activeTags
  };

  iriStore.appendEntry(sessionKey, record);
  return iri;
}

export function captureCurrentState(sessionKey) {
  const session = getSession(sessionKey);
  return {
    timestamp: Date.now(),
    sessionKey,
    entries: session.entries,
    currentIRI: session.currentIRI,
    coherence: session._lifetimeCoherence,
    envelope: iriStore.getEnvelope(sessionKey)
  };
}

export function restoreFromBackup(snapshot) {
  const session = getSession(snapshot.sessionKey);
  session.entries = snapshot.entries || [];
  session.currentIRI = snapshot.currentIRI || 0.15;
  session._lifetimeCoherence = snapshot.coherence || 1.0;
  session.lastUpdate = snapshot.timestamp;
  if (snapshot.envelope) iriStore.setEnvelope(snapshot.sessionKey, snapshot.envelope);
  session.saveToDisk().catch(console.error);
  console.log(`[recovery] Session ${snapshot.sessionKey} restored from backup`);
}

export function getSessionIRI(sessionKey) {
  return iriStore.getSessionIRI(sessionKey);
}

export function getAllSessions() {
  return iriStore.getAllSessions();
}

// Re-export all public API
export { getSession, iriStore };
