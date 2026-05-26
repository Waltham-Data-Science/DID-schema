# Accept–Reject Decision-Making Revealed via a Quantitative and Ethological Study of *C. elegans* Foraging

**Citation:** Haley JA, Chen T, Aoi M, Chalasani SH. *eLife* 13:RP103191 (2024; Version of Record 2025-09-10). DOI: 10.7554/eLife.103191.

**File:** `datasetPapers/elife-103191-v1.pdf`

## Short description

Single-animal video tracking of *C. elegans* foraging in arenas with small bacterial patches (OP50 *E. coli*) of varying density, size, and distribution. Patch encounters are classified with Gaussian-mixture and semi-supervised models into sense / non-respond and explore / exploit events, and a normative model predicts the observed accept–reject decisions using sensory signals, satiety, and patch-history statistics. Model predictions are validated with food-deprivation manipulations and sensory mutants (`osm-6`, `mec-4`).

## Subjects

| Field | Value |
|---|---|
| Species | *Caenorhabditis elegans* (and OP50 *E. coli* as food) |
| Stage | Young adult hermaphrodite, picked as L4 ~24.6 ± 3.4 h before experiment |
| Rearing | NGM (1.7 % agar), OP50 seeded, 20 °C |
| Controls / mutants | N2 Bristol (wild-type, WBStrain00000001); PR811 `osm-6(p811) V` (WBStrain00030796); TU253 `mec-4(u253) X` (WBStrain00035037) |
| Food strains | OP50 (WBStrain00041969); OP50-GFP (WBStrain00041972; LB + 100 µg/mL carbenicillin) |
| N | 443 total worms across conditions |

Transgenic/mutant strains always run in parallel with matched controls on the same day.

## Procedures / treatments

**Bacterial patch preparation**
- OP50 liquid culture → centrifuge 3000 rpm × 5 min → dilute to OD₆₀₀ = 10 (~13.1 × 10⁹ cfu/mL) → serial dilutions to OD₆₀₀ ∈ {0, 0.05, 0.1, 0.5, 1, 2, 3, 4, 5, 10}.
- 0.5 µL droplets on 3 % agar NGM (low-moisture) for quick-drying patches, stored at 4 °C up to 6 weeks.
- Growth times before assay: ~1 h (standard), 12 h, or 48 h at room temperature.

**Arenas (laser-cut PET transparency)**
| Assay | Arena Ø | Patches | Patch size | Duration |
|---|---|---|---|---|
| Single-density, multi-patch | 30 mm | 19 patches on isometric grid, 6 mm spacing | 0.5 µL | 1 h |
| Large single-patch | 30 mm | 1 center | 20 µL | 1 h |
| Small single-patch | 9 mm | 1 center | 0.5 µL | 1 h (higher resolution) |
| Multi-density, multi-patch | 30 mm | 18 × 0.5 µL droplets, OD mix {1, 5, 10} | 0.5 µL | 2 h (NGM without Bacto peptone) |

**Animal transfer:** 3 % agar plug method (single worm per small arena; 4 worms per 30 mm arena).

**Acclimation:** 30–60 L4 worms on a 200 µL OD₆₀₀ = 1 patch at 20 °C for ~24 h.

## Recording hardware / acquisition

- Edge-lit backlight (Advanced Illumination); condition plate on suspended glass, face-down.
- Cameras: PixeLink PL-B741F; Navitar lenses 1-60135 and 1-6044 (0.25×).
- Acquisition: StreamPix 8 (RRID:SCR_015773).
- Standard: 1024 × 1024 px, 3 fps, ~33 px/mm.
- High-res (small single-patch): ~105 px/mm, 8 fps.
- Recorded per-session temperature (21.99 ± 0.95 °C) and humidity (51.4 ± 11.7 %).
- Max 24 animals/day (2 cameras × 12 h).

## Bacterial-density estimation

- OP50-GFP imaged on Zeiss Axio Zoom.V16.
- MATLAB Image Processing Toolbox: illumination correction, patch-edge detection, radial fluorescence-intensity profile, peak amplitude over time fit by linear (per condition) or multinomial regression for very dilute conditions.
- Reported as "relative density" linearly scaled to 10 at OD₆₀₀ = 10 / 1 h / 0.5 µL.

## Behavioral tracking

- WormLab (MBF Bioscience, RRID:SCR_017669) auto-tracking + manual stitching of broken tracks (border/collision/dust).
- Midpoint exported (25 midline points in high-res assay; head–tail manually confirmed).
- Exclusion: <75 % tracked duration; poor contrast video for patch detection.

## Derived per-encounter variables

- Patch encounter entry/exit thresholds (midpoint 0.46024 mm / 0.28758 mm from patch edge).
- Duration, on-patch velocity, deceleration, minimum velocity, max velocity change.
- GMM classification: exploration vs exploitation (log duration + log velocity).
- Semi-supervised QDA: sensing vs non-responding (deceleration + min vel + Δvel).
- Silverman's test for bimodality (bootstrapped, n = 2000).

## Modeling

- Ridge regression with 50 000 replicates for coefficient estimation across N2, `osm-6`, `mec-4`; Benjamini–Hochberg-corrected mean-of-differences tests for mutant vs WT.
- Explore/exploit posterior probability; accept/reject decision model incorporating current patch density, recent patch history, and satiety state.

## Data / code availability

- **Raw + processed data (NDI Cloud):** DOI 10.63884/ndic.2025.pb77mj2s — behavior videos, fluorescence microscopy images, animal tracks, patch locations over time.
- **Code:** https://github.com/shreklab/Haley-et-al-2024 (copy archived at shreklab 2025).
- Per-figure source data files supplied with the eLife article.

## Relevance for DID/NDI schema design

Another direct NDI-Cloud consumer. Tests:

- `subject_group` / `cohort`: multiple worms per arena; need distinction between individual worm tracks and cohort-level acclimation plate.
- `stimulus/patch` or `environment/lawn`: patch-edge position, OD-derived density estimate, growth time, arena geometry, isometric-grid layout template.
- `imaging/video` document: camera model, lens, fps, spatial resolution, backlight type, arena-registration "contrast" video.
- Per-session `environment_metadata`: room temperature + humidity traces.
- `tracking` document: WormLab version, per-frame body-point export, manual stitching provenance, inclusion criteria.
- `behavior/derived_event` document: patch encounter detection thresholds, classifier model (GMM / QDA) with regularisation α, train/test split.
- `model` / `analysis` document (new): normative foraging model parameters (β coefficients per strain), bootstrap replicate count, statistical correction method.
- Must support multi-condition randomisation metadata (assay order randomised across days) and per-assay covariate recording (temp, humidity, animal age, bacterial growth time).
