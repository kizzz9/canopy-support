#!/usr/bin/env python3
"""Canopy サポートサイト静的ジェネレーター。

_src/content/{page}.{lang}.json を読み、ブランド共通テンプレートで
canopy-support/ と canopy-privacy-policy/ の全ロケールページを生成する。

使い方: python3 _src/build.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVACY_ROOT = os.path.join(os.path.dirname(ROOT), "canopy-privacy-policy")
LANGS = ["ja", "en", "fr", "de", "es", "it"]
LANG_LABELS = {"ja": "日本語", "en": "English", "fr": "Français", "de": "Deutsch", "es": "Español", "it": "Italiano"}

SUPPORT_BASE = "https://kizzz9.github.io/canopy-support"
PRIVACY_BASE = "https://kizzz9.github.io/canopy-privacy-policy"

CSS = """
:root {
  --bg: #F7FAF7; --surface: #FFFFFF; --line: #DCE7DE; --ink: #14261B;
  --muted: #5E7466; --accent: #1F8A55; --accent-soft: #E3F4EA; --glow: rgba(31,138,85,.18);
  --hero-from: #0B1F14; --hero-to: #16301F; --hero-ink: #EAF6EE; --hero-muted: #9CC2A6;
  --hero-accent: #5BE49B; --kbd-bg: #FFFFFF; --kbd-line: #C9D8CC;
  --mono: ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0C1A12; --surface: #132619; --line: #24402F; --ink: #EAF6EE;
    --muted: #94AF9D; --accent: #5BE49B; --accent-soft: #1A3324; --glow: rgba(91,228,155,.14);
    --kbd-bg: #1A3021; --kbd-line: #2E4A38;
  }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  background: var(--bg); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Segoe UI", sans-serif;
  line-height: 1.75; -webkit-font-smoothing: antialiased; font-size: 16px;
}
a { color: var(--accent); }
.container { max-width: 920px; margin: 0 auto; padding: 0 24px; }

