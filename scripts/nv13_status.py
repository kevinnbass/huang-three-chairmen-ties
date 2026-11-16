"""The kicker and the status sentence of the three-chairmen figure (nv13), in one place so that the project's generator and
the public build (build_nv13.py) print the same words."""
KICKER = 'Huang resignation · dated public records, Nov 2026 · draft'
STATUS = ('<b>Status:</b> draft of Nov 14, 2026, third version, corrected after three audits (and on Nov 16: one $1,000 line is a campaign committee\'s, not a lobbyist\'s own, and the counts of pages naming the chairmen are corrected to 93, 81 and 74; the last of these has not been read independently). Each passage behind a drawn item was matched by script to a saved copy of its source. '
          'Three independent audits, by a model from another maker, read the figure and its rows against the saved copies. The first, of the second version: 42 rows passed, 20 were qualified, 1 was wrong, and 30 points were raised on the figure. '
          'The second, of this version before correction: 152 passed, 12 were qualified, 5 were wrong (all five from one missed $500 gift on Nvidia\'s side, now counted), and 25 points were raised. '
          'The third, of the 60 rows added or changed since: 54 passed, 5 were qualified, 1 was wrong (a count the figure does not print), and 8 points were raised. Each finding has a written answer in the repository. '
          'The corrections made after the third audit, and two lines added while it ran, were checked by script only. No audit fetched the originals again, and eight items could not be rechecked from saved copies.')
# The published figure draws the ties to Anthropic only (fig_ties(scope='anthropic')). The fuller version (scope='both') also draws
# the same records for Nvidia: it is the version the three audits read, and it is kept by the builder, not published.
SCOPE = 'anthropic'
STATUS_SOCIAL = ('<b>Status:</b> draft of Nov 14, 2026. Each passage behind a drawn item was matched by script to a saved copy of its source. '
                 'Three independent audits, by a model from another maker, read an earlier, fuller version of this figure, which also drew the same records for Nvidia, and its rows against the saved copies; '
                 'their findings, and what was done about each, are in the repository. This version leaves Nvidia\'s side out of the drawing and was checked by script only. No audit fetched the originals again. '
                 'Corrected on Nov 16, 2026, after independent readings of a companion figure that shares these tables: one $1,000 line in Mast\'s panel is a campaign committee\'s contribution that a lobbyist\'s report lists, '
                 'not a lobbyist\'s own gift as it was worded; and the counts of saved pages naming each chairman were short: by a legal given name (Crawford), by a table and a photo caption that the extraction of two pages\' text had left out, '
                 'by two posts whose text had been taken again from the saved HTML for the companion figure and was still read here in its first, faulty form, and by a live entry that one page\'s HTML holds '
                 '(now Mast 93, Moolenaar 81, Crawford 74). Readings of that figure read the first correction, the given name, the table and the caption and found them right, and the last of them found the two posts; '
                 'the counts as they now stand have not been read independently.')
PUBLISHED_STATUS = STATUS_SOCIAL if SCOPE == 'anthropic' else STATUS
