---
name: New tracker found
about: You observed a tracker that's missing from an existing template
labels: new-tracker
---

**Template**
Which template should this go into? (e.g. `lg-tv`, `iphone-ios`)

**Domain or regex**
The exact endpoint. Use a regex if random subdomains are involved.

**How you observed it**
- [ ] Zeek `ssl.log`
- [ ] mitmproxy
- [ ] Pi-hole query log
- [ ] tcpdump
- [ ] Manufacturer FAQ / source code / leak
- [ ] Other (describe)

**Suggested tier and category**
- Tier (1=safe / 2=balanced / 3=aggressive):
- Category (ads / telemetry / analytics / account / backbone / update / crash / voice):

**why_block (1 sentence)**

**breaks_if_blocked (1 sentence — honest)**

**Have you tested blocking it?**
For how long, and what did you check?
