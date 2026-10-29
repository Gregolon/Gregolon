from xml.sax.saxutils import escape

USER = "seuusuario"
HOST = "github"
W = 60          # largura (em caracteres) de cada linha do painel
FILL = "FILL"   # marcador: vira ". . . . ." até alinhar à direita

# Tokens: (classe, texto). Classes: k=chave(laranja) v=valor(azul) fg=branco
#         add=verde del=vermelho
def kv(k, v):
    return [("k", k), ("fg", ":"), FILL, ("v", v)]

SECTIONS = [
    (None, [kv("OS", "Windows 11, Linux"),
            kv("Uptime", "XX anos, X meses, X dias"),
            kv("Host", "Sua Empresa"),
            kv("Kernel", "Seu Cargo"),
            kv("IDE", "VSCode")]),
    (None, [kv("Languages.Programming", "Python, JavaScript"),
            kv("Languages.Computer", "HTML, CSS, JSON"),
            kv("Languages.Real", "Português, English")]),
    (None, [kv("Hobbies.Software", "Seu hobby"),
            kv("Hobbies.Hardware", "Seu hobby")]),
    ("Contact", [kv("Email.Personal", "voce@email.com"),
                 kv("LinkedIn", "seuusuario"),
                 kv("Discord", "seuusuario")]),
    ("GitHub Stats", [
        [("k", "Repos"), ("fg", ":"), FILL, ("v", "0"), ("fg", " {"), ("k", "Contributed"),
         ("fg", ": "), ("v", "0"), ("fg", "} | "), ("k", "Stars"), ("fg", ":"), FILL, ("v", "0")],
        [("k", "Commits"), ("fg", ":"), FILL, ("v", "0"), ("fg", " | "), ("k", "Followers"),
         ("fg", ":"), FILL, ("v", "0")],
        [("k", "Lines of Code on GitHub"), ("fg", ":"), FILL, ("v", "0"), ("fg", " ( "),
         ("add", "0++"), ("fg", ", "), ("del", "0--"), ("fg", " )")],
    ]),
]

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", fg="#c9d1d9", k="#ffa657", v="#a5d6ff",
                          dot="#616e7f", add="#3fb950", **{"del": "#f85149"}),
    "light_mode.svg": dict(bg="#f6f8fa", fg="#24292f", k="#953800", v="#0a3069",
                           dot="#b1bac4", add="#1a7f37", **{"del": "#cf222e"}),
}

ascii_lines = open("ascii.txt", encoding="utf-8").read().rstrip("\n").split("\n")
ACOLS = max(len(l) for l in ascii_lines)

FS, CW, LH = 14, 7.7, 20        # fonte, largura do char, altura da linha (painel)
AX, PAD_TOP = 20, 38
ART_W = ACOLS * CW
RX = int(AX + ART_W + 30)

def render_row(tokens, x, y):
    used = sum(len(t[1]) for t in tokens if t != FILL) + 2   # ". " inicial
    nfill = tokens.count(FILL)
    free = W - used - 2 * nfill                              # espaço em volta dos pontos
    per, extra = divmod(max(free, nfill * 2), nfill)
    out = [f'<tspan x="{x}" y="{y}" class="dot">. </tspan>']
    i = 0
    for t in tokens:
        if t == FILL:
            n = per + (1 if i < extra else 0); i += 1
            out.append(f'<tspan class="dot"> {"." * n} </tspan>')
        else:
            out.append(f'<tspan class="{t[0]}">{escape(t[1])}</tspan>')
    return "".join(out)

def build(c):
    rows, y = [], PAD_TOP
    def header(txt):
        nonlocal y
        line = "─" * (W - len(txt) - 1)
        rows.append(f'<tspan x="{RX}" y="{y}" class="fg">{escape(txt)} {line}</tspan>')
        y += LH
    header(f"{USER}@{HOST}")
    y_first = PAD_TOP
    first = True
    for title, items in SECTIONS:
        if title:
            rows.append(f'<tspan x="{RX}" y="{y}" class="dot">.</tspan>'); y += LH
            header(title)
        elif not first:
            rows.append(f'<tspan x="{RX}" y="{y}" class="dot">.</tspan>'); y += LH
        first = False
        for tk in items:
            rows.append(render_row(tk, RX, y)); y += LH
    y_last = y - LH
    height = y_last + 24
    width = int(RX + W * CW + 24)

    # ASCII distribuído do topo ao fim do painel => alinhado com as informações
    n = len(ascii_lines)
    step = (y_last - y_first) / (n - 1)
    art = "".join(
        f'<text x="{AX}" y="{y_first + i*step:.1f}" textLength="{len(l)*CW:.1f}" '
        f'lengthAdjust="spacing" class="art" xml:space="preserve">{escape(l)}</text>'
        for i, l in enumerate(ascii_lines))

    css = "".join(f".{k}{{fill:{v}}}" for k, v in c.items() if k != "bg")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
text{{font-family:Consolas,"Courier New",monospace;font-size:{FS}px;white-space:pre}}
.art{{fill:{c["fg"]}}}
{css}
</style>
<rect width="100%" height="100%" rx="15" fill="{c["bg"]}"/>
{art}
<text xml:space="preserve">{"".join(rows)}</text>
</svg>'''

for name, c in THEMES.items():
    open(name, "w", encoding="utf-8").write(build(c))
    print("gerado", name)
