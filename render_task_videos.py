"""
Render MP4 videos from RoboCasa task demos (LeRobot format).

Reads pre-rendered episode videos from the LeRobot dataset structure and writes
output MP4s. Atomic and composite tasks are placed in separate subfolders;
the episode's language instruction is appended to each filename.

Usage:
    # Render one video per task for a specific list of tasks
    python render_task_videos.py --tasks PickPlaceCounterToCabinet SearingMeat WashLettuce

    # Render videos for all 50 target tasks
    python render_task_videos.py --target

    # Render videos for the atomic tasks
    python render_task_videos.py --atomic

    # Render composite tasks, 1 demo each, max 20 tasks
    python render_task_videos.py --composite --max_tasks 20

    # Control speed (video_skip=1 = real-time 20fps, video_skip=5 = 4fps)
    python render_task_videos.py --tasks SearingMeat --video_skip 1

    # Use a specific demo index
    python render_task_videos.py --tasks SearingMeat --demo_index 5

Output:
    output/task_videos/atomic/<TaskName>__<description>.mp4
    output/task_videos/composite/<TaskName>__<description>.mp4
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


def get_task_lerobot_path(task: str) -> str | None:
    for split in ("pretrain", "target"):
        path = get_ds_path(task, source="human", split=split)
        if path is not None and os.path.exists(path):
            return path
    return None


def get_episode_video_path(lerobot_path: str, camera_key: str, demo_index: int = 0) -> str | None:
    """Find the MP4 video path for a given episode and camera."""
    vid_dir = os.path.join(lerobot_path, "videos", "chunk-000", camera_key)
    if not os.path.isdir(vid_dir):
        return None
    mp4 = os.path.join(vid_dir, f"episode_{demo_index:06d}.mp4")
    if os.path.exists(mp4):
        return mp4
    # fallback to first available episode
    candidates = sorted(f for f in os.listdir(vid_dir) if f.endswith(".mp4"))
    return os.path.join(vid_dir, candidates[0]) if candidates else None


def resolve_camera_key(lerobot_path: str, preferred: str) -> str | None:
    """Map a user-facing camera name to the actual LeRobot video key."""
    vid_root = os.path.join(lerobot_path, "videos", "chunk-000")
    if not os.path.isdir(vid_root):
        return None
    keys = os.listdir(vid_root)
    # prefer exact suffix match
    for key in keys:
        if key.endswith(preferred.replace("robot0_", "robot0_")):
            return key
    # fallback: left > right > any
    for suffix in ("agentview_left", "agentview_right", "agentview"):
        for key in keys:
            if suffix in key:
                return key
    return keys[0] if keys else None


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


def render_video(
    lerobot_path: str,
    task_name: str,
    output_path: str,
    camera_key: str = None,
    video_skip: int = 3,
    demo_index: int = 0,
    max_frames: int = None,
):
    if camera_key is None:
        camera_key = resolve_camera_key(lerobot_path, "agentview_left")
    if camera_key is None:
        raise RuntimeError(f"No video camera found in {lerobot_path}")

    mp4_path = get_episode_video_path(lerobot_path, camera_key, demo_index)
    if mp4_path is None:
        raise RuntimeError(f"No episode video found for demo {demo_index} in {lerobot_path}")

    reader = imageio.get_reader(mp4_path)
    n_frames = reader.count_frames()
    if max_frames:
        n_frames = min(n_frames, max_frames)

    out_fps = max(1, 20 // video_skip)
    writer = imageio.get_writer(output_path, fps=out_fps, quality=7)
    try:
        for idx in range(0, n_frames, video_skip):
            try:
                frame = reader.get_data(idx)
            except Exception:
                break
            writer.append_data(frame)
    finally:
        writer.close()
        reader.close()


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Render MP4 videos from RoboCasa demos.")
    parser.add_argument("--tasks", nargs="+", help="Specific task names")
    parser.add_argument("--atomic", action="store_true", help="All atomic tasks")
    parser.add_argument("--composite", action="store_true", help="All composite tasks")
    parser.add_argument("--target", action="store_true", help="All 50 target tasks")
    parser.add_argument("--output_dir", type=str, default="output/task_videos")
    parser.add_argument("--camera", type=str, default="agentview_left",
                        help="Camera suffix to use (agentview_left, agentview_right, eye_in_hand)")
    parser.add_argument("--video_skip", type=int, default=3,
                        help="Write 1 in N frames (3=~6fps). Lower=slower video but smoother.")
    parser.add_argument("--demo_index", type=int, default=0,
                        help="Which demo episode to use (default: 0)")
    parser.add_argument("--max_frames", type=int, default=None,
                        help="Max frames to render per task (None = full episode)")
    parser.add_argument("--max_tasks", type=int, default=None,
                        help="Limit number of tasks to render")
    args = parser.parse_args()

    tasks = []
    if args.tasks:
        tasks += args.tasks
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

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Rendering videos for {len(tasks)} tasks → {args.output_dir}")
    print()

    missing, errors, done = [], [], []
    for task in tasks:
        lerobot_path = get_task_lerobot_path(task)
        if lerobot_path is None:
            print(f"  [{task}] SKIP — dataset not found locally")
            missing.append(task)
            continue

        category = task_category(task)
        out_dir = os.path.join(args.output_dir, category)
        os.makedirs(out_dir, exist_ok=True)

        description = slugify(get_episode_task(lerobot_path, args.demo_index) or task)
        filename = f"{task}__{description}.mp4"
        output_path = os.path.join(out_dir, filename)

        if os.path.exists(output_path):
            print(f"  [{task}] EXISTS — skipping (delete to re-render)")
            done.append(task)
            continue

        try:
            print(f"  [{task}] Rendering…", end=" ", flush=True)
            camera_key = resolve_camera_key(lerobot_path, args.camera)
            render_video(
                lerobot_path=lerobot_path,
                task_name=task,
                output_path=output_path,
                camera_key=camera_key,
                video_skip=args.video_skip,
                demo_index=args.demo_index,
                max_frames=args.max_frames,
            )
            size_mb = os.path.getsize(output_path) / 1e6
            print(f"→ {output_path} ({size_mb:.1f} MB)")
            instruction = get_episode_task(lerobot_path, args.demo_index)
            txt_path = output_path.replace(".mp4", ".txt")
            with open(txt_path, "w") as f:
                f.write(f"Task: {task}\n")
                f.write(f"Instruction: {instruction}\n")
            done.append(task)
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append((task, str(e)))

    print()
    print(f"Done: {len(done)} rendered, {len(missing)} missing datasets, {len(errors)} errors")
    if missing:
        print(f"\nDownload missing datasets:")
        print(f"  python robocasa/scripts/download_datasets.py --tasks {' '.join(missing[:5])} ...")
    if errors:
        print("\nErrors:")
        for task, err in errors:
            print(f"  {task}: {err}")


if __name__ == "__main__":
    main()
