"""
Render still images from RoboCasa task demos (LeRobot format).

For each task, reads a pre-rendered episode video from the LeRobot dataset,
samples evenly-spaced frames, and saves them as PNG files. Atomic and composite
tasks are placed in separate subfolders; the episode's language instruction is
included in the output folder name.

Usage:
    # Render images for a list of specific tasks
    python render_task_images.py --tasks PickPlaceCounterToCabinet SearingMeat WashLettuce

    # Render images for ALL 65 atomic tasks
    python render_task_images.py --atomic

    # Render images for ALL 300 composite tasks (slow)
    python render_task_images.py --composite

    # Render images for the 50 target tasks
    python render_task_images.py --target

    # Render N images per task at different timesteps
    python render_task_images.py --tasks SearingMeat --frames_per_task 5

    # Also create a horizontal contact-sheet strip per task
    python render_task_images.py --tasks SearingMeat --contact_sheet

    # Limit how many tasks to render (useful for quick preview)
    python render_task_images.py --atomic --max_tasks 10

Output is saved to:
    output/task_images/atomic/<TaskName>__<description>/frame_<N>.png
    output/task_images/composite/<TaskName>__<description>/frame_<N>.png
"""

import argparse
import json
import os
import re
import sys

import imageio
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from robocasa.utils.dataset_registry import (
    ATOMIC_TASK_DATASETS,
    COMPOSITE_TASK_DATASETS,
    TARGET_TASKS,
)
from robocasa.utils.dataset_registry_utils import get_ds_path


# ─── helpers ──────────────────────────────────────────────────────────────────

def task_category(task: str) -> str:
    if task in ATOMIC_TASK_DATASETS:
        return "atomic"
    if task in COMPOSITE_TASK_DATASETS:
        return "composite"
    return "other"


def slugify(text: str, max_len: int = 70) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "_", text).strip("_")
    return text[:max_len].rstrip("_")


def get_episode_task(lerobot_path: str, demo_index: int = 0) -> str:
    episodes_path = os.path.join(lerobot_path, "meta", "episodes.jsonl")
    if not os.path.exists(episodes_path):
        return ""
    with open(episodes_path) as f:
        for line in f:
            ep = json.loads(line)
            if ep.get("episode_index") == demo_index:
                tasks = ep.get("tasks", [])
                return tasks[0] if tasks else ""
    return ""


def get_task_lerobot_path(task: str, prefer_split: str = "pretrain") -> str | None:
    path = get_ds_path(task, source="human", split=prefer_split)
    if path is not None and os.path.exists(path):
        return path
    other = "target" if prefer_split == "pretrain" else "pretrain"
    path = get_ds_path(task, source="human", split=other)
    if path is not None and os.path.exists(path):
        return path
    return None


def resolve_camera_key(lerobot_path: str, preferred: str = "agentview_left") -> str | None:
    vid_root = os.path.join(lerobot_path, "videos", "chunk-000")
    if not os.path.isdir(vid_root):
        return None
    keys = os.listdir(vid_root)
    for suffix in (preferred, "agentview_left", "agentview_right", "agentview"):
        for key in keys:
            if suffix in key:
                return key
    return keys[0] if keys else None


def get_episode_video_path(lerobot_path: str, camera_key: str, demo_index: int = 0) -> str | None:
    vid_dir = os.path.join(lerobot_path, "videos", "chunk-000", camera_key)
    if not os.path.isdir(vid_dir):
        return None
    mp4 = os.path.join(vid_dir, f"episode_{demo_index:06d}.mp4")
    if os.path.exists(mp4):
        return mp4
    candidates = sorted(f for f in os.listdir(vid_dir) if f.endswith(".mp4"))
    return os.path.join(vid_dir, candidates[0]) if candidates else None


def render_frames(
    lerobot_path: str,
    task_name: str,
    output_dir: str,
    frames_per_task: int = 4,
    camera_key: str = None,
    demo_index: int = 0,
) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)

    if camera_key is None:
        camera_key = resolve_camera_key(lerobot_path)
    if camera_key is None:
        raise RuntimeError(f"No video camera found in {lerobot_path}")

    mp4_path = get_episode_video_path(lerobot_path, camera_key, demo_index)
    if mp4_path is None:
        raise RuntimeError(f"No episode video for demo {demo_index} in {lerobot_path}")

    reader = imageio.get_reader(mp4_path)
    n_frames = reader.count_frames()
    indices = np.linspace(0, n_frames - 1, frames_per_task, dtype=int)

    saved = []
    try:
        for i, idx in enumerate(indices):
            try:
                frame = reader.get_data(int(idx))
            except Exception:
                continue
            out_path = os.path.join(output_dir, f"frame_{i:02d}.png")
            imageio.imwrite(out_path, frame)
            saved.append(out_path)
    finally:
        reader.close()

    print(f"  [{task_name}] Saved {len(saved)} frames from {os.path.basename(mp4_path)}")
    return saved


