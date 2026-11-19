"""Builds 05-entra-users-groups/diagrams/nested-groups.svg: an animated view of lab 05.
Six users land in two team groups, the two groups are nested inside
L5-All-Staff, Reader is given to that one group on rg-lab-vm, and the access
flows down to every person (Kofi is checked). The guests sit outside every
group and get nothing. The last phase shows the exam trap: group-based
licensing does NOT follow nesting. Dark Biira colourway, CSS animation only.

Usage: python lab05_nested_groups.py <output.svg>
"""
import sys

OUT = sys.argv[1]

BG, PANEL, EDGE, GRID = "#060D1F", "#0A1830", "#1C3050", "#101F38"
NAVY = "#08152F"
CYAN, CYAN_SOFT, ICE = "#2DD4E8", "#9BE8F2", "#D6EEF4"
SLATE_L, SLATE_D = "#8FA3BF", "#3A4B66"
GREEN, GREEN_D = "#2BD99F", "#0F3B31"
RED, RED_D = "#FF6B5E", "#3A1620"
AMBER, AMBER_D = "#FFC04D", "#3A2C10"
VIOLET, VIOLET_D = "#A78BFA", "#1E1640"
WHITE = "#F4FAFD"
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, Menlo, monospace"

W, H = 1200, 760
CYCLE = 24
P1 = (0.00, 0.16)   # users into their team groups
P2 = (0.16, 0.32)   # teams nested inside L5-All-Staff
P3 = (0.32, 0.48)   # Reader given to L5-All-Staff
P4 = (0.48, 0.66)   # access flows down to every person; Kofi checked
P5 = (0.66, 0.80)   # guests: outside every group, no access
P6 = (0.80, 0.985)  # the trap: licensing does not follow nesting

css = [f"""
.t{{font-family:{FONT};fill:{ICE}}}
.m{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{ .anim{{animation:none!important;opacity:1!important;transform:none!important}} }}
@keyframes sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
"""]
_n = [0]


def pct(f):
    return f"{f * 100:.1f}%"


def win(*spans, fade=0.012):
    """A class visible only inside the given (on, off) fractions of the cycle."""
    _n[0] += 1
    name = f"w{_n[0]}"
    frames = []
    for on, off in spans:
        frames += [(0.0, 1)] if on <= 0 else [(on - 0.001, 0), (on + fade, 1)]
        frames += [(1.0, 1)] if off >= 0.985 else [(off, 1), (off + fade, 0)]
    if frames[0][0] > 0:
        frames.insert(0, (0.0, 0))
    if frames[-1][0] < 1:
        frames.append((1.0, 0))
    kf = "".join(f"{pct(t)}{{opacity:{o}}}" for t, o in frames)
    css.append(f"@keyframes {name}{{{kf}}}.{name}{{animation:{name} {CYCLE}s linear infinite}}")
    return f"anim {name}"


def slide(span, dx, dy):
    """Moves an element by (dx, dy) during the first half of span, then holds
    it there for the rest of the cycle."""
    _n[0] += 1
    name = f"mv{_n[0]}"
    a, b = span
    mid = a + (b - a) * 0.5
    kf = (f"0%{{transform:translate({-dx}px,{-dy}px)}}"
          f"{pct(a)}{{transform:translate({-dx}px,{-dy}px)}}"
          f"{pct(mid)}{{transform:translate(0px,0px)}}"
          f"100%{{transform:translate(0px,0px)}}")
    css.append(f"@keyframes {name}{{{kf}}}.{name}{{animation:{name} {CYCLE}s cubic-bezier(.45,.05,.35,1) infinite}}")
    return f"anim {name}"


body = []
add = body.append

