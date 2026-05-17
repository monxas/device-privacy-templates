<div align="center">

# device-privacy-templates  *(archived)*

**Per-device blocklists for Pi-hole — with notes on what each domain does and what breaks if you block it.**

</div>

> ## 📦 Archived
>
> This repo is **archived**. The author measured empirically that a well-configured Pi-hole with mainstream gravity adlists (Steven Black, AdGuard DNS, EasyPrivacy, firstparty-trackers, …) **already blocks ~64% of what these templates would push** — and most of the residual is Tier 2/3 manufacturer-specific endpoints (LG ThinQ, Samsung TV Plus, Apple location/MDM) that break features many users still want.
>
> The genuinely novel piece was the **YAML schema** (`breaks_if_blocked:` + `why_block:` + `tier:` per domain) — a way to document _why_ to block something, not just _what_. Left in place as schema reference; PRs no longer reviewed.
>
> Companion (also archived) repo with the richer L3 gateway / Zeek inspection / web UI: [`nosey-privacy-monitor`](https://github.com/monxas/nosey-privacy-monitor).

---

## What this is

Five curated YAML blocklists, one per device class:

| Template | Device | Domains | Tier 1 / 2 / 3 | Firmware tested |
| --- | --- | ---: | --- | --- |
| [`lg-tv`](templates/lg-tv.yaml) | LG webOS TVs | ~25 | 12 / 9 / 4 | webOS p20.04.54.40 |
| [`samsung-tv`](templates/samsung-tv.yaml) | Samsung Tizen TVs | ~18 | 9 / 6 / 3 | Tizen 6.x / 7.x |
| [`roku-tv`](templates/roku-tv.yaml) | Roku TVs + sticks | ~15 | 8 / 5 / 2 | Roku OS 13.x |
| [`echo-dot`](templates/echo-dot.yaml) | Amazon Echo / Dot / Show | ~20 | 10 / 7 / 3 | fos-aspen 1.10.x |
| [`iphone-ios`](templates/iphone-ios.yaml) | iPhone / iPad on iOS 17–18 | ~22 | 9 / 9 / 4 | iOS 18.5 |

Each domain comes with four fields you won't find in other blocklists:

```yaml
- regex: '(\.|^)mrf\.io$'
  tier: 1                                       # 1 safe, 2 balanced, 3 aggressive
  category: analytics
  why_block: "Marfeel — A/B testing + experience experiments on news sites"
  breaks_if_blocked: "News articles still load; no in-page experiment UI"
```

That's the whole point of this repo: **informed consent over blanket blocking**.

---

## Why this exists (the gap in existing blocklists)

| | Public adlists (Steven Black, HaGeZi, etc.) | Per-device adlists (Perflyst SmartTV) | **device-privacy-templates** |
| --- | :---: | :---: | :---: |
| Per-device scope | ❌ | ✅ | ✅ |
| Tiered severity (safe / balanced / aggressive) | ❌ | partial (free-text) | ✅ structured |
| `why_block` per domain | ❌ | free-text comments | ✅ structured field |
| `breaks_if_blocked` per domain | ❌ | rare | ✅ structured field |
| Dated against firmware version | ❌ | ❌ | ✅ |
| Machine-readable schema | ❌ | ❌ | ✅ YAML |

The structured schema is the actual wedge. Free-text comments don't survive a `cat *.txt > big.txt` — a YAML schema does, and a script can read it.

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/monxas/device-privacy-templates.git
cd device-privacy-templates

# 2. Install pyyaml
pip install pyyaml

# 3. Preview what would change in a Pi-hole group
PIHOLE_URL=http://pi.hole:8080 PIHOLE_PASSWORD=your_admin_password \
  ./scripts/apply-to-pihole.py --template lg-tv --group living-room-tv --tier 2 --diff

# 4. Apply for real (creates the group if missing)
PIHOLE_URL=http://pi.hole:8080 PIHOLE_PASSWORD=your_admin_password \
  ./scripts/apply-to-pihole.py --template lg-tv --group living-room-tv --tier 2 --apply

# 5. In Pi-hole admin: assign the TV's IP to the 'living-room-tv' group. Done.
```

**Requires**: Pi-hole 6 (REST API). No Zeek, no nftables, no extra services. If you already run Pi-hole, you're already set up.

---

## What the apply script does

1. Loads `templates/<name>.yaml`.
2. Logs into Pi-hole 6 via the REST API.
3. Ensures the named group exists (creates it if missing).
4. Diffs the template's domains against what's already in the group:
   - **ADD** — in the template, not yet in the group.
   - **KEEP** — already in the group.
   - **REMOVE** — in the group with a comment saying it was added by this script, but no longer in the template.
5. With `--diff`: prints the diff and exits (read-only).
6. With `--apply`: pushes ADD/REMOVE via API.

The script touches **only the domains it manages itself** (identified by the comment prefix). Your manual entries stay untouched.

---

## Tiers

| Tier | What it blocks | Risk |
| ---: | --- | --- |
| **1** | Pure ads, telemetry, and 3rd-party trackers | Always safe to block. Nothing user-visible breaks. |
| **2** | Tracking-heavy services tied to features you may not use | Default. May break minor features (push notifications you never asked for, ad personalization screens). |
| **3** | Aggressive — manufacturer account services, OTA updates, content discovery | Breaks the device's connection to the manufacturer's cloud. Apply only if you're using the device offline or via standalone apps. |

Pass `--tier 1`, `--tier 2`, or `--tier 3` to the apply script. Default is `2`.

---

## Freshness

Templates have a `last_observed` field. The point of this repo is **dated data**: the LG TV adlist from 2020 doesn't block `avs.amazon.dev` because that host didn't exist yet. We re-observe periodically and bump the date.

| Template | Last observed | Maintainer |
| --- | --- | --- |
| `lg-tv` | 2026-05-17 | @monxas |
| `iphone-ios` | 2026-05-17 | @monxas |
| `echo-dot` | 2026-05-17 | @monxas |
| `samsung-tv` | 2026-05-17 | community-reported |
| `roku-tv` | 2026-05-17 | community-reported |

If you observe a tracker that's missing — **please open a PR**. Instructions in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Honest limitations

- ❌ This is **DNS-level blocking only**. Devices that hardcode IPs or use DoH bypass it. (Use a DNS-over-HTTPS killer at your firewall — out of scope for this repo. See HaGeZi's `doh.txt`.)
- ❌ Templates **get stale**. Manufacturers move endpoints every 6–12 months. PRs welcome.
- ❌ This is **not a replacement for blanket adlists** (Steven Black, HaGeZi). Use those for browser-level ad blocking. Use these on top for per-device curation.
- ❌ **No GUI** — this is a script. The "UI" is `apply-to-pihole.py --diff`.

For a richer setup (L3 transparent gateway, Zeek SNI inspection, forensic capture reports), see the parent project [`nosey-privacy-monitor`](https://github.com/monxas/nosey-privacy-monitor) — heavier infra, smaller audience.

---

## License

MIT. Use, fork, redistribute. If you find new tracking domains, please open a PR.

---

<sub>Curated by humans who actually run their TVs and phones through this. Updated against firmware that exists in 2026, not 2018.</sub>
