"""Composers for the Travel Tracker iOS shortcuts."""

import uuid

from src.shortcut_generator.variables import named_var, action_output, interpolated_string
from src.shortcut_generator.actions import (
    _action,
    menu_start,
    menu_item,
    menu_end,
    text_action,
    set_variable,
    get_variable,
    get_dictionary_value,
    current_date,
    format_date,
    get_current_location,
    get_location_detail,
    ask_for_input,
    if_action,
    otherwise_action,
    end_if_action,
    save_file,
    show_alert,
    read_file,
    create_note,
    append_to_note,
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

    return _wrap_shortcut(actions)


def _wrap_shortcut(actions: list) -> dict:
    """Wrap a list of actions in the standard shortcut plist structure."""
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


def _build_trip_shortcut(label: str, odometer_prompt: str) -> dict:
    """Build a trip logging shortcut (shared logic for start/end).

    Args:
        label: "DEPARTURE" or "ARRIVAL" label for the log line.
        odometer_prompt: Prompt text when asking for odometer reading.
    """
    actions = []

    # Step 1: Read config file
    file_uuid = _uuid()
    actions.append(read_file(CONFIG_PATH, uuid=file_uuid))

    # Step 2: Parse JSON to dictionary
    dict_uuid = _uuid()
    actions.append(_action("is.workflow.actions.detect.dictionary", {
        "WFInput": action_output(file_uuid, "File"),
        "UUID": dict_uuid,
    }))

    # Step 3: Set variable "config", extract track_odometer and classify_trips
    actions.append(set_variable("config"))

    track_odo_uuid = _uuid()
    actions.append(get_variable("config", uuid=track_odo_uuid))
    actions.append(get_dictionary_value("track_odometer"))
    actions.append(set_variable("track_odometer"))

    classify_uuid = _uuid()
    actions.append(get_variable("config", uuid=classify_uuid))
    actions.append(get_dictionary_value("classify_trips"))
    actions.append(set_variable("classify_trips"))

    # Step 4: Get current date, format to "yyyy-MM-dd HH:mm" and "yyyy"
    date_uuid = _uuid()
    actions.append(current_date(uuid=date_uuid))

    formatted_date_uuid = _uuid()
    actions.append(format_date(
        action_output(date_uuid, "Date"),
        fmt="yyyy-MM-dd HH:mm",
        uuid=formatted_date_uuid,
    ))
    actions.append(set_variable("formatted_date"))

    actions.append(get_variable("config"))  # dummy to reset; re-get date
    year_uuid = _uuid()
    actions.append(format_date(
        action_output(date_uuid, "Date"),
        fmt="yyyy",
        uuid=year_uuid,
    ))
    actions.append(set_variable("current_year"))

    # Step 5: Get current location and city
    loc_uuid = _uuid()
    actions.append(get_current_location(uuid=loc_uuid))

    city_uuid = _uuid()
    actions.append(get_location_detail(loc_uuid, "Current Location", "City", uuid=city_uuid))
    actions.append(set_variable("city"))

    # Step 6: If track_odometer == "true": ask for odometer, else set to "-"
    odo_if_id = _uuid()
    odo_input_uuid = _uuid()
    actions.append(get_variable("track_odometer", uuid=odo_input_uuid))
    actions.append(if_action(odo_if_id, condition="Equals", comparison_value="true",
                             input_ref=action_output(odo_input_uuid, "Variable")))
    actions.append(ask_for_input(odometer_prompt, "Number"))
    actions.append(set_variable("odometer"))
    actions.append(otherwise_action(odo_if_id))
    actions.append(text_action("-"))
    actions.append(set_variable("odometer"))
    actions.append(end_if_action(odo_if_id))

    # Step 7: If classify_trips == "true": show Business/Private menu, else set to "-"
    cls_if_id = _uuid()
    cls_input_uuid = _uuid()
    actions.append(get_variable("classify_trips", uuid=cls_input_uuid))
    actions.append(if_action(cls_if_id, condition="Equals", comparison_value="true",
                             input_ref=action_output(cls_input_uuid, "Variable")))
    purpose_menu_id = _uuid()
    actions.append(menu_start(purpose_menu_id, "Trip purpose?", ["Business", "Private"]))
    actions.append(menu_item(purpose_menu_id, "Business"))
    actions.append(text_action("Business"))
    actions.append(set_variable("purpose"))
    actions.append(menu_item(purpose_menu_id, "Private"))
    actions.append(text_action("Private"))
    actions.append(set_variable("purpose"))
    actions.append(menu_end(purpose_menu_id))
    actions.append(otherwise_action(cls_if_id))
    actions.append(text_action("-"))
    actions.append(set_variable("purpose"))
    actions.append(end_if_action(cls_if_id))

    # Step 8: Build log line
    log_line_text = interpolated_string(
        f"[",
        (named_var("formatted_date"),),
        f"] {label} | City: ",
        (named_var("city"),),
        " | KM: ",
        (named_var("odometer"),),
        " | Purpose: ",
        (named_var("purpose"),),
    )
    log_line_uuid = _uuid()
    actions.append(text_action(log_line_text, uuid=log_line_uuid))
    actions.append(set_variable("log_line"))

    # Step 9: Build note title
    year_var = named_var("current_year")
    note_title_text = interpolated_string(
        "KMS TAX REPORT FOR ",
        (year_var,),
    )
    note_title_uuid = _uuid()
    actions.append(text_action(note_title_text, uuid=note_title_uuid))
    actions.append(set_variable("note_title"))

    # Step 10: Find notes using filter with interpolated OperandString
    find_notes_uuid = _uuid()
    actions.append({
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
                    "WFActionParameterFilterTemplates": [{
                        "Property": "Name",
                        "Operator": 99,  # Contains
                        "OperandString": interpolated_string("KMS TAX REPORT FOR ", (year_var,)),
                        "Removable": True,
                        "BoundedDate": False,
                    }],
                },
                "WFSerializationType": "WFContentPredicateTableTemplate",
            },
        },
    })

    # Step 11: Count results; if 0 create note, otherwise use found note
    count_uuid = _uuid()
    actions.append({
        "WFWorkflowActionIdentifier": "is.workflow.actions.count",
        "WFWorkflowActionParameters": {
            "Input": action_output(find_notes_uuid, "Notes"),
            "UUID": count_uuid,
        },
    })

    count_if_id = _uuid()
    actions.append(if_action(count_if_id, condition="Equals", comparison_value="0",
                             input_ref=action_output(count_uuid, "Count")))

    # Create new note with header
    header_text = interpolated_string(
        "KMS TAX REPORT FOR ",
        (year_var,),
        "\n====================\n",
    )
    header_uuid = _uuid()
    actions.append(text_action(header_text, uuid=header_uuid))
    create_note_uuid = _uuid()
    actions.append(create_note(uuid=create_note_uuid))
    actions.append(set_variable("found_note"))

    actions.append(otherwise_action(count_if_id))
    # Use the found note directly — set found_note from find results
    actions.append(get_variable("config"))  # reset pipeline
    found_note_get_uuid = _uuid()
    actions.append(_action("is.workflow.actions.getvariable", {
        "WFVariable": action_output(find_notes_uuid, "Notes"),
        "UUID": found_note_get_uuid,
    }))
    actions.append(set_variable("found_note"))

    actions.append(end_if_action(count_if_id))

    # Step 12: Append log_line to found_note
    actions.append(append_to_note(
        named_var("found_note"),
        named_var("log_line"),
    ))

    return _wrap_shortcut(actions)


def build_trip_start_shortcut() -> dict:
    """Build the Trip Start (departure) shortcut."""
    return _build_trip_shortcut("DEPARTURE", "Enter current odometer reading (departure):")


def build_trip_end_shortcut() -> dict:
    """Build the Trip End (arrival) shortcut."""
    return _build_trip_shortcut("ARRIVAL", "Enter current odometer reading (arrival):")
