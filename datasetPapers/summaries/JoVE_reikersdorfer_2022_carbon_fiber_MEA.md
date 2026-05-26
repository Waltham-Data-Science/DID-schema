# Construction and Implementation of Carbon Fiber Microelectrode Arrays for Chronic and Acute In Vivo Recordings

**Citation:** Reikersdorfer KN*, Stacy AK*, Bressler DA, Hayashi LS, Hengen KB, Van Hooser SD. *J Vis Exp* (DOI: 10.3791/62760). Author manuscript available in PMC 2022 Mar 16. (*equal contribution.*)

**File:** `datasetPapers/Construction and Implementation of Carbon Fiber Microelectrode Arrays for Chronic and Acute In Vivo Recordings.pdf`

## Short description

A JoVE protocol paper describing step-by-step fabrication and implantation of custom 16- and 64-channel carbon fiber electrode arrays (CFEAs) for acute and chronic single-unit extracellular recordings. Representative electrophysiology is shown from **one adult female ferret (acute, V1, 16 ch)** and **one adult male mouse (chronic, retrosplenial cortex, 64 ch)**.

## Subjects

| Field | Ferret (acute) | Mouse (chronic) |
|---|---|---|
| Species | *Mustela putorius furo* | *Mus musculus* |
| Sex | Female | Male |
| Age | Adult | Adult |
| N | 1 (representative) | 1 (representative) |
| Behavioral state | Anaesthetised, non-survival | Freely behaving |
| Target region | Primary visual cortex (V1) | Retrosplenial cortex |

Impedance aggregate stats: N = 48 electrodes, 12.96 ± 2.74 connected channels per 16-ch array (connected defined as post-plating impedance < 4 MΩ).

## Procedures / treatments

**Mouse (survival surgery):**
- Induction: 2.5 % isoflurane, maintenance 2.0 % via nose cone; target respiration 60 breaths/min; 37 °C heating pad.
- Eye ointment, toe-pinch anaesthesia check.
- 4 × 4 mm craniotomy (0.8 mm burr), contralateral burr hole for stainless-steel ground screw + silver ground wire.
- Post-op: antibiotic ointment, 2–5 day single-housed recovery, 0.5–1.0 mg/kg sustained-release buprenorphine on surgery day.

**Ferret (non-survival):**
- Induction: ketamine 20 mg/kg i.m., then 1.0–2.0 % isoflurane in 2:1 N₂O:O₂ via mask.
- Tracheostomy; ventilation at 1.0–2.0 % isoflurane; 37 °C heating pad.
- Monitoring: HR, end-tidal CO₂, respiration (3.5–4.0 %), continuous ECG with isoflurane titration on distress.
- 4 × 4 mm craniotomy; Ag/AgCl reference pellet inserted between skull and contralateral muscle.
- Terminal: 1 mL pentobarbital sodium + phenytoin sodium.

**Implantation (both species):**
- Aseptic technique per IACUC / ASC (autoclave 135 °C, 15 min; 70 % ethanol on stereotax).
- Durotomy with dura pick; pia nicked with metal microelectrode (ferret) or CFEA + dura pick (mouse).
- Electrode lowered at ~2 µm/s under stereo microscope; 30-min settle for acute; UV-cured dental-cement headcap for chronic; 5-0 sutures.

## CFEA fabrication parameters (essential for reuse)

- 7 µm commercial carbon fibers, cut to 8 cm, epoxy baked off at 400 °C × 6 h.
- Parylene C coating, 2.3 g per run (≈1 µm), vacuum deposition chamber, ~2 h.
- 20–30 fibers per 3D-printed / laser-cut cassette, 2–3 mm spacing; 10 cassettes/box, 2 holders/chamber.
- Bundle diameter (16-ch): ~26 µm.
- Gold electroplating: −0.05 µA, 30 s, 5 s pause; final impedance < 0.2 MΩ (PBS).
- Silver paint channel fill, UV-cured dental cement headstage mount, 24 h cure before use.

## Recording hardware / acquisition

- Headstage connected to commercial acquisition system (see JoVE Table of Materials).
- Spike sorting with commercial spike-sorting software (cited in Table of Materials; specific tool not named in body text).
- Demonstrated stability: single units discernible up to ≥120 days (chronic mouse); example of 4 single units at 11 months post-implantation.
- Acute ferret: 16-channel recording in V1 within ~30 min of implantation settle.

## Data / code availability

- **No dataset deposited.** Only representative traces shown in Figures 6 (mouse chronic) and 7 (ferret acute).
- Video protocol available at DOI 10.3791/62760.
- Jig, cassette, and headstage adapter designs referenced but not explicitly linked to a public repository in the extracted text.

## Relevance for DID/NDI schema design

Excellent test case for **probe-construction provenance** documents, which the current schemas gloss over:

- `probe` document needs: construction method ("custom carbon fiber" vs commercial), fiber diameter, coating material + thickness, electroplating material + parameters (current, duration, pulse pattern), channel count, bundle diameter, headstage adapter model, per-channel impedance (pre- and post-plating) and connection state.
- `probe_location` must support cross-species implant coordinates (mouse retrosplenial cortex, ferret V1), with distinct reference-electrode documents (ground screw vs Ag/AgCl muscle pellet).
- `subject` document must distinguish survival vs terminal preparations and link to IACUC protocol ID.
- `surgery` / `anaesthesia` document type: per-species drug regimen (ketamine, isoflurane, N₂O/O₂, buprenorphine, pentobarbital+phenytoin), monitoring variables (HR, ETCO₂, respiration, ECG), body temperature target, recovery regimen.
- `session` should distinguish acute (settle time, duration) vs chronic (days-since-implant, longitudinal session linkage).
- Impedance measurements are a recurring per-channel time-series — argues for a dedicated `probe/impedance_measurement` document rather than embedding in `probe`.
