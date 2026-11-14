"""Builds 04-custom-rbac-role/diagrams/two-planes.svg: an animated view of lab 04.
The test user sends five requests. Start and Delete go to the management-plane
gate (the custom role's action list); SSH and sudo go to the data-plane gate
on the VM. Halfway through, Virtual Machine User Login is added and the second
SSH gets in. Dark Biira colourway, CSS animation only (plays on GitHub).

Usage: python lab04_two_planes.py <output.svg>
"""
import sys

OUT = sys.argv[1]

BG, PANEL, EDGE, GRID = "#060D1F", "#0A1830", "#1C3050", "#101F38"
NAVY = "#08152F"
CYAN, CYAN_SOFT, ICE = "#2DD4E8", "#9BE8F2", "#D6EEF4"
SLATE_L, SLATE_D = "#8FA3BF", "#3A4B66"
GREEN, GREEN_D = "#2BD99F", "#0F3B31"
RED, RED_D = "#FF6B5E", "#3A1620"
AMBER = "#FFC04D"
VIOLET, VIOLET_D = "#A78BFA", "#1E1640"
WHITE = "#F4FAFD"
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, Menlo, monospace"

W, H = 1200, 760
CYCLE = 24
# phases
P1 = (0.00, 0.16)   # start: allowed
P2 = (0.16, 0.32)   # delete: denied
P3 = (0.32, 0.48)   # ssh: denied
P4 = (0.48, 0.58)   # User Login role added
P5 = (0.58, 0.76)   # ssh: allowed
P6 = (0.76, 0.985)  # sudo: denied

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


def mover(span, x_from, x_to):
    """A class that slides from x_from to x_to during the first 60% of span,
    holds, and is visible only inside span."""
    _n[0] += 1
    name = f"mv{_n[0]}"
    a, b = span
    mid = a + (b - a) * 0.55
    dx = x_to - x_from
    kf = (f"0%{{opacity:0;transform:translateX(0px)}}"
          f"{pct(max(a - 0.001, 0))}{{opacity:0;transform:translateX(0px)}}"
          f"{pct(a + 0.01)}{{opacity:1;transform:translateX(0px)}}"
          f"{pct(mid)}{{opacity:1;transform:translateX({dx}px)}}"
          f"{pct(b - 0.005)}{{opacity:1;transform:translateX({dx}px)}}"
          f"{pct(b + 0.005)}{{opacity:0;transform:translateX({dx}px)}}"
          f"100%{{opacity:0;transform:translateX({dx}px)}}")
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
add(f'<text class="t" x="96" y="44" font-size="24" font-weight="700" style="fill:{WHITE}">Two locks on one VM: managing it, and logging in to it</text>')
add(f'<text class="t" x="96" y="74" font-size="14" style="fill:{CYAN_SOFT}">azure-labs &#183; lab 04 custom RBAC role &#183; a least-privilege operator, tested on both planes</text>')
add(f'<rect x="0" y="96" width="{W}" height="2" fill="{CYAN}" opacity="0.9"/>')

# user card
UX, UY, UW, UH = 36, 124, 250, 470
add(f'<rect x="{UX}" y="{UY}" width="{UW}" height="{UH}" rx="16" fill="{PANEL}" stroke="{EDGE}"/>')
add(f'<circle cx="{UX + 44}" cy="{UY + 48}" r="22" fill="{NAVY}" stroke="{CYAN}" stroke-width="2"/>'
    f'<circle cx="{UX + 44}" cy="{UY + 42}" r="7" fill="{CYAN}"/>'
    f'<path d="M{UX + 32} {UY + 60} q12 -12 24 0" fill="{CYAN}"/>')
add(f'<text class="t" x="{UX + 78}" y="{UY + 44}" font-size="16" font-weight="800" style="fill:{WHITE}">lab-vmop</text>')
add(f'<text class="t" x="{UX + 78}" y="{UY + 64}" font-size="11.5" style="fill:{SLATE_L}">test user &#183; MFA on</text>')
add(f'<text class="t" x="{UX + 20}" y="{UY + 112}" font-size="11.5" font-weight="700" letter-spacing="1.1" style="fill:{SLATE_L}">ROLES ON rg-lab-vm</text>')
add(f'<rect x="{UX + 18}" y="{UY + 126}" width="{UW - 36}" height="62" rx="10" fill="{NAVY}" stroke="{CYAN}" stroke-width="1.3"/>'
    f'<text class="t" x="{UX + 32}" y="{UY + 152}" font-size="13.5" font-weight="800" style="fill:{CYAN}">Lab VM Operator</text>'
    f'<text class="t" x="{UX + 32}" y="{UY + 173}" font-size="11" style="fill:{SLATE_L}">custom &#183; 5 actions &#183; management</text>')
add(f'<g class="{win((P4[0], 0.985))}"><rect x="{UX + 18}" y="{UY + 202}" width="{UW - 36}" height="62" rx="10" fill="{VIOLET_D}" stroke="{VIOLET}" stroke-width="1.3"/>'
    f'<text class="t" x="{UX + 32}" y="{UY + 228}" font-size="13.5" font-weight="800" style="fill:{VIOLET}">VM User Login</text>'
    f'<text class="t" x="{UX + 32}" y="{UY + 249}" font-size="11" style="fill:{SLATE_L}">built-in &#183; 1 data action</text></g>')
