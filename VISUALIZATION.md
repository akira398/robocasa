# RoboCasa Visualization — Setup & Usage

This guide covers how to render still images and MP4 videos from RoboCasa demo datasets.

---

## 1. Environment Setup

### 1.1 Create the conda environment

```bash
conda create -n robocasa python=3.11 -y
conda activate robocasa
```

### 1.2 Install RoboCasa

```bash
# From the repo root
pip install -e .
```

### 1.3 Install RoboSuite

RoboSuite is not on PyPI in the required version — install from source:

```bash
git clone https://github.com/ARISE-Initiative/robosuite.git /path/to/robosuite
cd /path/to/robosuite
pip install -e .
```

Then pin the versions RoboCasa requires:

```bash
pip install mujoco==3.3.1 numpy==2.2.5 numba==0.61.2 scipy==1.15.3
```

### 1.4 Install visualization dependencies

```bash
pip install imageio imageio[ffmpeg] Pillow h5py
```

### 1.5 Download kitchen assets

```bash
python robocasa/scripts/download_kitchen_assets.py
```

This downloads ~10 GB of textures, fixtures, and 3D objects into `robocasa/models/assets/`.

---

## 2. Configure Dataset Path

Edit (or create) `robocasa/macros_private.py` and set the path where your datasets will live:

```python
DATASET_BASE_PATH = "/absolute/path/to/robocasa/datasets"
```

The datasets script will download into `<DATASET_BASE_PATH>/v1.0/pretrain/...`.

---

## 3. Download Datasets

Use the built-in script to download human demo datasets for specific tasks:

```bash
# Download a few specific tasks
echo "y" | python -m robocasa.scripts.download_datasets \
  --tasks TurnOnStove PickPlaceCounterToCabinet OpenCabinet SearingMeat \
  --split pretrain

# Download all tasks (atomic + composite, pretrain split)
echo "y" | python -m robocasa.scripts.download_datasets --all --split pretrain

# Download all tasks (both pretrain and target splits)
echo "y" | python -m robocasa.scripts.download_datasets --all --split pretrain target
```

> **Note:** The script does not have `--atomic` or `--composite` flags. Use `--all` to download
> everything, or `--tasks` to list specific task names.

Each dataset downloads as a LeRobot-format archive containing:
- `data/chunk-000/episode_XXXXXX.parquet` — state/action data
- `videos/chunk-000/<camera>/episode_XXXXXX.mp4` — pre-rendered video per episode
- `meta/episodes.jsonl` — episode metadata including language instructions

---

## 4. Render Still Images

`render_task_images.py` extracts evenly-spaced frames from a demo video and saves them as PNG files. It also optionally creates a horizontal contact-sheet strip per task.

### Basic usage

```bash
# Render images for specific tasks
python render_task_images.py --tasks TurnOnStove SearingMeat LoadDishwasher

# Render all atomic tasks
python render_task_images.py --atomic

# Render all composite tasks
python render_task_images.py --composite

# Render the 50 target tasks
python render_task_images.py --target
```

### Key options

| Flag | Default | Description |
|------|---------|-------------|
| `--tasks TASK [TASK ...]` | — | Specific task names |
| `--atomic` | off | All 65 atomic tasks |
| `--composite` | off | All 300 composite tasks |
| `--target` | off | The 50 target evaluation tasks |
| `--frames_per_task N` | 4 | Number of frames to extract per task |
| `--contact_sheet` | off | Also save a horizontal strip of all frames |
| `--camera SUFFIX` | `agentview_left` | Camera to use (`agentview_left`, `agentview_right`, `eye_in_hand`) |
| `--demo_index N` | 0 | Which episode to render |
| `--output_dir PATH` | `output/task_images` | Root output directory |
| `--max_tasks N` | — | Limit number of tasks (useful for quick preview) |

### Example — 10 tasks with contact sheets

```bash
python render_task_images.py \
  --tasks TurnOnToaster TurnOnStove PickPlaceCounterToStove \
          PickPlaceCounterToCabinet OpenCabinet \
          WashLettuce LoadDishwasher PrepareCoffee SearingMeat DivideBuffetTrays \
  --frames_per_task 4 \
  --contact_sheet
```

### Output structure

```
output/task_images/
├── atomic/
│   └── <TaskName>__<instruction>/
│       ├── frame_00.png
│       ├── frame_01.png
│       ├── frame_02.png
│       ├── frame_03.png
│       └── contact_sheet.png     ← all frames in one strip
└── composite/
    └── <TaskName>__<instruction>/
        ├── frame_00.png
        └── ...
```

Atomic and composite tasks are separated into subfolders. The folder name includes the task name and a slugified version of the episode's language instruction.

---

## 5. Render Videos

