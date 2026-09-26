// Filters and sorts the cards build_site.py rendered. The page works without this;
// it only adds search, tabs, category and language filters, sort, and shareable URLs.
(() => {
  const grid = document.getElementById("grid");
  const cards = Array.from(grid.querySelectorAll(".card"));
  const q = document.getElementById("q");
  const tagSelect = document.getElementById("tag");
  const sortSelect = document.getElementById("sort");
  const cats = document.getElementById("cats");
  const shown = document.getElementById("shown");
  const empty = document.getElementById("empty");
  const tabs = Array.from(document.querySelectorAll(".tab"));
  const catButtons = Array.from(cats.querySelectorAll(".cat"));
  const TAGGED = new Set(["servers", "frameworks"]);

  const params = new URLSearchParams(location.search);
  const state = {
    tab: params.get("tab") || "servers",
    cat: params.get("cat") || "",
    tag: params.get("lang") || "",
    sort: params.get("sort") || "stars",
    q: params.get("q") || "",
  };
  if (!tabs.some((t) => t.dataset.tab === state.tab)) state.tab = "servers";

  // "updated 3d ago" from the ISO date each card carries
  const now = Date.now();
  const ago = (iso) => {
    const days = Math.max(0, Math.round((now - Date.parse(iso)) / 864e5));
    if (days < 1) return "updated today";
    if (days < 30) return `updated ${days}d ago`;
    if (days < 365) return `updated ${Math.round(days / 30)}mo ago`;
    return `updated ${Math.round(days / 365)}y ago`;
  };
  for (const t of grid.querySelectorAll("time")) t.textContent = ago(t.dateTime);

  const compare = {
    stars: (a, b) => b.dataset.stars - a.dataset.stars || a.dataset.name.localeCompare(b.dataset.name),
    pushed: (a, b) => (b.dataset.pushed || "").localeCompare(a.dataset.pushed || "") || a.dataset.name.localeCompare(b.dataset.name),
    name: (a, b) => a.dataset.name.localeCompare(b.dataset.name),
  };

  function syncUrl() {
    const p = new URLSearchParams();
    if (state.tab !== "servers") p.set("tab", state.tab);
    if (state.cat) p.set("cat", state.cat);
    if (state.tag) p.set("lang", state.tag);
    if (state.sort !== "stars") p.set("sort", state.sort);
    if (state.q) p.set("q", state.q);
    const query = p.toString();
    history.replaceState(null, "", query ? `?${query}` : location.pathname);
  }

  function render() {
    const words = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    const searching = words.length > 0;
    // a search looks across every tab; otherwise the tab, category and language apply
    const visible = cards.filter((c) => {
      if (searching) return words.every((w) => c.dataset.search.includes(w));
      if (c.dataset.tab !== state.tab) return false;
      if (state.tab === "servers" && state.cat && c.dataset.cat !== state.cat) return false;
      if (TAGGED.has(state.tab) && state.tag && c.dataset.tag !== state.tag) return false;
      return true;
    });
    visible.sort(compare[state.sort] || compare.stars);

    const keep = new Set(visible);
    for (const c of cards) c.hidden = !keep.has(c);
    visible.forEach((c, i) => {
      c.style.setProperty("--i", i);
      grid.appendChild(c);
      // restart the entrance animation so a new filter reads as a new result
      c.style.animation = "none";
      void c.offsetWidth;
      c.style.animation = "";
    });

    for (const t of tabs) t.setAttribute("aria-selected", String(!searching && t.dataset.tab === state.tab));
    for (const b of catButtons) b.setAttribute("aria-pressed", String(b.dataset.cat === state.cat));
    cats.hidden = searching || state.tab !== "servers";
    tagSelect.closest(".select").hidden = searching || !TAGGED.has(state.tab);

    const noun = visible.length === 1 ? "entry" : "entries";
    shown.textContent = searching
      ? `${visible.length} ${noun} match "${state.q}"`
      : `${visible.length} ${noun}`;
    empty.hidden = visible.length > 0;
    syncUrl();
  }

  for (const t of tabs) {
    t.addEventListener("click", () => {
      state.tab = t.dataset.tab;
      state.cat = "";
      state.q = "";
      q.value = "";
      render();
    });
  }
  for (const b of catButtons) {
    b.addEventListener("click", () => {
      state.cat = b.dataset.cat;
      render();
    });
  }
  q.value = state.q;
  q.addEventListener("input", () => {
    state.q = q.value.trim();
    render();
  });
  tagSelect.value = state.tag;
  tagSelect.addEventListener("change", () => {
    state.tag = tagSelect.value;
    render();
  });
  sortSelect.value = state.sort;
  sortSelect.addEventListener("change", () => {
    state.sort = sortSelect.value;
    render();
  });

  // "/" or Cmd/Ctrl+K jumps to search, Escape clears it
  document.addEventListener("keydown", (e) => {
    const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
    if ((e.key === "/" && !typing) || (e.key.toLowerCase() === "k" && (e.metaKey || e.ctrlKey))) {
      e.preventDefault();
      q.focus();
      q.select();
    } else if (e.key === "Escape" && document.activeElement === q) {
      q.value = "";
      state.q = "";
      render();
      q.blur();
    }
  });

  render();
})();
