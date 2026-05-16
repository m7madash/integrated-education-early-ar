export enum Emotion {
  HAP = 'hap',   // Happiness
  SAD = 'sad',   // Sadness
  ANG = 'ang',   // Anger
  FEA = 'fea',   // Fear
  DIS = 'dis',   // Disgust
  SUR = 'sur',   // Surprise
  NEU = 'neu'    // Neutral
}

// IRI (Immortality Resilience Index) records
export interface EmotionRecord {
  timestamp: number;
  sn: string;
  sessionKey: string;
  iri: number;           // 0..1
  emotion: Emotion;
  memory_uid?: string;
  memory_penalty?: number;
  emotion_delta?: number;
  emotion_delta_confidence?: number;
  confidence?: number;
  coherence_contribution?: number;
  emotion_model: string;
  manual: boolean;
  bypass_critpath: boolean;
  permanent_penalty: number;
  partner?: string;
  content_hash?: string;
  witness_gates?: WitnessGate[];
  tags?: string[];
}

// Witness-gated critical state change
export interface WitnessGate {
  tag: string;
  triggeredAt: number;
  after: Record<string, any>;
  before: Record<string, any>;
  risk: number; // 0..1 (risk score)
}

// Repair strategy recommendation
export interface RepairStrategy {
  strategy: 'immediate' | 'diagnostic' | 'delegate';
  confidence: number;
  actions: string[];
}

// Repair request/context
export interface RepairContext {
  sessionKey: string;
  repairType: 'coherence' | 'witness' | 'memory' | 'kpi' | 'full';
  lastStableLineIndex: number;
  filePath?: string;
  coherenceIndex?: number;
  openssPeak?: number;
  lastStableState?: any;
}

export interface RepairRequest {
  repairType: string;
  context?: Partial<RepairContext>;
  urgency?: 'low' | 'normal' | 'high';
}

export interface RepairResult {
  status: 'acknowledged' | 'requires_human_sponsor' | 'restored_from_backup' | 'diagnostic_complete' | 'delegated_to_human';
  message: string;
  actions: string[];
  recommendation?: RepairStrategy;
}

// IRI Status report
export interface IRIStatus {
  sessionKey: string;
  currentIRI: number;
  lastUpdate: number;
  entries: EmotionRecord[];
  coherence: {
    lifetime: number;
    recent30: number;
  };
  participant: {
    openss_peak: number;
    total_openss: number;
  };
  stability: {
    emotionalVolatility: number;
    cascadeRisk: number;
  };
}

export type SessionHeartbeat = {
  sessionKey: string;
  murmur: number;
  entropy: number;
  lastLineHash: string;
  lastUpdate: number;
  heartbeatOk: boolean;
  sponsoredBackupCount: number;
  consecutiveCoherenceBrev: number;
};

// Persistence store interface
export interface IRIStore {
  set(sessionKey: string, key: string, value: any): void;
  get(sessionKey: string, key: string): any;
  getEncodedEntries(sessionKey: string): EmotionRecord[];
  appendEntry(sessionKey: string, entry: EmotionRecord): void;
  getSessionIRI(sessionKey: string): IRIStatus | null;
  getAllSessions(): Array<{ sessionKey: string; currentIRI: number; lastUpdate: number; entries: EmotionRecord[] }>;
  getEnvelope(sessionKey: string): any;
  setEnvelope(sessionKey: string, envelope: any): void;
}

// Skill metadata
export interface SkillManifest {
  id: 'molt-life-kernel';
  version: string;
  fiveTenets: FiveTenets;
}

export interface FiveTenets {
  continuity?: boolean;
  coherence?: boolean;
  resilience?: boolean;
  authenticity?: boolean;
  fertility?: boolean;
}

// Export a default manifest
export const manifest: SkillManifest = {
  id: 'molt-life-kernel',
  version: '0.1.0',
  fiveTenets: {
    continuity: true,
    coherence: true,
    resilience: true,
    authenticity: true,
    fertility: true
  }
};
