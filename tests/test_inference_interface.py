import base64
import json
from pathlib import Path
import sys
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infer_hosted import decode_response, request_body
from infer_local import serialize
from make_smoke_image import blank_png


class InferenceInterfaceTests(unittest.TestCase):
    def test_transport_preserves_image_and_explicit_model(self):
        image = blank_png()
        body = request_body(image, "workspace/small-model", .3, .3)
        args = body["params"]["arguments"]
        self.assertEqual(base64.b64decode(args["image"]), image)
        self.assertEqual(args["model_id"], "workspace/small-model")
        self.assertEqual(args["confidence"], .3)
        self.assertNotIn("api_key", json.dumps(body))

    def test_json_and_event_stream_preserve_predictions(self):
        prediction = {"predictions": [{"class": "tent", "x": 5, "y": 7}]}
        response = {"jsonrpc": "2.0", "id": 1, "result": {
            "content": [{"type": "text", "text": json.dumps(prediction)}]}}
        raw = json.dumps(response)
        self.assertEqual(decode_response(raw, "application/json"), prediction)
        self.assertEqual(decode_response("event: message\ndata: "+raw+"\n\n", "text/event-stream"), prediction)

    def test_service_error_is_not_a_successful_prediction(self):
        response = {"id": 1, "result": {"isError": True,
            "content": [{"type": "text", "text": "credit_cap_exceeded"}]}}
        with self.assertRaises(ValueError):
            decode_response(json.dumps(response), "application/json")

    def test_invalid_threshold_and_empty_image_fail_before_network(self):
        for data, score in ((b"", .3), (b"test", 1.1)):
            with self.assertRaises(ValueError):
                request_body(data, "workspace/model", score, .3)

    def test_local_serialization_keeps_numeric_class_identity(self):
        detections = types.SimpleNamespace(xyxy=[[1, 2, 10, 12]], class_id=[1], confidence=[.8])
        self.assertEqual(serialize(detections), [{"bbox_xyxy": [1., 2., 10., 12.],
                          "class_id": 1, "confidence": .8}])


if __name__ == "__main__":
    unittest.main()
