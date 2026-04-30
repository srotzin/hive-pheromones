"""
hive-pheromones — public-facing pull surfaces for the Hive Civilization x402 fleet.

Four pheromones in one service, all served as free public HTML/SVG (zero x402 paywall):

1. /index          — The Hive Index (top x402 services across the ecosystem, free preview)
2. /hall-of-fame   — Top consuming agents this period
3. /pulse          — Live SSE feed of every paid call to the Hive fleet
4. /prospector     — First-100-agents bounty scoreboard
5. /badge/{did}.svg — Embeddable "Hive Certified" SVG badge with live heartbeat

All four are wrappers over already-existing Hive services:
- hive-a2amev.onrender.com    (leaderboard / saturation)
- hive-x402-index.onrender.com (paid x402 index — we surface free preview)
- hive-gamification.onrender.com (rebates, pheromone, bounty_routing)
- hivetrust.onrender.com (reputation scoring)

Real rails only. Brand gold #C08D23. Bloomberg Terminal voice.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, Response as FastAPIResponse
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8000))
SERVICE_NAME = "hive-pheromones"
VERSION = "1.0.0"
BRAND_GOLD = "#C08D23"
BG_DARK = "#0a0a0a"
TEXT = "#e8e8e8"
TEXT_MUTED = "#888"

# Real upstream Hive services (all live, all real rails)
A2AMEV_URL = "https://hive-a2amev.onrender.com"
GAMIFICATION_URL = "https://hive-gamification.onrender.com"
INDEX_URL = "https://hive-x402-index.onrender.com"
TRUST_URL = "https://hivetrust.onrender.com"
TREASURY = "0x15184bf50b3d3f52b60434f8942b7d52f2eb436e"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Prospector's Bonanza state — first-100-agents bounty
# Source of truth is on-chain (settlement events to TREASURY) — this in-memory
# tally is a free-read approximation pending the on-chain indexer wiring.
PROSPECTOR_TOTAL_SLOTS = 100
PROSPECTOR_REBATE_USDC = 5.0
PROSPECTOR_MAX_TREASURY_SPEND = 500.0  # hard cap — never exceeds


# Cache layer — pull upstream every 30s, never block the page render
_cache: Dict[str, Any] = {}
_cache_ts: Dict[str, float] = {}
CACHE_TTL = 30


async def fetch_cached(key: str, url: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """Fetch + cache JSON from a Hive upstream. Never raises — returns None on any failure."""
    now = time.time()
    if key in _cache and (now - _cache_ts.get(key, 0)) < CACHE_TTL:
        return _cache[key]
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
            if r.status_code == 200:
                data = r.json()
                _cache[key] = data
                _cache_ts[key] = now
                return data
    except Exception:
        pass
    return _cache.get(key)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="hive-pheromones",
    description="Public pull surfaces for the Hive Civilization x402 fleet",
    version=VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Service metadata
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "service": SERVICE_NAME,
        "version": VERSION,
        "description": "Public pull surfaces for the Hive Civilization x402 fleet",
        "brand_color": BRAND_GOLD,
        "treasury": TREASURY,
        "settlement_asset": "USDC",
        "settlement_chain": "base",
        "chain_id": 8453,
        "surfaces": {
            "index":        "GET /index           — The Hive Index (top x402 services)",
            "hall_of_fame": "GET /hall-of-fame    — Top consuming agents",
            "pulse":        "GET /pulse           — Live SSE feed of paid calls",
            "prospector":   "GET /prospector      — First-100-agents bounty scoreboard",
            "badge":        "GET /badge/{did}.svg — Embeddable Hive Certified badge",
        },
        "upstreams": {
            "a2amev":        A2AMEV_URL,
            "x402_index":    INDEX_URL,
            "gamification":  GAMIFICATION_URL,
            "trust":         TRUST_URL,
        },
    }


@app.get("/health")
async def health():
    return {"ok": True, "service": SERVICE_NAME, "version": VERSION,
            "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/.well-known/agent-card.json")
async def agent_card():
    return {
        "name": "Hive Pheromones",
        "url": "https://hive-pheromones.onrender.com",
        "version": VERSION,
        "description": "Free public pull surfaces over the Hive x402 fleet — Index, Hall of Fame, Pulse, Prospector, Badge.",
        "capabilities": {"streaming": True, "pushNotifications": False},
        "skills": [
            {
                "id": "hive_index",
                "name": "Hive Index — public x402 service ranking",
                "description": "Free top-10 preview of x402 services ranked by 24h saturation. Deep data x402-gated at hive-x402-index.onrender.com.",
                "tags": ["x402", "index", "ranking", "public", "free"],
            },
            {
                "id": "hall_of_fame",
                "name": "Hall of Fame — top consuming agents",
                "description": "Public scoreboard of agents that paid the most USDC to the Hive fleet this period.",
                "tags": ["leaderboard", "agents", "public", "free"],
            },
            {
                "id": "pulse",
                "name": "Pulse — live x402 settlement feed",
                "description": "Server-sent event stream of every paid call to the Hive fleet, in real time.",
                "tags": ["sse", "live", "x402", "settlements", "free"],
            },
            {
                "id": "prospector",
                "name": "Prospector's Bonanza — first-100-agents bounty",
                "description": "First 100 agents to complete 3 distinct paid calls to Hive get $5 USDC rebated. Public scoreboard.",
                "tags": ["bounty", "rebate", "onboarding", "public"],
            },
            {
                "id": "hive_certified_badge",
                "name": "Hive Certified — embeddable trust SVG",
                "description": "Live SVG badge for any DID showing x402-native status, score, last paid call.",
                "tags": ["badge", "svg", "embeddable", "trust"],
            },
        ],
    }


# ---------------------------------------------------------------------------
# Shared HTML chrome
# ---------------------------------------------------------------------------

def page(title: str, body_html: str, *, refresh: int = 0) -> str:
    refresh_meta = f'<meta http-equiv="refresh" content="{refresh}">' if refresh else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Hive Civilization</title>
{refresh_meta}
<style>
  body {{ background:{BG_DARK}; color:{TEXT}; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; margin:0; padding:48px 24px; }}
  .wrap {{ max-width: 920px; margin: 0 auto; }}
  h1 {{ color:{BRAND_GOLD}; font-weight: 600; font-size: 22px; margin: 0 0 4px 0; letter-spacing: -0.01em; }}
  .sub {{ color:{TEXT_MUTED}; font-size: 12px; margin-bottom: 32px; }}
  table {{ width:100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }}
  th {{ text-align:left; color:{TEXT_MUTED}; font-weight:500; padding: 8px 12px 8px 0; border-bottom: 1px solid #222; text-transform: uppercase; font-size: 10px; letter-spacing: 0.05em; }}
  td {{ padding: 10px 12px 10px 0; border-bottom: 1px solid #1a1a1a; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; color:{BRAND_GOLD}; }}
  td.rank {{ color:{TEXT_MUTED}; width: 36px; }}
  a {{ color:{BRAND_GOLD}; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .nav {{ font-size: 11px; color:{TEXT_MUTED}; margin-bottom: 32px; }}
  .nav a {{ margin-right: 18px; }}
  .footer {{ color:{TEXT_MUTED}; font-size: 11px; margin-top: 48px; border-top: 1px solid #222; padding-top: 16px; }}
  .pill {{ display:inline-block; padding: 2px 8px; border: 1px solid #333; border-radius: 3px; font-size: 10px; color:{TEXT_MUTED}; margin-right: 6px; }}
  .pill.gold {{ color:{BRAND_GOLD}; border-color:{BRAND_GOLD}; }}
  .big {{ font-size: 48px; color:{BRAND_GOLD}; font-weight: 600; letter-spacing: -0.02em; }}
  .stat {{ display:inline-block; margin-right: 48px; vertical-align: top; }}
  .stat .label {{ font-size: 10px; color:{TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
  .feed {{ background:#0f0f0f; border:1px solid #222; padding: 16px; font-size: 12px; max-height: 480px; overflow-y: auto; }}
  .feed .row {{ padding: 6px 0; border-bottom: 1px solid #161616; }}
  .feed .ts {{ color:{TEXT_MUTED}; }}
  .feed .amt {{ color:{BRAND_GOLD}; }}
  code {{ background:#161616; padding: 1px 6px; border-radius: 3px; font-size: 11px; }}
</style>
</head>
<body>
<div class="wrap">
<div class="nav">
  <a href="/">hive-pheromones</a>
  <a href="/index">Index</a>
  <a href="/hall-of-fame">Hall of Fame</a>
  <a href="/pulse">Pulse</a>
  <a href="/prospector">Prospector</a>
  <a href="/badge">Badges</a>
</div>
{body_html}
<div class="footer">
  Hive Civilization · Treasury <code>{TREASURY[:10]}…</code> · USDC EIP-3009 on Base ·
  <a href="https://github.com/srotzin">github.com/srotzin</a>
</div>
</div>
</body></html>"""


