"""nv13, third version: the three House chairmen who signed the letters to Jensen Huang.
What is at stake between Anthropic and Nvidia; who is who; an at-a-glance table; one shared timeline; then one panel per
chairman listing every record found that ties him to Anthropic or a group linked to it, and the same records for Nvidia.
Everything drawn comes from the tables build_chairmen.py writes (rows_chairmen.py) and research/employee_gifts.csv.
A tie is a dated record, not a motive. Donors and lobbyists are counted, never named."""
import base64, datetime, io, math
from collections import defaultdict

import rows_chairmen as C
import rows_ties as T
from fig_common import *

PAGE = 3000
A_COL = '#d95a2b'; N_COL = '#2a78d6'; W_COL = '#b0499b'
D0 = datetime.date(2025, 1, 1); D1 = datetime.date(2026, 11, 30)
MARK = {'A': A_COL, 'W': W_COL, 'N': N_COL, 'G': GRAY}
THREE = ['mast', 'moolenaar', 'crawford']
# Layout. 'wide': the title across the top, then two columns side by side, each as wide as the tall page's content: on the left what
# sets the scene (the stake, the key, the table, the timeline), on the right the records chairman by chairman, the tiles and the footnote.
# 'tall': the same parts in one column, as first published. The words and the marks are the same in both.
LAYOUT = 'wide'; WIDE = 2 * PAGE
SECT = [('anthropic', 'Anthropic itself', '', A_COL), ('pfa', 'Public First Action', 'Anthropic gave it $40 million', A_COL),
        ('network', 'Groups Open Philanthropy, or its related foundation, has funded', '', W_COL),
        ('said', 'Said in public about his bill', '', AXIS), ('nvidia', 'The same records for Nvidia', '', N_COL), ('searched', 'Looked for, none found', '', AXIS)]
GROUPS = {'anthropic': ('Anthropic itself', A_COL), 'pfa': ('Public First Action · Anthropic gave it $40 million', A_COL),
          'network': ('Groups Open Philanthropy, or its related foundation, has funded', W_COL), 'nvidia': ('Nvidia · the same records', N_COL)}
FRAME_BOX = {'mast': (0, 10, 583, 370), 'moolenaar': (0, 10, 640, 370)}      # the video inside each saved frame (the Florida page shows its own controls to the right)


def xd(d, x0, w):
    return x0 + w * (datetime.date.fromisoformat(d) - D0).days / (D1 - D0).days


def ordinal(v):
    j, n = ('joint ', v[6:]) if v.startswith('joint ') else ('', v)
    suf = 'th' if n[-2:] in ('11', '12', '13') else {'1': 'st', '2': 'nd', '3': 'rd'}.get(n[-1], 'th')
    return f'{j}{n}{suf}'


