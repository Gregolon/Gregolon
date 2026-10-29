import os, json, datetime, urllib.request
from xml.sax.saxutils import escape

USER = "Gregolon"
HOST = "github"
W = 60          # largura (em caracteres) de cada linha do painel
FILL = "FILL"   # marcador: vira ". . . . ." até alinhar à direita

# Tokens: (classe, texto). Classes: k=chave(laranja) v=valor(azul) fg=branco
#         add=verde del=vermelho

TOKEN = os.environ.get("GH_TOKEN")
BIRTH = (2007, 7, 6)   # (ano, mês, dia) -> Uptime automático

def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}"})
    with urllib.request.urlopen(req) as r:
        d = json.load(r)
    if "errors" in d:
        raise RuntimeError(d["errors"])
    return d["data"]

def get_stats():
    st = dict(repos="0", contrib="0", stars="0", followers="0",
              commits="0", loc="0", add="0", dele="0")
    if not TOKEN:
        return st
    fmt = lambda n: f"{n:,}"
    u = gql("""query($l:String!){user(login:$l){id createdAt followers{totalCount}
      repositories(ownerAffiliations:OWNER,privacy:PUBLIC){totalCount}
      repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY]){totalCount}}}""",
        {"l": USER})["user"]
    uid = u["id"]
    st["repos"] = fmt(u["repositories"]["totalCount"])
    st["contrib"] = fmt(u["repositoriesContributedTo"]["totalCount"])
    st["followers"] = fmt(u["followers"]["totalCount"])

    # stars + lista de repositórios
    repos, stars, cur = [], 0, None
    while True:
        r = gql("""query($l:String!,$c:String){user(login:$l){repositories(first:100,after:$c,
          ownerAffiliations:OWNER){pageInfo{hasNextPage endCursor}
          nodes{nameWithOwner stargazerCount isPrivate}}}}""", {"l": USER, "c": cur})["user"]["repositories"]
        for n in r["nodes"]:
            repos.append(n["nameWithOwner"])
            if not n["isPrivate"]:
                stars += n["stargazerCount"]
        if not r["pageInfo"]["hasNextPage"]:
            break
        cur = r["pageInfo"]["endCursor"]
    st["stars"] = fmt(stars)

    # commits (soma ano a ano desde a criação da conta)
    y0 = int(u["createdAt"][:4]); total = 0
    for y in range(y0, datetime.date.today().year + 1):
        c = gql("""query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){
          contributionsCollection(from:$f,to:$t){totalCommitContributions
          restrictedContributionsCount}}}""",
          {"l": USER, "f": f"{y}-01-01T00:00:00Z", "t": f"{y}-12-31T23:59:59Z"}
          )["user"]["contributionsCollection"]
        total += c["totalCommitContributions"] + c["restrictedContributionsCount"]
    st["commits"] = fmt(total)

    # linhas de código nos seus commits
    add = dele = 0
    for full in repos:
        owner, name = full.split("/"); cur = None
        while True:
            h = gql("""query($o:String!,$n:String!,$id:ID!,$c:String){repository(owner:$o,name:$n){
              defaultBranchRef{target{... on Commit{history(first:100,after:$c,author:{id:$id}){
              pageInfo{hasNextPage endCursor} nodes{additions deletions}}}}}}}""",
              {"o": owner, "n": name, "id": uid, "c": cur})["repository"]["defaultBranchRef"]
            if not h:
                break
            h = h["target"]["history"]
            for n in h["nodes"]:
                add += n["additions"]; dele += n["deletions"]
            if not h["pageInfo"]["hasNextPage"]:
                break
            cur = h["pageInfo"]["endCursor"]
    st.update(loc=fmt(add - dele), add=fmt(add), dele=fmt(dele))
    return st

def uptime():
    if not BIRTH:
        return "XX anos, X meses, X dias"
    b, t = datetime.date(*BIRTH), datetime.date.today()
    y = t.year - b.year; m = t.month - b.month; d = t.day - b.day
    if d < 0:
        m -= 1; d += (t.replace(day=1) - datetime.timedelta(days=1)).day
    if m < 0:
        y -= 1; m += 12
    return f"{y} anos, {m} meses, {d} dias"

S = get_stats()

def kv(k, v):
    return [("k", k), ("fg", ":"), FILL, ("v", v)]

SECTIONS = [
    (None, [kv("OS", "Windows 11, Linux"),
            kv("Uptime", uptime()),
            kv("Host", "DestroMacroAtacado"),
            kv("Kernel", "Junior systems analyst"),
            kv("IDE", "VSCode")]),
    (None, [kv("Languages.Programming", "Python, JavaScript"),
            kv("Languages.Computer", "HTML, CSS, JSON"),
            kv("Languages.Real", "Português, English")]),
    (None, [kv("Hobbies.Software", "Automation, ERP"),
            kv("Hobbies.Hardware", "Overclocking")]),
    ("Contact", [kv("Email.Personal", "viniciusgregolonn@gmail.com"),
                 kv("LinkedIn", "Gregolon"),
                 kv("Discord", "Gregolon")]),
    ("GitHub Stats", [
        [("k", "Repos"), ("fg", ":"), FILL, ("v", S["repos"]), ("fg", " {"), ("k", "Contributed"),
         ("fg", ": "), ("v", S["contrib"]), ("fg", "} | "), ("k", "Stars"), ("fg", ":"), FILL, ("v", S["stars"])],
        [("k", "Commits"), ("fg", ":"), FILL, ("v", S["commits"]), ("fg", " | "), ("k", "Followers"),
         ("fg", ":"), FILL, ("v", S["followers"])],
        [("k", "Lines of Code on GitHub"), ("fg", ":"), FILL, ("v", S["loc"]), ("fg", " ( "),
         ("add", S["add"] + "++"), ("fg", ", "), ("del", S["dele"] + "--"), ("fg", " )")],
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