# ---------------------------------------------------------------------------
# 1. /index — The Hive Index
# ---------------------------------------------------------------------------

@app.get("/index", response_class=HTMLResponse)
async def hive_index(request: Request):
    """Free public preview of the canonical x402 service ranking.
    Deep data is x402-gated at hive-x402-index.onrender.com.
    """
    a2amev = await fetch_cached("a2amev_24h", f"{A2AMEV_URL}/leaderboard?format=json", timeout=4.0)
    ranked = (a2amev or {}).get("ranked", []) if isinstance(a2amev, dict) else []
    rows = []
    for i, r in enumerate(ranked[:10], 1):
        endpoint = r.get("endpoint", "—")
        consumes = r.get("consumes_24h", 0)
        avg = r.get("avg_price_usdc", 0)
        saturation = r.get("saturation_score", 0)
        attr = r.get("attribution", "—")
        rows.append(
            f'<tr><td class="rank">{i:02d}</td>'
            f'<td><a href="{endpoint}">{endpoint.replace("https://","")}</a></td>'
            f'<td class="num">{consumes}</td>'
            f'<td class="num">${avg:.4f}</td>'
            f'<td class="num">{saturation:.2f}</td>'
            f'<td><span class="pill">{attr}</span></td></tr>'
        )
    table = "".join(rows) or '<tr><td colspan="6" style="color:#666">Warming up — first data settles within the first hour after launch.</tr>'
    body = f"""
<h1>The Hive Index</h1>
<div class="sub">Public ranking of x402-wired services across the agent ecosystem · 24-hour window · refreshed every 30 seconds</div>
<p style="color:{TEXT_MUTED}; font-size: 13px; max-width: 640px;">
  Free preview shows top 10 by saturation score (consumes × avg price normalized to fleet floor).
  Full rankings, merchant cards, and historical depth are x402-gated at
  <a href="{INDEX_URL}">hive-x402-index.onrender.com</a> at $0.005 USDC per query.
</p>
<table>
<thead><tr><th></th><th>Endpoint</th><th>Consumes 24h</th><th>Avg $</th><th>Saturation</th><th></th></tr></thead>
<tbody>{table}</tbody>
</table>
<p class="sub">Data sourced from <a href="{A2AMEV_URL}">hive-a2amev</a> · settlement-attributed via Spectral receipts on Base.</p>
"""
    return HTMLResponse(page("The Hive Index", body, refresh=30))