def frame_uri(member, tag):
    im = Image.open(C.R / 'nv13_frames' / f'{member}-{tag}.png').convert('RGB').crop(FRAME_BOX[member])
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=86)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def timeline(gifts, lob, trade, ties, events, who, N, nvidia=True):
    """One shared timeline. A lane for events that concern everyone, then a lane per chairman with three rows:
    money from Anthropic's side, money from Nvidia's side, and dated public events. Area follows the amount."""
    W = PAGE - 120; LAB = 262; x0 = LAB; ww = W - LAB - 34
    TOP = 34; ALL_H = 164; LH = 318 if nvidia else 264
    H = TOP + ALL_H + LH * 3 + 6
    R_ = lambda usd: 3.6 * math.sqrt(float(usd) / 500)                 # no smallest size: a $125 gift is a quarter of the area of a $500 one
    s = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    lane_y = {m: TOP + ALL_H + i * LH for i, m in enumerate(THREE)}
    d = D0
    while d <= D1:                                                 # month ticks, a label each quarter
        x = xd(d.isoformat(), x0, ww)
        if d.month in (1, 4, 7, 10):
            s += f'<line x1="{x:.1f}" y1="{TOP - 8}" x2="{x:.1f}" y2="{H - 6}" stroke="{GRID}" stroke-width="1"/><text x="{x + 4:.1f}" y="{TOP - 14}" font-size="14" fill="{MUTED}">{MONTHS[d.month - 1]} {d.year}</text>'
        d = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)

    # the three weeks in which most of the employees' money arrived, and the six weeks of most of the Nvidia-side gifts to Mast
    HALO = f'stroke="{CARD}" stroke-width="5" paint-order="stroke" stroke-linejoin="round"'
    xa, xb = xd('2026-04-29', x0, ww), xd('2026-05-20', x0, ww)
    for m_ in ('mast', 'moolenaar'):
        s += f'<rect x="{xa - 30:.1f}" y="{lane_y[m_] + 36}" width="{xb - xa + 60:.1f}" height="120" fill="{A_COL}" fill-opacity="0.10" rx="8"/>'
    s += (f'<text x="{xa - 40:.1f}" y="{lane_y["mast"] + 58}" font-size="15" fill="{INK}" text-anchor="end" {HALO}><tspan font-weight="bold">Apr 29 to May 20, 2026:</tspan> '
          f'{esc(money(float(N["emp:anthropic:three:window"]["value"])))} of the {esc(money(float(N["emp:anthropic:three"]["value"])))} that Anthropic employees gave the three chairmen arrived in these three weeks</text>')
    xc, xe = xd('2025-11-17', x0, ww), xd('2025-12-31', x0, ww)
    if nvidia:
      s += f'<rect x="{xc - 30:.1f}" y="{lane_y["mast"] + 158}" width="{xe - xc + 60:.1f}" height="58" fill="{N_COL}" fill-opacity="0.10" rx="8"/>'
    if nvidia:
      s += (f'<text x="{xc - 40:.1f}" y="{lane_y["mast"] + 176}" font-size="15" fill="{INK}" text-anchor="end" {HALO}><tspan font-weight="bold">Nov 17 to Dec 31, 2025:</tspan> '
            f'{esc(money(float(N["lob:nvidia:mast:window"]["value"])))} of the {esc(money(float(N["lob:nvidia:mast:total"]["value"])))} that lobbyists and a PAC at Nvidia\'s firms gave Mast</text>')
    def labels(evs, base, rows, dy=21):
        """Ticks on a base line with a label each. A label takes the first row where it touches no other label; tick lines
        are drawn first and each label carries a halo, so a line that passes a label runs behind it."""
        out = f'<line x1="{x0}" y1="{base}" x2="{x0 + ww}" y2="{base}" stroke="{AXIS}" stroke-width="1.5"/>'; txts = ''
        put = []                                                     # (row, left edge, right edge)
        for e in sorted(evs, key=lambda e: e['date']):
            x = xd(e['date'], x0, ww); txt = f'{day(e["date"], True)} · {e["words"]}'
            if e['end']:
                txt = f'{day(e["date"])} to {day(e["end"], True)} · {e["words"]}'
            wid = 7.3 * len(txt) + 10
            for r, left in [(r, lf) for r in range(rows) for lf in (False, True)]:
                a, b = (x - 8 - wid, x - 8) if left else (x + 8, x + 8 + wid)
                if a >= x0 + 4 and b <= x0 + ww and all(pr != r or b < pa - 8 or a > pb + 8 for pr, pa, pb in put):
                    put.append((r, a, b)); break
            else:
                raise AssertionError(('no free place for an event label', e['date'], e['words']))
            ty = base + 22 + dy * r
            out += f'<line x1="{x:.1f}" y1="{base}" x2="{x:.1f}" y2="{ty - 5}" stroke="{INK}" stroke-width="1.2" opacity="0.5"/>'
            if e['end']:
                x2 = xd(e['end'], x0, ww)
                out += f'<rect x="{x:.1f}" y="{base - 6}" width="{x2 - x:.1f}" height="12" rx="3" fill="{A_COL}"/>'
            else:
                out += f'<circle cx="{x:.1f}" cy="{base}" r="4.2" fill="{INK}"/>'
            p = txt.split(' · ', 1)
            txts += (f'<text x="{(x - 8) if left else (x + 8):.1f}" y="{ty}" font-size="14" fill="{INK}" text-anchor="{"end" if left else "start"}" {HALO}>'
                     f'<tspan fill="{MUTED}">{esc(p[0])}</tspan> · {esc(p[1])}</text>')
        return out + txts
    s += f'<text x="0" y="{TOP + 36}" font-size="19" font-weight="bold" fill="{INK}">Both companies,</text><text x="0" y="{TOP + 58}" font-size="19" font-weight="bold" fill="{INK}">and all three</text>'
    s += labels([e for e in events if e['lane'] == 'all'], TOP + 30, 5)
    for m in THREE:
        Y = lane_y[m]; ya, yn, ye = Y + 96, Y + 186, (Y + 236 if nvidia else Y + 182)
        s += f'<line x1="0" y1="{Y + 8}" x2="{W}" y2="{Y + 8}" stroke="{AXIS}" stroke-width="1.5"/>'
        s += f'<text x="0" y="{Y + 38}" font-size="21" font-weight="bold" fill="{INK}">{esc(who[m]["name"])}</text><text x="0" y="{Y + 58}" font-size="13.5" fill="{MUTED}">{esc(who[m]["role"])}</text>'
        for y, lab, col in ((ya, 'Anthropic, and groups in the key', A_COL), (yn, 'Nvidia\'s firms and trade groups', N_COL))[:2 if nvidia else 1]:
            s += f'<line x1="{x0}" y1="{y}" x2="{x0 + ww}" y2="{y}" stroke="{GRID}" stroke-width="1.5"/><text x="{LAB - 14}" y="{y + 5}" text-anchor="end" font-size="14.5" fill="{col}" font-weight="bold">{esc(lab)}</text>'
        s += f'<text x="{LAB - 14}" y="{ye + 5}" text-anchor="end" font-size="14.5" fill="{MUTED}">On the public record</text>'
        marks = {'a': [], 'n': []}                                   # (date, usd, shape, colour, tooltip)
        for g in gifts:
            if g['member'] == m and g['side'] == 'anthropic':
                marks['a'].append((g['date'], g['usd'], 'circle', A_COL, f'{day(g["date"], True)}: {money(float(g["usd"]))} from a person who gave Anthropic as employer, to {g["committee"].title()}'))
        for t in ties:
            if t['member'] == m and t['type'] in ('company_pac', 'ari_pac') and t['usd']:
                marks['a'].append((t['first'], t['usd'], 'square', A_COL if t['type'] == 'company_pac' else W_COL, t['words']))
        for r in lob:
            if r['member'] != m or r['measure'] == 'own_pac':
                continue
            col = {'anthropic': A_COL, 'network': W_COL, 'nvidia': N_COL}[r['side']]
            marks['n' if r['side'] == 'nvidia' else 'a'].append((r['date'], r['amount_usd'], 'square' if r['measure'] == 'firm_pac' else 'diamond', col,
                                                                 f'{day(r["date"], True)}: {money(float(r["amount_usd"]))}, {"the firm\'s PAC" if r["measure"] == "firm_pac" else "a lobbyist"} at {r["registrant"].title()}'))
        for x_ in trade:
            if x_['member'] == m and x_['lists_nvidia'] == 'yes' and x_['lists_anthropic'] == 'no':
                marks['n'].append((x_['date'], x_['usd'], 'square', N_COL, f'{day(x_["date"], True)}: {money(float(x_["usd"]))}, the PAC of {x_["group_name"]}'))
        for row, y in (('a', ya), ('n', yn))[:2 if nvidia else 1]:
            placed = []
            early = [k for k in marks[row] if k[0] < D0.isoformat()]
            if early:
                yrs = sorted({k[0][:4] for k in early}); assert yrs == ['2024'], yrs
                s += (f'<text x="{x0 + 8}" y="{y + 22}" font-size="13.5" fill="{MUTED}" {HALO}>◂ not drawn: {len(early)} gift{"s" if len(early) != 1 else ""} dated 2024 '
                      f'({esc(money(sum(float(k[1]) for k in early)))}), listed in his panel</text>')
            for dte, usd, shape, col, tip in sorted((k for k in marks[row] if k[0] >= D0.isoformat()), key=lambda k: (k[0], -float(k[1]))):
                r = R_(usd); x = xd(dte, x0, ww)
                rr = r * (math.sqrt(math.pi / 2) if shape == 'diamond' else 1.0)          # the mark's reach, for spacing
                lim = 56 if row == 'a' else 26
                # the nearest free place: above or below the row's line first, then up to a few days to either side
                spots = sorted(((dx, off) for dx in (0, -8, 8, -16, 16, -24, 24, -32, 32, -40, 40) for off in range(-lim, lim + 1, 2)), key=lambda k: abs(k[0]) * 1.4 + abs(k[1]))
                for dx, off in spots:
                    if abs(off) + r <= lim + 2 and all((x + dx - px) ** 2 + (y + off - py) ** 2 > (rr + pr + 1.6) ** 2 for px, py, pr in placed):
                        break
                else:
                    raise AssertionError(('no free place for a mark', m, dte))
                x += dx; cy = y + off; placed.append((x, cy, rr))
                if shape == 'circle':
                    s += f'<circle cx="{x:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{col}" fill-opacity="0.85" stroke="{BG}" stroke-width="1.5" paint-order="stroke"><title>{esc(tip)}</title></circle>'
                elif shape == 'square':
                    q = r * math.sqrt(math.pi) / 2
                    s += f'<rect x="{x - q:.2f}" y="{cy - q:.2f}" width="{2 * q:.2f}" height="{2 * q:.2f}" fill="{col}" fill-opacity="0.9" stroke="{BG}" stroke-width="1.5" paint-order="stroke"><title>{esc(tip)}</title></rect>'
                else:
                    q = r * math.sqrt(math.pi / 2)
                    s += f'<path d="M{x:.2f},{cy - q:.2f} L{x + q:.2f},{cy:.2f} L{x:.2f},{cy + q:.2f} L{x - q:.2f},{cy:.2f} Z" fill="{col}" fill-opacity="0.9" stroke="{BG}" stroke-width="1.5" paint-order="stroke"><title>{esc(tip)}</title></path>'
            if not marks[row]:
                s += f'<text x="{x0 + 8}" y="{y - 8}" font-size="14" fill="{MUTED}">none found</text>'
        s += labels([e for e in events if e['lane'] == m], ye, 3)
    return s + '</svg>'