add(f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>')
add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>')

# masthead
add(f'<g transform="translate(52 52)">'
    f'<path d="M0 -26 L20 -17 V4 Q20 16 0 26 Q-20 16 -20 4 V-17 Z" fill="{NAVY}" stroke="{CYAN}" stroke-width="2.5" filter="url(#glowC)"/>'
    f'<circle r="12" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.5"/><circle r="4" fill="{CYAN}"/>'
    f'<g class="anim" style="animation:sweep 6s linear infinite;transform-origin:0px 0px">'
    f'<path d="M0 0 L-7 -16 A17 17 0 0 1 7 -16 Z" fill="{CYAN}" opacity="0.45"/></g></g>')
add(f'<text class="t" x="96" y="44" font-size="24" font-weight="700" style="fill:{WHITE}">One role, one group, eight members: access through nesting</text>')
add(f'<text class="t" x="96" y="74" font-size="14" style="fill:{CYAN_SOFT}">az-104-labs &#183; lab 05 Entra users and groups &#183; who gets Reader, and who does not</text>')
add(f'<rect x="0" y="96" width="{W}" height="2" fill="{CYAN}" opacity="0.9"/>')

# Entra tenant panel
TX, TY, TW, TH = 28, 118, 760, 488
add(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="16" fill="none" stroke="{VIOLET}" stroke-width="1.6" stroke-dasharray="6 6"/>')
add(f'<text class="t" x="{TX + 18}" y="{TY + 26}" font-size="12" font-weight="700" letter-spacing="1.1" style="fill:{VIOLET}">MICROSOFT ENTRA ID &#183; biira.online</text>')

# L5-All-Staff: the outer, nested group
AX, AY, AW, AH = TX + 18, TY + 44, 560, 340
add(f'<g class="{win((P2[0], 0.985))}"><rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" rx="14" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.6"/>'
    f'<text class="t" x="{AX + 18}" y="{AY + 28}" font-size="16" font-weight="800" style="fill:{WHITE}">L5-All-Staff</text>'
    f'<text class="t" x="{AX + 140}" y="{AY + 28}" font-size="12" style="fill:{SLATE_L}">security &#183; assigned &#183; nested</text></g>')
# member counters
add(f'<g class="{win((P2[0] + 0.06, 0.985))}"><rect x="{AX + AW - 196}" y="{AY + 10}" width="84" height="26" rx="13" fill="{NAVY}" stroke="{SLATE_D}"/>'
    f'<text class="t" x="{AX + AW - 154}" y="{AY + 28}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{ICE}">direct: 2</text></g>')
add(f'<g class="{win((P2[0] + 0.10, 0.985))}"><rect x="{AX + AW - 104}" y="{AY + 10}" width="90" height="26" rx="13" fill="{NAVY}" stroke="{CYAN}"/>'
    f'<text class="t" x="{AX + AW - 59}" y="{AY + 28}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{CYAN}">all: 8</text></g>')

# the two team groups and their people
TEAMS = [
    ("L5-Branch-Operations", AX + 18, ["Ama Mensah", "Kofi Boateng", "Efua Asante"], GREEN),
    ("L5-Treasury", AX + 286, ["Yaw Darko", "Akosua Owusu", "Kwame Adjei"], AMBER),
]
GY, GW_, GH = AY + 52, 256, 246
for name, gx, people, hue in TEAMS:
    add(f'<rect x="{gx}" y="{GY}" width="{GW_}" height="{GH}" rx="12" fill="{NAVY}" stroke="{hue}" stroke-width="1.3"/>')
    add(f'<text class="t" x="{gx + 14}" y="{GY + 24}" font-size="13.5" font-weight="800" style="fill:{hue}">{name}</text>')
    for i, person in enumerate(people):
        py = GY + 44 + i * 64
        cls = win((P1[0] + 0.02 + i * 0.03, 0.985))
        add(f'<g class="{cls}"><rect x="{gx + 12}" y="{py}" width="{GW_ - 24}" height="50" rx="10" fill="{PANEL}" stroke="{EDGE}"/>'
            f'<circle cx="{gx + 36}" cy="{py + 25}" r="13" fill="{NAVY}" stroke="{hue}" stroke-width="1.5"/>'
            f'<circle cx="{gx + 36}" cy="{py + 21}" r="4.5" fill="{hue}"/>'
            f'<path d="M{gx + 28} {py + 33} q8 -8 16 0" fill="{hue}"/>'
            f'<text class="t" x="{gx + 58}" y="{py + 22}" font-size="13" font-weight="700" style="fill:{WHITE}">{person}</text>'
            f'<text class="t" x="{gx + 58}" y="{py + 40}" font-size="11" style="fill:{SLATE_L}">member &#183; disabled</text></g>')
        # Reader badge on every person once access flows down
        add(f'<g class="{win((P4[0] + 0.04 + i * 0.015, P5[1]))}"><rect x="{gx + GW_ - 82}" y="{py + 14}" width="62" height="22" rx="11" fill="{GREEN_D}" stroke="{GREEN}"/>'
            f'<text class="t" x="{gx + GW_ - 51}" y="{py + 29}" font-size="10.5" font-weight="700" text-anchor="middle" style="fill:{GREEN}">Reader</text></g>')

# Kofi check-access highlight
KX, KY = AX + 18 + 12, GY + 44 + 64
add(f'<g class="{win((P4[0] + 0.08, P4[1]))}"><rect x="{KX - 4}" y="{KY - 4}" width="{GW_ - 16}" height="58" rx="12" fill="none" stroke="{CYAN}" stroke-width="2.5" filter="url(#glowC)"/></g>')

# guests, outside every group
GX0, GY0 = TX + 18, AY + AH + 16
add(f'<rect x="{GX0}" y="{GY0}" width="{AW}" height="84" rx="12" fill="none" stroke="{SLATE_D}" stroke-dasharray="4 5"/>')
add(f'<text class="t" x="{GX0 + 14}" y="{GY0 + 22}" font-size="12" font-weight="700" letter-spacing="1" style="fill:{SLATE_L}">GUESTS &#183; in no group</text>')
for i, g in enumerate(["Guest One (Partner Auditor)", "Guest Two (Vendor Engineer)"]):
    gx = GX0 + 14 + i * 272
    add(f'<rect x="{gx}" y="{GY0 + 32}" width="258" height="40" rx="10" fill="{PANEL}" stroke="{EDGE}"/>'
        f'<text class="t" x="{gx + 12}" y="{GY0 + 50}" font-size="12" font-weight="700" style="fill:{WHITE}">{g}</text>'
        f'<text class="t m" x="{gx + 12}" y="{GY0 + 65}" font-size="10" style="fill:{SLATE_L}">...#EXT#@ &#183; PendingAcceptance</text>')
    add(f'<g class="{win(P5)}"><rect x="{gx + 200}" y="{GY0 + 41}" width="50" height="22" rx="11" fill="{RED_D}" stroke="{RED}"/>'
        f'<text class="t" x="{gx + 225}" y="{GY0 + 56}" font-size="10.5" font-weight="700" text-anchor="middle" style="fill:{RED}">none</text></g>')

# right side: Azure, rg-lab-vm
RX, RY, RW, RH = 812, 118, 360, 300
add(f'<rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" rx="16" fill="none" stroke="{CYAN}" stroke-width="1.6" stroke-dasharray="6 6"/>')
add(f'<text class="t" x="{RX + 18}" y="{RY + 26}" font-size="12" font-weight="700" letter-spacing="1.1" style="fill:{CYAN}">AZURE &#183; sub-noble-seclab-001</text>')
add(f'<rect x="{RX + 18}" y="{RY + 44}" width="{RW - 36}" height="{RH - 62}" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
add(f'<text class="t" x="{RX + 36}" y="{RY + 74}" font-size="16" font-weight="800" style="fill:{WHITE}">rg-lab-vm</text>')
add(f'<text class="t" x="{RX + 36}" y="{RY + 94}" font-size="11.5" style="fill:{SLATE_L}">VM, disk, IP, VNet from lab 03</text>')
add(f'<text class="t" x="{RX + 36}" y="{RY + 130}" font-size="11.5" font-weight="700" letter-spacing="1" style="fill:{SLATE_L}">ACCESS CONTROL (IAM)</text>')
add(f'<g class="{win((0, P3[0] + 0.05))}"><rect x="{RX + 36}" y="{RY + 142}" width="{RW - 72}" height="58" rx="10" fill="none" stroke="{SLATE_D}" stroke-dasharray="5 5"/>'
    f'<text class="t" x="{RX + RW / 2}" y="{RY + 176}" font-size="12" text-anchor="middle" style="fill:{SLATE_L}">no group assignment yet</text></g>')
add(f'<g class="{win((P3[0] + 0.05, 0.985))}"><rect x="{RX + 36}" y="{RY + 142}" width="{RW - 72}" height="58" rx="10" fill="{GREEN_D}" stroke="{GREEN}" stroke-width="1.4"/>'
    f'<text class="t" x="{RX + 52}" y="{RY + 167}" font-size="14" font-weight="800" style="fill:{GREEN}">Reader</text>'
    f'<text class="t" x="{RX + 52}" y="{RY + 188}" font-size="11.5" style="fill:{ICE}">assigned to: L5-All-Staff (group)</text></g>')
add(f'<g class="{win((P3[0] + 0.05, 0.985))}"><text class="t" x="{RX + 36}" y="{RY + 226}" font-size="11.5" style="fill:{SLATE_L}">one assignment, not eight</text></g>')

# the arrow from the role to the group
add(f'<g class="{win((P3[0] + 0.05, 0.985))}"><path d="M{RX + 36} {RY + 171} C {RX - 40} {RY + 171}, {AX + AW + 60} {AY + 22}, {AX + AW + 4} {AY + 22}" '
    f'fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7 6" marker-end="url(#arrG)"/></g>')

# check access result card
CX, CY, CW = RX, RY + RH + 18, RW
add(f'<g class="{win((P4[0] + 0.08, P4[1]))}"><rect x="{CX}" y="{CY}" width="{CW}" height="150" rx="14" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.4"/>'
    f'<text class="t" x="{CX + 18}" y="{CY + 28}" font-size="13" font-weight="800" style="fill:{WHITE}">Check access: Kofi Boateng</text>'
    + "".join(f'<text class="t" x="{CX + 18}" y="{CY + y}" font-size="12" style="fill:{SLATE_L}">{k}</text>'
              f'<text class="t m" x="{CX + 120}" y="{CY + y}" font-size="12" font-weight="700" style="fill:{c}">{v}</text>'
              for y, k, v, c in ((58, "Role", "Reader", GREEN), (80, "Resource", "rg-lab-vm", ICE), (102, "Assigned to", "L5-All-Staff", CYAN))) +
    f'<text class="t" x="{CX + 18}" y="{CY + 132}" font-size="11.5" style="fill:{SLATE_L}">Kofi &#8594; Branch-Operations &#8594; All-Staff &#8594; Reader</text></g>')
# licensing trap card
add(f'<g class="{win(P6)}"><rect x="{CX}" y="{CY}" width="{CW}" height="150" rx="14" fill="{AMBER_D}" stroke="{AMBER}" stroke-width="1.4"/>'
    f'<text class="t" x="{CX + 18}" y="{CY + 28}" font-size="13" font-weight="800" style="fill:{AMBER}">Exam trap: licences</text>'
    f'<text class="t" x="{CX + 18}" y="{CY + 56}" font-size="12.5" style="fill:{ICE}">A licence given to L5-All-Staff</text>'
    f'<text class="t" x="{CX + 18}" y="{CY + 76}" font-size="12.5" style="fill:{ICE}">reaches <tspan font-weight="800" style="fill:{RED}">nobody</tspan>: group-based</text>'
    f'<text class="t" x="{CX + 18}" y="{CY + 96}" font-size="12.5" style="fill:{ICE}">licensing ignores nested groups.</text>'
    f'<text class="t" x="{CX + 18}" y="{CY + 128}" font-size="11.5" style="fill:{SLATE_L}">Azure roles follow nesting; licences do not.</text></g>')
# licence chip that stops at the outer group
add(f'<g class="{win(P6)}"><rect x="{AX + AW - 150}" y="{AY + AH - 32}" width="136" height="24" rx="12" fill="{AMBER_D}" stroke="{AMBER}"/>'
    f'<text class="t" x="{AX + AW - 82}" y="{AY + AH - 16}" font-size="11" font-weight="700" text-anchor="middle" style="fill:{AMBER}">licence stops here</text></g>')

# captions
CAPS = [
    (P1, GREEN, "Users:", "six disabled users, created through Microsoft Graph after the portal's bulk job failed."),
    (P2, CYAN, "Nesting:", "L5-All-Staff holds two groups and no people. Direct members 2, all members 8."),
    (P3, GREEN, "One assignment:", "Reader on rg-lab-vm goes to L5-All-Staff, not to each person."),
    (P4, CYAN, "Access flows down:", "Check access on Kofi shows Reader, assigned to L5-All-Staff."),
    (P5, RED, "Guests:", "invited, but in no group, so they get nothing. Membership is the access."),
    (P6, AMBER, "The trap:", "Azure RBAC follows nested groups. Group-based licensing does not."),
]
add(f'<rect x="24" y="{H - 140}" width="{W - 48}" height="52" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
for span, hue, lead, rest in CAPS:
    add(f'<text class="{win(span)} t" x="44" y="{H - 108}" font-size="14.5"><tspan font-weight="800" style="fill:{hue}">{lead}</tspan> {rest}</text>')

add(f'<text class="t" x="{W / 2}" y="{H - 50}" font-size="13" text-anchor="middle" style="fill:{ICE}">'
    f'<tspan font-weight="700" style="fill:{AMBER}">Give roles to groups, not people.</tspan> '
    f'Adding someone to a team is then the whole access change.</text>')
add(f'<text class="t" x="{W / 2}" y="{H - 26}" font-size="11.5" text-anchor="middle" style="fill:{SLATE_L}">'
    f'Membership type: Assigned. Dynamic groups and group-based licensing need Entra ID P1 or P2.</text>')

defs = f'''<defs>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0 H0 V48" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glowC" x="-80%" y="-80%" width="260%" height="260%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{CYAN}" flood-opacity="0.6"/></filter>
<marker id="arrG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{GREEN}"/></marker>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Six users sit in two team groups, which are nested inside L5-All-Staff. Reader on rg-lab-vm is given to L5-All-Staff, '
       f'and every person gets it through nesting; Check access on Kofi shows Reader assigned to L5-All-Staff. Two guests are in no group and get nothing. '
       f'Group-based licensing does not follow nested groups.">'
       f'<title>One role, one group, eight members: access through nesting</title>'
       f'<style>{"".join(css)}</style>{defs}' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
