# The three chairmen who summoned Huang: the records that tie them to Anthropic

**Status: draft.** Every quoted passage has been matched by script to a saved copy of its source, and the numbers in the
figure are recomputed from the tables here by `scripts/verify_nv13.py`. Three independent audits read an earlier, fuller
version of the figure and its rows against the saved copies; what they found, and what was done about each finding, is
under [The audits](#the-audits). A tie is a record with a date. Nothing here says why anyone acted.

![The figure](figures/nv13-three-chairmen.png)

Also as [HTML](figures/nv13-three-chairmen.html) (point at a mark on the timeline to read it) and [JPG](figures/nv13-three-chairmen.jpg).
The image is wide (12,000 pixels): open it and zoom in.

## What this is

On Nov 5 and Nov 12, 2026 the chairmen of three House committees wrote to Jensen Huang, the founder of Nvidia: Brian Mast
(Foreign Affairs), John Moolenaar (the Select Committee on the Chinese Communist Party) and Rick Crawford (Intelligence).
The first letter asked him to brief the committees; the second asked for a transcribed interview on Dec 1, 2026 and said a
subpoena would follow otherwise. The letters followed a New York Times report of Oct 29, 2026, headlined "Nvidia Chief, Jensen Huang, Is Seen as Target of Chinese Spy Plot"; Nvidia told the Times his meetings with a customer's executive were "not unusual or unexpected". The Times report also carries Nvidia's statement that such customers receive "zero information relevant to national security" and that it had "investigated and debunked" claims that the customer was smuggling chips, and says that when the president was first briefed, "U.S. officials did not believe the Nvidia executive knew" of the intelligence gathering the report describes. It adds: "It is unclear whether intelligence officials have since updated their assessment, but some senior officials inside the Trump administration doubt that Mr. Huang could have remained unaware".

An article on X on Nov 12, 2026 alleged that "Anthropic's people overlap with the think tanks, ex-officials and forums behind this coverage."

This repository sets out, for each of the three chairmen, every tie to Anthropic, or to a group linked to it, found in the
records searched, and how common each tie is across Congress. It holds the figure, the tables it is drawn from, a link and
a passage for every source, and a script that checks the numbers. The same search was run on Nvidia's side; the figure
does not draw it, and [What the figure leaves out](#what-the-figure-leaves-out) gives its result.

## The short version

| Whose | Record | Rep. Brian Mast | Rep. John Moolenaar | Rep. Rick Crawford |
|---|---|---|---|---|
| Anthropic | Its employees' own gifts | $43,000 · 5 people | $28,000 · 4 people | $42,000 · 2 people |
| Anthropic | AnthroPAC, its political committee | $2,500 | – | $1,000 |
| Anthropic | Its lobbying reports naming a chip bill he sponsors | 8 reports | 1 report; 2 more name the act with no bill number | – (cosponsors both) |
| Anthropic | Its co-founder testifying to his committee | – | Jun 25, 2025 | – |
| Anthropic | Gifts from lobbyists at its firms | – | – | $6,000 |
| Anthropic | PACs of trade groups that list it and not Nvidia | – (none found) | – (none found) | – (none found) |
| Public First Action (funded by Anthropic) | An ad naming him, by Public First Action | Aug 19 to Sep 2, 2026 | Aug 5–25, 2026 | – (its Arkansas ads name Sen. Cotton) |
| Groups Open Philanthropy has funded | ARI's PAC | $2,500 | $2,500 (to a joint committee) | $1,000 |
| Groups Open Philanthropy has funded | Fellows, advisers and former staff | 2 records | 4 records | – |
| Groups Open Philanthropy has funded | Witnesses listed for his committee's hearings | 6 people | – | – |
| Groups Open Philanthropy has funded | Gifts reported by lobbyists and PACs of their firms | $4,500 | $1,500 | – |
| Groups Open Philanthropy has funded | ARI's public support for a bill of his | his bill (Jan 2026) | the Senate version (Sep 2025) | – |

- **Ads.** Public First Action, to which Anthropic gave $40 million in 2026 (the group says it has raised more than $80
  million, and names no donor), ran video ads naming Mast and Moolenaar. On screen: "backing legislation to put export
  controls on advanced chips" and "tell him to keep fighting to keep advanced chips from going to our enemies". Its
  Arkansas ads name Sen. Tom Cotton, not Crawford.
- **Employees' own money.** People who gave Anthropic as their employer gave committees tied to the three chairmen
  $113,000; $62,000 of it is dated Apr 29 to May 20, 2026.
- **Lobbyists' own money.** Lobbyists at firms then registered to lobby for Anthropic gave $6,000, all of it to Crawford;
  lobbyists and a PAC at firms registered for groups Open Philanthropy has funded gave $6,000.
- **Public support.** ARI, a group Open Philanthropy has funded, is named among the backers of Mast's bill in his
  committee's release, and called the Senate's version of Moolenaar's bill a "major win".
- **Crawford has the fewest records** of the three: 4 of the table's 12 lines hold a record for him, against 9 for
  Mast and 8 for Moolenaar, and all of his are gifts of money: no ad, no bill of his own among the two counted, no fellow,
  adviser or witness. These count kinds of record, not their weight.

## What is at stake between the two companies

| | | |
|---|---|---|
| Nvidia | Chips | It sells AI chips, and two of the chairmen have bills on their export. Mast's, his committee says, "applies long-standing congressional oversight to exports of America's sensitive, military-enhancing AI chips"; it has passed his committee and no further, and Moolenaar's has not left committee. Mast, in the release of Jan 21, 2026: "Companies like Nvidia are requesting to sell millions of advanced AI chips, which are the cutting edge of warfare, to Chinese military companies like Alibaba and Tencent." |
| Nvidia | Now also AI models | It also releases open AI models, with data and tools. Its release of Dec 15, 2025: "NVIDIA is the first to release a collection of state-of-the-art open models, training datasets and reinforcement learning environments and libraries"; the same release describes developers using open models alongside "proprietary models for state-of-the-art reasoning". A trade report of Oct 16, 2026 says its newest models show it "reinforcing its own GPU infrastructure while supporting the open source community." |
| Nvidia | On the Senate's bill | TechSpot, Sep 4, 2025: "Nvidia has since posted a statement opposing the GAIN AI Act. The company says it is comparable to the Biden-era AI Diffusion Rule that was rescinded in May, and part of an attempt to overturn Trump's AI Action Plan". It also reported Nvidia's statement "that H20 sales have not reduced its supply of H100, H200, or Blackwell GPUs". Of that rule Huang had said, as Fortune quoted him on May 2, 2025: "the U.S. semiconductor industry is being pushed out of China, the world's largest market." |
| Anthropic | AI models | It makes the Claude AI models and runs them on other companies' chips: "Currently, Anthropic uses a large number of chips, including Nvidia and AMD GPUs, Google TPUs, and Amazon Trainium hardware" (Data Center Dynamics, Aug 6, 2026). |
| Anthropic | Now also a chip-design team | In Aug 2026 its spokesperson confirmed "that the company was building an in-house silicon team to design custom chips for Claude", calling it "the latest step in our multi-chip approach" and saying the company would continue deploying a "diversified hardware stack". The report is of a design team: it does not describe finished chips, or chips for sale. |
| Anthropic | On export controls | It asks for tighter limits on chip exports. Its co-founder to Moolenaar's committee on Jun 25, 2025, before either House bill was introduced: the government should be "maintaining and strengthening export controls of advanced semiconductors to China". That is its general position, not a statement on either bill. |
| Anthropic | Its own account | Announcing its first gift to Public First Action on Feb 12, 2026, it said of the policies it backs: "Nor are they for the benefit of Anthropic as an AI developer—effective AI governance means more scrutiny of companies like ours, not less." That is the company's statement; no record here tests it. |
| Both | May 1, 2025 | After Anthropic argued for tighter controls and described chip smuggling, an Nvidia spokesperson said American firms should "rise to the challenge, rather than tell tall tales that large, heavy, and sensitive electronics are somehow smuggled in 'baby bumps' or 'alongside live lobsters,'" and: "America cannot manipulate regulators to capture victory in AI." |
| Both | &nbsp; | Anthropic's spokesperson replied: "National security is bigger than the interest of any single company. Anthropic stands by its recently filed public submission in support of strong and balanced export controls". |
| Both | Also partners | Reported on Nov 10, 2026: Anthropic said seven companies, Nvidia among them, had agreed to buy $26 billion of its stock between them, in a private sale at the price of its public offering. Nvidia's own share is not given. Anthropic also runs Claude partly on Nvidia chips. |

## What the records show, in more detail

**Employees' own gifts.** A gift is the donor's own money, not the company's; the FEC line shows the employer the donor
wrote down.

| Chairman | From Anthropic employees | People | Dates | Share of his campaign's receipts (Jan 2025 to Oct 14, 2026) | Rank by dollars from Anthropic employees |
|---|---|---|---|---|---|
| Rep. Brian Mast | $43,000 | 5 | Oct 6, 2025 to May 4, 2026 | 0.8% of $5.1 million | 38 of 154 |
| Rep. John Moolenaar | $28,000 | 4 | Sep 29, 2025 to May 20, 2026 | 1.4% of $2.1 million | joint 69 of 154 |
| Rep. Rick Crawford | $42,000 | 2 | Sep 11, 2025 to Oct 5, 2026 | 3.7% of $1.1 million | 39 of 154 |

These gifts are common. Since January 2025, 154 of the 535 sitting members received a gift from
someone who gave Anthropic as employer ($4.6 million in 788 gifts from 70 people; 89 Democrats, 64 Republicans, 1 independent).

**Lobbyists' own gifts.** Each is reported by the lobbyist, or by the firm for its PAC, as the giver's own contribution. The
reports do not show whether a client asked for it. In brackets: the part given by lobbyists listed for that client.

| Firms then registered to lobby for | Rep. Brian Mast | Rep. John Moolenaar | Rep. Rick Crawford | All three |
|---|---|---|---|---|
| Anthropic | $0 ($0) | $0 ($0) | $6,000 ($3,500) | $6,000 |
| groups Open Philanthropy has funded | $4,500 ($1,000) | $1,500 ($500) | $0 ($0) | $6,000 |

- Crawford, Anthropic's firms: $6,000 in two gifts from lobbyists at firms then registered to lobby for Anthropic. Navigators Global (registered for Anthropic since Feb 2026): $3,500 from a lobbyist listed there for Anthropic, on Apr 15, 2026, to Rural America Counts PAC with him named as honoree. Ballard Partners (registered for Anthropic since Mar 2026): $2,500 from a lobbyist not listed for Anthropic, on Apr 30, 2026. Each is reported as the giver's own contribution; the reports do not show whether a client asked for it.
- Mast, firms of groups in the key: $4,500 in three gifts reported by lobbyists, or the PAC, of firms then registered to lobby for one of these groups. Dentons (registered for the Future of Life Institute since Aug 2023): $1,000 from a campaign committee that a lobbyist there lists in a contribution report and that carries that lobbyist's name (the committee's money, not the lobbyist's own), on Feb 16, 2024; $2,500 from the firm's own PAC (Sep 24, 2025). Kyle House Group (registered for Open Philanthropy Action Fund since Mar 2023): $1,000 from a lobbyist listed there for Open Philanthropy Action Fund, on Sep 25, 2024. Each is reported as the giver's own contribution; the reports do not show whether a client asked for it.
- Moolenaar, firms of groups in the key: $1,500 in two gifts from lobbyists, or the PAC, of firms then registered to lobby for one of these groups. Navigators Global (registered for Americans for Responsible Innovation (ARI) from Feb to Sep 2024): $500 from a lobbyist listed there for Americans for Responsible Innovation (ARI), on Jun 28, 2024. Dentons (registered for the Future of Life Institute since Aug 2023): $1,000 from the firm's own PAC (Mar 3, 2026). Each is reported as the giver's own contribution; the reports do not show whether a client asked for it.

**Trade groups' PACs.** Of three trade groups whose member lists were read, none lists Anthropic and not Nvidia. TechNet lists both (107 members); its PAC gave none of the three anything (FEC records through Sep 2026).

**AnthroPAC.** Anthropic's political committee has paid 78 of the 535 sitting members ($190,250); among the three, Mast and
Crawford.

**Lobbying on their bills.** H.R. 6875, the AI OVERWATCH Act, which he sponsors (introduced Dec 18, 2025), is named in 8 lobbying reports filed for Anthropic and 6 filed for Nvidia. Its official title includes the words "require a license for the export, reexport, or in-country transfer of certain integrated circuits". A report names a bill; it does not say which office was contacted or what was asked.

H.R. 5885, the GAIN AI Act, which he sponsors (introduced Oct 31, 2025), is named in 1 lobbying report filed for Anthropic and 1 filed for Nvidia. Its official title includes the words "certify that United States persons have priority in acquiring those chips". 2 more filed for Anthropic and 2 more filed for Nvidia name the act without a bill number, as Senate amendment 3505 to the defense authorization bill for fiscal 2026 or by name: Anthropic's give the amendment with the act's name (1) and the name alone (1); Nvidia's give the amendment's number alone (2). Sen. Banks submitted the amendment on Aug 1, 2025, and its text carries the act's name as its short title. A report names a bill; it does not say which office was contacted or what was asked.

**The ads as they ran.**

- Moolenaar: Google's political-ads report lists a 30-second video by Public First Action shown from Aug 5, 2026 to Aug 25, 2026, aimed at his district (MI-2). For that entry, which has two versions, Google gives 900,000 to 1,000,000 showings and $25,000 to $30,000 spent. Both versions show the same words: "Congressman John Moolenaar backing legislation to put export controls on advanced chips" and "Call Congressman John Moolenaar. Tell him to keep fighting to keep advanced chips from going to our enemies." The voice-over was not captured.
- Mast: Google's political-ads report lists a 30-second video by Public First Action shown from Aug 19, 2026 to Sep 2, 2026, aimed at 38 Florida zip codes, which are the 38 zip-code areas the Census Bureau maps wholly or partly to his district (FL-21); eleven of them also reach into another district. For that entry, which has two versions, Google gives 800,000 to 900,000 showings and $20,000 to $25,000 spent. Both versions show the same words: "Congressman Brian Mast backing legislation to put export controls on advanced chips" and "Call Congressman Brian Mast. Tell him to keep fighting to keep advanced chips from going to our enemies." The voice-over was not captured.

The frames are in [`sources/ads/`](sources/ads/). Public First Action's announcement of Jul 17, 2026 lists 11 House
Republicans; Crawford is not one of them.

**Who funds the group that ran them.** Anthropic is the only donor the saved records identify: a search on Sep 16, 2026 found no other organisation naming itself as one. On Jun 30, 2026 the group said it had raised more than $80 million, and its announcement named no donor; Anthropic had by then announced $20 million of its $40 million. The FEC lists one filing by the group, a notice of spending on an ad in Mar 2026: it names no donor, and it is not an account of the group's funding. Anthropic's chief executive, Dario Amodei, gave $1 million of his own on May 4, 2026 to Public First, a super PAC: a separate committee, to which the group itself gave $1 million on Feb 24, 2026. Five other people who gave Anthropic as employer gave that committee $2,154,900 in Jun 2026. None of this identifies a donor to the group, and the ads shown in the panels are the group's.

**Public support for the bills.** His committee's release of Jan 21, 2026 says the bill "has received broad support from industry groups including the Foundation for Defense of Democracies Action, American Compass, Americans for Responsible Innovation, the American Security Fund and Exiger."

TechSpot reported on Sep 4, 2025: "Americans for Responsible Innovation calls the GAIN AI Act a "major win" for US economic competitiveness and national security." That was the proposal then in the Senate's defence bill; he introduced the House bill of the same name on Oct 31, 2025.

**A witness.** Jack Clark, then Anthropic's co-founder and head of policy, testified to the House Select Committee on the CCP on Jun 25, 2025; the transcript shows Moolenaar presiding. Clark's written statement says the government should control powerful AI "by maintaining and strengthening export controls of advanced semiconductors to China" and thanks the committee for its "ongoing work to prevent China from obtaining advanced semiconductor chips".

**Groups Open Philanthropy, or its related foundation, has funded.** ARI's PAC gave to all three (to Moolenaar through a
joint fundraising committee); its PACs gave to 115 candidates in all ($279,000, Feb 2025 to Sep 2026). A Horizon fellow is
placed with Mast's committee and another with Moolenaar's; an Institute for Progress fellow is described as senior advisor
to Moolenaar's committee; two former staff members of that committee now work at such groups; a former Mast aide was later
listed as a lobbyist for Open Philanthropy Action Fund; six people from three such groups were listed as witnesses for
hearings of subcommittees of Mast's committee. Each is worded in the figure and sourced in `research/evidence.tsv`.

**Said at the time about Mast's bill.** On the day his committee approved the bill, its release quoted him: "Companies like Nvidia are requesting to sell millions of advanced AI chips, which are the cutting edge of warfare, to Chinese military companies like Alibaba and Tencent." The Register reported that day that the White House's AI adviser, David Sacks, "endorsed a post that speculated that the bill had been orchestrated by "never Trumpers" with financial support from Anthropic CEO Dario Amodei." No record here tests that claim.

**Looked for and not found.** For each of the three, the builder's evidence set records a search of his official X account
for eleven terms (among them Anthropic, Open Philanthropy, Public First, Horizon Institute and Amodei), posts since January
2025, made on Sep 16, 2026, that found no post; the search responses themselves were not saved.

## Who is who: how each group connects to Anthropic

Each line is one record; its source is in `research/evidence.tsv` (rows CK01 to CK25).

| | |
|---|---|
| Anthropic | An AI company. It says it supports "smart export controls on AI chips". |
| Its employees | A gift from an employee is that person's own money. The FEC record shows the employer the donor wrote down. |
| AnthroPAC | Anthropic's own political committee, registered with the FEC on Apr 3, 2026. |
| Its lobbyists | Anthropic and the firms it hires report each quarter which bills they lobbied on. |
| Jack Clark | Listed as Anthropic's co-founder and head of policy on his testimony of Jun 2025. |
| Public First Action | An advocacy group. Anthropic gave it $40 million in 2026 and says the money cannot be used to influence any candidate's election. |
| &nbsp; | One of its founders, Brad Carson, is also the president of Americans for Responsible Innovation (ARI). |
| &nbsp; | Anthropic is the only donor the saved records identify: a search on Sep 16, 2026 found no other organisation naming itself as one. On Jun 30, 2026 the group said it had raised more than $80 million, and its announcement named no donor; Anthropic had by then announced $20 million of its $40 million. The FEC lists one filing by the group, a notice of spending on an ad in Mar 2026: it names no donor, and it is not an account of the group's funding. |
| Open Philanthropy | A grant-maker, renamed Coefficient Giving in Nov 2025. It is a separate organisation from Anthropic, with its own tax return. Three records link the two: |
| &nbsp; | Dustin Moskovitz, listed as a director on its 2024 tax return, took part in Anthropic's Series A funding round in 2021. The records do not show what he holds now. |
| &nbsp; | Luke Muehlhauser, who leads its grants on AI governance and policy, sat on Anthropic's board until May 2024. |
| &nbsp; | Holden Karnofsky, its former chief executive, joined Anthropic's staff in Jan 2025. |
| Americans for Responsible Innovation (ARI) | An advocacy group with its own PAC. $3.4M in awards, 2024–25. |
| Horizon Institute for Public Service | Places fellows in congressional offices and committees. Good Ventures Foundation, which Open Philanthropy's tax return lists as a related organisation, reported paying it $11.8M in its fiscal year ending Jun 2023. |
| Institute for Progress | $12.0M in awards, 2021–26. |
| Center for AI Safety | $12.5M in awards, 2022–23, the last of them a $1.9M exit grant in Oct 2023. |
| Center for a New American Security (CNAS) | $14.6M in awards, 2017–25. Its chief executive, Richard Fontaine, was named in Jun 2025 to Anthropic's Long-Term Benefit Trust, which Anthropic describes as "an independent body of five financially disinterested members" (its page lists four trustees as of Oct 2026). The trust is to elect most of Anthropic's board; Anthropic says that power will "phase in according to time- and funding-based milestones", and that large enough majorities of stockholders can change the trust's powers without the trustees' consent. |
| Carnegie Endowment for International Peace | $2.4M in awards, 2015–26, for several subjects: three of the seven are for research on AI (2022 and 2025). |
| Foundation for American Innovation | $3.7M in awards, 2023–26: $976,000 for AI policy (the 2024 award is an exit grant) and $2.7M in 2026 for energy permitting. |
| Open Philanthropy Action Fund | Listed as a related organisation on Open Philanthropy's 2024 tax return; both 2024 returns list the same president. It hires lobbying firms. |
| Future of Life Institute | $1.9M in awards, 2015–20. |
| &nbsp; | Anthropic's chief executive, Dario Amodei, gave $1 million of his own on May 4, 2026 to Public First, a super PAC: a separate committee, to which the group itself gave $1 million on Feb 24, 2026. Five other people who gave Anthropic as employer gave that committee $2,154,900 in Jun 2026. None of this identifies a donor to the group, and the ads shown in the panels are the group's. |

No record here shows Anthropic directing Open Philanthropy or any of these groups, or any of them directing a member of
Congress. A grant total is what was awarded over the years given; it does not show money still flowing.

## What the records do not show

- Any contact between these members and Anthropic about Huang, or why any of them signed the letters.
- Any contact between the members themselves and Nvidia beyond the letters. The letter of Nov 12 mentions a "conversation
  with NVIDIA staff yesterday" and does not say who took part.
- Why any donor or lobbyist gave, or whether a client asked a lobbyist to give. Anthropic employees gave to 154
  members of both parties.
- Which offices a lobbying report's lobbyists visited, or what they asked for.
- Which of Public First Action's donors paid for the ads. Anthropic says its money to the group cannot be used to influence
  any candidate's election; the ads ask viewers to call the congressman and do not ask for a vote.
- That a grant came with any instruction, or that a past award means money still flows.
- Who on a witness list appeared, except where a transcript is cited.
- The voice-over of the ads: only the words on screen were read, from frames of each video.
- Anything about the truth of the reports on Huang. This repository is not about them.

Not finding a record is not proof that nothing happened.

**Not searched:** trade groups other than the three whose member lists were read (the Semiconductor Industry Association,
the Information Technology Industry Council, TechNet); ads outside Google's report; lobbyists' gifts after June 2026,
whose reports are not yet due; lobbying registrations before 2024 that had ended by then; gifts on which the employer
field does not begin with "Anthropic", and committees not keyed to a member; bills other than the two chip bills; posts on X were
searched only for Anthropic-side terms, up to Sep 16, 2026.

**Two counts an auditor could not redo.** "535" is the number of voting seats in Congress; no roster of the 535 is
published here and vacancies were not checked. Each chairman's count of news pages is this project's own count over its
1,086 saved story pages; `research/story_pages.tsv` lists the pages and which chairman each names, so it can be recounted.

## What the figure leaves out

The same search was run on Nvidia's side, by the same rules, and an earlier version of the figure drew it beside
Anthropic's. This version does not: its subject is the ties to Anthropic. Its notes say so in one sentence, and the rows
are in the tables here (20 rows of `research/nv13_ties.csv` with section `nvidia`, the `nvidia` lines of
`research/nv13_glance.csv`, and the Nvidia-side lines of `research/lobbyist_gifts.csv` and `research/trade_pac_gifts.csv`).
What that search found:

- **Employees and PAC:** nobody who gave Nvidia as employer gave to a committee tied to any of the three, and Nvidia's
  employee PAC has reported no contribution to any sitting member.
- **Lobbyists and PACs at firms registered to lobby for Nvidia:** $17,500 to the three
  (Rep. Brian Mast $13,625, Rep. John Moolenaar $2,875, Rep. Rick Crawford $1,000), against $6,000 from lobbyists at Anthropic's firms.
- **Trade groups:** the PACs of two trade groups that list Nvidia as a member and do not list Anthropic gave Mast
  $4,500.
- **Lobbying reports, a reported meeting, ads:** reports filed for Nvidia name the same two bills, and two more of its
  reports name the GAIN AI Act as a Senate amendment to the defense bill, without a bill number (two of Anthropic's name
  the act without a bill number too); Fortune reported in May
  2025 that Huang addressed a meeting of Mast's committee; Google's political-ads search offers no advertiser named Nvidia.

## Check it yourself

```
python3 scripts/verify_nv13.py
```

recomputes the counts, sums, dates, shares and ranks the figure states from the tables in `research/` and the copies in
`sources/`, checks the two ads against Google's report and the Census Bureau's table, and looks up each of the 294
passages whose source is copied here. It needs only Python. The other 169 passages are a link and the words to find
there (`research/evidence.tsv`).

**One employee's gift.** `research/employee_gifts.csv` has one row per FEC line counted: the committee, the date, the amount,
the employer as filed, and the line's FEC identifiers. `fec_page_url` opens the page of the committee's report that holds
the line. The donors are numbered (`donor_id`), not named: the names are on the FEC's pages, and this repository does not
repeat them.

**One lobbyist's gift.** `research/lobbyist_gifts.csv` has one row per gift counted: the firm, the client it was registered
for and from when, the date, the amount, the committee paid, the honoree as the filer wrote it, and `report_url`, the
contribution report on the Senate's site. Lobbyists are numbered within each side, not named.

**The figure.**

```
pip install playwright pillow && playwright install chromium
python3 scripts/build_nv13.py        # writes figures/nv13-three-chairmen.html, .png, .jpg from research/
```

## How the employees' gifts were counted

1. **The rule.** An FEC line counts if it is from an individual, the employer as filed begins with the company's name
   (ANTHROPIC or NVIDIA), it is not a memo line, the amount is above zero, it is dated Jan 1, 2025 or later, and the
   receiving committee is tied to a sitting member: his principal or authorised campaign committee by the FEC's own
   committee-candidate links, a joint fundraising committee linked to that one candidate, or a joint or leadership
   committee the builder's evidence set had tied to him (`research/committee_keys.csv` gives the basis for each of the
   270 committees). The same rule, the same files and the same code for both companies.
