# Premature Vision Drives Aberrant Development of Response Properties in Primary Visual Cortex

**Citation:** Griswold SV, Van Hooser SD. *eLife* 14:RP106513 (2025; Version of Record 2025-10-08). DOI: 10.7554/eLife.106513.

**File:** `datasetPapers/elife-106513-v2.pdf`

## Short description

Terminal multichannel extracellular recordings in monocular V1 of ferrets (P55–68) reared under three conditions — both eyes opened early (P25), one eye opened early (P25), or neither eye opened early — to test how premature visual experience shifts receptive-field development (orientation / direction / spatial / temporal frequency tuning, spontaneous firing rate).

## Subjects

| Field | Value |
|---|---|
| Species | Ferret (*Mustela putorius furo*), Marshall BioResources |
| Sex | Female only (all experiments) |
| Arrival | Litters of ≥4 kits with jill at P12–21 |
| Recording age | P55–68 (terminal, after ocular-dominance critical period) |
| Housing | 60 × 60 × 35 cm stainless-steel cage, 12 h:12 h light cycle, hammock + toys |
| N total | 27 female ferrets: 17 one-eye premature (EO1), 4 two-eye premature (EO2), 11 control |

## Treatment groups and premature-vision manipulation

| Group | Manipulation | Cell label |
|---|---|---|
| Control | Neither eye opened early; time of natural opening noted | `control` |
| EO1 | One eye gently opened with forceps at P25 | `EO1contra` (neurons viewing through the early-opened eye, contralateral hemisphere) and `EO1ipsi` (ipsilateral hemisphere) |
| EO2 | Both eyes opened at P25 | `EO2` |

**Visual-exposure protocol:** 2 h/day for 4 consecutive days starting at P25, in a rat cage on a heating pad, gently kept awake for "natural, unguided viewing" of the lab environment. No further intervention between P28 and the terminal recording. Time of natural eye opening noted for each eye individually (kits often open one eye ≤1 day before the other).

## Surgical preparation (terminal, P55–68)

- Ketamine 20 mg/kg i.m. induction.
- Atropine 0.16–0.8 mg/kg i.m., dexamethasone 0.5 mg/kg i.m.
- Mask isoflurane → tracheostomy → ventilated 1.5–3 % isoflurane in 2:1 N₂O:O₂.
- IP cannula for gallamine triethiodide (10–30 mg/kg/h) and Ringer's (3 mL/kg/h).
- Wound margins infused with bupivacaine.
- Custom stereotaxic frame (non-vision-blocking).
- Bilateral V1 craniotomy; 1 × 1 mm durotomy.
- Eyelids sutured open; contact lenses.
- Post-paralysis N₂O:O₂ adjusted to 1:1.
- ECG continuous, body 37 °C.
- Euthanasia: sodium pentobarbital 200 mg/kg i.p., transcardial perfusion (4 % PFA), brain cryo-sectioned on Leica SM2010R; NeuN + DiI electrode-track reconstruction on Keyence BZ-X710.

## Recording hardware / acquisition

| Item | Detail |
|---|---|
| Electrode | Plexon S-probe, 32 channels, 50 µm inter- and intra-tetrode spacing |
| Manipulator | Sutter MP-285 |
| Amplifier / digitizer | Intan RHD2000 |
| Stimulus-timing acquisition | Micro1401 + Spike2 (Cambridge Electronic Design) |
| Spike sorting | JRClust in MATLAB (Jun et al. 2017), offline |
| Electrode-entry angle | 30–45° from cortical surface |
| Min recording depth | 200 µm |
| Spacing between recording sites | electrode advanced ≥640 µm before next site |
| Optic-disk localisation | Heine Omega 600 indirect ophthalmoscope + Volk 78D / 90D lens; wooden-rod triangulation for eye orientation |

## Visual stimuli

- MATLAB + Psychophysics Toolbox; Sony GDM-520 21-inch CRT, 800 × 600, 100 Hz.
- RF manually mapped with drifting-grating patches.
- **Stimulus set 1:** orientation {0, 45, 90, 135°} × SF {0.04, 0.08, 0.16, 0.24, 0.32, 0.64, 0.90, 1.25 cpd} × contrast {0.04, 0.08, 0.16, 0.32, 0.64, 1}, TF fixed at 4 Hz, back-and-forth every 4 cycles, 5 repetitions.
- **Stimulus set 2:** direction {0, 45, …, 315°} × TF {0.5, 1, 2, 4, 8, 16, 32 Hz}, contrast 1, SF fixed at 0.1 cpd, unidirectional, 7 repetitions.
- Trial: 4 s stimulus + 3.5 s gray interstimulus interval; blank control stimulus of same duration per set.

## Key recorded / derived variables

- Spike-sorted single units with F0 and F1 responses per trial.
- **Inclusion criterion:** ANOVA p < 0.05 over stimuli + blank (per stimulus type).
- Orientation selectivity = 1 − circular variance; double-Gaussian fit for preferred angle.
- Direction selectivity = 1 − direction circular variance.
- Spatial- and temporal-frequency preference from Movshon-model fit; L50 / H50 cutoffs; bandwidth = log₂(H50/L50).
- Low-pass index (LPI) = R(TF = 0.5 Hz) / max(R).
- Contrast response: Naka-Rushton fit; sensitivity = 1 / (contrast where response > 5 SD of blank).
- Spontaneous (background) firing rate and response suppression.
- Per-cell metadata: animal ID, hemisphere (contra/ipsi relative to early-opened eye), group (control / EO1contra / EO1ipsi / EO2), depth, preferred stimulus parameters.

## Statistics

Linear mixed-effects models in MATLAB (`fitlme`); fixed effects = treatment group, random effects = animal identity. Per-animal random-effect values reported alongside condition means.

## Data / code availability

- **Raw + processed data (NDI Cloud):** DOI 10.63884/ndic.2025.28xb47y1 (Griswold & Van Hooser 2025). Managed by the Neuroscience Data Interface (García Murillo et al. 2022, RRID:SCR_023368).
- Analysis uses MATLAB + Psychophysics Toolbox + JRClust + `fitlme`; no separate repository cited in the extracted text.

## Relevance for DID/NDI schema design

Direct NDI consumer with a developmental-manipulation twist — valuable for:

- `subject` document: species-specific developmental-timeline fields (natural eye-opening time per eye, P-day at each event, sex restriction rationale, litter ID, jill ID).
- `treatment/intervention` document: manipulation type = "premature eye opening" with per-eye timestamps and forceps method, plus exposure-session metadata (daily duration, number of days, environment description).
- `session` tagging: experimental group (control / EO1 / EO2) and per-cell hemisphere-vs-opened-eye relationship (contra / ipsi).
- `probe/probe_location` with V1 monocular-periphery constraint; electrode-track reconstruction via DiI requires linking a `histology/track_reconstruction` document with NeuN counterstain.
- `stimulus/grating` document must express cross-factor covariation (orientation × SF × contrast in set 1; direction × TF in set 2) with shared blank control; may motivate a `stimulus/factorial_set` schema.
- Derived-analysis docs: `data/fitcurve` with model family (Movshon TF model, Naka-Rushton contrast, double Gaussian orientation), parameter bounds, and cutoff definitions (L50/H50/LPI).
- `statistics/mixed_effects` document: fixed-effect levels, random-effect grouping variable, estimates per level.
