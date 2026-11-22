"""Builds 06-azure-files-share/diagrams/files-access.svg: an animated view of lab 06.
Three clients reach one file share. From home, SMB on port 445 is blocked.
The portal works over HTTPS, first with the storage key, then with Entra
(denied as Owner, read-only once File Data Privileged Reader is added). A
snapshot keeps Version 1 and a restore brings it back. The VM inside Azure
mounts over SMB with the key, until shared key access is switched off.

Each phase has a short caption at the TOP that changes exactly when the
movement it describes happens. Dark Biira colourway, CSS animation only.

Usage: python lab06_files_access.py <output.svg>
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
CYCLE = 32
P1 = (0.00, 0.12)   # home laptop: 445 blocked
P2 = (0.12, 0.24)   # portal upload with the key
P3 = (0.24, 0.40)   # snapshot, change to v2, restore v1
P4 = (0.40, 0.52)   # Entra as Owner: denied
P5 = (0.52, 0.62)   # + Privileged Reader: list allowed
P6 = (0.62, 0.72)   # Reader upload: denied
P7 = (0.72, 0.85)   # VM: SMB with the key works
P8 = (0.85, 0.985)  # keys off: SMB cut, Entra still reads

css = [f"""
.t{{font-family:{FONT};fill:{ICE}}}
.m{{font-family:{MONO}}}
@media (prefers-reduced-motion: reduce){{ .anim{{animation:none!important;opacity:1!important;transform:none!important}} }}
@keyframes sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
"""]
_n = [0]


def pct(f):
    return f"{f * 100:.1f}%"


def win(*spans, fade=0.010):
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


def mover(span, dx, travel=0.55):
    """Slides right by dx during the first part of span, holds, visible only in span."""
    _n[0] += 1
    name = f"mv{_n[0]}"
    a, b = span
    mid = a + (b - a) * travel
    kf = (f"0%{{opacity:0;transform:translateX(0px)}}"
          f"{pct(max(a - 0.001, 0))}{{opacity:0;transform:translateX(0px)}}"
          f"{pct(a + 0.008)}{{opacity:1;transform:translateX(0px)}}"
          f"{pct(mid)}{{opacity:1;transform:translateX({dx}px)}}"
          f"{pct(b - 0.004)}{{opacity:1;transform:translateX({dx}px)}}"
          f"{pct(b + 0.004)}{{opacity:0;transform:translateX({dx}px)}}"
          f"100%{{opacity:0;transform:translateX({dx}px)}}")
    css.append(f"@keyframes {name}{{{kf}}}.{name}{{animation:{name} {CYCLE}s cubic-bezier(.45,.05,.35,1) infinite}}")
    return f"anim {name}"


def at(span, frac):
    a, b = span
    return a + (b - a) * frac


body = []
add = body.append

add(f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>')
add(f'<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>')

# masthead
add(f'<g transform="translate(52 50)">'
    f'<path d="M0 -26 L20 -17 V4 Q20 16 0 26 Q-20 16 -20 4 V-17 Z" fill="{NAVY}" stroke="{CYAN}" stroke-width="2.5" filter="url(#glowC)"/>'
    f'<circle r="12" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.5"/><circle r="4" fill="{CYAN}"/>'
    f'<g class="anim" style="animation:sweep 6s linear infinite;transform-origin:0px 0px">'
    f'<path d="M0 0 L-7 -16 A17 17 0 0 1 7 -16 Z" fill="{CYAN}" opacity="0.45"/></g></g>')
add(f'<text class="t" x="96" y="42" font-size="24" font-weight="700" style="fill:{WHITE}">One file share, three ways in: who gets through, and with what</text>')
add(f'<text class="t" x="96" y="70" font-size="14" style="fill:{CYAN_SOFT}">az-104-labs &#183; lab 06 Azure Files &#183; SMB vs HTTPS, keys vs Entra roles, snapshots</text>')
add(f'<rect x="0" y="92" width="{W}" height="2" fill="{CYAN}" opacity="0.9"/>')

# TOP caption strip: one short line per phase, switching with the movement
TOPS = [
    (P1, RED, "1  From home: SMB on port 445 is blocked before it leaves the building"),
    (P2, GREEN, "2  Portal upload over HTTPS (443): works, using the storage key"),
    ((P3[0], at(P3, 0.33)), CYAN, "3  Snapshot taken: policy.txt frozen at Version 1"),
    ((at(P3, 0.33), at(P3, 0.66)), AMBER, "3  Live file changed to Version 2; the snapshot still says Version 1"),
    ((at(P3, 0.66), P3[1]), GREEN, "3  Restore from the snapshot: Version 1 is back"),
    (P4, RED, "4  Switch to Entra as Owner: denied, Owner has no data actions"),
    (P5, GREEN, "5  Add Storage File Data Privileged Reader: listing works"),
    (P6, RED, "6  Same Reader role tries to upload: denied, no write"),
    (P7, GREEN, "7  VM inside Azure maps the share over SMB with the key: works"),
    (P8, RED, "8  Shared key access OFF: the VM is cut off, Entra still reads"),
]
add(f'<rect x="24" y="106" width="{W - 48}" height="42" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
for span, hue, text in TOPS:
    add(f'<g class="{win(span)}"><rect x="24" y="106" width="6" height="42" rx="3" fill="{hue}"/>'
        f'<text class="t" x="{W / 2}" y="133" font-size="16" font-weight="700" text-anchor="middle" style="fill:{hue}">{text}</text></g>')

# clients
CX, CW, CH = 28, 250, 112
LANES = {"home": 236, "portal": 386, "vm": 536}
CLIENTS = [
    ("home", "Your laptop", "home network &#183; SMB client", SLATE_L),
    ("portal", "Azure portal (you)", "HTTPS 443 &#183; key or Entra", VIOLET),
    ("vm", "vm-files-01", "inside Azure &#183; Linux cifs", CYAN),
]
for key, title, sub, hue in CLIENTS:
    y = LANES[key]
    add(f'<rect x="{CX}" y="{y - CH / 2}" width="{CW}" height="{CH}" rx="14" fill="{PANEL}" stroke="{hue}" stroke-width="1.4"/>')
    add(f'<text class="t" x="{CX + 18}" y="{y - 18}" font-size="15.5" font-weight="800" style="fill:{WHITE}">{title}</text>')
    add(f'<text class="t" x="{CX + 18}" y="{y + 4}" font-size="11.5" style="fill:{SLATE_L}">{sub}</text>')
# portal identity chip (changes in P5)
add(f'<g class="{win((0, P5[0]))}"><rect x="{CX + 16}" y="{LANES["portal"] + 16}" width="{CW - 32}" height="24" rx="12" fill="{NAVY}" stroke="{SLATE_D}"/>'
    f'<text class="t" x="{CX + CW / 2}" y="{LANES["portal"] + 32}" font-size="11" text-anchor="middle" style="fill:{SLATE_L}">role: Owner (management plane only)</text></g>')
add(f'<g class="{win((P5[0], 0.985))}"><rect x="{CX + 16}" y="{LANES["portal"] + 16}" width="{CW - 32}" height="24" rx="12" fill="{GREEN_D}" stroke="{GREEN}"/>'
    f'<text class="t" x="{CX + CW / 2}" y="{LANES["portal"] + 32}" font-size="11" font-weight="700" text-anchor="middle" style="fill:{GREEN}">+ File Data Privileged Reader</text></g>')
# portal auth method chip (key until P4)
add(f'<g class="{win((0, P4[0]))}"><text class="t m" x="{CX + 18}" y="{LANES["portal"] + 54}" font-size="10.5" style="fill:{AMBER}">auth: access key</text></g>')
add(f'<g class="{win((P4[0], 0.985))}"><text class="t m" x="{CX + 18}" y="{LANES["portal"] + 54}" font-size="10.5" style="fill:{VIOLET}">auth: Entra user account</text></g>')
add(f'<text class="t m" x="{CX + 18}" y="{LANES["home"] + 30}" font-size="10.5" style="fill:{SLATE_L}">Test-NetConnection :445</text>')
add(f'<text class="t m" x="{CX + 18}" y="{LANES["vm"] + 30}" font-size="10.5" style="fill:{SLATE_L}">mount -t cifs ... (key)</text>')

# lanes and the home gate
LX0, LX1 = CX + CW, 700
for key, y in LANES.items():
    add(f'<line x1="{LX0}" y1="{y}" x2="{LX1}" y2="{y}" stroke="{EDGE}" stroke-width="2" stroke-dasharray="2 6"/>')
GATE_X = 470
add(f'<rect x="{GATE_X}" y="{LANES["home"] - 40}" width="18" height="80" rx="4" fill="{RED_D}" stroke="{RED}" stroke-width="1.4"/>')
add(f'<text class="t" x="{GATE_X + 9}" y="{LANES["home"] - 48}" font-size="10.5" text-anchor="middle" style="fill:{RED}">home network &#183; 445 out blocked</text>')

# storage account
SX, SY, SW, SH = 700, 170, 472, 440
add(f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="none" stroke="{CYAN}" stroke-width="1.6" stroke-dasharray="6 6"/>')
add(f'<text class="t" x="{SX + 18}" y="{SY + 26}" font-size="14" font-weight="800" style="fill:{WHITE}">stlabfilesnoble01</text>')
add(f'<text class="t" x="{SX + 18}" y="{SY + 44}" font-size="11" style="fill:{SLATE_L}">.file.core.windows.net &#183; SMB 445 and HTTPS 443</text>')
add(f'<g class="{win((0, P8[0] + 0.01))}"><rect x="{SX + SW - 176}" y="{SY + 14}" width="160" height="26" rx="13" fill="{AMBER_D}" stroke="{AMBER}"/>'
    f'<text class="t" x="{SX + SW - 96}" y="{SY + 32}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{AMBER}">shared key access: ON</text></g>')
add(f'<g class="{win((P8[0] + 0.01, 0.985))}"><rect x="{SX + SW - 176}" y="{SY + 14}" width="160" height="26" rx="13" fill="{RED_D}" stroke="{RED}"/>'
    f'<text class="t" x="{SX + SW - 96}" y="{SY + 32}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{RED}">shared key access: OFF</text></g>')

# the share and its files
FX, FY, FW, FH = SX + 18, SY + 62, SW - 36, 224
add(f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
add(f'<text class="t" x="{FX + 16}" y="{FY + 26}" font-size="14" font-weight="800" style="fill:{CYAN}">branch-docs</text>')
add(f'<text class="t" x="{FX + 120}" y="{FY + 26}" font-size="11" style="fill:{SLATE_L}">share &#183; Transaction optimized &#183; soft delete 7 days</text>')
files = ["cash-handling-procedure.md", "complaints-log.csv", "opening-hours.txt", "staff-rota.csv"]
for i, f in enumerate(files):
    add(f'<text class="t m" x="{FX + 18}" y="{FY + 54 + i * 22}" font-size="12" style="fill:{ICE}">{f}</text>')
PY = FY + 54 + 4 * 22
add(f'<text class="t m" x="{FX + 18}" y="{PY}" font-size="12" style="fill:{ICE}">policy.txt</text>')
v2 = (at(P3, 0.33), at(P3, 0.66))
add(f'<g class="{win((0, v2[0]), (v2[1], 0.985))}"><rect x="{FX + 140}" y="{PY - 14}" width="92" height="20" rx="10" fill="{GREEN_D}" stroke="{GREEN}"/>'
    f'<text class="t" x="{FX + 186}" y="{PY}" font-size="11" font-weight="700" text-anchor="middle" style="fill:{GREEN}">Version 1</text></g>')
add(f'<g class="{win(v2)}"><rect x="{FX + 140}" y="{PY - 14}" width="92" height="20" rx="10" fill="{AMBER_D}" stroke="{AMBER}"/>'
    f'<text class="t" x="{FX + 186}" y="{PY}" font-size="11" font-weight="700" text-anchor="middle" style="fill:{AMBER}">Version 2</text></g>')
add(f'<g class="{win((at(P7, 0.55), 0.985))}"><text class="t m" x="{FX + 18}" y="{PY + 24}" font-size="12" style="fill:{CYAN}">from-linux.txt</text>'
    f'<text class="t" x="{FX + 140}" y="{PY + 24}" font-size="11" style="fill:{CYAN_SOFT}">written over SMB, seen over HTTPS</text></g>')

# snapshot
NX, NY, NW, NH = FX, FY + FH + 16, FW, 86
add(f'<rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" rx="12" fill="none" stroke="{SLATE_D}" stroke-dasharray="5 5"/>')
add(f'<g class="{win((0, P3[0]))}"><text class="t" x="{NX + NW / 2}" y="{NY + 48}" font-size="12" text-anchor="middle" style="fill:{SLATE_L}">no snapshots yet</text></g>')
add(f'<g class="{win((P3[0], 0.985))}"><rect x="{NX}" y="{NY}" width="{NW}" height="{NH}" rx="12" fill="{NAVY}" stroke="{CYAN}" stroke-width="1.3"/>'
    f'<text class="t" x="{NX + 16}" y="{NY + 26}" font-size="13" font-weight="800" style="fill:{CYAN}">Snapshot 2026-11-20T04:30Z</text>'
    f'<text class="t" x="{NX + 16}" y="{NY + 46}" font-size="11.5" style="fill:{SLATE_L}">read-only &#183; Manual &#183; "before policy v2"</text>'
    f'<text class="t m" x="{NX + 16}" y="{NY + 70}" font-size="12" style="fill:{GREEN}">policy.txt = Version 1</text></g>')
add(f'<g class="{win((at(P3, 0.66), P3[1]))}"><path d="M{NX + NW - 60} {NY} L {NX + NW - 60} {PY + 8}" stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="6 5" marker-end="url(#arrG)"/>'
    f'<text class="t" x="{NX + NW - 70}" y="{NY - 8}" font-size="11" font-weight="700" text-anchor="end" style="fill:{GREEN}">restore: overwrite original</text></g>')

# requests and results
PILL_W = 136


def request(span, lane, label, stop_x, ok, msg, msg_x=None):
    y = LANES[lane]
    x0 = LX0 + 8
    cls = mover(span, stop_x - x0 - PILL_W)
    add(f'<g class="{cls}"><rect x="{x0}" y="{y - 15}" width="{PILL_W}" height="30" rx="15" fill="{WHITE}" filter="url(#glowC)"/>'
        f'<text class="t" x="{x0 + PILL_W / 2}" y="{y + 5}" font-size="12" font-weight="800" text-anchor="middle" style="fill:{NAVY}">{label}</text></g>')
    hue, dark = (GREEN, GREEN_D) if ok else (RED, RED_D)
    bx = msg_x if msg_x is not None else LX0 + 30
    add(f'<g class="{win((at(span, 0.55), span[1]))}"><rect x="{bx}" y="{y + 22}" width="300" height="28" rx="9" fill="{dark}" stroke="{hue}" stroke-width="1.3"/>'
        f'<text class="t m" x="{bx + 150}" y="{y + 41}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{hue}">{msg}</text></g>')


request(P1, "home", "SMB :445", GATE_X, False, "TcpTestSucceeded: False")
request(P2, "portal", "Upload (key)", SX + 10, True, "uploaded: 5 files")
request(P4, "portal", "List (Entra)", SX - 4, False, "403: no permission to list")
request(P5, "portal", "List (Reader)", SX + 10, True, "6 files listed")
request(P6, "portal", "Upload (Reader)", SX - 4, False, "403: not authorized to write")
request(P7, "vm", "SMB :445 + key", SX + 10, True, "mounted at /media/branch-docs")
# keys off: two results, no mover
add(f'<g class="{win((at(P8, 0.25), P8[1]))}"><rect x="{LX0 + 30}" y="{LANES["vm"] + 22}" width="300" height="28" rx="9" fill="{RED_D}" stroke="{RED}" stroke-width="1.3"/>'
    f'<text class="t m" x="{LX0 + 180}" y="{LANES["vm"] + 41}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{RED}">Host is down &#183; mount error(13)</text></g>')
add(f'<g class="{win((at(P8, 0.45), P8[1]))}"><rect x="{LX0 + 30}" y="{LANES["portal"] + 22}" width="300" height="28" rx="9" fill="{GREEN_D}" stroke="{GREEN}" stroke-width="1.3"/>'
    f'<text class="t m" x="{LX0 + 180}" y="{LANES["portal"] + 41}" font-size="11.5" font-weight="700" text-anchor="middle" style="fill:{GREEN}">Entra + Reader: still lists</text></g>')
add(f'<g class="{win(P8)}"><line x1="{LX0 + 10}" y1="{LANES["vm"]}" x2="{LX1}" y2="{LANES["vm"]}" stroke="{RED}" stroke-width="3" stroke-dasharray="10 8"/></g>')

# bottom caption bar: fuller explanation per phase
CAPS = [
    (P1, RED, "Port 445:", "SMB needs outbound 445. Home and many ISP networks block it; HTTPS on 443 is not affected."),
    (P2, GREEN, "Access key:", "the portal quietly read the key, which an Owner may do. The key opens every share in the account."),
    (P3, CYAN, "Snapshot:", "a read-only copy of the whole share at one moment. Changes after it never touch it."),
    (P4, RED, "Two planes:", "Owner holds actions, not dataActions. Without the key, it cannot even list the files."),
    (P5, GREEN, "Data role:", "Storage File Data Privileged Reader is for portal, CLI and REST. SMB uses the SMB Share roles."),
    (P6, RED, "Least privilege:", "Reader lists and downloads. Writing needs Privileged Contributor."),
    (P7, GREEN, "Inside Azure:", "445 is open, so SMB works. The SMB username is the account name; the password is the key."),
    (P8, RED, "Keys off:", "every key, SAS and key-based SMB mount stops at once. Only Entra roles over HTTPS remain."),
]
add(f'<rect x="24" y="{H - 128}" width="{W - 48}" height="48" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')
for span, hue, lead, rest in CAPS:
    add(f'<text class="{win(span)} t" x="44" y="{H - 98}" font-size="14"><tspan font-weight="800" style="fill:{hue}">{lead}</tspan> {rest}</text>')

add(f'<text class="t" x="{W / 2}" y="{H - 46}" font-size="13" text-anchor="middle" style="fill:{ICE}">'
    f'<tspan font-weight="700" style="fill:{AMBER}">A storage key is one password for every file.</tspan> '
    f'Roles say who; keys only say "someone with the key".</text>')
add(f'<text class="t" x="{W / 2}" y="{H - 22}" font-size="11.5" text-anchor="middle" style="fill:{SLATE_L}">'
    f'Identity-based SMB (per-user mounts) needs AD DS, Entra Domain Services or Entra Kerberos: not set up in this lab.</text>')

defs = f'''<defs>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0 H0 V48" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<filter id="glowC" x="-80%" y="-80%" width="260%" height="260%"><feDropShadow dx="0" dy="0" stdDeviation="4" flood-color="{CYAN}" flood-opacity="0.6"/></filter>
<marker id="arrG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{GREEN}"/></marker>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="A laptop at home cannot reach the file share because port 445 is blocked. The portal uploads over HTTPS with the storage key. '
       f'A snapshot keeps Version 1 of policy.txt and a restore brings it back. With Entra, Owner is denied; File Data Privileged Reader can list but not upload. '
       f'A VM in Azure mounts the share over SMB with the key until shared key access is turned off, which cuts it off while Entra access keeps working.">'
       f'<title>One file share, three ways in</title>'
       f'<style>{"".join(css)}</style>{defs}' + "".join(body) + '</svg>')
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(svg), "bytes")
