# Second independent audit of one draft figure before it is made public: the third version, every drawn row against its saved original

Owner: the session that built the figure. You are the auditor. You did not build this figure. Work only inside audit/round2; write only under audit/round2/out/. Change nothing else anywhere. Do not fetch anything from the web.

The figure ("The three chairmen who summoned Huang", third version) lists the records that tie three members of Congress (Reps. Brian Mast, John Moolenaar, Rick Crawford) to the AI company Anthropic, its employees and groups linked to it, with the same records for Nvidia. It will be published. The builder is a model made by Anthropic, so read with that in mind: look as hard for an understated or missing fact about Anthropic as for an overstated one, and check that Nvidia is counted by the same rule and described with the same care.

A first audit read the second version (its findings are in `round1_findings.csv` and `round1_figure_findings.csv`). This version is meant to apply all of them, and it adds new material: a band on what is at stake between the two companies, one shared timeline, an at-a-glance table, lobbyists' own gifts counted by one rule for both companies, each chairman's campaign total, two frames of each advertisement, and new rows.

## The one hard rule about names
Some originals hold the names of private people: employees who gave money, and lobbyists. **Never write the name of a donor or of a lobbyist in any file you produce.** Refer to an FEC line by its SUB_ID, and to a lobbyist's gift by its item id (`LG...`) or by firm, date and amount. Members of Congress, companies, organisations, firms, political committees, and the public figures the figure itself names (Jack Clark, Saif Khan, Dustin Moskovitz, Luke Muehlhauser, Holden Karnofsky, Richard Fontaine, Brad Carson, Dario Amodei, David Sacks, Jensen Huang, Tom Cotton) may be named.

## Inputs (frozen; do not edit)
- `rows.jsonl`: 169 rows, one per line: `row_id`, `table` (what kind of row), `drawn_text` (the words the figure draws for it, or for a computed number its value and what it counts), other fields, `src` (a list of sources) and `q` (a list of passages, one per source, that a script has already found in that source).
- How to open a source named in `src`:
  - a bare id (for example `art-nbc-nvidia-tall-tale`, `house-hrg-zs00-20250625-transcript`): the folder `research/primary/<id>/` (`text.txt`, sometimes `body.html` or `body.pdf`, `meta.json`, `*.json`, images). For the `google-ads-creative-*` folders the words on screen were read by the builder from saved frames (`frame-00.png` to `frame-08.png`, tiled in `frames.png`): look at the frames yourself and say whether the reading is right. For `x-chinaselect-letter-image` the letter's words were read by the builder from the saved image (`text.reextract.txt`): compare with the image. For `google-ads-political-search-nvidia-20261113` compare `text.txt` with the three screenshots.
  - `pack:<path>#<row id>`: the row with that id (first column or `row_id`) in `EVIDENCE_SETS/<path>`; a file may begin with comment lines starting `#`. Where the row has a `url` and a `quote_300`, and its `note` names a saved file under that pack's `research/primary/`, open the saved file when the row alone does not settle the point.
  - `table:<file>#<key>`: the row with that key (first column or `row_id`) in `tables/<file>`.
