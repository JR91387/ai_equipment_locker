// SPDX-License-Identifier: MIT
// Detail panel: what a thing is and where it lives, plus the person's note, tags, favourite and picture.
"use strict";

(function () {
  const { el } = Locker;
  const panel = document.getElementById("detail");

  function close() { panel.hidden = true; panel.replaceChildren(); }

  function facts(d, kind) {
    const rows = [];
    const add = (label, value, cls) => { if (value !== null && value !== undefined && value !== "") rows.push(el("dt", {}, label), el("dd", { class: cls }, value)); };
    add("Tool", d.tool);
    add("Kind", kind === "item" ? Locker.kindName(d.kind) : d.category);
    add("What", d.description || d.holds);
    add("Path", d.path, "path");
    add("Size", Locker.size(d.size_bytes, d.size_over));
    add("Status", d.presence && d.presence !== "present" ? d.presence : null);
    add("Origin", d.origin === "vendored" ? "Inside third-party code" : null);
    add("Project", d.project_root, "path");
    return el("dl", {}, rows);
  }

  function readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1]);
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(file);
    });
  }

  function editors(d, target, reopen) {
    const a = d.annotation || {};
    const note = el("textarea", { "aria-label": "Note", placeholder: "Your note (only stored in the catalog)" });
    note.value = a.note || "";
    const label = el("input", { type: "text", placeholder: "Display name (optional)", "aria-label": "Display name" });
    label.value = a.label || "";
    const fav = el("button", { class: "quiet", type: "button" }, a.is_favorite ? "★ Favourite" : "☆ Mark favourite");
    const save = async (fields, message) => {
      try { await Locker.post("annotation", { target, fields }); Locker.toast(message); Locker.summary = null; reopen(); }
      catch (err) { Locker.toast(err.message); }
    };
    fav.addEventListener("click", () => save({ is_favorite: !a.is_favorite }, "Saved"));
    const saveNote = el("button", { class: "primary", type: "button",
      on: { click: () => save({ note: note.value, label: label.value || null }, "Note saved") } }, "Save");
    const tagInput = el("input", { type: "text", placeholder: "Add a tag", "aria-label": "Add a tag" });
    const tagRow = el("div", { class: "row tags" }, (d.tags || []).map((t) =>
      el("button", { class: "pill sky", type: "button", title: "Remove tag",
        on: { click: async () => { await Locker.post("tag", { target, name: t, on: false }); reopen(); } } }, t + " ×")), tagInput);
    tagInput.addEventListener("keydown", async (ev) => {
      if (ev.key !== "Enter" || !tagInput.value.trim()) return;
      try { await Locker.post("tag", { target, name: tagInput.value.trim() }); reopen(); } catch (err) { Locker.toast(err.message); }
    });
    const file = el("input", { type: "file", accept: "image/png,image/jpeg,image/webp,image/gif", "aria-label": "Picture" });
    file.addEventListener("change", async () => {
      if (!file.files[0]) return;
      if (file.files[0].size > 2 * 1024 * 1024) { Locker.toast("Pictures up to 2 MB"); return; }
      try { await Locker.post("image", { target, data: await readFile(file.files[0]) }); Locker.summary = null; reopen(); }
      catch (err) { Locker.toast(err.message); }
    });
    return [el("div", { class: "row" }, fav), label, note, el("div", { class: "row" }, saveNote), el("h3", {}, "Tags"), tagRow,
      el("h3", {}, "Picture"), d.image_id ? el("img", { src: "/api/image/" + d.image_id, alt: "" }) : null, el("div", { class: "row" }, file)];
  }

  function history(d) {
    if (!d.history || !d.history.length) return null;
    return [el("h3", {}, "Recent changes"), el("ul", { class: "meta" },
      d.history.map((h) => el("li", {}, h.change + " · " + new Date(h.at).toLocaleString())))];
  }

  async function open(kind, id) {
    let d;
    try { d = await Locker.api("detail/" + kind + "/" + encodeURIComponent(id)); }
    catch (err) { Locker.toast(err.message); return; }
    const target = { kind, id: kind === "tool" ? id : Number(id) };
    const title = (d.annotation && d.annotation.label) || d.name || d.display || (d.path || "").split(/[\\/]/).pop();
    const parts = [el("button", { class: "quiet close", type: "button", on: { click: close } }, "Close"),
      kind === "tool" && !d.image_id ? Locker.thumb(null, d.gradient, d.display, d.gradient_light) : null,
      el("h2", {}, title), facts(d, kind), ...editors(d, target, () => open(kind, id)), ...(history(d) || [])];
    panel.replaceChildren(...parts.filter(Boolean));
    panel.hidden = false;
    panel.focus();
  }

  document.addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !panel.hidden) close(); });
  Locker.detail = { open, close };
})();
