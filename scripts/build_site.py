#!/usr/bin/env python3
"""Build the searchable website for this list from README.md, into _site/.

README.md stays the single source of truth: this reads it with the same parser the
validator uses, adds live stars and last-push dates from the GitHub API when a token
is available, and renders one static page (cards rendered in HTML, so it works
without JavaScript; site/app.js only filters and sorts them).

    python scripts/build_site.py                  # no token: no stars, still builds
    GITHUB_TOKEN=$(gh auth token) python scripts/build_site.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import validate

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "site"
OUT = ROOT / "_site"
REPO = "Sagargupta16/awesome-mcp-servers"
REPO_URL = f"https://github.com/{REPO}"
SUBMIT_URL = f"{REPO_URL}/issues/new?template=add-server.yml"

# The page's tabs: (key, label, README sections in it). Servers are split by category.
TABS = [
    ("servers", "Servers", validate.SERVER_CATEGORIES),
    ("frameworks", "Frameworks", ["Frameworks & Libraries"]),
    ("clients", "Clients", ["Clients"]),
    ("official", "Official", ["Official"]),
    ("learn", "Learn", ["Tutorials & Articles", "Videos"]),
    ("community", "Community", ["Community"]),
]
# owner/repo, also for links into a monorepo folder (".../tree/main/src/fetch"),
# which then show the stars of the repository that holds them
GITHUB_RE = re.compile(
    r"^https?://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/#?].*)?$"
)
BATCH = 50  # repositories per GraphQL request


@dataclass
class Item:
    name: str
    url: str
    desc: str
    tag: str  # language for servers and frameworks, support tier for clients
    tab: str
    category: str
    slug: str = ""  # owner/repo for GitHub links
    stars: int | None = None
    pushed: str = ""  # ISO date of the last push


def github_slug(url: str) -> str:
    """Return owner/repo for a repository URL, or "" for anything else."""
    m = GITHUB_RE.match(url)
    return f"{m.group(1)}/{m.group(2)}" if m else ""


def load_items(lines: list[str]) -> list[Item]:
    """Return every entry in README.md, tagged with the tab and category it belongs to."""
    entries, _, _ = validate.parse(lines)
    items = []
    for tab, _, sections in TABS:
        for section in sections:
            for e in entries.get(section, []):
                items.append(
                    Item(
                        e.name, e.url, e.desc, e.third, tab, section, github_slug(e.url)
                    )
                )
    return items


def _graphql(query: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": REPO},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp).get("data") or {}


def add_github_stats(items: list[Item], token: str) -> int:
    """Fill stars and last push for GitHub entries; return how many were found."""
    slugs = sorted({i.slug for i in items if i.slug})
    stats: dict[str, tuple[int, str]] = {}
    for start in range(0, len(slugs), BATCH):
        batch = slugs[start : start + BATCH]
        fields = " ".join(
            f"r{n}: repository(owner: {json.dumps(s.split('/')[0])}, name: {json.dumps(s.split('/')[1])})"
            " { nameWithOwner stargazerCount pushedAt }"
            for n, s in enumerate(batch)
        )
        try:
            data = _graphql(f"query {{ {fields} }}", token)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"GitHub stats batch failed, building without them: {exc}")
            continue
        for n, slug in enumerate(batch):
            repo = data.get(f"r{n}")
            if repo:
                stats[slug.lower()] = (repo["stargazerCount"], repo["pushedAt"][:10])
    for i in items:
        if i.slug.lower() in stats:
            i.stars, i.pushed = stats[i.slug.lower()]
    return len(stats)


def _stars(n: int | None) -> str:
    if n is None:
        return ""
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def render_card(i: Item) -> str:
    meta = []
    if i.tag:
        meta.append(f'<span class="chip">{escape(i.tag)}</span>')
    if i.stars is not None:
        meta.append(
            f'<span class="stat" title="{i.stars:,} stars"><svg viewBox="0 0 16 16" aria-hidden="true">'
            '<path d="M8 1.5l1.9 4 4.4.5-3.3 3 .9 4.3L8 11.2 4.1 13.3 5 9 1.7 6l4.4-.5z"/></svg>'
            f"{_stars(i.stars)}</span>"
        )
    if i.pushed:
        meta.append(f'<time class="stat" datetime="{i.pushed}">{i.pushed}</time>')
    source = i.slug or re.sub(r"^https?://(www\.)?", "", i.url).split("/")[0]
    search = " ".join([i.name, i.desc, i.tag, i.category, i.slug]).lower()
    return (
        f'<a class="card" href="{escape(i.url, quote=True)}" target="_blank" rel="noopener"'
        f' data-tab="{i.tab}" data-cat="{escape(i.category, quote=True)}"'
        f' data-tag="{escape(i.tag, quote=True)}" data-stars="{i.stars or 0}"'
        f' data-pushed="{i.pushed}" data-name="{escape(i.name.lower(), quote=True)}"'
        f' data-search="{escape(search, quote=True)}">'
        f'<span class="card-top"><span class="name">{escape(i.name)}</span>'
        '<svg class="arrow" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11L11 5M6 5h5v5"/></svg></span>'
        f'<span class="source">{escape(source)}</span>'
        f'<span class="desc">{escape(i.desc)}</span>'
        f'<span class="meta">{"".join(meta)}</span></a>'
    )


def render_page(items: list[Item], template: str, built: datetime) -> str:
    counts = {tab: sum(1 for i in items if i.tab == tab) for tab, _, _ in TABS}
    tabs = "".join(
        f'<button class="tab" role="tab" data-tab="{key}" aria-selected="{str(key == "servers").lower()}">'
        f'{label}<span class="count">{counts[key]}</span></button>'
        for key, label, _ in TABS
        if counts[key]
    )
    categories = "".join(
        f'<button class="cat" data-cat="{escape(c, quote=True)}">{escape(c)}'
        f'<span class="count">{sum(1 for i in items if i.category == c)}</span></button>'
        for c in validate.SERVER_CATEGORIES
        if any(i.category == c for i in items)
    )
    tags = sorted(
        {i.tag for i in items if i.tab in ("servers", "frameworks") and i.tag}
    )
    tag_options = "".join(
        f'<option value="{escape(t, quote=True)}">{escape(t)}</option>' for t in tags
    )
    servers = [i for i in items if i.tab == "servers"]
    values = {
        "{{SERVER_COUNT}}": str(len(servers)),
        "{{CATEGORY_COUNT}}": str(len({i.category for i in servers})),
        "{{CLIENT_COUNT}}": str(counts["clients"]),
        "{{TOTAL_COUNT}}": str(len(items)),
        "{{UPDATED}}": built.strftime("%Y-%m-%d"),
        "{{UPDATED_ISO}}": built.strftime("%Y-%m-%dT%H:%MZ"),
        "{{TABS}}": tabs,
        "{{CATEGORIES}}": categories,
        "{{TAG_OPTIONS}}": tag_options,
        "{{CARDS}}": "\n".join(render_card(i) for i in items),
        "{{REPO_URL}}": REPO_URL,
        "{{SUBMIT_URL}}": escape(SUBMIT_URL, quote=True),
    }
    page = template
    for key, value in values.items():
        page = page.replace(key, value)
    return page


def build(token: str | None) -> Path:
    items = load_items(
        (ROOT / "README.md").read_text(encoding="utf-8").splitlines(True)
    )
    found = add_github_stats(items, token) if token else 0
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    template = (SITE_SRC / "index.html").read_text(encoding="utf-8")
    built = datetime.now(timezone.utc)
    (OUT / "index.html").write_text(
        render_page(items, template, built), encoding="utf-8"
    )
    for name in ("styles.css", "app.js", "favicon.svg"):
        shutil.copy2(SITE_SRC / name, OUT / name)
    (OUT / "servers.json").write_text(
        json.dumps([asdict(i) for i in items], indent=1) + "\n", encoding="utf-8"
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built {len(items)} entries into {OUT} ({found} with GitHub stats)")
    return OUT


if __name__ == "__main__":
    build(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    sys.exit(0)
