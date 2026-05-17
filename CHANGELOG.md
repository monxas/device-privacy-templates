# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning is [SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-05-17

### Added
- Initial 5 device templates, each with structured schema:
  - `lg-tv` (LG webOS, tested vs webOS p20.04.54.40)
  - `samsung-tv` (Tizen 6.x / 7.x, community-reported)
  - `roku-tv` (Roku OS 13.x, community-reported)
  - `echo-dot` (Echo / Dot / Show, fos-aspen 1.10.x)
  - `iphone-ios` (iOS 17–18, tested vs iOS 18.5)
- `scripts/apply-to-pihole.py` — single Python script (no extra services) that pushes
  a template to a Pi-hole 6 group via REST API, with `--diff` / `--apply` modes
  and `--tier N` filtering.
- `docs/SCHEMA.md` — full per-field documentation of the template format.
- `CONTRIBUTING.md` — per-domain PR checklist + maintainer rules.
- GitHub Actions workflow: YAML lint + script smoke test + schema validation.

### Notes
- The original code lived in [`nosey-privacy-monitor`](https://github.com/monxas/nosey-privacy-monitor),
  which still exists as a richer (heavier) alternative for users who also want an L3
  transparent gateway, Zeek SNI inspection, and a web UI bridge. This repo is the
  focused subset: just templates + a 200-LOC apply script.
