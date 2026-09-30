#!/bin/sh
# Appends the drafted sign-off lines to their plan documents. Run from the DID-schema root,
# by the signer. Each .txt names its target: review/73/signoff/X.txt -> schemas/X.md
set -e
for f in review/73/signoff/*.txt; do
  doc="schemas/$(basename "$f" .txt).md"
  [ -f "$doc" ] || { echo "missing $doc"; exit 1; }
  printf '\n' >> "$doc"; cat "$f" >> "$doc"
  echo "appended $(grep -c '^TEAM-SIGN-OFF' "$f") line(s) to $doc"
done

# The ledger's signature-join test pins the counts the signatures move: `derived`
# 40 -> 49 (the 8 spatial rows + `calculator` now join through signed families) and
# rows reading `signed` 48 -> 57. Update the pins with the reason beside them.
python3 - <<'PY'
p = "tests/test_coverage_signature_join.py"
s = open(p).read()
a = "        self.assertEqual(derived, 40)\n"
b = "        self.assertEqual(self.gov[\"by_state\"][coverage.G_SIGNED], 48,\n"
assert s.count(a) == 1 and s.count(b) == 1, "signature-join pins moved; update by hand"
s = s.replace(a, "        # derived 40 -> 49 and signed 48 -> 57 on 2026-09-29: jess signed\n"
                 "        # [spatial_transcriptomics_family] and [calculator mixin dropped (#73)],\n"
                 "        # so the 8 spatial rows and `calculator` join through signed families.\n"
                 "        self.assertEqual(derived, 49)\n")
s = s.replace(b, "        self.assertEqual(self.gov[\"by_state\"][coverage.G_SIGNED], 57,\n")
s = s.replace("\"9 transcribed + 40 derived, less `ngrid`, whose \"",
              "\"9 transcribed + 49 derived, less `ngrid`, whose \"")
open(p, "w").write(s)
print("updated the signature-join pins in", p)
PY
echo "now run: python3 tools/gates.py   (expect 28 of 28)"
