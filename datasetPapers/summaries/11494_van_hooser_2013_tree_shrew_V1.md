# Transformation of Receptive Field Properties from LGN to Superficial V1 in the Tree Shrew

**Citation:** Van Hooser SD, Roy A, Rhodes HJ, Culp JH, Fitzpatrick D. *J. Neurosci.* 33(28):11494–11505 (July 10, 2013). DOI: 10.1523/JNEUROSCI.1464-13.2013.

**File:** `datasetPapers/11494.full.pdf`

---

## Short description

Extracellular single-unit recordings in the lateral geniculate nucleus (LGN) and primary visual cortex (V1) of anesthetized tree shrews, measuring receptive-field (RF) properties (ON/OFF structure, orientation / direction selectivity, modulation to drifting gratings, spatial and temporal frequency tuning) as a function of laminar position.

## Subjects

| Field | Value |
|---|---|
| Species | Tree shrew (*Tupaia belangeri*) |
| Sex | Either sex (pooled; individual-level sex not broken out) |
| Age | 3 months – 1 year |
| N animals | 14 experiments total (first 6 used tetrodes; subsequent 8 used carbon-fiber electrodes) |
| Sample unit | Single unit recorded extracellularly |

## Procedures / treatments

- **Anaesthesia induction:** ketamine 200 mg/kg i.m. + xylazine 4.7 mg/kg i.m.
- **Intraperitoneal cannula** for later neuromuscular blocker delivery.
- **Tracheostomy**, then mounted in custom stereotaxic frame (non-vision-blocking).
- **Analgesic:** bupivicaine 2.5 mg/ml, 10–30 µL infiltrated along wound margins.
- **Contact lenses** (Platt Contact Lens) for corneal protection.
- **Craniotomy:** 2–4 mm², some experiments with dura intact, others with a pinhole made by 31.5 ga needle.
- **Neuromuscular blocker (maintenance):** pancuronium bromide 0.2 mg/h.
- **Ventilation:** 0.5–2.5 % isoflurane in 1:1 N₂O/O₂.
- **Monitoring:** continuous EKG; isoflurane titrated on EKG distress.
- **End of experiment:** transcardial perfusion (0.9 % saline → 10 % formalin), brains cryoprotected in 20 % sucrose, 50 µm coronal sections on freezing microtome, alternate sections Nissl / cytochrome-oxidase stained.
- **Electrolytic lesions** (5 µA constant current for ~5 s, electrode negative) in some penetrations for post-hoc laminar verification.

## Recording hardware / acquisition

| Field | Value |
|---|---|
| Electrodes | Carbon-fiber (CarboStar-1, Kation Scientific); early experiments: commercial tetrodes (Thomas Recording) |
| Manipulator | Sutter MP-285, 1 µm digital position readout |
| Amplifier | Multichannel Systems preamplifier/amplifier |
| Acquisition | Micro1401 acquisition board + Spike2 software (Cambridge Electronic Design) |
| Spike sorting | Spike2 clustering |
| Layer ID during recording | Cortical “hash” response to ophthalmoscope flashes (0.5 s ON / 0.5 s OFF); LGN layers identified by dominant eye and ON/OFF hash profile |

## Visual stimuli

| Field | Value |
|---|---|
| Stimulus software | Psychophysics Toolbox in MATLAB (Macintosh G3, OS9) |
| Display | Sony GDM-520 CRT; white point x = 0.291, y = 0.307; mean luminance 54 cd/m² |
| Stimulus types | Drifting sinusoidal gratings; flashed thin (0.25–0.5°) black/white bars ≥20° long, 3–7 Hz flash rate, on gray background |
| Coarse orientation sweep | 80 % contrast, 0.2 cpd, 4 Hz, 10° circular aperture, 30° steps pseudorandom |
| Fine orientation sweep | 22.5° steps at preferred spatial / temporal frequency |
| SF / TF sweeps | Sinusoidal gratings at preferred orientation |
| Bar mapping | Bar center varied in 0.25–0.5° steps orthogonal to preferred orientation; contrast = black or white on gray |

