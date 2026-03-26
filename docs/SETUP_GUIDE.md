# Travel Tracker Setup Guide

Complete instructions for setting up automated mileage tracking on your iPhone.

---

## Requirements

- **iPhone** running iOS 17 or later (iOS 16 works but requires a manual tap per trip)
- **Car with Bluetooth** (any car stereo or hands-free system)
- **Python 3.10+** on your computer (no external libraries needed)

---

## Step 1: Generate the Shortcuts

On your computer, open a terminal in the project directory and run:

```bash
python3 generate.py
```

This creates three files in the `output/` folder:

| File | Purpose |
|---|---|
| `Travel Tracker Setup.shortcut` | One-time configuration |
| `Trip Start.shortcut` | Logs your departure |
| `Trip End.shortcut` | Logs your arrival |

---

## Step 2: Install on iPhone

Transfer all three `.shortcut` files from `output/` to your iPhone using one of these methods:

**AirDrop (recommended)**
1. Make sure AirDrop is enabled on your iPhone (Settings > General > AirDrop > Everyone)
2. On your Mac, right-click each `.shortcut` file and choose Share > AirDrop
3. Select your iPhone
4. Tap "Add" when prompted on the iPhone

**iCloud Drive**
1. Copy the three files to your iCloud Drive folder on the computer
2. On the iPhone, open the Files app and navigate to iCloud Drive
3. Tap each `.shortcut` file to install it

**Email**
1. Attach the three files to an email and send it to yourself
2. Open the email on your iPhone, tap each attachment, then tap "Add to Shortcuts"

---

## Step 3: Run the Setup Shortcut

After installing, open the **Shortcuts** app on your iPhone and run **Travel Tracker Setup**.

The setup shortcut will ask you to configure:

- **Starting odometer reading** — the current mileage on your car
- **Trip classification default** — whether new trips default to Business or Private
- **Car name** — a label used to identify your vehicle in the log (useful if you have multiple cars)

Your answers are saved to a text file in iCloud Drive under `Shortcuts/TravelTracker/config.txt`.

---

## Step 4: Set Up Bluetooth Automations

This is the key step that makes tracking fully automatic. You will create two automations — one that fires when your phone **connects** to the car Bluetooth, and one when it **disconnects**.

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
11. **Important:** Tap **Run Immediately** to disable the confirmation prompt (iOS 17+ only)
12. Tap **Done**

### Automation 2: Trip End (Bluetooth Disconnect)

1. In the **Automation** tab, tap **+** again
2. Tap **Bluetooth**
3. Select the same car Bluetooth device
4. Under "When", select **Disconnects**
5. Tap **Next**
6. Tap **Add Action** > search "Run Shortcut" > select it
7. Select **Trip End**
8. Tap **Run Immediately** to disable the confirmation prompt
9. Tap **Done**

> **Note on "Run Immediately":** This toggle appears in iOS 17+. When enabled, the shortcut runs silently in the background with no banner or tap required. On iOS 16, you will see a notification — tap it to log the trip.

---

## Step 5: Verify It Works

1. Get in your car and connect your phone to the car Bluetooth (play music, make a call, or just wait for auto-connect)
2. Wait a few seconds — the Trip Start shortcut should run silently
3. Check your log: open the **Files** app > iCloud Drive > Shortcuts > TravelTracker > `log.txt`
4. You should see a DEPARTURE entry with today's date, time, and city
5. Disconnect from Bluetooth (turn off the car or toggle Bluetooth off)
6. Check the log again — an ARRIVAL entry should appear

---

## How It Works

```
Phone connects to car Bluetooth
        |
        v
[Trip Start shortcut runs]
  - Gets current time
  - Looks up current city (via location)
  - Reads odometer from config
  - Appends DEPARTURE line to log.txt
        |
        v
  [You drive]
        |
        v
Phone disconnects from car Bluetooth
        |
        v
[Trip End shortcut runs]
  - Gets current time
  - Looks up current city (via location)
  - Reads odometer from config
  - Appends ARRIVAL line to log.txt
```

---

## Log Format

Each entry in `log.txt` follows this format:

```
[YYYY-MM-DD HH:MM] TYPE | City: <city> | KM: <odometer> | Purpose: <purpose>
```

Example:

```
[2026-01-15 08:30] DEPARTURE | City: Amsterdam | KM: 45230 | Purpose: Business
[2026-01-15 09:15] ARRIVAL | City: Rotterdam | KM: 45298 | Purpose: Business
```

- **TYPE** is either `DEPARTURE` or `ARRIVAL`
- **City** is determined automatically from your GPS location
- **KM** is the odometer reading you track in the config
- **Purpose** is `Business` or `Private`

---

## For Your Accountant

At the end of the tax year, share the `log.txt` file from iCloud Drive > Shortcuts > TravelTracker.

The file is plain text and can be opened in any spreadsheet or text editor. Each line is a complete record suitable for Dutch rittenadministratie requirements.

A sample of what the log looks like is in `templates/tax_report_template.txt`.

---

## Troubleshooting

**The shortcut doesn't run when I connect to Bluetooth.**
- Check that the automation is enabled: Shortcuts > Automation > tap the automation > make sure the toggle at the top is green
- Make sure "Run Immediately" is turned on (iOS 17+) or that you tapped the notification (iOS 16)
- Verify the correct Bluetooth device is selected in the automation

**The city shows as "Unknown" or is wrong.**
- The shortcut uses your GPS location. Make sure Location Services are enabled for Shortcuts: Settings > Privacy & Security > Location Services > Shortcuts > "While Using"
- If you are in an area with poor GPS, the city lookup may fail — the entry will still be logged with a fallback value

**The log file is missing.**
- Run the Setup shortcut again. It creates the `TravelTracker` folder and initial config if they don't exist.

**I have two cars.**
- Run the Setup shortcut to set a car name, then create a separate set of automations for the second car's Bluetooth device. Each automation calls the same Trip Start / Trip End shortcuts, but you can adjust the car name in the config between trips if needed.

**I want to change the default trip purpose.**
- Re-run the Setup shortcut and choose a different default when prompted.