2. **The sources.** The FEC's bulk file of itemised individual contributions for the 2026 cycle, downloaded Nov 13, 2026
   (36,691,128 lines scanned; sha256 of the file `436528f8563dbafaa6dd2e21f885d923fe67097e6adf0d2b517cafb92b83ab7c`), and the
   same lines read from the FEC's API to the end for both companies. The API holds 80 Anthropic and 21 Nvidia lines the
   weekly file does not have yet; for 8 more its later filing replaces the file's copy.
3. **Nine lines the current record no longer ties to Anthropic.** 9 gifts to Banks for Senate in April 2026 ($31,500) were
   reported on the committee's original second-quarter report with ANTHROPIC as the donors' employer. Its amended report
   (FEC file 2011599) leaves the employer empty on those lines and keeps the occupation. They are counted here from the
   earlier capture and marked `earlier-capture`; each row gives the page image of both filings (`fec_page_url`,
   `amended_fec_page_url`). Without them the Anthropic total is $4.6 million in 779 gifts; the number of members is unchanged.
   The builder holds no earlier capture of a Nvidia line, so a Nvidia line blanked the same way would be missed.
4. **Limits.** A gift to a committee not tied to one member (a party committee, most PACs) is not counted. A line whose
   employer field does not begin with the company's name is not counted. People are counted by name. The bulk file
   carries whole dollars.