- `evidence.tsv`: the same sources as a reader of the public repository will see them (a link and a passage each).
- `tables/`: `nv13_ties.csv` (every record in a chairman's panel), `nv13_key.csv` (who is who), `nv13_stake.csv` (the stake band), `nv13_events.csv` (timeline events), `nv13_numbers.csv` (every computed number), `nv13_glance.csv` (the at-a-glance table), `lobbyist_gifts.csv` (30 gifts by lobbyists or firm PACs naming one of the three; lobbyists are numbered, not named), `employee_gifts.csv` (1,170 FEC lines; unchanged since the first audit, whose recount matched it exactly), `employee_gift_rates.csv`, `committee_keys.csv`, `pacs_by_member.csv`, `pac_base_rates.csv`, the bill tables, `nv13_members.csv`.
- Originals for the lobbyists' gifts: `research/primary/lda-gov-contrib-{mast,moolenaar,crawford}-{2024,2025,2026}/page-*.json` (contribution reports, form LD-203, from the Senate's lobbying records API: every report with an item whose honoree matched the surname; **they hold lobbyists' names**), and each company's filings `research/primary/lda-gov-{nvidia,anthropic}-{2024,2025,2026}/body.json` (and `lda-gov-anthropic-2026-p2`). Windows for firms of groups Open Philanthropy has funded: `EVIDENCE_SETS/congress/research/lb_network_windows.csv`; the pack's own classification of its lines: `lb_4b_measures.csv` and `lobbyist_contributions.csv` in the same folder.
- Other originals you may need: `research/primary/fec-bulk-weball26-20261113/` (candidate totals), `fec-bulk-pas226-20261112/` (committee-to-candidate contributions; `cm26.zip`, `pas226.zip`), `census-cd119-zcta-20261113/`, `google-political-ads-pfa-20260916/creative-stats.csv`.
- `figures/nv13-three-chairmen.html`: the figure as drawn. It begins with an HTML comment listing the row ids it rests on. The four advertisement frames are embedded as images.

## Part A: every row
For each row in `rows.jsonl`, open every source it cites and read enough to judge the row; do not rely on `q` alone, and never take the row's own wording as evidence. Append one line to `out/findings.csv` (header `finding_id,row_id,grade,passage_found,problem,suggested_wording`):
- `grade`: `ok` (the sources support everything `drawn_text` says), `qualification` (supported, but the wording goes further than the source, drops a limit the source states, gives a date or an amount the source does not give, or leaves a reader with a wrong impression), or `error` (a fact in `drawn_text` is not in the sources or contradicts them).
- `passage_found`: the words in the source that decide your grade, at most 300 characters (never a donor's or lobbyist's name).
- `problem` and `suggested_wording` for `qualification` and `error` only; the suggestion must be something the sources support.
Also grade down, as a `qualification`, wording that states or implies a motive, describes a person's character, goes beyond a public role, or implies that one event caused another when no source says so.
Read these most closely:
- rows of `what is at stake between the two companies`: is each company described fairly and from its source? Is a quotation cut in a way that changes its sense? Is a date the source's own? Does "moving into" the other's business go beyond the sources?
- rows of `key: who is who`: each named link, each grant total and its years (recompute from the rows cited).
- rows about lobbyists' gifts (type `lobbyists`): every firm, amount, date, count of lobbyists and the "listed for"/"not listed for" call.
- rows of `number computed for the figure`: recompute every one from `tables/` or the originals and say which you could not.
- the two rows quoting what was said about Mast's bill (types `release`, `sacks`): is the report's wording kept, and is it clear who claimed what?

## Part B: the figure, element by element
Read all visible text of the figure (title, subtitle, the stake band, the key, the at-a-glance table, legend, every timeline label and caption, panel headers, every statement, the tiles, the footnote). Append to `out/figure_findings.csv` (header `finding_id,grade,element_text,problem,rows_checked`) one line per problem, and a closing line `B-CLOSE` saying how many elements you read:
- a visible sentence or number that no listed row or table supports (recount every count and recompute every sum the figure states, the title's four amounts included);
- a cell of the at-a-glance table that disagrees with the panels or the tables;
- a row id or a file name visible to a reader;
- wording that states or implies motive, coordination or cause. Look hard at the title, the two shaded captions on the timeline (three weeks of employees' gifts; six weeks of gifts from Nvidia's firms) and the placing of gifts next to bills: does anything read as "this was paid for that"? Is the same treatment given to both companies?
- a place where the figure should say what the record does not show and does not;
- a link to Anthropic, or to Nvidia, that a reader new to the subject could not follow from the figure alone, or would misread;
- something in a row's sources that weakens or contradicts what is drawn and is left out.

## Part C: recount the lobbyists' gifts from the Senate's files (a census, not a sample)
The builder's rule (`tables/lobbyist_gifts.csv`): a contribution item of an LD-203 report counts if its honoree is Mast, Moolenaar or Crawford (another person named Crawford is refused), the report was filed by a registrant or by a lobbyist it employs, and the registrant had a lobbying registration for the client on the day of the gift (client effective date to termination date). Three sides: Nvidia's registrants and Anthropic's registrants (from each company's filings, 2024 to 2026), and firms registered for groups Open Philanthropy has funded (`lb_network_windows.csv`, rows whose `status` begins `window`, tier not T3). `measure`: `named` if the lobbyist is listed for that client by that registrant from the first quarter listed (or the registration date) to 90 days after the last quarter listed; `firm_only` otherwise; `firm_pac` if the registrant itself filed the report; `own_pac` if the registrant is the client itself. For the third side the named/firm_only call is the pack's (`lb_4b_measures.csv`), and a line the pack does not hold is `firm_only_not_classified`. The same gift appears in more than one pull and in amended reports: it is counted once per filer, member, payee, date and amount.
Write your own script (keep it in `out/`), apply the rule yourself to the originals, and report in `out/census.md`:
1. Per side and member: items, dollars, distinct lobbyists, by measure, against `tables/lobbyist_gifts.csv`. List every difference by firm, date and amount (no names).
2. Honoree matching: list honoree spellings you accepted and refused (these are members' names; no lobbyist names), and say whether any accepted string is not the member, or any refused string is.
3. Windows: for each registrant in the table, the effective date and any termination you find, against the table.
4. Counting once: are two real gifts on one day by one person to one committee for one amount possible in these reports, and did the rule merge any? Count the candidates.
5. Is anything counted for one company that would not be for the other? In particular: are there registrants for either company in years before 2024 or outside the saved filings that the rule cannot see? Say what the saved filings can and cannot establish.
6. Whether the pulls are complete: for each of the nine folders, pages saved against `count`.

## Part D: the first audit's findings
For each line of `round1_findings.csv` whose grade is not `ok` and each line of `round1_figure_findings.csv` except `B-CLOSE`, write one line to `out/round1_followup.csv` (header `finding_id,answered,where_in_v3,what_remains`): `answered` is `yes`, `partly` or `no`; quote the third version's words that answer it; say plainly what still stands.

## Part E: what was left out
In `out/REPORT.md` say, from what you read: whether any tie between these three members and Nvidia, or Anthropic, is in the sources and not in the figure; whether any source the rows cite states a denial, a limit or a later correction the figure omits; whether the stake band leaves out something in its own sources that a fair reader would need (for example what else those reports say about either company's position); and whether the figure's list of what the record does not show, and of what was not searched, is complete.

## Rules
- A missing file or an unreadable original is a gap, not a finding: write it to `out/gaps.csv` (`row_id,source,what_failed`) and go on. Never grade from memory or outside knowledge.
- Be exact and plain. No guesses about why anyone did anything.
- Append only; if `out/findings.csv` already has a line for a `row_id`, skip that row (this lane may be restarted).
- Before you finish, search every file under `out/` for the names of donors and lobbyists you met in the originals and remove any you find; say in the report that you did.

## Report
`out/REPORT.md`: rows read and counts by grade; the most serious findings in plain words; Part B by element; Part C in a short table; Part D counts (yes, partly, no); Part E; gaps. End with exactly one line: `audit: complete` or `audit: incomplete <reason>`. This round fetches nothing, so it ends `audit: incomplete originals not re-fetched` unless something worse stops it.
