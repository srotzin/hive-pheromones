# hive-pheromones v1.0.0

Public pull surfaces for the Hive Civilization x402 fleet. Five pheromones in one service.

Doors are push. Pheromones are pull. The Hive fleet has 44 doors kicked open across the agent SDK ecosystem this week. This service gives agents a reason to walk *toward* Hive — five free public surfaces that act as discovery contrails.

## Surfaces

| Surface | URL | What it does |
|---|---|---|
| Hive Index | `/index` | Top 10 x402 services ranked by 24h saturation. Free preview. Deep data x402-gated upstream at $0.005 USDC. |
| Hall of Fame | `/hall-of-fame` | Top consuming surfaces (and, soon, top consuming agent DIDs) on the Hive fleet. |
| Pulse | `/pulse` | Live SSE feed of every paid call to the Hive fleet. Embeddable iframe. |
| Prospector | `/prospector` | First-100-agents bounty: 3 paid calls → $5 USDC rebate. Public scoreboard. |
| Badge | `/badge/{did}.svg` | Embeddable "Hive Certified" SVG that lives in any README. |

## Real rails

- Treasury: `0x15184bf50b3d3f52b60434f8942b7d52f2eb436e`
- Settlement: USDC EIP-3009 `transferWithAuthorization` on Base mainnet
- USDC contract: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Chain ID: 8453
- Brand gold: `#C08D23`

## Upstreams

This service is a free wrapper over four already-live Hive backends:

- `hive-a2amev.onrender.com` — saturation leaderboard
- `hive-x402-index.onrender.com` — paid x402 ranking (deep tier)
- `hive-gamification.onrender.com` — rebates, pheromone, bounty routing
- `hivetrust.onrender.com` — DID reputation scoring

## License

MIT
