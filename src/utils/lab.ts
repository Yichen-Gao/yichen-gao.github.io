import fs from 'node:fs/promises';
import path from 'node:path';

export type AlertLevel = 'info' | 'warn' | 'critical';
export type Tone = 'teal' | 'amber' | 'rose' | 'slate';

export interface AlertItem {
  level: AlertLevel;
  title: string;
  detail: string;
  link?: string;
}

export interface OverviewMetric {
  label: string;
  value: string;
  note: string;
  tone?: Tone;
}

export interface OverviewHighlight {
  title: string;
  body: string;
}

export interface OverviewRow {
  name: string;
  focus: string;
  note: string;
}

export interface OverviewData {
  updated_at: string;
  mode: string;
  metrics: OverviewMetric[];
  alerts: AlertItem[];
  highlights: OverviewHighlight[];
  top_users: OverviewRow[];
  top_nodes: OverviewRow[];
  next_steps: string[];
}

export interface GpuCardData {
  index: number;
  memory_used_gb: number;
  memory_total_gb: number;
  utilization_pct: number;
  busy: boolean;
  users: string[];
  top_processes: string[];
}

export interface NodeData {
  id: string;
  label: string;
  role: string;
  status: 'online' | 'degraded' | 'offline';
  host: string;
  gpu_model: string;
  gpu_count: number;
  gpu_busy: number;
  gpu_mem_used_gb: number;
  gpu_mem_total_gb: number;
  cpu_used_pct: number;
  load_avg: string;
  ram_used_gb: number;
  ram_total_gb: number;
  disk_used_tb: number;
  disk_total_tb: number;
  jobs: string[];
  notes: string[];
  gpus: GpuCardData[];
  top_processes: string[];
}

export interface ClusterData {
  updated_at: string;
  sample_window: string;
  notes: string[];
  nodes: NodeData[];
}

export interface MountpointData {
  name: string;
  host: string;
  used_tb: number;
  total_tb: number;
  note: string;
}

export interface CleanupCandidate {
  name: string;
  path: string;
  size: string;
  kind: string;
  risk: 'low' | 'review';
  action: string;
  reason: string;
}

export interface StorageRow {
  name: string;
  scope: string;
  note: string;
}

export interface StorageData {
  updated_at: string;
  reclaimable_estimate: string;
  mountpoints: MountpointData[];
  cleanup_candidates: CleanupCandidate[];
  stale_accounts: StorageRow[];
  growth_hotspots: StorageRow[];
  policies: string[];
}

export interface TrafficUser {
  user: string;
  used_gb: number;
  status: 'ok' | 'watch' | 'limit' | 'blocked';
  note: string;
}

export interface TrafficSpike {
  time: string;
  user: string;
  size: string;
  note: string;
}

export interface TrafficData {
  updated_at: string;
  month: string;
  quota_gb: number;
  used_gb: number;
  hard_limit_gb: number;
  ignored_window: string;
  alerts: AlertItem[];
  users: TrafficUser[];
  spikes: TrafficSpike[];
  rules: string[];
}

export interface ReportCard {
  title: string;
  body: string[];
}

export interface DailyReportData {
  updated_at: string;
  date: string;
  highlights: string[];
  anomalies: string[];
  actions: string[];
}

export interface WeeklyReportData {
  updated_at: string;
  range: string;
  highlights: string[];
  decisions: string[];
  focus: string[];
}

const labDataRoot = path.join(process.cwd(), 'public', 'lab-data');

export async function loadLabJson<T>(relativePath: string, fallback: T): Promise<T> {
  try {
    const fullPath = path.join(labDataRoot, relativePath);
    const raw = await fs.readFile(fullPath, 'utf-8');
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export function toPercent(value: number, total: number): number {
  if (total <= 0) return 0;
  return Math.max(0, Math.min(100, Math.round((value / total) * 100)));
}

export function formatPercent(value: number, total: number): string {
  return `${toPercent(value, total)}%`;
}
