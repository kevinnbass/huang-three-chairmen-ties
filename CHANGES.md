# Changes and corrections

This file lists what changed between drafts and every error found on the way, with what was done about it.

## Correction of Nov 17, 2026: lobbying reports that name the GAIN AI Act without a bill number

- **What was wrong.** The count of lobbying reports that name a chairman's chip bill read bill numbers only. A report
  that named a measure as an amendment to another bill, or by its name alone, was in no count, for either company. Four
  reports name the GAIN AI Act that way, two filed for each company. Anthropic's own report for the third quarter of
  2025 names Senate amendment 3505 to the defense authorization bill for fiscal 2026, with the act's name; a firm's
  report for Anthropic for the fourth quarter of 2025 gives the act's name alone. Nvidia's own reports for the third and
  fourth quarters of 2025 name "S.A. 3505", without the act's name. The amendment's text, as Congress.gov prints it,
  carries "GAIN AI Act of 2025" as its short title; Sen. Banks submitted it on Aug 1, 2025, and Moolenaar introduced
  H.R. 5885 on Oct 31, 2025.
- **How it was found.** By the builder, on Nov 17, 2026, reading pages that another working session of this project had
  saved from the Senate's lobbying records. Its first check searched the two companies' reports for the act's name and
  found only Anthropic's two; it recorded that Nvidia had none. A second search, for amendment numbers, found Nvidia's
  two before anything was published. The audits had been given the count by bill number.
- **What was done.** One rule for both companies: a report counts for a measure when its text gives a bill number of the
  measure, or the number of a Senate amendment whose official text carries the measure, or the measure's name. The
  three bases are counted apart in a new table, `research/lobbying_family_reports.csv`, and
  `research/lobbying_filings.csv` says for each report which measures it names and how (column `chip_measures`). The
  count by bill number does not change: `research/lobbying_bill_reports.csv` is the same file, byte for byte.
  Moolenaar's panel still says that H.R. 5885 is named in 1 report filed for Anthropic and 1 filed for Nvidia, and now
  adds that 2 more filed for each company name the act without a bill number, and how each does. The at-a-glance table
  says the same. For the other four measures no report of either company falls outside the count by bill number, so
  Mast's line on H.R. 6875 does not change. The script's window (reports of 2025 and 2026) is now written in its code.
- **What is not known.** One Anthropic report, for the third quarter of 2026, names Senate amendment 6561 to the defense
  authorization bill for fiscal 2027. The official record of that bill gives the amendment's sponsors and day and no
  text or description; the page of its text could not be fetched and the Internet Archive holds no copy. It is counted
  for no measure. An amendment is recognised only when a report gives its number: a report that describes a provision
  in its own words, without the act's name, a bill number or an amendment number, is not counted for any measure.
- **Not read independently.** No auditor has read this correction.

## Third correction of Nov 16, 2026: the counts of saved pages naming each chairman, again

- **What was wrong.** This figure counted each saved page from the text first taken from it, even where the companion
  figure had since taken the article's text again from the saved HTML because the first extraction had missed it. The
  companion figure's thirteenth reading (its repository, `audit2/`, files `n-...`, `n-findings13.csv`) found that two
  posts of one site name all three chairmen in the post's own summary and were not counted here. Separately, that
  reading found live pages whose saved HTML holds entries the text lacked; one such entry, on one page, names Mast.
- **What was done.** This figure now reads the same text as the companion figure for every page, and the live entry is
  added to the text read (a new file beside the saved page; nothing was replaced). The panels now say: Mast named on 93
  of the 1,086 saved pages (was 90), Moolenaar 81 (79), Crawford 74 (72). `research/story_pages.tsv` marks the three
  pages. No other number and no tie in this figure changes.
- **The second correction, read.** The companion figure's twelfth reading (`audit2/`, files `m-...`, `m-findings13.csv`)
  read the table, the caption and the counts as they then stood (90, 79, 72) and found them right for the text this
  figure then read.
- **Not yet read independently.** The three counts as they now stand.
- **A limit.** A page is counted when its text names the chairman anywhere; on a live page or a round-up that can be in
  an entry about something else. A passage the extraction lost is found only by the searches described here and below.

## Second correction of Nov 16, 2026: the counts of saved pages naming each chairman

- **What was wrong.** While answering the next reading of the companion figure, every saved page's HTML was searched for a
  member's name that the text taken from it lacks. Two pages name the chairmen only in a part of the piece that the
  extraction had left out: a timeline table that lists the three chairmen's letter, and a photo caption that names Mast.
