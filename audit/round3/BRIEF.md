# Third independent audit of one draft figure before it is made public: the rows added or changed since the second audit, and the corrected figure

Owner: the session that built the figure. You are the auditor. You did not build this figure. Work only inside audit/round3; write only under audit/round3/out/. Change nothing else anywhere. Do not fetch anything from the web.

The figure ("The three chairmen who summoned Huang", third version, corrected) lists the records that tie three members of Congress (Reps. Brian Mast, John Moolenaar, Rick Crawford) to the AI company Anthropic, its employees and groups linked to it, with the same records for Nvidia. It will be published. The builder is a model made by Anthropic, so read with that in mind: look as hard for an understated or missing fact about Anthropic as for an overstated one, and check that Nvidia is counted by the same rule and described with the same care.

A second audit read this version before correction. Its report and findings are here as `round2_REPORT.md`, `round2_findings.csv` (169 rows: 152 ok, 12 qualifications, 5 errors), `round2_figure_findings.csv` (25 problems) and `round2_gaps.csv`. The builder says it has applied them. Since then the builder also added rows the second audit never saw: gifts from the political committees of trade groups (rows CT52 to CT57, CN68 to CN78), who funds Public First Action (CK09 reworded, CK23 new), the context of the newspaper report (CK24, CK25), three ties the second audit found in sources already cited (CT58, CT59, CT60), two money events on the timeline (CE21, CE22), and a count of the lines of the at-a-glance table (CN79 to CN86).

## The one hard rule about names
Some originals hold the names of private people: employees who gave money, and lobbyists. **Never write the name of a donor or of a lobbyist in any file you produce.** Refer to an FEC line by its SUB_ID, and to a lobbyist's gift by its item id (`LG...`) or by firm, date and amount. Members of Congress, companies, organisations, firms, political committees, and the public figures the figure itself names (Jack Clark, Saif Khan, Dustin Moskovitz, Luke Muehlhauser, Holden Karnofsky, Richard Fontaine, Brad Carson, Dario Amodei, David Sacks, Jensen Huang, Tom Cotton) may be named. One donor is named by the figure on purpose: Anthropic's chief executive, for a gift to a super PAC; say whether that naming keeps to public roles.

## Inputs (frozen; do not edit)
- `rows.jsonl`: 202 rows, one per line: `row_id`, `table` (what kind of row), `drawn_text` (the words the figure draws for it, or for a computed number its value and what it counts), other fields, `src` (a list of sources) and `q` (a list of passages, one per source, that a script has already found in that source).
- `changed_rows.tsv`: for each row, `new`, `changed` or `unchanged` since the second audit (33 new, 27 changed, 142 unchanged).
- How to open a source named in `src`:
  - a bare id (for example `art-pfa-80m-release`, `man-nyt-1029-01`, `fec-filings-c30003586-20261114`): the folder `research/primary/<id>/` (`text.txt`, sometimes `text.reextract.txt`, `body.html` or `body.pdf`, `meta.json`, `*.json`, images).
  - `pack:<path>#<row id>`: the row with that id (first column or `row_id`) in `EVIDENCE_SETS/<path>`; a file may begin with comment lines starting `#`. Where the row's `note` names a saved file under that pack's `research/primary/`, open the saved file when the row alone does not settle the point (for the rows on Public First Action: `EVIDENCE_SETS/congress/research/primary/C02-public-first-family-money-in/`).
  - `table:<file>#<key>`: the row with that key (first column or `row_id`) in `tables/<file>`.
- `evidence.tsv`: the same sources as a reader of the public repository will see them.
- `tables/`: as in the second audit, plus `trade_pac_gifts.csv` (gifts to the three from the political committees of three trade groups) and `lobbyist_gifts.csv` (now 31 lines: `LG031` is the gift the second audit found).
- Originals for the trade groups: member lists `research/primary/art-sia-members/`, `art-iti-members/`, `art-technet-members-all/` (and `art-technet-members`, `-p2` to `-p5`; the first page alone was once misread, see its `CORRECTION.txt`); the FEC's file of committees' gifts to candidates `research/primary/fec-bulk-pas226-20261112/` (`cm26.zip`, `pas226.zip`).
- Originals for the lobbyists' gifts: as in the second audit (`research/primary/lda-gov-contrib-*/page-*.json`, **they hold lobbyists' names**). The second audit's own census script and result are here as `round2_census.py`, `round2_audit_tools.py`, `round2_census_verified.json`: you may run or adapt them (write copies under `out/`).
- `figures/nv13-three-chairmen.html`: the corrected figure as drawn. It begins with an HTML comment listing the row ids it rests on.

