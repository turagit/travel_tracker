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
