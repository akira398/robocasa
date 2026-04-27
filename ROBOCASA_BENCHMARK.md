# RoboCasa365 Benchmark — Complete Reference

> ICLR 2026 · [robocasa.ai](https://robocasa.ai) · arXiv: 2603.04356  
> Original RoboCasa: RSS 2024 · arXiv: 2406.02523

---

## Table of Contents

1. [Quick Stats](#1-quick-stats)
2. [What Is RoboCasa365?](#2-what-is-robocasa365)
3. [Task Types: Atomic vs Composite](#3-task-types-atomic-vs-composite)
4. [Navigation and Mobile Manipulation](#4-navigation-and-mobile-manipulation)
5. [Pure Manipulation Tasks](#5-pure-manipulation-tasks)
6. [Episode Lengths / Task Duration](#6-episode-lengths--task-duration)
7. [Training Data (Datasets)](#7-training-data-datasets)
8. [Benchmarking Protocols](#8-benchmarking-protocols)
9. [Benchmark Results](#9-benchmark-results)
10. [Comparison with Other Benchmarks](#10-comparison-with-other-benchmarks)
11. [Why Good for Long-Horizon Reasoning?](#11-why-good-for-long-horizon-reasoning)
12. [Complete Atomic Task List](#12-complete-atomic-task-list)
13. [Complete Composite Task List (by Category)](#13-complete-composite-task-list-by-category)
14. [Target Task Splits](#14-target-task-splits)
15. [Lifelong Learning Phases](#15-lifelong-learning-phases)

---

## 1. Quick Stats

| Metric | Value |
|--------|-------|
| **Total tasks** | 365 (65 atomic + 300 composite) |
| **Tasks requiring navigation** | 4 (1 atomic + 3 composite) |
| **Pure manipulation tasks** | 313 / 317 registered (98.7%) |
| **Composite categories** | 60 activity groups |
| **Kitchen scenes (pretrain)** | 2,500+ |
| **Kitchen scenes (target/test)** | 10 (held-out) |
| **3D objects** | 2,200+ |
| **Total demonstration data** | 2,290+ hours |
| — Human demos (pretrain) | 482 hours, 300 tasks, 100 demos/task |
| — Human demos (target) | 193 hours, 50 tasks, 500 demos/task |
| — Synthetic (MimicGen) | 1,615 hours, 60 atomic tasks, ~10,000 demos/task |
| **Total composite episodes** | 31,922+ |
| **Episode length range** | 10 – 166 seconds (avg 52s, median 46s) |
| **Control frequency** | 20 Hz |
| **Robot** | Franka Panda on Omron mobile base (PandaOmron) |
| **Simulator** | MuJoCo via RoboSuite |
| **Venue** | ICLR 2026 |

---

## 2. What Is RoboCasa365?

RoboCasa365 is a large-scale simulation benchmark for training and evaluating **generalist robot policies** for household manipulation tasks. It models a realistic kitchen environment where a robot must combine navigation, dexterous manipulation, and long-horizon task planning.

The benchmark is designed around three core research questions:
- Can a robot learn to perform **many diverse tasks** from demonstrations?
- Can large pretraining datasets enable **foundation model**-style transfer to new tasks?
- Can a robot **continually acquire** harder tasks over time without forgetting simpler ones?

### Robot

The robot is a **Franka Panda arm mounted on an Omron mobile base** (`PandaOmron`). This gives it:
- 7-DOF arm for dexterous manipulation
- Full mobile base for navigating between kitchen fixtures
- Gripper for grasping and placing objects

### Kitchen Environment

The kitchen contains up to 14 types of fixtures:

| Fixture | Tasks involving it |
|---------|--------------------|
| Cabinets (upper/lower) | Pick-place, open/close |
| Refrigerator | Pick-place, open/close, fridge-internal moves |
| Fridge Freezer Drawer | Pick-place, open/close |
| Stove | Pick-place, turn on/off knobs, adjust heat |
| Oven | Pick-place, open/close, preheat, slide rack |
| Microwave | Pick-place, open/close, press button |
| Sink | Pick-place, turn on/off faucet, adjust water temp, turn spout |
| Dishwasher | Open/close, load, slide rack |
| Drawers | Pick-place, open/close, organize |
| Coffee Machine | Setup mug, serve mug, start machine |
| Toaster | Pick-place, turn on |
| Toaster Oven | Pick-place, open/close door, slide rack, turn on, adjust temp |
| Blender | Pick-place, open/close lid, turn on |
| Electric Kettle | Open/close lid, turn on |
| Stand Mixer | Open/close head |
| Counter | Primary workspace for staging, prep, plating |

---

## 3. Task Types: Atomic vs Composite

### Atomic Tasks (65 total)

Single-skill, single-step tasks. Each can be completed in a single action sequence without requiring sub-goal planning. They serve as:
- Standalone evaluation tasks
- Building blocks composed into composite tasks
- Pretraining data for MimicGen synthetic augmentation (60/65 have MimicGen support)

**Dataset:** 100 human demos × 65 tasks = 6,500 episodes  
**Horizon:** 10–35 seconds (200–700 steps @ 20 Hz)  
**18 of 65 atomic tasks** have target (held-out) evaluation splits.

### Composite Tasks (300 total)

Multi-step, long-horizon tasks spanning **60 activity categories**. Each task requires:
- Planning a sequence of 2–10+ sub-goals
- Navigating between multiple fixtures
- Executing diverse manipulation skills
- Sometimes semantic reasoning (e.g., sort by type, load in FIFO order)

**Dataset:** ~100 human demos × 300 tasks ≈ 31,922 episodes  
**Horizon:** 10–166 seconds (200–4,800 steps @ 20 Hz)  

---

## 4. Navigation and Mobile Manipulation

**Yes — RoboCasa is a full mobile manipulation benchmark.**

The robot uses its Omron mobile base to move between kitchen fixtures. However, the large majority of tasks are **pure manipulation** — the robot starts positioned near the relevant fixture and uses only its arm.

### Navigation breakdown

| Category | Tasks requiring navigation | Tasks without navigation |
|----------|---------------------------|--------------------------|
| Atomic | 1 / 65 | 64 / 65 |
| Composite | 3 / 252 registered | 249 / 252 registered |
| **Total** | **4 / 317 (1.3%)** | **313 / 317 (98.7%)** |

### Tasks that require navigation (mobile base)

| Task | Type | Horizon | Description |
|------|------|---------|-------------|
| `NavigateKitchen` | Atomic | 300 | Drive the mobile base to a target fixture |
| `ServeTea` | Composite | 900 | Pick cup from microwave, navigate to dining table, place on saucer |
| `PlaceDishesBySink` | Composite | 1,600 | Collect cup and bowl from counter, bring to sink area |
| `HotDogSetup` | Composite | 2,800 | Gather bun from counter + sausage from fridge, deliver to dining table |

These tasks use `DINING_COUNTER_EXCLUDED_LAYOUTS`, placing the destination fixture far from the starting position so the mobile base must traverse the kitchen.

### Pure manipulation (313 tasks)

All other tasks position the robot near the relevant fixture at episode start. Navigation is implicit in initialization but not part of the task horizon — the robot only uses its arm during the episode.

---

## 5. Pure Manipulation Tasks

The benchmark has extensive pure-manipulation coverage. **All 65 atomic tasks are pure manipulation** (no locomotion required beyond moving between adjacent positions).

Manipulation skill types covered:

| Skill Type | Examples |
|------------|----------|
| **Grasping & placing** | All 20 PickPlace variants, most composite tasks |
| **Articulated door control** | Open/close fridge, cabinet, microwave, oven, dishwasher, toaster oven |
| **Drawer operation** | Open/close drawer, slide dishwasher/oven rack |
| **Appliance knob/button** | Turn on stove, microwave, toaster, kettle, blender |
| **Fine manipulation** | Adjust water temperature, adjust heat, turn sink spout |
| **Lid manipulation** | Open/close blender lid, kettle lid, stand mixer head |
| **Multi-object sorting** | Sort by type, size, category, FIFO order |
| **Stacking & arranging** | Stack bowls, stack cans, arrange on trays |
| **Tool use** | Ladles, tongs, spatulas, colanders, measuring cups, scales |
| **Surface manipulation** | Scrub, wipe, rinse surfaces and boards |

---

## 6. Episode Lengths / Task Duration

### Composite Task Duration Distribution (304 tasks)

| Duration Range | Count | Percentage |
|----------------|-------|------------|
| < 30 seconds | 65 | 21% |
| 30 – 60 seconds | 141 | 46% |
| 60 – 100 seconds | 81 | 27% |
| > 100 seconds | 17 | 6% |

**Summary stats:** min=10s, max=166s, mean=51.8s, median=46s

### 10 Longest Composite Tasks

| Rank | Task | Steps @20Hz | Duration @20Hz |
|------|------|-------------|----------------|
| 1 | DivideBuffetTrays | 4,800 | 240s |
| 2 | RecycleSodaCans | 4,500 | 225s |
| 3 | PrepareDrinkStation | 3,900 | 195s |
| 4 | SetBowlsForSoup | 3,600 | 180s |
| 4 | SpicyMarinade | 3,600 | 180s |
| 6 | BeverageSorting | 3,500 | 175s |
| 6 | PrepareCocktailStation | 3,500 | 175s |
| 8 | ArrangeUtensilsByType | 3,400 | 170s |
| 8 | ReturnWashingSupplies | 3,400 | 170s |
| 10 | ClearSink | 3,300 | 165s |
| 10 | PackFoodByTemp | 3,300 | 165s |

### 10 Shortest Composite Tasks

| Task | Median Duration | Steps @20Hz | Demos |
|------|----------------|-------------|-------|
| TiltPan | 10s | 400 | 108 |
| ShakePan | 11s | 400 | 110 |
| JuiceFruitReamer | 12s | 400 | 110 |
| PackDessert | 12s | 400 | 108 |
| WipeTable | 13s | — | 106 |
| LowerHeat | 14s | 500 | 110 |
| MakeIcedCoffee | 14s | 500 | 102 |
| GarnishCake | 16s | — | 107 |
| RemoveCuttingBoardItems | 16s | 500 | 104 |
| BreadSetupSlicing | 16s | 800 | 107 |

### Atomic Task Horizons

Atomic tasks have shorter, tighter horizons:
- Minimum: 10s (200 steps)
- Maximum: 35s (700 steps)
- Typical: 15–20s (300–400 steps)

---

## 7. Training Data (Datasets)

RoboCasa365 provides both **training data and evaluation protocols**.

### Summary Table

| Dataset | Split | # Tasks | # Scenes | Demos/Task | Total Hours |
|---------|-------|---------|----------|-----------|------------|
| Human Pretraining | pretrain | 300 | 2,500 | 100 | 482 |
| Synthetic (MimicGen) | pretrain | 60 | 2,500 | ~10,000 | 1,615 |
| Human Target | target | 50 | 10 | 500 | 193 |
| **Total** | | **310 unique** | | | **2,290+** |

### Pretrain Split

- 2,500 diverse kitchen scenes (layout × style combinations)
- Collected via teleoperation (human)
- MimicGen: automatically augments 60 atomic tasks to ~10k demos each

### Target Split (Evaluation)

- **10 held-out scenes** — completely separate from pretrain scenes
- **50 tasks** split into three evaluation groups:
  - `atomic_seen` (18 tasks): atomic tasks also seen during pretraining
  - `composite_seen` (16 tasks): composite tasks also seen during pretraining
  - `composite_unseen` (16 tasks): composite tasks **never** seen during pretraining
- 500 human demos per task (5× more than pretrain)
- Tests generalization to novel scenes and novel task compositions

### MimicGen Augmentation

60 of the 65 atomic tasks have MimicGen synthetic data:
- Starts from 100 human demos
- Augments to ~10,000 demos per task
- Adds variation in object poses, scene configurations
- Used for pretraining foundation models

---

## 8. Benchmarking Protocols

RoboCasa365 defines three distinct benchmarking settings:

### 8.1 Multi-Task Learning

**Goal:** Train a single policy on all 300 pretraining tasks from human demos only.

- Training data: Human pretrain datasets, 300 tasks, 482 hours
- Evaluation: 50 random rollouts per task in **pretrain scenes**
- Reports success rate on: atomic-seen, composite-seen, composite-unseen
- Supported algorithms: Diffusion Policy, π₀, π₀.₅, GR00T N1.5

### 8.2 Foundation Model Learning

**Goal:** Pretrain on 2,290+ hours of data, then fine-tune on 50 target tasks.

**Phase 1 — Pretraining:**
- Data: 482h human (300 tasks) + 1,615h MimicGen (60 atomic tasks)
- Train for 80,000 steps (GR00T)

**Phase 2 — Target Task Fine-Tuning (3 independent experiments):**
- Fine-tune on each of: `atomic_seen`, `composite_seen`, `composite_unseen`
- Data splits: 10%, 30%, 100% of 500 demos per task
- Evaluate in held-out **target scenes**

### 8.3 Lifelong Learning

**Goal:** Sequentially acquire tasks of increasing complexity without forgetting earlier tasks.

Four phases, each building on the previous:

| Phase | Task Type | # Tasks | Complexity |
|-------|-----------|---------|------------|
| Phase 1 | All atomic tasks | 65 | Single-step skills |
| Phase 2 | Short composite | 20 | 2–3 stage sequences |
| Phase 3 | Medium composite | 20 | 4–5 stage sequences |
| Phase 4 | Long composite | 20 | 6+ stage sequences |

---

## 9. Benchmark Results

### Multi-Task Learning (Human pretrain data only, 482 hours)

| Task Split | Diffusion Policy | π₀ | π₀.₅ | GR00T N1.5 |
|------------|-----------------|-----|------|-----------|
| Atomic-Seen | 15.7% | 34.6% | 39.6% | **43.0%** |
| Composite-Seen | 0.2% | 6.1% | 7.1% | **9.6%** |
| Composite-Unseen | 1.25% | 1.1% | 1.2% | **4.4%** |
| **Average** | 6.1% | 14.8% | 16.9% | **20.0%** |

### Foundation Model Learning (GR00T N1.5 only)

| Task Split | Pretrain Only | Target Only (100%) | **Pretrain + Target (100%)** |
|------------|--------------|-------------------|---------------------------|
| Atomic-Seen | 41.9% | 60.6% | **68.5%** |
| Composite-Seen | 0.0% | 35.0% | **40.6%** |
| Composite-Unseen | 0.2% | 33.3% | **42.1%** |
| **Average** | 15.1% | 43.7% | **51.1%** |

### Key Takeaways

- Even SOTA (GR00T N1.5) achieves only **9.6%** on composite tasks in the multi-task setting — these tasks are genuinely hard
- Composite-Unseen goes from **0.2%** (pretrain only) → **42.1%** (pretrain + fine-tune), showing strong transfer
- Long pretraining helps even on tasks never seen before (Composite-Unseen: 0.2% → 42.1%)

---

## 10. Comparison with Other Benchmarks

| Feature | LIBERO | LIBERO-Long | MetaWorld | Calvin | **RoboCasa365** |
|---------|--------|------------|-----------|--------|-----------------|
| Total tasks | 50 | 10 | 50 | 34 | **365** |
| Long-horizon multi-step tasks | partial | ✓ (4–6 steps) | ✗ | chained | **✓ 300 tasks (2–10+ steps)** |
| Typical episode length | ~15–30s | ~60–120s | ~5–15s | ~30–60s | **10–166s (avg 52s)** |
| Navigation / mobile manipulation | ✗ | ✗ | ✗ | ✓ | **✓ full mobile base** |
| Scene diversity | ~10 | ~10 | single | 1 | **2,500+** |
| Total demo data | ~50 hrs | ~10 hrs | scripted | ~24 hrs | **2,290+ hrs** |
| Number of task categories | 4 | 1 | 12 | 4 | **60** |
| Generalization (unseen scenes) | limited | limited | ✗ | partial | **✓ 10 held-out target scenes** |
| Lifelong learning protocol | ✓ | ✗ | ✗ | ✗ | **✓ 4-phase** |
| Foundation model pretraining | ✗ | ✗ | ✗ | ✗ | **✓ 2,290+ hours** |

### vs. LIBERO-Long (detailed)

LIBERO-Long has 10 tasks, each with 4–6 sequential manipulation stages, ~60–120s per episode. It is a useful benchmark but limited by:
- Only 10 tasks (RoboCasa has 300 composite)
- No navigation between distant fixtures
- No generalization to novel environments
- ~10 hours of data total
- No unseen task split

RoboCasa composite tasks range from easier (comparable to LIBERO-Long's shortest tasks) up to significantly harder (166-second tasks with 10+ stages). The hardest tasks in RoboCasa are 1.4× longer than the longest LIBERO-Long tasks.

---

## 11. Why Good for Long-Horizon Reasoning?

1. **Sequential decision chains:** Tasks require 2–10+ sub-goals in correct order. Failure at any step cascades. No partial credit from atomic success alone.

2. **Semantic task goals:** Tasks like `LoadFridgeFifo` (load items in first-in-first-out order), `BeverageSorting` (sort by beverage type), `FilterMicrowavableItem` (identify microwave-safe items) require category understanding, not just motor imitation.

3. **Hidden state:** Fridge interiors, cabinets, and drawers are only visible when open. The robot must plan retrieval sequences under partial observability.

4. **Long temporal credit assignment:** At 20 Hz control, a 166-second episode = 3,320 control steps. Policies must maintain context over thousands of timesteps.

5. **Composition generalization:** Composite-Unseen evaluation directly tests whether learned skills compose to novel task sequences not seen during training.

6. **Realistic action space diversity:** Appliance control (knobs, buttons, lids) + navigation + dexterous grasping + tool use — the full action vocabulary of household robots.

7. **Scale prevents memorization:** 2,500+ visual environments and 2,200+ object variants mean policies cannot simply memorize visual patterns.

---

## 12. Complete Atomic Task List

65 tasks total. **Horizon** = max episode length in control steps (@ 20 Hz). **Target** = has held-out target evaluation split.

| Task Name | Category | Horizon (steps) | Horizon (secs) | Target |
|-----------|----------|----------------|---------------|--------|
| AdjustToasterOvenTemperature | Toaster Oven | 300 | 15s | ✓ |
| AdjustWaterTemperature | Sink | 300 | 15s | |
| CheesyBread | Simple Prep | 500 | 25s | |
| CloseBlenderLid | Blender | 600 | 30s | ✓ |
| CloseCabinet | Doors | 500 | 25s | ✓ |
| CloseDishwasher | Doors | 200 | 10s | |
| CloseDrawer | Drawer | 300 | 15s | |
| CloseElectricKettleLid | Electric Kettle | 200 | 10s | |
| CloseFridge | Doors | 600 | 30s | ✓ |
| CloseFridgeDrawer | Drawer | 300 | 15s | ✓ |
| CloseMicrowave | Doors | 300 | 15s | |
| CloseOven | Doors | 300 | 15s | |
| CloseStandMixerHead | Stand Mixer | 300 | 15s | |
| CloseToasterOvenDoor | Toaster Oven | 300 | 15s | ✓ |
| CoffeeServeMug | Coffee Machine | 300 | 15s | |
| CoffeeSetupMug | Coffee Machine | 400 | 20s | ✓ |
| LowerHeat | Stove | 500 | 25s | |
| MakeIcedCoffee | Simple Prep | 500 | 25s | |
| NavigateKitchen | Navigation | 300 | 15s | ✓ |
| OpenBlenderLid | Blender | 300 | 15s | ✓ |
| OpenCabinet | Doors | 700 | 35s | |
| OpenDishwasher | Doors | 300 | 15s | ✓ |
| OpenDrawer | Drawer | 500 | 25s | |
| OpenElectricKettleLid | Electric Kettle | 200 | 10s | ✓ |
| OpenFridge | Doors | 600 | 30s | |
| OpenFridgeDrawer | Drawer | 300 | 15s | |
| OpenMicrowave | Doors | 400 | 20s | |
| OpenOven | Doors | 200 | 10s | |
| OpenStandMixerHead | Stand Mixer | 300 | 15s | ✓ |
| OpenToasterOvenDoor | Toaster Oven | 300 | 15s | |
| PackDessert | Simple Prep | 400 | 20s | |
| PickPlaceCabinetToCounter | Pick & Place | 300 | 15s | |
| PickPlaceCounterToBlender | Pick & Place | 500 | 25s | |
| PickPlaceCounterToCabinet | Pick & Place | 500 | 25s | ✓ |
| PickPlaceCounterToDrawer | Pick & Place | 500 | 25s | |
| PickPlaceCounterToMicrowave | Pick & Place | 700 | 35s | |
| PickPlaceCounterToOven | Pick & Place | 400 | 20s | |
| PickPlaceCounterToSink | Pick & Place | 400 | 20s | |
| PickPlaceCounterToStandMixer | Pick & Place | 400 | 20s | |
| PickPlaceCounterToStove | Pick & Place | 400 | 20s | ✓ |
| PickPlaceCounterToToasterOven | Pick & Place | 300 | 15s | ✓ |
| PickPlaceDrawerToCounter | Pick & Place | 500 | 25s | ✓ |
| PickPlaceFridgeDrawerToShelf | Pick & Place | 400 | 20s | ✓ |
| PickPlaceFridgeShelfToDrawer | Pick & Place | 400 | 20s | |
| PickPlaceMicrowaveToCounter | Pick & Place | 500 | 25s | |
| PickPlaceSinkToCounter | Pick & Place | 600 | 30s | ✓ |
| PickPlaceStoveToCounter | Pick & Place | 300 | 15s | ✓ |
| PickPlaceToasterOvenToCounter | Pick & Place | 300 | 15s | |
| PickPlaceToasterToCounter | Pick & Place | 400 | 20s | ✓ |
| PreheatOven | Oven | 300 | 15s | |
| SlideDishwasherRack | Drawer | 300 | 15s | ✓ |
| SlideOvenRack | Oven | 300 | 15s | ✓ |
| SlideToasterOvenRack | Toaster Oven | 200 | 10s | |
| StartCoffeeMachine | Coffee Machine | 200 | 10s | |
| TurnOffMicrowave | Microwave | 200 | 10s | |
| TurnOffSinkFaucet | Sink | 200 | 10s | |
| TurnOffStove | Stove | 500 | 25s | ✓ |
| TurnOnBlender | Blender | 200 | 10s | ✓ |
| TurnOnElectricKettle | Electric Kettle | 300 | 15s | ✓ |
| TurnOnMicrowave | Microwave | 300 | 15s | ✓ |
| TurnOnSinkFaucet | Sink | 400 | 20s | ✓ |
| TurnOnStove | Stove | 300 | 15s | |
| TurnOnToaster | Toaster | 200 | 10s | |
| TurnOnToasterOven | Toaster Oven | 300 | 15s | |
| TurnSinkSpout | Sink | 200 | 10s | |

**Atomic task counts by category:**

| Category | Count |
|----------|-------|
| Pick & Place | 20 |
| Appliance control (stove, microwave, blender, kettle, mixer, toaster, coffee) | 19 |
| Doors (open/close: cabinet, fridge, microwave, oven, dishwasher, toaster oven) | 12 |
| Drawers (open/close, slide) | 6 |
| Sink (faucet, spout, temperature) | 5 |
| Simple prep recipes | 3 |
| Navigation | 1 |
| **Total** | **65** |

---

## 13. Complete Composite Task List (by Category)

300 tasks across 60 categories. Columns: **Task Name | Horizon (steps) | Median Duration | # Demos | Target Split**

*TARGET = has held-out target evaluation split (composite_seen or composite_unseen)*

---

### 1. Adding Ice To Beverages (4 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| MakeIceLemonade | 2,000 | 74s | 101 | |
| PlaceEqualIceCubes | 1,900 | 61s | 104 | |
| PlaceIceInCup | 800 | 25s | 101 | |
| RetrieveIceTray | 1,700 | 50s | 101 | |

---

### 2. Arranging Buffet (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ArrangeBuffetDessert | 2,700 | 91s | 103 | |
| CutBuffetPizza | 1,300 | 46s | 100 | |
| DivideBuffetTrays | 4,800 | **166s** | 100 | |
| PlaceBeveragesTogether | 2,600 | 91s | 109 | |
| TongBuffetSetup | 1,600 | 58s | 104 | |

---

### 3. Arranging Cabinets (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| GatherTableware | 1,500 | 44s | 103 | |
| ResetCabinetDoors | 2,200 | 68s | 106 | |
| StackCans | 1,200 | 36s | 101 | |

---

### 4. Arranging Condiments (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| CategorizeCondiments | 1,100 | 38s | 105 | composite_unseen |
| LineUpCondiments | 2,000 | 66s | 102 | |
| OrganizeCondiments | 1,500 | 49s | 105 | |

---

### 5. Baking (7 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| CookieDoughPrep | 1,900 | 61s | 108 | |
| CoolBakedCake | 2,400 | 69s | 102 | |
| CoolBakedCookies | — | 34s | 105 | |
| CupcakeCleanup | 700 | 24s | 101 | |
| MixCakeFrosting | 1,700 | 62s | 104 | |
| OrganizeBakingIngredients | 1,600 | 50s | 107 | |
| PastryDisplay | 700 | 21s | 103 | |

---

### 6. Boiling (8 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BoilCorn | — | 40s | 101 | |
| BoilEggs | — | 22s | 107 | |
| BoilPot | — | 28s | 108 | |
| CoolKettle | 1,600 | 55s | 100 | |
| FillKettle | 2,200 | 79s | 105 | |
| HeatMultipleWater | 2,800 | 100s | 105 | |
| PlaceLidToBoil | — | 22s | 103 | |
| StartElectricKettle | 700 | 23s | 108 | |

---

### 7. Brewing (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ArrangeTea | 1,500 | 116s | 104 | composite_unseen |
| DeliverBrewedCoffee | 700 | 23s | 107 | composite_seen |
| KettleBoiling | 1,000 | 31s | 101 | composite_seen |
| OrganizeCoffeeCondiments | 1,300 | 44s | 100 | |
| PrepareCoffee | 1,200 | 39s | 102 | composite_seen |
| SweetenCoffee | 1,300 | 46s | 107 | |

---

### 8. Broiling Fish (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| OvenBroilFish | 1,000 | 35s | 105 | |
| PrepareBroilingStation | 600 | 20s | 106 | |
| RemoveBroiledFish | 1,400 | 50s | 105 | |
| ToasterOvenBroilFish | — | 51s | 103 | |
| WashFish | 900 | 29s | 104 | |

---

### 9. Chopping Food (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ArrangeCuttingFruits | — | 41s | 106 | |
| ArrangeVegetables | 1,100 | 34s | 100 | |
| BreadSetupSlicing | 800 | 16s | 107 | |
| ClearCuttingBoard | 1,200 | 35s | 108 | |
| MeatTransfer | 2,300 | 70s | 104 | |
| OrganizeVegetables | 600 | 18s | 109 | |

---

### 10. Chopping Vegetables (2 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| CuttingToolSelection | 800 | 21s | 108 | composite_unseen |
| GatherCuttingTools | 1,600 | 46s | 105 | |

---

### 11. Cleaning Appliances (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| CleanBlenderJug | — | 19s | 109 | |
| PrepFridgeForCleaning | 2,400 | 81s | 101 | |
| PrepSinkForCleaning | 1,200 | 43s | 102 | |

---

### 12. Cleaning Sink (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ClearFoodWaste | 1,100 | 37s | 104 | |
| ClearSinkArea | 2,200 | 77s | 108 | |
| RinseSinkBasin | 900 | 29s | 104 | composite_seen |

---

### 13. Clearing Table (8 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BowlAndCup | 1,600 | 57s | 104 | |
| CandleCleanup | 3,000 | 100s | 102 | |
| ClearReceptaclesForCleaning | 2,600 | 78s | 103 | |
| ClusterItemsForClearing | — | 43s | 106 | |
| CondimentCollection | 1,400 | 38s | 106 | |
| DessertAssembly | 900 | 27s | 103 | |
| DrinkwareConsolidation | 2,400 | 37s | 104 | |
| FoodCleanup | 800 | 57s | 101 | |

---

### 14. Defrosting Food (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| DefrostByCategory | 2,200 | 61s | 100 | |
| MicrowaveThawing | 3,100 | 87s | 102 | |
| MicrowaveThawingFridge | 1,800 | 63s | 100 | |
| MoveToCounter | 800 | 24s | 109 | |
| QuickThaw | 1,100 | 34s | 110 | |
| ThawInSink | 1,000 | 36s | 111 | |

---

### 15. Filling Serving Dishes (4 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BuildAppetizerPlate | 2,700 | 90s | 106 | |
| DisplayMeatVariety | 2,900 | 90s | 106 | |
| MeatSkewerAssembly | 800 | 23s | 100 | |
| MixedFruitPlatter | 1,700 | 60s | 108 | |

---

### 16. Frying (8 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AssembleCookingArray | 2,200 | 73s | 103 | |
| DistributeSteakOnPans | — | 22s | 106 | |
| FryingPanAdjustment | 800 | 30s | 108 | |
| MealPrepStaging | 2,000 | 68s | 102 | |
| PressChicken | 1,000 | 28s | 104 | |
| RotatePan | 400 | 12s | 102 | |
| SearingMeat | 2,900 | 79s | 101 | composite_seen |
| SetupFrying | 2,100 | 78s | 102 | |

---

### 17. Garnishing Dishes (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AddLemonToFish | 1,400 | 47s | 101 | |
| AddSugarCubes | 600 | 22s | 111 | |
| GarnishCake | — | 16s | 107 | |
| GarnishCupcake | 1,200 | 36s | 108 | |
| GarnishPancake | 1,800 | 64s | 105 | composite_unseen |

---

### 18. Loading Dishwasher (2 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| LoadDishwasher | 1,200 | 41s | 100 | composite_seen |
| PrepareDishwasher | 900 | 26s | 105 | |

---

### 19. Loading Fridge (8 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| CreateChildFriendlyFridge | 2,200 | 82s | 105 | |
| LoadCondimentsInFridge | 2,000 | 57s | 106 | |
| LoadFridgeByType | 1,000 | 32s | 104 | |
| LoadFridgeFifo | 1,000 | 37s | 105 | |
| LoadPreparedFood | 1,000 | 36s | 103 | |
| MoveFreezerToFridge | 1,000 | 36s | 103 | |
| PlaceVeggiesInDrawer | 1,300 | 42s | 105 | |
| RearrangeFridgeItems | 1,600 | 56s | 106 | |

---

### 20. Making Juice (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ChooseRipeFruit | 600 | 21s | 108 | |
| FillBlenderJug | 1,000 | 33s | 105 | |
| JuiceFruitReamer | 400 | 12s | 110 | |

---

### 21. Making Salads (2 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| PrepareCheeseStation | 1,600 | 57s | 107 | |
| WashLettuce | 1,100 | 38s | 104 | composite_seen |

---

### 22. Making Smoothies (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AddIceCubes | 1,100 | 32s | 110 | |
| AddSweetener | 800 | 26s | 106 | |
| BlendIngredients | 1,200 | 45s | 107 | |
| PlaceStraw | 900 | 28s | 100 | |
| PrepareSmoothie | 1,200 | 42s | 110 | |

---

### 23. Making Tea (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ArrangeTeaAccompaniments | 1,100 | 42s | 102 | |
| ServeTea | 900 | 33s | 105 | |
| StrainerSetup | 1,500 | 47s | 108 | |

---

### 24. Making Toast (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BreadSelection | 1,300 | 36s | 106 | composite_unseen |
| PrepareToast | 2,500 | 88s | 101 | |
| SweetSavoryToastSetup | 2,700 | 74s | 110 | |

---

### 25. Managing Freezer Space (8 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ClearFreezer | 2,400 | 82s | 104 | |
| FreezeBottledWaters | 2,600 | 90s | 103 | |
| FreezeIceTray | 1,600 | 52s | 110 | |
| MaximizeFreezerSpace | 1,100 | 38s | 105 | |
| MoveFridgeToFreezer | 1,100 | 42s | 103 | |
| MoveToFreezerDrawer | 1,200 | 35s | 102 | |
| ReorganizeFrozenVegetables | 1,800 | 62s | 106 | |
| SeparateFreezerRack | 1,600 | 56s | 103 | composite_unseen |

---

### 26. Measuring Ingredients (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ChooseMeasuringCup | 1,200 | 40s | 106 | |
| OrganizeMeasuringCups | — | 30s | 103 | |
| WeighIngredients | 2,000 | 62s | 104 | composite_unseen |

---

### 27. Meat Preparation (2 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| PrepForTenderizing | 1,600 | 54s | 107 | |
| PrepMarinatingMeat | 1,900 | 59s | 101 | |

---

### 28. Microwaving Food (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| FilterMicrowavableItem | 1,100 | 38s | 106 | |
| MicrowaveCorrectMeal | 1,000 | 38s | 108 | |
| MicrowaveDefrostMeat | 1,200 | 39s | 105 | |
| PlaceMicrowaveSafeItem | 900 | 30s | 108 | |
| ReheatMeal | 1,200 | 43s | 107 | |
| ReturnHeatedFood | 900 | 31s | 107 | |

---

### 29. Mixing and Blending (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ColorfulSalsa | 1,600 | 52s | 109 | |
| MakeBananaMilkshake | — | 76s | 109 | |
| SpicyMarinade | 3,600 | 109s | 101 | |

---

### 30. Mixing Ingredients (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BlendSalsaMix | — | 65s | 103 | |
| BlendVegetableSauce | — | 64s | 100 | |
| CheeseMixing | — | 27s | 104 | |
| MakeCheesecakeFilling | — | 49s | 107 | |
| MakeChocolateMilk | — | 22s | 111 | |
| PrepareVeggieDip | — | 69s | 101 | |

---

### 31. Organizing Dishes and Containers (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| EmptyDishRack | — | 26s | 105 | |
| OrganizeMugsByHandle | 900 | 22s | 105 | |
| StackBowlsCabinet | 1,400 | 38s | 103 | composite_seen |

---

### 32. Organizing Recycling (4 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| RecycleBottlesBySize | 2,500 | 83s | 101 | |
| RecycleBottlesByType | 1,900 | 60s | 100 | composite_unseen |
| RecycleSodaCans | 4,500 | 146s | 104 | |
| RecycleStackedYogurt | 1,400 | 45s | 102 | |

---

### 33. Organizing Utensils (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ArrangeUtensilsByType | 3,400 | 126s | 102 | |
| ClusterUtensilsInDrawer | — | 24s | 108 | |
| OrganizeMetallicUtensils | 2,100 | 67s | 104 | |

---

### 34. Packing Lunches (4 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| PackFoodByTemp | 3,300 | 123s | 110 | |
| PackFruitContainer | 1,300 | 45s | 107 | |
| PackIdenticalLunches | 2,600 | 87s | 102 | composite_seen |
| PackSnack | — | 21s | 106 | |

---

### 35. Plating Food (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BalancedMealPrep | 1,000 | 32s | 108 | |
| PlateSteakMeal | 700 | 24s | 107 | |
| PlateStoreDinner | 2,600 | 95s | 104 | |

---

### 36. Portioning Meals (7 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| DistributeChicken | 1,600 | 52s | 110 | |
| PortionFruitBowl | 1,400 | 47s | 107 | |
| PortionHotDogs | 1,500 | 48s | 109 | composite_unseen |
| PortionInTupperware | 1,300 | 46s | 106 | |
| PortionOnSize | 1,800 | 58s | 106 | |
| PortionYogurt | 1,400 | 46s | 103 | |
| ScalePortioning | 1,400 | 49s | 102 | |

---

### 37. Preparing Hot Chocolate (2 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AddMarshmallow | 800 | 28s | 108 | |
| SweetenHotChocolate | 1,400 | 26s | 111 | |

---

### 38. Preparing Marinade (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BlendMarinade | 2,000 | 73s | 108 | |
| GatherMarinadeIngredients | 2,200 | 80s | 105 | |
| PlaceMeatInMarinade | 2,200 | 75s | 108 | |

---

### 39. Preparing Sandwiches (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| GatherVegetables | 900 | 31s | 105 | |
| HeatKebabSandwich | 1,800 | 62s | 104 | composite_unseen |
| HotDogSetup | 2,800 | 104s | 104 | |
| PrepareSandwichStation | — | 41s | 106 | |
| PrepareSausageCheese | 2,400 | 85s | 104 | |
| ToastHeatableIngredients | — | 35s | 109 | |

---

### 40. Reheating Food (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| HeatMug | 1,200 | 48s | 102 | |
| MakeLoadedPotato | 2,000 | 70s | 102 | |
| ReheatMeatOnStove | — | 20s | 106 | |
| SimmeringSauce | 2,300 | 66s | 105 | |
| WaffleReheat | 2,700 | 86s | 100 | composite_unseen |
| WarmCroissant | 1,100 | 33s | 107 | composite_seen |

---

### 41. Restocking Supplies (8 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BeverageSorting | 3,500 | 102s | 102 | |
| FreshProduceOrganization | 1,000 | 34s | 103 | |
| RefillCondimentStation | 1,300 | 47s | 104 | |
| RestockBowls | 2,400 | 90s | 105 | |
| RestockCannedFood | 700 | 20s | 108 | |
| RestockPantry | 1,700 | 58s | 100 | |
| RestockSinkSupplies | 1,500 | 48s | 103 | |
| StockingBreakfastFoods | 1,600 | 49s | 105 | |

---

### 42. Sanitizing Cutting Board (4 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| RemoveCuttingBoardItems | 500 | 16s | 104 | |
| RinseCuttingBoard | 1,500 | 49s | 107 | |
| SanitizePrepCuttingBoard | 1,400 | 46s | 108 | |
| ScrubCuttingBoard | 800 | 22s | 103 | composite_seen |

---

### 43. Sanitizing Surface (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| ArrangeSinkSanitization | — | 36s | 107 | |
| CleanMicrowave | 1,400 | 45s | 110 | |
| CountertopCleanup | — | 47s | 104 | |
| PrepForSanitizing | 2,500 | 88s | 100 | |
| SanitizeSink | — | 26s | 103 | |
| WipeTable | — | 13s | 106 | |

---

### 44. Sautéing Vegetables (7 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AdjustHeat | 1,500 | 49s | 104 | |
| ButterOnPan | 900 | 28s | 111 | |
| PlaceVegetablesEvenly | 1,000 | 33s | 108 | |
| PreheatPot | 1,800 | 56s | 105 | |
| ShakePan | 400 | 11s | 110 | |
| StirVegetables | 1,600 | 52s | 105 | composite_seen |
| TiltPan | 400 | 10s | 108 | |

---

### 45. Seasoning Food (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| LemonSeasoningFish | 1,500 | 54s | 101 | |
| SeasoningSteak | 900 | 32s | 102 | |
| SetUpSpiceStation | 2,700 | 84s | 100 | |

---

### 46. Serving Beverages (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| DeliverStraw | 1,700 | 50s | 104 | composite_seen |
| MatchCupAndDrink | 2,500 | 84s | 110 | |
| PrepareCocktailStation | 3,500 | 131s | 102 | |
| PrepareDrinkStation | 3,900 | 135s | 100 | |
| ServeMealJuice | — | 48s | 103 | |
| SetupSodaBowl | 2,400 | 91s | 100 | |

---

### 47. Serving Food (6 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AlcoholServingPrep | 3,100 | 98s | 101 | |
| DessertUpgrade | 800 | 25s | 109 | |
| PanTransfer | 1,200 | 39s | 100 | composite_seen |
| PlaceFoodInBowls | 1,700 | 59s | 107 | |
| PrepareSoupServing | 2,300 | 65s | 107 | |
| ServeSteak | 1,400 | 49s | 100 | composite_seen |

---

### 48. Setting the Table (13 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AlignSilverware | 1,700 | 58s | 106 | |
| ArrangeBreadBasket | 2,900 | 83s | 104 | composite_unseen |
| ArrangeBreadBowl | 900 | 28s | 105 | |
| ArrangeDrinkware | 1,100 | 39s | 103 | |
| BeverageOrganization | 3,000 | 81s | 100 | |
| DateNight | 3,200 | 110s | 107 | |
| SeasoningSpiceSetup | 2,800 | 88s | 105 | |
| SetBowlsForSoup | 3,600 | 135s | 100 | |
| SetupBowls | 1,800 | 65s | 107 | |
| SetupButterPlate | 2,700 | 95s | 101 | |
| SetupFruitBowl | 2,500 | 90s | 102 | |
| SetupWineGlasses | 2,100 | 77s | 101 | |
| SizeSorting | 1,000 | 27s | 106 | |

---

### 49. Simmering Sauces (1 task)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| TurnOffSimmeredSauceHeat | 1,000 | 34s | 109 | |

---

### 50. Slicing Meat (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| CleanBoard | 3,200 | 115s | 101 | |
| RetrieveMeat | 700 | 25s | 107 | |
| SetUpCuttingStation | 1,600 | 52s | 102 | composite_seen |

---

### 51. Slow Cooking (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AddToSoupPot | — | 45s | 105 | |
| BeginSlowCooking | — | 34s | 107 | |
| StopSlowCooking | — | 25s | 108 | |

---

### 52. Snack Preparation (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| BreadAndCheese | 600 | 18s | 215 | |
| CerealAndBowl | 2,900 | 79s | 102 | |
| MakeFruitBowl | 2,300 | 75s | 110 | |
| VeggieDipPrep | 2,100 | 52s | 103 | |
| YogurtDelightPrep | 1,500 | 39s | 105 | |

---

### 53. Sorting Ingredients (2 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| SeparateRawIngredients | — | 50s | 107 | |
| SortBreakfastIngredients | — | 46s | 106 | |

---

### 54. Steaming Food (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| MultistepSteaming | 2,300 | 85s | 101 | |
| SteamFish | — | 20s | 107 | |
| SteamInMicrowave | 1,400 | 45s | 102 | composite_seen |

---

### 55. Steaming Vegetables (3 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| PrepareVeggiesForSteaming | — | 19s | 104 | |
| RemoveSteamedVegetables | — | 24s | 104 | |
| SteamVeggiesWithWater | — | 40s | 107 | |

---

### 56. Storing Leftovers (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| FreezeCookedFood | 1,300 | 47s | 108 | |
| PrepareStoringLeftovers | 1,600 | 54s | 102 | |
| StoreDumplings | 2,500 | 91s | 106 | |
| StoreLeftoversByType | 1,700 | 60s | 100 | |
| StoreLeftoversInBowl | 1,700 | 58s | 110 | composite_seen |

---

### 57. Tidying Cabinets and Drawers (5 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| DrawerUtensilSort | — | 32s | 101 | |
| OrganizeCleaningSupplies | 2,700 | 67s | 105 | |
| PlaceBreakfastItemsAway | — | 56s | 103 | |
| SnackSorting | 1,300 | 40s | 100 | |
| UtensilShuffle | — | 36s | 103 | |

---

### 58. Toasting Bread (7 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| GetToastedBread | 2,000 | 77s | 103 | composite_seen |
| PJSandwichPrep | — | 47s | 105 | |
| ServeWarmCroissant | 1,200 | 37s | 100 | |
| ToastBagel | 1,500 | 51s | 103 | |
| ToastBaguette | 2,600 | 78s | 101 | |
| ToastOnCorrectRack | 2,600 | 82s | 103 | |
| ToastOneSlotPair | — | 24s | 106 | |

---

### 59. Washing Dishes (19 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AdjustWaterTemperature | — | — | — | |
| ClearSink | 3,300 | 125s | 101 | |
| CollectWashingSupplies | 1,800 | 58s | 101 | |
| DivideBasins | 1,400 | 36s | 152 | |
| DryDishes | 1,100 | 38s | 105 | |
| DryDrinkware | 900 | 29s | 102 | |
| DumpLeftovers | 600 | 21s | 103 | |
| PlaceDishesBySink | 1,600 | 62s | 103 | |
| PlaceOnDishRack | 1,000 | 35s | 103 | |
| PreRinseStation | 1,500 | 46s | 105 | |
| PreSoakPan | 1,600 | 46s | 106 | composite_seen |
| ReturnWashingSupplies | 3,400 | 119s | 100 | |
| RinseBowls | 1,900 | 70s | 100 | |
| RinseFragileItem | — | 27s | 104 | |
| ScrubBowl | 900 | 30s | 100 | |
| SoakSponge | 1,700 | 62s | 100 | |
| SortingCleanup | 2,000 | 70s | 110 | |
| StackBowlsInSink | 900 | 32s | 100 | |
| TransportCookware | 1,900 | 68s | 101 | |

---

### 60. Washing Fruits and Vegetables (11 tasks)

| Task | Steps | Duration | Demos | Target |
|------|-------|----------|-------|--------|
| AfterwashSorting | 2,000 | 63s | 101 | |
| AirDryFruit | 1,900 | 48s | 104 | |
| ClearClutter | 2,200 | 62s | 100 | |
| ClearSinkSpace | 1,200 | 28s | 101 | |
| DrainVeggies | 1,600 | 59s | 107 | |
| GatherProduceWashing | — | 42s | 103 | |
| PrepareVegetableRoasting | — | 24s | 107 | |
| PrewashFoodAssembly | 1,100 | 37s | 101 | |
| PrewashFoodSorting | 2,400 | 75s | 106 | |
| WashFruitColander | 2,100 | 60s | 103 | composite_unseen |
| WashInSaucepan | — | 41s | 104 | |

---

## 14. Target Task Splits

These 50 tasks form the held-out evaluation set, evaluated on 10 unseen kitchen scenes.

### Atomic-Seen (18 tasks)
Tasks also present in pretraining; tests generalization to novel scenes for known tasks.

| # | Task |
|---|------|
| 1 | CloseBlenderLid |
| 2 | CloseFridge |
| 3 | CloseToasterOvenDoor |
| 4 | CoffeeSetupMug |
| 5 | NavigateKitchen |
| 6 | OpenCabinet |
| 7 | OpenDrawer |
| 8 | OpenStandMixerHead |
| 9 | PickPlaceCounterToCabinet |
| 10 | PickPlaceCounterToStove |
| 11 | PickPlaceDrawerToCounter |
| 12 | PickPlaceSinkToCounter |
| 13 | PickPlaceToasterToCounter |
| 14 | SlideDishwasherRack |
| 15 | TurnOffStove |
| 16 | TurnOnElectricKettle |
| 17 | TurnOnMicrowave |
| 18 | TurnOnSinkFaucet |

### Composite-Seen (16 tasks)
Multi-step tasks also present in pretraining; tests generalization to novel scenes.

| # | Task | Duration |
|---|------|----------|
| 1 | DeliverStraw | 50s |
| 2 | GetToastedBread | 77s |
| 3 | KettleBoiling | 31s |
| 4 | LoadDishwasher | 41s |
| 5 | PackIdenticalLunches | 87s |
| 6 | PreSoakPan | 46s |
| 7 | PrepareCoffee | 39s |
| 8 | RinseSinkBasin | 29s |
| 9 | ScrubCuttingBoard | 22s |
| 10 | SearingMeat | 79s |
| 11 | SetUpCuttingStation | 52s |
| 12 | StackBowlsCabinet | 38s |
| 13 | SteamInMicrowave | 45s |
| 14 | StirVegetables | 52s |
| 15 | StoreLeftoversInBowl | 58s |
| 16 | WashLettuce | 38s |

### Composite-Unseen (16 tasks)
Multi-step tasks **never seen** during pretraining; tests true compositional generalization.

| # | Task | Duration |
|---|------|----------|
| 1 | ArrangeBreadBasket | 83s |
| 2 | ArrangeTea | 116s |
| 3 | BreadSelection | 36s |
| 4 | CategorizeCondiments | 38s |
| 5 | CuttingToolSelection | 21s |
| 6 | GarnishPancake | 64s |
| 7 | GatherTableware | 44s |
| 8 | HeatKebabSandwich | 62s |
| 9 | MakeIceLemonade | 74s |
| 10 | PanTransfer | 39s |
| 11 | PortionHotDogs | 48s |
| 12 | RecycleBottlesByType | 60s |
| 13 | SeparateFreezerRack | 56s |
| 14 | WaffleReheat | 86s |
| 15 | WashFruitColander | 60s |
| 16 | WeighIngredients | 62s |

---

## 15. Lifelong Learning Phases

### Phase 1 — All 65 Atomic Tasks
All atomic tasks listed in Section 12.

### Phase 2 — Short Composite Tasks (20 tasks, 2–3 stages)

KettleBoiling, PrepareCoffee, ClearCuttingBoard, RinseSinkBasin, LoadDishwasher, WashLettuce, StrainerSetup, PrepareToast, ChooseMeasuringCup, OrganizeCleaningSupplies, StackBowlsCabinet, RecycleStackedYogurt, AddMarshmallow, ScrubCuttingBoard, TurnOffSimmeredSauceHeat, SetUpCuttingStation, VeggieDipPrep, PreSoakPan, OrganizeCondiments, PrepForSanitizing

### Phase 3 — Medium Composite Tasks (20 tasks, 4–5 stages)

PlaceEqualIceCubes, RetrieveIceTray, RestockBowls, WashFish, PrepFridgeForCleaning, MicrowaveThawing, MealPrepStaging, AddLemonToFish, SimmeringSauce, StirVegetables, ClearSink, DeliverStraw, ServeSteak, StoreLeftoversInBowl, GetToastedBread, ToastBagel, AfterwashSorting, BlendIngredients, MicrowaveCorrectMeal, ArrangeBreadBowl

### Phase 4 — Long Composite Tasks (20 tasks, 6+ stages)

ArrangeBuffetDessert, CoolBakedCake, ClearReceptaclesForCleaning, MixedFruitPlatter, LoadFridgeByType, FreezeBottledWaters, PackIdenticalLunches, PlateStoreDinner, ScalePortioning, GatherMarinadeIngredients, PrepareSausageCheese, AlignSilverware, SetBowlsForSoup, SteamInMicrowave, ArrangeUtensilsByType, BeverageSorting, ClearSinkArea, HotDogSetup, PrepareDrinkStation, CleanBoard
