# How to Create the Travel Tracker Shortcuts

This guide walks you through creating three shortcuts in the iOS/macOS Shortcuts app. It takes about 10 minutes. Once created, you can share them via iCloud links for others to install.

---

## Shortcut 1: Travel Tracker Setup

This shortcut runs once to configure your preferences.

### Create the shortcut

1. Open **Shortcuts** app
2. Tap **+** to create a new shortcut
3. Name it **"Travel Tracker Setup"**

### Add the actions (in order)

**Action 1-8: Odometer preference menu**

1. Add **"Choose from Menu"** action
   - Prompt: `Track odometer readings?`
   - Two items: `Yes` and `No`
2. Under the **Yes** branch:
   - Add **"Text"** action → type `true`
   - Add **"Set Variable"** action → name it `track_odometer`
3. Under the **No** branch:
   - Add **"Text"** action → type `false`
   - Add **"Set Variable"** action → name it `track_odometer`

**Action 9-16: Trip classification menu**

4. Add **"Choose from Menu"** action
   - Prompt: `Classify trips as business/private?`
   - Two items: `Yes` and `No`
5. Under **Yes**: Add **"Text"** → `true`, then **"Set Variable"** → `classify_trips`
6. Under **No**: Add **"Text"** → `false`, then **"Set Variable"** → `classify_trips`

**Action 17-24: Multi-car menu**

7. Add **"Choose from Menu"** action
   - Prompt: `Track multiple cars?`
   - Two items: `Yes` and `No`
8. Under **Yes**: Add **"Text"** → `true`, then **"Set Variable"** → `multi_car`
9. Under **No**: Add **"Text"** → `false`, then **"Set Variable"** → `multi_car`

**Action 25: Build config JSON**

10. Add **"Text"** action. Type this exactly, inserting variables where shown:
    ```
    {"track_odometer": "[track_odometer]", "classify_trips": "[classify_trips]", "multi_car": "[multi_car]"}
    ```
    To insert a variable: tap the text field, tap where you want the variable, then tap the variable button (magic wand icon) and select the variable name.

    - Replace `[track_odometer]` with the `track_odometer` variable
    - Replace `[classify_trips]` with the `classify_trips` variable
    - Replace `[multi_car]` with the `multi_car` variable

**Action 26: Save config file**

11. Add **"Save File"** action
    - Set path to: `Shortcuts/travel_tracker_config.json`
    - Enable **"Overwrite If File Exists"**
    - Disable **"Ask Where to Save"**

**Action 27: Confirmation**

12. Add **"Show Alert"** action
    - Title: `Setup Complete`
    - Message:
      ```
      Travel Tracker is configured.

      Next steps:
      1. Open Settings > Shortcuts > Automations
      2. Create a Bluetooth automation for "connects" → Run "Trip Start"
      3. Create a Bluetooth automation for "disconnects" → Run "Trip End"
      4. Enable "Run Immediately" on both (iOS 17+)
      ```

### Done! Tap the shortcut name at the top and choose an icon (car icon recommended, blue color).

---

## Shortcut 2: Trip Start

This shortcut logs a departure. It runs automatically when your phone connects to the car's Bluetooth.

### Create the shortcut

1. Open **Shortcuts** app
2. Tap **+** to create a new shortcut
3. Name it **"Trip Start"**

### Add the actions (in order)

**Step 1: Read config**

1. Add **"Get File"** action (search for "Get File from Folder")
   - Path: `Shortcuts/travel_tracker_config.json`
   - Disable "Show Document Picker"
   - Enable "Error If Not Found"

2. Add **"Get Dictionary from Input"** action
   (This parses the JSON file into a dictionary)

3. Add **"Set Variable"** → name it `config`

**Step 2: Extract preferences**

4. Add **"Get Variable"** → select `config`
5. Add **"Get Dictionary Value"** → Key: `track_odometer`
6. Add **"Set Variable"** → name it `track_odometer`

7. Add **"Get Variable"** → select `config`
8. Add **"Get Dictionary Value"** → Key: `classify_trips`
9. Add **"Set Variable"** → name it `classify_trips`

**Step 3: Get date and time**

10. Add **"Current Date"** action
11. Add **"Format Date"** action
    - Format: **Custom**
    - Custom format: `yyyy-MM-dd HH:mm`
12. Add **"Set Variable"** → name it `formatted_date`

13. Add **"Current Date"** action (add another one)
14. Add **"Format Date"** action
    - Format: **Custom**
    - Custom format: `yyyy`
15. Add **"Set Variable"** → name it `current_year`

**Step 4: Get location**

16. Add **"Get Current Location"** action
17. Add **"Get Details of Location"** action
    - Get: **City**
18. Add **"Set Variable"** → name it `city`

**Step 5: Conditional odometer**

