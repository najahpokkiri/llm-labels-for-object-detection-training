# Historical capability test: tents and buildings

Experiment recorded 18 September 2026; evidence recovered 6 October 2026. The final trained checkpoint is distributed separately as a GitHub release asset; updated7October2026.

## Intended question

Could Astra-assisted annotations support a compact detector, could an explicit building class help distinguish roofs from tents, and could limited Sudan supervision improve performance on more varied imagery? These were exploratory questions, not a preregistered controlled study.

## Data and sequence

- Tent-only baseline: 36 Gaza crops, 3,421 tent boxes; 28/4/4 image split. TentNetFA prediction candidates plus Astra refinement/discovery contributed pseudo-labels.
- Gaza extension: retained images, tent labels and splits; added 523 building boxes. Later model capacity and input resolution also changed.
- Sudan: nine completed crops, 310 buildings, no accepted positive tents. Training received four images/70 buildings; validation two/148; test three/92. Each split included a reviewed empty crop. Incomplete images were excluded.
- Final hosted version: 45 images, 3,421 tents, 833 buildings; 32/6/7 split, auto-orientation and stretch resize to 512×512. A prepared 49-image variant was not the named final training version.

## Reported results

| Run | Tent AP50 | Building AP50 | Combined AP50 | Test |
| --- | ---: | ---: | ---: | --- |
| Tent-only RF-DETR Nano | 56.1% | — | 56.1% | Four Gaza crops |
| Earlier joint RF-DETR Small | 60.8% | 74.7% | 67.7% | Four Gaza crops; 19 buildings |
| Final mixed RF-DETR Small | 57.8% | 27.5% | 42.65% | Seven mixed crops; 111 buildings |

Scores measure agreement with AI-reviewed pseudo-references, not independent human-validated accuracy. The joint Nano panel used a different evaluation display and cannot establish improvement over the tent-only baseline. Exact earlier Small checkpoint mapping, full augmentation recipe and seed were not recovered.

The final building test includes 92 Sudan references, 88 in one crop. Changing the test population prevents treating 67.7→42.65 as a causal regression or adaptation measurement. No paired evaluation of both checkpoints on identical domain-separated images was retained. No Africa-only AP/recall is available. With no accepted positive Sudan tents, African tent recall cannot be assessed.

## Qualitative findings and limits

The tent-only model detected ordinary roofs as tents in Morocco. The external Turkey stadium output showed useful detections, misses and class confusion. The final supplied Sudan overview missed many small structures and included apparent background building false positives. Sudan became an adapted domain after training samples were added; Turkey remained outside training.

Object scale/rendering mismatch is plausible, not a demonstrated cause. Source crop sizes differed from inference tile sizes. A7October native384-pixel Sudan test-crop run produced22 building candidates against88 reviewed references; totals are not matched accuracy or recall. The historical full-scene input diagnostic remains unexecuted. The retained inference workflow used 512 source-pixel tiles, 20% overlap, confidence0.30 and NMS IoU0.30; the displayed confusion-matrix threshold is unknown.

This test does not establish exhaustive counts, occupancy, sensor-wide generalisation, segmentation masks, precise footprints or production readiness. Next evaluation: fixed processing, both checkpoints on identical independent reference scenes, domain-specific metrics and more diverse confirmed target positives.

## Attribution and release

[TentNetFA](https://github.com/algorithmicgovernance/TentNetFA) and [Jess Rapson's project account](https://jess-rapson.com/prediction/2026/03/22/tracking-conflict-displacement.html) describe the credited work with Karim and Forensic Architecture. Their candidate predictions are not independent ground truth for this detector. Their density/count validation cannot be transferred to these boxes.

Source imagery and the historical label archive are not redistributed. Public figure reproduction permissions remain unresolved. No new training or independent accuracy evaluation was performed.

Final checkpoint: version1 of `najah-campus-tu-berlin-de/gaza-sudan-joint-final`, RF-DETR Small t1. Release:v0.1.0, `final-rfdetr-small.weights.pt`,127380711bytes. SHA256:7311614347d35c52992a222c750f2d468ea20ec8862f144889d1e21302615967. Weights:CC BY4.0, attribution Najah Pokkiri / Axis Spatial; the public Roboflow project declaresCC BY4.0. This does not grant rights to the original imagery or TentNetFA graphics. Upstream RF-DETR Small architecture/code has its own Apache2.0 licence.

Verified local runtime:Python3.12, rfdetr1.11.2, torch2.14.1; local legacy class IDs1building/2tent. Hosted IDs0building/1tent. Local single-image execution and hosted connector execution succeeded on a familiar Gaza crop, with differing candidate counts; equivalence is not established. Native Sudan execution succeeded locally. The package does not reproduce training or historical tiled-scene inference.
