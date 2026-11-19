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

  function thumb(imageId, gradient, name, light) {
    if (imageId) return el("div", { class: "thumb" }, el("img", { src: "/api/image/" + imageId, alt: "" }));
    const box = el("div", { class: "thumb swatch" + (light ? " on-light" : "") }, el("span", { class: "mono" }, initials(name)));
    box.style.backgroundImage = "url(gradients/g" + String(gradient || 1).padStart(2, "0") + ".svg)";
    return box;
  }
  Locker.thumb = thumb;

  function toolCard(t) {
    const counts = Object.entries(t.items || {}).sort((a, b) => b[1] - a[1]).slice(0, 4)
      .map(([k, n]) => el("span", { class: "pill" }, n + " " + Locker.kindName(k).toLowerCase().replace(n === 1 ? /s$/ : /$^/, "")));
    return el("button", { class: "card", type: "button", on: { click: () => { location.hash = "#/tool/" + t.tool; } } },
      thumb(t.image_id, t.gradient, t.label || t.display, t.gradient_light),
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
      : empty("Locker's empty", data.scan && data.scan.running ? "First scan in progress…" : "Press Refresh to take stock of your AI gear.", "locker");
    Locker.view.replaceChildren(...head("Your AI gear", data.tools.length + " tools on this machine"), body, pinForm());
  }

  function itemCard(it) {
    return el("button", { class: "card", type: "button", on: { click: () => Locker.detail.open("item", it.id) } },
      el("div", { class: "body" },
        el("h3", {}, it.is_favorite ? el("span", { class: "star" }, "★ ") : null, it.label || it.name),
        it.description ? el("div", { class: "desc" }, it.description) : el("div", { class: "meta" }, "No description")));
  }

  function locationCard(loc) {
    const pills = [el("span", { class: "pill" }, loc.category)];
    if (loc.origin === "vendored") pills.push(el("span", { class: "pill sand" }, "third-party"));
    if (loc.presence !== "present") pills.push(el("span", { class: "pill red" }, loc.presence));
    return el("button", { class: "card", type: "button", on: { click: () => Locker.detail.open("location", loc.id) } },
      el("div", { class: "body" },
        el("div", { class: "path" }, loc.path),
        el("div", { class: "counts" }, pills, loc.size_bytes !== null ? el("span", { class: "meta" }, Locker.size(loc.size_bytes, loc.size_over)) : null)));
  }

  async function tool(code) {
    const [data, summary] = await Promise.all([Locker.api("tool/" + encodeURIComponent(code)),
      Locker.summary ? Promise.resolve(Locker.summary) : Locker.api("summary")]);
    Locker.summary = summary;
    const info = summary.tools.find((t) => t.tool === code) || { display: code };
    const sections = data.groups.map((g) => el("section", {},
      el("h2", {}, Locker.kindName(g.kind) + " (" + g.items.length + ")"),
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
    const cols = [["tool", "Tool"], ["kind", "Kind", (v) => Locker.kindName(v)], ["name", "Name"], ["path", "Path"],
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
        : empty("No gear matches", "Check the spelling or clear the search to see the whole locker."));
  }

  Locker.views = { shelves, tool, table, search };
})();