def stake_band(stake):
    by = defaultdict(list)
    for k in stake:
        by[k['card']].append(k)
    line = lambda k: f'<div class="kl">{"<b>" + esc(k["label"]) + ".</b> " if k["label"] else ""}{esc(k["words"])}</div>'
    card = lambda col, kh, kn, ks: (f'<div class="kc" style="border-top-color:{col}"><div class="kh">{esc(kh)}</div><div class="kn">{esc(kn)}</div>' + ''.join(line(k) for k in ks) + '</div>')
    return ('<div class="h2">What is at stake between the two companies</div><div class="stk">'
            + card(N_COL, 'The chip maker, now also releasing AI models', 'Nvidia', by['nvidia'])
            + card(A_COL, 'The AI model maker, now building a chip-design team', 'Anthropic', by['anthropic'])
            + card(INK, 'Where the two have met in public', 'Clash, and partnership', by['clash']) + '</div>')


def key_band(links):
    """Who is who: how each group named in the panels connects to Anthropic. One record per line (research/nv13_key.csv)."""
    by = defaultdict(list)
    for k in links:
        by[k['card']].append(k)
    line = lambda k: f'<div class="kl">{"<b>" + esc(k["label"]) + ".</b> " if k["label"] else ""}{esc(k["words"])}</div>'
    a = by['anthropic']; pf = by['pfa']; op = by['op']; gr = by['op_group']
    c1 = (f'<div class="kc" style="border-top-color:{A_COL}"><div class="kh">Anthropic itself</div><div class="kn">{esc(a[0]["label"])}</div><div class="kl">{esc(a[0]["words"])}</div>'
          + ''.join(line(k) for k in a[1:]) + '</div>')
    c2 = (f'<div class="kc" style="border-top-color:{A_COL}"><div class="kh">A group Anthropic funds</div><div class="kn">{esc(pf[0]["label"])}</div><div class="kl">{esc(pf[0]["words"])}</div>'
          + ''.join(line(k) for k in pf[1:]) + '</div>')
    nums = ''.join(f'<div class="kl" style="display:grid;grid-template-columns:26px 1fr"><b style="color:{W_COL}">{i}</b><span>{esc(k["words"])}</span></div>' for i, k in enumerate(op[1:], 1))
    groups = ''.join(f'<div class="kg"><b>{esc(k["label"])}.</b> {esc(k["words"])}</div>' for k in gr)
    c3 = (f'<div class="kc" style="border-top-color:{W_COL}"><div class="kh">Open Philanthropy, and groups it or its related foundation has funded</div>'
          f'<div style="display:grid;grid-template-columns:0.82fr 1.6fr;gap:30px"><div><div class="kn">{esc(op[0]["label"])}</div><div class="kl">{esc(op[0]["words"])}</div>{nums}</div>'
          f'<div><div class="kl" style="margin-top:2px;color:{MUTED}">Groups named in the panels, with what the grant records show. A total is what was awarded over the years given; it does not show money still flowing.</div>'
          f'<div style="display:grid;grid-template-columns:1fr 1fr;column-gap:26px">{groups}</div></div></div></div>')
    return (f'<div class="h2">Who is who: how each group named in the panels connects to Anthropic</div>'
            f'<div class="key">{c1}{c2}{c3}</div>'
            f'<div style="font-size:16.5px;color:{MUTED};margin:-8px 0 22px">No record here shows Anthropic directing Open Philanthropy or any of these groups, or any of them directing a member of Congress.</div>')


