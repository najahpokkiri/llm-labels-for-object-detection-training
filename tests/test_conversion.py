import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from convert_labels import convert


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((Path(__file__).parents[1] / "examples/reviewed-labels.synthetic.json").read_text())

    def test_coordinates_categories_and_empty_image(self):
        result = convert(self.data)
        self.assertEqual(result["annotations"][0]["bbox"], [10, 20, 20, 20])
        self.assertEqual(result["annotations"][0]["area"], 400)
        self.assertEqual(result["annotations"][1]["category_id"], 2)
        self.assertEqual(len(result["images"]), 2)
        self.assertTrue(all(a["image_id"] == 1 for a in result["annotations"]))

    def test_invalid_geometry_and_nonfinite_values(self):
        for box in ([-1, 0, 10, 10], [0, 0, 101, 10], [10, 0, 9, 10],
                    [0, 0, 0, 10], [0, 0, float("nan"), 10], [0, 0, True, 10]):
            with self.subTest(box=box):
                data = copy.deepcopy(self.data)
                data["images"][0]["objects"][0]["bbox_xyxy"] = box
                with self.assertRaises(ValueError):
                    convert(data)

    def test_unfinished_and_uncertain_are_not_background(self):
        data = copy.deepcopy(self.data)
        data["images"][1]["review_complete"] = False
        with self.assertRaises(ValueError):
            convert(data)
        data = copy.deepcopy(self.data)
        data["images"][1]["uncertain_objects"] = [{"description": "unclear cover"}]
        with self.assertRaises(ValueError):
            convert(data)

    def test_duplicate_boxes_files_and_unknown_class(self):
        for mutation in ("box", "file", "class"):
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(self.data)
                if mutation == "box":
                    data["images"][0]["objects"].append(copy.deepcopy(data["images"][0]["objects"][0]))
                elif mutation == "file":
                    data["images"][1]["file_name"] = data["images"][0]["file_name"]
                else:
                    data["images"][0]["objects"][0]["class_name"] = "vehicle"
                with self.assertRaises(ValueError):
                    convert(data)

    def test_cli_exports_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "annotations.json"
            command = [sys.executable, str(ROOT / "convert_labels.py"),
                       str(ROOT / "examples/reviewed-labels.synthetic.json"), str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output.read_bytes()
            exported = json.loads(content)
            self.assertEqual(len(exported["images"]), 2)
            self.assertEqual(len(exported["annotations"]), 2)
            repeated = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(repeated.returncode, 2)
            self.assertEqual(output.read_bytes(), content)

    def test_cli_rejects_incomplete_labels_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "incomplete.json"
            output = Path(directory) / "annotations.json"
            data = copy.deepcopy(self.data)
            data["images"][0]["review_complete"] = False
            source.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(ROOT / "convert_labels.py"),
                                     str(source), str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