## How the lobbyists' gifts were counted

1. **The files.** Every contribution report (form LD-203) in the Senate's lobbying records with an item whose honoree
   matches Mast, Moolenaar or Crawford, filing years 2024 to 2026, pulled on Nov 13, 2026; and each company's lobbying
   filings for 2024 to 2026. The 31 gifts counted are in `research/lobbyist_gifts.csv`.
2. **The rule.** An item counts if its honoree is one of the three (strings naming another Crawford are refused), and the
   report was filed by a registrant, or by a lobbyist it employs, that had a lobbying registration for the client on the
   day of the gift. Three sides are read the same way: Nvidia's registrants, Anthropic's registrants, and firms registered
   for the groups in the key.
3. **Listed or not.** A lobbyist is "listed" for a client from the first quarter a filing names him or her for it to 90
   days after the last. A gift by another lobbyist at the firm, or by the firm's PAC, is counted and marked as such. A
   group's own PAC (ARI's) is counted as its PAC, not as a lobbyist's gift.
4. **Limits.** A large firm has many clients, so a gift by a lobbyist not listed for the client is a weak tie. Reports for
   the second half of 2026 are not yet due. A gift that names several honorees would be marked as a shared event; none
   was found. The same gift appears in more than one pull and in amended reports: it is counted once.

