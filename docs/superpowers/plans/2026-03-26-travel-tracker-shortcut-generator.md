# Travel Tracker iOS Shortcut Generator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python tool that generates three Apple iOS `.shortcut` files (Setup, Trip Start, Trip End) for automated mileage tracking, satisfying Dutch Belastingdienst "rittenadministratie" requirements for BV/ZZP freelancers.

**Architecture:** A Python package using only stdlib (`plistlib`, `uuid`, `json`) that models Shortcut actions as composable Python objects, then serializes them to binary plist `.shortcut` files. Three shortcuts work together: Setup configures preferences (car selection, odometer, trip classification, multi-car) and saves them to a JSON file in iCloud; Trip Start/End are triggered by Bluetooth connect/disconnect automations and log trips to an Apple Note named "KMS TAX REPORT FOR YYYY".

**Tech Stack:** Python 3.10+ (stdlib only: `plistlib`, `uuid`, `json`, `pathlib`). No external dependencies.

---

## Why This Tool Exists

In the Netherlands, the Belastingdienst requires BV owners and ZZP/freelancers who use a company car to maintain a detailed "rittenadministratie" (mileage log). Each trip must record: date, start time, start location, end time, end location, and optionally odometer readings and trip purpose (business/private). Failure to maintain this log can result in a 22% "bijtelling" addition to taxable income.

This tool automates that logging by generating iOS Shortcuts that:
1. Detect when you enter/leave your car via Bluetooth/CarPlay connection
2. Automatically log the trip start/end city and timestamp to an Apple Note
3. Optionally prompt for odometer readings and trip purpose
4. Organize everything into a yearly note for your accountant

The shortcuts are generated (not hand-built) so they are reproducible, configurable, and version-controlled.

## iOS Shortcut Technical Context

`.shortcut` files are binary plists. Each contains a `WFWorkflowActions` array of action dictionaries. Actions reference each other via UUIDs ("magic variables"). Control flow (if/else, menus) uses `WFControlFlowMode` (0=start, 1=middle, 2=end) with shared `GroupingIdentifier` UUIDs. String interpolation uses the Unicode Object Replacement Character (`\uFFFC`) with positional `attachmentsByRange` maps.

**Key limitation:** Bluetooth device selection cannot be embedded in a `.shortcut` file — it's configured in iOS Automations (Settings > Shortcuts > Automations). The Setup shortcut saves the user's preferences; the user then manually creates two automations (BT connect → Run Trip Start, BT disconnect → Run Trip End). On iOS 17+, these automations can run silently without user confirmation.

## File Structure

```
travel_tracker/
├── src/
│   └── shortcut_generator/
│       ├── __init__.py              # Package init, version
│       ├── actions.py               # Action builder functions (one per Shortcut action type)
│       ├── variables.py             # Variable reference builders (magic vars, string interpolation)
│       ├── shortcuts.py             # High-level shortcut composers (setup, trip_start, trip_end)
│       └── generator.py            # CLI entry point, writes .shortcut files to output/
├── tests/
│   ├── __init__.py
│   ├── test_actions.py              # Unit tests for each action builder
│   ├── test_variables.py            # Unit tests for variable references and interpolation
│   ├── test_shortcuts.py            # Integration tests for complete shortcut generation
│   └── test_generator.py           # CLI/output tests
├── output/                          # Generated .shortcut files go here (gitignored)
├── templates/
│   └── tax_report_template.txt      # Example note format for reference
├── docs/
│   ├── SETUP_GUIDE.md               # End-user instructions
│   └── superpowers/plans/           # This plan
├── generate.py                      # Convenience entry point: python generate.py
└── README.md                        # Project overview
```

---

## Task 1: Variable Reference Builders

**Files:**
- Create: `src/shortcut_generator/__init__.py`
- Create: `src/shortcut_generator/variables.py`
- Create: `tests/__init__.py`
- Create: `tests/test_variables.py`

This task builds the foundation — the variable reference system that all actions depend on. Every time one action references another's output, it uses these builders.

- [ ] **Step 1: Write failing tests for variable builders**

```python
# tests/__init__.py
# (empty)

# tests/test_variables.py
import unittest
from src.shortcut_generator.variables import (
    named_var,
    action_output,
    interpolated_string,
    plain_text,
)


class TestNamedVar(unittest.TestCase):
    def test_named_var_structure(self):
        result = named_var("MyVariable")
        self.assertEqual(result["WFSerializationType"], "WFTextTokenAttachment")
        self.assertEqual(result["Value"]["Type"], "Variable")
        self.assertEqual(result["Value"]["VariableName"], "MyVariable")


class TestActionOutput(unittest.TestCase):
    def test_action_output_structure(self):
        result = action_output("ABC-123", "Current Location")
        self.assertEqual(result["WFSerializationType"], "WFTextTokenAttachment")
        self.assertEqual(result["Value"]["Type"], "ActionOutput")
        self.assertEqual(result["Value"]["OutputUUID"], "ABC-123")
        self.assertEqual(result["Value"]["OutputName"], "Current Location")

    def test_action_output_with_aggrandizement(self):
        result = action_output("ABC-123", "Current Location", property_name="City")
        aggr = result["Value"]["Aggrandizements"]
        self.assertEqual(len(aggr), 1)
        self.assertEqual(aggr[0]["Type"], "WFPropertyVariableAggrandizement")
        self.assertEqual(aggr[0]["PropertyName"], "City")


class TestInterpolatedString(unittest.TestCase):
    def test_no_variables(self):
        result = interpolated_string("Hello World")
        self.assertEqual(result["WFSerializationType"], "WFTextTokenString")
        self.assertEqual(result["Value"]["string"], "Hello World")
        self.assertEqual(result["Value"]["attachmentsByRange"], {})

    def test_single_variable(self):
        var = {"Type": "Variable", "VariableName": "City"}
        result = interpolated_string("Start: ", (var,), " done")
        self.assertIn("\uFFFC", result["Value"]["string"])
        self.assertEqual(result["Value"]["string"], "Start: \uFFFC done")
        self.assertIn("{7, 1}", result["Value"]["attachmentsByRange"])

    def test_multiple_variables(self):
        var1 = {"Type": "Variable", "VariableName": "City"}
        var2 = {"Type": "ActionOutput", "OutputUUID": "X", "OutputName": "Date"}
        result = interpolated_string("From ", (var1,), " on ", (var2,), ".")
        self.assertEqual(result["Value"]["string"], "From \uFFFC on \uFFFC.")
        self.assertEqual(len(result["Value"]["attachmentsByRange"]), 2)


class TestPlainText(unittest.TestCase):
    def test_plain_text_is_token_string(self):
        result = plain_text("hello")
        self.assertEqual(result["WFSerializationType"], "WFTextTokenString")
        self.assertEqual(result["Value"]["string"], "hello")
        self.assertEqual(result["Value"]["attachmentsByRange"], {})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_variables.py -v`
