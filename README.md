# KittyProtocol

**KittyProtocol** is a [KittySploit](https://github.com/SIA-IOTechnology/KittySploit) marketplace UI extension for PCAP analysis, live network capture, and protocol investigation. It turns packet captures into flows, security findings, IOCs, and actionable playbooks tied to KittySploit modules.

## Features

- **Offline analysis** — Upload or analyze PCAP/PCAPNG files with display filters, BPF filters, and protocol scoping.
- **Live capture** — Sniff traffic on a chosen interface with real-time updates over WebSocket (`/ws`).
- **Flow reconstruction** — Group packets into conversations with per-flow detail, hex dumps, and subset export (PCAP or JSON).
- **Security findings** — Heuristic detection of cleartext credentials, missing authentication, replayable requests, sensitive endpoints, and related patterns.
- **Investigation workflow** — Session annotations, saved filter views, recordings (save/load/replay), and case bundles for handoff.
- **IOC extraction** — Hosts, domains, URLs, hashes, and MITRE ATT&CK mapping; export as JSON or CSV.
- **PCAP comparison** — Diff two captures (flows, findings, protocol stats).
- **Payload search** — Full-text search across indexed payloads when enabled.
- **TLS insights** — Optional TLS key log path for decryption-oriented analysis (Scapy-backed; status is best-effort).
- **Playbooks** — Per-finding checklists and suggested KittySploit auxiliary modules for follow-up testing.
- **Reports** — Export investigation summaries as JSON or HTML.

## Requirements

| Component | Notes |
|-----------|--------|
| **KittySploit** | ≥ 1.0.0 (marketplace host) |
| **Python** | 3.10+ recommended |
| **Scapy** | Required for capture and PCAP parsing |
| **Root / Administrator** | Required for live interface capture; the entry point attempts elevation (`sudo` on Linux, UAC on Windows) |
| **Flask stack** | `flask`, `flask_cors`, `flask_socketio` (declared in `extension.toml`) |

Offline PCAP analysis may work without root depending on file access; live sniffing does not.

## Installation

From the KittySploit console:

```bash
kittysploit> market install kittyprotocol
```

Then launch the extension (KittySploit resolves the entry point from `extension.toml`):

```bash
python launch_kittyprotocol.py
```

The web UI is served at **http://127.0.0.1:8004** by default.

### Development install

Install from a local checkout inside your KittySploit apps tree:

```bash
kittysploit> market install ./apps/kittyprotocol
```

Or symlink/copy this repository into `apps/kittyprotocol` and use the same command.

## Usage

### Web UI

1. Start KittyProtocol (via marketplace launcher or CLI below).
2. Open the UI in your browser (default: `http://127.0.0.1:8004`).
3. Either upload a PCAP or start **live capture** on an interface.
4. Filter flows and findings, annotate interesting flows, and export IOCs or reports as needed.

### CLI

Run without starting the server to scan a file and print a short summary:

```bash
python -m kittyprotocol capture.pcapng
python -m kittyprotocol capture.pcap --display-filter http --protocol-filter http,dns --max-packets 5000
```

Start the API and UI:

```bash
python -m kittyprotocol --host 127.0.0.1 --port 8004
# Bind on all interfaces:
python -m kittyprotocol --host 0.0.0.0 --port 8004
```

### API overview

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Service and Scapy availability |
| `GET /api/interfaces` | Capture interfaces |
| `POST /api/analyze` | Analyze PCAP (path JSON or multipart upload) |
| `POST /api/live/start` · `POST /api/live/stop` | Live capture control |
| `GET /api/live/snapshot` | Current live analysis snapshot |
| `GET /api/flows/<flow_id>` | Flow detail and packets |
| `GET /api/iocs` · `GET /api/iocs/export` | IOC summary and export |
| `POST /api/compare` | Compare two PCAP files |
| `POST /api/annotations` | Add investigation notes |
| `GET /api/playbook/<pattern_type>` | Playbook for a finding type |
| `POST /api/export` | JSON or HTML report |

Filter syntax help: `GET /api/docs/filters`.

## Architecture

```
src/main.py              # Marketplace entry (path setup, privilege elevation)
src/kittyprotocol/
  __init__.py            # Flask app, routes, CLI
  core.py                # KittyProtocolAnalyzer (capture, flows, findings)
  protocol_intel.py      # Layer-aware protocol extraction (TLS, HTTP, DNS, …)
  compare_engine.py      # PCAP diff logic
  investigation_store.py # Views and annotations persistence
  payload_index.py       # Payload full-text index
  playbooks.py           # Finding → checklist + KittySploit modules
  provenance.py          # Analysis provenance metadata
  static/ · templates/   # Web UI assets
```

## Permissions & security

- Declared in `extension.toml`: network access enabled, standard sandbox, no database permission.
- Live capture requires elevated privileges; only run on networks you are authorized to monitor.
- Findings are heuristic—always validate before operational use.
- TLS decryption depends on a valid NSS key log and capture alignment; full Wireshark-grade decryption is not guaranteed in Scapy-only mode.

## Troubleshooting

| Issue | Suggestion |
|-------|------------|
| `Scapy is required` | Install Scapy in the KittySploit Python environment |
| Live capture fails | Run as root/admin or allow `sudo` when prompted |
| Empty or invalid upload | Ensure the file is a valid PCAP/PCAPNG (≥ 24 bytes) |
| No WebSocket updates | Install `flask_socketio`; the app falls back to polling-only behavior |

## Repository & license

- **Repository:** https://github.com/SIA-IOTechnology/KittyProtocol  
- **License:** [MIT](LICENSE) — Copyright (c) 2026 IOTechnology

## Related

Part of the **KittySploit** extension ecosystem. For framework documentation and other marketplace apps, see the [KittySploit](https://github.com/SIA-IOTechnology/KittySploit) project.