## The audits

The three audits read an earlier, fuller version of the figure, which drew the same records for Nvidia beside Anthropic's.
The figure published here leaves Nvidia's side out of the drawing; every record it shows is a row those audits read, or
one of the rows corrected after the third audit that are listed below. This version itself was checked by script only
(`scripts/verify_nv13.py`). The audit reports and the dispositions therefore also speak of rows that are in the tables
and not in the figure.

An auditor from a different model family (GPT-6.1 Sol, run through Codex with no network access) read the rows against the
saved originals, read the figure element by element, and recounted with its own scripts.

- **Round 1** (the second version): 63 rows read against the saved originals: 42 ok, 20 qualifications, 1 errors; 30 points on the figure. Closing line: `audit: incomplete originals not re-fetched`. Files: `audit/round1/`.
- **Round 2** (the third version, before the corrections listed in CHANGES.md): 169 rows read against the saved originals: 152 ok, 12 qualifications, 5 errors; 25 points on the figure. Closing line: `audit: incomplete originals not re-fetched`. Files: `audit/round2/`.
- **Round 3** (the corrected third version: the rows added or changed since round 2, and the whole figure again): 60 rows read against the saved originals: 54 ok, 5 qualifications, 1 errors; 8 points on the figure. Closing line: `audit: incomplete originals not re-fetched`. Files: `audit/round3/`.

