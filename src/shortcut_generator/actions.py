"""Builder functions for individual iOS Shortcut actions."""

from src.shortcut_generator.variables import action_output, plain_text


def _action(identifier: str, params: dict) -> dict:
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": params,
    }


def text_action(text, uuid: str | None = None) -> dict:
    if isinstance(text, str):
        text = plain_text(text)
    params = {"WFTextActionText": text}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.gettext", params)


def ask_for_input(prompt: str, input_type: str = "Text", default_answer: str | None = None, uuid: str | None = None) -> dict:
    params = {"WFAskActionPrompt": prompt, "WFInputType": input_type}
    if default_answer is not None:
        params["WFAskActionDefaultAnswer"] = default_answer
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.ask", params)


def show_alert(title: str, message: str, show_cancel: bool = False) -> dict:
    return _action("is.workflow.actions.alert", {
        "WFAlertActionTitle": title,
        "WFAlertActionMessage": message,
        "WFAlertActionCancelButtonShown": show_cancel,
    })


def current_date(uuid: str | None = None) -> dict:
    params = {"WFDateActionMode": "Current Date"}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.date", params)


def format_date(date_ref: dict, fmt: str = "yyyy-MM-dd HH:mm", uuid: str | None = None) -> dict:
    params = {"WFDateFormatStyle": "Custom", "WFDateFormat": fmt, "WFDate": date_ref}
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


def get_location_detail(location_uuid: str, location_output_name: str, property_name: str, uuid: str | None = None) -> dict:
    params = {
        "WFInput": action_output(location_uuid, location_output_name),
        "WFContentItemPropertyName": property_name,
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.properties.locations", params)


def find_notes(name_contains: str, uuid: str | None = None) -> dict:
    params = {
        "WFContentItemSortProperty": "WFItemCreationDate",
        "WFContentItemSortOrder": "Latest First",
        "WFContentItemLimit": 1,
        "WFContentItemLimitEnabled": True,
        "WFContentItemFilter": {
            "Value": {
                "WFActionParameterFilterPrefix": 1,
                "WFActionParameterFilterTemplates": [
                    {"Property": "Name", "Operator": 4, "OperandString": name_contains, "Removable": True, "BoundedDate": False}
                ],
            },
            "WFSerializationType": "WFContentPredicateTableTemplate",
        },
    }
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.filter.notes", params)


def create_note(uuid: str | None = None) -> dict:
    params = {"ShowWhenRun": False}
    if uuid:
        params["UUID"] = uuid
    return _action("com.apple.mobilenotes.SharingExtension", params)


def append_to_note(note_ref: dict, text_ref: dict) -> dict:
    return _action("is.workflow.actions.appendnote", {"WFNote": note_ref, "WFInput": text_ref})


def save_file(path: str, overwrite: bool = True) -> dict:
    return _action("is.workflow.actions.documentpicker.save", {
        "WFFileDestinationPath": path, "WFSaveFileOverwrite": overwrite, "WFAskWhereToSave": False,
    })


def read_file(path: str, uuid: str | None = None) -> dict:
    params = {"WFGetFilePath": path, "WFFileErrorIfNotFound": True, "WFShowFilePicker": False}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.documentpicker.open", params)


def append_to_file(path: str) -> dict:
    return _action("is.workflow.actions.file.append", {"WFFilePath": path, "WFAppendFileWriteMode": "Append"})


def if_action(grouping_id: str, condition: str = "Equals", comparison_value: str | None = None, input_ref: dict | None = None) -> dict:
    params = {"WFControlFlowMode": 0, "GroupingIdentifier": grouping_id, "WFCondition": condition}
    if comparison_value is not None:
        params["WFConditionalActionString"] = comparison_value
    if input_ref:
        params["WFInput"] = input_ref
    return _action("is.workflow.actions.conditional", params)


def otherwise_action(grouping_id: str) -> dict:
    return _action("is.workflow.actions.conditional", {"WFControlFlowMode": 1, "GroupingIdentifier": grouping_id})


def end_if_action(grouping_id: str) -> dict:
    return _action("is.workflow.actions.conditional", {"WFControlFlowMode": 2, "GroupingIdentifier": grouping_id})


def menu_start(grouping_id: str, prompt: str, items: list[str]) -> dict:
    return _action("is.workflow.actions.choosefrommenu", {
        "WFMenuPrompt": prompt, "WFControlFlowMode": 0, "GroupingIdentifier": grouping_id, "WFMenuItems": items,
    })


def menu_item(grouping_id: str, title: str) -> dict:
    return _action("is.workflow.actions.choosefrommenu", {
        "WFMenuItemTitle": title, "WFControlFlowMode": 1, "GroupingIdentifier": grouping_id,
    })


def menu_end(grouping_id: str) -> dict:
    return _action("is.workflow.actions.choosefrommenu", {"WFControlFlowMode": 2, "GroupingIdentifier": grouping_id})


def choose_from_list(prompt: str | None = None, uuid: str | None = None) -> dict:
    params = {"WFChooseFromListActionSelectMultiple": False}
    if prompt:
        params["WFChooseFromListActionPrompt"] = prompt
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.choosefromlist", params)


def dictionary_action(items: dict[str, str], uuid: str | None = None) -> dict:
    field_items = []
    for key, value in items.items():
        field_items.append({
            "WFItemType": 0,
            "WFKey": {"Value": {"string": key, "attachmentsByRange": {}}, "WFSerializationType": "WFTextTokenString"},
            "WFValue": {"Value": {"string": value, "attachmentsByRange": {}}, "WFSerializationType": "WFTextTokenString"},
        })
    params = {"WFItems": {"Value": {"WFDictionaryFieldValueItems": field_items}, "WFSerializationType": "WFDictionaryFieldValue"}}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.dictionary", params)


def get_dictionary_value(key: str, uuid: str | None = None) -> dict:
    params = {"WFDictionaryKey": key, "WFGetDictionaryValueType": "Value"}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.getvalueforkey", params)


def get_text_from_input(uuid: str | None = None) -> dict:
    params = {}
    if uuid:
        params["UUID"] = uuid
    return _action("is.workflow.actions.detect.text", params)
