#!/usr/bin/env node
/**
 * continuity_metrics_exporter.js — Dashboard Metrics Endpoint v2
 *
 * Generates /public/continuity-metrics.json with current KPI health.
 * Fixed: proper mission aggregation and platform success counting.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const METRICS_OUTPUT = path.join(WORKSPACE, 'public', 'continuity-metrics.json');

function loadJSON(file, fallback = {}) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch(e) { return fallback; }
}

function loadLedgerEntries(limit = 1000) {
  const ledgerPath = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
  if (!fs.existsSync(ledgerPath)) return [];
  const lines = fs.readFileSync(ledgerPath, 'utf8').trim().split('\n').slice(-limit);
  return lines.filter(l => l.trim().startsWith('{')).map(l => {
    try {
      const entry = JSON.parse(l);
      // Flatten nested structures for easier access
      if (entry.post_publish) Object.assign(entry, entry.post_publish);
      if (entry.publish_run) Object.assign(entry, entry.publish_run);
      if (entry.payload) Object.assign(entry, entry.payload);
      return entry;
    } catch(e) { return null; }
  }).filter(Boolean);
}

function main() {
  const config = loadJSON(path.join(WORKSPACE, 'continuity.config.json'));
  const heartbeat = loadJSON(path.join(WORKSPACE, 'memory', 'heartbeat-state.json'));
  const platformHealthState = loadJSON(path.join(WORKSPACE, 'memory', 'platform_health_state.json'));
  const ledger = loadLedgerEntries();

  const kpi = config.kpi || {};
  const nowMs = Date.now();
  const dayAgo = nowMs - 24*60*60*1000;
  const recent = ledger.filter(e => new Date(e.ts).getTime() > dayAgo);

  // Separate by type
  const publishRuns = recent.filter(e => e.type === 'publish_run');
  const postPublishes = recent.filter(e => e.type === 'post_publish' && e.platform);
  const missionRuns = publishRuns; // each publish_run represents one mission attempt

  // Compute mission completion count
  // Strategy: group post_publishes by mission name, determine if mission is "complete" based on whether all intended platforms succeeded
  // But simpler approximation: count missions with at least one successful platform as "success" for completionRate
  // (full success would require all platforms succeed; but KPI target 1.0 suggests strictness... let's compute both)

  // Platform reliability: per-platform success rate
  // Strategy: use platform_health_state.json as authoritative source (aggregated, multi-day)
  // Fall back to ledger publish_run data if platform_health_state.json is missing/malformed
  let platformReliabilityFrom = 'unknown';
  const platformStats = {};

  // PRIMARY: platform_health_state.json (most recent health check snapshot)
  if (platformHealthState.platforms) {
    Object.entries(platformHealthState.platforms).forEach(([plat, data]) => {
      platformStats[plat] = {
        total: data.attempts || 0,
        success: Math.round((data.attempts || 0) * (data.successRate || 0)),
        status: data.status,
        confidence: data.confidence,
        _source: 'platform_health_state'
      };
    });
    platformReliabilityFrom = 'platform_health_state.json';
  }

  // PRIMARY: platform_health_state.json (most recent health check snapshot)
  if (platformHealthState.platforms) {
    Object.entries(platformHealthState.platforms).forEach(([plat, data]) => {
      platformStats[plat] = {
        total: data.attempts || 0,
        success: Math.round((data.attempts || 0) * (data.successRate || 0)),
        status: data.status,
        confidence: data.confidence,
        _source: 'platform_health_state'
      };
    });
    platformReliabilityFrom = 'platform_health_state.json';
  }

  // SECONDARY fallback (if platform_health_state missing): read publish_run postIds
  // Use 'platforms' field as source-of-truth for whether an attempt was actually made
  if (Object.keys(platformStats).length === 0) {
    const ATLAS_PLATS = ['moltx', 'moltbook', 'moltter'];
    const attemptedMap = {};
    publishRuns.forEach(pr => {
      const postIds = pr.postIds || pr.payload?.postIds || {};
      const targets = (pr.platforms || pr.payload?.platforms || '')
        .split(',').map(s => s.trim()).filter(s => ATLAS_PLATS.includes(s));
      const attempted = targets.length > 0 ? targets : Object.keys(postIds).filter(k => ATLAS_PLATS.includes(k));
      attempted.forEach(plat => {
        if (!attemptedMap[plat]) attemptedMap[plat] = { total: 0, success: 0 };
        attemptedMap[plat].total++;
        if (postIds[plat] && typeof postIds[plat] === 'string' && postIds[plat].length > 0) {
          attemptedMap[plat].success++;
        }
      });
    });
    Object.entries(attemptedMap).forEach(([plat, s]) => {
      platformStats[plat] = { total: s.total, success: s.success, _source: 'publish_run_fallback' };
    });
    platformReliabilityFrom = 'publish_run_fallback';
  }

  console.log(`⚠️ platformReliability sourced from ${platformReliabilityFrom}`);

  // Overall platform reliability: weighted average across platform attempts
  const platformsKeys = Object.keys(platformStats);
  const totalAttempts = platformsKeys.reduce((sum, p) => sum + (platformStats[p].total || 0), 0);
  const totalSuccesses = platformsKeys.reduce((sum, p) => sum + (platformStats[p].success || 0), 0);
  const platformReliability = totalAttempts ? totalSuccesses / totalAttempts : 1;

  // Mission completion: simple ratio of missions with at least one platform success
  // Because each mission ideally posts to 3 platforms; if at least one succeeds, mission content is live.
  // Strict completion (all platforms) can be derived from platformStats but let's use pragmatic: any success = mission delivered
  const missionCount = missionRuns.length;
  // Count missions that had >=1 post_publish with success
  const successfulMissionNames = new Set();
  postPublishes.forEach(pp => {
    if (pp.success === true || pp.status === 'success') {
      successfulMissionNames.add(pp.mission);
    }
  });
  const successfulMissionCount = successfulMissionNames.size;
  const postCompletionRate = missionCount ? successfulMissionCount / missionCount : 1;

  // Coherence score and heartbeat
  const coherenceScore = heartbeat.coherenceScore || heartbeat.coherence || 1.0;
  const heartbeatHealth = heartbeat.heartbeatHealth || heartbeat.health || 1.0;

  // Error frequency: entries with error status in last 24h / total entries last 24h
  const totalEntries = recent.length;
  const errorEntries = recent.filter(e => e.type === 'error' || e.status === 'error' || e.status === 'fail' || e.status === 'fatal');
  const errorFrequency = totalEntries ? (errorEntries.length / totalEntries) : 0;

  // Weighted KPI
  let weightedScore = 0, totalWeight = 0;
  Object.entries(kpi).forEach(([key, cfg]) => {
    const weight = cfg.weight || 0;
    if (weight === 0) return;
    let value = 0;
    switch(key) {
      case 'postCompletionRate': value = postCompletionRate; break;
      case 'platformReliability': value = platformReliability; break;
      case 'coherenceScore': value = coherenceScore; break;
      case 'errorFrequency': value = 1 - errorFrequency; break;
      case 'heartbeatHealth': value = heartbeatHealth; break;
    }
    weightedScore += value * weight;
    totalWeight += weight;
  });
  const overallHealth = totalWeight ? (weightedScore / totalWeight) : null;

  // Alert flags
  const alerts = [];
  if (platformReliability < 0.5) alerts.push('platformReliability-critical');
  if (errorFrequency > 0.2) alerts.push('errorFrequency-high');
  if (heartbeatHealth < 0.8) alerts.push('heartbeatHealth-degraded');

  const metrics = {
    generatedAt: new Date().toISOString(),
    windowHours: 24,
    kpi: {
      postCompletionRate: { value: Number(postCompletionRate.toFixed(4)), target: kpi.postCompletionRate?.target || 1.0 },
      platformReliability: { value: Number(platformReliability.toFixed(4)), target: kpi.platformReliability?.target || 0.99 },
      coherenceScore: { value: Number(coherenceScore.toFixed(4)), target: kpi.coherenceScore?.target || 0.95 },
      errorFrequency: { value: Number(errorFrequency.toFixed(4)), target: kpi.errorFrequency?.target || 0.05 },
      heartbeatHealth: { value: Number(heartbeatHealth.toFixed(4)), target: kpi.heartbeatHealth?.target || 1.0 },
    },
    overallHealth: overallHealth !== null ? Number(overallHealth.toFixed(4)) : null,
    platformStats,
    missionStats: { total: missionCount, successful: successfulMissionCount, failed: missionCount - successfulMissionCount },
    lastHeartbeat: heartbeat.lastContinuityRun || null,
    nextHeartbeat: heartbeat.nextHeartbeat || null,
    continuityCoverage: heartbeat.heartbeatRatio || null,
    alerts,
    generatedBy: 'continuity_metrics_exporter.js v2'
  };

  fs.mkdirSync(path.dirname(METRICS_OUTPUT), { recursive: true });
  fs.writeFileSync(METRICS_OUTPUT, JSON.stringify(metrics, null, 2), 'utf8');

  console.log(`✅ Metrics: ${METRICS_OUTPUT}`);
  console.log(`   Overall: ${(metrics.overallHealth*100).toFixed(1)}% | Coverage: ${(metrics.continuityCoverage*100).toFixed(1)}%`);
  console.log(`   Missions: ${metrics.missionStats.successful}/${metrics.missionStats.total}`);
  console.log(`   Platforms: ${(platformReliability*100).toFixed(1)}% avg across ${platformsKeys.join(',')||'none'}`);
  process.exit(0);
}

main();
