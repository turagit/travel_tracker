"""Composer for the Travel Tracker setup shortcut."""

import uuid

from src.shortcut_generator.variables import named_var, interpolated_string
from src.shortcut_generator.actions import (
    menu_start,
    menu_item,
    menu_end,
    text_action,
    set_variable,
    save_file,
    show_alert,
)

CONFIG_PATH = "Shortcuts/travel_tracker_config.json"


def _uuid() -> str:
    return str(uuid.uuid4()).upper()


def _yes_no_menu(prompt: str, var_name: str) -> list:
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
    """Build the setup shortcut plist dict for Travel Tracker configuration."""
    actions = []

    # Step 1: Yes/No menu for odometer tracking
    actions.extend(_yes_no_menu("Track odometer readings?", "track_odometer"))

    # Step 2: Yes/No menu for trip classification
    actions.extend(_yes_no_menu("Classify trips as business/private?", "classify_trips"))

    # Step 3: Yes/No menu for multiple cars
    actions.extend(_yes_no_menu("Track multiple cars?", "multi_car"))

    # Step 4: Build JSON config string from variables
    config_text = interpolated_string(
        '{"track_odometer": "',
        (named_var("track_odometer"),),
        '", "classify_trips": "',
        (named_var("classify_trips"),),
        '", "multi_car": "',
        (named_var("multi_car"),),
        '"}',
    )
    actions.append(text_action(config_text))

    # Step 5: Save to config file
    actions.append(save_file(CONFIG_PATH, overwrite=True))

    # Step 6: Confirmation alert with Bluetooth automation instructions
    actions.append(show_alert(
        title="Setup Complete",
        message=(
            "Travel Tracker configuration saved to Shortcuts/travel_tracker_config.json.\n\n"
            "To enable automatic trip tracking, set up a Bluetooth automation:\n"
            "1. Open Shortcuts → Automation → New Automation\n"
            "2. Choose 'Bluetooth' trigger (connect/disconnect from your car)\n"
            "3. Run the Travel Tracker Log Trip shortcut automatically."
        ),
        show_cancel=False,
    ))

    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2302.0.4",
        "WFWorkflowClientRelease": "2302.0.4",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 463140863,
            "WFWorkflowIconGlyphNumber": 59820,
            "WFWorkflowIconImageData": b"",
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowTypes": ["NCWidget", "WatchKit"],
        "WFWorkflowInputContentItemClasses": [
            "WFStringContentItem",
            "WFGenericFileContentItem",
        ],
    }
