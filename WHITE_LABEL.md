# White-Label Guide — Look Up!

This guide covers everything needed to onboard a new white-label client (hotel, resort, property management company, etc.) from intake to go-live. The entire process is configuration only — no code changes, no rebuilds.

---

## How it works

Each white-label client gets a custom hostname (e.g. `sky.grandmaui.com`). When a visitor loads that hostname, the app fetches the tenant config from the backend, applies the client's colors and logo, and runs as a fully branded experience — all on the same shared codebase and database.

The client sees:
- Their logo in the nav bar
- Their brand colors throughout the UI
- Their property pre-loaded as the default location
- A bookmarkable/installable PWA at their URL (no App Store needed)

---

## Step 1 — Collect client info

Send the client (or their contact) a short intake form. You need:

| Field | Example | Notes |
|---|---|---|
| Brand / property name | `Grand Wailea Stargazing` | Shown in the nav and browser tab |
| Logo URL | `https://cdn.grandwailea.com/logo.png` | Hosted on their CDN or upload to S3/Cloudflare Images; PNG/SVG, transparent bg, min 200px wide |
| Primary color | `#1a5276` | Their brand hex — used for buttons, active states, accents |
| Property lat/lng | `20.6868, -156.4425` | Drop a pin in Google Maps → right-click → copy coordinates |
| Contact email | `concierge@grandwailea.com` | For notification sender info |
| Hostname | `sky.grandwailea.com` | The subdomain they'll CNAME to you (see Step 3) |
| Feature toggles | notifications: yes, AR: yes | Usually leave both on |

---

## Step 2 — Generate an admin key (one-time setup)

If you haven't already, set `ADMIN_KEY` in your backend environment (Railway dashboard):

```bash
openssl rand -hex 32
# e.g.: a3f8c2...  → paste this into Railway env vars as ADMIN_KEY
```

This key protects all `/api/admin/*` endpoints. Store it in your password manager.

---

## Step 3 — Create the tenant record

Run this curl from your terminal (replace values with the client's info and your backend URL):

```bash
curl -X POST https://your-backend.up.railway.app/api/admin/tenants \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -d '{
    "hostname": "sky.grandwailea.com",
    "brand_name": "Grand Wailea Stargazing",
    "logo_url": "https://cdn.grandwailea.com/logo-white.png",
    "primary_color": "#1a5276",
    "property_name": "Grand Wailea, A Waldorf Astoria Resort",
    "default_lat": 20.6868,
    "default_lng": -156.4425,
    "contact_email": "concierge@grandwailea.com",
    "show_notifications": true,
    "show_ar_mode": true
  }'
```

A `201 Created` response means the tenant is live in the database immediately — no restart needed.

**To update a tenant later** (logo change, color update, etc.):

```bash
curl -X PUT https://your-backend.up.railway.app/api/admin/tenants/sky.grandwailea.com \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -d '{ "logo_url": "https://cdn.grandwailea.com/new-logo.png", ... }'
```

**To list all tenants:**

```bash
curl https://your-backend.up.railway.app/api/admin/tenants \
  -H "X-Admin-Key: YOUR_ADMIN_KEY"
```

**To deactivate a tenant** (they stop paying, etc.):

```bash
curl -X DELETE https://your-backend.up.railway.app/api/admin/tenants/sky.grandwailea.com \
  -H "X-Admin-Key: YOUR_ADMIN_KEY"
```

---

## Step 4 — Set up the domain

### Option A: Subdomain of yours (fastest)

The client doesn't touch their DNS. You create `sky.grandwailea.lookupapp.app` — handled entirely on your Vercel dashboard, no client action required.

1. Vercel dashboard → your project → Settings → Domains → Add `sky.grandwailea.lookupapp.app`
2. Share that URL with the client

### Option B: Client's own subdomain (more professional)

The client adds one DNS record on their end — a CNAME. This is usually a 5-minute task for their IT person or domain registrar support.

1. Vercel dashboard → your project → Settings → Domains → Add `sky.grandwailea.com`
2. Vercel shows you a CNAME target (e.g. `cname.vercel-dns.com`)
3. Send the client this instruction:

   > "Please add a CNAME record in your DNS:
   > - **Name/Host**: `sky`
   > - **Value/Target**: `cname.vercel-dns.com`
   > - **TTL**: Auto or 3600"

4. Vercel provisions the SSL certificate automatically once the record propagates (usually under 10 minutes)

---

## Step 5 — Test it

Open `https://sky.grandwailea.com` (or your subdomain URL) in a private browser window.

Check:
- [ ] Logo appears in the nav bar
- [ ] Brand color is applied to buttons, active tabs, and accents
- [ ] Browser tab title shows the brand name
- [ ] The property location is pre-populated on first load (if `default_lat`/`default_lng` were set)
- [ ] Events load correctly for the property's coordinates
- [ ] AR mode works on mobile

**Test the tenant config endpoint directly:**

```bash
curl "https://your-backend.up.railway.app/api/tenant?host=sky.grandwailea.com"
```

Should return the client's config, not the default Look Up! config.

---

## Step 6 — Deliver to the client

Send the client:
1. **The URL** — `https://sky.grandwailea.com`
2. **A QR code** — generate at [qr.io](https://qr.io) or [qrcode-monkey.com](https://www.qrcode-monkey.com); use their brand color if you want
3. **Install instructions for guests**:
   - iOS: "Open in Safari → tap Share → Add to Home Screen"
   - Android: "Open in Chrome → tap the menu (⋮) → Install app"

That's it. The client has nothing to manage — no login, no dashboard, no app to maintain.

---

## Checklist summary

```
[ ] Collect: brand name, logo URL, primary color, lat/lng, hostname
[ ] Run POST /api/admin/tenants curl
[ ] Add domain in Vercel dashboard
[ ] Client adds CNAME (Option B only)
[ ] Test in private window
[ ] Send URL + QR code to client
```

Typical time from intake form to go-live: **under 2 hours**.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Page still shows "Look Up!" branding | Check `GET /api/tenant?host=<hostname>` — if it returns `is_white_label: false`, the hostname in the DB doesn't match exactly (check for `www.` prefix, trailing slash, etc.) |
| Logo not showing | Verify the logo URL is publicly accessible (open it in an incognito tab); check for CORS headers if it's on a private CDN |
| Color not applying | Open DevTools → Elements → check `<style id="tenant-theme">` is present in `<head>` |
| Domain shows SSL error | Wait up to 30 min after CNAME propagation; Vercel auto-provisions certs |
| CNAME not propagating | Run `dig sky.grandwailea.com CNAME` to check; typical propagation is 5–15 min, max 24h |
