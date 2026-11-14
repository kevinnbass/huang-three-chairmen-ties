"""Render the three-chairmen figure (figures/nv13-three-chairmen.html, .png, .jpg) from the tables in research/.
Run: python3 scripts/build_nv13.py
Needs Python 3.10 or later, playwright with its chromium browser (pip install playwright; playwright install chromium)
and pillow. Everything the figure draws is in research/: nv13_ties.csv, nv13_key.csv, nv13_stake.csv, nv13_events.csv,
nv13_numbers.csv, nv13_glance.csv, lobbyist_gifts.csv, employee_gifts.csv, nv13_members.csv and the four frames in nv13_frames/."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fig_ties, nv13_status

if __name__ == '__main__':
    fig_ties.fig_ties(nv13_status.KICKER, nv13_status.PUBLISHED_STATUS, scope=nv13_status.SCOPE, stem='nv13-three-chairmen')
