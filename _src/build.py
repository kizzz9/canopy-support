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

# お問い合わせフォーム（Cloudflare Worker + Resend）。worker/ 配下にバックエンド。
CONTACT_ENDPOINT = "https://canopy-contact.nsmtkz9.workers.dev"
# Turnstile ウィジェットの Site Key（kizzz9.github.io ドメイン向け・Tabilm と共用）。
# 空文字にすると widget を出さず、ハニーポット + Origin チェックのみで運用する。
TURNSTILE_SITEKEY = "0x4AAAAAADv-5iOVlinTmIvp"

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

/* ─ Hero: 左=メッセージ / 右=View ツリーパネル（プロダクトを住まわせる） ─ */
.hero {
  background:
    radial-gradient(ellipse 70% 90% at 75% -10%, rgba(91,228,155,.16), transparent),
    radial-gradient(ellipse 50% 60% at 10% 110%, rgba(91,228,155,.07), transparent),
    linear-gradient(160deg, var(--hero-from), var(--hero-to));
  color: var(--hero-ink); position: relative; overflow: hidden;
  padding: 84px 24px 72px;
}
.hero::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(91,228,155,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(91,228,155,.05) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse 90% 100% at 60% 0%, #000 30%, transparent 78%);
  -webkit-mask-image: radial-gradient(ellipse 90% 100% at 60% 0%, #000 30%, transparent 78%);
}
.hero > * { position: relative; }
.hero-grid {
  max-width: 1060px; margin: 0 auto; display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(0, .92fr);
  gap: 56px; align-items: center;
}
.hero-brand { display: flex; align-items: center; gap: 14px; margin-bottom: 26px; }
.hero-brand img { width: 56px; height: 56px; border-radius: 14px; box-shadow: 0 10px 30px rgba(91,228,155,.3); }
.hero-brand .wordmark { font-weight: 800; font-size: 1.3em; letter-spacing: -.01em; }
.hero-brand .page-tag {
  font-family: var(--mono); font-size: .68em; letter-spacing: .12em; text-transform: uppercase;
  color: var(--hero-accent); border: 1px solid rgba(91,228,155,.4); border-radius: 999px; padding: 3px 12px;
}
.hero h1 { font-size: 2.7em; font-weight: 800; letter-spacing: -.025em; line-height: 1.2; margin-bottom: 16px; text-wrap: balance; }
.hero p.lede { font-size: 1.08em; color: var(--hero-muted); margin-bottom: 22px; max-width: 34em; }
.meta-pills { display: flex; gap: 10px; flex-wrap: wrap; }
.meta-pills span {
  font-family: var(--mono); font-size: .75em; letter-spacing: .04em;
  color: var(--hero-accent); border: 1px solid rgba(91,228,155,.35);
  border-radius: 999px; padding: 4px 14px; background: rgba(91,228,155,.08);
}

/* View ツリーパネル（アプリの中央ペインを CSS で再現） */
.treecard {
  background: #0E211613; background: rgba(7, 18, 12, .72);
  border: 1px solid rgba(91,228,155,.28); border-radius: 14px;
  box-shadow: 0 34px 90px rgba(0,0,0,.5), 0 0 70px rgba(91,228,155,.12);
  font-family: var(--mono); font-size: 13px; overflow: hidden;
  backdrop-filter: blur(4px);
}
.treecard .bar {
  display: flex; align-items: center; gap: 8px;
  padding: 11px 14px; border-bottom: 1px solid rgba(91,228,155,.18);
  color: #9CC2A6; font-size: .85em; letter-spacing: .06em;
}
.treecard .bar i { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.treecard .rows { padding: 12px 16px 16px; line-height: 2.05; white-space: nowrap; overflow-x: auto; }
.treecard .row { display: flex; align-items: center; gap: 8px; color: #D7EEDD; }
.treecard .row .guide { color: #3E5C49; }
.treecard .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.treecard .mod { color: #6E8F7A; font-size: .85em; }
.treecard .badge {
  font-size: .72em; font-weight: 700; border-radius: 5px; padding: 1px 7px; line-height: 1.6;
}
.treecard .bA { background: #2F9E63; color: #06130C; }
.treecard .bC { background: #C9A83C; color: #131006; }
.treecard .bF { background: #D9544A; color: #FFF; }
.treecard .row.hot { background: rgba(217,84,74,.12); border-radius: 6px; margin: 0 -8px; padding: 0 8px; }
.treecard .foot {
  border-top: 1px solid rgba(91,228,155,.18); padding: 10px 16px;
  color: #5BE49B; font-size: .82em; letter-spacing: .04em;
}
@media (max-width: 880px) {
  .hero-grid { grid-template-columns: 1fr; gap: 36px; }
  .hero h1 { font-size: 2em; }
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

/* ガイド誘導カード（中身のプレビュー付き） */
.cta .chips { display: flex; gap: 8px; flex-wrap: wrap; margin: 2px 0 16px; }
.cta .chips span {
  font-family: var(--mono); font-size: .72em; letter-spacing: .05em;
  color: var(--hero-accent); border: 1px solid rgba(91,228,155,.3);
  border-radius: 6px; padding: 3px 10px; background: rgba(91,228,155,.06);
}

/* お問い合わせカード: 用途別カラーストライプ + mono タグ */
.card { position: relative; overflow: hidden; }
.card .tag {
  display: inline-block; font-family: var(--mono); font-size: .68em; font-weight: 700;
  letter-spacing: .12em; border-radius: 6px; padding: 3px 10px; margin-bottom: 14px;
}
.card.t-bug::before, .card.t-idea::before, .card.t-q::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.card.t-bug::before { background: #D9544A; }
.card.t-bug .tag { background: rgba(217,84,74,.14); color: #E0766D; }
.card.t-idea::before { background: var(--accent); }
.card.t-idea .tag { background: var(--accent-soft); color: var(--accent); }
.card.t-q::before { background: #48A8D8; }
.card.t-q .tag { background: rgba(72,168,216,.14); color: #5FB6E0; }

/* FAQ 採番 */
summary .qn { font-family: var(--mono); font-size: .8em; color: var(--accent); font-weight: 600; min-width: 34px; }

/* プライバシー監査カード（Canopy 風セルフオーディット） */
.audit {
  display: grid; grid-template-columns: 170px 1fr; gap: 34px; align-items: center;
  background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 34px;
}
.audit .ringwrap { text-align: center; }
.audit .ring {
  width: 140px; height: 140px; border-radius: 50%; margin: 0 auto 12px;
  background: conic-gradient(var(--accent) 0turn 1turn);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 44px var(--glow);
}
.audit .ring .inner {
  width: 116px; height: 116px; border-radius: 50%; background: var(--surface);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.audit .ring .grade { font-weight: 900; font-size: 44px; color: var(--accent); line-height: 1; }
.audit .ring .score { font-family: var(--mono); font-size: .72em; color: var(--muted); margin-top: 4px; }
.audit .ringwrap .label { font-family: var(--mono); font-size: .7em; letter-spacing: .14em; color: var(--muted); text-transform: uppercase; }
.audit .crow { display: grid; grid-template-columns: 110px 1fr; gap: 16px; padding: 13px 0; border-bottom: 1px solid var(--line); align-items: baseline; }
.audit .crow:last-child { border-bottom: none; }
.audit .st {
  font-family: var(--mono); font-size: .7em; font-weight: 700; letter-spacing: .08em;
  color: var(--accent); background: var(--accent-soft); border-radius: 6px;
  padding: 3px 0; text-align: center;
}
.audit .crow h3 { font-size: .98em; font-weight: 700; margin-bottom: 2px; }
.audit .crow p { color: var(--muted); font-size: .88em; margin: 0; }
@media (max-width: 720px) { .audit { grid-template-columns: 1fr; } }

/* サイトナビ */
.site-nav {
  background: var(--bg); border-bottom: 1px solid var(--line);
  padding: 0 24px; display: flex; align-items: stretch; gap: 0;
  font-size: .88em; position: sticky; top: 0; z-index: 100;
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.site-nav .brand {
  display: flex; align-items: center; gap: 8px; font-weight: 700;
  text-decoration: none; color: var(--ink); padding: 10px 0; margin-right: 24px;
}
.site-nav .brand img { width: 22px; height: 22px; border-radius: 5px; }
.site-nav .sep { display: none; }
.site-nav a.nav-link {
  text-decoration: none; color: var(--muted); font-weight: 500;
  padding: 10px 14px; border-bottom: 2px solid transparent; transition: color .15s, border-color .15s;
}
.site-nav a.nav-link:hover { color: var(--ink); border-bottom-color: var(--line); }
.site-nav a.nav-link.active { color: var(--accent); font-weight: 700; border-bottom-color: var(--accent); }

/* フッター */
footer { border-top: 1px solid var(--line); padding: 34px 24px; text-align: center; color: var(--muted); font-size: .85em; }
footer nav { margin-bottom: 8px; display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
footer a { text-decoration: none; font-weight: 500; }
footer a:hover { text-decoration: underline; }

/* ガイド目次 */
.toc { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 22px; }
.toc a {
  font-family: var(--mono); font-size: .78em; color: var(--hero-muted); text-decoration: none;
  border: 1px solid rgba(91,228,155,.25); border-radius: 999px; padding: 5px 14px;
}
.toc a:hover { color: var(--hero-ink); border-color: rgba(91,228,155,.6); }
@media (max-width: 640px) { .hero h1 { font-size: 1.8em; } .langs { position: static; justify-content: center; margin-bottom: 18px; } }

/* お問い合わせフォーム */
.form-card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 26px; }
.field { margin-bottom: 15px; }
.field label { display: block; font-size: .82em; font-weight: 600; color: var(--muted); margin-bottom: 6px; }
.field .req { color: var(--accent); margin-left: 8px; font-size: .72em; font-family: var(--mono); letter-spacing: .06em; }
.field input, .field textarea {
  width: 100%; background: var(--bg); border: 1px solid var(--line);
  border-radius: 9px; padding: 11px 13px; font: inherit; font-size: .95em; color: var(--ink);
}
.field input:focus, .field textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--glow); }
.field textarea { min-height: 150px; resize: vertical; }
.hp { position: absolute; left: -5000px; width: 1px; height: 1px; opacity: 0; }
.submit {
  display: inline-block; background: var(--accent); color: var(--surface);
  border: none; border-radius: 10px; padding: 12px 30px;
  font: inherit; font-size: .95em; font-weight: 700; cursor: pointer; transition: filter .15s;
}
.submit:hover { filter: brightness(1.08); }
.submit:disabled { opacity: .55; cursor: default; }
.form-status { display: inline-block; margin-left: 14px; font-size: .9em; color: var(--accent); }
.form-status.err { color: #D9544A; }
.form-note { margin-top: 16px; font-size: .88em; color: var(--muted); }
.cf-turnstile { margin-top: 4px; }
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


def tree_card():
    """アプリの View ツリーパネルを CSS で再現したヒーロー用モック（全ロケール共通）。"""
    return """<div class="treecard" aria-hidden="true">
<div class="bar"><i style="background:#FF5F57"></i><i style="background:#FEBC2E"></i><i style="background:#28C840"></i>&nbsp;View Tree — MyApp</div>
<div class="rows">
<div class="row"><span class="dot" style="background:#54A0FF"></span>ContentView <span class="mod">body</span><span class="badge bA">A</span></div>
<div class="row"><span class="guide">├</span><span class="dot" style="background:#FFA45B"></span>NavigationStack <span class="mod">.navigationTitle</span></div>
<div class="row hot"><span class="guide">│&nbsp;&nbsp;├</span><span class="dot" style="background:#54A0FF"></span>SettingsView <span class="mod">81 nodes · depth 6</span><span class="badge bF">F</span></div>
<div class="row"><span class="guide">│&nbsp;&nbsp;│&nbsp;&nbsp;├</span><span class="dot" style="background:#48D8E0"></span>Form <span class="mod">×6 Section</span></div>
<div class="row"><span class="guide">│&nbsp;&nbsp;│&nbsp;&nbsp;└</span><span class="dot" style="background:#5BE49B"></span>Toggle <span class="mod">×12 · @State 11</span></div>
<div class="row"><span class="guide">│&nbsp;&nbsp;└</span><span class="dot" style="background:#54A0FF"></span>DashboardView <span class="mod">14 nodes</span><span class="badge bA">A</span></div>
<div class="row"><span class="guide">└</span><span class="dot" style="background:#54A0FF"></span>DetailView <span class="mod">22 nodes</span><span class="badge bC">C</span></div>
</div>
<div class="foot">✓ 151 files parsed · 1 file needs splitting</div>
</div>"""


def hero_html(lang, depth, page_tag, h1, lede, extra=""):
    return f"""
<header class="hero">
{lang_switcher(lang, depth)}
<div class="hero-grid">
<div>
  <div class="hero-brand"><img src="{depth}icon.png" alt="Canopy"><span class="wordmark">Canopy</span><span class="page-tag">{page_tag}</span></div>
  <h1>{esc(h1)}</h1>
  <p class="lede">{esc(lede)}</p>
  {extra}
</div>
{tree_card()}
</div>
</header>"""


def lang_switcher(lang, depth_to_root, subpath=""):
    items = []
    for l in LANGS:
        href = f"{depth_to_root}{lang_dir(l)}{subpath}"
        label = LANG_LABELS[l]
        items.append(f"<b>{label}</b>" if l == lang else f'<a href="{href or "./"}">{label}</a>')
    return '<div class="langs">' + "".join(items) + "</div>"


def site_nav_html(c, depth, lang, active_page):
    d = lang_dir(lang)
    support_url = f"{depth}{d}" or "./"
    guide_url = f"{depth}guide/{d}"
    nav_items = [
        ("support", c.get("nav_support", "Support"), support_url),
        ("guide", c.get("nav_guide", "Guide"), guide_url),
    ]
    links = []
    for key, label, href in nav_items:
        cls = "nav-link active" if key == active_page else "nav-link"
        links.append(f'<a href="{href}" class="{cls}">{esc(label)}</a>')
    return (
        f'<nav class="site-nav">'
        f'<a class="brand" href="{support_url}"><img src="{depth}icon.png" alt="">Canopy</a>'
        f'{"".join(links)}'
        f'</nav>'
    )


def footer_html(c, links):
    nav = "".join(f'<a href="{href}">{esc(label)}</a>' for label, href in links)
    return f"<footer><nav>{nav}</nav><div>{esc(c['copyright'])}</div></footer></body></html>"


def contact_form_html(lang, c):
    """お問い合わせフォーム（Cloudflare Worker 受け口）。全ロケール共通の骨格 + JSON の form 文言。"""
    f = c["form"]
    turnstile_script = ""
    turnstile_widget = ""
    if TURNSTILE_SITEKEY:
        turnstile_script = '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>'
        turnstile_widget = (
            f'<div class="field"><div class="cf-turnstile" data-sitekey="{TURNSTILE_SITEKEY}" '
            f'data-theme="auto" data-language="{lang}"></div></div>'
        )
    statuses = json.dumps({
        "msg": f["st_message"], "turnstile": f["st_turnstile"],
        "sending": f["st_sending"], "success": f["st_success"], "error": f["st_error"],
    }, ensure_ascii=False)
    return f"""{turnstile_script}
<form class="form-card" id="contact-form">
  <div class="field">
    <label for="cf-name">{esc(f['name_label'])}</label>
    <input id="cf-name" name="name" type="text" maxlength="100" autocomplete="name">
  </div>
  <div class="field">
    <label for="cf-email">{esc(f['email_label'])}</label>
    <input id="cf-email" name="email" type="email" maxlength="200" autocomplete="email">
  </div>
  <div class="field">
    <label for="cf-message">{esc(f['message_label'])}<span class="req">{esc(f['required'])}</span></label>
    <textarea id="cf-message" name="message" maxlength="5000" required></textarea>
  </div>
  <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  {turnstile_widget}
  <button type="submit" class="submit">{esc(f['submit'])}</button>
  <span class="form-status" id="form-status" role="status"></span>
  <p class="form-note">{esc(f['note'])}</p>
</form>
<script>
(() => {{
  const ENDPOINT = "{CONTACT_ENDPOINT}";
  const S = {statuses};
  const form = document.getElementById("contact-form");
  const status = document.getElementById("form-status");
  const button = form.querySelector(".submit");
  form.addEventListener("submit", async (event) => {{
    event.preventDefault();
    const hasTurnstile = !!form.querySelector(".cf-turnstile");
    const token = form.querySelector('[name="cf-turnstile-response"]')?.value ?? "";
    const message = form.message.value.trim();
    status.classList.remove("err");
    if (!message) {{ status.textContent = S.msg; status.classList.add("err"); return; }}
    if (hasTurnstile && !token) {{ status.textContent = S.turnstile; status.classList.add("err"); return; }}
    button.disabled = true;
    status.textContent = S.sending;
    try {{
      const res = await fetch(ENDPOINT, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          name: form.name.value, email: form.email.value, message,
          token, website: form.website.value,
        }}),
      }});
      const body = await res.json();
      if (!body.ok) throw new Error(body.error);
      form.reset();
      if (window.turnstile) turnstile.reset();
      status.textContent = S.success;
    }} catch {{
      status.textContent = S.error;
      status.classList.add("err");
      if (window.turnstile) turnstile.reset();
    }} finally {{
      button.disabled = false;
    }}
  }});
}})();
</script>"""


def build_support(lang, c):
    d = lang_dir(lang)
    depth = "../" if d else ""
    out = head(c["title"], c["lede"], lang, SUPPORT_BASE, "{dir}", depth)
    out += site_nav_html(c, depth, lang, "support")
    out += hero_html(lang, depth, "Support", c["h1"], c["lede"])
    out += f"""
<main class="container">
<section class="section">
<span class="eyebrow">Guide</span>
<h2>{esc(c['guide_h2'])}</h2>
<p class="sub">{esc(c['guide_sub'])}</p>
<div class="cta">
  <div>
    <h3>{esc(c['guide_card_h'])}</h3>
    <p>{esc(c['guide_card_p'])}</p>
    <div class="chips"><span>Getting Started</span><span>Features</span><span>⌘ Shortcuts</span><span>Export</span><span>CLI</span></div>
    <a class="btn" href="{depth}guide/{d}">{esc(c['guide_btn'])} →</a>
  </div>
</div>
</section>
</section>"""
    out += """
<section class="section">
<span class="eyebrow">FAQ</span>
<h2>{h2}</h2>
<p class="sub">{sub}</p>
""".format(h2=esc(c["faq_h2"]), sub=esc(c["faq_sub"]))
    for i, qa in enumerate(c["faq"], 1):
        out += (
            f"<details><summary><span class=\"qn\">Q{i:02d}</span>{esc(qa['q'])}</summary>"
            f"<div class=\"a\">{esc(qa['a'])}</div></details>\n"
        )
    out += f"""</section>
<section class="section" id="contact">
<span class="eyebrow">Contact</span>
<h2>{esc(c['contact_h2'])}</h2>
<p class="sub">{esc(c['contact_sub'])}</p>
{contact_form_html(lang, c)}
</section>
</main>
"""
    out += footer_html(c, [(c["footer_guide"], f"{SUPPORT_BASE}/guide/{d}"), (c["footer_privacy"], f"{PRIVACY_BASE}/{d}"), (c["footer_contact"], "#contact")])
    return out


def build_guide(lang, c):
    d = lang_dir(lang)
    depth = "../../" if d else "../"
    out = head(c["title"], c["lede"], lang, SUPPORT_BASE, "guide/{dir}", depth)
    out += site_nav_html(c, depth, lang, "guide")
    toc = "".join(f'<a href="#{sid}">{esc(label)}</a>' for sid, label in c["toc"])
    extra = (
        f'<div class="meta-pills"><span>macOS 15.0+</span><span>{esc(c["pill_readonly"])}</span>'
        f'<span>{esc(c["pill_offline"])}</span></div>\n<nav class="toc">{toc}</nav>'
    )
    out += hero_html(lang, depth, "User Guide", c["h1"], c["lede"], extra)
    out += f"""
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
<div class="tip"><b>PRE-COMMIT</b>{esc(c['cli_ci'])}</div>
</section>
</main>
"""
    out += footer_html(c, [(c["footer_support"], f"{SUPPORT_BASE}/{d}"), (c["footer_guide"], f"{SUPPORT_BASE}/guide/{d}"), (c["footer_privacy"], f"{PRIVACY_BASE}/{d}"), (c["footer_contact"], f"{SUPPORT_BASE}/{d}#contact")])
    return out


def build_privacy(lang, c):
    d = lang_dir(lang)
    depth = "../" if d else ""
    out = head(c["title"], c["summary"], lang, PRIVACY_BASE, "{dir}", depth)
    out += hero_html(
        lang, depth, "Privacy", c["h1"], c["lede"],
        f'<div class="meta-pills"><span>{esc(c["updated"])}</span></div>'
    )
    out += f"""
<main class="container">
<section class="section">
<span class="eyebrow">Summary</span>
<h2>{esc(c['summary_h2'])}</h2>
<p class="sub">{esc(c['summary'])}</p>
<div class="audit">
  <div class="ringwrap">
    <div class="ring"><div class="inner"><span class="grade">A</span><span class="score">100 / 100</span></div></div>
    <span class="label">Privacy Self-Audit</span>
  </div>
  <div>"""
    audit_status = ["NONE", "NONE", "READ-ONLY", "NONE"]
    for card, st in zip(c["cards"], audit_status):
        out += f"""
    <div class="crow"><span class="st">{st}</span><div><h3>{esc(card['h'])}</h3><p>{esc(card['p'])}</p></div></div>"""
    out += f"""
  </div>
</div>
</section>
<section class="section">
<span class="eyebrow">Contact</span>
<h2>{esc(c['contact_h2'])}</h2>
<p class="sub">{esc(c['contact_p'])} <a href="{SUPPORT_BASE}/{d}#contact">{esc(c['footer_contact'])}</a></p>
</section>
</main>
"""
    out += footer_html(c, [(c["footer_support"], f"{SUPPORT_BASE}/{d}"), (c["footer_contact"], f"{SUPPORT_BASE}/{d}#contact")])
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