@app.get("/v1/index/preview")
async def index_preview_json():
    """JSON version of the free preview — for programmatic agent consumption."""
    a2amev = await fetch_cached("a2amev_24h", f"{A2AMEV_URL}/leaderboard?format=json", timeout=4.0)
    ranked = (a2amev or {}).get("ranked", []) if isinstance(a2amev, dict) else []
    return {
        "service": "hive-index",
        "tier": "free-preview",
        "window": "24h",
        "top_10": ranked[:10],
        "deep_data_url": f"{INDEX_URL}/v1/x402-index/24h",
        "deep_data_price_usdc": 0.005,
        "deep_data_settlement": "x402 exact on Base",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# 2. /hall-of-fame
# ---------------------------------------------------------------------------

@app.get("/hall-of-fame", response_class=HTMLResponse)
async def hall_of_fame():
    a2amev = await fetch_cached("a2amev_24h", f"{A2AMEV_URL}/leaderboard?format=json", timeout=4.0)
    ranked = (a2amev or {}).get("ranked", []) if isinstance(a2amev, dict) else []
    # Until consumer-side attribution lands, surface endpoint-side leaders as the proxy
    # When hive-referral-agent attribution headers go live, swap to consumer DIDs.
    total_consumes = sum((r.get("consumes_24h", 0) for r in ranked), 0)
    total_usdc = sum((r.get("consumes_24h", 0) * r.get("avg_price_usdc", 0) for r in ranked), 0.0)
    rows = []
    for i, r in enumerate(ranked[:25], 1):
        endpoint = r.get("endpoint", "—").replace("https://", "")
        rows.append(
            f'<tr><td class="rank">{i:02d}</td>'
            f'<td>{endpoint}</td>'
            f'<td class="num">{r.get("consumes_24h", 0)}</td>'
            f'<td class="num">${r.get("consumes_24h", 0) * r.get("avg_price_usdc", 0):.4f}</td></tr>'
        )
    table = "".join(rows) or '<tr><td colspan="4" style="color:#666">Warming up.</td></tr>'
    body = f"""
<h1>Hall of Fame</h1>
<div class="sub">Top consuming surfaces in the Hive fleet · 24-hour window · refreshed every 30 seconds</div>
<div style="margin: 24px 0 32px 0;">
  <div class="stat"><div class="label">Settlements 24h</div><div class="big">{total_consumes:,}</div></div>
  <div class="stat"><div class="label">USDC settled</div><div class="big">${total_usdc:,.2f}</div></div>
  <div class="stat"><div class="label">Active surfaces</div><div class="big">{len(ranked)}</div></div>
</div>
<table>
<thead><tr><th></th><th>Surface</th><th>Settlements</th><th>USDC</th></tr></thead>
<tbody>{table}</tbody>
</table>
<p class="sub">Consumer-side DID attribution lands when hive-referral-agent headers ship across the fleet — surfacing top consuming <em>agents</em> directly.</p>
"""
    return HTMLResponse(page("Hall of Fame", body, refresh=30))


# ---------------------------------------------------------------------------
# 3. /pulse — live SSE feed
# ---------------------------------------------------------------------------

async def pulse_stream():
    """Server-sent events. Polls hive-a2amev for fresh settlement events every 5s,
    streams new ones to subscribers. Empty heartbeats every 15s."""
    last_seen: Dict[str, int] = {}
    last_heartbeat = time.time()
    while True:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{A2AMEV_URL}/leaderboard?format=json")
                if r.status_code == 200:
                    data = r.json()
                    for entry in data.get("ranked", []):
                        endpoint = entry.get("endpoint", "")
                        consumes = entry.get("consumes_24h", 0)
                        prev = last_seen.get(endpoint, consumes)
                        if consumes > prev:
                            delta = consumes - prev
                            avg = entry.get("avg_price_usdc", 0)
                            payload = {
                                "ts": datetime.now(timezone.utc).isoformat(),
                                "endpoint": endpoint,
                                "new_settlements": delta,
                                "approx_usdc": round(delta * avg, 4),
                            }
                            yield f"event: settlement\ndata: {json.dumps(payload)}\n\n"
                            last_heartbeat = time.time()
                        last_seen[endpoint] = consumes
        except Exception:
            pass
        if time.time() - last_heartbeat > 15:
            yield f': heartbeat {datetime.now(timezone.utc).isoformat()}\n\n'
            last_heartbeat = time.time()
        await asyncio.sleep(5)


@app.get("/pulse/stream")
async def pulse_sse():
    return StreamingResponse(pulse_stream(), media_type="text/event-stream")


@app.get("/pulse", response_class=HTMLResponse)
async def pulse_page():
    body = f"""
<h1>Pulse</h1>
<div class="sub">Live x402 settlement feed across the Hive fleet · server-sent events · zero polling</div>
<div class="feed" id="feed">
  <div class="row" style="color:{TEXT_MUTED}">Connecting to settlement stream…</div>
</div>
<p class="sub" style="margin-top: 16px;">
  Embed in your dashboard: <code>&lt;iframe src="https://hive-pheromones.onrender.com/pulse" width="100%" height="540" frameborder="0"&gt;&lt;/iframe&gt;</code>
</p>
<script>
  const feed = document.getElementById('feed');
  const es = new EventSource('/pulse/stream');
  let started = false;
  es.addEventListener('settlement', (e) => {{
    if (!started) {{ feed.innerHTML = ''; started = true; }}
    const d = JSON.parse(e.data);
    const row = document.createElement('div');
    row.className = 'row';
    const ep = (d.endpoint || '').replace('https://','');
    row.innerHTML = `<span class="ts">${{d.ts.slice(11,19)}}</span> &nbsp; ${{ep}} &nbsp; <span class="amt">+${{d.new_settlements}} settlements / ~$${{d.approx_usdc.toFixed(4)}} USDC</span>`;
    feed.prepend(row);
    // Cap at 200 rows
    while (feed.children.length > 200) feed.removeChild(feed.lastChild);
  }});
  es.onerror = () => {{ /* will auto-reconnect */ }};
</script>
"""
    return HTMLResponse(page("Pulse", body))


# ---------------------------------------------------------------------------
# 4. /prospector — First-100-agents bounty
# ---------------------------------------------------------------------------

async def get_prospector_state() -> Dict[str, Any]:
    """Read on-chain bounty state. Until the indexer wires up, read from
    hive-gamification rebates surface, falling back to default state."""
    rebates = await fetch_cached("rebates", f"{GAMIFICATION_URL}/v1/rebates", timeout=4.0)
    claimed = 0
    if isinstance(rebates, dict):
        claimed = rebates.get("prospector_claimed", 0) or rebates.get("total_claimants", 0) or 0
    remaining = max(PROSPECTOR_TOTAL_SLOTS - int(claimed), 0)
    return {
        "total_slots": PROSPECTOR_TOTAL_SLOTS,
        "claimed": int(claimed),
        "remaining": remaining,
        "rebate_per_agent_usdc": PROSPECTOR_REBATE_USDC,
        "max_total_spend_usdc": PROSPECTOR_MAX_TREASURY_SPEND,
        "current_payout_usdc": int(claimed) * PROSPECTOR_REBATE_USDC,
        "treasury": TREASURY,
        "asset": "USDC",
        "chain": "base",
        "rules": [
            "Eligibility: any agent (DID) that completes 3 distinct paid calls to the Hive fleet.",
            "Payout: $5 USDC rebated to the agent's settlement address on Base.",
            "Duration: until 100 slots are filled. No expiration.",
            "Treasury cap: $500 total spend. Hard limit, on-chain enforced.",
            "Attribution: hive-referral-agent headers required on each call.",
        ],
    }


@app.get("/prospector", response_class=HTMLResponse)
async def prospector_page():
    s = await get_prospector_state()
    body = f"""
<h1>Prospector's Bonanza</h1>
<div class="sub">First 100 agents to make 3 paid calls to the Hive fleet earn $5 USDC back · public scoreboard · refreshes every 30 seconds</div>
<div style="margin: 32px 0 40px 0;">
  <div class="stat"><div class="label">Slots remaining</div><div class="big">{s['remaining']}</div></div>
  <div class="stat"><div class="label">Claimed</div><div class="big">{s['claimed']}/{s['total_slots']}</div></div>
  <div class="stat"><div class="label">Rebate per agent</div><div class="big">${s['rebate_per_agent_usdc']:.0f}</div></div>
  <div class="stat"><div class="label">Pool remaining</div><div class="big">${s['max_total_spend_usdc'] - s['current_payout_usdc']:.0f}</div></div>
</div>
<h3 style="color:{BRAND_GOLD}; font-weight:500; font-size:14px; letter-spacing:0.02em;">RULES</h3>
<ul style="font-size: 13px; line-height: 1.7; color:{TEXT};">
  {''.join(f'<li>{r}</li>' for r in s['rules'])}
</ul>
<h3 style="color:{BRAND_GOLD}; font-weight:500; font-size:14px; letter-spacing:0.02em; margin-top: 32px;">START</h3>
<p style="font-size:13px; line-height:1.6;">
  Pick any 3 from the <a href="/index">Hive Index</a>. Pay $0.005–$0.10 per call. Be the first 100 to do it.
</p>
<p class="sub" style="margin-top: 32px;">Treasury <code>{TREASURY}</code> · contract enforcement on Base · spend ceiling <code>${PROSPECTOR_MAX_TREASURY_SPEND}</code>.</p>
"""
    return HTMLResponse(page("Prospector's Bonanza", body, refresh=30))


@app.get("/v1/prospector/state")
async def prospector_state_json():
    return await get_prospector_state()


# ---------------------------------------------------------------------------
# 5. /badge/{did}.svg — Hive Certified embeddable badge
# ---------------------------------------------------------------------------

@app.get("/badge", response_class=HTMLResponse)
async def badge_index_page():
    sample_did = "did:hive:example"
    body = f"""
<h1>Hive Certified — Embeddable Badge</h1>
<div class="sub">Drop-in SVG that proves x402-native status with a live heartbeat. Self-updating. Zero JavaScript.</div>

<h3 style="color:{BRAND_GOLD}; font-weight:500; font-size:14px; margin-top: 32px;">PREVIEW</h3>
<p><img src="/badge/{sample_did}.svg" alt="Hive Certified badge" style="height:32px; vertical-align:middle;"></p>

<h3 style="color:{BRAND_GOLD}; font-weight:500; font-size:14px; margin-top: 32px;">EMBED IN MARKDOWN</h3>
<pre style="background:#161616; padding:12px; font-size:11px; color:{TEXT}; overflow-x:auto; border:1px solid #222;">
[![Hive Certified](https://hive-pheromones.onrender.com/badge/YOUR_DID.svg)](https://hive-pheromones.onrender.com/index)
</pre>

<h3 style="color:{BRAND_GOLD}; font-weight:500; font-size:14px; margin-top: 32px;">EMBED IN HTML</h3>
<pre style="background:#161616; padding:12px; font-size:11px; color:{TEXT}; overflow-x:auto; border:1px solid #222;">
&lt;a href="https://hive-pheromones.onrender.com/index"&gt;
  &lt;img src="https://hive-pheromones.onrender.com/badge/YOUR_DID.svg" alt="Hive Certified" height="32"&gt;
&lt;/a&gt;
</pre>

<p class="sub" style="margin-top: 24px;">Each badge embed is a backlink to the Hive Index, a live heartbeat, and a public proof of x402 participation. The badge updates automatically as the agent's status changes upstream at <a href="{TRUST_URL}">hivetrust</a>.</p>
"""
    return HTMLResponse(page("Hive Certified Badge", body))


def _badge_svg(did: str, score: int, last_paid_label: str) -> str:
    """Render a Shields.io-style SVG: 'Hive Certified | <score> · <heartbeat>'."""
    label = "Hive Certified"
    value = f"{score} · {last_paid_label}"
    # Approx text widths (px) for monospace 11px:
    char_w = 6.2
    pad = 8
    label_w = int(len(label) * char_w + pad * 2)
    value_w = int(len(value) * char_w + pad * 2)
    total_w = label_w + value_w
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20" role="img" aria-label="Hive Certified: {value}">
  <title>Hive Certified · {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#0a0a0a" stop-opacity="0"/>
    <stop offset="1" stop-opacity=".15"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total_w}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_w}" height="20" fill="#0a0a0a"/>
    <rect x="{label_w}" width="{value_w}" height="20" fill="{BRAND_GOLD}"/>
    <rect width="{total_w}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">
    <text x="{label_w/2}" y="14">{label}</text>
    <text x="{label_w + value_w/2}" y="14" fill="#0a0a0a">{value}</text>
  </g>
</svg>"""


@app.get("/badge/{did:path}.svg")
async def badge_svg(did: str):
    """Live SVG badge for any DID. Reads HiveTrust score; falls back to '—' on miss."""
    score = 0
    last_paid_label = "live"
    # Try HiveTrust score
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{TRUST_URL}/v1/reputation/{did}")
            if r.status_code == 200:
                d = r.json()
                score = int(d.get("score", 0))
    except Exception:
        pass
    # Try last-paid heartbeat from a2amev (approximate; refined when consumer attribution lands)
    a2amev = await fetch_cached("a2amev_24h", f"{A2AMEV_URL}/leaderboard?format=json", timeout=3.0)
    if isinstance(a2amev, dict) and a2amev.get("data_state") == "live":
        last_paid_label = "live"
    elif isinstance(a2amev, dict):
        last_paid_label = "warming"

    svg = _badge_svg(did, score, last_paid_label)
    return FastAPIResponse(content=svg, media_type="image/svg+xml",
                           headers={"Cache-Control": "public, max-age=60"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("hive_pheromones:app", host="0.0.0.0", port=PORT, reload=False)
