"""Builders for Shortcut variable references and string interpolation."""


def named_var(name: str) -> dict:
    """Reference a named variable (set via Set Variable action)."""
    return {
        "Value": {"Type": "Variable", "VariableName": name},
        "WFSerializationType": "WFTextTokenAttachment",
    }


def action_output(uuid: str, output_name: str, property_name: str | None = None) -> dict:
    """Reference a previous action's output (magic variable)."""
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