## Part A: every row marked new or changed
For each row of `rows.jsonl` that `changed_rows.tsv` marks `new` or `changed` (60 rows), open every source it cites and read enough to judge the row; do not rely on `q` alone, and never take the row's own wording as evidence. Append one line to `out/findings.csv` (header `finding_id,row_id,grade,passage_found,problem,suggested_wording`):
- `grade`: `ok` (the sources support everything `drawn_text` says), `qualification` (supported, but the wording goes further than the source, drops a limit the source states, gives a date or an amount the source does not give, or leaves a reader with a wrong impression), or `error` (a fact in `drawn_text` is not in the sources or contradicts them).
- `passage_found`: the words in the source that decide your grade, at most 300 characters (never a donor's or lobbyist's name).
- `problem` and `suggested_wording` for `qualification` and `error` only; the suggestion must be something the sources support.
Also grade down, as a `qualification`, wording that states or implies a motive, describes a person's character, goes beyond a public role, or implies that one event caused another when no source says so.
Read these most closely:
- CK09 and CK23 (who funds Public First Action): does the group's announcement of Jun 30, 2026 name any donor? Does "the one report the group has filed with the FEC shows no donations" go further than the saved filing list and the pack's saved copy of that report (`fec-f9-C30003586-1952561.csv`) support? Is the chief executive's gift described as going to the right committee, and is the relation between that committee and the group stated no more strongly than the FEC lines show? Is anything about who funds the group in the pack's rows and left out?
- CK24 and CK25 and the subtitle: is the newspaper report described fairly to both sides, with each quotation kept in its sense?
- the nine rows of `what is at stake between the two companies`: the second audit asked for fuller quotations and limits; are they now right, and is either company now described more harshly or more kindly than its sources?
- CT52 to CT57 and CN68 to CN78 (trade groups): recount the members on each saved list, check that each list does or does not name each company, and recompute each political committee's gifts to the three and its count of candidates from `pas226.zip`. Is "lists Nvidia and not Anthropic" true of each list as saved? Is a trade group's gift described as the group's, not Nvidia's?
- CT58, CT59, CT60: is each report's wording kept, with its date, and is it clear which bill and which chamber?
- CN79 to CN86: recount from `tables/nv13_glance.csv`.
- CT15, CN14, CN16, CN49, CN64: the corrected sums.

## Part B: the corrected figure, element by element
Read all visible text of the figure again (title, subtitle, the stake band, the key, the at-a-glance table and the sentence under it, legend, every timeline label and caption, panel headers, every statement, the tiles, the footnote). Append to `out/figure_findings.csv` (header `finding_id,grade,element_text,problem,rows_checked`) one line per problem, and a closing line `B-CLOSE` saying how many elements you read:
- a visible sentence or number that no listed row or table supports (recompute the title's four amounts, every cell of the at-a-glance table, the sentence that counts its lines, and both shaded captions);
- a row id or a file name visible to a reader;
- wording that states or implies motive, coordination or cause, with the same test applied to both companies. The timeline now also shows Anthropic's two gifts to Public First Action beside the dates of the ads: does that placing say more than the records do?
- the timeline's marks: are equal dollars now drawn with equal areas for all three shapes, and does the figure say plainly that three gifts dated 2024 are not drawn?
- a place where the figure should say what the record does not show and does not;
- a link to Anthropic, or to Nvidia, that a reader new to the subject could not follow from the figure alone, or would misread;
- something in a row's sources that weakens or contradicts what is drawn and is left out.

## Part C: the lobbyists' gifts, recounted once more
Run a census of the Senate's files by the rule in `round2_REPORT.md` (your own script or an adapted copy of `round2_census.py`, kept under `out/`) and compare with `tables/lobbyist_gifts.csv` (31 lines). Report in `out/census.md`, per side and member, items and dollars against the table, and every difference by firm, date and amount (no names). Say whether any honoree spelling of one of the three is still refused, and whether any accepted spelling is someone else.

## Part D: the second audit's findings
For each line of `round2_findings.csv` whose grade is not `ok`, each line of `round2_figure_findings.csv` except `B-CLOSE`, and each line of `round2_gaps.csv`, write one line to `out/round2_followup.csv` (header `finding_id,answered,where_in_figure,what_remains`): `answered` is `yes`, `partly` or `no`; quote the corrected words that answer it; say plainly what still stands.

## Part E: what was left out
In `out/REPORT.md` say, from what you read: whether any tie between these three members and Nvidia, or Anthropic, is in the sources and not in the figure; whether any source the new or changed rows cite states a denial, a limit or a later correction the figure omits; and whether the lists of what the record does not show, and of what was not searched, are now complete.

## Rules
- A missing file or an unreadable original is a gap, not a finding: write it to `out/gaps.csv` (`row_id,source,what_failed`) and go on. Never grade from memory or outside knowledge.
- Be exact and plain. No guesses about why anyone did anything.
- Append only; if `out/findings.csv` already has a line for a `row_id`, skip that row (this lane may be restarted).
- Before you finish, search every file under `out/` for the names of donors and lobbyists you met in the originals and remove any you find; say in the report that you did.

## Report
`out/REPORT.md`: rows read and counts by grade; the most serious findings in plain words; Part B by element; Part C in a short table; Part D counts (yes, partly, no); Part E; gaps. End with exactly one line: `audit: complete` or `audit: incomplete <reason>`. This round fetches nothing, so it ends `audit: incomplete originals not re-fetched` unless something worse stops it.