19. Add **"Get Variable"** → select `track_odometer`
20. Add **"If"** action
    - Condition: **is** → `true`
21. Inside the **If** branch:
    - Add **"Ask for Input"** action
      - Prompt: `Enter current odometer reading (departure):`
      - Input Type: **Number**
    - Add **"Set Variable"** → name it `odometer`
22. Inside the **Otherwise** branch:
    - Add **"Text"** → type `-`
    - Add **"Set Variable"** → name it `odometer`
23. (End If is added automatically)

**Step 6: Conditional trip purpose**

24. Add **"Get Variable"** → select `classify_trips`
25. Add **"If"** action
    - Condition: **is** → `true`
26. Inside the **If** branch:
    - Add **"Choose from Menu"** action
      - Prompt: `Trip purpose?`
      - Items: `Business`, `Private`
    - Under **Business**: Add **"Text"** → `Business`, then **"Set Variable"** → `purpose`
    - Under **Private**: Add **"Text"** → `Private`, then **"Set Variable"** → `purpose`
27. Inside the **Otherwise** branch:
    - Add **"Text"** → `-`
    - Add **"Set Variable"** → `purpose`
28. (End If)

**Step 7: Build log line**

29. Add **"Text"** action with this content (insert variables where shown):
    ```
    [[formatted_date]] DEPARTURE | City: [city] | KM: [odometer] | Purpose: [purpose]
    ```
    Replace each `[variable_name]` by tapping the variable button and selecting the variable.

    The `[` and `]` at the start are literal square brackets — the line should look like:
    `[2026-03-26 08:30] DEPARTURE | City: Amsterdam | KM: 45230 | Purpose: Business`

30. Add **"Set Variable"** → name it `log_line`

**Step 8: Build note title**

31. Add **"Text"** action:
    ```
    KMS TAX REPORT FOR [current_year]
    ```
    (Insert the `current_year` variable)

32. Add **"Set Variable"** → name it `note_title`

**Step 9: Find or create the yearly note**

33. Add **"Find Notes"** action
    - Filter: Name **contains** `KMS TAX REPORT FOR [current_year]`
      (Insert the `current_year` variable in the filter value)
    - Sort by: Creation Date, Latest First
    - Limit: 1

34. Add **"Count"** action (counts the found notes)

35. Add **"If"** action
    - Condition: **is** → `0`

36. Inside the **If** branch (no note found — create one):
    - Add **"Text"** action:
      ```
      KMS TAX REPORT FOR [current_year]
      ====================
      ```
      (Insert `current_year` variable)
    - Add **"Create Note"** action
    - Add **"Set Variable"** → name it `found_note`

37. Inside the **Otherwise** branch (note exists):
    - Add **"Get Variable"** → select the result of "Find Notes" (step 33)
    - Add **"Set Variable"** → name it `found_note`

38. (End If)

**Step 10: Append to note**

39. Add **"Append to Note"** action
    - Note: select the `found_note` variable
    - Text: select the `log_line` variable

### Done! Set the icon to a car with green color.

---

## Shortcut 3: Trip End

This is identical to Trip Start with two differences:
- The label says **ARRIVAL** instead of **DEPARTURE**
- The odometer prompt says **"Enter current odometer reading (arrival):"**

**Easiest method:** Duplicate "Trip Start" in the Shortcuts app (long-press > Duplicate), rename to "Trip End", then:

1. Find the **"Text"** action in Step 7 (the log line) and change `DEPARTURE` to `ARRIVAL`
2. Find the **"Ask for Input"** action in Step 5 and change the prompt to `Enter current odometer reading (arrival):`

---

## Setting Up Bluetooth Automations

After creating all three shortcuts:

### Automation 1: Trip Start (Bluetooth Connect)

1. Open **Shortcuts** > **Automation** tab
2. Tap **+** > **Create Personal Automation**
3. Select **Bluetooth**
4. Choose your car's Bluetooth device
5. Select **"Is Connected"** > Tap **Next**
6. Add action: **"Run Shortcut"** > select **"Trip Start"**
7. Toggle **"Run Immediately"** ON (iOS 17+)
8. Tap **Done**

### Automation 2: Trip End (Bluetooth Disconnect)

1. Tap **+** > **Create Personal Automation** > **Bluetooth**
2. Same car device > select **"Is Disconnected"**
3. **"Run Shortcut"** > select **"Trip End"**
4. Toggle **"Run Immediately"** ON
5. Tap **Done**

---

## Share via iCloud (for other users)

Once you've created and tested the shortcuts:

1. In the Shortcuts app, long-press a shortcut
2. Tap **Share**
3. Tap **Copy iCloud Link**
4. Wait for the link to generate
5. Paste the link — it looks like `https://www.icloud.com/shortcuts/abc123...`

Do this for all three shortcuts and add the links to your repo's README.