Expected: ModuleNotFoundError — `src.shortcut_generator.variables` does not exist yet.

- [ ] **Step 3: Implement variables.py**

```python
# src/shortcut_generator/__init__.py
"""iOS Shortcut generator for Dutch tax mileage tracking."""

# src/shortcut_generator/variables.py
"""Builders for Shortcut variable references and string interpolation."""


def named_var(name: str) -> dict:
    """Reference a named variable (set via Set Variable action)."""
    return {
        "Value": {"Type": "Variable", "VariableName": name},
        "WFSerializationType": "WFTextTokenAttachment",
    }


def action_output(uuid: str, output_name: str, property_name: str | None = None) -> dict:
    """Reference a previous action's output (magic variable).

    Args:
        uuid: The UUID of the source action.
        output_name: The output name of the source action.
        property_name: Optional property to extract (e.g. "City" from a location).
    """
    value = {
        "Type": "ActionOutput",
        "OutputUUID": uuid,
        "OutputName": output_name,
    }
    if property_name:
        value["Aggrandizements"] = [
            {
                "Type": "WFPropertyVariableAggrandizement",
                "PropertyName": property_name,
            }
        ]
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def plain_text(text: str) -> dict:
    """A WFTextTokenString with no variable references."""
    return {
        "Value": {"string": text, "attachmentsByRange": {}},
        "WFSerializationType": "WFTextTokenString",
    }


def interpolated_string(*parts) -> dict:
    """Build a WFTextTokenString with embedded variable references.

    Args:
        *parts: Mix of plain strings and single-element tuples containing
                a variable dict (the inner Value dict, not the wrapper).
                Example: interpolated_string("City: ", (var_dict,), " end")
    """
    string = ""
    attachments = {}
    for part in parts:
        if isinstance(part, tuple):
            var_dict = part[0]
            pos = len(string)
            string += "\uFFFC"
            attachments[f"{{{pos}, 1}}"] = var_dict
        else:
            string += part
    return {
        "Value": {"string": string, "attachmentsByRange": attachments},
        "WFSerializationType": "WFTextTokenString",
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_variables.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shortcut_generator/__init__.py src/shortcut_generator/variables.py tests/__init__.py tests/test_variables.py
git commit -m "feat: add variable reference builders for shortcut generation"
```

---

## Task 2: Action Builder Functions

**Files:**
- Create: `src/shortcut_generator/actions.py`
- Create: `tests/test_actions.py`

Each function returns a well-formed action dict (`WFWorkflowActionIdentifier` + `WFWorkflowActionParameters`). These are the atoms that shortcuts are composed from.

- [ ] **Step 1: Write failing tests for action builders**

```python
# tests/test_actions.py
import unittest
from src.shortcut_generator.actions import (
    text_action,
    ask_for_input,
    show_alert,
    current_date,
    format_date,
    set_variable,
    get_variable,
    get_current_location,
    get_location_detail,
    find_notes,
    append_to_note,
    create_note,
    save_file,
    read_file,
    append_to_file,
    if_action,
    otherwise_action,
    end_if_action,
    menu_start,
    menu_item,
    menu_end,
    choose_from_list,
    dictionary_action,
    get_dictionary_value,
    get_text_from_input,
)


class TestTextAction(unittest.TestCase):
    def test_plain_string(self):
        result = text_action("hello")
        self.assertEqual(result["WFWorkflowActionIdentifier"], "is.workflow.actions.gettext")
        self.assertEqual(
            result["WFWorkflowActionParameters"]["WFTextActionText"]["Value"]["string"],
            "hello",
        )

    def test_with_uuid(self):
        result = text_action("hello", uuid="MY-UUID")
        self.assertEqual(result["WFWorkflowActionParameters"]["UUID"], "MY-UUID")


class TestAskForInput(unittest.TestCase):
    def test_basic(self):
        result = ask_for_input("Enter KM:", input_type="Number")
        self.assertEqual(result["WFWorkflowActionIdentifier"], "is.workflow.actions.ask")
        params = result["WFWorkflowActionParameters"]
        self.assertEqual(params["WFAskActionPrompt"], "Enter KM:")
        self.assertEqual(params["WFInputType"], "Number")


class TestGetCurrentLocation(unittest.TestCase):
    def test_structure(self):
        result = get_current_location(uuid="LOC-UUID")
        self.assertEqual(
            result["WFWorkflowActionIdentifier"],
            "is.workflow.actions.getcurrentlocation",
        )
        self.assertEqual(result["WFWorkflowActionParameters"]["UUID"], "LOC-UUID")


class TestGetLocationDetail(unittest.TestCase):
    def test_city(self):
        result = get_location_detail("LOC-UUID", "Current Location", "City")
        self.assertEqual(
            result["WFWorkflowActionIdentifier"],
            "is.workflow.actions.properties.locations",
        )
        params = result["WFWorkflowActionParameters"]
        self.assertEqual(params["WFContentItemPropertyName"], "City")
        self.assertEqual(
            params["WFInput"]["Value"]["OutputUUID"], "LOC-UUID"
        )


class TestFindNotes(unittest.TestCase):
    def test_find_by_name(self):
        result = find_notes("KMS TAX REPORT FOR 2026", uuid="NOTES-UUID")
        self.assertEqual(
            result["WFWorkflowActionIdentifier"],
            "is.workflow.actions.filter.notes",
        )
        params = result["WFWorkflowActionParameters"]
        self.assertTrue(params["WFContentItemLimitEnabled"])
        self.assertEqual(params["WFContentItemLimit"], 1)
        templates = params["WFContentItemFilter"]["Value"][
            "WFActionParameterFilterTemplates"
        ]
        self.assertEqual(templates[0]["Operator"], 4)
        self.assertEqual(templates[0]["OperandString"], "KMS TAX REPORT FOR 2026")


class TestAppendToNote(unittest.TestCase):
    def test_structure(self):
        from src.shortcut_generator.variables import action_output

        note_ref = action_output("NOTES-UUID", "Notes")
        text_ref = action_output("TEXT-UUID", "Text")
        result = append_to_note(note_ref, text_ref)
        self.assertEqual(
            result["WFWorkflowActionIdentifier"], "is.workflow.actions.appendnote"
        )


class TestControlFlow(unittest.TestCase):
    def test_if_otherwise_endif_share_grouping_id(self):
        gid = "GROUP-1"
        if_act = if_action(gid, condition="Equals", comparison_value="yes")
        ow_act = otherwise_action(gid)
        end_act = end_if_action(gid)
        for act in [if_act, ow_act, end_act]:
            self.assertEqual(
                act["WFWorkflowActionIdentifier"], "is.workflow.actions.conditional"
            )
            self.assertEqual(
                act["WFWorkflowActionParameters"]["GroupingIdentifier"], gid
            )
        self.assertEqual(if_act["WFWorkflowActionParameters"]["WFControlFlowMode"], 0)
        self.assertEqual(ow_act["WFWorkflowActionParameters"]["WFControlFlowMode"], 1)
        self.assertEqual(end_act["WFWorkflowActionParameters"]["WFControlFlowMode"], 2)


class TestMenu(unittest.TestCase):
    def test_menu_structure(self):
        gid = "MENU-1"
        start = menu_start(gid, "Pick one:", ["A", "B"])
        item_a = menu_item(gid, "A")
        item_b = menu_item(gid, "B")
        end = menu_end(gid)
        self.assertEqual(start["WFWorkflowActionParameters"]["WFControlFlowMode"], 0)
        self.assertEqual(item_a["WFWorkflowActionParameters"]["WFControlFlowMode"], 1)
        self.assertEqual(end["WFWorkflowActionParameters"]["WFControlFlowMode"], 2)
        self.assertEqual(start["WFWorkflowActionParameters"]["WFMenuItems"], ["A", "B"])


class TestDictionary(unittest.TestCase):
    def test_text_items(self):
        result = dictionary_action({"car": "Tesla", "track_odometer": "true"})
        self.assertEqual(
            result["WFWorkflowActionIdentifier"], "is.workflow.actions.dictionary"
        )
        items = result["WFWorkflowActionParameters"]["WFItems"]["Value"][
            "WFDictionaryFieldValueItems"
        ]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["WFItemType"], 0)


class TestFileActions(unittest.TestCase):
    def test_save_file(self):
        result = save_file("Shortcuts/travel_tracker_config.json", overwrite=True)
        self.assertEqual(
            result["WFWorkflowActionIdentifier"],
            "is.workflow.actions.documentpicker.save",
        )
        params = result["WFWorkflowActionParameters"]
        self.assertTrue(params["WFSaveFileOverwrite"])
        self.assertFalse(params["WFAskWhereToSave"])

    def test_read_file(self):
        result = read_file("Shortcuts/travel_tracker_config.json")
        self.assertEqual(
            result["WFWorkflowActionIdentifier"],
            "is.workflow.actions.documentpicker.open",
        )
        params = result["WFWorkflowActionParameters"]
        self.assertFalse(params["WFShowFilePicker"])
        self.assertTrue(params["WFFileErrorIfNotFound"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_actions.py -v`