Each of the 128 findings and gaps of the three rounds that was not graded ok has one written disposition (107 applied, 18 stated as a limit, 3 applied in part): `audit/DISPOSITIONS.csv`.

**After the third audit.** Its findings were applied, and those changes were checked by script against the saved copies but not read by an auditor: the key lines on who funds Public First Action (CK09, CK23), the fuller account of the Times report (CK25), Nvidia's statement on chip supply (CS03), the two timeline labels that now say "announces" (CE21, CE22), the corrected count for TechNet's PAC (CN78), the heading of Anthropic's card, and the timeline's marks. Two changes were made while the third audit was running and are in the same position: the full sentence on Nvidia's reason (CS03), and the line quoting Anthropic's own statement that its policies are not for its benefit (CS10), which the second audit's report asked for in an addendum that has no finding number.

**What no audit could recheck.** Eight items: the responses of three searches of X and of one search for other donors to Public First Action (the evidence set records the searches; the responses were not saved); each chairman's count of news pages (the auditors were not given the page list, which is in `research/story_pages.tsv`); and the roster behind "535". No audit fetched an original again: each closes `audit: incomplete originals not re-fetched`.

No audit fetched the originals again, so a source that has changed since it was saved would not be caught.

## What is in this repository

| Path | What |
|---|---|
| `figures/` | the figure as .png, .jpg, .html |
| `research/evidence.tsv` | one line per cited source of every row of the figure: what it is, its link, the passage, when it was saved, and where a copy sits in this repository if one does |
| `research/nv13_ties.csv` | the 40 records in the three panels, as worded in the figure, and 20 rows of section `nvidia` from the same search of Nvidia's side, which the figure does not draw |
| `research/nv13_key.csv`, `grants_cited.csv` | the key's 25 lines, and the grant rows behind its totals |
| `research/nv13_stake.csv`, `nv13_events.csv` | the 10 lines on what is at stake, and the dated events on the timeline |
| `research/nv13_numbers.csv`, `nv13_glance.csv` | every number computed for the figure, and the at-a-glance table |
| `research/employee_gifts.csv` | all 1,321 counted gift lines, both companies, with FEC identifiers and a link to each page image; no names |
| `research/lobbyist_gifts.csv` | the 31 counted gifts by lobbyists and firm PACs, with a link to each report; no names |
| `research/trade_pac_gifts.csv` | gifts to the three from the PACs of trade groups whose member lists were read, with a link to each FEC page |
| `research/employee_gift_rates.csv`, `committee_keys.csv` | the totals across the 535 members; each committee and the member it is tied to |
| `research/pacs_by_member.csv`, `pac_base_rates.csv`, `pac_lines.csv` | company PAC money by member, from FEC filings |
| `research/lobbying_bill_reports.csv`, `lobbying_filings.csv`, `chip_bills.csv`, `chip_bill_backers.csv` | lobbying reports naming each chip-export bill (with a link to each report), and the bills |
| `research/lobbying_family_reports.csv` | for each company and each of the five chip-export measures, the reports that name it by a bill number, by a Senate amendment's number, or by name only (added Nov 17, 2026) |
| `research/story_pages.tsv` | the addresses of the 1,086 saved news pages behind "named on N pages", and which name each chairman; no page text |
| `research/nv13_frames/` | the four ad frames the figure shows |
| `sources/` | copies of sources that are official records or the builder's own captures: the committees' release, post and letter; the hearing statement and transcript; FEC candidate totals, committee records, the one filing by Public First Action, and the committee-to-candidate lines for ARI's and the trade groups' PACs; the three trade groups' member lists as read; Google's report lines, ad pages and frames; the Census rows for the district |
| `audit/` | both audit rounds (brief, report, findings, recount) and the disposition of every finding |
| `scripts/` | `build_nv13.py` and `verify_nv13.py` run on this copy; `as_built/` holds the scripts as they were run, which need the builder's evidence sets and downloads |
| `CHANGES.md` | what changed between drafts, and every error found on the way |

Sources that are not official records (news reports, the companies' and other organisations' pages, the article on X) are
linked and quoted in a sentence or two; they are not copied. The frames of the ads are reproduced as evidence of what the
ads say.

## Who made this

The figure, the tables, the scripts and this file were drafted with Claude, a model made by Anthropic, working at the
direction of the repository's owner. Anthropic is the subject of the figure. For that reason every statement is tied to
a record a reader can open, the work was audited by another company's model, the same search was run on Nvidia's side
and its result is stated in the figure's notes and above, and the corrections made on the way are listed in
[`CHANGES.md`](CHANGES.md).
