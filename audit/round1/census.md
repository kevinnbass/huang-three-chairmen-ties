# Independent offline FEC census

The authoritative census is `census_v3.py` with `census_v3_results.json`, `census_v3_check.py` / `census_v3_checks.json`, and `census_identity.py` / `census_identity.json`. Earlier numbered and unnumbered census outputs are preserved intermediate attempts, not additional findings. No network was used. Every individual name stayed in process memory.

The script independently derives sitting-candidate links from `members_network.csv` and the three FEC committee/candidate ZIPs, then unions the rule-authorised evidence-set keys. It uses IND, a case-insensitive company prefix, non-X memo code, positive amount, and date since 2025-01-01. Bulk is the baseline. Committee plus transaction ID identifies later-filing replacements; eligible API-only lines are added. Earlier Banks originals are read from the saved C05 capture identified by the pack notes. The JFC test uses **committee designation J**, not committee type. No committee is assigned to a member merely because the committee name resembles the member’s name.

## 1. The three members

| Member | Employer prefix | Lines | Dollars | People | Builder lines / dollars / people |
| --- | --- | --- | --- | --- | --- |
| Mast | Anthropic | 6 | $43,000 | 5 | 6 / $43,000 / 5 |
| Mast | Nvidia | 0 | $0 | 0 | 0 / $0 / 0 |
| Moolenaar | Anthropic | 5 | $28,000 | 4 | 5 / $28,000 / 4 |
| Moolenaar | Nvidia | 0 | $0 | 0 | 0 / $0 / 0 |
| Crawford | Anthropic | 2 | $7,000 | 1 | 2 / $7,000 / 1 |
| Crawford | Nvidia | 0 | $0 | 0 | 0 / $0 / 0 |

Every member/company SUB_ID set equals the builder’s set. Auditor-only SUB_IDs: none. Builder-only SUB_IDs: none. This is a census, including all zero cells; positive controls reproduce the Anthropic cells and explicit rejection controls exercise both company prefixes and every eligibility exclusion.

The exact included IDs are:

- Mast, Anthropic: 4012320261303383685, 4071620261534553098, 4071620261534553107, 4102920261615705077, 4102920261615705306, 4102920261615705790.
- Moolenaar, Anthropic: 4010820261300483823, 4081120261570806015, 4081120261570806044, 4081120261570806049, 4081120261570806057.
- Crawford, Anthropic: 4120820251297390035, 4120820251297390036.

Nvidia has no qualifying IDs for any of the three. That negative is bounded to the saved files, dates, prefixes and keyed committees. The headline sum is $43,000 + $28,000 + $7,000 = $78,000. Mast’s $43,000 consists of $26,000 to Mast for Congress and $17,000 to Mast Victory Committee. The latter attribution is authorised by the supplied key table but not independently established by CCL/CM/CN alone; see the sample below.

## 2. All 535 members

| Employer prefix | Members reached / 535 | Dollars | Lines | People | Member parties |
| --- | --- | --- | --- | --- | --- |
| Anthropic | 134 | $3,481,696 | 660 | 65 | 82 D / 51 R / 1 I |
| Nvidia | 63 | $155,789 | 510 | 77 | 58 D / 3 R / 2 I |

Both totals match `employee_gift_rates.csv`, as do the complete SUB_ID/member sets in `employee_gifts.csv`. Across the entire census, auditor-only and builder-only sets are empty for both companies. `census_v3_checks.json` compares committee, date, amount and employer on every counted line. It records only two field discrepancies: SUB_IDs **4080720261570548076** and **4080720261570548077** say **ANTHROPIC PBC** in each saved earlier capture, while the figure’s employee table and congress rows HM1068/HM1069 say **ANTHROPIC**. Both qualify under the prefix rule; amounts and totals do not change.

Names are counted after uppercasing, removing honorifics, and standardising surname punctuation/spacing. Nvidia yields 78 normalised name forms. The 77-person result is supported by one compatible added-middle-name variant: SUB_IDs **4120220251296455322** and **4060820261520441554** have matching city, state, postal code, employer and occupation in the originals. `census_identity.json` records those comparisons without either name. Anthropic yields 65 normalised names without that further consolidation. The three members’ donor counts also match independently.

The party arithmetic in the figure is incomplete: the Anthropic recipient members include one independent and Nvidia’s include two. Mast is 26th by total dollars; Crawford is 89th. Five members have $28,000, with 45 above them: Moolenaar is joint 46th by dollars. The drawn 47 is an ordinal within a tied group, not a distinct monetary rank.

