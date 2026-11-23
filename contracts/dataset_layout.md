# C2 · YOLO dataset layout

Producer: **Member A** (2.2.1, 2.2.2) · Consumer: **Member B** (3.1.x, 3.2.1)

```text
data/processed/yolo/images/{train,val,test}/<video>_<frame>.jpg
data/processed/yolo/labels/{train,val,test}/<video>_<frame>.txt   # "cls cx cy w h" normalised 0-1, one line per box
data/processed/dataset.yaml   # Ultralytics format: path, train, val, test, names (from contracts/classes.json)
data/splits/splits.json       # {"train":["v01",...],"val":[...],"test":[...]}  video IDs only, no frame leakage
```

Rules

- File stem = `<video_id>_<frame_index>`. `src.data.split.video_id_from_stem()` must recover `video_id`.
- Images with no tool keep an **empty** `.txt` (background image).
- Class ids are 0–5 only (C1); m2cai16 `SpecimenBag` is dropped.
- `dataset.yaml` example:

```yaml
path: data/processed/yolo
train: images/train
val: images/val
test: images/test
names: {0: grasper, 1: bipolar, 2: hook, 3: scissors, 4: clipper, 5: irrigator}
```