Expected: ImportError — `src.shortcut_generator.actions` does not exist yet.

- [ ] **Step 3: Implement actions.py**

```python
# src/shortcut_generator/actions.py
"""Builder functions for individual iOS Shortcut actions.

Each function returns a dict with WFWorkflowActionIdentifier and
WFWorkflowActionParameters, ready to be added to WFWorkflowActions.
"""

from src.shortcut_generator.variables import action_output, plain_text


def _action(identifier: str, params: dict) -> dict:
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": params,
    }


def text_action(text, uuid: str | None = None) -> dict:
    """Create a Text action. text can be a plain string or a WFTextTokenString dict."""
    if isinstance(text, str):
        text = plain_text(text)
    params = {"WFTextActionText": text}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.gettext", params)


def ask_for_input(
    prompt: str,
    input_type: str = "Text",
    default_answer: str | None = None,
    uuid: str | None = None,
) -> dict:
    params = {"WFAskActionPrompt": prompt, "WFInputType": input_type}
    if default_answer is not None:
        params["WFAskActionDefaultAnswer"] = default_answer
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.ask", params)


def show_alert(title: str, message: str, show_cancel: bool = False) -> dict:
    return _action(
        "is.workflow.actions.alert",
        {
            "WFAlertActionTitle": title,
            "WFAlertActionMessage": message,
            "WFAlertActionCancelButtonShown": show_cancel,
        },
    )


def current_date(uuid: str | None = None) -> dict:
    params = {"WFDateActionMode": "Current Date"}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.date", params)


def format_date(
    date_ref: dict,
    fmt: str = "yyyy-MM-dd HH:mm",
    uuid: str | None = None,
) -> dict:
    """Format a date with a custom format string.

    Args:
        date_ref: A WFTextTokenAttachment referencing a date action output.
        fmt: A date format string (ICU/Unicode format).
    """
    params = {
        "WFDateFormatStyle": "Custom",
        "WFDateFormat": fmt,
        "WFDate": date_ref,
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.format.date", params)


def set_variable(name: str) -> dict:
    return _action("is.workflow.actions.setvariable", {"WFVariableName": name})


def get_variable(name: str, uuid: str | None = None) -> dict:
    from src.shortcut_generator.variables import named_var

    params = {"WFVariable": named_var(name)}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.getvariable", params)


def get_current_location(uuid: str | None = None) -> dict:
    params = {}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.getcurrentlocation", params)


def get_location_detail(
    location_uuid: str,
    location_output_name: str,
    property_name: str,
    uuid: str | None = None,
) -> dict:
    """Get a detail (City, Street, etc.) from a location action's output."""
    params = {
        "WFInput": action_output(location_uuid, location_output_name),
        "WFContentItemPropertyName": property_name,
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.properties.locations", params)


def find_notes(name_contains: str, uuid: str | None = None) -> dict:
    """Find notes whose name matches exactly."""
    params = {
        "WFContentItemSortProperty": "WFItemCreationDate",
        "WFContentItemSortOrder": "Latest First",
        "WFContentItemLimit": 1,
        "WFContentItemLimitEnabled": True,
        "WFContentItemFilter": {
            "Value": {
                "WFActionParameterFilterPrefix": 1,
                "WFActionParameterFilterTemplates": [
                    {
                        "Property": "Name",
                        "Operator": 4,
                        "OperandString": name_contains,
                        "Removable": True,
                        "BoundedDate": False,
                    }
                ],
            },
            "WFSerializationType": "WFContentPredicateTableTemplate",
        },
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.filter.notes", params)


def create_note(uuid: str | None = None) -> dict:
    """Create a note from the pipeline input (the previous action's output)."""
    params = {
        "ShowWhenRun": False,
    }
    if uuid:
        params["UUID"] = uuid
    return _action("com.apple.mobilenotes.SharingExtension", params)


def append_to_note(note_ref: dict, text_ref: dict) -> dict:
    """Append text to an existing note.

    Args:
        note_ref: WFTextTokenAttachment pointing to the note (from find_notes).
        text_ref: WFTextTokenAttachment pointing to the text to append.
    """
    return _action(
        "is.workflow.actions.appendnote",
        {"WFNote": note_ref, "WFInput": text_ref},
    )


def save_file(path: str, overwrite: bool = True) -> dict:
    return _action(
        "is.workflow.actions.documentpicker.save",
        {
            "WFFileDestinationPath": path,
            "WFSaveFileOverwrite": overwrite,
            "WFAskWhereToSave": False,
        },
    )


def read_file(path: str, uuid: str | None = None) -> dict:
    params = {
        "WFGetFilePath": path,
        "WFFileErrorIfNotFound": True,
        "WFShowFilePicker": False,
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.documentpicker.open", params)


def append_to_file(path: str) -> dict:
    return _action(
        "is.workflow.actions.file.append",
        {"WFFilePath": path, "WFAppendFileWriteMode": "Append"},
    )


def if_action(
    grouping_id: str,
    condition: str = "Equals",
    comparison_value: str | None = None,
    input_ref: dict | None = None,
) -> dict:
    params = {
        "WFControlFlowMode": 0,
        "GroupingIdentifier": grouping_id,
        "WFCondition": condition,
    }
    if comparison_value is not None:
        params["WFConditionalActionString"] = comparison_value
    if input_ref:
        params["WFInput"] = input_ref
    return _action("is.workflow.actions.conditional", params)


def otherwise_action(grouping_id: str) -> dict:
    return _action(
        "is.workflow.actions.conditional",
        {"WFControlFlowMode": 1, "GroupingIdentifier": grouping_id},
    )


def end_if_action(grouping_id: str) -> dict:
    return _action(
        "is.workflow.actions.conditional",
        {"WFControlFlowMode": 2, "GroupingIdentifier": grouping_id},
    )


def menu_start(grouping_id: str, prompt: str, items: list[str]) -> dict:
    return _action(
        "is.workflow.actions.choosefrommenu",
        {
            "WFMenuPrompt": prompt,
            "WFControlFlowMode": 0,
            "GroupingIdentifier": grouping_id,
            "WFMenuItems": items,
        },
    )


def menu_item(grouping_id: str, title: str) -> dict:
    return _action(
        "is.workflow.actions.choosefrommenu",
        {
            "WFMenuItemTitle": title,
            "WFControlFlowMode": 1,
            "GroupingIdentifier": grouping_id,
        },
    )


def menu_end(grouping_id: str) -> dict:
    return _action(
        "is.workflow.actions.choosefrommenu",
        {"WFControlFlowMode": 2, "GroupingIdentifier": grouping_id},
    )


def choose_from_list(prompt: str | None = None, uuid: str | None = None) -> dict:
    params = {"WFChooseFromListActionSelectMultiple": False}
    if prompt:
        params["WFChooseFromListActionPrompt"] = prompt
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.choosefromlist", params)


def dictionary_action(items: dict[str, str], uuid: str | None = None) -> dict:
    """Create a Dictionary action from a simple key→value string mapping."""
    field_items = []
    for key, value in items.items():
        field_items.append(
            {
                "WFItemType": 0,
                "WFKey": {
                    "Value": {"string": key, "attachmentsByRange": {}},
                    "WFSerializationType": "WFTextTokenString",
                },
                "WFValue": {
                    "Value": {"string": value, "attachmentsByRange": {}},
                    "WFSerializationType": "WFTextTokenString",
                },
            }
        )
    params = {
        "WFItems": {
            "Value": {"WFDictionaryFieldValueItems": field_items},
            "WFSerializationType": "WFDictionaryFieldValue",
        }
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.dictionary", params)


def get_dictionary_value(key: str, uuid: str | None = None) -> dict:
    params = {"WFDictionaryKey": key, "WFGetDictionaryValueType": "Value"}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.getvalueforkey", params)


def get_text_from_input(uuid: str | None = None) -> dict:
    """Get Text from Input — converts pipeline input to text."""
    params = {}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.detect.text", params)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_actions.py -v`
Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shortcut_generator/actions.py tests/test_actions.py
git commit -m "feat: add action builder functions for all shortcut action types"
```

---

## Task 3: Shortcut Composers — Setup Shortcut

**Files:**
- Create: `src/shortcut_generator/shortcuts.py`
- Create: `tests/test_shortcuts.py`

The Setup shortcut asks the user to configure their preferences and saves them to a JSON config file in iCloud Drive.

**What the Setup Shortcut does (user flow):**
1. Asks: "Do you want to track odometer readings?" (Yes/No menu)
2. Asks: "Do you want to classify trips as business/private?" (Yes/No menu)
3. Asks: "Do you want to track multiple cars?" (Yes/No menu)
4. Builds a config dictionary with these preferences
5. Saves to `Shortcuts/travel_tracker_config.json`
6. Shows a confirmation alert with instructions to set up Bluetooth automations

- [ ] **Step 1: Write failing tests for setup shortcut**

```python
# tests/test_shortcuts.py
import unittest
import plistlib
from src.shortcut_generator.shortcuts import build_setup_shortcut


