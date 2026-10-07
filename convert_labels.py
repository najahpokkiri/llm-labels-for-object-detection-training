"""Validate reviewed pixel-coordinate labels and convert them to COCO."""
import argparse
import json
import math
from pathlib import Path


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def convert(document):
    """Input: {images: [{file_name, image_width, image_height, objects, ...}]}.

    review_complete must be true. This is a reviewer assertion, not AI proof.
    Unresolved uncertain_objects prevent export as complete supervision.
    """
    images = document.get("images")
    if not isinstance(images, list) or not images:
        raise ValueError("images must be a nonempty list")
    categories = {"tent": 1, "building": 2}
    result = {"images": [], "annotations": [], "categories": [
        {"id": cid, "name": name} for name, cid in categories.items()]}
    seen_files = set()
    for image_id, item in enumerate(images, 1):
        name = item.get("file_name")
        if not isinstance(name, str) or not name or name in seen_files:
            raise ValueError("file_name must be nonempty and unique")
        seen_files.add(name)
        width, height = item.get("image_width"), item.get("image_height")
        if any(not isinstance(v, int) or isinstance(v, bool) or v <= 0 for v in (width, height)):
            raise ValueError(f"{name}: dimensions must be positive integers")
        if item.get("review_complete") is not True:
            raise ValueError(f"{name}: review_complete must be true before supervised export")
        uncertain = item.get("uncertain_objects", [])
        if not isinstance(uncertain, list) or uncertain:
            raise ValueError(f"{name}: unresolved uncertainty prevents complete supervision")
        objects = item.get("objects")
        if not isinstance(objects, list):
            raise ValueError(f"{name}: objects must be a list, including for reviewed empty images")
        result["images"].append({"id": image_id, "file_name": name, "width": width, "height": height})
        seen_boxes = set()
        for obj in objects:
            cls, box = obj.get("class_name"), obj.get("bbox_xyxy")
            if cls not in categories:
                raise ValueError(f"{name}: unknown class {cls!r}")
            if not isinstance(box, list) or len(box) != 4 or not all(number(v) for v in box):
                raise ValueError(f"{name}: bbox_xyxy needs four finite numbers")
            left, top, right, bottom = box
            if not (0 <= left < right <= width and 0 <= top < bottom <= height):
                raise ValueError(f"{name}: box is inverted, empty or outside the image")
            identity = (cls, *box)
            if identity in seen_boxes:
                raise ValueError(f"{name}: duplicate annotation")
            seen_boxes.add(identity)
            bbox = [left, top, right-left, bottom-top]
            result["annotations"].append({"id": len(result["annotations"])+1,
                "image_id": image_id, "category_id": categories[cls], "bbox": bbox,
                "area": bbox[2]*bbox[3], "iscrowd": 0})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        result = convert(json.loads(args.input.read_text()))
    except (ValueError, TypeError, AttributeError, OSError) as error:
        parser.exit(2, f"Invalid labels: {error}\n")
    if args.output.exists():
        parser.exit(2, "Output already exists; select a new path.\n")
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Exported {len(result['images'])} images and {len(result['annotations'])} boxes")


if __name__ == "__main__":
    main()
