# Edge-AI Distributed Fleet Coordination for AMRs

**SIH 2026 · Problem Statement 26123 · Bharat Electronics Limited**

A distributed multi-robot coordination prototype for **Autonomous Mobile Robots (AMRs)** operating in smart warehouses.

The project combines task allocation, robot-local A* planning, peer-intent conflict resolution, runtime safety checks, dynamic rerouting, failure recovery, direct UDP peer communication, telemetry, reproducible benchmarking, and a live operations dashboard.

> **Canonical runtime:** `ref_sih_amr/`  
> **Dashboard:** FastAPI + WebSocket + HTML5 Canvas  
> **Live coordination:** fleet-level Hungarian allocation + robot-local A* + peer-intent reservations + runtime safety checks

![Autonomous AMR Fleet Hub dashboard](assets/dashboard/fleet_dashboard_hud.png)

**Live web dashboard:** [https://beh-fleet-amr.vercel.app/](https://beh-fleet-amr.vercel.app/)

---

## What it does

| Capability | Implementation |
|---|---|
| Multi-AMR coordination | Concurrent simulated robot managers |
| Task allocation | Hungarian assignment |
| Navigation | Grid-based A* path planning |
| Motion coordination | Robot-local planning with peer-intent reservations |
| Safety | Vertex, edge-swap, occupancy, and reservation checks |
| Dynamic rerouting | Blocked-cell detection and replanning |
| Resilience | Battery/failure handling and task reassignment |
| Peer communication | Direct UDP peer mesh with deterministic in-process test transport |
| Telemetry | Queue-based `TelemetryBus` + WebSocket stream |
| Operations dashboard | Live fleet state, task pipeline, and warehouse visualization |
| Benchmarking | Reproducible scenarios and coordination strategies |

---

## Architecture

```text
                         SMART WAREHOUSE
                               │
                     ┌─────────▼─────────┐
                     │   Fleet Simulator │
                     │   Robot Managers  │
                     └─────────┬─────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
          Task Allocation   A* Planning   Peer Comms
          Hungarian Method  Grid Search    Intent / Heartbeats
                │              │              │
                └──────────────┼──────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │     Robot-local Safety    │
                 │ reservations / yield /   │
                 │ runtime conflict checks  │
                 └─────────────┬─────────────┘
                               │
                     ┌─────────▼─────────┐
                     │    TelemetryBus   │
                     └─────────┬─────────┘
                               │
                       FastAPI + WebSocket
                               │
                     ┌─────────▼─────────┐
                     │   Fleet Dashboard │
                     │  Canvas Warehouse  │
                     └───────────────────┘
```

The live fleet uses the **P2P strategy** for motion coordination: each robot maintains its own reservation state and exchanges intent directly with peers. Hungarian allocation remains a fleet-level task-assignment service. CBS is retained as an explicit centralized comparison/benchmark strategy and is **not** the live P2P motion-coordination path.

---

## Run the dashboard

### Requirements

- Python 3.10+ (Python 3.12 recommended)
- Windows, Linux, or macOS

### Install runtime dependencies

```bash
python3 -m pip install -r requirements.txt
```

For full validation, benchmark analysis, and optional ML/ONNX tooling:

```bash
python3 -m pip install -r requirements-dev.txt
```

### Start

On Windows:

```powershell
.\start_dashboard.bat
```

Then open:

```text
http://localhost:8000
```

The dashboard starts the simulator and streams live fleet telemetry to the web frontend.

### Dashboard includes

- Fleet robot positions and state
- Battery and velocity information
- Current task assignments
- Logistics order pipeline
- Coordination state
- Warehouse visualization
- Benchmark information

---

## Validation and benchmarking

Validation records are maintained under [`docs/validation/`](docs/validation/).

Run the regression suite:

```powershell
python -m pytest ref_sih_amr/tests -q
```

The test suite covers architecture boundaries, allocation, collision avoidance, blocked aisles, robot-failure recovery, communication degradation, planning behavior, and fleet coordination scenarios.

Benchmark scenarios and metrics are maintained under:

```text
ref_sih_amr/experiments/
```

Tracked metrics include:

- Makespan and task completion time
- Waiting time and throughput
- Collision and deadlock counts
- Replan count
- Communication latency and message loss
- CPU and memory usage
- Edge-inference latency
- Energy-proxy metrics

The benchmark framework includes sequential execution, independent planning, stop-and-wait coordination, P2P local coordination, and the legacy CBS comparison strategy.

For the latest recorded decentralized acceptance evidence, see [`docs/validation/P2P_ACCEPTANCE_MATRIX.md`](docs/validation/P2P_ACCEPTANCE_MATRIX.md). The matrix reports measured results rather than hard-coding a success claim.

---

## Repository structure

`ref_sih_amr/` is the canonical SIH runtime. Omniverse/OpenUSD integration is isolated from that runtime.

```text
SIH/
├── ref_sih_amr/                 # Canonical SIH AMR runtime
│   ├── allocator/               # Task allocation
│   ├── comms/                   # Peer communication
│   ├── dashboard/               # FastAPI + HTML5 Canvas dashboard
│   ├── experiments/             # Benchmark scenarios
│   ├── robot/                   # Robot policies, A*, CBS, task management
│   ├── sim/                     # Fleet simulation and orchestration
│   └── tests/                   # Regression and behavioral tests
│
├── omniverse/                   # OpenUSD / Omniverse integration
├── assets/                      # Warehouse and dashboard assets
├── scenarios/                   # Omniverse scenario assets
├── mcp_fleet/                   # Optional MCP integration
├── docs/validation/             # Validation records
├── start_dashboard.bat          # Dashboard launcher
├── requirements.txt             # Live-runtime dependencies
├── requirements-dev.txt         # Validation/benchmark/ML dependencies
├── SECURITY.md
├── LICENSE
└── README.md
```

### Canonical runtime vs. Omniverse

`ref_sih_amr/` is the **primary implementation** used by the regression suite and live dashboard.

The Omniverse/MCP components are optional integration and visualization tooling. They are not required to run the canonical simulator, benchmarks, tests, or dashboard.

---

## Evidence boundaries

### Fleet-level allocation, robot-level coordination

The live runtime deliberately separates **task assignment** from **motion coordination**:

- Hungarian allocation assigns queued orders to eligible AMRs.
- Each assigned AMR performs its own A* planning.
- Each AMR owns its local reservation state and exchanges intent directly with peers.
- The live P2P path does not use a fleet-wide motion reservation table or centralized motion coordinator.

This separation supports deterministic fleet-level task assignment while keeping motion coordination at the distributed robot level.

### Edge-class emulation

No Raspberry Pi or Jetson hardware measurement is claimed.

For repeatable **Pi-class resource emulation**, `robot/node.py` can run as an independent robot process inside Docker containers with approximately 1 CPU and 1 GB RAM per robot. Measurements from this setup should be reported as **containerized edge-class emulation**, not physical hardware evidence.

The instrumentation under `ref_sih_amr/edge/` is retained for future target-device measurements.

### Optional Omniverse/MCP integration

The canonical SIH runtime does not require NVIDIA Omniverse, OpenUSD, or MCP.

- `ref_sih_amr/` — judge/demo runtime
- `omniverse/`, `assets/omniverse/` — optional visualization/integration assets
- `mcp_fleet/` — optional integration tooling

---

## Coordination pipeline

1. **Tasks enter the fleet queue.**
2. **The allocator assigns work** to eligible robots.
3. **A*** generates obstacle-aware paths.
4. **Peer intents and local reservations** resolve multi-robot conflicts.
5. **Runtime safety checks** guard against occupancy, vertex, and edge-swap conflicts.
6. **Blocked paths or changing conditions** trigger replanning.
7. **Robot failure or degraded communication** can trigger recovery and task reassignment.
8. **TelemetryBus** publishes fleet state to the dashboard.

---

## Engineering principles

- Core simulation and coordination code does not depend on the dashboard.
- The dashboard consumes telemetry rather than owning coordination logic.
- Robot coordination is modeled at the distributed edge-node level.
- Deterministic safety checks remain authoritative.
- Benchmark scenarios remain reproducible.
- Omniverse integration remains separate from the canonical runtime.
- Evidence is reported with explicit boundaries instead of overstating hardware or deployment results.

---

## SIH problem statement

**26123 — Edge-AI Based Distributed Fleet Coordination for Autonomous Mobile Robots (AMRs) in Smart Warehouses**

The prototype targets coordinated operation of multiple AMRs in warehouse environments, with emphasis on local decision-making, collision avoidance, task allocation, rerouting, resilience, telemetry, and measurable fleet performance.

---

## Status

**SIH 2026 prototype · actively developed**

For the working demonstration, use the canonical runtime and dashboard described above.
