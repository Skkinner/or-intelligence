#!/usr/bin/env node
// Owner: Member D. Pushes the current issue bodies + labels from .github/issues/manifest.json to the
// existing GitHub issues (uses .github/issues/issue_numbers.json). Never creates or closes issues.
//
// Usage: node scripts/github/sync_issues.mjs [--repo owner/name] [--only 2.2.1,3.1.1] [--dry-run]
// Run `node scripts/github/generate.mjs` first after editing docs/planning/wbs_data.json.
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const args = process.argv.slice(2);
const opt = (f) => (args.includes(f) ? args[args.indexOf(f) + 1] : null);
const DRY = args.includes("--dry-run");
const manifest = JSON.parse(readFileSync(join(ROOT, ".github/issues/manifest.json"), "utf8"));
const numbers = JSON.parse(readFileSync(join(ROOT, ".github/issues/issue_numbers.json"), "utf8"));
const only = opt("--only")?.split(",");
const repo = opt("--repo")
  ?? execFileSync("gh", ["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], { cwd: ROOT, encoding: "utf8" }).trim();
const tmp = mkdtempSync(join(tmpdir(), "ori-sync-"));
const fill = (body) => body.replace(/\{\{#([\d.]+)\}\}/g, (_, id) => (numbers[id] ? `#${numbers[id]}` : `WBS ${id}`));

let n = 0;
for (const is of manifest.issues) {
  if (only && !only.includes(is.wbs)) continue;
  const num = numbers[is.wbs];
  if (!num) { console.log(`skip ${is.wbs}: no issue number`); continue; }
  const file = join(tmp, `${is.wbs}.md`);
  writeFileSync(file, fill(is.body));
  const a = ["issue", "edit", String(num), "--repo", repo, "--title", is.title, "--body-file", file];
  for (const l of is.labels) a.push("--add-label", l);
  if (DRY) console.log("[dry-run] gh", a.join(" "));
  else { execFileSync("gh", a, { cwd: ROOT, stdio: ["ignore", "ignore", "inherit"] }); console.log(`updated #${num} ${is.title}`); }
  n++;
}
console.log(`${n} issue(s) ${DRY ? "would be " : ""}updated in ${repo}`);
