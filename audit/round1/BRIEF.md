# Independent audit of one draft figure before it is made public: every drawn row against its saved original

Owner: the session that built the figure. You are the auditor. You did not build this figure. Work only inside audit/round1; write only under audit/round1/out/. Change nothing else anywhere. Do not fetch anything from the web.

The figure ("The three chairmen who summoned Huang") lists documented ties between three members of Congress (Reps. Brian Mast, John Moolenaar, Rick Crawford) and the AI company Anthropic, its employees, and groups linked to it, with the same records for Nvidia. It will be published. The builder is a model made by Anthropic, so read with that in mind: look as hard for an understated or missing fact about Anthropic as for an overstated one, and check that Nvidia is counted by the same rule.

## The one hard rule about names
Some originals hold the names of private people: employees who gave money, and lobbyists. **Never write the name of a donor or of a lobbyist in any file you produce.** Refer to an FEC line by its SUB_ID and to a lobbyist's gift by its row id. Members of Congress, companies, organisations, firms, and the public figures the figure itself names (Jack Clark, Saif Khan, Dustin Moskovitz, Luke Muehlhauser, Holden Karnofsky, Richard Fontaine, Brad Carson, Dario Amodei, Jensen Huang, Cari Tuna) may be named.

## Inputs (frozen; do not edit)
- `rows.jsonl`: 63 rows, one per line: `row_id`, `table` (what kind of row), `drawn_text` (the words the figure draws for it), other fields, `src` (a list of sources) and `q` (a list of passages, one per source, that a script has already found in that source).
- How to open a source named in `src`:
  - a bare id (for example `anthropic-pfa-2`, `google-ads-creative-mi2-20261113`): the folder `research/primary/<id>/` (`text.txt`, sometimes `body.html`, `meta.json`, `lines.txt`, `*.json`, images). For the two `google-ads-creative-*` folders the words on screen were read by the builder from the saved frames (`frame-00.png` to `frame-08.png`, tiled in `frames.png`): look at the frames yourself and say whether the reading is right.
  - `pack:<path>#<row id>`: the row with that id (first column or `row_id`) in `EVIDENCE_SETS/<path>`; each such file may begin with one comment line starting `#`. Where the row has a `url` and a `quote_300`, and its `note` names a saved file under that pack's `research/primary/`, open the saved file when the row alone does not settle the point.
  - `table:<file>#<key>`: the row with that key in `tables/<file>`.
- `evidence.tsv`: the same sources as a reader of the public repository will see them (a link and a passage each).
- `tables/employee_gifts.csv`: every FEC line the builder counted as an employee's gift, both companies (1,170 lines): `sub_id`, committee, date, amount, employer as filed, a donor number (no names), the source, and the member the committee is tied to. `tables/committee_keys.csv`: each committee holding a counted line, the member it is tied to, and on what basis. `tables/employee_gift_rates.csv`: the totals. The other tables: company PAC money by member, the bills, lobbying reports naming each bill, the key's lines, the three members' header facts.
- FEC originals for the recount: `research/primary/fec-bulk-indiv26-employers-20261113/lines.txt` (every line of the FEC bulk file whose EMPLOYER begins with ANTHROPIC or NVIDIA; pipe-delimited, header on line 1; **holds names**), `research/primary/fec-sched_a-employer-anthropic-2026/page-*.json` and `.../fec-sched_a-employer-nvidia-2026/page-*.json` (the same lines from the FEC API), `research/primary/fec-bulk-committees-2026-20261113/` (`ccl26.zip` committee-candidate links, `cm26.zip` committees, `cn26.zip` candidates), `research/primary/fec-bulk-indiv26-banks-amended-20261113/lines.txt` (nine lines of an amended report), and the sitting members with their FEC candidate ids in `EVIDENCE_SETS/congress/research/members_network.csv` (`cohort` = sitting).
- `figures/nv13-three-chairmen.html`: the figure as drawn. It begins with an HTML comment listing the row ids it rests on.