/* ─ Hero: アプリと同じ「森の中の発光」世界観 ─ */
.hero {
  background:
    radial-gradient(ellipse 70% 90% at 70% -10%, rgba(91,228,155,.13), transparent),
    radial-gradient(ellipse 50% 60% at 20% 110%, rgba(91,228,155,.07), transparent),
    linear-gradient(160deg, var(--hero-from), var(--hero-to));
  color: var(--hero-ink); position: relative; overflow: hidden;
  padding: 72px 24px 64px; text-align: center;
}
.hero::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(91,228,155,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(91,228,155,.05) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse 80% 90% at 50% 0%, #000 30%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse 80% 90% at 50% 0%, #000 30%, transparent 75%);
}
.hero > * { position: relative; }
.hero img.icon {
  width: 96px; height: 96px; border-radius: 22px;
  box-shadow: 0 18px 50px rgba(91,228,155,.28), 0 4px 14px rgba(0,0,0,.4);
  margin-bottom: 20px;
}
.hero h1 { font-size: 2.3em; font-weight: 800; letter-spacing: -.02em; margin-bottom: 10px; text-wrap: balance; }
.hero p.lede { font-size: 1.1em; color: var(--hero-muted); max-width: 560px; margin: 0 auto 18px; }
.meta-pills { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
.meta-pills span {
  font-family: var(--mono); font-size: .75em; letter-spacing: .04em;
  color: var(--hero-accent); border: 1px solid rgba(91,228,155,.35);
  border-radius: 999px; padding: 4px 14px; background: rgba(91,228,155,.08);
}

/* 言語スイッチャー */
.langs { position: absolute; top: 18px; right: 20px; display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.langs a, .langs b {
  font-family: var(--mono); font-size: .72em; text-decoration: none; font-weight: 500;
  padding: 4px 10px; border-radius: 999px; border: 1px solid transparent;
}
.langs a { color: var(--hero-muted); }
.langs a:hover { color: var(--hero-ink); border-color: rgba(91,228,155,.4); }
.langs b { color: #0B1F14; background: var(--hero-accent); }

/* ─ セクション ─ */
.section { padding: 64px 0 8px; }
.section:last-of-type { padding-bottom: 64px; }
.eyebrow {
  font-family: var(--mono); font-size: .74em; font-weight: 600; letter-spacing: .16em;
  text-transform: uppercase; color: var(--accent); display: block; margin-bottom: 10px;
}
.section h2 { font-size: 1.65em; font-weight: 800; letter-spacing: -.01em; margin-bottom: 6px; text-wrap: balance; }
.section p.sub { color: var(--muted); margin-bottom: 30px; }

/* カード */
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
.card {
  background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
  padding: 24px; transition: border-color .2s, box-shadow .2s, transform .2s;
}
.card:hover { border-color: var(--accent); box-shadow: 0 10px 32px var(--glow); transform: translateY(-2px); }
.card .emoji { font-size: 30px; display: block; margin-bottom: 12px; }
.card h3 { font-size: 1.02em; font-weight: 700; margin-bottom: 6px; }
.card p { color: var(--muted); font-size: .92em; }
.card a { font-weight: 600; text-decoration: none; }
.card a:hover { text-decoration: underline; }

/* CTA バナー */
.cta {
  display: flex; align-items: center; gap: 22px; flex-wrap: wrap;
  background: linear-gradient(135deg, var(--hero-from), var(--hero-to));
  border: 1px solid rgba(91,228,155,.3); border-radius: 16px; padding: 30px;
  color: var(--hero-ink);
}
.cta .emoji { font-size: 42px; }
.cta h3 { font-weight: 800; font-size: 1.15em; margin-bottom: 4px; }
.cta p { color: var(--hero-muted); font-size: .93em; margin-bottom: 14px; }
.cta .btn {
  display: inline-block; background: var(--hero-accent); color: #0B1F14;
  font-weight: 700; font-size: .9em; text-decoration: none;
  padding: 10px 26px; border-radius: 10px; box-shadow: 0 4px 18px rgba(91,228,155,.35);
}
.cta .btn:hover { filter: brightness(1.08); }

/* FAQ */
details {
  background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
  padding: 0 22px; margin-bottom: 12px;
}
details[open] { border-color: var(--accent); }
summary {
  cursor: pointer; font-weight: 700; font-size: .98em; padding: 18px 0; list-style: none;
  display: flex; align-items: center; gap: 12px;
}
summary::before { content: "▸"; color: var(--accent); font-size: .9em; transition: transform .2s; }
details[open] summary::before { transform: rotate(90deg); }
summary::-webkit-details-marker { display: none; }
details .a { color: var(--muted); font-size: .93em; padding: 0 0 18px 24px; }

/* ステップ（ガイド） */
.steps { display: grid; gap: 14px; }
.step { display: grid; grid-template-columns: 44px 1fr; gap: 16px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 22px; }
.step .n {
  font-family: var(--mono); font-weight: 700; font-size: 1.2em; color: var(--accent);
  width: 44px; height: 44px; border: 1px solid var(--line); border-radius: 12px;
  display: flex; align-items: center; justify-content: center; background: var(--accent-soft);
}
.step h3 { font-size: 1em; font-weight: 700; margin-bottom: 4px; }
.step p { color: var(--muted); font-size: .92em; }

/* Tip コールアウト */
.tip { border-left: 3px solid var(--accent); background: var(--accent-soft); border-radius: 0 12px 12px 0; padding: 14px 20px; margin-top: 20px; font-size: .93em; }
.tip b { color: var(--accent); font-family: var(--mono); font-size: .85em; letter-spacing: .08em; margin-right: 8px; }

/* 凡例ドット */
.legend { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px; }
.legend .row { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 12px; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; font-size: .9em; }
.legend .dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; align-self: center; }
.legend .k { font-family: var(--mono); font-size: .92em; color: var(--accent); flex-shrink: 0; }
.legend .row span:last-child { color: var(--muted); }

/* ショートカット keycaps */
.keys { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 10px; }
.keys .row { display: flex; justify-content: space-between; align-items: center; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; font-size: .92em; }
kbd {
  font-family: var(--mono); font-size: .85em; font-weight: 600;
  background: var(--kbd-bg); border: 1px solid var(--kbd-line); border-bottom-width: 2.5px;
  border-radius: 6px; padding: 3px 9px; margin-left: 4px; white-space: nowrap;
}

/* CLI コードブロック */
pre.term {
  background: #0B1F14; color: #C8EAD3; border: 1px solid rgba(91,228,155,.25);
  border-radius: 12px; padding: 22px 24px; overflow-x: auto;
  font-family: var(--mono); font-size: .88em; line-height: 1.9;
}
pre.term .c { color: #6E8F7A; }
pre.term .p { color: #5BE49B; user-select: none; }

/* フッター */
footer { border-top: 1px solid var(--line); padding: 34px 24px; text-align: center; color: var(--muted); font-size: .85em; }
footer nav { margin-bottom: 8px; display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
footer a { text-decoration: none; font-weight: 500; }
footer a:hover { text-decoration: underline; }

/* ガイド目次 */
.toc { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 22px; }
.toc a {
  font-family: var(--mono); font-size: .78em; color: var(--hero-muted); text-decoration: none;
  border: 1px solid rgba(91,228,155,.25); border-radius: 999px; padding: 5px 14px;
}
.toc a:hover { color: var(--hero-ink); border-color: rgba(91,228,155,.6); }
@media (max-width: 640px) { .hero h1 { font-size: 1.8em; } .langs { position: static; justify-content: center; margin-bottom: 18px; } }
"""

DOT_COLORS = {"red": "#FF6B6B", "blue": "#54A0FF", "green": "#5BE49B", "purple": "#B98AF5",
              "orange": "#FFA45B", "cyan": "#48D8E0", "yellow": "#F5D76E", "gray": "#8A9A8E"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def lang_dir(lang, root_lang="ja"):
    return "" if lang == root_lang else f"{lang}/"


def head(title, desc, lang, base, path_tpl, icon_depth):
    alts = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{base}/{path_tpl.format(dir=lang_dir(l))}">' for l in LANGS
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{esc(desc)}">
<title>{esc(title)}</title>
<link rel="icon" href="{icon_depth}icon.png">
{alts}
<style>{CSS}</style>
</head>
<body>"""


def lang_switcher(lang, depth_to_root, subpath=""):
    items = []
    for l in LANGS:
        href = f"{depth_to_root}{lang_dir(l)}{subpath}"
        label = LANG_LABELS[l]
        items.append(f"<b>{label}</b>" if l == lang else f'<a href="{href or "./"}">{label}</a>')
    return '<div class="langs">' + "".join(items) + "</div>"


def footer_html(c, links):
    nav = "".join(f'<a href="{href}">{esc(label)}</a>' for label, href in links)
    return f"<footer><nav>{nav}</nav><div>{esc(c['copyright'])}</div></footer></body></html>"


def build_support(lang, c):
    d = lang_dir(lang)
    depth = "../" if d else ""
    out = head(c["title"], c["lede"], lang, SUPPORT_BASE, "{dir}", depth)
    out += f"""
<header class="hero">
{lang_switcher(lang, depth)}
<img class="icon" src="{depth}icon.png" alt="Canopy">
<h1>{esc(c['h1'])}</h1>
<p class="lede">{esc(c['lede'])}</p>
</header>
<main class="container">
<section class="section">
<span class="eyebrow">Guide</span>
<h2>{esc(c['guide_h2'])}</h2>
<p class="sub">{esc(c['guide_sub'])}</p>
<div class="cta">
  <span class="emoji">📖</span>
  <div>
    <h3>{esc(c['guide_card_h'])}</h3>
    <p>{esc(c['guide_card_p'])}</p>
    <a class="btn" href="{depth}guide/{d}">{esc(c['guide_btn'])}</a>
  </div>
</div>
</section>
<section class="section">
<span class="eyebrow">Contact</span>
<h2>{esc(c['contact_h2'])}</h2>
<p class="sub">{esc(c['contact_sub'])}</p>
<div class="grid">"""
    for card in c["contact_cards"]:
        out += f"""
<div class="card"><span class="emoji">{card['emoji']}</span><h3>{esc(card['h'])}</h3>
<p>{esc(card['p'])}<br><a href="https://github.com/kizzz9/Canopy/issues" target="_blank" rel="noopener">GitHub Issues →</a></p></div>"""
    out += """
</div>
</section>
<section class="section">
<span class="eyebrow">FAQ</span>
<h2>{h2}</h2>
<p class="sub">{sub}</p>
""".format(h2=esc(c["faq_h2"]), sub=esc(c["faq_sub"]))
    for qa in c["faq"]:
        out += f"<details><summary>{esc(qa['q'])}</summary><div class=\"a\">{esc(qa['a'])}</div></details>\n"
    out += "</section>\n</main>\n"
    out += footer_html(c, [(c["footer_privacy"], f"{PRIVACY_BASE}/{d}"), (c["footer_contact"], "https://github.com/kizzz9/Canopy/issues")])
    return out


def build_guide(lang, c):
    d = lang_dir(lang)
    depth = "../../" if d else "../"
    out = head(c["title"], c["lede"], lang, SUPPORT_BASE, "guide/{dir}", depth)
    toc = "".join(f'<a href="#{sid}">{esc(label)}</a>' for sid, label in c["toc"])
    out += f"""
<header class="hero">
{lang_switcher(lang, depth, subpath="guide/" if False else "")}
<img class="icon" src="{depth}icon.png" alt="Canopy">
<h1>{esc(c['h1'])}</h1>
<p class="lede">{esc(c['lede'])}</p>
<div class="meta-pills"><span>macOS 15.0+</span><span>{esc(c['pill_readonly'])}</span><span>{esc(c['pill_offline'])}</span></div>
<nav class="toc">{toc}</nav>
</header>
<main class="container">
<section class="section" id="start">
<span class="eyebrow">Getting Started</span>
<h2>{esc(c['start_h2'])}</h2>
<p class="sub">{esc(c['start_sub'])}</p>
<div class="steps">"""
    for i, st in enumerate(c["steps"], 1):
        out += f"""
<div class="step"><div class="n">{i}</div><div><h3>{esc(st['h'])}</h3><p>{st['p']}</p></div></div>"""
    out += f"""
</div>
<div class="tip"><b>TIP</b>{esc(c['start_tip'])}</div>
</section>
<section class="section" id="features">
<span class="eyebrow">Features</span>
<h2>{esc(c['features_h2'])}</h2>
<p class="sub">{esc(c['features_sub'])}</p>
<div class="grid">"""
    for f in c["features"]:
        out += f"""
<div class="card"><span class="emoji">{f['emoji']}</span><h3>{esc(f['h'])}</h3><p>{esc(f['p'])}</p></div>"""
    out += f"""
</div>
</section>
<section class="section" id="panels">
<span class="eyebrow">Interface</span>
<h2>{esc(c['panels_h2'])}</h2>
<p class="sub">{esc(c['panels_sub'])}</p>
<div class="grid">"""
    for p in c["panels"]:
        out += f"""
<div class="card"><span class="emoji">{p['emoji']}</span><h3>{esc(p['h'])}</h3><p>{esc(p['p'])}</p></div>"""
    out += f"""
</div>
</section>
<section class="section" id="legend">
<span class="eyebrow">Legend</span>
<h2>{esc(c['legend_h2'])}</h2>
<p class="sub">{esc(c['legend_sub'])}</p>
<h3 style="margin-bottom:12px;font-size:1.02em">{esc(c['legend_dots_h'])}</h3>
<div class="legend">"""
    for row in c["legend_dots"]:
        color = DOT_COLORS.get(row["color"], "#8A9A8E")
        out += f"""
<div class="row"><span class="dot" style="background:{color}"></span><span class="k">{esc(row['k'])}</span><span>{esc(row['v'])}</span></div>"""
    out += f"""
</div>
<h3 style="margin:26px 0 12px;font-size:1.02em">{esc(c['legend_badges_h'])}</h3>
<div class="legend">"""
    for row in c["legend_badges"]:
        out += f"""
<div class="row"><span class="k">{esc(row['k'])}</span><span>{esc(row['v'])}</span></div>"""
    out += f"""
</div>
</section>
<section class="section" id="shortcuts">
<span class="eyebrow">Shortcuts</span>
<h2>{esc(c['keys_h2'])}</h2>
<p class="sub">{esc(c['keys_sub'])}</p>
<div class="keys">"""
    for k in c["keys"]:
        kbds = "".join(f"<kbd>{esc(x)}</kbd>" for x in k["keys"])
        out += f"""
<div class="row"><span>{esc(k['label'])}</span><span>{kbds}</span></div>"""
    out += f"""
</div>
</section>
<section class="section" id="export">
<span class="eyebrow">Export</span>
<h2>{esc(c['export_h2'])}</h2>
<p class="sub">{esc(c['export_sub'])}</p>
<div class="grid">"""
    for e in c["exports"]:
        out += f"""
<div class="card"><span class="emoji">{e['emoji']}</span><h3>{esc(e['h'])}</h3><p>{esc(e['p'])}</p></div>"""
    out += f"""
</div>
<div class="tip"><b>TIP</b>{esc(c['export_tip'])}</div>
</section>
<section class="section" id="cli">
<span class="eyebrow">CLI</span>
<h2>{esc(c['cli_h2'])}</h2>
<p class="sub">{esc(c['cli_sub'])}</p>
<pre class="term"><span class="c"># {esc(c['cli_c1'])}</span>
<span class="p">$</span> Canopy --analyze /path/to/project --format json

<span class="c"># {esc(c['cli_c2'])}</span>
<span class="p">$</span> Canopy --analyze /path/to/project --format sarif

<span class="c"># {esc(c['cli_c3'])}</span>
<span class="p">$</span> Canopy --format json-schema</pre>
<div class="tip"><b>SETUP</b>{esc(c['cli_setup'])}</div>
<div class="tip"><b>CI</b>{esc(c['cli_ci'])}</div>
</section>
</main>
"""
    out += footer_html(c, [(c["footer_support"], f"{SUPPORT_BASE}/{d}"), (c["footer_privacy"], f"{PRIVACY_BASE}/{d}"), (c["footer_contact"], "https://github.com/kizzz9/Canopy/issues")])
    return out


def build_privacy(lang, c):
    d = lang_dir(lang)
    depth = "../" if d else ""
    out = head(c["title"], c["summary"], lang, PRIVACY_BASE, "{dir}", depth)
    out += f"""
<header class="hero">
{lang_switcher(lang, depth)}
<img class="icon" src="{depth}icon.png" alt="Canopy">
<h1>{esc(c['h1'])}</h1>
<p class="lede">{esc(c['lede'])}</p>
<div class="meta-pills"><span>{esc(c['updated'])}</span></div>
</header>
<main class="container">
<section class="section">
<span class="eyebrow">Summary</span>
<h2>{esc(c['summary_h2'])}</h2>
<div class="cta"><span class="emoji">🔒</span><div><h3>{esc(c['summary'])}</h3></div></div>
</section>
<section class="section">
<span class="eyebrow">Details</span>
<h2>{esc(c['details_h2'])}</h2>
<p class="sub">&nbsp;</p>
<div class="grid">"""
    for card in c["cards"]:
        out += f"""
<div class="card"><span class="emoji">{card['emoji']}</span><h3>{esc(card['h'])}</h3><p>{esc(card['p'])}</p></div>"""
    out += f"""
</div>
</section>
<section class="section">
<span class="eyebrow">Contact</span>
<h2>{esc(c['contact_h2'])}</h2>
<p class="sub">{esc(c['contact_p'])} <a href="https://github.com/kizzz9/Canopy/issues" target="_blank" rel="noopener">GitHub Issues</a></p>
</section>
</main>
"""
    out += footer_html(c, [(c["footer_support"], f"{SUPPORT_BASE}/{d}"), (c["footer_contact"], "https://github.com/kizzz9/Canopy/issues")])
    return out


def main():
    content_dir = os.path.join(ROOT, "_src", "content")
    built = 0
    for lang in LANGS:
        for page, builder, out_root, sub in [
            ("support", build_support, ROOT, ""),
            ("guide", build_guide, ROOT, "guide"),
            ("privacy", build_privacy, PRIVACY_ROOT, ""),
        ]:
            src = os.path.join(content_dir, f"{page}.{lang}.json")
            if not os.path.exists(src):
                print(f"skip: {page}.{lang}.json なし")
                continue
            c = json.load(open(src))
            html_out = builder(lang, c)
            d = lang_dir(lang)
            out_dir = os.path.join(out_root, sub, d) if sub else os.path.join(out_root, d)
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "index.html"), "w") as f:
                f.write(html_out)
            built += 1
            print(f"built: {os.path.relpath(os.path.join(out_dir, 'index.html'), os.path.dirname(ROOT))}")
    print(f"\n{built} pages generated")


if __name__ == "__main__":
    main()
