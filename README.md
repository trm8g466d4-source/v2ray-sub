# v2ray subscription

Daily auto-updated v2ray subscription from wenpblog.com.

## Subscription URLs

Use any of the following URLs in your v2ray client:

| URL | Access |
|-----|--------|
| `https://cdn.jsdelivr.net/gh/trm8g466d4-source/v2ray-sub@main/v2ray_sub.txt` | jsdelivr CDN (recommended) |
| `https://raw.githubusercontent.com/trm8g466d4-source/v2ray-sub/main/v2ray_sub.txt` | GitHub raw |

## Endpoints

| File | Description |
|------|-------------|
| `v2ray_sub.txt` | Base64 encoded subscription (v2rayN/v2rayNG) |
| `v2ray_nodes_raw.txt` | Raw node URIs, one per line |
| `status.json` | Update status and node count |
| `fetch_nodes.py` | Node fetcher script (runs on GitHub Actions) |

## Auto Update

GitHub Actions runs daily at 09:00 (UTC+8) to fetch latest nodes automatically.
