"""Run a named Roboflow model through its hosted MCP inference tool.

Requires access to that model and network connectivity. Sends the supplied
image to Roboflow; hosted billing/limits apply. No local weights are used.
"""
import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

DEFAULT_MODEL = "najah-campus-tu-berlin-de/gaza-sudan-joint-final-1-rfdetr-small-t1"


def request_body(image_bytes, model_id, confidence, overlap):
    if not image_bytes:
        raise ValueError("Image is empty")
    if not all(0 <= v <= 1 for v in (confidence, overlap)):
        raise ValueError("Thresholds must be between zero and one")
    if not model_id or len(model_id.split("/")) != 2:
        raise ValueError("Use workspace/model-slug or dataset/version")
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
        "name": "models_infer", "arguments": {
            "model_id": model_id, "image": base64.b64encode(image_bytes).decode("ascii"),
            "confidence": confidence, "overlap": overlap}}}


def decode_response(raw, content_type):
    if "text/event-stream" in content_type:
        messages = [json.loads(line[6:]) for line in raw.splitlines() if line.startswith("data: ")]
        message = next((m for m in reversed(messages) if m.get("id") == 1), None)
        if message is None:
            raise ValueError("No final MCP result")
    else:
        message = json.loads(raw)
    if "error" in message:
        raise ValueError("MCP request rejected")
    result = message.get("result", {})
    if result.get("isError"):
        raise ValueError("Inference tool reported an error")
    if result.get("structuredContent") is not None:
        return result["structuredContent"]
    texts = [c["text"] for c in result.get("content", []) if c.get("type") == "text"]
    if not texts:
        raise ValueError("Inference returned no prediction data")
    predictions = json.loads(texts[0])
    if isinstance(predictions, dict) and predictions.get("error"):
        raise ValueError("Inference request rejected")
    return predictions


def infer(image_bytes, model_id, confidence, overlap, api_key):
    body = request_body(image_bytes, model_id, confidence, overlap)
    request = urllib.request.Request("https://mcp.roboflow.com/mcp",
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                 "x-api-key": api_key})
    with urllib.request.urlopen(request, timeout=60) as response:
        return decode_response(response.read().decode(), response.headers.get("Content-Type", ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model-id", default=DEFAULT_MODEL)
    parser.add_argument("--confidence", type=float, default=0.30)
    parser.add_argument("--overlap", type=float, default=0.30)
    args = parser.parse_args()
    if args.output.exists():
        parser.exit(2, "Output exists; choose a new path.\n")
    key = os.environ.get("ROBOFLOW_API_KEY") or getpass.getpass("Roboflow key (not saved): ")
    try:
        result = infer(args.image.read_bytes(), args.model_id, args.confidence, args.overlap, key)
        record = {"model_id": args.model_id, "confidence": args.confidence,
                  "overlap": args.overlap, "execution": "hosted Roboflow models_infer",
                  "result": result}
        args.output.write_text(json.dumps(record, indent=2)+"\n")
    except urllib.error.HTTPError as error:
        parser.exit(2, f"Roboflow HTTP {error.code}; check model access and service status.\n")
    except Exception as error:
        # URLs or provider exceptions may contain credentials; do not log them.
        parser.exit(2, f"Inference failed ({type(error).__name__}); no successful result saved.\n")
    finally:
        key = None
    print("Hosted inference result saved; this is not an accuracy evaluation.")


if __name__ == "__main__":
    main()