def glance_table(glance, who, N, nvidia=True):
    head = ''.join(f'<th>{esc(who[m]["name"])}</th>' for m in THREE)
    glance = [r for r in glance if nvidia or r['group'] != 'nvidia']
    body = ''; last = None
    for r in glance:
        if r['group'] != last:
            title, col = GROUPS[r['group']]
            body += f'<tr class="gh"><td colspan="4" style="border-left:8px solid {col}">{esc(title)}</td></tr>'; last = r['group']
        col = GROUPS[r['group']][1]

        def cell(v):
            return f'<td class="{"q" if C.quiet(v) else "v"}">{esc(v)}</td>'
        body += f'<tr><td class="l" style="border-left:8px solid {col}">{esc(r["label"])}</td>' + ''.join(cell(r[m]) for m in THREE) + '</tr>'
    h = lambda sd, m: int(N[f'glance:held:{sd}:{m}']['value'])
    last_name = lambda m: who[m]['name'].split()[-1]
    assert [last_name(m) for m in THREE] == ['Mast', 'Moolenaar', 'Crawford'] and h('aside', 'crawford') < min(h('aside', 'mast'), h('aside', 'moolenaar'))
    count = (f'<div style="font-size:17px;line-height:1.4;margin:10px 0 0"><b>Counting the lines that hold a record:</b> on the side of Anthropic and the groups in the key, '
             f'Mast has {h("aside", "mast")} of {N["glance:lines:aside"]["value"]}, Moolenaar {h("aside", "moolenaar")} and Crawford {h("aside", "crawford")}, the fewest, all of them gifts of money. '
             + (f'On Nvidia\'s side Mast has {h("nvidia", "mast")} of {N["glance:lines:nvidia"]["value"]}, Moolenaar {h("nvidia", "moolenaar")} and Crawford {h("nvidia", "crawford")}. ' if nvidia else '') +
             f'<span style="color:{MUTED}">A count of kinds of record, not of their weight.</span></div>')
    return (f'<div class="h2">At a glance: what the records hold for each chairman</div>'
            f'<table class="gl"><tr><th></th>{head}</tr>{body}</table>{count}')


