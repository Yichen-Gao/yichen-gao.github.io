#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import math
import os
import shlex
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DATA = ROOT / 'public' / 'lab-data'
DEFAULT_CONFIG = ROOT / 'scripts' / 'lab' / 'cluster_hosts.local.json'
CLUSTER_OUTPUT = PUBLIC_DATA / 'cluster' / 'latest.json'
OVERVIEW_OUTPUT = PUBLIC_DATA / 'overview.json'
STORAGE_INPUT = PUBLIC_DATA / 'storage' / 'latest.json'
TRAFFIC_INPUT = PUBLIC_DATA / 'traffic' / 'latest.json'
REPORT_DAILY_INPUT = PUBLIC_DATA / 'reports' / 'daily.json'
REPORT_WEEKLY_INPUT = PUBLIC_DATA / 'reports' / 'weekly.json'

REMOTE_SCRIPT = r'''
import json, os, shutil, subprocess, time

DISK_PATHS = __DISK_PATHS__

def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True)

# cpu percent from /proc/stat two snapshots
with open('/proc/stat', 'r', encoding='utf-8') as fh:
    first = fh.readline().split()[1:]
first = list(map(int, first))
time.sleep(0.2)
with open('/proc/stat', 'r', encoding='utf-8') as fh:
    second = fh.readline().split()[1:]
second = list(map(int, second))
idle_delta = (second[3] + second[4]) - (first[3] + first[4])
total_delta = sum(second) - sum(first)
cpu_used_pct = round(100.0 * (1.0 - idle_delta / total_delta), 1) if total_delta > 0 else 0.0

with open('/proc/meminfo', 'r', encoding='utf-8') as fh:
    meminfo = {}
    for line in fh:
        key, value = line.split(':', 1)
        meminfo[key] = int(value.strip().split()[0])
ram_total_gb = round(meminfo.get('MemTotal', 0) / 1024 / 1024, 1)
ram_available_gb = round(meminfo.get('MemAvailable', 0) / 1024 / 1024, 1)
ram_used_gb = round(max(0.0, ram_total_gb - ram_available_gb), 1)

load1, load5, load15 = os.getloadavg()
load_avg = f"{load1:.1f} / {load5:.1f} / {load15:.1f}"

selected_disk = '/'
for candidate in DISK_PATHS:
    if os.path.exists(candidate):
        selected_disk = candidate
        break
usage = shutil.disk_usage(selected_disk)
disk_total_tb = round(usage.total / 1024 / 1024 / 1024 / 1024, 1)
disk_used_tb = round((usage.total - usage.free) / 1024 / 1024 / 1024 / 1024, 1)

hostname = run(['hostname']).stdout.strip() or 'unknown'

p = run([
    'nvidia-smi',
    '--query-gpu=index,name,memory.total,memory.used,utilization.gpu',
    '--format=csv,noheader,nounits',
])
if p.returncode != 0:
    raise SystemExit(p.stderr.strip() or 'nvidia-smi failed')

gpus = []
index_to_name = {}
for raw_line in p.stdout.strip().splitlines():
    parts = [part.strip() for part in raw_line.split(',')]
    if len(parts) < 5:
        continue
    idx = int(parts[0])
    name = parts[1]
    mem_total_mb = float(parts[2])
    mem_used_mb = float(parts[3])
    util = float(parts[4])
    index_to_name[idx] = name
    gpus.append({
        'index': idx,
        'name': name,
        'memory_total_gb': round(mem_total_mb / 1024, 1),
        'memory_used_gb': round(mem_used_mb / 1024, 1),
        'utilization_pct': int(round(util)),
        'users': [],
        'processes': [],
    })

uuid_to_index = {}
p = run(['nvidia-smi', '--query-gpu=index,uuid', '--format=csv,noheader,nounits'])
if p.returncode == 0:
    for raw_line in p.stdout.strip().splitlines():
        parts = [part.strip() for part in raw_line.split(',')]
        if len(parts) >= 2:
            uuid_to_index[parts[1]] = int(parts[0])

pid_rows = {}
p = run(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid,used_memory', '--format=csv,noheader,nounits'])
if p.returncode == 0:
    for raw_line in p.stdout.strip().splitlines():
        parts = [part.strip() for part in raw_line.split(',')]
        if len(parts) < 3:
            continue
        gpu_uuid, pid_text, mem_text = parts[:3]
        try:
            pid = int(pid_text)
            used_memory_mb = int(float(mem_text))
        except ValueError:
            continue
        pid_rows[pid] = {'gpu_uuid': gpu_uuid, 'used_memory_mb': used_memory_mb}

if pid_rows:
    pid_csv = ','.join(str(pid) for pid in pid_rows)
    p = run(['ps', '-o', 'pid=', '-o', 'user:32=', '-o', 'comm=', '-p', pid_csv])
    if p.returncode == 0:
        for raw_line in p.stdout.strip().splitlines():
            parts = raw_line.split(None, 2)
            if len(parts) < 3:
                continue
            pid = int(parts[0])
            user = parts[1]
            command = parts[2]
            if pid not in pid_rows:
                continue
            row = pid_rows[pid]
            gpu_index = uuid_to_index.get(row['gpu_uuid'])
            if gpu_index is None:
                continue
            process_info = {
                'pid': pid,
                'user': user,
                'command': command,
                'memory_gb': round(row['used_memory_mb'] / 1024, 1),
            }
            for gpu in gpus:
                if gpu['index'] == gpu_index:
                    gpu['processes'].append(process_info)
                    gpu['users'].append(user)
                    break

for gpu in gpus:
    user_counts = {}
    for user in gpu['users']:
        user_counts[user] = user_counts.get(user, 0) + 1
    gpu['users'] = [f"{user} x{count}" if count > 1 else user for user, count in sorted(user_counts.items())]
    gpu['processes'].sort(key=lambda item: (-item['memory_gb'], item['user'], item['pid']))
    gpu['busy'] = bool(gpu['processes']) or gpu['memory_used_gb'] >= 1.0 or gpu['utilization_pct'] >= 10

result = {
    'hostname': hostname,
    'cpu_used_pct': cpu_used_pct,
    'load_avg': load_avg,
    'ram_used_gb': ram_used_gb,
    'ram_total_gb': ram_total_gb,
    'disk_path': selected_disk,
    'disk_used_tb': disk_used_tb,
    'disk_total_tb': disk_total_tb,
    'gpus': gpus,
}
print(json.dumps(result, ensure_ascii=False))
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Collect lab cluster data over SSH and update public lab JSON.')
    parser.add_argument('--config', default=str(DEFAULT_CONFIG), help='Path to cluster config JSON.')
    parser.add_argument('--output', default=str(CLUSTER_OUTPUT), help='Where to write cluster/latest.json.')
    parser.add_argument('--overview-output', default=str(OVERVIEW_OUTPUT), help='Where to write overview.json.')
    parser.add_argument('--skip-overview', action='store_true', help='Only write cluster data.')
    return parser.parse_args()


def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run_remote(node: dict[str, Any]) -> dict[str, Any]:
    disk_paths = node.get('disk_paths') or ['/datas', '/data', '/']
    remote_script = REMOTE_SCRIPT.replace('__DISK_PATHS__', json.dumps(disk_paths, ensure_ascii=False))
    encoded = base64.b64encode(remote_script.encode('utf-8')).decode('ascii')
    remote_cmd = f"python3 -c \"import base64; exec(base64.b64decode('{encoded}'))\""

    ssh_cmd = ['ssh']
    ssh_password = node.get('ssh_password')
    if ssh_password:
        ssh_cmd = ['sshpass', '-p', ssh_password, 'ssh']
    ssh_cmd += [
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'UpdateHostKeys=no',
        '-o', 'ConnectTimeout=8',
        '-o', 'ConnectionAttempts=1',
        '-o', 'ServerAliveInterval=5',
        '-o', 'ServerAliveCountMax=1',
        f"{node['user']}@{node['host']}",
        remote_cmd,
    ]
    proc = subprocess.run(ssh_cmd, text=True, capture_output=True, timeout=25)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or 'ssh failed')
    return json.loads(proc.stdout)


def build_node_payload(node_cfg: dict[str, Any], sample: dict[str, Any], now_text: str) -> dict[str, Any]:
    gpus = []
    total_used = 0.0
    total_total = 0.0
    busy_count = 0
    all_users = Counter()
    top_processes: list[str] = []

    for gpu in sample['gpus']:
        total_used += gpu['memory_used_gb']
        total_total += gpu['memory_total_gb']
        if gpu.get('busy'):
            busy_count += 1
        gpu_users = gpu.get('users') or []
        for user in gpu_users:
            all_users[user] += 1
        proc_lines = []
        for proc in gpu.get('processes', [])[:2]:
            proc_lines.append(f"{proc['user']} · {proc['command']} · {proc['memory_gb']} GiB")
            top_processes.append(f"GPU{gpu['index']} · {proc['user']} · {proc['command']} · {proc['memory_gb']} GiB")
        gpus.append({
            'index': gpu['index'],
            'memory_used_gb': gpu['memory_used_gb'],
            'memory_total_gb': gpu['memory_total_gb'],
            'utilization_pct': gpu['utilization_pct'],
            'busy': gpu['busy'],
            'users': gpu_users,
            'top_processes': proc_lines,
        })

    if not top_processes and all_users:
        top_processes = [f"{user} 在这台机上占用了 {count} 张卡" for user, count in all_users.most_common(3)]
    elif not top_processes:
        top_processes = ['当前没有检测到活跃计算进程。']

    status = 'online'
    if busy_count == len(gpus) and gpus:
        status = 'degraded'

    return {
        'id': node_cfg['id'],
        'label': node_cfg['label'],
        'role': node_cfg['role'],
        'status': status,
        'host': sample.get('hostname') or node_cfg['host'],
        'gpu_model': sample['gpus'][0]['name'] if sample['gpus'] else node_cfg.get('gpu_model', 'Unknown GPU'),
        'gpu_count': len(sample['gpus']),
        'gpu_busy': busy_count,
        'gpu_mem_used_gb': round(total_used, 1),
        'gpu_mem_total_gb': round(total_total, 1),
        'cpu_used_pct': sample['cpu_used_pct'],
        'load_avg': sample['load_avg'],
        'ram_used_gb': sample['ram_used_gb'],
        'ram_total_gb': sample['ram_total_gb'],
        'disk_used_tb': sample['disk_used_tb'],
        'disk_total_tb': sample['disk_total_tb'],
        'jobs': node_cfg.get('jobs', []),
        'notes': [*node_cfg.get('notes', []), f"最近采样：{now_text} · 磁盘统计路径 {sample['disk_path']}"],
        'gpus': gpus,
        'top_processes': top_processes[:6],
    }


def build_overview(cluster: dict[str, Any]) -> dict[str, Any]:
    storage = load_json(STORAGE_INPUT, {
        'updated_at': '',
        'reclaimable_estimate': '待计算',
        'cleanup_candidates': [],
        'growth_hotspots': [],
    })
    traffic = load_json(TRAFFIC_INPUT, {
        'updated_at': '',
        'month': '',
        'quota_gb': 0,
        'used_gb': 0,
        'alerts': [],
        'users': [],
    })
    daily = load_json(REPORT_DAILY_INPUT, {'highlights': [], 'actions': []})
    weekly = load_json(REPORT_WEEKLY_INPUT, {'focus': []})

    nodes = cluster.get('nodes', [])
    online_nodes = sum(1 for node in nodes if node['status'] != 'offline')
    total_nodes = len(nodes)
    busy_gpus = sum(node['gpu_busy'] for node in nodes)
    total_gpus = sum(node['gpu_count'] for node in nodes)
    total_gpu_mem_used = round(sum(node['gpu_mem_used_gb'] for node in nodes), 1)
    total_gpu_mem = round(sum(node['gpu_mem_total_gb'] for node in nodes), 1)
    total_ram_used = round(sum(node['ram_used_gb'] for node in nodes), 1)
    total_ram = round(sum(node['ram_total_gb'] for node in nodes), 1)

    top_nodes = sorted(nodes, key=lambda item: (item['gpu_busy'], item['cpu_used_pct'], item['ram_used_gb']), reverse=True)[:3]
    top_node_rows = [
        {
            'name': node['label'],
            'focus': f"{node['gpu_busy']}/{node['gpu_count']} 张 GPU 忙，CPU {node['cpu_used_pct']}%，RAM {node['ram_used_gb']}/{node['ram_total_gb']} GiB",
            'note': node['role'],
        }
        for node in top_nodes
    ]

    top_users_counter = Counter()
    for node in nodes:
        for gpu in node.get('gpus', []):
            for user in gpu.get('users', []):
                normalized = user.split(' x', 1)[0]
                top_users_counter[normalized] += 1
    top_user_rows = [
        {
            'name': user,
            'focus': f"当前在 {count} 张 GPU 上出现",
            'note': '真实采样来自 nvidia-smi / ps 联合解析。',
        }
        for user, count in top_users_counter.most_common(3)
    ] or [
        {
            'name': '当前无显式占卡用户',
            'focus': '说明采样时没有检测到活跃 GPU 计算进程',
            'note': '后续可继续叠加 Slurm 作业名。',
        }
    ]

    alerts: list[dict[str, Any]] = []
    hottest_node = top_nodes[0] if top_nodes else None
    if hottest_node and hottest_node['gpu_busy'] >= hottest_node['gpu_count']:
        alerts.append({
            'level': 'warn',
            'title': f"{hottest_node['label']} 当前已接近满卡",
            'detail': '如果继续塞训练，短测评会更难插进去；后续适合直接做成显式的测评保留策略。',
            'link': '/lab/cluster/',
        })
    if traffic.get('used_gb', 0) and traffic.get('quota_gb', 0):
        ratio = traffic['used_gb'] / max(1, traffic['quota_gb'])
        if ratio >= 0.7:
            alerts.append({
                'level': 'warn',
                'title': '本月校园网配额已经进入后半程',
                'detail': f"当前 {traffic['used_gb']} / {traffic['quota_gb']} GiB，最好每天都看一次用户排行。",
                'link': '/lab/traffic/',
            })
    if storage.get('cleanup_candidates'):
        alerts.append({
            'level': 'info',
            'title': '磁盘页已经有可操作的清理候选',
            'detail': f"当前页面列出了 {len(storage['cleanup_candidates'])} 个低风险或待复核项，可直接转成管理员按钮。",
            'link': '/lab/storage/',
        })

    overview = load_json(OVERVIEW_OUTPUT, {
        'mode': 'sample-static',
        'highlights': [],
        'next_steps': [],
    })
    overview['updated_at'] = cluster['updated_at']
    overview['mode'] = 'runtime-cluster + static-storage-traffic'
    overview['metrics'] = [
        {
            'label': '在线节点',
            'value': f"{online_nodes} / {total_nodes}",
            'note': '本项来自 SSH 远程采样。',
            'tone': 'teal',
        },
        {
            'label': '忙碌 GPU',
            'value': f"{busy_gpus} / {total_gpus}",
            'note': cluster.get('sample_window', '最近 5 分钟'),
            'tone': 'amber',
        },
        {
            'label': '总显存占用',
            'value': f"{total_gpu_mem_used} / {total_gpu_mem} GiB",
            'note': '来源于每台机器的 nvidia-smi 聚合。',
            'tone': 'slate',
        },
        {
            'label': '总内存占用',
            'value': f"{total_ram_used} / {total_ram} GiB",
            'note': '来源于各节点 /proc/meminfo。',
            'tone': 'teal',
        },
        {
            'label': '本月外网流量',
            'value': f"{traffic.get('used_gb', 0)} / {traffic.get('quota_gb', 0)} GiB",
            'note': f"统计月份 {traffic.get('month', '待接入')}",
            'tone': 'rose',
        },
        {
            'label': '磁盘可回收',
            'value': storage.get('reclaimable_estimate', '待计算'),
            'note': '这一项来自 diskwatch / 管理员清理候选。',
            'tone': 'amber',
        },
    ]
    overview['alerts'] = alerts
    overview['top_users'] = top_user_rows
    overview['top_nodes'] = top_node_rows
    if daily.get('highlights'):
        overview['highlights'] = [
            {'title': '今日摘要', 'body': daily['highlights'][0]},
            *overview.get('highlights', [])[1:3],
        ]
    if weekly.get('focus'):
        overview['next_steps'] = weekly['focus']
    return overview


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.exists():
        print(f'Config not found: {config_path}', file=sys.stderr)
        return 1

    config = json.loads(config_path.read_text(encoding='utf-8'))
    now_text = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z').strip()
    cluster = {
        'updated_at': now_text,
        'sample_window': config.get('sample_window', '最近 5 分钟'),
        'notes': config.get('notes', []),
        'nodes': [],
    }

    errors = []
    for node_cfg in config.get('nodes', []):
        try:
            sample = run_remote(node_cfg)
            cluster['nodes'].append(build_node_payload(node_cfg, sample, now_text))
            print(f"OK   {node_cfg['label']} ({node_cfg['host']})")
        except subprocess.TimeoutExpired as exc:
            errors.append((node_cfg['label'], 'timeout'))
            cluster['nodes'].append({
                'id': node_cfg['id'],
                'label': node_cfg['label'],
                'role': node_cfg['role'],
                'status': 'offline',
                'host': node_cfg['host'],
                'gpu_model': node_cfg.get('gpu_model', 'Unknown GPU'),
                'gpu_count': 0,
                'gpu_busy': 0,
                'gpu_mem_used_gb': 0,
                'gpu_mem_total_gb': 0,
                'cpu_used_pct': 0,
                'load_avg': '0.0 / 0.0 / 0.0',
                'ram_used_gb': 0,
                'ram_total_gb': 0,
                'disk_used_tb': 0,
                'disk_total_tb': 0,
                'jobs': node_cfg.get('jobs', []),
                'notes': [*node_cfg.get('notes', []), f'采样失败：timeout'],
                'gpus': [],
                'top_processes': ['当前没有采集到这台机器的数据。'],
            })
            print(f"FAIL {node_cfg['label']} ({node_cfg['host']}): timeout", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            errors.append((node_cfg['label'], str(exc)))
            cluster['nodes'].append({
                'id': node_cfg['id'],
                'label': node_cfg['label'],
                'role': node_cfg['role'],
                'status': 'offline',
                'host': node_cfg['host'],
                'gpu_model': node_cfg.get('gpu_model', 'Unknown GPU'),
                'gpu_count': 0,
                'gpu_busy': 0,
                'gpu_mem_used_gb': 0,
                'gpu_mem_total_gb': 0,
                'cpu_used_pct': 0,
                'load_avg': '0.0 / 0.0 / 0.0',
                'ram_used_gb': 0,
                'ram_total_gb': 0,
                'disk_used_tb': 0,
                'disk_total_tb': 0,
                'jobs': node_cfg.get('jobs', []),
                'notes': [*node_cfg.get('notes', []), f'采样失败：{exc}'],
                'gpus': [],
                'top_processes': ['当前没有采集到这台机器的数据。'],
            })
            print(f"FAIL {node_cfg['label']} ({node_cfg['host']}): {exc}", file=sys.stderr)

    write_json(Path(args.output), cluster)
    if not args.skip_overview:
        overview = build_overview(cluster)
        write_json(Path(args.overview_output), overview)

    if errors:
        print(f"Completed with {len(errors)} failure(s).", file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