def create_contact_sheet(image_paths: list[str], output_path: str, task_name: str):
    """Combine multiple frames into a single horizontal strip with task name label."""
    from PIL import Image, ImageDraw, ImageFont

    images = [np.array(Image.open(p)) for p in image_paths]
    if not images:
        return

    h, w = images[0].shape[:2]
    label_h = 40
    n = len(images)
    canvas = Image.new("RGB", (w * n, h + label_h), (30, 30, 30))

    draw = ImageDraw.Draw(canvas)
    for i, img in enumerate(images):
        canvas.paste(Image.fromarray(img), (i * w, label_h))

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, 8), task_name, fill=(255, 255, 255), font=font)

    canvas.save(output_path)
    print(f"  [{task_name}] Contact sheet → {output_path}")


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Render still images from RoboCasa demos.")
    parser.add_argument("--tasks", nargs="+", help="Specific task names to render")
    parser.add_argument("--atomic", action="store_true", help="Render all atomic tasks")
    parser.add_argument("--composite", action="store_true", help="Render all composite tasks")
    parser.add_argument("--target", action="store_true", help="Render all 50 target tasks")
    parser.add_argument("--frames_per_task", type=int, default=4,
                        help="Number of frames to capture per task (default: 4)")
    parser.add_argument("--output_dir", type=str, default="output/task_images",
                        help="Root output directory")
    parser.add_argument("--camera", type=str, default="agentview_left",
                        help="Camera suffix to use (agentview_left, agentview_right, eye_in_hand)")
    parser.add_argument("--demo_index", type=int, default=0,
                        help="Which demo in the dataset to render (default: 0)")
    parser.add_argument("--max_tasks", type=int, default=None,
                        help="Limit number of tasks (useful for quick preview)")
    parser.add_argument("--contact_sheet", action="store_true",
                        help="Also create a horizontal contact-sheet per task")
    args = parser.parse_args()

    tasks = []
    if args.tasks:
        tasks = list(args.tasks)
    if args.atomic:
        tasks += list(ATOMIC_TASK_DATASETS.keys())
    if args.composite:
        tasks += list(COMPOSITE_TASK_DATASETS.keys())
    if args.target:
        tasks += (
            TARGET_TASKS["atomic_seen"]
            + TARGET_TASKS["composite_seen"]
            + TARGET_TASKS["composite_unseen"]
        )
    tasks = list(dict.fromkeys(tasks))

    if not tasks:
        parser.error("Specify at least one of: --tasks, --atomic, --composite, --target")

    if args.max_tasks:
        tasks = tasks[: args.max_tasks]

    print(f"Rendering images for {len(tasks)} tasks → {args.output_dir}")
    print()

    missing = []
    for task in tasks:
        lerobot_path = get_task_lerobot_path(task)
        if lerobot_path is None:
            print(f"  [{task}] SKIP — no local dataset found (run download_datasets first)")
            missing.append(task)
            continue

        category = task_category(task)
        description = slugify(get_episode_task(lerobot_path, args.demo_index) or task)
        folder_name = f"{task}__{description}"
        out_dir = os.path.join(args.output_dir, category, folder_name)
        camera_key = resolve_camera_key(lerobot_path, args.camera)

        try:
            saved = render_frames(
                lerobot_path=lerobot_path,
                task_name=task,
                output_dir=out_dir,
                frames_per_task=args.frames_per_task,
                camera_key=camera_key,
                demo_index=args.demo_index,
            )
            if args.contact_sheet and saved:
                sheet_path = os.path.join(out_dir, "contact_sheet.png")
                create_contact_sheet(saved, sheet_path, task)
            instruction = get_episode_task(lerobot_path, args.demo_index)
            txt_path = os.path.join(out_dir, "instruction.txt")
            with open(txt_path, "w") as f:
                f.write(f"Task: {task}\n")
                f.write(f"Instruction: {instruction}\n")
        except Exception as e:
            print(f"  [{task}] ERROR: {e}")

    print()
    print(f"Done. Output in: {os.path.abspath(args.output_dir)}")
    if missing:
        print(f"\n{len(missing)} tasks had no local dataset:")
        print("  Download with: python robocasa/scripts/download_datasets.py --tasks " + " ".join(missing[:5]) + " ...")


if __name__ == "__main__":
    main()
