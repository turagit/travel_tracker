# Travel Tracker

Automated mileage tracking for Dutch tax compliance (rittenadministratie) via iOS Shortcuts.

## The Problem

In the Netherlands, BV owners and ZZP freelancers must maintain a detailed mileage log
("rittenadministratie") for company cars. Each trip needs: date, time, start city, end city,
and optionally odometer readings and trip purpose. Missing logs can trigger a 22% "bijtelling"
on taxable income.

## The Solution

A Python tool that generates three iOS Shortcuts:

| Shortcut | Purpose |
|---|---|
| **Travel Tracker Setup** | One-time config: odometer tracking, trip classification, multi-car |
| **Trip Start** | Auto-logs departure when phone connects to car Bluetooth |
| **Trip End** | Auto-logs arrival when phone disconnects from car Bluetooth |

On iOS 17+, Bluetooth automations run silently — no taps needed.

## Quick Start

```bash
python3 generate.py
```

Then AirDrop the three `.shortcut` files from `output/` to your iPhone.

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed instructions.

## Requirements

- Python 3.10+ (no external dependencies)
- iPhone with iOS 17+ (iOS 16 works but requires manual tap per trip)

## Project Structure

```
src/shortcut_generator/
├── variables.py    # Variable reference builders
├── actions.py      # Shortcut action builders
├── shortcuts.py    # High-level shortcut composers
└── generator.py    # CLI entry, writes .shortcut files
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## How the .shortcut Files Work

`.shortcut` files are binary plists containing workflow actions. This project
generates them programmatically using Python's `plistlib` — no external tools needed.
The generated files can be opened directly on iOS to install the shortcuts.

## License

MIT
