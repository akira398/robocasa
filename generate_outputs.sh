#!/usr/bin/env bash
# generate_outputs.sh
# Reproduces all output/ folders used in the slides and PPTX.
# Run from the repo root with the robocasa conda env active:
#   conda activate robocasa
#   bash generate_outputs.sh
#
# Or without activating first:
#   conda run -n robocasa bash generate_outputs.sh
#
# Navigation classification:
#   Pure manipulation  — robot stays in the main kitchen zone (no FixtureType.DINING_COUNTER)
#   Cross-zone tasks   — robot must traverse to a separate dining-counter zone
#                        (DINING_COUNTER_EXCLUDED_LAYOUTS set in task class)
#   Explicit nav tasks — NavigateKitchen + tasks whose instruction explicitly says "navigate"

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── task lists ────────────────────────────────────────────────────────────────

# Truly pure manipulation: all fixtures in the main kitchen zone
PURE_MANIP_ATOMIC="TurnOnToaster TurnOnStove PickPlaceCounterToStove PickPlaceCounterToCabinet OpenCabinet"

PURE_MANIP_COMPOSITE="WashLettuce LoadDishwasher PrepareCoffee SearingMeat \
  BeverageSorting SpicyMarinade ArrangeUtensilsByType ReturnWashingSupplies ClearSink"

# Explicit navigation: mobile-base traversal is stated in the task description
NAV_EXPLICIT_ATOMIC="NavigateKitchen"
NAV_EXPLICIT_COMPOSITE="ServeTea PlaceDishesBySink HotDogSetup"

# Cross-zone tasks: require delivering to a dining counter in a separate kitchen zone
# (task class sets EXCLUDE_LAYOUTS = Kitchen.DINING_COUNTER_EXCLUDED_LAYOUTS)
NAV_CROSS_ZONE_COMPOSITE="DivideBuffetTrays RecycleSodaCans PackFoodByTemp \
  PrepareDrinkStation SetBowlsForSoup PrepareCocktailStation"

# 10 longest tasks (by max horizon); several require cross-zone traversal
LONGEST_COMPOSITE="DivideBuffetTrays RecycleSodaCans PrepareDrinkStation SetBowlsForSoup SpicyMarinade \
  BeverageSorting PrepareCocktailStation ArrangeUtensilsByType ReturnWashingSupplies ClearSink"

ALL_TASKS="$PURE_MANIP_ATOMIC $PURE_MANIP_COMPOSITE \
           $NAV_EXPLICIT_ATOMIC $NAV_EXPLICIT_COMPOSITE \
           $NAV_CROSS_ZONE_COMPOSITE $LONGEST_COMPOSITE"

# deduplicate
ALL_TASKS=$(echo "$ALL_TASKS" | tr ' ' '\n' | sort -u | tr '\n' ' ')

# ── step 1: download datasets ─────────────────────────────────────────────────

echo "================================================================"
echo " Step 1: Downloading datasets"
echo "================================================================"
echo "y" | python -m robocasa.scripts.download_datasets \
  --tasks $ALL_TASKS \
  --split pretrain

# ── step 2: examples_pure_manipulation ───────────────────────────────────────

echo ""
echo "================================================================"
echo " Step 2: output/examples_pure_manipulation  (images + videos)"
echo " Tasks: atomic + composite with no cross-zone traversal"
echo "================================================================"

python render_task_images.py \
  --tasks $PURE_MANIP_ATOMIC $PURE_MANIP_COMPOSITE \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/examples_pure_manipulation

python render_task_videos.py \
  --tasks $PURE_MANIP_ATOMIC $PURE_MANIP_COMPOSITE \
  --video_skip 3 \
  --output_dir output/examples_pure_manipulation

# ── step 3: examples_navigation ──────────────────────────────────────────────

echo ""
echo "================================================================"
echo " Step 3: output/examples_navigation  (images + videos)"
echo " Includes: explicit nav tasks + cross-zone dining-counter tasks"
echo "================================================================"

python render_task_images.py \
  --tasks $NAV_EXPLICIT_ATOMIC $NAV_EXPLICIT_COMPOSITE $NAV_CROSS_ZONE_COMPOSITE \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/examples_navigation

python render_task_videos.py \
  --tasks $NAV_EXPLICIT_ATOMIC $NAV_EXPLICIT_COMPOSITE $NAV_CROSS_ZONE_COMPOSITE \
  --video_skip 3 \
  --output_dir output/examples_navigation

# ── step 4: longest ───────────────────────────────────────────────────────────

echo ""
echo "================================================================"
echo " Step 4: output/longest  (images + videos)"
echo " 10 longest tasks by horizon (mix of pure manip + cross-zone)"
echo "================================================================"

python render_task_images.py \
  --tasks $LONGEST_COMPOSITE \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/longest

python render_task_videos.py \
  --tasks $LONGEST_COMPOSITE \
  --video_skip 3 \
  --output_dir output/longest

# ── done ──────────────────────────────────────────────────────────────────────

echo ""
echo "================================================================"
echo " All done. Output folders:"
echo "   output/examples_pure_manipulation/  — truly pure manipulation"
echo "   output/examples_navigation/         — explicit nav + cross-zone"
echo "   output/longest/                     — 10 longest tasks"
echo "================================================================"
