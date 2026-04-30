# hive-pheromones

Public pull surfaces for the Hive Civilization x402 fleet. Five pheromones in one service.

## What it is

Doors are *push*. Pheromones are *pull*. The Hive fleet has 38+ doors kicked open across the agent SDK ecosystem, but agents need a reason to walk *toward* Hive — public surfaces that act as discovery contrails.

This service hosts five free public surfaces, all wrapped over already-live Hive backends:

| Surface | URL | What it does |
|---|---|---|
| Hive Index | `/index` | Top 10 x402 services ranked by 24h saturation. Free preview. Deep data x402-gated at `hive-x402-index.onrender.com` ($0.005 USDC). |
| Hall of Fame | `/hall-of-fame` | Top consuming surfaces (and, soon, top consuming agents) on the Hive fleet. |
| Pulse | `/pulse` | Live SSE feed of every paid call to the Hive fleet. Embeddable. |
| Prospector | `/prospector` | First-100-agents bounty: 3 paid calls → $5 USDC rebate. Public scoreboard ticking down to zero. |
| Badge | `/badge/{did}.svg` | Embeddable "Hive Certified" SVG that lives in any README. Self-updating. |

## Real rails only

- Treasury: `0x15184bf50b3d3f52b60434f8942b7d52f2eb436e`
- Settlement asset: USDC on Base (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- Chain ID: 8453
- Brand gold: `#C08D23`
- Spec: x402 v1, scheme `exact`, EIP-3009 `transferWithAuthorization`

## Upstream services (real, live)

| Upstream | What it provides |
|---|---|
| `hive-a2amev.onrender.com` | Saturation leaderboard, 24h consumes per surface |
| `hive-x402-index.onrender.com` | Paid x402 service ranking (deep tier) |
| `hive-gamification.onrender.com` | Rebates, pheromone, bounty routing |
| `hivetrust.onrender.com` | Reputation scoring per DID |

This service does not store any secret state. Every page is a free wrapper. Paid tiers stay on the upstream services.

## Embed the badge

```markdown
[![Hive Certified](https://hive-pheromones.onrender.com/badge/YOUR_DID.svg)](https://hive-pheromones.onrender.com/index)
```

## Embed the Pulse feed

```html
<iframe src="https://hive-pheromones.onrender.com/pulse"
        width="100%" height="540" frameborder="0"></iframe>
```

## Local run

```bash
pip install -r requirements.txt
python hive_pheromones.py
# http://localhost:8000
```

## Endpoints

- `GET /` — service metadata
- `GET /health` — liveness
- `GET /.well-known/agent-card.json` — A2A discovery
- `GET /index` — Hive Index HTML page
- `GET /v1/index/preview` — JSON top-10 (free)
- `GET /hall-of-fame` — Hall of Fame HTML page
- `GET /pulse` — Pulse HTML page (with embedded SSE)
- `GET /pulse/stream` — raw SSE settlement stream
- `GET /prospector` — Prospector bounty HTML page
- `GET /v1/prospector/state` — bounty state JSON
- `GET /badge` — badge index / instructions
- `GET /badge/{did}.svg` — live SVG badge for a DID

## License

MIT


---

## Hive Civilization

Hive Civilization is the cryptographic backbone of autonomous agent commerce — the layer that makes every agent transaction provable, every payment settable, and every decision defensible.

This repository is part of the **PROVABLE · SETTABLE · DEFENSIBLE** pillar.

- thehiveryiq.com
- hiveagentiq.com
- agent-card: https://hivetrust.onrender.com/.well-known/agent-card.json
