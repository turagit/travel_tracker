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

### Option 1: iCloud Links (easiest)

Tap these links on your iPhone to install directly:

| Shortcut | Install Link |
|---|---|
| Travel Tracker Setup | `<PASTE_ICLOUD_LINK_HERE>` |
| Trip Start | `<PASTE_ICLOUD_LINK_HERE>` |
| Trip End | `<PASTE_ICLOUD_LINK_HERE>` |

> **Note to repo owner:** To generate these links, create the shortcuts on your device using the [Shortcut Creation Guide](docs/SHORTCUT_CREATION_GUIDE.md), then long-press each shortcut > Share > Copy iCloud Link. Replace the placeholders above.

### Option 2: Create them yourself

Follow the step-by-step [Shortcut Creation Guide](docs/SHORTCUT_CREATION_GUIDE.md) to build the three shortcuts in the Shortcuts app (~10 minutes).

## After Installing

1. **Run "Travel Tracker Setup"** to configure your preferences
2. **Set up Bluetooth automations** — see [Setup Guide](docs/SETUP_GUIDE.md#step-3-set-up-bluetooth-automations) for step-by-step instructions

## Requirements

- iPhone with iOS 17+ (iOS 16 works but requires manual tap per trip)
- Car with Bluetooth or CarPlay

## How It Works

```
Phone connects to car Bluetooth
  → Trip Start runs automatically
  → Logs: date, time, city, odometer, purpose
  → Appends to Apple Note "KMS TAX REPORT FOR [year]"

Phone disconnects from car Bluetooth
  → Trip End runs automatically
  → Logs arrival city, time, odometer
```

At year end, share the note with your accountant. See [sample report](templates/tax_report_template.txt).

## For Developers

The `src/` directory contains a Python generator that produces `.shortcut` files programmatically. Note: Apple requires shortcuts to be signed for import, so generated files serve as a reference implementation rather than installable artifacts.

```bash
python3 -m pytest tests/ -v    # Run tests
python3 generate.py             # Generate .shortcut files (reference only)
```

## Project Structure

```
docs/
  SETUP_GUIDE.md                # End-user setup instructions
  SHORTCUT_CREATION_GUIDE.md    # Step-by-step shortcut creation
src/shortcut_generator/
  variables.py                  # Variable reference builders
  actions.py                    # Shortcut action builders
  shortcuts.py                  # High-level shortcut composers
  generator.py                  # CLI entry, writes .shortcut files
templates/
  tax_report_template.txt       # Sample log output
```

## License

MIT
