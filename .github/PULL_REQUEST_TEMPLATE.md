## What this PR changes

<!-- Briefly: a new domain, a new template, a re-validation, a script tweak. -->

## Evidence

<!-- How did you confirm this domain is a tracker and not a legit service?
     Zeek log line, mitmproxy session, public docs, manufacturer wiki — anything but "I think it's a tracker". -->

## Per-domain checklist (if you added or changed a domain)

- [ ] `domain:` or `regex:` is set (one, not both)
- [ ] `tier:` is set (1, 2, or 3) or template `default_tier` covers it
- [ ] `category:` matches one of: ads, telemetry, analytics, account, backbone, update, crash, voice
- [ ] `why_block:` describes what the endpoint does (1 sentence)
- [ ] `breaks_if_blocked:` honestly describes what stops working
- [ ] `observed_via:` (recommended) — Zeek log? mitmproxy? manufacturer docs?
- [ ] Tested for at least 30 min after blocking to confirm `breaks_if_blocked:` is accurate
- [ ] CHANGELOG entry added under `## [Unreleased]`

## Re-validation checklist (if you bumped `last_observed`)

- [ ] Re-ran the apply script with `--diff` and inspected the output
- [ ] Removed any endpoints that no longer respond / no longer resolve
- [ ] Bumped `tested_firmware:` to the version you ran against
