# AGENTS.md — travel_tracker (Dutch mileage log via iOS Shortcuts)

Automated *rittenadministratie* for a Dutch company car: three iOS Shortcuts
(Travel Tracker Setup, Trip Start, Trip End) run on car-Bluetooth connect and
disconnect, logging date, time, start and end city, optional odometer and
purpose into the Apple Note "KMS TAX REPORT FOR [year]", which goes to the
accountant at year end. A missing log can trigger the 22% bijtelling. The
Python code here generates `.shortcut` files, but Apple only imports signed
shortcuts, so the generated files are reference only; users build them by
hand from the guide. Public repo, MIT.

## Repo map

- `src/shortcut_generator/` — `variables.py`, `actions.py`, `shortcuts.py`
  (the three shortcuts), `generator.py` (writes `.shortcut` files).
- `generate.py` — `python3 generate.py [output_dir]` (default `output/`).
- `tests/` — pytest: actions, generator, shortcuts, variables.
- `docs/SHORTCUT_CREATION_GUIDE.md` — the real install path: build the
  shortcuts by hand in about 10 minutes. `docs/SETUP_GUIDE.md` — Bluetooth
  automations. `docs/superpowers/` — specs and plans.
- `templates/tax_report_template.txt` — what the yearly note looks like.

## Commands

```bash
python3 -m pytest tests/ -v     # 36 tests
python3 generate.py             # reference .shortcut files into output/
```

`output/` is not gitignored; delete it after looking, don't commit it.

## Hard rules

- The guide and the generator must describe the same three shortcuts; a
  change to one is a change to both.
- The README's iCloud install links are still `<PASTE_ICLOUD_LINK_HERE>`.
  Only the owner can create them on device; never invent links.
- Real trip notes and odometer readings are personal tax records. They never
  enter the repo; `templates/` holds made-up examples only.

## Agent skills

### Issue tracker

Issues live in GitHub. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
