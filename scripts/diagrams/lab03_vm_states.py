"""Builds 03-vm-deep-dive/diagrams/vm-states.svg: an animated view of lab 03.
One VM goes Running -> OS shutdown (Stopped) -> Azure Stop (deallocated) ->
Start on a new host. Billing badges show what charges in each state, and the
two proof files show which disk survives.
Dark Biira colourway, flat fills, CSS animation only (plays on GitHub).

Usage: python lab03_vm_states.py <output.svg>
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
VIOLET = "#A78BFA"
WHITE = "#F4FAFD"
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, Menlo, monospace"

W, H = 1200, 760
CYCLE = 20
# phases (fractions of the cycle)
A = (0.00, 0.22)   # running
B = (0.22, 0.46)   # OS shutdown: Stopped
C = (0.46, 0.72)   # Azure stop: deallocated
D = (0.72, 0.985)  # started on a new host

css = [f"""
.t{{font-family:{FONT};fill:{ICE}}}
.m{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{ .anim{{animation:none!important;opacity:1!important}} }}
@keyframes sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
"""]
_n = [0]


def pct(f):
    return f"{f * 100:.1f}%"


def win(*spans, fade=0.012):
    """A class whose opacity is 1 inside any of the given (on, off) spans."""
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
add(f'<text class="t" x="96" y="44" font-size="24" font-weight="700" style="fill:{WHITE}">Turning a VM off: what keeps billing, what survives</text>')
add(f'<text class="t" x="96" y="74" font-size="14" style="fill:{CYAN_SOFT}">azure-labs &#183; lab 03 VM deep dive &#183; only Azure can stop the compute bill</text>')
add(f'<rect x="0" y="96" width="{W}" height="2" fill="{CYAN}" opacity="0.9"/>')

# state strip
STATES = [("RUNNING", "", A, GREEN), ("STOPPED", "shutdown -h inside Ubuntu", B, AMBER),
          ("STOPPED (DEALLOCATED)", "portal Stop / az vm deallocate", C, RED),
          ("RUNNING AGAIN", "Start: a new host", D, GREEN)]
SX = [40, 320, 600, 900]
SW = [260, 260, 280, 260]
for (label, sub, span, hue), x, w in zip(STATES, SX, SW):
    add(f'<rect x="{x}" y="118" width="{w}" height="54" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="1"/>')
    add(f'<g class="{win(span)}"><rect x="{x}" y="118" width="{w}" height="54" rx="12" fill="{NAVY}" stroke="{hue}" stroke-width="2.2"/></g>')
    add(f'<text class="t" x="{x + w / 2}" y="{142 if sub else 151}" font-size="14" font-weight="800" letter-spacing="1.2" text-anchor="middle" style="fill:{hue}">{label}</text>')
    if sub:
        add(f'<text class="t m" x="{x + w / 2}" y="161" font-size="11" text-anchor="middle" style="fill:{SLATE_L}">{sub}</text>')
for x in (304, 584, 884):
    add(f'<path d="M{x} 145 h10 m-5 -5 l5 5 l-5 5" fill="none" stroke="{SLATE_L}" stroke-width="1.6"/>')


def badge(x, y, kind, cls=""):
    if kind == "bill":
        add(f'<g class="{cls}"><rect x="{x}" y="{y}" width="96" height="26" rx="13" fill="{AMBER_D}" stroke="{AMBER}" stroke-width="1.2"/>'
            f'<circle cx="{x + 16}" cy="{y + 13}" r="4.5" fill="{AMBER}" style="animation:blink 1.2s ease-in-out infinite"/>'
            f'<text class="t" x="{x + 56}" y="{y + 17.5}" font-size="12" font-weight="700" text-anchor="middle" style="fill:{AMBER}">billing</text></g>')
    else:
        add(f'<g class="{cls}"><rect x="{x}" y="{y}" width="96" height="26" rx="13" fill="{PANEL}" stroke="{SLATE_D}" stroke-width="1.2"/>'
            f'<text class="t" x="{x + 48}" y="{y + 17.5}" font-size="12" font-weight="700" text-anchor="middle" style="fill:{SLATE_L}">free</text></g>')


# physical host
HX, HY, HW, HH = 40, 200, 520, 390
add(f'<rect x="{HX}" y="{HY}" width="{HW}" height="{HH}" rx="16" fill="none" stroke="{SLATE_L}" stroke-width="1.5" stroke-dasharray="7 6"/>')
add(f'<text class="t" x="{HX + 20}" y="{HY + 28}" font-size="12" font-weight="700" letter-spacing="1.2" style="fill:{SLATE_L}">PHYSICAL SERVER IN THE DATACENTRE</text>')
add(f'<text class="{win((0, C[0]))} t m" x="{HX + HW - 20}" y="{HY + 28}" font-size="12" text-anchor="end" style="fill:{CYAN_SOFT}">host A</text>')
add(f'<text class="{win(C)} t m" x="{HX + HW - 20}" y="{HY + 28}" font-size="12" font-weight="700" text-anchor="end" style="fill:{RED}">handed back to Azure</text>')
add(f'<text class="{win(D)} t m" x="{HX + HW - 20}" y="{HY + 28}" font-size="12" text-anchor="end" style="fill:{GREEN}">host B</text>')

# VM compute card
VX, VY, VW, VH = HX + 24, HY + 50, HW - 48, 150
add(f'<g class="{win((0, C[0]), D)}">')
add(f'<rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="14" fill="{PANEL}" stroke="{CYAN}" stroke-width="1.4"/>')
add(f'<text class="t" x="{VX + 22}" y="{VY + 36}" font-size="18" font-weight="800" style="fill:{WHITE}">vm-lab-01</text>')
add(f'<text class="t" x="{VX + 22}" y="{VY + 60}" font-size="12.5" style="fill:{CYAN_SOFT}">Standard_D2s_v3 &#183; 2 vCPU &#183; 8 GiB &#183; Ubuntu 24.04</text>')
add(f'<text class="t" x="{VX + 22}" y="{VY + 92}" font-size="12" font-weight="700" letter-spacing="1" style="fill:{SLATE_L}">COMPUTE</text>')
add('</g>')
add(f'<g class="{win(A, D)}"><text class="t" x="{VX + 22}" y="{VY + 124}" font-size="13" font-weight="600" style="fill:{GREEN}">&#9679; Ubuntu running</text></g>')
add(f'<g class="{win(B)}"><text class="t" x="{VX + 22}" y="{VY + 124}" font-size="13" font-weight="600" style="fill:{AMBER}">&#9679; Ubuntu halted, but the server is still reserved</text></g>')
badge(VX + VW - 118, VY + 104, "bill", win((0, C[0]), D))
# empty slot while deallocated
add(f'<g class="{win(C)}"><rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" rx="14" fill="none" stroke="{SLATE_D}" stroke-width="1.4" stroke-dasharray="5 6"/>'
    f'<text class="t" x="{VX + VW / 2}" y="{VY + 70}" font-size="15" font-weight="700" text-anchor="middle" style="fill:{SLATE_L}">no VM here: CPU and RAM released</text>'
    f'<text class="t" x="{VX + VW / 2}" y="{VY + 94}" font-size="12.5" text-anchor="middle" style="fill:{SLATE_L}">compute stops billing</text></g>')
badge(VX + VW - 118, VY + 104, "free", win(C))

# temp disk
TX, TY, TW, TH = VX, VY + VH + 22, VW, 130
add(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="14" fill="{PANEL}" stroke="{VIOLET}" stroke-width="1.4"/>')
add(f'<text class="t" x="{TX + 22}" y="{TY + 32}" font-size="15" font-weight="800" style="fill:{VIOLET}">Temporary disk &#183; 16 GiB &#183; /mnt</text>')
add(f'<text class="t" x="{TX + 22}" y="{TY + 54}" font-size="12" style="fill:{SLATE_L}">part of this server; included in the size price</text>')
add(f'<g class="{win((0, C[0]))}"><rect x="{TX + 22}" y="{TY + 72}" width="210" height="36" rx="9" fill="{WHITE}"/>'
    f'<text class="t m" x="{TX + 127}" y="{TY + 95}" font-size="13" font-weight="700" text-anchor="middle" style="fill:{NAVY}">/mnt/proof.txt</text></g>')
add(f'<g class="{win(C)}"><rect x="{TX + 22}" y="{TY + 72}" width="210" height="36" rx="9" fill="{RED_D}" stroke="{RED}"/>'
    f'<text class="t" x="{TX + 127}" y="{TY + 95}" font-size="13" font-weight="700" text-anchor="middle" style="fill:{RED}">wiped</text></g>')
add(f'<g class="{win(D)}"><rect x="{TX + 22}" y="{TY + 72}" width="210" height="36" rx="9" fill="none" stroke="{SLATE_D}" stroke-dasharray="4 5"/>'
    f'<text class="t m" x="{TX + 127}" y="{TY + 95}" font-size="12" text-anchor="middle" style="fill:{SLATE_L}">empty: No such file</text></g>')

# resources that live outside the server
RX, RW = 600, 560
add(f'<text class="t" x="{RX}" y="{HY + 28}" font-size="12" font-weight="700" letter-spacing="1.2" style="fill:{SLATE_L}">SEPARATE RESOURCES: THEY STAY WHEN THE SERVER GOES</text>')
ROWS = [
    ("OS disk", "30 GiB managed disk, stored apart from the server", "bill", "/opt/proof.txt"),
    ("Public IP", "Standard, static: the address is held for you", "bill", None),
    ("NIC", "owns the private IP 10.30.0.4", "free", None),
    ("NSG", "allow 22 from one IP; deny the rest", "free", None),
]
ry = HY + 46
for name, sub, kind, file_ in ROWS:
    h = 96 if file_ else 72
    add(f'<rect x="{RX}" y="{ry}" width="{RW}" height="{h}" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="1"/>')
    add(f'<text class="t" x="{RX + 20}" y="{ry + 30}" font-size="15" font-weight="800" style="fill:{WHITE}">{name}</text>')
    add(f'<text class="t" x="{RX + 20}" y="{ry + 52}" font-size="12" style="fill:{CYAN_SOFT}">{sub}</text>')
    badge(RX + RW - 116, ry + 14, kind)
    if file_:
        add(f'<rect x="{RX + 20}" y="{ry + 62}" width="190" height="26" rx="7" fill="{WHITE}"/>'
            f'<text class="t m" x="{RX + 115}" y="{ry + 80}" font-size="12.5" font-weight="700" text-anchor="middle" style="fill:{NAVY}">{file_}</text>')
        add(f'<text class="{win(D)} t" x="{RX + 224}" y="{ry + 80}" font-size="12.5" font-weight="700" style="fill:{GREEN}">&#10003; still here after deallocate</text>')
    if name in ("Public IP", "NIC"):
        add(f'<text class="{win(D)} t" x="{RX + RW - 130}" y="{ry + 58}" font-size="12" font-weight="700" text-anchor="end" style="fill:{GREEN}">&#10003; same address</text>')
    ry += h + 12

# caption per phase
CAPS = [
    (A, GREEN, "Running.", "Compute, the OS disk and the public IP all bill."),
    (B, AMBER, "Status: Stopped.", "Ubuntu halted, but Azure was never told. The server is still yours, so compute still bills."),
    (C, RED, "Status: Stopped (deallocated).", "Server handed back. Compute stops billing; /mnt is wiped. Disk and IP keep billing."),
    (D, GREEN, "Started on a new server.", "Same OS disk, same IPs. The temp disk comes back empty."),
]
add(f'<rect x="24" y="{H - 132}" width="{W - 48}" height="52" rx="12" fill="{PANEL}" stroke="{EDGE}" stroke-width="1"/>')
for span, hue, lead, rest in CAPS:
    add(f'<text class="{win(span)} t" x="44" y="{H - 100}" font-size="14.5"><tspan font-weight="800" style="fill:{hue}">{lead}</tspan> {rest}</text>')

# footer
add(f'<text class="t" x="{W / 2}" y="{H - 44}" font-size="13" text-anchor="middle" style="fill:{ICE}">'
    f'<tspan font-weight="700" style="fill:{AMBER}">A stopped VM is not a free VM</tspan> until Azure says <tspan class="m" style="fill:{RED}">deallocated</tspan>.</text>')
add(f'<text class="t" x="{W / 2}" y="{H - 22}" font-size="11.5" text-anchor="middle" style="fill:{SLATE_L}">'
    f'Only Azure can deallocate: the portal Stop button, az vm deallocate, or the auto-shutdown schedule.</text>')

defs = f'''<defs>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0 H0 V48" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glowC" x="-80%" y="-80%" width="260%" height="260%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{CYAN}" flood-opacity="0.7"/></filter>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="A VM goes from running, to stopped from inside Ubuntu, to deallocated by Azure, to running on a new server. '
       f'Compute bills until deallocated; the OS disk and public IP bill throughout; the temporary disk is wiped; the OS disk file and both IPs survive.">'
       f'<title>Turning a VM off: what keeps billing, what survives</title>'
       f'<style>{"".join(css)}</style>{defs}' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