- **What was done.** The table and the caption were added to the text read for those two pages (new files beside the saved
  pages; nothing was replaced). The panels now say: Mast named on 90 of the 1,086 saved pages (was 88), Moolenaar 79 (78),
  Crawford 72 (71). `research/story_pages.tsv` marks the two pages.
- **The first correction, read.** The companion figure's eleventh reading (its repository, `audit2/`, files `l-...`,
  `l-findings13.csv`) read the correction below: all 31 lines of `research/lobbyist_gifts.csv`, the reworded line, the
  labels and the three counts of pages as they then stood (88, 78, 71). It found nothing to change, and judged the $4,500
  fair under this figure's rule and the window of Jan 2024 to Jun 2026 plainly stated.
- **Read since.** The companion figure's twelfth reading read the table, the caption and these counts and found them right
  for the text then read; see the third correction above for what the reading after it found.
- **A limit.** The search finds a lost passage only when it names a member whose name is searched. Other tables and
  captions can still be missing from a page's text.

## Correction of Nov 16, 2026: one line of committee money worded as a lobbyist's gift; one count of pages

- **What was wrong.** Two things, both found by an independent reading of the companion figure "Fifteen days, mapped",
  which is built from the same tables (its tenth reading, in that figure's repository under `audit2/`, files `k-...`).
  First, Mast's panel said "$1,000 from a lobbyist there" for a contribution of Feb 16, 2024 at a firm registered for
  the Future of Life Institute. The lobbyist's contribution report lists that $1,000 under a campaign committee that
  carries the lobbyist's own name: it is the committee's money, not the lobbyist's own. The builder had never read who
  made each contribution in a lobbyist's report. Second, the count of saved news pages naming Crawford searched for
  "Rick Crawford" and a title before the surname; two pages give his legal given name, Eric, and were missed.
- **What was done.** Every line of `research/lobbyist_gifts.csv` now says whose money it is (`own_money`, and
  `contributor` where it is not the lobbyist's own), by one rule for all three sides: a line is a lobbyist's own money
  only when the report says SELF or gives the filer's own name and nothing else. Of the 31 lines, 23 are a lobbyist's
  own, 7 are a firm's or a group's PAC, as they were already labelled, and this one is a campaign committee's. Its name
  is not printed, because it would name the lobbyist. The table keeps its window, gifts dated Jan 2024 to Jun 2026; the
  companion figure's table reads the same reports back to 2020. Mast's panel now says what the line is; the at-a-glance row is
  headed "Gifts reported by lobbyists and PACs of their firms"; the notes say that one line is a campaign committee's
  contribution. Crawford's panel says 71 of the 1,086 saved pages (was 69); the other two chairmen's counts were
  checked against a wider search of every name form and did not change.
- **What moved.** No sum: the $4,500 on that row for Mast counted the line before and counts it now, under the rule the
  notes give (a gift counts if a lobbyist's or a firm's report names the chairman and the firm was registered for the
  client that day). What changed is what the line is said to be. No line on Anthropic's own side changed.
- **Not yet read independently.** These two corrections were checked by script only.

## Correction of Nov 15, 2026: the count across all 535 members, after every joint committee's statement was read

- **What was wrong.** On Nov 14 the rule for joint fundraising committees (a committee is tied to a member only when that
  member is the one sitting member among the participants its statement of organisation lists) was applied to the joint
  committees that had no tie before. An independent audit of a companion figure found that 44 joint committees tied
  earlier, by the FEC's own link or by an earlier review, had never been read against their statements, and that 13 more
  committees held gifts only in the FEC's API pages and were in no table.
- **What was done.** The statements of all 57 were pulled from the FEC, with the sponsors of 88 leadership PACs, and every
  such committee is now judged from its own statement. Mast Victory Committee was one of the 44: its statement lists
  three participants and one sitting member, so the $17,000 counted for Mast stands. Four committees no longer count for
  any member (one is shared by at least 15 sitting members; two list a participant that is not in the FEC's committee
  list; one filed its statement on paper, which could not be read) and nine enter the count.
- **What moved in this figure.** No chairman's line and not the title's sum ($113,000). The comparison across all 535
  sitting members did: gifts from people who gave Anthropic as employer now reach 154 members and $4,623,749 (was 151
  and $4,529,249), 89 Democrats, 64 Republicans and 1 independent (was 87, 63 and 1). By dollars Mast is 38th of the 154
  (was 36th of 151), Crawford 39th (was 37th) and Moolenaar joint 69th (was joint 66th). Nvidia's figures did not change.
- The note on where the gift lines come from now says 80 lines are taken from the FEC's API because its bulk file does
  not hold them yet (it said 51): the gifts to the 13 committees found only in the API pages are among them.
- `research/employee_gift_rates.csv` now gives, for each company, the number and the sum of negative receipt lines
  (refunds and chargebacks) on the same committees. They are not taken off the sums. The line-by-line list and the table
  of joint committees are published with the companion figure, not here.

## Correction of Nov 14, 2026: gifts to a joint fundraising committee had been missed

- **Crawford's line and the title's sum were too low.** The table that ties committees to members had been built from the
  FEC's committee-to-candidate links, and most joint fundraising committees have none. Crawford Victory Committee, a joint
  committee whose statement of organisation lists Crawford for Congress, his leadership PAC and the NRCC, received $35,000
  on Oct 5, 2026 from one person who gave Anthropic as employer (two lines, $20,000 and $15,000). It is now counted:
  Crawford's line rose from $7,000 from one person to $42,000 from two people, and the sum for the three chairmen from
  $78,000 to $113,000. The line says that a joint committee's money is shared with its other participants and that the
  records do not show how much of it reached the campaign. Mast's and Moolenaar's lines did not change.
- **The counts across Congress changed with it.** The statement of organisation of each of 58 joint committees and the FEC
  record of each of 49 leadership PACs was read. A joint committee is tied to a member only when that member is the one
  sitting member among its participants; nine are attributed to no one. Members with a gift from someone who gave
  Anthropic as employer rose from 134 to 151 of 535 ($3,481,696 to $4,529,249), and the three chairmen's ranks among them
  were recomputed. The same rule applied to Nvidia's employees moved its count from 63 to 65 members.
- The builder found this itself while pulling October's lines for another figure. The corrected version was checked by
  script only; no auditor has read it.

## The published figure (Nov 14, 2026): the ties to Anthropic

- **Nvidia's side is no longer drawn.** The version the audits read set the same records for Nvidia beside Anthropic's
  in every panel, on the timeline and in the title. The published figure is about the ties to Anthropic, so those parts
  were taken out of the drawing: the title names no sum for Nvidia, neither the $0 from its employees nor the $17,500 from
  lobbyists and PACs at its firms. One sentence in the notes says what was left out and gives the three results, and the
  rows stay in the tables. This version was checked by script only.

## Version 3, corrected after the second and third audits (Nov 14, 2026)

- **A gift on Nvidia's side had been missed, and is now counted.** The second audit recounted every lobbyist's gift from
  the Senate's files and found one the builder's rule had dropped: $500 to Mast on Nov 19, 2025 from a lobbyist at a firm
  registered for Nvidia, with the honoree written "MastForCongress". The rule looked for the surname as a separate word.
  It now also accepts a surname that runs straight into "for Congress" (and still refuses Masto and Masters). The sum for
  Nvidia's firms rose from $17,000 to $17,500, Mast's from $13,125 to $13,625, and the title, table, timeline and panel
  were corrected. The title now says "lobbyists and PACs", since the sum includes a firm's own PAC.
- **Each company's own account was added where the other's had been given.** Nvidia's stated reason for opposing the
  Senate's bill, the whole of its "tall tales" remark, its reply to the Times and the report's statement that officials at
  first "did not believe the Nvidia executive knew"; Anthropic's statement that the policies it backs are not for its own
  benefit, and that its chip work is a design team inside a "diversified hardware stack". Quotations the auditor found cut
  short were restored.
- **Three records the auditor found in sources already cited were added:** Mast's committee naming ARI among his bill's
  backers; ARI calling the Senate's version of Moolenaar's bill a "major win"; and Fortune's report that Huang addressed a
  meeting of Mast's committee in 2025.
- **Who funds Public First Action is now stated from the records:** Anthropic is the only donor they identify; the group
  says it has raised more than $80 million and names no donor; its one FEC filing shows no donations; and Anthropic's
  chief executive gave $1 million of his own to a separate super PAC with a similar name.
- **The timeline's marks were redrawn** so that equal dollars take equal areas whatever the shape, and three gifts dated
  2024, which had fallen off the left edge, are now announced in their rows instead.
- **The layout is now two columns.** The first half of the figure (what is at stake, who is who, the table, the timeline)
  is on the left and the second half (each chairman's records, how common the ties are, the notes) is on the right, under
  one title. Nothing else changed with it except four phrases that pointed "below". This was done after the audits; the
  words and the marks are those the audits read.
- **Limits were tightened:** the share of a campaign's receipts is "for scale" where part of the money went to a joint
  committee; Crawford's "no report" lines are bounded to the two bills searched; the letter of Nov 12 mentions a talk with
  Nvidia's staff, and the list of what the record does not show now says so.

## Version 3 as first built (Nov 13, 2026)

- **Lobbyists' own gifts are now counted for both companies by one rule, and the result changed the picture.** Version 2
  said of Nvidia "none on file" under each chairman. That was true of Nvidia's employees and of its PAC, and it was all
  that had been searched. The contribution reports lobbyists file with the Senate were then pulled for all three chairmen
  (2024 to 2026) and read the same way for Nvidia's firms, Anthropic's firms and the firms of the groups in the key.
  Lobbyists and a PAC at firms registered for Nvidia gave the three chairmen more than lobbyists at Anthropic's firms did.
  The title, the at-a-glance table, the timeline and each panel now say so.
- **Crawford gained two records on Anthropic's side** from the same search: gifts in April 2026 from lobbyists at two firms
  then registered for Anthropic.
- **Trade groups were searched.** The PACs of two trade groups that list Nvidia as a member, and not Anthropic, gave Mast
  money; TechNet, which lists both companies, gave none of the three anything. A first reading of TechNet's list took one
  page of five and would have said Nvidia was absent; the whole list was then read.
- **What is at stake is stated.** A band at the top says what each company makes, that each is moving into the other's
  business, where the two have clashed in public over chip export limits, and that Nvidia agreed to buy Anthropic stock.
  Each line is a quotation or a dated record.
- **One shared timeline** replaces three separate strips, with the three chairmen on one scale.
- **An at-a-glance table** puts the three side by side by kind of record.
- **Scale.** Each chairman's campaign receipts are given, and the employees' gifts as a share of them.
- **The ads.** Each of the two ad entries has two versions; both were captured and show the same words. Two frames of each ad
  are in the figure. Google's totals are stated for the entry, not for one video.
- **The hearing.** Jack Clark's written statement and the transcript of the Jun 25, 2025 hearing are now cited, so the
  figure says he testified and quotes what he asked for.
- **Applied from the first audit** (all 21 row findings and 30 figure findings; `audit/DISPOSITIONS.csv`): a firm's
  registration for Anthropic took effect Feb 11, 2026, not in March; "no client directed it" was removed, because a
  lobbyist's report does not show that; witnesses "were listed", since a witness list does not show who appeared; grant
  totals say when an award was an exit grant or for another subject; the foundation that paid Horizon and its fiscal year
  are named; the trust is described in Anthropic's own words as independent; party counts include independents; tied
  ranks are shown as ties; the title says the gifts went to committees; negatives say what was searched and for which
  dates; "every documented tie" became "every tie found, in the records searched".

## Version 2 (Nov 13, 2026)

- **A key was added: "Who is who".** The first draft named groups (Americans for Responsible Innovation, Horizon, the
  Institute for Progress, others) without saying how each connects to Anthropic. The key states each link once, each
  from a cited record, and the panels sort their statements by that link.
- **The ads were found.** The first draft said of Public First Action's announced advertisements: "No saved record shows the
  ad or that it ran." That was wrong. Google's political-ads report, already saved in the builder's evidence, lists a
  30-second video aimed at Rep. Moolenaar's district (Aug 5 to 25, 2026) and one aimed at the 38 zip-code areas of Rep.
  Mast's district (Aug 19 to Sep 2, 2026). Both were opened and played; the words on screen name each chairman. The line
  was replaced by the record.
- **Statements name the firm and the client.** "Lobbyists whose firms had clients in the network" became the firm, the
  client it was registered for at the time, and the date. The lobbyist is not named.
- **The search that found nothing is described exactly:** eleven search terms, the member's official X account, posts since
  January 2025, searched Sep 16, 2026.
- **Each bill is described in its official title's words.**

## Corrections to the count of employees' gifts (all before version 1 was shown)

- **16 recovered lines became 9.** Nine gifts to Banks for Senate were first reported with Anthropic as the donor's employer;
  the committee's amended report leaves that field empty. They are counted from the earlier capture and marked. An early
  run counted 16 such lines: six were duplicates (the FEC's bulk file drops cents, so 143.56 there is 143, and the
  comparison was to the cent) and one went to a committee the counting rule does not tie to a member.
- **Totals rose when the second source was finished.** The first totals for Anthropic (130 members, $3.04 million) were
  quoted before the FEC API had been read to the end. The API holds lines the weekly bulk file lacks. The finished count is
  in the README.
- **One committee rule for every line.** An early run tied a party committee, and a PAC that is not a leadership PAC, to
  single members. The rule now admits only a member's campaign committee, a joint fundraising committee linked to that
  one candidate, or a joint or leadership committee the evidence set had already tied to the member.
- **People are counted by name, not by name and zip code.** One donor with two zip codes was counted twice in an early run.

## Not changed

- Donors and lobbyists are not named, here or in the figure.
- Quoted passages longer than a sentence or two are not copied from sources that are not official records.
