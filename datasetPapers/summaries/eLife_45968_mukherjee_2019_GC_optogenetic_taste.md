# Impact of Precisely-Timed Inhibition of Gustatory Cortex on Taste Behavior Depends on Single-Trial Ensemble Dynamics

**Citation:** Mukherjee N, Wachutka J, Katz DB. *eLife* 8:e45968 (June 24, 2019). DOI: 10.7554/eLife.45968.

**File:** `datasetPapers/elife-45968-v2.pdf`

## Short description

In awake rats with intra-oral cannulas (IOCs), the authors simultaneously recorded bilateral gustatory cortex (GC) single-unit and jaw EMG activity while optogenetically silencing GC (ArchT) for either 0.5 s (early / middle / late, aligned to taste delivery) or 2.5 s (whole trial). Hidden ensemble-state change-point analysis is combined with behavioural gape detection to test whether perturbation effects on gaping depend on the per-trial timing of the identity→palatability ensemble transition.

## Subjects

| Field | Value |
|---|---|
| Species | *Rattus norvegicus* (Long-Evans), adult female |
| N (primary) | 5 rats |
| N (re-analysed controls) | 10 rats from Sadacca et al. 2016 and Li et al. 2016 |
| Weight | 275–300 g at virus injection; 300–350 g at implant |
| Housing | Individual cages, 12 h:12 h light cycle, ad libitum food/water pre-surgery; mild water restriction (20 mL/day) once habituation began |
| Welfare | Weight kept ≥80 % pre-surgery throughout; Brandeis IACUC |

## Procedures / treatments

**Surgery 1 — AAV injection (4–6 weeks pre-implant):**
- Ketamine/xylazine (1 mL ketamine + 0.05 mL xylazine / kg i.p.); skull leveled in stereotax.
- Bilateral GC craniotomies at AP +1.4, ML ±5.0 (from bregma, Paxinos & Watson 2007).
- Virus: AAV9-CAG-ArchT-GFP (2.5 × 10¹¹ particles/mL), mixed with Oregon Green 488 tracer.
- Nanoject III injector; glass micropipette (10–20 µm tip).
- 3 depths per hemisphere: DV −4.9, −4.7, −4.5 mm from dura; 44 pulses × 25 nL / depth; 7 s between pulses; 1.1 µL total / depth.
- Post-injection: Kwik-Sil seal, scalp suture, meloxicam 0.04 mg/kg, saline, Pro-Pen-G 150 000 U/kg.
- 4–6 week recovery.

**Surgery 2 — opto-trode + IOC + EMG implant:**
- Bilateral opto-trode bundle per hemisphere: 30 or 32 microwires (0.0015″ formvar-coated nichrome) + 1 optical fiber (0.22 NA, 200 µm core, 2.5 mm ferrule, Thorlabs). Microwire tips 0.5 mm ventral to fiber tip.
- Custom 3D-printed microdrive; custom San Francisco Circuits interface board; 32-ch Omnetics connector.
- Lowered to DV 4.3 mm from dura.
- EMG: PFA-coated stainless steel wire × 2 inserted into anterior digastric muscle (opposite side from IOC) via suture-needle channeling.
- IOC: thin polyethylene tubing through masseter, past the zygomatic arch, out the scalp — right side only; plastic connector cemented.
- Post-op: buprenorphine 0.05 mg/kg + saline + Pro-Pen-G; 7 days to 90 % pre-surgery weight.

**Habituation:** 3 days of 100 × 40 µL distilled-water pulses (15 s ISI). Opto-trode advanced 0.075 mm per session; cumulative 0.2 mm by end of habituation.

## Stimuli and trial structure

- **Tastes (4):** 30 mM sucrose (Dil Suc), 300 mM sucrose (Conc Suc), 0.1 mM quinine-HCl (Dil Qui), 1 mM quinine-HCl (Conc Qui).
- **Delivery:** pressurized polyamide tubes into IOC under slight N₂ pressure; 40 µL per pulse; ~5 mL total per session.

**Session types:**

| Session | Trials | Structure |
|---|---|---|
| 0.5 s perturbation | 128 total (16 sets × 8 trials); 4 sets/taste: no-laser / early (0–0.5 s) / middle (0.7–1.2 s) / late (1.4–1.9 s) | Pseudo-random order |
| 2.5 s perturbation | 120 total (8 sets × 15 trials); 2 sets/taste: laser-off / laser-on (0–2.5 s) | Pseudo-random order |

- Counterbalanced order: 12 rats 2.5 s first then 0.5 s; 12 rats vice versa.
- Laser: 532 nm DPSS (Laserglow), calibrated to 40 mW at fiber tip; via FC/PC patch cables; Thorlabs ferrules. Illumination sphere ~1 mm³.
- Trial sequencing controlled by Raspberry Pi.
- After each session opto-trode advanced 0.075 mm.

