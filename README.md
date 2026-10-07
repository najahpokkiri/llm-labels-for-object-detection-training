# LLM labels for aerial and satellite object detection

This companion example converts reviewed LLM bounding-box proposals into COCO annotations and includes explicit hosted/local inference entry points. Conversion and hosted request code use Python 3.9+ and the standard library. Local detector inference additionally requires rfdetr and a compatible checkpoint. The final trained weights are available as a GitHub release asset; source imagery is excluded.

Run from this directory:

```sh
python3 -m unittest discover -s tests -v
python3 convert_labels.py examples/reviewed-labels.synthetic.json _annotations.coco.json
```

The fixture has invented coordinates and filenames, including one reviewed empty image. It tests software behaviour, not detection accuracy, and is not a training dataset. No corresponding image files are included.

## Generate and review labels

Upload a clear crop to an image-capable model in ChatGPT. Record the source dimensions. A starting prompt:

> Annotate individual visible tents and buildings. Use the supplied image's pixel dimensions, with the origin at the top left. Return image_width, image_height, objects and uncertain_objects. Each object needs class_name and bbox_xyxy as [left, top, right, bottom]. Exclude shadows, vehicles and walls. Mark ambiguous objects as uncertain. Do not assume the annotation is exhaustive.

This is a new teaching prompt, not the recovered historical prompt. Draw proposals on the exact original image and check missing objects, boundaries and class identity. Wrap accepted per-image JSON records in an `images` list, add `file_name`, and set `review_complete: true` only after review. Resolve uncertain regions or exclude the whole incomplete image; this small converter does not support ignore masks. Do not erase uncertainty just to make export pass.

The converter rejects unknown classes, invalid geometry, nonfinite coordinates, exact duplicate boxes/files, unfinished review and unresolved uncertain objects. It retains reviewed empty images. It cannot verify visual completeness, box alignment or human review. Inspect near-duplicate boxes visually.

Upload your clean images with matching filenames and the generated COCO annotations to your review service. Keep overlays separate from training pixels. Freeze a version and reserve independent sites/acquisitions for testing. The example does not automate uploads, paid training or publication.

## Train and use a detector

The historical capability test used hosted RF-DETR training. Follow current [RF-DETR documentation](https://rfdetr.roboflow.com/latest/) and [Roboflow documentation](https://docs.roboflow.com/) for your selected model/version. Record input dimensions, preprocessing, augmentation and train/validation/test membership. If running on a large scene, verify source-pixel object scale before choosing tiling settings.

See [MODEL_CARD.md](MODEL_CARD.md) for the pilot's evidence and limits, and [EXECUTION_STATUS.md](EXECUTION_STATUS.md) for the dated execution record. The supplied local inference command has executed the exact final checkpoint on real Gaza and Sudan crops.

## Hosted inference command

This sends your image to Roboflow. You need access to the chosen model and permitted hosted credit spending. The script prompts for the API key without saving it; an existing ROBOFLOW_API_KEY environment variable is also supported. Do not put a key in the command or repository.

```sh
python3 infer_hosted.py your-owned-image.png predictions.json --model-id workspace/model-slug
```

Omitting model-id selects the historical named model. A connector call now succeeds; the standalone hosted CLI remains unverified against the restored service. The October6 HTTP402 was superseded on October7. No credits/billing settings were changed. The script uses the official MCP models_infer tool and retains the model ID and thresholds in its result. Input threshold values are fractions, not percentages.

For an explicitly non-scientific connectivity input:

```sh
python3 make_smoke_image.py blank-smoke.png
python3 infer_hosted.py blank-smoke.png smoke-predictions.json
```

The generated blank image is not satellite imagery and cannot establish detector quality. Even a successful blank-image request would only verify model execution/access.

## Local inference command — checkpoint required

Create a separate Python environment and install the optional rfdetr package following current vendor documentation. Supply a trusted compatible Small checkpoint, your image and a new result path:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
curl -fL https://github.com/najahpokkiri/llm-labels-for-object-detection-training/releases/download/v0.1.0/final-rfdetr-small.weights.pt -o final-rfdetr-small.weights.pt
python3 infer_local.py final-rfdetr-small.weights.pt your-owned-image.png local-predictions.json --num-classes 2
```

This is a single-image API path, not the historical tiled-scene workflow. It retains numerical class IDs and checkpoint SHA-256; confirm the checkpoint's class mapping before rendering labels. The exact checkpoint loaded and ran on7October2026 with Python3.12, rfdetr1.11.2 and torch2.14.1. This legacy checkpoint returns local class1=building and2=tent; hosted inference returns0=building and1=tent. Check the SHA256 before loading downloaded weights:7311614347d35c52992a222c750f2d468ea20ec8862f144889d1e21302615967. The package never silently downloads a generic COCO model to stand in for the trained detector. Record your installed runtime version for a real run; these commands do not reproduce the historical training recipe.

## Release status

Companion repository: https://github.com/najahpokkiri/llm-labels-for-object-detection-training. Code: MIT. Final model weights: CC BY4.0, attributed to Najah Pokkiri / Axis Spatial, matching the public Roboflow project declaration. Source imagery and reference graphics are not redistributed; their public reproduction permissions remain separate. API keys and private paths are excluded. The checkpoint is a capability-test artefact, not an independently validated operational detector.