class TestSetupShortcut(unittest.TestCase):
    def test_returns_valid_plist_dict(self):
        result = build_setup_shortcut()
        self.assertIn("WFWorkflowActions", result)
        self.assertIn("WFWorkflowClientVersion", result)
        self.assertIn("WFWorkflowIcon", result)
        self.assertIsInstance(result["WFWorkflowActions"], list)
        self.assertGreater(len(result["WFWorkflowActions"]), 0)

    def test_serializes_to_binary_plist(self):
        result = build_setup_shortcut()
        data = plistlib.dumps(result, fmt=plistlib.FMT_BINARY)
        self.assertIsInstance(data, bytes)
        self.assertGreater(len(data), 0)
        roundtrip = plistlib.loads(data)
        self.assertEqual(roundtrip["WFWorkflowActions"], result["WFWorkflowActions"])

    def test_contains_save_file_action(self):
        result = build_setup_shortcut()
        identifiers = [
            a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]
        ]
        self.assertIn("is.workflow.actions.documentpicker.save", identifiers)

    def test_contains_menu_actions(self):
        result = build_setup_shortcut()
        identifiers = [
            a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]
        ]
        menu_count = identifiers.count("is.workflow.actions.choosefrommenu")
        # 3 menus (odometer, classify, multi-car) × 4 parts each (start, yes, no, end) = 12
        self.assertEqual(menu_count, 12)

    def test_contains_alert_at_end(self):
        result = build_setup_shortcut()
        last_action = result["WFWorkflowActions"][-1]
        self.assertEqual(
            last_action["WFWorkflowActionIdentifier"], "is.workflow.actions.alert"
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_shortcuts.py -v`
Expected: ImportError — `build_setup_shortcut` does not exist.

- [ ] **Step 3: Implement build_setup_shortcut**

```python
# src/shortcut_generator/shortcuts.py
"""High-level shortcut composers that assemble actions into complete shortcuts."""

import uuid as _uuid

from src.shortcut_generator.actions import (
    text_action,
    show_alert,
    set_variable,
    get_variable,
    menu_start,
    menu_item,
    menu_end,
    dictionary_action,
    save_file,
    read_file,
    get_dictionary_value,
    get_current_location,
    get_location_detail,
    find_notes,
    create_note,
    append_to_note,
    current_date,
    format_date,
    ask_for_input,
    if_action,
    otherwise_action,
    end_if_action,
    get_text_from_input,
)
from src.shortcut_generator.variables import action_output, interpolated_string


def _uuid() -> str:
    return str(__import__("uuid").uuid4()).upper()


CONFIG_PATH = "Shortcuts/travel_tracker_config.json"

# Shared shortcut wrapper
ICON_COLOR_BLUE = 463140863
ICON_GLYPH_CAR = 59820


def _wrap_shortcut(actions: list[dict], icon_glyph: int = ICON_GLYPH_CAR) -> dict:
    """Wrap a list of actions into a complete shortcut plist dict."""
    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2302.0.4",
        "WFWorkflowClientRelease": "2302.0.4",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": ICON_COLOR_BLUE,
            "WFWorkflowIconGlyphNumber": icon_glyph,
            "WFWorkflowIconImageData": b"",
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowTypes": ["NCWidget", "WatchKit"],
        "WFWorkflowInputContentItemClasses": [
            "WFStringContentItem",
            "WFGenericFileContentItem",
        ],
    }


