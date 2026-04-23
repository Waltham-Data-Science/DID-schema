# Extracellular Vesicles Aid in the Transfer of Long-Term Associative Memory Between *Caenorhabditis elegans*

**Citation:** Bhar M, Nandi T, Narayanan H, Kishore K, Babu K. *bioRxiv* 2025.02.26.640282, posted June 13, 2025 (preprint; CC-BY-NC-ND 4.0). DOI: 10.1101/2025.02.26.640282.

**File:** `datasetPapers/Extracellular vesicles aid in the transfer of long-term associative memory between Caenorhabditis elegans.pdf`

## Short description

Behavioral + fluorescence-imaging + LC-MS study in *C. elegans* (and *C. briggsae*) testing whether long-term associative memory (LTAM), formed by pairing heat with a volatile chemoattractant, is transferred between individuals via extracellular vesicles (EVs) released onto the culture plate. Includes cross-species exchange assays and EV-release-deficient mutants (`klp-6`, `cil-7`, `daf-22`).

## Subjects

| Field | Value |
|---|---|
| Organism | *C. elegans* (wild-type N2 Bristol) and *C. briggsae* |
| Developmental stage | Young adult hermaphrodite, synchronised (egg / L1 removed) |
| Standard rearing | NGM plates seeded with OP50 *E. coli*, 22 °C |
| Plate format | 60 mm diameter (training and transfer) |
| N per replicate | 8–10 worms (chemotaxis); 4–7 worms (imaging); ~70 worms/plate × 4 plates per LC-MS sample; 30–35 worms (chemical supplementation) |
| Replicate structure | 3–6 biological replicates per condition, each run across multiple days with all conditions side-by-side |

Strains and genotyping primers are listed in **Supplementary Tables S1 (strains) and S2 (primers)**. Mutant alleles used include `klp-6`, `cil-7 (tm5848)` (from NBRP Japan), `daf-22`, and `crh-1`; `Pklp-6::GFP::KLP-6` rescue construct gifted from Maureen Barr lab.

## Procedures / treatments

**Training paradigm (Dahiya et al. 2019, with minor modifications):**
- Simultaneous exposure to heat + chemoattractant (IAA, diacetyl, or heptanone) for 2 min.
- 10-min rest at 22 °C.
- Cycle × 5.
- Rest 20 h at 22 °C.
- LTAM read out at 20–24 h.
- Concentrations of odorants per Dahiya et al. 2019 and Zhang et al. 2016.

**Behavioral readout:**
- Chemotaxis index (CI) = displacement along odorant gradient / total distance traveled.
- Videos tracked in FIJI with Trackmate plugin.

**Exchange assay:**
- Naïve worms transferred to plate formerly holding trained worms (and vice versa) within 30 min of training; CI measured 20–24 h later.
- Cross-species variant: naïve *C. elegans* ↔ trained *C. briggsae*.

**Imaging:**
- Young adult hermaphrodites mounted on 1 % agarose pads with 34 mg/mL 2,3-butanedione monoxime (BDM) in M9.
- Zeiss Apotome, 63× oil, Z-stacks, within 4 h of training.
- FIJI "Analyze Particles" for cell-body mean grey value + puncta count along neuronal processes.

**LC-MS of EVs:**
- 4 × 60 mm plates, ~70 worms each per sample (naïve, trained, IAA-only, heat-only, and EV-release mutants).
- Differential centrifugation: 3000 × g 15 min 15 °C (pellet worms + bacteria) → 10 000 × g 30 min 4 °C × 3.
- Supernatant sent to IISc LC-MS facility.
- Triplicates across multiple days.

**Chemical supplementation:**
- 300 µL of 100 mM imazapyr (Sigma 37877), 2-methoxy-5-methyl aniline (Sigma 103284), or SGCDC sodium salt (SRL 97971) on unseeded NGM; or cocktail (100 µL each at 100 mM).
- OP50 seeded after chemical dried.
- 30–35 synchronised naïve young adults per plate; CI tested at 3.5 h and 6 h post-supplementation.

## Statistics

GraphPad Prism 8; Grubbs outlier test (α = 0.05); one-way ANOVA with Dunnett's correction (some plots with Sidak's for within-group comparisons); p ≤ 0.05 significance threshold.

## Data / code availability

- **No public data deposit cited** in the methods, results, or acknowledgements of the extracted text.
- LC-MS raw spectra processed by the IISc Mass Spectrometry Facility — no accession number given.
- Supplementary Tables S1 (strains) and S2 (primers) referenced; not extracted here.
- Training paradigm and track-analysis code rely on FIJI + Trackmate (open source, no custom code linked).
- RNA sequencing was performed (acknowledged) but no accession is cited in the extracted sections.

Reuse of this dataset would require the authors' supplementary material for strain list, primer sequences, raw tracking videos, LC-MS spectra, and the raw imaging Z-stacks — all of which are referenced but not deposited in the extracted text.

## Relevance for DID/NDI schema design

Non-mammalian model; no electrophysiology; stress-tests a different stack than the tree-shrew / rat papers:

- `subject` must support invertebrate multi-animal groups (plate population rather than a single subject), plus developmental-stage enums (young adult hermaphrodite) and synchronisation protocol metadata.
- `subject_group` / `cohort` document: plate ID, worm count, strain genotype, source (CGC, NBRP, lab-generated transgenic), allele identifiers.
- `stimulus`/`treatment` generalises to paired chemical + heat sequences with cycle structure (2 min pair × 5 with 10 min rest); useful test for cyclic training-paradigm schema.
- `behavior/chemotaxis` document: plate geometry (60 mm), odorant identity + concentration, gradient source, scoring window, CI formula, Trackmate version/parameters.
- `imaging` document must carry live-mount details (agarose %, BDM concentration, M9 buffer) and objective/Z-stack parameters.
- `data/massspec` document (new type) for LC-MS on EV fractions with centrifugation provenance (speed, duration, temperature, rounds).
- `data/fluorescence_quantification`: ROI selection method, threshold, "Analyze Particles" parameters.
- Highlights that `depends_on` / `subject_identifier` must support *group-level* rather than individual-level linkage for populations.
