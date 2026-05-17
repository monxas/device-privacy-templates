# Template schema

Every file in `templates/` follows the same structure.

## Top-level fields

```yaml
name: lg-tv                                 # required, matches filename
description: "LG webOS smart TVs"           # required, one line
default_tier: 2                             # required, fallback if a domain omits its tier
last_observed: "2026-05-17"                 # required, ISO date of last re-observation
tested_firmware: "webOS p20.04.54.40"       # required, exact version string the maintainer ran
tested_hardware: "LG 43UQ80006LB"           # required, model name
maintainer: "monxas"                        # optional, GitHub handle or "community"

domains:                                    # required, list (see below)
  - ...
```

## Domain entry

Each entry blocks one tracker. Two forms allowed:

### Exact-match

```yaml
- domain: ad.lgappstv.com
  tier: 1
  category: ads
  why_block: "Ad server for the LG Content Store"
  breaks_if_blocked: "Removes banner ads in the LG Content Store"
  observed_via: "Zeek ssl.log on LG OLED CX, 2026-05"   # optional but recommended
```

### Regex

```yaml
- regex: '(\.|^)mrf\.io$'
  tier: 1
  category: analytics
  why_block: "Marfeel — A/B testing + experience experiments"
  breaks_if_blocked: "Nothing user-visible"
```

Use `regex` when the tracker uses random subdomains (e.g. `25755activ.ibroadlink.com`, `device-gateway-deu-6dc239d5.ibroadlink.com`). Use `domain` for stable hostnames.

## Required fields per entry

| Field | Required | Notes |
| --- | :---: | --- |
| `domain` *or* `regex` | ✅ (one of) | The thing being blocked |
| `tier` | recommended | Falls back to template's `default_tier` if omitted |
| `category` | ✅ | One of: `ads`, `telemetry`, `analytics`, `account`, `backbone`, `update`, `crash`, `voice` |
| `why_block` | ✅ | Short reason in plain English |
| `breaks_if_blocked` | ✅ | What stops working — honest, even if "nothing user-visible" |
| `observed_via` | optional | How you confirmed (Zeek log, mitmproxy, public docs, manufacturer wiki, etc.) |

## Tiers

| Tier | Meaning | Examples |
| ---: | --- | --- |
| **1** | Pure ads, telemetry, 3rd-party SDKs. Always safe to block. | Adobe Analytics, Marfeel, AppsFlyer |
| **2** | Tracking-heavy services tied to features you may not use. Default for `--tier`. | Personalization servers, recommendation APIs |
| **3** | Aggressive: manufacturer account, OTA updates, content discovery. May leave the device in a degraded state. | LG account auth, Roku account, Echo's voice backend |

## Category values

Keep these consistent so the apply script can group/report by category later.

- `ads` — ad-serving (banner inventory, video pre-roll, etc.)
- `telemetry` — device usage metrics back to the manufacturer
- `analytics` — 3rd-party analytics SDKs (Mixpanel, Amplitude, Adobe)
- `account` — login / device identity / household linking
- `backbone` — the device's primary cloud connection (Amazon AVS, LG ThinQ, Roku Channel Store)
- `update` — OTA firmware/app updates
- `crash` — crash reporting (Crashlytics, Bugsnag)
- `voice` — voice assistant inference endpoints

## How freshness works

Each template has `last_observed`. When you re-validate a template against the latest firmware, bump this date and add a one-line note in `CHANGELOG.md`.

If a template's `last_observed` is older than **12 months**, the apply script will print a warning. (Not blocking — just a heads-up.)

## A complete example

```yaml
name: example-device
description: "Example device class for the schema doc"
default_tier: 2
last_observed: "2026-05-17"
tested_firmware: "1.2.3"
tested_hardware: "Acme HomeWidget v2"
maintainer: "your-github-handle"

domains:

  - domain: telemetry.acme.com
    tier: 1
    category: telemetry
    why_block: "Anonymized device usage stats to Acme"
    breaks_if_blocked: "Acme app shows '?' on usage chart"
    observed_via: "Zeek ssl.log, 2026-05-15"

  - regex: '(\.|^)track\.acme-partner\.io$'
    tier: 1
    category: analytics
    why_block: "Acme partner sells aggregated data — embedded SDK"
    breaks_if_blocked: "Nothing"

  - domain: ota.acme.com
    tier: 3
    category: update
    why_block: "Firmware updates from manufacturer"
    breaks_if_blocked: "Device stuck on current firmware — apply only if running custom firmware"
```