def _yes_no_menu(prompt: str, var_name: str) -> list[dict]:
    """Build a Yes/No menu that sets a variable to 'true' or 'false'."""
    gid = _uuid()
    return [
        menu_start(gid, prompt, ["Yes", "No"]),
        menu_item(gid, "Yes"),
        text_action("true"),
        set_variable(var_name),
        menu_item(gid, "No"),
        text_action("false"),
        set_variable(var_name),
        menu_end(gid),
    ]


def build_setup_shortcut() -> dict:
    """Build the Setup shortcut that configures tracking preferences.

    User flow:
    1. Yes/No: Track odometer readings?
    2. Yes/No: Classify trips (business/private)?
    3. Yes/No: Track multiple cars?
    4. Save config to iCloud JSON file
    5. Show confirmation with next-steps instructions
    """
    actions = []

    # Three preference menus
    actions.extend(
        _yes_no_menu(
            "Do you want to log odometer readings for each trip?", "track_odometer"
        )
    )
    actions.extend(
        _yes_no_menu(
            "Do you want to classify each trip as business or private?",
            "classify_trips",
        )
    )
    actions.extend(
        _yes_no_menu(
            "Do you want to track multiple work cars?", "multi_car"
        )
    )

    # Build config dictionary from variables
    odometer_var = {"Type": "Variable", "VariableName": "track_odometer"}
    classify_var = {"Type": "Variable", "VariableName": "classify_trips"}
    multi_car_var = {"Type": "Variable", "VariableName": "multi_car"}

    config_text_uuid = _uuid()
    actions.append(
        text_action(
            interpolated_string(
                '{"track_odometer": "',
                (odometer_var,),
                '", "classify_trips": "',
                (classify_var,),
                '", "multi_car": "',
                (multi_car_var,),
                '"}',
            ),
            uuid=config_text_uuid,
        )
    )

    # Save config file
    actions.append(save_file(CONFIG_PATH, overwrite=True))

    # Confirmation alert
    actions.append(
        show_alert(
            "Setup Complete!",
            "Travel Tracker is configured.\n\n"
            "Next steps:\n"
            "1. Open Settings > Shortcuts > Automations\n"
            "2. Tap + > Create Personal Automation\n"
            "3. Select 'Bluetooth' trigger\n"
            "4. Choose your work car's Bluetooth device\n"
            "5. Set 'When I Connect' → Run 'Trip Start' shortcut\n"
            "6. Create another automation:\n"
            "   'When I Disconnect' → Run 'Trip End' shortcut\n"
            "7. For both: enable 'Run Immediately' (iOS 17+)\n\n"
            "That's it! Trips will be logged automatically.",
        )
    )

    return _wrap_shortcut(actions)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_shortcuts.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shortcut_generator/shortcuts.py tests/test_shortcuts.py
git commit -m "feat: add setup shortcut composer with preference menus and config save"
```

---

## Task 4: Shortcut Composers — Trip Start & Trip End

**Files:**
- Modify: `src/shortcut_generator/shortcuts.py`
- Modify: `tests/test_shortcuts.py`

**What Trip Start does (triggered by Bluetooth connect):**
1. Read config from iCloud JSON file
2. Get current date, format it
3. Get current location → extract city name
4. If config says track_odometer=true → ask for odometer reading
5. If config says classify_trips=true → ask business/private
6. Build the log line: `"[2026-03-26 08:30] START | City: Amsterdam | KM: 12345 | Business"`
7. Find the note "KMS TAX REPORT FOR YYYY" (current year)
8. If note doesn't exist → create it with a header
9. Append the log line to the note

**What Trip End does (triggered by Bluetooth disconnect):**
Same as Trip Start but logs `"END"` instead of `"START"` and the prompt text says "ending" odometer.

- [ ] **Step 1: Write failing tests for trip shortcuts**

Add to `tests/test_shortcuts.py`:

```python
# Add these imports at the top:
from src.shortcut_generator.shortcuts import build_trip_start_shortcut, build_trip_end_shortcut


class TestTripStartShortcut(unittest.TestCase):
    def test_returns_valid_plist_dict(self):
        result = build_trip_start_shortcut()
        self.assertIn("WFWorkflowActions", result)
        self.assertIsInstance(result["WFWorkflowActions"], list)
        self.assertGreater(len(result["WFWorkflowActions"]), 0)

    def test_serializes_to_binary_plist(self):
        result = build_trip_start_shortcut()
        data = plistlib.dumps(result, fmt=plistlib.FMT_BINARY)
        roundtrip = plistlib.loads(data)
        self.assertEqual(len(roundtrip["WFWorkflowActions"]), len(result["WFWorkflowActions"]))

    def test_reads_config_file(self):
        result = build_trip_start_shortcut()
        identifiers = [a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]]
        self.assertIn("is.workflow.actions.documentpicker.open", identifiers)

    def test_gets_location(self):
        result = build_trip_start_shortcut()
        identifiers = [a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]]
        self.assertIn("is.workflow.actions.getcurrentlocation", identifiers)
        self.assertIn("is.workflow.actions.properties.locations", identifiers)

    def test_finds_or_creates_note(self):
        result = build_trip_start_shortcut()
        identifiers = [a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]]
        self.assertIn("is.workflow.actions.filter.notes", identifiers)

    def test_contains_start_label_in_text(self):
        result = build_trip_start_shortcut()
        text_actions = [
            a for a in result["WFWorkflowActions"]
            if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.gettext"
        ]
        found_start = False
        for ta in text_actions:
            text_param = ta["WFWorkflowActionParameters"].get("WFTextActionText", {})
            if isinstance(text_param, dict):
                s = text_param.get("Value", {}).get("string", "")
            else:
                s = str(text_param)
            if "DEPARTURE" in s:
                found_start = True
        self.assertTrue(found_start, "Expected a text action containing 'DEPARTURE'")


