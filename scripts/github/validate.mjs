#!/usr/bin/env node
// Owner: Member D. Validates the repository setup against the WBS:
//   1. every task has exactly one valid owner and one issue in the manifest
//   2. every tracked file has exactly one owner (CODEOWNERS-style rules, last match wins)
//   3. no two tasks of different members own the same path
//   4. every requirement maps to existing tasks; every dependency exists
//   5. owned paths that do not exist yet are listed (they are deliverables still to be created)
// Usage: node scripts/github/validate.mjs     (exit 1 on any hard error)
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const D = JSON.parse(readFileSync(join(ROOT, "docs/planning/wbs_data.json"), "utf8"));
const M = JSON.parse(readFileSync(join(ROOT, ".github/issues/manifest.json"), "utf8"));
const errors = [];
const warn = [];
const ids = new Set(D.tasks.map((t) => t.id));
const memberIds = new Set(D.members.map((m) => m.id));

// 1. owners + issues
for (const t of D.tasks) {
  if (!memberIds.has(t.owner)) errors.push(`task ${t.id} has invalid owner ${t.owner}`);
  const n = M.issues.filter((i) => i.wbs === t.id).length;
  if (n !== 1) errors.push(`task ${t.id} has ${n} issues in manifest`);
  for (const dep of t.deps) if (!ids.has(dep)) errors.push(`task ${t.id} depends on unknown ${dep}`);
  for (const k of ["steps", "outputs", "files", "accept"]) if (!t[k]?.length) errors.push(`task ${t.id} has no ${k}`);
}
if (new Set(M.issues.map((i) => i.title)).size !== M.issues.length) errors.push("duplicate issue titles in manifest");

// 3. path conflicts between members
const pathOwner = new Map();
for (const t of D.tasks) for (const f of t.files) {
  if (pathOwner.has(f) && pathOwner.get(f) !== t.owner) errors.push(`path ${f} owned by ${pathOwner.get(f)} and ${t.owner}`);
  pathOwner.set(f, t.owner);
}
for (const [p, o] of D.extraOwnership) if (!pathOwner.has(p)) pathOwner.set(p, o);

// 2. every tracked/new file has an owner
const rules = [...pathOwner.entries()].map(([p, o]) => [p.startsWith("/") ? p.slice(1) : p, o]);
const depth = (p) => p.replace(/\/$/, "").split("/").length + (p.endsWith("/") ? 0 : 0.5);
rules.sort((a, b) => depth(a[0]) - depth(b[0]) || a[0].localeCompare(b[0]));
const match = (rule, file) => {
  if (rule === "*.md") return !file.includes("/") && file.endsWith(".md");
  if (rule.endsWith("/")) return file.startsWith(rule);
  return file === rule;
};
const files = execFileSync("git", ["ls-files", "--cached", "--others", "--exclude-standard"], { cwd: ROOT, encoding: "utf8" })
  .split("\n").filter(Boolean);
const unowned = [];
const perMember = {};
for (const f of files) {
  let owner = null;
  for (const [r, o] of rules) if (match(r, f)) owner = o;
  if (!owner) unowned.push(f);
  else perMember[owner] = (perMember[owner] ?? 0) + 1;
}
if (unowned.length) errors.push(`files without an owner:\n  ${unowned.join("\n  ")}`);

// 4. requirements
for (const r of D.requirements) {
  if (!r.tasks.length) errors.push(`requirement ${r.id} has no task`);
  for (const t of r.tasks) if (!ids.has(t)) errors.push(`requirement ${r.id} references unknown task ${t}`);
}
for (const dl of D.deliverables) for (const t of dl.tasks) if (!ids.has(t)) errors.push(`deliverable ${dl.id} references unknown task ${t}`);

// 5. owned paths not yet present = deliverables to be produced
for (const [p, o] of pathOwner) if (!p.includes("*") && !existsSync(join(ROOT, p))) warn.push(`${p} (Member ${o}) — to be created by the owner`);

console.log(`tasks: ${D.tasks.length} · issues: ${M.issues.length} · requirements: ${D.requirements.length} · files checked: ${files.length}`);
console.log("files per owner:", perMember);
if (warn.length) console.log(`\nOwned paths not created yet (${warn.length}):\n  ${warn.join("\n  ")}`);
if (errors.length) { console.error(`\nERRORS (${errors.length}):\n- ${errors.join("\n- ")}`); process.exit(1); }
console.log("\nOK: every task has one owner and one issue, every file has one owner, all requirements mapped.");