`render_task_videos.py` reads a pre-rendered episode video from the dataset and writes a new MP4, optionally subsampled to reduce file size.

### Basic usage

```bash
# Render videos for specific tasks
python render_task_videos.py --tasks TurnOnStove SearingMeat LoadDishwasher

# Render all atomic tasks
python render_task_videos.py --atomic

# Render all composite tasks
python render_task_videos.py --composite

# Render the 50 target tasks
python render_task_videos.py --target
```

### Key options

| Flag | Default | Description |
|------|---------|-------------|
| `--tasks TASK [TASK ...]` | — | Specific task names |
| `--atomic` | off | All 65 atomic tasks |
| `--composite` | off | All 300 composite tasks |
| `--target` | off | The 50 target evaluation tasks |
| `--video_skip N` | 3 | Write 1 in every N frames (3 → ~6 fps from 20 Hz data) |
| `--camera SUFFIX` | `agentview_left` | Camera to use |
| `--demo_index N` | 0 | Which episode to render |
| `--max_frames N` | — | Cap number of frames (None = full episode) |
| `--output_dir PATH` | `output/task_videos` | Root output directory |
| `--max_tasks N` | — | Limit number of tasks |

`video_skip=1` gives real-time 20 fps. `video_skip=3` gives ~6 fps (3× speed). `video_skip=5` gives ~4 fps (5× speed).

### Example — 10 tasks at real-time speed

```bash
python render_task_videos.py \
  --tasks TurnOnToaster TurnOnStove PickPlaceCounterToStove \
          PickPlaceCounterToCabinet OpenCabinet \
          WashLettuce LoadDishwasher PrepareCoffee SearingMeat DivideBuffetTrays \
  --video_skip 1
```

### Output structure

```
output/task_videos/
├── atomic/
│   └── <TaskName>__<instruction>.mp4
└── composite/
    └── <TaskName>__<instruction>.mp4
```

---

## 6. Reproduce the Example Output Folders

The following commands reproduce the four pre-generated example folders in `output/`.

### Pure manipulation — 10 tasks short to long

```bash
python render_task_images.py \
  --tasks TurnOnToaster TurnOnStove PickPlaceCounterToStove PickPlaceCounterToCabinet OpenCabinet \
          WashLettuce LoadDishwasher PrepareCoffee SearingMeat DivideBuffetTrays \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/examples_pure_manipulation

python render_task_videos.py \
  --tasks TurnOnToaster TurnOnStove PickPlaceCounterToStove PickPlaceCounterToCabinet OpenCabinet \
          WashLettuce LoadDishwasher PrepareCoffee SearingMeat DivideBuffetTrays \
  --video_skip 3 \
  --output_dir output/examples_pure_manipulation
```

### Navigation tasks

```bash
python render_task_images.py \
  --tasks NavigateKitchen ServeTea PlaceDishesBySink HotDogSetup \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/examples_navigation

python render_task_videos.py \
  --tasks NavigateKitchen ServeTea PlaceDishesBySink HotDogSetup \
  --video_skip 3 \
  --output_dir output/examples_navigation
```

### 10 longest tasks

```bash
# Download the datasets first
echo "y" | python -m robocasa.scripts.download_datasets \
  --tasks DivideBuffetTrays RecycleSodaCans PrepareDrinkStation SetBowlsForSoup SpicyMarinade \
          BeverageSorting PrepareCocktailStation ArrangeUtensilsByType ReturnWashingSupplies ClearSink \
  --split pretrain

python render_task_images.py \
  --tasks DivideBuffetTrays RecycleSodaCans PrepareDrinkStation SetBowlsForSoup SpicyMarinade \
          BeverageSorting PrepareCocktailStation ArrangeUtensilsByType ReturnWashingSupplies ClearSink \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/longest

python render_task_videos.py \
  --tasks DivideBuffetTrays RecycleSodaCans PrepareDrinkStation SetBowlsForSoup SpicyMarinade \
          BeverageSorting PrepareCocktailStation ArrangeUtensilsByType ReturnWashingSupplies ClearSink \
  --video_skip 3 \
  --output_dir output/longest
```

---

## 7. Notes

- **Dataset format**: Datasets use the [LeRobot](https://github.com/huggingface/lerobot) format. Each task has pre-rendered episode videos in `videos/chunk-000/<camera>/episode_XXXXXX.mp4` — no simulator is needed for rendering.
- **Camera names**: Available cameras are `agentview_left`, `agentview_right`, and `eye_in_hand`. The default is `agentview_left`.
- **Skipping existing files**: Both scripts skip tasks that already have output files. Delete the output file to force a re-render.
- **Missing datasets**: Tasks whose dataset is not downloaded locally are skipped with a message. Run `download_datasets.py` first.
