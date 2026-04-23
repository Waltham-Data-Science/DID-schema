# Vasopressin and Oxytocin Excite BNST Neurons via Oxytocin Receptors, Which Reduce Anxious Arousal

**Citation:** Francesconi W, Olivera-Pasilio V, Berton F, Olson SL, Chudoba R, Monroy LM, Krabichler Q, Grinevich V, Dabrowska J. *Cell Reports* 44:115768 (June 24, 2025). DOI: 10.1016/j.celrep.2025.115768.

**File:** `datasetPapers/CELREP115768_grabs 1..1.pdf`

## Short description

Slice electrophysiology, viral tract tracing, peptide optogenetics, and chemogenetics in male rats to test how AVP and OT act on dorsolateral BNST (BNSTDL) neurons, and how OTR-BNST neurons regulate fear-potentiated startle (FPS) and elevated-plus-maze (EPM) behaviour.

## Subjects

- **Species / sex:** male rats only (no females).
- **Strains:** wild-type Sprague-Dawley (Envigo, RRID:MGI:5651135); OTR-Cre, AVP-Cre (Grinevich lab, Heidelberg; knock-in); CRF-Cre (Messing lab, UT Austin; Wistar background).
- **Age / weight:** 60–90 days; SD 240–300 g, transgenics 220–400 g.
- **Housing:** groups of 3, 12 h light/dark (lights on 07:00), ad lib food/water, ≥1 week habituation.
- **Approximate Ns:** 92 OTR-Cre, 26 CRF-Cre, 83 AVP-Cre for AAV surgeries; 45 OTR-Cre for FPS/EPM; 27 SD for BNST cannulation.

## Procedures / treatments

- **Drugs (ephys bath):** AVP 0.2 µM, OT 0.2 µM, TGOT 0.4 µM, FE201874 0.2–0.4 µM, d[Cha4]-AVP 1 µM; antagonists OTA 0.4 µM, SR49059 5 µM, Nelivaptan 1 µM, Manning compound 1 µM; synaptic blockers CNQX 10 µM, D-AP5 50 µM, PTX 25 µM; CNO 20 µM (ephys) / 2 mg/kg i.p. (behavior).
- **Intra-BNST infusion:** AVP 10 ng/0.5 µL per hemisphere vs saline vehicle.
- **Stereotaxic AAVs:** hSyn-DIO-hM4Di-mCherry, hSyn-FLEx-mGFP-synaptophysin-mRuby, EF1a-DIO-ChR2-eYFP, OTp-ChR2-mCherry. Coordinates (from bregma): BNSTDL AP 0.0, ML ±3.4, DV −7.1 (15° coronal); SON, SCN, PVN coordinates given.
- **Cannulation:** 22 ga guide, AP 0.0, ML ±3.4, DV −5.1; Chicago Blue dye placement check.
- **Optogenetics:** 470 nm, 10 ms pulses; tetanic 30 Hz × 20 s; SCN/SON 10 Hz × 20 s; PVN four bursts × 15 s at 6.3 Hz every 30 s.
- **Behavior:** 5-day FPS paradigm (habituation; pre-shock; conditioning with 3.7 s cue light + 0.5 s 0.5 mA foot-shock × 10; cued/non-cued recall in context B; contextual recall in context A; extinction); EPM 5 min (ANY-Maze 6.34).

## Recording / acquisition

Whole-cell patch-clamp on 300 µm coronal BNST slices; Multiclamp 700B + pCLAMP11 + NI USB-6251 at 10 kHz; custom MATLAB scripts (Desai, NIH). Pipette solution: K-gluconate 135, KCl 2, MgCl₂ 3, HEPES 10, Na-phosphocreatine 5, ATP-K 2, GTP-Na 0.2 mM. Neurobiotin 0.1 % for morphology; streptavidin-Alexa 488/594 post-hoc. Startle: SR-Lab; 95 dB WNB; 200 ms jump-amplitude window.

## Key recorded variables

RMP, Rin, rheobase, 1st-spike threshold (dV/dt > 5 mV/ms), 1st-spike latency, steady-state firing vs injected current (I/O), cell type (I/II/III by Ih, post-inhibitory spike, IKIR/ID signatures). Behavioral: jump amplitude, cued/non-cued/contextual fear % change, EPM entries / time / freezing per compartment.

## Data and code availability

- **Raw ephys (MATLAB) + behavior (CSV):** ndi-cloud.com/datasets/67f723d574f5f79c6062389d — DOI 10.63884/ndic.2025.jyxfer8m (NDI-Cloud accession 67f723d574f5f79c6062389d).
- **Acquisition/analysis MATLAB code:** Zenodo DOI 10.5281/zenodo.15238413.
- **Microscopy:** on request from lead contact.

## Relevance for DID/NDI schema design

Directly consumes NDI-Cloud and is a strong stress-test for: `subject` (transgenic line + genotyping primers + breeder source); `treatment/drug` (bath concentration + route + timing + washout); `stereotaxic_injection` (viral construct + Addgene ID + coordinates + angle + volume + rate); `cannulation`; `optogenetic_stimulation` (wavelength, pulse width, frequency, burst pattern); `slice_electrophysiology` (aCSF composition, pipette solution, temperature, Ra cutoff); cell-type classification document (types I/II/III with ionic-current signatures); `behavior/FPS` and `behavior/EPM` protocol documents with trial structure and apparatus metadata; `histology` with antibody RRIDs and confocal Z-stack parameters.
