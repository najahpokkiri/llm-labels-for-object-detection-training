"""Single-image local RF-DETR Small inference with an explicitly supplied checkpoint.

Optional rfdetr dependency required. The final exported checkpoint was run
with rfdetr 1.11.2 on 7 October 2026. Class IDs remain numeric: the tested
legacy checkpoint uses 1=building, 2=tent, whereas hosted inference uses
0=building, 1=tent. Other checkpoints may use another mapping.
"""
import argparse
import hashlib
import json
from pathlib import Path
from importlib.metadata import version


def serialize(detections):
    return [{"bbox_xyxy": [float(v) for v in box], "class_id": int(cls),
             "confidence": float(score)}
            for box, cls, score in zip(detections.xyxy, detections.class_id, detections.confidence)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--num-classes", type=int, default=2)
    parser.add_argument("--threshold", type=float, default=0.30)
    args = parser.parse_args()
    if not args.checkpoint.is_file() or not args.image.is_file():
        parser.exit(2, "Supply an existing trusted checkpoint and image.\n")
    if args.output.exists():
        parser.exit(2, "Output exists; choose a new path.\n")
    if args.num_classes < 1 or not 0 <= args.threshold <= 1:
        parser.exit(2, "Invalid class count or threshold.\n")
    try:
        import rfdetr
        from rfdetr import RFDETRSmall
    except ImportError:
        parser.exit(2, "Install the optional rfdetr package in your own environment.\n")
    model = RFDETRSmall(pretrain_weights=str(args.checkpoint), num_classes=args.num_classes)
    detections = model.predict(str(args.image), threshold=args.threshold)
    record = {"execution": "local single-image RF-DETR Small", "threshold": args.threshold,
              "rfdetr_version": version("rfdetr"),
              "checkpoint_sha256": hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
              "predictions": serialize(detections)}
    args.output.write_text(json.dumps(record, indent=2)+"\n")
    print("Single-image predictions saved; no scene tiling or accuracy evaluation performed.")


if __name__ == "__main__":
    main()
