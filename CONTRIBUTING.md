# Contributing

The whole point of this repo is **community-curated**, **dated**, **structured** per-device blocklists. The way you contribute is by observing your own devices and sending PRs.

## Most-wanted contributions (in order)

1. **A new domain inside an existing template** — you observed something the current list misses.
2. **A new template for a device class we don't cover** — Google Nest, Sonos, Apple TV, Android, Shelly, Aqara, Tuya, Tasmota, Ring, Wyze…
3. **Re-validating an existing template** against a newer firmware (bump `last_observed`, mention the firmware version, remove dead endpoints).
4. **Schema improvements** — but discuss in an issue first.
5. **Other code changes to `scripts/apply-to-pihole.py`** — keep the script small; PRs that more than double the LOC will be questioned.

## How to add a domain to an existing template

1. Capture evidence: a Zeek `ssl.log` line, a mitmproxy session, a manufacturer FAQ, *something*. "I assume it's a tracker" is not enough.
2. Edit the template YAML. Use the schema in [docs/SCHEMA.md](docs/SCHEMA.md).
3. **Be honest** about `breaks_if_blocked`. If you don't know yet, write "unknown — please test and update". Better honest than wrong.
4. Bump `last_observed` if you also re-verified the rest of the template.
5. Add a one-line entry under `## [Unreleased]` in `CHANGELOG.md`.
6. Open a PR. Include in the description: how you observed it (1–2 sentences), and what you tested (e.g. "left LG TV on for 6h, restarted app store, checked all menus").

## How to add a new template (new device class)

1. Copy the smallest existing template (`roku-tv.yaml` is a fine reference) and rename.
2. Fill in `name`, `description`, `default_tier`, `last_observed`, `tested_firmware`, `tested_hardware`, `maintainer`.
3. Start with **3–10 high-confidence Tier 1 entries** — pure ads / telemetry. Don't pad the file.
4. Open a PR. We'd rather have 5 well-documented entries than 50 copy-pasted guesses.

## Per-domain PR checklist

```
- [ ] One of: `domain:` or `regex:`
- [ ] `tier:` is set (1, 2, or 3) or template `default_tier` covers it
- [ ] `category:` matches one of: ads, telemetry, analytics, account, backbone, update, crash, voice
- [ ] `why_block:` describes what the endpoint does (1 sentence)
- [ ] `breaks_if_blocked:` honestly describes what stops working (including "nothing user-visible")
- [ ] `observed_via:` (recommended) — Zeek log? mitmproxy? manufacturer docs?
- [ ] Tested for at least 30 min after blocking to confirm `breaks_if_blocked:` is accurate
```

## What we'll reject

- Domains taken from older adlists with no verification. We don't blindly inherit cruft.
- Blocking a manufacturer's core service (e.g. `apple.com`, `amazon.com`) without explicit Tier 3 justification.
- Entries with empty or copy-pasted `why_block` / `breaks_if_blocked`.
- "I think this is a tracker" without evidence.

## Code of conduct

Standard: be kind, assume good faith, no harassment. The maintainers (currently @monxas) reserve the right to close PRs that don't follow the rules above.

## Maintainer notes

- We don't merge PRs that fail CI. CI runs YAML lint + schema validation.
- We don't accept GUIs, ORMs, or "let's add support for X DNS backend" as a single PR. Pi-hole is the canonical backend; everything else is a separate proposal.
- This repo is intentionally small. If you want a richer system (UI, L3 gateway, forensic Zeek capture), see [nosey-privacy-monitor](https://github.com/monxas/nosey-privacy-monitor) — different repo, different scope.

Thanks for caring about this.
