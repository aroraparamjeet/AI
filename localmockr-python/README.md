# LocalMockr v2 — API Proxy & Mock Studio

A lightweight, zero-dependency API proxy with a full browser dashboard. Run it locally to intercept HTTP calls from your app and route them based on per-rule configuration — no pip packages, no build step, just Python.

---

## Requirements

- **Python 3.8+** (standard library only — nothing to install)
- A modern browser (Chrome, Edge, Firefox)
- Windows, macOS, or Linux

---

## Quick Start

```powershell
# 1. Clone the repo
git clone https://github.com/aroraparamjeet/AI.git
cd AI/localmockr-python

# 2. Run
python localmockr.py
```

The dashboard opens automatically at **http://localhost:3848**  
Point your app at the proxy: **http://localhost:3847**

### Windows shortcuts

| Script | How to run |
|--------|-----------|
| `run.bat` | Double-click in Explorer, or `.\run.bat` in CMD |
| `run.ps1` | Right-click → Run with PowerShell, or `.\run.ps1` in PowerShell |

---

## Ports

| Port | Purpose |
|------|---------|
| `3847` | Proxy — your app sends all requests here |
| `3848` | Dashboard UI — manage rules, view logs |

---

## Files

| File | Purpose |
|------|---------|
| `localmockr.py` | Main server — proxy logic, dashboard API, all three modes |
| `ui.html` | Browser dashboard (read from disk on every request) |
| `fake_api.py` | Controllable local API for fallback testing (see below) |
| `run.bat` | Simple Windows launcher (CMD/double-click) |
| `run.ps1` | Simple Windows launcher (PowerShell) |
| `mocks.json` | Auto-created — stores your rules and request logs |

---

## The Three Proxy Modes

Set per rule in the dashboard.

| Mode | Behaviour |
|------|-----------|
| 🌐 **Always Network** | Every request is forwarded to the real external API. Your saved response is ignored. |
| 🔀 **Network + Fallback** | Tries the real API first. If it is unreachable or times out, returns your saved local JSON. |
| 📦 **Always Mock** | Always returns your saved local JSON. The external API is never called. |

---

## Creating a Rule

1. Open the dashboard at **http://localhost:3848**
2. Click **＋ New Rule**
3. Fill in:
   - **Path** — e.g. `/api/users` (supports `*` wildcard, e.g. `/api/users/*`)
   - **Method** — GET, POST, PUT, DELETE, PATCH, or ANY
   - **Mode** — choose one of the three above
   - **External URL** — the real API base URL (used in Network and Fallback modes)
   - **Response Body** — the JSON to return in Mock and Fallback modes
4. Click **💾 Save**

Your app now sends requests to `http://localhost:3847/api/users` and LocalMockr handles them according to the rule.

---

## Dynamic Templates

Use these placeholders anywhere in your response body:

| Placeholder | Resolves to |
|-------------|-------------|
| `{{timestamp}}` | Current UTC timestamp — e.g. `2024-11-08T14:32:01Z` |
| `{{random_id}}` | Random 8-character alphanumeric string |

Example:
```json
{
  "id": "{{random_id}}",
  "created_at": "{{timestamp}}",
  "status": "ok"
}
```

---

## Global Base URL

If most of your rules hit the same API, set a **Global Base URL** in Settings instead of repeating it on every rule. Rules with their own External URL override it.

---

## Testing Fallback Mode with `fake_api.py`

`fake_api.py` is a tiny local API you can start and stop on demand to prove fallback works.

### Setup — two terminal windows

**Terminal 1 — LocalMockr:**
```powershell
python localmockr.py
```

**Terminal 2 — Fake API:**
```powershell
python fake_api.py
```

The fake API runs on **http://localhost:9000**.

### Available endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server uptime |
| GET | `/api/stats` | Live stats including a `random_metric` that changes every call |
| GET | `/api/users` | List of 5 users |
| GET | `/api/users/{id}` | Single user by ID |
| POST | `/api/users` | Create a user (echoed back with generated ID) |
| GET | `/api/products` | List of products with stock and ratings |
| GET | `/api/products/{id}` | Single product by ID |
| GET | `/api/orders` | List of orders |

### Step-by-step fallback test

**1. Create a rule in LocalMockr:**

| Field | Value |
|-------|-------|
| Path | `/api/stats` |
| Method | GET |
| Mode | 🔀 Network + Fallback |
| External URL | `http://localhost:9000` |
| Response Body | your fallback JSON (see below) |

**Suggested fallback JSON:**
```json
{
  "source": "FALLBACK",
  "note": "Live API is down — serving cached response",
  "users": { "total": 5, "active": 4 },
  "products": { "total": 5, "in_stock": 4 },
  "orders": { "total": 5, "total_revenue": 306.47 }
}
```

**2. Hit the proxy while the fake API is running:**
```
GET http://localhost:3847/api/stats
```
Response contains `"source": "LIVE"` and a changing `random_metric` — proves it's hitting the real API.

**3. Stop the fake API** — press `Ctrl+C` in Terminal 2.

**4. Hit the proxy again:**
```
GET http://localhost:3847/api/stats
```
Response now contains `"source": "FALLBACK"` — LocalMockr detected the API was down and served your saved JSON automatically.

**5. Restart the fake API** — `python fake_api.py` — and live data returns immediately.

---

## Request Logs

Click the **📋 Logs** tab to see every proxied request with:
- Timestamp, method, path
- HTTP status code
- Which mode was used
- Whether the response came from the network or the local mock
- Applied delay

Click **🗑 Clear** to wipe the log.

---

## Themes

Open **⚙️ Settings** → **Appearance** to switch between 8 built-in themes (dark and light) or define custom accent and background colours. Your choice is saved in the browser.

---

## Troubleshooting

**Dashboard is blank / all black**  
Make sure `ui.html` is in the same folder as `localmockr.py`. The server reads it from disk on every request.

**"Cannot reach server" toast in the dashboard**  
`localmockr.py` is not running, or something else is on port 3848. Check your terminal for errors.

**Port already in use**  
Another process is using 3847 or 3848. Find and stop it, or edit `PROXY_PORT` / `UI_PORT` at the top of `localmockr.py`.

**Fallback not triggering**  
Check the network timeout setting on the rule — the default is 8 seconds. If the external API is slow but not down, LocalMockr waits the full timeout before declaring failure. Reduce the timeout to trigger fallback faster during testing.

**Rules not saving**  
`mocks.json` is written to the same folder as `localmockr.py`. Make sure the folder is writable.