class TestTripEndShortcut(unittest.TestCase):
    def test_returns_valid_plist_dict(self):
        result = build_trip_end_shortcut()
        self.assertIn("WFWorkflowActions", result)

    def test_serializes_to_binary_plist(self):
        result = build_trip_end_shortcut()
        data = plistlib.dumps(result, fmt=plistlib.FMT_BINARY)
        self.assertIsInstance(data, bytes)

    def test_contains_arrival_label(self):
        result = build_trip_end_shortcut()
        text_actions = [
            a for a in result["WFWorkflowActions"]
            if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.gettext"
        ]
        found_end = False
        for ta in text_actions:
            text_param = ta["WFWorkflowActionParameters"].get("WFTextActionText", {})
            if isinstance(text_param, dict):
                s = text_param.get("Value", {}).get("string", "")
            else:
                s = str(text_param)
            if "ARRIVAL" in s:
                found_end = True
        self.assertTrue(found_end, "Expected a text action containing 'ARRIVAL'")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_shortcuts.py -v`
Expected: ImportError for `build_trip_start_shortcut` and `build_trip_end_shortcut`.

- [ ] **Step 3: Implement trip shortcut builders**

Add to `src/shortcut_generator/shortcuts.py`:

```python
def _build_trip_shortcut(label: str, odometer_prompt: str) -> dict:
    """Shared builder for Trip Start and Trip End shortcuts.

    Args:
        label: "DEPARTURE" or "ARRIVAL"
        odometer_prompt: Prompt text for odometer reading if enabled.
    """
    actions = []

    # --- Step 1: Read config ---
    config_file_uuid = _uuid()
    actions.append(read_file(CONFIG_PATH, uuid=config_file_uuid))

    # Parse JSON config into dictionary
    config_dict_uuid = _uuid()
    actions.append(
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.detect.dictionary",
            "WFWorkflowActionParameters": {
                "WFInput": action_output(config_file_uuid, "File"),
                "UUID": config_dict_uuid,
            },
        }
    )
    actions.append(set_variable("config"))

    # Extract config values
    actions.append(get_variable("config"))
    track_odometer_uuid = _uuid()
    actions.append(get_dictionary_value("track_odometer", uuid=track_odometer_uuid))
    actions.append(set_variable("track_odometer"))

    actions.append(get_variable("config"))
    classify_trips_uuid = _uuid()
    actions.append(get_dictionary_value("classify_trips", uuid=classify_trips_uuid))
    actions.append(set_variable("classify_trips"))

    # --- Step 2: Get current date and format it ---
    date_uuid = _uuid()
    actions.append(current_date(uuid=date_uuid))
    date_ref = action_output(date_uuid, "Date")

    formatted_date_uuid = _uuid()
    actions.append(format_date(date_ref, fmt="yyyy-MM-dd HH:mm", uuid=formatted_date_uuid))
    actions.append(set_variable("formatted_date"))

    # Also get just the year for the note title
    year_uuid = _uuid()
    actions.append(format_date(date_ref, fmt="yyyy", uuid=year_uuid))
    actions.append(set_variable("current_year"))

    # --- Step 3: Get current location → city ---
    loc_uuid = _uuid()
    actions.append(get_current_location(uuid=loc_uuid))

    city_uuid = _uuid()
    actions.append(
        get_location_detail(loc_uuid, "Current Location", "City", uuid=city_uuid)
    )
    actions.append(set_variable("city"))

    # --- Step 4: Conditional odometer reading ---
    odometer_if_gid = _uuid()
    actions.append(
        if_action(
            odometer_if_gid,
            condition="Equals",
            comparison_value="true",
            input_ref=action_output(track_odometer_uuid, "Dictionary Value"),
        )
    )
    odometer_uuid = _uuid()
    actions.append(ask_for_input(odometer_prompt, input_type="Number", uuid=odometer_uuid))
    actions.append(set_variable("odometer"))
    actions.append(otherwise_action(odometer_if_gid))
    actions.append(text_action("-"))
    actions.append(set_variable("odometer"))
    actions.append(end_if_action(odometer_if_gid))

    # --- Step 5: Conditional trip classification ---
    classify_if_gid = _uuid()
    actions.append(
        if_action(
            classify_if_gid,
            condition="Equals",
            comparison_value="true",
            input_ref=action_output(classify_trips_uuid, "Dictionary Value"),
        )
    )
    classify_menu_gid = _uuid()
    actions.append(menu_start(classify_menu_gid, "Trip purpose:", ["Business", "Private"]))
    actions.append(menu_item(classify_menu_gid, "Business"))
    actions.append(text_action("Business"))
    actions.append(set_variable("trip_purpose"))
    actions.append(menu_item(classify_menu_gid, "Private"))
    actions.append(text_action("Private"))
    actions.append(set_variable("trip_purpose"))
    actions.append(menu_end(classify_menu_gid))
    actions.append(otherwise_action(classify_if_gid))
    actions.append(text_action("-"))
    actions.append(set_variable("trip_purpose"))
    actions.append(end_if_action(classify_if_gid))

    # --- Step 6: Build log line ---
    date_var = {"Type": "Variable", "VariableName": "formatted_date"}
    city_var = {"Type": "Variable", "VariableName": "city"}
    odometer_var = {"Type": "Variable", "VariableName": "odometer"}
    purpose_var = {"Type": "Variable", "VariableName": "trip_purpose"}

    log_line_uuid = _uuid()
    actions.append(
        text_action(
            interpolated_string(
                f"[",
                (date_var,),
                f"] {label} | City: ",
                (city_var,),
                " | KM: ",
                (odometer_var,),
                " | Purpose: ",
                (purpose_var,),
            ),
            uuid=log_line_uuid,
        )
    )
    actions.append(set_variable("log_line"))

    # --- Step 7: Find or create the yearly note ---
    year_var = {"Type": "Variable", "VariableName": "current_year"}
    note_title_uuid = _uuid()
    actions.append(
        text_action(
            interpolated_string("KMS TAX REPORT FOR ", (year_var,)),
            uuid=note_title_uuid,
        )
    )
    actions.append(set_variable("note_title"))

    find_notes_uuid = _uuid()
    # We need to use the year variable in the find — but find_notes takes a static string.
    # Workaround: use the note_title variable approach. Since the find_notes filter
    # requires a static string and we need a dynamic year, we use a Count approach:
    # find notes containing the title, check if count > 0.
    # Actually, we can use the note_title variable in the filter by embedding it.
    # But the filter OperandString is static in the plist. So instead:
    # We'll find ALL notes, then rely on name. Simpler: create note title with year,
    # search for it. Since the plist is generated at generation time, we use the
    # current year at generation. BUT we want it to work across years.
    #
    # Solution: Use the Get Variable + string interpolation in the Find Notes filter.
    # The filter OperandString CAN be a WFTextTokenString with variable interpolation.
    actions.append(
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.filter.notes",
            "WFWorkflowActionParameters": {
                "WFContentItemSortProperty": "WFItemCreationDate",
                "WFContentItemSortOrder": "Latest First",
                "WFContentItemLimit": 1,
                "WFContentItemLimitEnabled": True,
                "UUID": find_notes_uuid,
                "WFContentItemFilter": {
                    "Value": {
                        "WFActionParameterFilterPrefix": 1,
                        "WFActionParameterFilterTemplates": [
                            {
                                "Property": "Name",
                                "Operator": 99,  # Contains
                                "OperandString": interpolated_string(
                                    "KMS TAX REPORT FOR ", (year_var,)
                                ),
                                "Removable": True,
                                "BoundedDate": False,
                            }
                        ],
                    },
                    "WFSerializationType": "WFContentPredicateTableTemplate",
                },
            },
        }
    )
    actions.append(set_variable("found_note"))

    # Count results — if 0, create the note
    count_uuid = _uuid()
    actions.append(
        {
            "WFWorkflowActionIdentifier": "is.workflow.actions.count",
            "WFWorkflowActionParameters": {
                "Input": action_output(find_notes_uuid, "Notes"),
                "UUID": count_uuid,
            },
        }
    )

    note_if_gid = _uuid()
    actions.append(
        if_action(
            note_if_gid,
            condition="Equals",
            comparison_value="0",
            input_ref=action_output(count_uuid, "Count"),
        )
    )

    # Create the note with header
    header_uuid = _uuid()
    actions.append(
        text_action(
            interpolated_string(
                "KMS TAX REPORT FOR ",
                (year_var,),
                "\n========================================\n"
                "Automated mileage log for Dutch tax compliance\n"
                "Format: [Date Time] TYPE | City | KM | Purpose\n"
                "========================================\n",
            ),
            uuid=header_uuid,
        )
    )
    new_note_uuid = _uuid()
    actions.append(create_note(uuid=new_note_uuid))
    actions.append(set_variable("found_note"))

    actions.append(otherwise_action(note_if_gid))
    # Note already exists, found_note is already set
    actions.append(end_if_action(note_if_gid))

    # --- Step 8: Append log line to note ---
    note_ref = action_output(find_notes_uuid, "Notes")
    log_ref = {
        "Value": {"Type": "Variable", "VariableName": "log_line"},
        "WFSerializationType": "WFTextTokenAttachment",
    }
    # Re-get the variable to put it in pipeline
    actions.append(get_variable("log_line"))
    actions.append(
        append_to_note(
            {"Value": {"Type": "Variable", "VariableName": "found_note"}, "WFSerializationType": "WFTextTokenAttachment"},
            log_ref,
        )
    )

    return _wrap_shortcut(actions)


