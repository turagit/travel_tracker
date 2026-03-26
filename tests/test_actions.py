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
        self.assertEqual(params["WFInput"]["Value"]["OutputUUID"], "LOC-UUID")


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
        templates = params["WFContentItemFilter"]["Value"]["WFActionParameterFilterTemplates"]
        self.assertEqual(templates[0]["Operator"], 4)
        self.assertEqual(templates[0]["OperandString"], "KMS TAX REPORT FOR 2026")


class TestAppendToNote(unittest.TestCase):
    def test_structure(self):
        from src.shortcut_generator.variables import action_output
        note_ref = action_output("NOTES-UUID", "Notes")
        text_ref = action_output("TEXT-UUID", "Text")
        result = append_to_note(note_ref, text_ref)
        self.assertEqual(result["WFWorkflowActionIdentifier"], "is.workflow.actions.appendnote")


class TestControlFlow(unittest.TestCase):
    def test_if_otherwise_endif_share_grouping_id(self):
        gid = "GROUP-1"
        if_act = if_action(gid, condition="Equals", comparison_value="yes")
        ow_act = otherwise_action(gid)
        end_act = end_if_action(gid)
        for act in [if_act, ow_act, end_act]:
            self.assertEqual(act["WFWorkflowActionIdentifier"], "is.workflow.actions.conditional")
            self.assertEqual(act["WFWorkflowActionParameters"]["GroupingIdentifier"], gid)
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
        self.assertEqual(result["WFWorkflowActionIdentifier"], "is.workflow.actions.dictionary")
        items = result["WFWorkflowActionParameters"]["WFItems"]["Value"]["WFDictionaryFieldValueItems"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["WFItemType"], 0)


class TestFileActions(unittest.TestCase):
    def test_save_file(self):
        result = save_file("Shortcuts/travel_tracker_config.json", overwrite=True)
        self.assertEqual(result["WFWorkflowActionIdentifier"], "is.workflow.actions.documentpicker.save")
        params = result["WFWorkflowActionParameters"]
        self.assertTrue(params["WFSaveFileOverwrite"])
        self.assertFalse(params["WFAskWhereToSave"])

    def test_read_file(self):
        result = read_file("Shortcuts/travel_tracker_config.json")
        self.assertEqual(result["WFWorkflowActionIdentifier"], "is.workflow.actions.documentpicker.open")
        params = result["WFWorkflowActionParameters"]
        self.assertFalse(params["WFShowFilePicker"])
        self.assertTrue(params["WFFileErrorIfNotFound"])


if __name__ == "__main__":
    unittest.main()