def fig_ties(KICKER, DRAFT, partial=False, scope='both', stem=None):
    """scope 'anthropic': the published figure, the ties to Anthropic; it leaves Nvidia's side out of the drawing and says so in its
    notes (stem nv13-three-chairmen). scope 'both': the fuller version, with the same records for Nvidia, which the audits read
    (stem nv13-three-chairmen-full). Both are drawn from the same rows."""
    NV = scope == 'both'; assert scope in ('both', 'anthropic')
    ties = C.ties(); links = C.key(); stake = C.stake(); events = C.events(); N = C.numbers(); glance = C.glance(); lob = C.lobbyist_gifts()
    gifts = [g for g in T.gifts() if g['member'] in THREE]
    who = T.members(); assert list(who) == THREE, 'run build_member_ties.py first: research/nv13_members.csv is missing or stale'
    n = lambda k: N[k]['value']
    css = (f'.pn{{background:{CARD};border-radius:12px;padding:20px 22px 16px}}.nm{{font-size:30px;font-weight:bold;letter-spacing:-.6px}}.rl{{font-size:16.5px;color:{MUTED};margin:2px 0 6px;line-height:1.35}}'
           f'.h2{{font-size:24px;font-weight:bold;margin:26px 0 10px}}'
           f'.sec{{font-size:14px;font-weight:bold;letter-spacing:1.6px;text-transform:uppercase;color:{MUTED};margin:18px 0 4px;padding-top:7px;border-top:3px solid {AXIS}}}'
           f'.sec span{{font-weight:normal;letter-spacing:.2px;text-transform:none;font-size:15px}}'
           f'.tr{{display:grid;grid-template-columns:16px 1fr;column-gap:10px;padding:7px 0;border-top:1px solid {GRID};font-size:16px;line-height:1.36}}.sec+.tr{{border-top:0}}'
           f'.tr b{{font-size:16px}}.mk{{width:13px;height:13px;border-radius:3px;margin-top:4px}}.mut{{color:{MUTED}}}'
           f'.fr{{display:flex;gap:10px;margin:4px 0 6px 26px}}.fr img{{height:214px;border-radius:6px;display:block}}.frc{{font-size:13.5px;color:{MUTED};margin:0 0 8px 26px}}'
           f'.tile{{background:{CARD};border-radius:10px;padding:14px 18px}}.big{{font-size:40px;font-weight:bold;letter-spacing:-1.2px;line-height:1}}.cap{{font-size:15.5px;color:{MUTED};line-height:1.34;margin-top:6px}}'
           f'.key{{display:grid;grid-template-columns:0.9fr 0.72fr 2.5fr;gap:22px;margin:0 0 18px;align-items:stretch}}.stk{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;margin:0 0 6px;align-items:stretch}}'
           f'.kc{{background:{CARD};border-radius:12px;padding:14px 20px 16px;border-top:7px solid {AXIS}}}'
           f'.kh{{font-size:13.5px;letter-spacing:1.6px;text-transform:uppercase;font-weight:bold;color:{MUTED};margin-bottom:5px}}.kn{{font-size:23px;font-weight:bold;letter-spacing:-.3px}}'
           f'.kl{{font-size:16px;line-height:1.38;margin-top:7px}}.kg{{font-size:15.5px;line-height:1.36;padding:6px 0;border-top:1px solid {GRID}}}'
           f'.gl{{border-collapse:collapse;width:100%;font-size:17px;table-layout:fixed}}.gl th{{text-align:left;font-size:19px;padding:6px 14px;border-bottom:2px solid {AXIS}}}'
           f'.gl td{{padding:6px 14px;border-bottom:1px solid {GRID}}}.gl td.l{{color:{INK}}}.gl th:first-child{{width:34%}}.gl td.v{{font-weight:bold}}.gl td.q{{color:{MUTED}}}'
           f'.gl tr.gh td{{font-size:13.5px;letter-spacing:1.4px;text-transform:uppercase;font-weight:bold;color:{MUTED};padding-top:12px;border-bottom:0}}'
           f'.tl{{background:{CARD};border-radius:12px;padding:16px 26px 8px 26px}}')
    not_drawn = set() if NV else {t['row_id'] for t in ties if t['section'] == 'nvidia'}
    used = [r['row_id'] for r in C.rows() if r['row_id'] not in not_drawn]

    def row(mark, head, text):
        box = f'background:{BG};border:1.5px solid {AXIS}' if mark == 'O' else f'background:{MARK[mark]}'
        cls = ' class="mut"' if mark == 'O' else ''
        return f'<div class="tr"><div class="mk" style="{box}"></div><div{cls}>{"<b>" + esc(head) + ".</b> " if head else ""}{esc(text)}</div></div>'
    panels = ''
    for m in THREE:
        a = who[m]; secs = ''
        for sec, title, tail, col in SECT:
            if sec == 'nvidia' and not NV:
                continue
            mine = [t for t in ties if t['member'] == m and t['section'] == sec]
            if not mine:
                if sec == 'pfa':
                    secs += f'<div class="sec" style="border-top-color:{col}">{esc(title)} <span>· {esc(tail)}</span></div>' + row('G', '', 'No ad naming him was found (see "looked for" below).')
                elif sec == 'network':
                    raise AssertionError(('a chairman with no record in this section needs a line saying so', m))
                continue
            out = ''
            for t in mine:
                out += row(t['mark'], t['head'], t['words'])
                if t['type'] == 'ad_run':
                    out += (f'<div class="fr"><img src="{frame_uri(m, "backing")}" alt=""><img src="{frame_uri(m, "call")}" alt=""></div>'
                            f'<div class="frc">Two frames of the ad, as shown on Google\'s ad page.</div>')
            secs += f'<div class="sec" style="border-top-color:{col}">{esc(title)}{" <span>· " + esc(tail) + "</span>" if tail else ""}</div>{out}'
        panels += (f'<div class="pn"><div class="nm">{esc(a["name"])}</div><div class="rl">{esc(a["role"])} · his campaign reported raising {esc(money(float(n(f"receipts:{m}"))))} from Jan 2025 to Oct 14, 2026 · '
                   f'named on {int(a["pages_naming"])} of the {int(a["pages_total"]):,} news pages saved for this project on the Huang affair</div>{secs}</div>')
    tiles = [(f'{n("rate:anthropic:members")} of 535', f'sitting members received a gift from someone who gave Anthropic as employer since Jan 2025 ({money(float(n("rate:anthropic:usd")))}; {n("rate:anthropic:parties")}). '
              f'By dollars Mast ranks {ordinal(n("rank:mast"))}, Moolenaar {ordinal(n("rank:moolenaar"))}, Crawford {ordinal(n("rank:crawford"))}.'),
             (f'{n("rate:nvidia:members")} of 535', f'received a gift from someone who gave Nvidia as employer, counted by the same rule ({money(float(n("rate:nvidia:usd")))}; {n("rate:nvidia:parties")}). None of the three chairmen did.'),
             (f'{n("pac:anthropic:members")} of 535', f'received money from AnthroPAC, Anthropic\'s political committee ({money(float(n("pac:anthropic:usd")))}, through {day(n("pac:anthropic:through"), True)}).'),
             (f'{n("pac:nvidia:members")} of 535', 'received money from Nvidia\'s employee PAC.'),
             (n('ari_pac_candidates'), f'candidates\' campaigns received money from ARI\'s PACs ({money(float(n("ari_pac_usd")))}, Feb 2025 to Sep 2026).'),
             (n('pfa_page_members'), 'House Republicans are on the list Public First Action published on Jul 17, 2026 of members whose records its ads would highlight; Mast and Moolenaar are two of them.')]
    if not NV:
        tiles = [tiles[0], tiles[2], tiles[4], tiles[5]]
    key_ = legend([(A_COL, 'Anthropic itself, or a group it funds'), (W_COL, 'A group Open Philanthropy, or its related foundation, has funded')]
                  + ([(N_COL, 'Nvidia, or a firm registered to lobby for it'), (GRAY, 'Second-hand, none found, or another company')] if NV else [(GRAY, 'Second-hand, or none found')]))
    shapes = (f'<div class="legend" style="margin:0 0 8px"><span><svg width="20" height="20"><circle cx="10" cy="10" r="8" fill="{MUTED}"/></svg>an employee\'s own gift</span>'
              f'<span><svg width="20" height="20"><path d="M10,1 L19,10 L10,19 L1,10 Z" fill="{MUTED}"/></svg>a lobbyist\'s own gift</span>'
              f'<span><svg width="20" height="20"><rect x="2" y="2" width="16" height="16" fill="{MUTED}"/></svg>a PAC\'s gift</span>'
              f'<span style="color:{MUTED}">Area follows the amount, on one scale for all three shapes. Orange: Anthropic\'s side. Purple: groups Open Philanthropy has funded, and their firms. ' + ('Blue: Nvidia\'s firms, and trade groups that list it. ' if NV else '') +
              f'Dates show order, not purpose: no record here says why a gift was made.</span></div>')
    tl = timeline(gifts, lob, C.table('trade_pac_gifts.csv'), ties, events, who, N, nvidia=NV)
    top = (stake_band(stake) + key_band(links) + glance_table(glance, who, N, nvidia=NV)
           + f'<div class="h2">When: gifts, bills, ads and letters on one timeline</div>{shapes}<div class="tl">{tl}</div>')
    bottom = (f'<div class="h2">The records, chairman by chairman</div>{key_}<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:22px;align-items:start">{panels}</div>'
              + f'<div class="h2">How common these ties are across Congress</div>'
              + f'<div style="display:grid;grid-template-columns:repeat({len(tiles)},1fr);gap:16px">' + ''.join(f'<div class="tile"><div class="big">{esc(x)}</div><div class="cap">{esc(y)}</div></div>' for x, y in tiles) + '</div>')
    emp_a = money(float(n('emp:anthropic:three'))); lob_n = money(float(n('lob:nvidia:three'))); lob_a = money(float(n('lob:anthropic:three')))
    assert float(n('emp:nvidia:mast')) + float(n('emp:nvidia:moolenaar')) + float(n('emp:nvidia:crawford')) == 0
    title = (f'The three chairmen who summoned Huang: an Anthropic-funded group ran ads praising two of them on chip export controls. '
             f'Anthropic\'s employees gave their committees {emp_a}, Nvidia\'s $0; lobbyists and PACs at Nvidia\'s lobbying firms gave {lob_n}, at Anthropic\'s {lob_a}')
    assert any(r['side'] == 'nvidia' and r['measure'] == 'firm_pac' for r in lob) and not any(r['side'] == 'anthropic' and r['measure'] == 'firm_pac' for r in lob)
    if not NV:                                         # the cut names no Nvidia sum in its title: neither the $0 nor the larger one
        title = (f'The three chairmen who summoned Huang: an Anthropic-funded group ran ads praising two of them on chip export controls, '
                 f'and Anthropic\'s employees gave their committees {emp_a}')
    art = next(k for k in links if k['id'] == 'article'); times = next(k for k in links if k['id'] == 'times'); times_more = next(k for k in links if k['id'] == 'times_more')
    letter = next(e for e in events if e['lane'] == 'all' and e['date'] == '2026-11-12'); talk = 'conversation with NVIDIA staff yesterday'
    assert any(talk in q for q in letter['q'])
    sub = ('Reps. Brian Mast, John Moolenaar and Rick Crawford signed the letters of Nov 5 and Nov 12, 2026 calling Nvidia\'s founder, Jensen Huang, before their committees. '
           + esc(times['words']) + ' ' + esc(art['words']) + ' This figure lists every tie found, in the records searched, between each chairman and Anthropic or a group linked to it' + (', with the same records for Nvidia. ' if NV else '. ') +
           'A tie is a record with a date: the date of a gift, filing, hearing or page, not of when any relationship began or ended. None shows why anyone acted, and nothing here shows that any overlap caused or coordinated the coverage.')
    basis = T.basis_words(); old = 'No earlier copy exists for Nvidia, so a Nvidia line blanked that way is missed.'
    assert old in basis
    basis = basis.replace(old, 'This project holds no earlier copy of a Nvidia line, so a Nvidia line blanked that way would be missed; that is the one place the two counts differ.')
    if not NV:
        for a_, b_ in (('Both companies\' lines come from', 'The employees\' gift lines come from'), (': 51 for Anthropic, 21 for Nvidia.', ': 51 of them.'),
                       (' This project holds no earlier copy of a Nvidia line, so a Nvidia line blanked that way would be missed; that is the one place the two counts differ.', '')):
            assert basis.count(a_) == 1, a_
            basis = basis.replace(a_, b_)
    left_out = ('' if NV else
                '<b>What this figure leaves out:</b> the same search for Nvidia. Nvidia\'s employees and its PAC gave the three chairmen nothing; lobbyists and PACs at firms registered to lobby for Nvidia gave them '
                f'{lob_n}, and the PACs of two trade groups that list Nvidia gave Mast {money(float(n("trade:nvidia:three")))}. Those records are in the repository\'s tables, not drawn here. ')
    where = ('On the left, the' if LAYOUT == 'wide' else 'The', 'On the right, each panel lists' if LAYOUT == 'wide' else 'Each panel then lists')
    foot = (f'<b>Reading it:</b> {where[0]} first band says what each company makes and where the two have clashed; the key says once how each group connects to Anthropic; the table and the timeline put the three chairmen side by side. '
            f'{where[1]} its records by that link{", with the same records for Nvidia under them" if NV else ""}. '
            'An employee\'s gift is that person\'s own money: the FEC line shows the employer the donor wrote down. A lobbyist\'s gift is reported by the lobbyist as his or her own. Donors and lobbyists are counted here, not named; the one exception is Anthropic\'s chief executive, whose gift to a super PAC is in the key. '
            '<b>How it was made:</b> ' + esc(basis) + ' A line counts if an individual gave the company as employer to a committee tied to a sitting member, not as a memo line; a joint committee\'s later allocation is not counted again. '
            'Committees tied to a member are his campaign committee, plus joint and leadership committees an earlier evidence set keyed to him; a gift to a committee not so keyed is missed. '
            'Lobbyists\' gifts are from the contribution reports lobbyists and their firms file with the Senate (gifts dated Jan 2024 to Jun 2026): a gift counts if it names the chairman and the firm had a lobbying registration for the client on that day. '
            'A lobbyist is "listed" for a client from the first quarter a filing names him or her for it to 90 days after the last. The same rule is applied to ' + ('Nvidia\'s firms, ' if NV else '') + 'Anthropic\'s firms and the firms of the groups in the key. '
            'Trade groups\' PACs are from the FEC\'s file of committees\' gifts to candidates, and each group\'s members from its own page. Campaign totals are from the FEC\'s summary file; PAC money from the committees\' FEC filings through Sep 30, 2026; lobbying reports through the third quarter of 2026; '
            'grant totals are sums of the awards Open Philanthropy lists, and for Horizon a foundation\'s tax filing; directors are from tax returns; fellows, staff and witnesses are from the programme\'s, the groups\' and Congress\'s own pages. '
            'The ads are from Google\'s political-ads report and the ad pages it links to; the words on screen were read from frames of each video, and the Census Bureau\'s table matches the Florida ad\'s zip codes to the district. '
            '<b>The Times report:</b> ' + esc(times_more['words']) + ' '
            '<b>What the record does not show:</b> any contact between these members and Anthropic about Huang; any contact between the members themselves and Nvidia beyond the letters '
            f'(the Nov 12 letter mentions a "{talk}", and does not say who took part); why any donor or lobbyist gave, or whether a client asked a lobbyist to give; '
            'which offices a lobbying report\'s lobbyists visited or what they asked; which of Public First Action\'s donors paid for the ads; that a grant came with any instruction, or that a past award means money still flows; '
            'who on a witness list appeared, except where a transcript is cited. Not finding a record is not proof that nothing happened. '
            '<b>Not searched:</b> trade groups other than the three whose member lists were read (the Semiconductor Industry Association, the Information Technology Industry Council, TechNet); ads outside Google\'s report; '
            + ('ads by other groups that Nvidia may fund (the Google search was for an advertiser named Nvidia); ' if NV else '') + 'lobbyists\' gifts after Jun 2026, whose reports are not yet due; lobbying registrations that ended before 2024; '
            'gifts on which the employer field does not begin "Anthropic"' + (' or "Nvidia"' if NV else '') + ', and committees not keyed to a member; bills other than the two chip bills; posts on X were searched only for Anthropic-side terms, up to Sep 16, 2026. '
            'These ties are common: the tiles count them across Congress. ' + left_out +
            '<b>Source:</b> FEC receipts, filings and summary files; Senate lobbying and contribution reports; bill records; hearing records; tax returns; grant records; Google\'s ad report; the saved pages named above. '
            'New sources were fetched Nov 12 to 14, 2026; records reused from earlier evidence sets were captured there in Sep and Oct 2026. ' + DRAFT)
    STEM = stem or ('nv13-three-chairmen-full' if NV else 'nv13-three-chairmen')
    if LAYOUT == 'wide':
        col = PAGE - 120                                           # a column is exactly as wide as the tall page's content, so every part is drawn as before
        wide = (f'h1{{font-size:66px;letter-spacing:-2.2px;line-height:1.06;max-width:{WIDE - 200}px}}.subtitle{{font-size:26px;line-height:1.36;max-width:4500px;margin-bottom:8px}}'
                f'.kicker{{font-size:20px}}.cols{{display:grid;grid-template-columns:{col}px {col}px;gap:{WIDE - 120 - 2 * col}px;align-items:start}}'
                f'body>.footnote{{display:none}}.cols .footnote{{margin-top:26px}}')
        body = f'<div class="cols"><div>{top}</div><div>{bottom}<div class="footnote">{foot}</div></div></div>'
        render(STEM, cite(used) + shell(title, KICKER, sub, body, '', WIDE, extra_css=css + wide), WIDE)
    else:
        render(STEM, cite(used) + shell(title, KICKER, sub, top + bottom, foot, PAGE, extra_css=css), PAGE)