## Key recorded / derived variables (per neuron)

Stored per unit:

- **Anatomical:** brain region (LGN vs V1), LGN layer (1, 2, 3, 4, 5, 6), V1 layer (4A / 4B / 2–3A / 3B / 3C / 5–6), cortical depth (µm; also normalised to "standard cortex" coordinates: layer 2/3 = 0–900 µm, layer 4 = 900–1300 µm, layer 5/6 = 1300–2200 µm).
- **Spike trains** around each stimulus presentation.
- **Tuning curves:** orientation, direction, spatial frequency, temporal frequency, contrast (subset).
- **Derived indices:**
  - ON/OFF index = max(R_ON)/(max(R_ON)+max(R_OFF))
  - ON/OFF segregation index (custom, SE-thresholded)
  - Sign index = |max(R_ON)−max(R_OFF)| / (max(R_ON)+max(R_OFF))
  - Orientation selectivity (1 − circular variance)
  - Direction selectivity (1 − directional circular variance)
  - Modulation index = 2·F1/(F0+F1)
  - SF / TF: low-cutoff, preferred, high-cutoff (half-max of difference-of-Gaussians fit) plus low-pass / band-pass / high-pass classification.

## Analysis code / software

- MATLAB with custom software from Heimel et al., 2005 and Van Hooser et al., 2006.
- Psychophysics Toolbox (Brainard 1997; Pelli 1997).
- Difference-of-Gaussians (DOG) fits for SF / TF.
- Statistics: Kruskal–Wallis with Bonferroni correction; χ² for frequency comparisons; α = 0.05.

## Sample sizes

- LGN: 27 neurons analysed (layers 1, 2, 4, 5).
- V1 layer 4: 21–23 neurons.
- V1 layer 2/3: 44 neurons.
- Few infragranular (L5/6) recordings.

## Metadata necessary for reuse

1. Subject: species, age, sex, weight (if recorded), health status, eye dominance mapping between geniculate layers.
2. Session: anaesthesia drugs + doses, time points, isoflurane level trace, EKG trace, paralysis start time.
3. Probe: electrode type (carbon fiber vs tetrode), impedance, insertion coordinates, manipulator depth trace.
4. Layer assignment: hash-based transition depths (ON onset, ON→OFF, OFF disappearance, white matter), post-hoc histological lesion coordinates where available.
5. Stimulus: monitor geometry (distance, pixel size, gamma), mean luminance, contrast, spatial and temporal frequency, orientation sequence (including pseudorandom seed), bar width / length / polarity / position list, trial count per condition.
6. Spike data: waveform, cluster quality, spontaneous rate ("blank" condition response).
7. Histology: section thickness, stain (Nissl / CO), lesion markers, reconstructed electrode track.

## Data products (implicit — not deposited per paper)

No public repository is cited. Data are summarised in figures (tuning curves, laminar scatter plots, histograms) but raw spike trains and stimulus logs are referenced only by custom MATLAB analyses in the authors' lab.

## Relevance for DID/NDI schema design

This paper exercises nearly the full sensory-electrophysiology stack and is a good stress test for:

- `subject` (species / age / sex) — including non-rodent, non-primate species.
- `probe` + `probe_location` — multi-electrode types (carbon fiber, tetrode) used in the same dataset.
- Laminar assignment document: LGN layer (ordinal 1–6), V1 layer (enum 4A / 4B / 2–3A / 3B / 3C / 5 / 6), cortical depth (µm), normalised "standard cortex" depth.
- `stimulus_presentation` + `stimulus_parameter` for bars (length, width, position, polarity) and gratings (SF, TF, orientation, contrast, aperture).
- `stimulus_tuningcurve` / `stimulus_response_scalar` for all indices above.
- `data/fitcurve` for DOG fits of SF and TF curves (peak, low / high cutoffs, bandwidth).
- Histology / lesion document for electrolytic markers and section staining metadata.
- Drug / treatment document for anaesthetic regimens (ketamine, xylazine, isoflurane, bupivicaine, pancuronium) with dose / route / timing.
