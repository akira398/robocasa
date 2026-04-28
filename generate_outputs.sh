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
#
# Navigation classification is data-driven: we measure the robot's base position
# displacement from episode_000000.parquet (observation.state[0:2] = base x,y).
# Tasks with max displacement from start > 0.5 m are classified as navigation.
# The LONGEST_PURE_MANIP list uses a stricter threshold of < 0.01 m (no movement at all).
#
# Measured max displacements for tasks in this script (observation.state[0:2], episode 0):
#   TurnOnToaster           ~0.00 m   pure
#   TurnOnStove              0.22 m   pure
#   PickPlaceCounterToStove ~0.00 m   pure
#   PickPlaceCounterToCabinet~0.00 m  pure
#   OpenCabinet             ~0.00 m   pure
#   WashLettuce             ~0.00 m   pure
#   LoadDishwasher          ~0.00 m   pure
#   PrepareCoffee           ~0.00 m   pure
#   SpicyMarinade           0.0002 m  pure
#   ClearSink               0.0002 m  pure
#   MicrowaveThawing        0.0002 m  pure
#   CerealAndBowl           0.0013 m  pure
#   SweetSavoryToastSetup   0.0009 m  pure
#   OrganizeCleaningSupplies 0.0009 m pure
#   ToastBaguette           0.0009 m  pure
#   PrepareToast            0.0002 m  pure
#   RestockBowls            0.0002 m  pure
#   MakeFruitBowl           0.0006 m  pure
#   SearingMeat              1.02 m   navigation
#   ReturnWashingSupplies    1.49 m   navigation
#   PlaceDishesBySink        1.21 m   navigation
#   ArrangeUtensilsByType    1.85 m   navigation
#   BeverageSorting          2.40 m   navigation
#   NavigateKitchen          2.44 m   navigation
#   ServeTea                 2.94 m   navigation
#   HotDogSetup              2.94 m   navigation
#   RecycleSodaCans          3.05 m   navigation
#   DivideBuffetTrays        3.70 m   navigation
#   PrepareCocktailStation   3.41 m   navigation
#   SetBowlsForSoup          4.52 m   navigation
#   PackFoodByTemp           4.80 m   navigation
#   PrepareDrinkStation      6.93 m   navigation

# Pure manipulation: max base displacement <= 0.5 m in demo episode 0
PURE_MANIP_ATOMIC="TurnOnToaster TurnOnStove PickPlaceCounterToStove PickPlaceCounterToCabinet OpenCabinet"

PURE_MANIP_COMPOSITE="WashLettuce LoadDishwasher PrepareCoffee SpicyMarinade ClearSink"

# Navigation: max base displacement > 0.5 m in demo episode 0
NAV_ATOMIC="NavigateKitchen"
NAV_COMPOSITE="ServeTea PlaceDishesBySink HotDogSetup \
  SearingMeat ReturnWashingSupplies \
  BeverageSorting ArrangeUtensilsByType \
  DivideBuffetTrays RecycleSodaCans PackFoodByTemp \
  PrepareDrinkStation SetBowlsForSoup PrepareCocktailStation"

# 10 longest pure-manipulation composite tasks, data-driven: max base displacement < 0.01 m
# (no robot base movement whatsoever in demo episode 0):
#   SpicyMarinade(3600,0.0002m), ClearSink(3300,0.0002m), MicrowaveThawing(3100,0.0002m),
#   CerealAndBowl(2900,0.0013m), SweetSavoryToastSetup(2700,0.0009m),
#   OrganizeCleaningSupplies(2700,0.0009m), ToastBaguette(2600,0.0009m),
#   PrepareToast(2500,0.0002m), RestockBowls(2400,0.0002m), MakeFruitBowl(2300,0.0006m)
# Excluded (move > 0.5 m): CleanBoard(2.57m), HeatMultipleWater(0.77m), PackIdenticalLunches(2.73m)
# WaffleReheat(2700) has no pretrain dataset available.
LONGEST_PURE_MANIP="SpicyMarinade ClearSink MicrowaveThawing CerealAndBowl \
  SweetSavoryToastSetup OrganizeCleaningSupplies ToastBaguette \
  PrepareToast RestockBowls MakeFruitBowl"

ALL_TASKS="$PURE_MANIP_ATOMIC $PURE_MANIP_COMPOSITE \
           $NAV_ATOMIC $NAV_COMPOSITE \
           $LONGEST_PURE_MANIP"

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
echo " Tasks with base displacement > 0.5 m in demo data"
echo "================================================================"

python render_task_images.py \
  --tasks $NAV_ATOMIC $NAV_COMPOSITE \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/examples_navigation

python render_task_videos.py \
  --tasks $NAV_ATOMIC $NAV_COMPOSITE \
  --video_skip 3 \
  --output_dir output/examples_navigation

# ── step 4: longest ───────────────────────────────────────────────────────────

echo ""
echo "================================================================"
echo " Step 4: output/longest  (images + videos)"
echo " 10 longest pure-manipulation tasks (all fixtures adjacent, no base traversal)"
echo "================================================================"

python render_task_images.py \
  --tasks $LONGEST_PURE_MANIP \
  --frames_per_task 4 --contact_sheet \
  --output_dir output/longest

python render_task_videos.py \
  --tasks $LONGEST_PURE_MANIP \
  --video_skip 3 \
  --output_dir output/longest

# ── done ──────────────────────────────────────────────────────────────────────

echo ""
echo "================================================================"
echo " All done. Output folders:"
echo "   output/examples_pure_manipulation/  — base displacement <= 0.5 m in demos"
echo "   output/examples_navigation/         — base displacement > 0.5 m in demos"
echo "   output/longest/                     — 10 longest pure-manipulation tasks"
echo "================================================================"
