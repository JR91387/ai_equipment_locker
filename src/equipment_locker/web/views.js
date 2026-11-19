// SPDX-License-Identifier: MIT
// Views: tool shelves, one tool, flat table, search results. All text goes in via textContent (no HTML injection).
"use strict";

(function () {
  const { el } = Locker;
  const head = (title, sub) => [el("h1", {}, title), sub ? el("p", { class: "sub" }, sub) : null];
  const empty = (title, text, icon) => el("div", { class: "empty" },
    icon ? el("div", { class: "empty-art" }, Locker.svg(Locker.icons[icon])) : null, el("h2", {}, title), el("p", {}, text));

  function initials(name) {
    const words = String(name || "?").replace(/[^A-Za-z0-9 ]+/g, " ").trim().split(/\s+/);
    return (words.length > 1 ? words[0][0] + words[1][0] : words[0].slice(0, 2)).toUpperCase();
  }

  // A person's own picture wins, then the tool's bundled icon, then its palette gradient with initials.
  function thumb(t) {
    if (t.image_id) return el("div", { class: "thumb" }, el("img", { src: "/api/image/" + t.image_id, alt: "" }));
    if (t.icon) return el("div", { class: "thumb icon-tile" + (t.icon_dark ? " dark" : "") }, el("img", { src: t.icon, alt: "" }));
    const box = el("div", { class: "thumb swatch" + (t.gradient_light ? " on-light" : "") },
      el("span", { class: "mono" }, initials(t.label || t.display)));
    box.style.backgroundImage = "url(gradients/g" + String(t.gradient || 1).padStart(2, "0") + ".svg)";
    return box;
  }
  Locker.thumb = thumb;

  const KINDS = new Set(["skill", "agent", "command", "mcp_server", "plugin", "extension", "rule", "model", "workflow",
    "output_style", "prompt", "hook"]);
  const TILES = ["#3B4F2F", "#4E86A6", "#B4422C", "#8C7448", "#2B3026", "#6E7F4F", "#2F6680", "#9A5A3C"];
  const hash = (s) => [...String(s)].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);

  // Small square with the kind's icon; its colour comes from the item's name, so neighbours differ but never shuffle.
  function kindTile(kind, seed, small) {
    const icon = KINDS.has(kind) ? kind : "folder";
    const box = el("span", { class: "ktile" + (small ? " small" : "") }, el("img", { src: "icons/kinds/" + icon + ".svg", alt: "" }));
    box.style.backgroundColor = icon === "folder" ? "#8C7448" : TILES[hash(seed) % TILES.length];
    return box;
  }
  Locker.kindTile = kindTile;

  function toolCard(t) {
    const counts = Object.entries(t.items || {}).sort((a, b) => b[1] - a[1]).slice(0, 4)
      .map(([k, n]) => el("span", { class: "pill" }, n + " " + Locker.kindName(k).toLowerCase().replace(n === 1 ? /s$/ : /$^/, "")));
    return el("button", { class: "card", type: "button", on: { click: () => { location.hash = "#/tool/" + t.tool; } } },
      thumb(t),
      el("div", { class: "body" },
        el("h3", {}, t.is_favorite ? el("span", { class: "star", "aria-label": "favourite" }, "★ ") : null,
          t.label || t.display),
        el("div", { class: "counts" }, counts.length ? counts : el("span", { class: "pill sand" }, "folders only")),
        el("div", { class: "meta" }, t.present + " places · " + (Locker.size(t.bytes) || "size pending"))));
  }

  function pinForm() {
    const input = el("input", { type: "text", placeholder: "Pin a folder: /path/to/folder", "aria-label": "Folder to pin" });
    const add = async () => {
      if (!input.value.trim()) return;
      try { await Locker.post("pin", { path: input.value.trim() }); input.value = ""; Locker.toast("Pinned. It shows after the next scan."); }
      catch (err) { Locker.toast(err.message); }
    };
    return el("div", { class: "foot" }, input, el("button", { class: "quiet", type: "button", on: { click: add } }, "Pin"),
      el("span", {}, "Read-only: Equipment Locker never changes your tool files."));
  }

  async function shelves() {
    const data = await Locker.api("summary");
    Locker.summary = data;
    Locker.showScan(data.scan, data.last_scan);
    const body = data.tools.length
      ? el("div", { class: "grid" }, data.tools.map(toolCard))
      : empty("Locker's empty", data.scan && data.scan.running ? "First scan in progress…" : "Press Refresh to take stock of your AI tools.", "locker");
    Locker.view.replaceChildren(...head("Your tools", data.tools.length + " tools on this computer"), body, pinForm());
  }

  function itemCard(it) {
    return el("button", { class: "card row", type: "button", on: { click: () => Locker.detail.open("item", it.id) } },
      kindTile(it.kind, it.name), el("div", { class: "body" },
        el("h3", {}, it.is_favorite ? el("span", { class: "star" }, "★ ") : null, it.label || it.name),
        it.description ? el("div", { class: "desc" }, it.description) : el("div", { class: "meta" }, "No description")));
  }

  function locationCard(loc) {
    const pills = [el("span", { class: "pill" }, loc.category)];
    if (loc.origin === "vendored") pills.push(el("span", { class: "pill sand" }, "third-party"));
    if (loc.presence !== "present") pills.push(el("span", { class: "pill red" }, loc.presence));
    return el("button", { class: "card row", type: "button", on: { click: () => Locker.detail.open("location", loc.id) } },
      kindTile("folder", loc.path), el("div", { class: "body" },
        el("div", { class: "path" }, loc.path),
        el("div", { class: "counts" }, pills, loc.size_bytes !== null ? el("span", { class: "meta" }, Locker.size(loc.size_bytes, loc.size_over)) : null)));
  }

  async function tool(code) {
    const [data, summary] = await Promise.all([Locker.api("tool/" + encodeURIComponent(code)),
      Locker.summary ? Promise.resolve(Locker.summary) : Locker.api("summary")]);
    Locker.summary = summary;
    const info = summary.tools.find((t) => t.tool === code) || { display: code };
    const sections = data.groups.map((g) => el("section", {},
      el("h2", { class: "kind-head" }, kindTile(g.kind, g.kind, true), Locker.kindName(g.kind) + " (" + g.items.length + ")"),
      el("div", { class: "grid compact" }, g.items.map(itemCard))));
    const own = data.locations.filter((l) => l.origin !== "vendored");
    const vendored = data.locations.filter((l) => l.origin === "vendored");
    sections.push(el("section", {}, el("h2", {}, "Folders and files (" + own.length + ")"),
      el("div", { class: "grid compact" }, own.map(locationCard))));
    if (vendored.length) sections.push(el("section", {}, el("h2", {}, "In third-party code (" + vendored.length + ")"),
      el("div", { class: "grid compact" }, vendored.map(locationCard))));
    const about = el("button", { class: "quiet", type: "button", on: { click: () => Locker.detail.open("tool", code) } }, "Note, tags, picture");
    Locker.view.replaceChildren(el("a", { class: "crumb", href: "#/" }, "← All tools"),
      ...head(info.label || info.display, (info.present || 0) + " places · " + (Locker.size(info.bytes) || "")), about, ...sections);
  }

  function sortable(rows, columns) {
    let key = columns[0][0], dir = 1;
    const tbody = el("tbody");
    const draw = () => {
      rows.sort((a, b) => (a[key] ?? "") > (b[key] ?? "") ? dir : (a[key] ?? "") < (b[key] ?? "") ? -dir : 0);
      tbody.replaceChildren(...rows.map((r) => el("tr", { on: { click: () => Locker.detail.open(r.type, r.id) } },
        columns.map(([k, , fmt]) => el("td", { class: k === "path" ? "path" : null }, fmt ? fmt(r[k], r) : r[k] ?? "")))));
    };
    const ths = columns.map(([k, label]) => el("th", { scope: "col", on: { click: () => { dir = key === k ? -dir : 1; key = k; draw(); } } }, label));
    draw();
    return el("div", { class: "wrap" }, el("table", {}, el("thead", {}, el("tr", {}, ths)), tbody));
  }

  async function table() {
    const { rows } = await Locker.api("table");
    const kindCell = (v, r) => el("span", { class: "kcell" }, kindTile(r.type === "item" ? v : "folder", r.name, true), Locker.kindName(v));
    const cols = [["tool", "Tool"], ["kind", "Kind", kindCell], ["name", "Name"], ["path", "Path"],
      ["size_bytes", "Size", (v) => Locker.size(v)]];
    Locker.view.replaceChildren(...head("Everything", rows.length + " rows · click a column to sort"),
      rows.length ? sortable(rows, cols) : empty("Nothing yet", "Run a scan to fill the locker."));
  }

  async function search(q) {
    if (Locker.query.value.trim() !== q) Locker.query.value = q;
    const { results } = await Locker.api("search?q=" + encodeURIComponent(q));
    const rows = results.filter((r) => r.kind !== "project").map((r) => ({ ...r, type: r.kind, id: r.kind === "tool" ? r.tool : r.ref_id }));
    const cols = [["title", "Name"], ["kind", "Kind"], ["tool", "Tool"], ["path", "Path"]];
    Locker.view.replaceChildren(...head("Search: " + q, results.length + " matches"),
      rows.length ? sortable(rows, cols)
        : empty("Nothing matches", "Check the spelling or clear the search to see every tool."));
  }

  Locker.views = { shelves, tool, table, search };
})();
