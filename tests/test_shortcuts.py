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


if __name__ == "__main__":
    unittest.main()