## Acquisition

- Intan RHD2132 (32-channel ADC), 30 kHz sampling, 0.1 Hz–20 kHz bandwidth for both neural and EMG channels.
- Faraday-caged behavior chamber.
- Post-hoc DC current 7 mA × 7 s through selected microwires to mark electrode tips.

## Histology

- Ketamine/xylazine overdose → transcardial 0.9 % saline → 10 % formalin.
- 7-day post-fix in 30 % sucrose + 10 % formalin.
- 50 µm coronal sections on freezing microtome.
- Rinses 3 × PBS; permeabilise in 0.3 % Triton X-100 + 1 % donkey serum in PBS × 2 h RT.
- Primary: 1:500 rabbit anti-GFP (Life Technologies), 12 h 4 °C.
- Secondary: 1:200 Alexa Fluor 488 donkey anti-rabbit IgG, 12 h 4 °C.
- Mount: Fluoromount Aqueous; imaged on Keyence fluorescence microscope to confirm infection + opto-trode placement.

## Spike sorting and derived variables

- Semi-supervised spike sorting: 300–3000 Hz bandpass → Gaussian Mixture Model clustering → manual refinement.
- Code: `blech_clust` on GitHub (https://github.com/narendramukherjee/blech_clust, commit 59088cc; archived copy at elifesciences-publications).
- Per neuron × trial: spike trains, tastes (4), perturbation condition (2–6 levels), EMG trace.
- **Gape detection:** Bayesian Spectrum Analysis (BSA) of EMG, with thresholds validated against manual annotation.
- **Change-point model:** categorical HMM with 3 states (detection / identity / palatability) run on 1.5 s windows, 10 ms bins; inference via modified EM ("hard" E-step) to avoid label-switching.

## Statistics

- Bayesian hierarchical models in PyMC3; NUTS sampler; Gelman-Rubin R̂ ∈ [0.99, 1.01]; 95 % credible intervals as significance tests.
- Hierarchical Poisson GLM for firing × taste × perturbation × interaction.
- Regression of standardized (z-scored) single-unit firing on palatability ranks (Conc Qui = 1, Dil Qui = 2, Dil Suc = 3, Conc Suc = 4) in 250 ms bins / 25 ms step.
- Logistic-sigmoid fit of β_palatability(t), deriving upper asymptote L, slope k, inflection t₀, and peak latency t_peak = (ln 19)/k + t₀.

## Data / code availability

- **Data:** HDF5 files hosted on Brandeis University LTS `katz-lab` share (`files.brandeis.edu`). Access **by request** to Donald Katz (dbkatz@brandeis.edu). Not a public open-access DOI.
- **Code:** `blech_clust` spike sorter on GitHub (link above) + Bayesian analysis code implicitly released with PyMC3 models (no separate repo cited in extract).

## Relevance for DID/NDI schema design

Excellent stress test for the interplay of **multiple parallel data streams** on the same subject/session:

- `subject` document: rat + sex + weight-trajectory constraint (≥80 % pre-surgery).
- `stereotaxic_injection` document must carry multi-depth, multi-pulse AAV protocols with per-pulse volume / inter-pulse interval and tracer (Oregon Green 488) metadata.
- `probe` + `probe_location` with custom opto-trode geometry: microwire offset from fiber tip, per-channel position within bundle, microdrive displacement history (per-session advance; total distance moved).
- `implant/IOC` document (new): cannula material, insertion route, per-side hardware (IOC right, EMG left).
- `emg` document: muscle identity (anterior digastric), electrode type, per-channel position; linked to a `behavior/gape` detection document with BSA parameters.
- `optogenetic_perturbation` (extension of `stimulus`): wavelength (532 nm), power at tip (40 mW), duration (0.5 s / 2.5 s), onset relative to event, pulse pattern.
- `stimulus/intra_oral_taste`: solute (sucrose / quinine-HCl), concentration, volume, pressure source, IOC flush/prime state.
- `trial` document needs first-class support for trial-type × taste × perturbation factorial structure and within-session counterbalancing.
- `analysis/change_point_model`: HMM state priors, inference algorithm (EM with hard E-step), window alignment for perturbation trials.
- `analysis/bayesian_fit`: prior distributions, sampler (NUTS), R̂ convergence diagnostics, credible-interval reporting.
- Data-availability pattern (institutional guest-account access) is a useful negative example: DID/NDI schemas should capture not just DOI deposits but also access-by-request provenance (`data_access` document: method = "contact", URL, institution, lead contact).
