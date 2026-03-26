# Travel Tracker Setup Guide

Complete instructions for setting up automated mileage tracking on your iPhone.

---

## Requirements

- **iPhone** running iOS 17 or later (iOS 16 works but requires a manual tap per trip)
- **Car with Bluetooth** (any car stereo, hands-free system, or CarPlay)

---

## Step 1: Install the Shortcuts

**If iCloud links are available** (check the [README](../README.md)), tap each link on your iPhone to install.

**If no iCloud links yet**, follow the [Shortcut Creation Guide](SHORTCUT_CREATION_GUIDE.md) to build them yourself (~10 minutes).

You need all three shortcuts installed:

| Shortcut | Purpose |
|---|---|
| **Travel Tracker Setup** | One-time configuration |
| **Trip Start** | Logs your departure |
| **Trip End** | Logs your arrival |

---

## Step 2: Run the Setup Shortcut

After installing, open the **Shortcuts** app on your iPhone and run **Travel Tracker Setup**.

It will ask you to configure:

- **Track odometer readings?** — If yes, the shortcut will prompt for your current KM reading at each trip start/end
- **Classify trips?** — If yes, you'll choose Business or Private for each trip
- **Track multiple cars?** — For users with more than one work vehicle

Your preferences are saved to a JSON config file in iCloud Drive (`Shortcuts/travel_tracker_config.json`).

---

## Step 3: Set Up Bluetooth Automations

This is the key step that makes tracking fully automatic. You create two automations — one for Bluetooth **connect** and one for **disconnect**.

### Automation 1: Trip Start (Bluetooth Connect)

1. Open the **Shortcuts** app
2. Tap the **Automation** tab (clock icon at the bottom)
3. Tap **+** in the top-right corner
4. Scroll down and tap **Bluetooth**
5. Tap **Choose** and select your car's Bluetooth device from the list
6. Under "When", make sure **Connects** is selected
7. Tap **Next**
8. Tap **Add Action**
9. Search for "Run Shortcut" and tap it
10. Tap the blue "Shortcut" placeholder and select **Trip Start**
11. **Important:** Toggle **"Run Immediately"** ON to disable the confirmation prompt (iOS 17+)
12. Tap **Done**

### Automation 2: Trip End (Bluetooth Disconnect)

1. In the **Automation** tab, tap **+** again
2. Tap **Bluetooth**
3. Select the same car Bluetooth device
4. Under "When", select **Disconnects**
5. Tap **Next**
6. Tap **Add Action** > search "Run Shortcut" > select it
7. Select **Trip End**
8. Toggle **"Run Immediately"** ON
9. Tap **Done**

> **Note on "Run Immediately":** This toggle appears in iOS 17+. When enabled, the shortcut runs silently in the background with no banner or tap required. On iOS 16, you will see a notification — tap it to log the trip.

---

## Step 4: Verify It Works

1. Get in your car and connect your phone to the car Bluetooth
2. Wait a few seconds — the Trip Start shortcut should run silently
3. Open the **Notes** app — you should see a note titled **"KMS TAX REPORT FOR 2026"** (current year) with a DEPARTURE entry
4. Disconnect from Bluetooth (turn off the car or toggle Bluetooth off)
5. Check the note again — an ARRIVAL entry should appear

---

## How It Works

```
Phone connects to car Bluetooth
        |
        v
[Trip Start shortcut runs]
  - Reads your config preferences
  - Gets current date and time
  - Looks up current city via GPS
  - Optionally asks for odometer reading
  - Optionally asks for trip purpose (Business/Private)
  - Appends DEPARTURE line to Apple Note
        |
        v
  [You drive]
        |
        v
Phone disconnects from car Bluetooth
        |
        v
[Trip End shortcut runs]
  - Same process as above
  - Appends ARRIVAL line to Apple Note
```

---

## Log Format

Each entry in the Apple Note follows this format:

```
[YYYY-MM-DD HH:MM] TYPE | City: <city> | KM: <odometer> | Purpose: <purpose>
```

Example:

```
[2026-01-15 08:30] DEPARTURE | City: Amsterdam | KM: 45230 | Purpose: Business
[2026-01-15 09:15] ARRIVAL | City: Rotterdam | KM: 45298 | Purpose: Business
[2026-01-15 17:00] DEPARTURE | City: Rotterdam | KM: 45298 | Purpose: Business
[2026-01-15 18:10] ARRIVAL | City: Amsterdam | KM: 45366 | Purpose: Business
```

A sample report is in [`templates/tax_report_template.txt`](../templates/tax_report_template.txt).

---

## For Your Accountant

At the end of the tax year:
1. Open the note **"KMS TAX REPORT FOR YYYY"** in the Notes app
2. Select all text > Share > Email or export
3. Send to your accountant or import into your bookkeeping software

The structured format makes it easy to parse into spreadsheets.

---

## Troubleshooting

**The shortcut doesn't run when I connect to Bluetooth.**
- Check that the automation is enabled: Shortcuts > Automation > tap the automation > make sure the toggle is green
- Make sure "Run Immediately" is turned on (iOS 17+) or that you tapped the notification (iOS 16)
- Verify the correct Bluetooth device is selected in the automation

**The city shows as "Unknown" or is wrong.**
- Make sure Location Services are enabled for Shortcuts: Settings > Privacy & Security > Location Services > Shortcuts > "While Using"

**The note is not being created.**
- Ensure the Shortcuts app has access to Notes (Settings > Shortcuts > allow Notes access)
- Run the Trip Start shortcut manually once from the Shortcuts app to grant permissions

**I have two cars.**
- Create separate Bluetooth automations for each car's device. Both call the same Trip Start / Trip End shortcuts.

**I want to change my preferences.**
- Re-run the **Travel Tracker Setup** shortcut at any time.
