from xml.sax.saxutils import escape

USER = "seuusuario"
W = 62  # largura total (chars) da linha "chave: .... valor"

# ("titulo", [(chave, valor), ...]) -> edite à vontade
SECTIONS = [
    (None, [("OS", "Windows 11, Linux"),
            ("Uptime", "XX anos, X meses"),
            ("Host", "Sua Empresa"),
            ("Kernel", "Seu Cargo"),
            ("IDE", "VSCode")]),
    (None, [("Languages.Programming", "Python, JavaScript"),
            ("Languages.Computer", "HTML, CSS, JSON"),
            ("Languages.Real", "Português, English")]),
    (None, [("Hobbies.Software", "Seu hobby"),
            ("Hobbies.Hardware", "Seu hobby")]),
    ("Contact", [("Email.Personal", "voce@email.com"),
                 ("LinkedIn", "seuusuario"),
                 ("Discord", "seuusuario")]),
    ("GitHub Stats", [("Repos", "0 {Contributed: 0} | Stars: 0"),
                      ("Commits", "0 | Followers: 0"),
                      ("Lines of Code on GitHub", "0")]),
]

THEMES = {
    "dark_mode.svg":  dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", val="#a5d6ff", dot="#616e7f"),
    "light_mode.svg": dict(bg="#f6f8fa", fg="#24292f", key="#953800", val="#0a3069", dot="#b1bac4"),
}

ascii_lines = open("ascii.txt", encoding="utf-8").read().rstrip("\n").split("\n")

def build(t):
    CW, LH = 9.6, 20          # largura do char / altura de linha (direita)
    ax, rx = 20, 390          # x do ascii / x do painel
    rows, y = [], 40
    def header(txt):
        nonlocal y
        fill = "─" * (W - len(txt) - 1)
        rows.append(f'<tspan x="{rx}" y="{y}" class="fg">{escape(txt)} {fill}</tspan>')
        y += LH
    header(f"{USER}@github")
    first = True
    for title, items in SECTIONS:
        if title:
            y += LH // 2; header(title)
        elif not first:
            rows.append(f'<tspan x="{rx}" y="{y}" class="dot">.</tspan>'); y += LH
        first = False
        for k, v in items:
            n = max(W - len(k) - len(v) - 4, 2)
            rows.append(
                f'<tspan x="{rx}" y="{y}" class="dot">. </tspan>'
                f'<tspan class="key">{escape(k)}:</tspan>'
                f'<tspan class="dot"> {"." * n} </tspan>'
                f'<tspan class="val">{escape(v)}</tspan>')
            y += LH
    height = max(y + 20, len(ascii_lines) * 15 + 40)
    width = rx + int(W * CW) + 20
    art = "".join(
        f'<tspan x="{ax}" y="{30 + i*15}">{escape(l)}</tspan>' for i, l in enumerate(ascii_lines))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
text{{font-family:Consolas,"Courier New",monospace;white-space:pre}}
.art{{font-size:12px;fill:{t["fg"]}}}
.r{{font-size:16px}}
.fg{{fill:{t["fg"]}}} .key{{fill:{t["key"]}}} .val{{fill:{t["val"]}}} .dot{{fill:{t["dot"]}}}
</style>
<rect width="100%" height="100%" rx="15" fill="{t["bg"]}"/>
<text class="art" xml:space="preserve">{art}</text>
<text class="r" xml:space="preserve">{"".join(rows)}</text>
</svg>'''

for name, t in THEMES.items():
    open(name, "w", encoding="utf-8").write(build(t))
    print("gerado", name)