API reconciliation: Anthropic has 51 counted API-only lines plus 8 later-filing replacements and 9 earlier Banks lines; Nvidia has 21 counted API-only lines and no counted replacement or earlier-capture restoration. These reproduce the methodological counts in the footnote. Bulk integer-dollar precision is retained where the bulk copy stands.

## 3. Committee-key sample and reverse search

The sample has all four key rows for the three chairmen, plus 36 rows selected without replacement using Python `random.Random(20261113)`, in the frozen table’s order. All 40 committee IDs exist in CM26. Twenty-five are linked by CCL26 to the intended sitting candidate and confirmed as principal committees by CN26. Fifteen are leadership/JFC keys for which these three FEC files do not establish the attributed member. No sampled FEC link positively contradicts the named member. **That is not a verification of the 15 unsupported-by-CCL assignments.** The table’s generic reference to reviewed evidence-set rows does not provide row IDs with which to finish that provenance check.

| Committee ID | Member bioguide | CM designation/type | Result |
| --- | --- | --- | --- |
| C00583161 | M001199 | J/N | exists; ownership not established by these FEC files |
| C00632257 | M001199 | P/H | CCL candidate + CN principal confirmed |
| C00462374 | C001087 | P/H | CCL candidate + CN principal confirmed |
| C00561530 | M001194 | P/H | CCL candidate + CN principal confirmed |
| C00379479 | G000386 | D/Q | exists; ownership not established by these FEC files |
| C00492025 | S000510 | D/Q | exists; ownership not established by these FEC files |
| C00838649 | F000477 | D/N | exists; ownership not established by these FEC files |
| C00575548 | C001113 | P/S | CCL candidate + CN principal confirmed |
| C00843425 | B001326 | P/H | CCL candidate + CN principal confirmed |
| C00802298 | H001101 | P/H | CCL candidate + CN principal confirmed |
| C00801431 | G000605 | P/H | CCL candidate + CN principal confirmed |
| C00652164 | G000583 | D/Q | exists; ownership not established by these FEC files |
| C00854471 | M001232 | P/H | CCL candidate + CN principal confirmed |
| C00834291 | S001231 | P/H | CCL candidate + CN principal confirmed |
| C00415331 | C001067 | P/H | CCL candidate + CN principal confirmed |
| C00459297 | H001058 | P/H | CCL candidate + CN principal confirmed |
| C00938720 | K000394 | J/N | exists; ownership not established by these FEC files |
| C00577999 | B001299 | P/S | CCL candidate + CN principal confirmed |
| C00840017 | A000382 | P/S | CCL candidate + CN principal confirmed |
| C00588772 | H001076 | P/S | CCL candidate + CN principal confirmed |
| C00871152 | G000558 | J/N | exists; ownership not established by these FEC files |
| C00420760 | H001042 | P/S | CCL candidate + CN principal confirmed |
| C00689836 | R000610 | J/N | exists; ownership not established by these FEC files |
| C00771238 | P000145 | D/Q | exists; ownership not established by these FEC files |
| C00430991 | M001137 | P/H | CCL candidate + CN principal confirmed |
| C00801985 | K000401 | P/H | CCL candidate + CN principal confirmed |
| C00304709 | S000510 | P/H | CCL candidate + CN principal confirmed |
| C00365270 | M001111 | D/Q | exists; ownership not established by these FEC files |
| C00782698 | K000391 | J/N | exists; ownership not established by these FEC files |
| C00843763 | M001238 | P/H | CCL candidate + CN principal confirmed |
| C00736876 | W000790 | P/S | CCL candidate + CN principal confirmed |
| C00657833 | R000610 | P/H | CCL candidate + CN principal confirmed |
| C00768762 | G000555 | J/N | exists; ownership not established by these FEC files |
| C00766790 | B001277 | J/N | exists; ownership not established by these FEC files |
| C00716720 | H000273 | P/S | CCL candidate + CN principal confirmed |
| C00801274 | S001223 | P/H | CCL candidate + CN principal confirmed |
| C00607200 | S001201 | P/H | CCL candidate + CN principal confirmed |
| C00823930 | B001319 | J/N | exists; ownership not established by these FEC files |
| C00563429 | M001184 | D/Q | exists; ownership not established by these FEC files |
| C00606939 | R000608 | P/S | CCL candidate + CN principal confirmed |

Mast for Congress, Crawford for Congress and Moolenaar for Congress pass the candidate/principal check. Mast Victory Committee exists and is designated J, but has no CCL candidate link; its $17,000 remains contingent on the supplied evidence-set attribution, not an independently proved campaign ownership relationship from these FEC files.

