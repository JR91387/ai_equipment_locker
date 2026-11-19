// SPDX-License-Identifier: MIT
// Equipment Locker page: state, API helpers, routing. Views live in views.js, the detail panel in detail.js.
"use strict";

const Locker = {
  view: document.getElementById("view"),
  query: document.getElementById("q"),
  scanEl: document.getElementById("scan"),
  summary: null,
};

Locker.el = function (tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "on") Object.entries(value).forEach(([ev, fn]) => node.addEventListener(ev, fn));
    else if (key === "class") node.className = value;
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
};

Locker.svg = function (markup) {
  const wrap = document.createElement("span");
  wrap.innerHTML = markup; // static, trusted markup from this file only
  return wrap.firstChild;
};

Locker.icons = {
  locker: '<svg viewBox="0 0 64 52" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M12 20 15 4h34l3 16"/><path d="M6 24h52v24H6z"/><path d="M6 24l6-4h40l6 4"/><path d="M29 24v6h6v-6"/><path d="m32 33 1.6 3.3 3.6.5-2.6 2.5.6 3.6-3.2-1.7-3.2 1.7.6-3.6-2.6-2.5 3.6-.5z"/><path d="M20 12h12M20 15h18"/></svg>',
  crate: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="14" rx="1.5"/><path d="M3 10h18M8 6V4.5A1.5 1.5 0 0 1 9.5 3h5A1.5 1.5 0 0 1 16 4.5V6"/></svg>',
  folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
};

Locker.api = async function (path) {
  const res = await fetch("/api/" + path, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || res.statusText);
  return res.json();
};

Locker.post = async function (action, body) {
  const res = await fetch("/api/" + action, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Locker": "1" },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
};

Locker.toast = function (message) {
  const t = document.getElementById("toast");
  t.textContent = message;
  t.hidden = false;
  clearTimeout(Locker.toastTimer);
  Locker.toastTimer = setTimeout(() => { t.hidden = true; }, 2600);
};

Locker.size = function (bytes, over) {
  if (bytes === null || bytes === undefined) return "";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let n = Number(bytes), i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i += 1; }
  return (over ? "≥ " : "") + (i ? n.toFixed(1) : n) + " " + units[i];
};

Locker.kindName = function (kind) {
  const names = { skill: "Skills", agent: "Agents", command: "Commands", mcp_server: "MCP servers",
    plugin: "Plugins", extension: "Extensions", rule: "Rules", workflow: "Workflows", model: "Models",
    output_style: "Output styles", prompt: "Prompts", hook: "Hooks" };
  return names[kind] || kind;
};

Locker.showScan = function (state, last) {
  if (state && state.running) { Locker.scanEl.textContent = "Scanning…"; return; }
  if (state && state.error) { Locker.scanEl.textContent = "Last scan failed"; return; }
  const when = last && (last.finished || last.started);
  Locker.scanEl.textContent = when ? "Scanned " + new Date(when).toLocaleString() : "Not scanned yet";
};

Locker.route = async function () {
  const hash = location.hash.replace(/^#\/?/, "");
  const [name, arg] = hash.split("/");
  document.querySelectorAll(".views a").forEach((a) =>
    a.classList.toggle("on", a.dataset.view === (name === "table" ? "table" : "shelves")));
  try {
    if (name === "tool" && arg) await Locker.views.tool(decodeURIComponent(arg));
    else if (name === "table") await Locker.views.table();
    else if (name === "search") await Locker.views.search(decodeURIComponent(arg || ""));
    else await Locker.views.shelves();
  } catch (err) {
    Locker.view.replaceChildren(Locker.el("div", { class: "empty" }, Locker.el("h2", {}, "Could not load"), err.message));
  }
};

Locker.watchScan = async function () {
  try {
    const state = await Locker.api("scan");
    const wasRunning = Locker.scanRunning;
    Locker.scanRunning = state.running;
    Locker.showScan(state, Locker.summary && Locker.summary.last_scan);
    if (wasRunning && !state.running) { Locker.toast("Scan finished"); Locker.route(); }
  } catch (err) { /* page stays usable without status */ }
  setTimeout(Locker.watchScan, Locker.scanRunning ? 2000 : 15000);
};

document.getElementById("refresh").addEventListener("click", async () => {
  const res = await Locker.post("scan");
  Locker.toast(res.started ? "Scan started" : "A scan is already running");
  Locker.scanRunning = true;
  Locker.showScan({ running: true });
});

let searchTimer;
Locker.query.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    const q = Locker.query.value.trim();
    location.hash = q ? "#/search/" + encodeURIComponent(q) : "#/";
  }, 220);
});

window.addEventListener("hashchange", Locker.route);
window.addEventListener("DOMContentLoaded", () => { Locker.route(); Locker.watchScan(); });
