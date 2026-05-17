#!/usr/bin/env python3
"""
apply-to-pihole.py — push a curated template to a Pi-hole 6 group.

Usage:
  ./scripts/apply-to-pihole.py --template lg-tv --group tv-living --diff
  ./scripts/apply-to-pihole.py --template lg-tv --group tv-living --apply
  ./scripts/apply-to-pihole.py --template iphone-ios --group ramon-iphone --tier 1 --apply

Env vars:
  PIHOLE_URL       (default: http://pi.hole:8080)
  PIHOLE_PASSWORD  (required)

The script:
  1. Loads templates/<name>.yaml.
  2. Logs into Pi-hole 6 REST API.
  3. Ensures the named group exists (creates if missing).
  4. Diffs the template's domains against what's already in that group.
  5. With --diff: prints the diff and exits.
  6. With --apply: pushes ADD / KEEP / REMOVE changes via API.

No registry. No Zeek. No L3 gateway. Just template → Pi-hole.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Any

try:
    import yaml
except ImportError:
    sys.stderr.write("pyyaml is required.  pip install pyyaml\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# Pi-hole 6 REST client (minimal, only what this script needs)
# ---------------------------------------------------------------------------

class Pihole:
    def __init__(self, base: str, password: str):
        self.base = base.rstrip("/")
        self.password = password
        self.sid: Optional[str] = None

    def _http(self, method: str, path: str, body: Any = None):
        data = None
        headers = {"X-FTL-SID": self.sid or ""}
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, method=method, headers=headers, data=data)
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)

    def login(self):
        s, d = self._http("POST", "/api/auth", body={"password": self.password})
        sid = (d or {}).get("session", {}).get("sid")
        if not sid:
            raise RuntimeError(f"Pi-hole login failed: {d}")
        self.sid = sid

    def ensure_group(self, name: str) -> int:
        s, d = self._http("GET", "/api/groups")
        for g in (d or {}).get("groups", []):
            if g["name"] == name:
                return g["id"]
        s, d = self._http("POST", "/api/groups",
                          body={"name": name, "comment": f"device-privacy-templates", "enabled": True})
        # Pi-hole responses vary; re-query to be safe
        s, d = self._http("GET", "/api/groups")
        for g in (d or {}).get("groups", []):
            if g["name"] == name:
                return g["id"]
        raise RuntimeError(f"could not create or find group: {name}")

    def list_domains(self) -> list[dict]:
        s, d = self._http("GET", "/api/domains")
        return (d or {}).get("domains", [])

    def add_domain(self, domain: str, *, regex: bool, groups: list[int], comment: str) -> bool:
        kind = "regex" if regex else "exact"
        body = {"domain": domain, "type": "deny", "kind": kind,
                "comment": comment, "groups": groups, "enabled": True}
        s, _ = self._http("POST", f"/api/domains/deny/{kind}", body=body)
        return s in (200, 201)

    def remove_domain(self, domain: str, *, regex: bool) -> bool:
        kind = "regex" if regex else "exact"
        s, _ = self._http("DELETE", f"/api/domains/deny/{kind}/{urllib.parse.quote(domain, safe='')}")
        return s in (200, 204)


# ---------------------------------------------------------------------------
# Template parsing + diff
# ---------------------------------------------------------------------------

def load_template(path: Path, tier_max: int) -> dict:
    tpl = yaml.safe_load(path.read_text()) or {}
    entries = []
    default_tier = tpl.get("default_tier", 2)
    for d in tpl.get("domains") or []:
        tier = d.get("tier", default_tier)
        if tier > tier_max:
            continue
        if "regex" in d:
            entries.append({"value": d["regex"], "is_regex": True, **d})
        elif "domain" in d:
            entries.append({"value": d["domain"], "is_regex": False, **d})
    return {"meta": {k: v for k, v in tpl.items() if k != "domains"}, "entries": entries}


def diff(ph: Pihole, group_id: int, entries: list[dict]) -> dict:
    existing = ph.list_domains()
    in_group = {(d.get("domain"), d.get("kind") == "regex"): d
                for d in existing if group_id in (d.get("groups") or [])}
    template_keys = {(e["value"], e["is_regex"]): e for e in entries}
    return {
        "add":  [e for k, e in template_keys.items() if k not in in_group],
        "keep": [e for k, e in template_keys.items() if k in in_group],
        "remove": [d for k, d in in_group.items()
                   if k not in template_keys and (d.get("comment") or "").startswith("device-privacy-templates")],
    }


def print_diff(d: dict, template_name: str, group_name: str):
    print(f"\n=== Diff: template '{template_name}' → group '{group_name}' ===\n")
    print(f"  to ADD     : {len(d['add'])}")
    print(f"  to KEEP    : {len(d['keep'])}")
    print(f"  to REMOVE  : {len(d['remove'])} (only nosey-managed)\n")
    for e in d["add"]:
        kind = "regex" if e["is_regex"] else "exact"
        why = (e.get("why_block") or "")[:60]
        breaks = (e.get("breaks_if_blocked") or "")[:50]
        print(f"  + T{e.get('tier','?')} [{kind:5}] {e['value']}")
        if why:
            print(f"       why    : {why}")
        if breaks:
            print(f"       breaks : {breaks}")
    if d["remove"]:
        print()
        for r in d["remove"]:
            kind = "regex" if r.get("kind") == "regex" else "exact"
            print(f"  - [{kind:5}] {r['domain']}  (was managed by this script)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--template", required=True, help="template name (file under templates/, no .yaml)")
    p.add_argument("--group", required=True, help="Pi-hole group name to push into")
    p.add_argument("--tier", type=int, default=2, help="apply tier <= N (1=safe, 2=balanced, 3=aggressive). default 2")
    p.add_argument("--templates-dir", default=str(Path(__file__).parent.parent / "templates"))
    p.add_argument("--pihole-url", default=os.environ.get("PIHOLE_URL", "http://pi.hole:8080"))
    p.add_argument("--pihole-password", default=os.environ.get("PIHOLE_PASSWORD"))
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--diff", action="store_true", help="dry-run, just show the diff")
    mode.add_argument("--apply", action="store_true", help="apply changes (creates group if missing)")
    args = p.parse_args()

    if not args.pihole_password:
        sys.stderr.write("ERR: set PIHOLE_PASSWORD env var (or --pihole-password)\n")
        return 2

    tpl_path = Path(args.templates_dir) / f"{args.template}.yaml"
    if not tpl_path.exists():
        sys.stderr.write(f"ERR: template not found: {tpl_path}\n")
        return 2
    tpl = load_template(tpl_path, tier_max=args.tier)
    meta = tpl["meta"]
    print(f"Template '{meta.get('name','?')}' — {meta.get('description','')}")
    print(f"  last_observed: {meta.get('last_observed','?')}  firmware: {meta.get('tested_firmware','?')}")
    print(f"  tier <= {args.tier} → {len(tpl['entries'])} domains selected")

    ph = Pihole(args.pihole_url, args.pihole_password)
    ph.login()
    group_id = ph.ensure_group(args.group)
    d = diff(ph, group_id, tpl["entries"])
    print_diff(d, args.template, args.group)

    if args.diff:
        return 0

    print(f"\n=== Applying — group_id={group_id} ===\n")
    added = failed = 0
    for e in d["add"]:
        ok = ph.add_domain(e["value"], regex=e["is_regex"], groups=[group_id],
                           comment=f"device-privacy-templates:{args.template}")
        if ok:
            added += 1
        else:
            failed += 1
            print(f"  ! failed to add {e['value']}")
    removed = 0
    for r in d["remove"]:
        if ph.remove_domain(r["domain"], regex=(r.get("kind") == "regex")):
            removed += 1
    print(f"\n  added:   {added}")
    if failed:
        print(f"  failed:  {failed}")
    print(f"  removed: {removed}")
    print(f"  kept:    {len(d['keep'])}\n")
    print(f"Done. Check Pi-hole admin → Groups → {args.group}.")


if __name__ == "__main__":
    sys.exit(main() or 0)