## Part A: every row
For each row in `rows.jsonl`, open every source it cites and read enough to judge the row; do not rely on `q` alone, and never take the row's own wording as evidence. Append one line to `out/findings.csv` (header `finding_id,row_id,grade,passage_found,problem,suggested_wording`):
- `grade`: `ok` (the sources support everything `drawn_text` says), `qualification` (supported, but the wording goes further than the source, drops a limit the source states, gives a date or an amount the source does not give, or leaves a reader with a wrong impression), or `error` (a fact in `drawn_text` is not in the sources or contradicts them).
- `passage_found`: the words in the source that decide your grade, at most 300 characters (never a donor's or lobbyist's name; give the SUB_ID or row id instead).
- `problem` and `suggested_wording` for `qualification` and `error` only; the suggestion must be something the sources support.
Also grade down, as a `qualification`, wording that states or implies a motive, describes a person's character, goes beyond a public role, or implies that one event caused another when no source says so.
Rows of the table `key: who is who` deserve the closest reading: each says how a group connects to Anthropic. Check each named link (the director who invested, the board seat, the staff move, each grant total and its years, the trust seat, "related organisation", "same president") against its sources, recompute each grant total from the rows cited, and say if a link is weaker, older or more indirect than the words make it sound.
For the two rows about advertisements that ran, check the dates, the showings and the spending against the Google report's line, the target (for the Florida ad, compare the zip codes on the report's line with the Census file's rows for district 1221), and the words on screen against the frames.

## Part B: the figure, element by element
Read all visible text of the figure (title, subtitle, the key, legend, panel headers, time-strip labels, every statement, the tiles, the footnote). Append to `out/figure_findings.csv` (header `finding_id,grade,element_text,problem,rows_checked`) one line per problem, and a closing line `B-CLOSE` saying how many elements you read:
- a visible sentence or number that no listed row or table supports (recount every count and recompute every sum the figure states, the title's $78,000 included);
- a row id or a file name visible to a reader;
- wording that states or implies motive, coordination or cause;
- a place where the figure should say what the record does not show and does not;
- a link to Anthropic that a reader new to the subject could not follow from the figure alone, or would misread;
- something in a row's sources that weakens or contradicts what is drawn and is left out.

## Part C: recount the employees' gifts from the FEC files (a census, not a sample)
The builder's rule: an FEC line counts if ENTITY_TP is IND, the EMPLOYER field begins with the company's name (ANTHROPIC or NVIDIA), MEMO_CD is not X, the amount is above zero, the date is Jan 1, 2025 or later, and the receiving committee is tied to a sitting member (his principal or authorised campaign committee by the FEC's committee-candidate links; a joint fundraising committee linked to that one candidate; or a committee `tables/committee_keys.csv` ties to him on the evidence set's keys). The bulk file's copy of a line stands; an API line is added only if the bulk file lacks it, or replaces the bulk copy when it is a later filing of the same transaction. Nine lines to Banks for Senate are counted from an earlier capture because the amended report leaves the employer empty.
Write your own script (keep it in `out/`), apply the rule yourself to the FEC originals, and report in `out/census.md`:
1. For each of the three members and each company: the lines you find (count, dollars, distinct donors counted by name without writing any name), against `tables/employee_gifts.csv`. List every SUB_ID in one and not the other.
2. Across all 535: members reached, dollars, lines and donors for each company, against `tables/employee_gift_rates.csv`. Explain every difference you can.
3. The committee keys: take a sample of at least 40 rows of `tables/committee_keys.csv` (all rows for the three members, the rest at random with a fixed seed you state) and check each against `ccl26`, `cm26`, `cn26`: is the committee really that member's? Report any that is not. Then look for the opposite error: committees in the FEC originals that hold a qualifying line, are linked by `ccl26` to a sitting member's candidate id, and are missing from `committee_keys.csv`.
4. The nine Banks lines: confirm from the two files that each amended line has an empty employer and matches an earlier-capture line by committee, day and amount; say what the congress pack's row for each shows (`EVIDENCE_SETS/congress/research/hard_money.csv`, rows whose ids are in `tables/employee_gifts.csv` is not possible, so match by the original `sub_id` printed in each row's `note`).
5. Is Nvidia counted by the same rule? Name anything that would count for one company and not the other (employer spellings such as "NVIDIA CORP" or "ANTHROPIC PBC" are both covered by "begins with"; look for spellings the rule misses for either company, and count them).

## Part D: what was left out
In `out/REPORT.md` say, from what you read: whether any tie between these three members and Nvidia is in the sources but not in the figure; whether any source the rows cite states a denial, a limit or a later correction the figure omits; and whether the figure's own list of what the record does not show is complete.

## Rules
- A missing file or an unreadable original is a gap, not a finding: write it to `out/gaps.csv` (`row_id,source,what_failed`) and go on. Never grade from memory or outside knowledge.
- Be exact and plain. No guesses about why anyone did anything.
- Append only; if `out/findings.csv` already has a line for a `row_id`, skip that row (this lane may be restarted).

## Report
`out/REPORT.md`: rows read and counts by grade; the most serious findings in plain words; Part B by element; Part C in a short table; Part D; gaps. End with exactly one line: `audit: complete` or `audit: incomplete <reason>`. This round fetches nothing, so it ends `audit: incomplete originals not re-fetched` unless something worse stops it.
