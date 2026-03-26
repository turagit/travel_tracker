import unittest
import plistlib
from src.shortcut_generator.shortcuts import build_setup_shortcut, build_trip_start_shortcut, build_trip_end_shortcut


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
        identifiers = [a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]]
        self.assertIn("is.workflow.actions.documentpicker.save", identifiers)

    def test_contains_menu_actions(self):
        result = build_setup_shortcut()
        identifiers = [a["WFWorkflowActionIdentifier"] for a in result["WFWorkflowActions"]]
        menu_count = identifiers.count("is.workflow.actions.choosefrommenu")
        # 3 menus (odometer, classify, multi-car) x 4 parts each (start, yes, no, end) = 12
        self.assertEqual(menu_count, 12)

    def test_contains_alert_at_end(self):
        result = build_setup_shortcut()
        last_action = result["WFWorkflowActions"][-1]
        self.assertEqual(last_action["WFWorkflowActionIdentifier"], "is.workflow.actions.alert")


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
        text_actions = [a for a in result["WFWorkflowActions"] if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.gettext"]
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
        text_actions = [a for a in result["WFWorkflowActions"] if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.gettext"]
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


if __name__ == "__main__":
    unittest.main()
