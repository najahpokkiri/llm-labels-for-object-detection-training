# Current execution status — 7 October 2026

The exact final RF-DETR Small checkpoint was downloaded from the official Roboflow version1 export and executed with this package's infer_local.py on two real images. rfdetr1.11.2, torch2.14.1, Python3.12; threshold0.30.

- Native384×384 Sudan test cropte05:22 local class1 building candidates; reference has88 buildings. Not matched true positives or a recall estimate.
- Familiar370×370 Gaza crop:113 local class2 tent candidates and11 class1 building candidates. No additional NMS, tiling or accuracy evaluation.
- Connector-hosted execution on the same Gaza crop succeeded with144 tent and16 building candidates. Different runtime/processing outputs; numerical equivalence is not established.
- A connector call on base64 Sudan PNG returned provider HTTP500; local execution succeeded.

Checkpoint127380711bytes; SHA2567311614347d35c52992a222c750f2d468ea20ec8862f144889d1e21302615967. This legacy local checkpoint's class indices differ from hosted inference: local1building/2tent; hosted0building/1tent. Class mapping must be checked separately for other weights.

No GitHub destination or public release URL is established. Original figure reproduction permissions remain unresolved. The October6 blockers below are historical and superseded by the verified download/local runs and successful hosted connector call. The standalone hosted CLI has not yet been exercised successfully against the restored service.

---

# Exact model execution status

Checked 6 October 2026. This record distinguishes executable interfaces from a successful detector run.

Historical version: `najah-campus-tu-berlin-de/gaza-sudan-joint-final/1`.
Named finished model: `najah-campus-tu-berlin-de/gaza-sudan-joint-final-1-rfdetr-small-t1`.

## Checkpoint retrieval — blocked

The weight endpoint used by the official Roboflow Python SDK's `InferenceModel.download` returned HTTP403: **Not authorized to download this model in pt format.** No checkpoint was downloaded. The response does not identify whether the restriction is a plan, permission or export-policy issue.

Exact missing item for local execution: the final two-class **RF-DETR Small checkpoint** for this named run, with confirmed export/load format and class-ID mapping. An authorised owner export or restored export entitlement is needed. A generic COCO RF-DETR checkpoint is not a substitute for the tent/building model.

## Hosted inference — blocked

The actual `models_infer` call for the named model was attempted using a newly generated blank512×512 PNG owned by this example. No restricted source imagery was sent. The service rejected it with HTTP402 and reason **credit_cap_exceeded**, saying the workspace cannot currently spend serverless inference credits and to verify billing/credit-cap settings.

This demonstrates a service-access blocker, not a successful model forward pass or measured detection result. Do not infer the available credit balance or upgrade requirement from that response. No billing changes were made. Owner action is needed to restore permitted serverless spending, or supply the local checkpoint instead.

## Verification scope

Unit tests cover hosted request encoding, JSON/SSE prediction decoding, rejection of service errors and numerical local output serialization. They use controlled fixtures, not the live detector. Converter tests and synthetic conversion run end to end. Local detector loading/prediction remains unexecuted: optional rfdetr runtime is not installed here and the required checkpoint is unavailable. The local command follows current official RF-DETR API documentation but its compatibility with the hosted export is not established.

Public figure permission is a separate pending publication question. Neither billing access nor a checkpoint grants imagery or graphic reproduction rights.

References: [official SDK weight download implementation](https://github.com/roboflow/roboflow-python/blob/main/roboflow/models/inference.py), [RF-DETR detection API](https://rfdetr.roboflow.com/latest/learn/run/detection/), [RF-DETR checkpoint FAQ](https://rfdetr.roboflow.com/latest/faq/). Private redacted request receipts are retained outside this code package.
