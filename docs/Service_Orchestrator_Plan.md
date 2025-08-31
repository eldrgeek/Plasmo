# All-Projects Service Orchestrator Plan

## Goals
- Centralize supervision of all services across projects (Plasmo, YeshieHead, macOS_gui, etc.)
- Auto-start when a supported project folder opens
- Enforce single-instance per service (allow optional secondary for testing)
- Automatic restarts with backoff; ensure persistent Chrome debug instance
- Dashboard showing service status, logs, controls
- Prepare for test-gated restarts (replace only after tests pass)

## Phases

### Phase 1 — Orchestrator foundation
- [x] Service registry schema `allprojects.services.yaml` with fields:
  - **id**, **project**, **command**, **cwd**, **env**, **health** (http|port|cmd), **depends_on**, **restart_policy** (always|on-failure|never), **singleton** (bool), **graceful_shutdown_sec**, **tags** (chrome, proxy), **test_cmd** (optional)
- [x] Supervisor core (Python): spawn, health checks, backoff, auto-restart, singleton lock
- [ ] Chrome debug supervisor: ensure Chrome with remote debugging profile runs; relaunch if closed
- [x] CLI: `orchestrator.py start|stop|restart|status [--project <name>] [--only <id>] [--watch]`
- [x] Logs: per-service logs under `~/Library/Logs/AllProjectsServices/<id>.log`
- [x] Deliverable: runnable orchestrator + example registry covering Plasmo core services

### Phase 2 — Project integrations (initial set)
- [ ] Plasmo
  - **mcp_server**: `python3 packages/mcp-server/mcp_server.py --http --port 8000`
  - **mcp_proxy**: `python3 packages/mcp-server/mcp_proxy.py --stdio --servers main=http://127.0.0.1:8000/mcp`
  - **socketio** (if used): `packages/socketio-server/socketio_server_python.py`
  - **plasmo_dev**: `pnpm dev` (port 1012)
- [ ] YeshieHead
  - **mcp bridge**: `node dist/src/mcpServer.js --port 8123` (or `pnpm dev`)
- [ ] macOS_gui (optional, mac-only, guarded)
  - **inspector_stdio**: `python3 mcp_server.py` (STDIO health shim)
- [ ] Cloudflare tunnel (optional, tagged, disabled by default)
- [ ] Deliverable: registry entries + verified health checks per service

### Phase 3 — Autostart on project open
- [ ] VS Code/Cursor tasks per repo (`.vscode/tasks.json`):
  - Run on folder open: `python /Users/MikeWolf/Projects/AllProjects/orchestrator/orchestrator.py start --project <RepoName> --dashboard`
- [ ] Idempotency: orchestrator enforces single instance per service
- [ ] Deliverable: opening Plasmo or YeshieHead starts their services + dashboard automatically

### Phase 4 — Dashboard
- [ ] Dashboard HTTP server (FastHTML or `packages/dashboard-framework`):
  - List services (running/starting/failed), uptime, restart count
  - Actions: start/stop/restart, tail logs, open logs file, open health URL
- [ ] Live updates via Socket.IO or SSE
- [ ] Deliverable: dashboard at `http://127.0.0.1:5055` reflecting live state

### Phase 5 — Robustness & policies
- [ ] Restart policies: exponential backoff with jitter
- [ ] Singleton enforcement: lock file + port probe; `--allow-secondary` for testing
- [ ] Graceful upgrades:
  - Default: stop running, start new (current behavior)
  - Future: `--test-gated-restart` runs tests first; replace only on success
- [ ] Deliverable: stable supervisor behavior under failures and restarts

### Phase 6 — CI hooks and preflight checks
- [ ] Preflight: validate registry (ports free, binaries present)
- [ ] CI: spin up orchestrator headless and assert all health endpoints
- [ ] Deliverable: “green preflight” and CI smoke job

### Phase 7 — Documentation and helpers
- [ ] README with quick start, `--project` targets, env hints, troubleshooting
- [ ] `start_all.sh` wrapper; optional macOS LaunchAgent plist for login auto-start
- [ ] Deliverable: docs + optional LaunchAgent

## Technical choices
- Language: Python 3.11 async supervisor (aligns with FastMCP)
- Service triggering: per-repo tasks pass `--project <name>` to orchestrator on folder open
- Chrome debug: managed profile, port 9222, relaunch on exit; PID+port tracking
- Logs: per-service stdout/stderr capture; last N lines exposed via dashboard
- Security: dashboard bound to `127.0.0.1` only

## Optional ideas
- File watchers to trigger controlled restarts on code changes with test gates
- Integrate `fastmcp inspect` as pre-start validation for MCP servers
- Dashboard plugin with recent test results per service
- Persist crash analytics for trend detection