add(f'<g class="{win((0, P4[0]))}"><rect x="{UX + 18}" y="{UY + 202}" width="{UW - 36}" height="62" rx="10" fill="none" stroke="{SLATE_D}" stroke-dasharray="5 5"/>'
    f'<text class="t" x="{UX + UW / 2}" y="{UY + 238}" font-size="11.5" text-anchor="middle" style="fill:{SLATE_L}">no login role yet</text></g>')
add(f'<g class="{win(P4)}"><text class="t" x="{UX + UW / 2}" y="{UY + 290}" font-size="12.5" font-weight="700" text-anchor="middle" style="fill:{VIOLET}">+ role added by the admin</text></g>')
add(f'<text class="t" x="{UX + 20}" y="{UY + 330}" font-size="11" style="fill:{SLATE_L}">not given:</text>')
add(f'<text class="t" x="{UX + 20}" y="{UY + 350}" font-size="11.5" style="fill:{SLATE_L}">&#215; delete, write, resize</text>')
add(f'<text class="t" x="{UX + 20}" y="{UY + 370}" font-size="11.5" style="fill:{SLATE_L}">&#215; read NIC / IP / VNet</text>')
add(f'<text class="t" x="{UX + 20}" y="{UY + 390}" font-size="11.5" style="fill:{SLATE_L}">&#215; Administrator Login (sudo)</text>')

# lanes
LANE_M, LANE_D = 250, 476
GX, GW = 520, 270            # gate
VX, VW = 880, 286           # vm
for y, label, hue in ((LANE_M, "MANAGEMENT PLANE &#183; Azure Resource Manager", CYAN),
                      (LANE_D, "DATA PLANE &#183; inside the VM", VIOLET)):
    add(f'<text class="t" x="{UX + UW + 24}" y="{y - 98}" font-size="11.5" font-weight="700" letter-spacing="1.1" style="fill:{hue}">{label}</text>')
    add(f'<line x1="{UX + UW}" y1="{y}" x2="{VX}" y2="{y}" stroke="{EDGE}" stroke-width="2" stroke-dasharray="2 6"/>')

# management gate
add(f'<rect x="{GX}" y="{LANE_M - 82}" width="{GW}" height="164" rx="14" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.4"/>')
add(f'<text class="t" x="{GX + 18}" y="{LANE_M - 56}" font-size="13" font-weight="800" style="fill:{WHITE}">Is the action in the role?</text>')
rows = [("virtualMachines/read", True), ("start/action", True), ("deallocate/action", True),
        ("restart/action", True), ("powerOff/action", True), ("delete", False)]
for i, (a, ok) in enumerate(rows):
    y = LANE_M - 32 + i * 18
    add(f'<text class="t m" x="{GX + 18}" y="{y}" font-size="11.5" style="fill:{GREEN if ok else RED}">{"&#10003;" if ok else "&#215;"} {a}</text>')

# data gate
add(f'<rect x="{GX}" y="{LANE_D - 74}" width="{GW}" height="148" rx="14" fill="{PANEL}" stroke="{VIOLET}" stroke-width="1.4"/>')
add(f'<text class="t" x="{GX + 18}" y="{LANE_D - 48}" font-size="13" font-weight="800" style="fill:{WHITE}">Entra login check</text>')
add(f'<text class="t" x="{GX + 18}" y="{LANE_D - 27}" font-size="11.5" style="fill:{SLATE_L}">VM identity + AADSSHLoginForLinux</text>')
add(f'<text class="t m" x="{GX + 18}" y="{LANE_D - 3}" font-size="11.5" style="fill:{ICE}">shell needs  login/action</text>')
add(f'<text class="t m" x="{GX + 18}" y="{LANE_D + 17}" font-size="11.5" style="fill:{ICE}">sudo  needs  adminLogin/action</text>')

