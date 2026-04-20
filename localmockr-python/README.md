# LocalMockr Python - API Proxy & Mock Dashboard

Zero-dependency proxy server with a full browser dashboard. Intercepts HTTP calls and routes them based on per-rule configuration.

## Requirements

- Python 3.8+ (no pip packages needed)

## Running

```bash
python embed_ui.py
python localmockr_embedded.py
```

Open **http://localhost:3848** in your browser.
Point your app at **http://localhost:3847**.

## Ports

| Port | Purpose |
|------|---------|
| 3847 | Proxy server - your app sends requests here |
| 3848 | Dashboard UI |

## Three Proxy Modes

| Mode | Behaviour |
|------|-----------|
| Always Network | Forward every request to the real external API |
| Network + Fallback | Try real API first, use saved response if unavailable |
| Always Mock | Always return saved local JSON |

## Files

| File | Purpose |
|------|---------|
| `localmockr.py` | Main server - proxy logic, all three modes |
| `ui.html` | Browser dashboard |
| `embed_ui.py` | Bakes ui.html into the Python source |
| `build.bat` | Build standalone .exe (Windows) |

## Dynamic Templates

Use in response body:

| Placeholder | Value |
|-------------|-------|
| `{{timestamp}}` | Current UTC timestamp |
| `{{random_id}}` | Random 8-char string |

## Building .exe

```bash
pip install pyinstaller
python embed_ui.py
pyinstaller --onefile --console --name LocalMockr localmockr_embedded.py
```
