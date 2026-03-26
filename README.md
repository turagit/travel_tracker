# Travel Tracker

Automated mileage tracking for Dutch tax compliance (rittenadministratie) via iOS Shortcuts.

## The Problem

In the Netherlands, BV owners and ZZP freelancers must maintain a detailed mileage log
("rittenadministratie") for company cars. Each trip needs: date, time, start city, end city,
and optionally odometer readings and trip purpose. Missing logs can trigger a 22% "bijtelling"
on taxable income.

## The Solution

Three iOS Shortcuts that work together:

| Shortcut | Purpose |
|---|---|
| **Travel Tracker Setup** | One-time config: odometer tracking, trip classification, multi-car |
| **Trip Start** | Auto-logs departure when phone connects to car Bluetooth |
| **Trip End** | Auto-logs arrival when phone disconnects from car Bluetooth |

On iOS 17+, Bluetooth automations run silently — no taps needed.

## Install the Shortcuts

The pre-built shortcut files are in the [`output/`](output/) folder:

1. **On your iPhone**, open this repo and tap each `.shortcut` file to install:
   - [`Travel Tracker Setup.shortcut`](output/Travel%20Tracker%20Setup.shortcut)
   - [`Trip Start.shortcut`](output/Trip%20Start.shortcut)
   - [`Trip End.shortcut`](output/Trip%20End.shortcut)
2. **Run "Travel Tracker Setup"** first to configure your preferences
3. **Set up Bluetooth automations** — see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for step-by-step instructions

Alternatively, you can AirDrop, email, or share the files from `output/` to your iPhone via any method — tapping a `.shortcut` file on iOS will prompt you to install it.

## Requirements

- iPhone with iOS 17+ (iOS 16 works but requires manual tap per trip)

## Alternative: Generate Shortcuts Yourself

If you want to customize the shortcuts or regenerate them, you can run the Python generator:

```bash
# Requires Python 3.10+ (no external dependencies)
python3 generate.py
```

This rebuilds the three `.shortcut` files in `output/` from source. Edit `src/shortcut_generator/shortcuts.py` to customize the shortcut behavior.

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed setup instructions.

## Project Structure

```
output/                     # Pre-built .shortcut files (ready to install)
src/shortcut_generator/
  variables.py              # Variable reference builders
  actions.py                # Shortcut action builders
  shortcuts.py              # High-level shortcut composers
  generator.py              # CLI entry, writes .shortcut files
templates/                  # Tax report sample
docs/SETUP_GUIDE.md         # End-user setup instructions
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