def build_trip_start_shortcut() -> dict:
    """Build the Trip Start shortcut (triggered on Bluetooth connect)."""
    return _build_trip_shortcut(
        label="DEPARTURE",
        odometer_prompt="Enter current odometer reading (start of trip):",
    )


def build_trip_end_shortcut() -> dict:
    """Build the Trip End shortcut (triggered on Bluetooth disconnect)."""
    return _build_trip_shortcut(
        label="ARRIVAL",
        odometer_prompt="Enter current odometer reading (end of trip):",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_shortcuts.py -v`
Expected: All 11 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/shortcut_generator/shortcuts.py tests/test_shortcuts.py
git commit -m "feat: add trip start/end shortcut composers with config-driven behavior"
```

---

## Task 5: CLI Generator & File Output

**Files:**
- Create: `src/shortcut_generator/generator.py`
- Create: `generate.py`
- Create: `tests/test_generator.py`

- [ ] **Step 1: Write failing tests for generator**

```python
# tests/test_generator.py
import os
import plistlib
import tempfile
import unittest
from src.shortcut_generator.generator import generate_shortcuts


class TestGenerator(unittest.TestCase):
    def test_generates_three_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = generate_shortcuts(output_dir=tmpdir)
            self.assertEqual(len(files), 3)
            for f in files:
                self.assertTrue(os.path.exists(f))
                self.assertTrue(f.endswith(".shortcut"))

    def test_file_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = generate_shortcuts(output_dir=tmpdir)
            basenames = sorted(os.path.basename(f) for f in files)
            self.assertEqual(
                basenames,
                ["Travel Tracker Setup.shortcut", "Trip End.shortcut", "Trip Start.shortcut"],
            )

    def test_files_are_valid_plists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = generate_shortcuts(output_dir=tmpdir)
            for f in files:
                with open(f, "rb") as fh:
                    data = plistlib.load(fh)
                self.assertIn("WFWorkflowActions", data)
                self.assertGreater(len(data["WFWorkflowActions"]), 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_generator.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement generator.py and generate.py**

```python
# src/shortcut_generator/generator.py
"""Generate .shortcut files and write them to disk."""

import os
import plistlib
from src.shortcut_generator.shortcuts import (
    build_setup_shortcut,
    build_trip_start_shortcut,
    build_trip_end_shortcut,
)


def generate_shortcuts(output_dir: str = "output") -> list[str]:
    """Generate all three .shortcut files and write to output_dir.

    Returns list of file paths written.
    """
    os.makedirs(output_dir, exist_ok=True)

    shortcuts = {
        "Travel Tracker Setup": build_setup_shortcut(),
        "Trip Start": build_trip_start_shortcut(),
        "Trip End": build_trip_end_shortcut(),
    }

    written = []
    for name, shortcut_data in shortcuts.items():
        path = os.path.join(output_dir, f"{name}.shortcut")
        with open(path, "wb") as f:
            plistlib.dump(shortcut_data, f, fmt=plistlib.FMT_BINARY)
        written.append(path)

    return written
```

```python
# generate.py
#!/usr/bin/env python3
"""Convenience entry point: python generate.py [output_dir]"""

import sys
from src.shortcut_generator.generator import generate_shortcuts


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    files = generate_shortcuts(output_dir)
    print(f"Generated {len(files)} shortcut files in '{output_dir}/':")
    for f in files:
        print(f"  {f}")
    print()
    print("To install on your iPhone:")
    print("  1. AirDrop the .shortcut files to your phone, OR")
    print("  2. Upload to iCloud Drive and tap to open on your phone")
    print()
    print("Run 'Travel Tracker Setup' first, then set up Bluetooth automations.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/test_generator.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Run all tests**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/ -v`
Expected: All tests PASS (should be ~24 total).

- [ ] **Step 6: Test the CLI entry point**

Run: `cd /Users/tura/git/travel_tracker && python3 generate.py output`
Expected: Prints 3 files generated, files exist in `output/`.

- [ ] **Step 7: Commit**

```bash
git add src/shortcut_generator/generator.py generate.py tests/test_generator.py
git commit -m "feat: add CLI generator that writes .shortcut files to disk"
```

---

## Task 6: Tax Report Template & Documentation

**Files:**
- Create: `templates/tax_report_template.txt`
- Create: `docs/SETUP_GUIDE.md`
- Create: `.gitignore`

- [ ] **Step 1: Create the tax report template**

This shows what the Apple Note will look like after the shortcuts run:

```text
KMS TAX REPORT FOR 2026
========================================
Automated mileage log for Dutch tax compliance
Format: [Date Time] TYPE | City | KM | Purpose
========================================

[2026-01-15 08:30] DEPARTURE | Amsterdam | KM: 45230 | Purpose: Business
[2026-01-15 09:15] ARRIVAL | Rotterdam | KM: 45298 | Purpose: Business
[2026-01-15 17:00] DEPARTURE | Rotterdam | KM: 45298 | Purpose: Business
[2026-01-15 18:10] ARRIVAL | Amsterdam | KM: 45366 | Purpose: Business
[2026-01-16 07:45] DEPARTURE | Amsterdam | KM: 45366 | Purpose: Private
[2026-01-16 08:30] ARRIVAL | Utrecht | KM: 45412 | Purpose: Private
```

- [ ] **Step 2: Create the setup guide**

```markdown
# Travel Tracker — Setup Guide

Automated mileage logging for Dutch tax compliance (rittenadministratie).

## Requirements

- iPhone with iOS 17 or later (for silent Bluetooth automations)
- A car with Bluetooth or CarPlay
- Apple Notes app

## Installation

### Step 1: Generate the shortcuts

On your computer (requires Python 3.10+):

\`\`\`bash
git clone <this-repo>
cd travel_tracker
python3 generate.py
\`\`\`

This creates three files in `output/`:
- **Travel Tracker Setup.shortcut** — one-time configuration
- **Trip Start.shortcut** — logs trip departure
- **Trip End.shortcut** — logs trip arrival

### Step 2: Install on your iPhone

Transfer the `.shortcut` files to your iPhone using one of:
- **AirDrop** (recommended) — select all three files, AirDrop to your phone
- **iCloud Drive** — copy files to iCloud Drive, tap each one on your phone
- **Email** — email the files to yourself, tap each attachment to install

When you open each file, iOS will ask "Add Shortcut?" — tap **Add**.

### Step 3: Run Setup

1. Open the **Shortcuts** app on your iPhone
2. Find and run **Travel Tracker Setup**
3. Answer the three configuration questions:
   - **Track odometer readings?** — Recommended for Belastingdienst compliance
   - **Classify trips?** — Required if you use the car for both business and private
   - **Track multiple cars?** — If you have more than one work vehicle

### Step 4: Set up Bluetooth Automations

This is the key step that makes tracking automatic:

1. Open **Settings** → **Shortcuts** → **Automations**
2. Tap **+** → **Create Personal Automation**
3. Select **Bluetooth**
4. Choose your car's Bluetooth device (or CarPlay)
5. Select **"Is Connected"**
6. Tap **Next**
7. Select **"Run Shortcut"** → choose **"Trip Start"**
8. **Important:** Toggle **"Run Immediately"** ON and **"Notify When Run"** OFF
9. Tap **Done**

Repeat for disconnection:

1. Tap **+** → **Create Personal Automation** → **Bluetooth**
2. Same car device, but select **"Is Disconnected"**
3. Run Shortcut → choose **"Trip End"**
4. Toggle **"Run Immediately"** ON
5. Tap **Done**

### Step 5: Verify it works

1. Turn on your car (or connect to its Bluetooth manually)
2. Check the **Notes** app — you should see a new note titled
   **"KMS TAX REPORT FOR 2026"** with your first entry
3. Turn off the car — a second entry should appear

## How It Works

```
Phone connects to car Bluetooth
        ↓
iOS Automation triggers "Trip Start" shortcut
        ↓
Shortcut reads your config (odometer? classify?)
        ↓
Gets current location → city name via GPS
        ↓
Optionally asks for odometer / trip purpose
        ↓
Appends log line to Apple Note for current year
        ↓
Phone disconnects from Bluetooth
        ↓
iOS Automation triggers "Trip End" shortcut
        ↓
Same process, logs ARRIVAL instead of DEPARTURE
```

## The Log Format

Each entry in the note looks like:

```
[2026-03-26 08:30] DEPARTURE | City: Amsterdam | KM: 45230 | Purpose: Business
[2026-03-26 09:15] ARRIVAL | City: Rotterdam | KM: 45298 | Purpose: Business
```

## For Your Accountant

At the end of the tax year:
1. Open the note **"KMS TAX REPORT FOR YYYY"**
2. Select all text → Share → Email/Export
3. Send to your accountant or import into your bookkeeping software

The structured format makes it easy to parse into spreadsheets.

## Troubleshooting

**Shortcut asks for permission every time:**
Make sure you're on iOS 17+. In the automation settings, ensure "Run Immediately"
is enabled and "Ask Before Running" is disabled.

**Location shows wrong city:**
The shortcut uses iPhone GPS. Make sure Location Services are enabled for the
Shortcuts app (Settings → Privacy → Location Services → Shortcuts → While Using).

**Note not being created:**
Ensure the Shortcuts app has access to Notes
(Settings → Shortcuts → allow Notes access).

**Odometer not being asked:**
Re-run "Travel Tracker Setup" and select "Yes" for odometer tracking.
```

- [ ] **Step 3: Create .gitignore**

```
output/
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 4: Commit**

```bash
git add templates/tax_report_template.txt docs/SETUP_GUIDE.md .gitignore
git commit -m "docs: add tax report template, setup guide, and gitignore"
```

---

## Task 7: README and Final Polish

**Files:**
- Modify: `README.md` (currently just `test2` file at root — we'll replace)
- Remove: `test2`

- [ ] **Step 1: Write README.md**

```markdown
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
```

- [ ] **Step 2: Remove test2 file**

```bash
rm test2
```

- [ ] **Step 3: Run all tests one final time**

Run: `cd /Users/tura/git/travel_tracker && python3 -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Generate the shortcuts and verify output**

Run: `cd /Users/tura/git/travel_tracker && python3 generate.py`
Expected: Three `.shortcut` files in `output/`, console output showing success.

- [ ] **Step 5: Commit**

```bash
git add README.md .gitignore
git rm test2
git commit -m "docs: add README with project overview and quick start"
```