The reverse search finds two committees with qualifying employer-prefix lines and a CCL link to a sitting candidate that are absent from the supplied key table:

- **C00027466, NRSC**: CM designation U, type Y; CCL’s candidate link is S4AK00214. It is a party committee, not a principal/authorised committee or a single-candidate JFC. That candidate field does not make NRSC receipts gifts to that senator.
- **C00832576, PATRIOT PAC**: designation D, type Q; links include multiple candidates, including two sitting members. It is not an authorised campaign or a single-candidate JFC, and the evidence table does not separately key it to a member. The same $5,000 Anthropic line must not be attributed twice merely because two candidate IDs appear.

Thus the reverse search finds no omitted committee that qualifies under the specified **automatic FEC-link** rules. It does find the above out-of-rule links; their SUB_IDs are preserved in `census_v3_results.json` rather than silently discarded. The control is the correctly identified principal committees and the NRSC/PATRIOT counterexamples to the invalid rule “any CCL link counts.”

## 4. The nine Banks lines

Each amended line has an empty employer and matches its earlier-capture line by committee C00577999, day and amount. Each earlier line is IND, positive and non-memo. Each congress row was found independently by its original SUB_ID in the note. The sum is $31,500. The earlier file is `congress/research/primary/C05-anthropic-employees-direct-giving/sched_a_2026_employer_ANTHROPIC_p010.json`; the amended file is the supplied Banks amended `lines.txt`. The two other saved captures of that page reproduce the two employer discrepancies described above.

| Original SUB_ID | Amended SUB_ID | Congress row | Date | Amount | Blank employer + committee/day/amount match |
| --- | --- | --- | --- | --- | --- |
| 4080720261570548072 | 4091520261598464089 | HM1066 | 2026-04-09 | $3,500 | yes |
| 4080720261570548073 | 4091520261598464090 | HM1067 | 2026-04-09 | $3,500 | yes |
| 4080720261570548076 | 4091520261598464093 | HM1068 | 2026-04-09 | $3,500 | yes |
| 4080720261570548077 | 4091520261598464094 | HM1069 | 2026-04-09 | $3,500 | yes |
| 4080720261570548095 | 4091520261598464112 | HM1070 | 2026-04-10 | $3,500 | yes |
| 4080720261570548147 | 4091520261598464164 | HM1079 | 2026-04-16 | $3,500 | yes |
| 4080720261570548148 | 4091520261598464165 | HM1080 | 2026-04-16 | $3,500 | yes |
| 4080720261570548167 | 4091520261598464184 | HM1085 | 2026-04-17 | $3,500 | yes |
| 4080720261570548168 | 4091520261598464185 | HM1086 | 2026-04-17 | $3,500 | yes |

The congress rows describe these as Anthropic-employer individual receipts, not company gifts. HM1068 and HM1069 transcribe the employer incompletely; their saved originals retain PBC. There is no numeric difference in these nine rows.

## 5. Symmetry, spellings and coverage

The same eligibility predicate and committee map are applied to both employers. ANTHROPIC PBC and all NVIDIA CORP/CORPORATION variants qualify under the same prefix test. The saved originals also contain the misspelling **NVIDIA COPORATION**: one qualifying member-linked line is included, because the prefix is still NVIDIA. The other counted spelling variants are enumerated without names in `census_v3_results.json`.

In the saved API pages, one non-prefix employer contains a company string: **ODE WITH ANTHROPIC**, SUB_ID **4110520261636320037**, $50 to ActBlue (C00401224). It is excluded by the prefix rule and, independently, is not a receipt to a keyed sitting-member committee. No non-prefix NVIDIA-containing employer appears in these saved pages. These are bounded observations, not proof about arbitrary misspellings in the full FEC corpus: the bulk extract was selected by prefix and the API pages came from employer searches. The unfiltered bulk file needed to test unrelated typos was not supplied.

The principal asymmetry is **recovery coverage**: nine Anthropic receipts ($31,500) are restored from an earlier capture after an amendment blanked their employer. Equivalent older Nvidia captures were not supplied. A like-for-like comparison without this restoration would be Anthropic $3,450,196 on 651 lines versus Nvidia $155,789 on 510 lines; this does not change the three-chairmen totals. It would be inaccurate to call the source coverage wholly symmetric, or to assert that no earlier Nvidia copy exists anywhere. The figure does disclose the exception, but should bound it to this evidence set.

The FEC data show filed employer descriptions, not independent confirmation of employment at the gift date, motive, client instructions, or a gift’s effect on any decision. JFC designation or a reviewed key is also not proof that the full receipt was ultimately allocated to one candidate.
