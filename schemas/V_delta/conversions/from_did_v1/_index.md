# did_v1 → V_delta conversion index

This file enumerates every V_delta document type that needs a conversion
doc from `did_v1`, and tracks its status. Update this index whenever a
new conversion doc is added or its status changes.

The corresponding template is [`_TEMPLATE.md`](_TEMPLATE.md). The shared
file-handling rules are in [`_files.md`](_files.md).

## Status legend

- **none** — no conversion doc exists yet
- **drafted** — markdown exists, awaiting domain review
- **reviewed** — domain-reviewed, awaiting implementation
- **applied-in-tooling** — implemented in the migration engine in
  `DID-matlab`, but not yet locked
- **frozen** — implemented, tested against real datasets, locked for
  V_delta
- **no-conversion-needed** — explicitly marked as having no did_v1
  predecessor

## Conversions

| V_delta class_name | did_v1 source | Status | Doc |
|---|---|---|---|
| `contrast_tuning` | NDIcalc-vis-matlab `vision/contrast_tuning` | drafted | [contrast_tuning.md](contrast_tuning.md) |
| `contrast_tuning_calc` | NDIcalc-vis-matlab `calc/contrasttuning_calc` (renamed) | drafted | [contrast_tuning_calc.md](contrast_tuning_calc.md) |
| `contrast_sensitivity_calc` | NDIcalc-vis-matlab `calc/contrastsensitivity_calc` (renamed) | drafted | [contrast_sensitivity_calc.md](contrast_sensitivity_calc.md) |
| `spatial_frequency_tuning` | NDIcalc-vis-matlab `vision/spatial_frequency_tuning` | drafted | [spatial_frequency_tuning.md](spatial_frequency_tuning.md) |
| `spatial_frequency_tuning_calc` | NDIcalc-vis-matlab `calc/spatial_frequency_tuning_calc` | drafted | [spatial_frequency_tuning_calc.md](spatial_frequency_tuning_calc.md) |
| `temporal_frequency_tuning` | NDIcalc-vis-matlab `vision/temporal_frequency_tuning` | drafted | [temporal_frequency_tuning.md](temporal_frequency_tuning.md) |
| `temporal_frequency_tuning_calc` | NDIcalc-vis-matlab `calc/temporal_frequency_tuning_calc` | drafted | [temporal_frequency_tuning_calc.md](temporal_frequency_tuning_calc.md) |
| `speed_tuning` | NDIcalc-vis-matlab `vision/speed_tuning` | drafted | [speed_tuning.md](speed_tuning.md) |
| `speed_tuning_calc` | NDIcalc-vis-matlab `calc/speedtuning_calc` (renamed) | drafted | [speed_tuning_calc.md](speed_tuning_calc.md) |
| `orientation_direction_tuning_calc` | NDIcalc-vis-matlab `calc/oridirtuning_calc` (renamed) | drafted | [orientation_direction_tuning_calc.md](orientation_direction_tuning_calc.md) |
| `reverse_correlation` | NDIcalc-vis-matlab `neuro/reverse_correlation` | drafted | [reverse_correlation.md](reverse_correlation.md) |
| `hartley_reverse_correlation` | NDIcalc-vis-matlab `neuro/hartley_reverse_correlation` | drafted | [hartley_reverse_correlation.md](hartley_reverse_correlation.md) |
| `hartley_calc` | NDIcalc-vis-matlab `calc/hartley_calc` | drafted | [hartley_calc.md](hartley_calc.md) |

## Notes

- **Not migrated:** `stimloopsplitter_calc` (deprecated per domain owner
  decision; not added to V_delta).
- **Already in V_delta from earlier set versions** (no `did_v1` conversion
  added in this PR): `orientation_direction_tuning` (the result type that
  `orientation_direction_tuning_calc` inherits from), `tuningcurve_calc`,
  `stimulus_tuningcurve`, `ngrid`. These have no NDIcalc-vis-matlab v1
  predecessor in `ndi_common/`; if any need a separate `did_v1` source
  resurrected later, add their conversions then.

## Conventions

- One conversion markdown per V_delta document type. If a V_delta class
  has multiple did_v1 sources, document the merge in a single file
  rather than splitting.
- If a V_delta class is genuinely new (no did_v1 ancestor), create
  `<class_name>_no_conversion_needed.md` with a one-line reason and add
  the row with status `no-conversion-needed`.
- File-handling behavior that follows the generic rules in `_files.md`
  should be linked, not restated.