# VM card
add(f'<rect x="{VX}" y="{LANE_M - 82}" width="{VW}" height="{LANE_D - LANE_M + 156}" rx="16" fill="{PANEL}" stroke="{EDGE}"/>')
add(f'<text class="t" x="{VX + 20}" y="{LANE_M - 50}" font-size="17" font-weight="800" style="fill:{WHITE}">vm-lab-01</text>')
add(f'<text class="t" x="{VX + 20}" y="{LANE_M - 28}" font-size="11.5" style="fill:{SLATE_L}">rg-lab-vm &#183; Ubuntu 24.04</text>')
add(f'<g class="{win((0, P1[0] + 0.09))}"><text class="t" x="{VX + 20}" y="{LANE_M + 6}" font-size="13" font-weight="700" style="fill:{SLATE_L}">&#9679; deallocated</text></g>')
add(f'<g class="{win((P1[0] + 0.09, 0.985))}"><text class="t" x="{VX + 20}" y="{LANE_M + 6}" font-size="13" font-weight="700" style="fill:{GREEN}">&#9679; running</text></g>')
add(f'<g class="{win(P2)}"><text class="t" x="{VX + 20}" y="{LANE_M + 30}" font-size="12" style="fill:{GREEN}">still here: 7 of 7 resources</text></g>')
# terminal
TY = LANE_D - 54
add(f'<rect x="{VX + 18}" y="{TY}" width="{VW - 36}" height="118" rx="10" fill="#03081A" stroke="{SLATE_D}"/>')
add(f'<g class="{win((0, P5[0] + 0.09))}"><text class="t m" x="{VX + 32}" y="{TY + 30}" font-size="12" style="fill:{SLATE_L}">no session</text></g>')
add(f'<g class="{win((P5[0] + 0.09, 0.985))}"><text class="t m" x="{VX + 32}" y="{TY + 30}" font-size="12" style="fill:{GREEN}">lab-vmop@vm-lab-01:~$</text></g>')
add(f'<g class="{win((P6[0] + 0.09, 0.985))}"><text class="t m" x="{VX + 32}" y="{TY + 54}" font-size="12" style="fill:{ICE}">$ sudo whoami</text>'
    f'<text class="t m" x="{VX + 32}" y="{TY + 76}" font-size="12" style="fill:{RED}">not in the sudoers file</text></g>')

# requests
REQS = [
    (P1, LANE_M, "Start", True, "allowed"),
    (P2, LANE_M, "Delete", False, "403: no virtualMachines/delete"),
    (P3, LANE_D, "az ssh vm", False, "Permission denied (publickey)"),
    (P5, LANE_D, "az ssh vm", True, "allowed"),
    (P6, LANE_D, "sudo whoami", False, "denied: no adminLogin/action"),
]
X0 = UX + UW + 20
for span, y, label, ok, msg in REQS:
    x_to = (VX + 10) if ok else (GX - 128)
    cls = mover(span, X0, x_to)
    add(f'<g class="{cls}"><rect x="{X0}" y="{y - 17}" width="120" height="34" rx="17" fill="{WHITE}" filter="url(#glowC)"/>'
        f'<text class="t" x="{X0 + 60}" y="{y + 5}" font-size="13" font-weight="800" text-anchor="middle" style="fill:{NAVY}">{label}</text></g>')
    a, b = span
    t_res = a + (b - a) * 0.55
    hue, dark = (GREEN, GREEN_D) if ok else (RED, RED_D)
    bx = GX + GW / 2 - 140
    by = (y + 82 + 6) if y == LANE_M else (y + 74 + 10)
    add(f'<g class="{win((t_res, b))}"><rect x="{bx}" y="{by}" width="280" height="34" rx="10" fill="{dark}" stroke="{hue}" stroke-width="1.3"/>'
        f'<text class="t m" x="{bx + 140}" y="{by + 22}" font-size="12" font-weight="700" text-anchor="middle" style="fill:{hue}">{msg}</text></g>')

# captions
CAPS = [
    (P1, GREEN, "Start:", "start/action is in the role, so Azure runs it."),
    (P2, RED, "Delete:", "the portal shows the button, but Azure refuses: delete is not in the role."),
    (P3, RED, "SSH with Entra:", "the custom role is management plane only; logging in is a data action."),
    (P4, VIOLET, "Admin adds Virtual Machine User Login", "on rg-lab-vm: one data action, login/action."),
    (P5, GREEN, "SSH again:", "Entra signs a short-lived certificate, the VM checks the role, the shell opens. No key file."),
    (P6, RED, "sudo:", "User Login is a shell, not root. Administrator Login would add sudo."),
]
add(f'<rect x="24" y="{H - 140}" width="{W - 48}" height="52" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
for span, hue, lead, rest in CAPS:
    add(f'<text class="{win(span)} t" x="44" y="{H - 108}" font-size="14.5"><tspan font-weight="800" style="fill:{hue}">{lead}</tspan> {rest}</text>')

add(f'<text class="t" x="{W / 2}" y="{H - 50}" font-size="13" text-anchor="middle" style="fill:{ICE}">'
    f'<tspan font-weight="700" style="fill:{AMBER}">Read the actions list, not the role name.</tspan> '
    f'A role that can delete a VM cannot log in to it, and one that can log in cannot delete it.</text>')
add(f'<text class="t" x="{W / 2}" y="{H - 26}" font-size="11.5" text-anchor="middle" style="fill:{SLATE_L}">'
    f'Assignable scope: the subscription (where the role may be given). Assignment scope: rg-lab-vm (where it is given).</text>')

defs = f'''<defs>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0 H0 V48" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glowC" x="-80%" y="-80%" width="260%" height="260%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{CYAN}" flood-opacity="0.6"/></filter>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="A test user with a custom VM operator role starts a VM (allowed) and tries to delete it (denied by Azure Resource Manager). '
       f'Entra SSH is denied until Virtual Machine User Login is added, then allowed; sudo is denied because User Login is not Administrator Login.">'
       f'<title>Two locks on one VM: managing it, and logging in to it</title>'
       f'<style>{"".join(css)}</style>{defs}' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
