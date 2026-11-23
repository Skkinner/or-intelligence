#!/usr/bin/env node
// Owner: Member D. One-time GitHub setup using the GitHub CLI (`gh`). Safe to re-run:
//   - never overwrites an existing repository (needs --use-existing to touch one),
//   - never creates an issue whose title already exists,
//   - only invites collaborators with --invite.
//
// Prerequisites:  gh installed, `gh auth login` done, run from the repository root with the initial commit made.
//
// Usage:
//   node scripts/github/setup_github.mjs [--owner <user-or-org>] [--name or-intelligence] [--public]
//                                        [--use-existing] [--invite] [--dry-run]
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const args = process.argv.slice(2);
const flag = (f) => args.includes(f);
const opt = (f, d) => (args.includes(f) ? args[args.indexOf(f) + 1] : d);
const DRY = flag("--dry-run");
const TMP = mkdtempSync(join(tmpdir(), "ori-gh-"));

function gh(a, { input, allowFail = false } = {}) {
  if (DRY) {
    const readOnly = (a[0] === "api" && !a.includes("-X")) || a[0] === "auth" || (a[0] === "repo" && a[1] === "view")
      || (a[0] === "issue" && a[1] === "list");
    if (!readOnly) { console.log("[dry-run] gh", a.join(" ")); return ""; }
  }
  try {
    return execFileSync("gh", a, { cwd: ROOT, encoding: "utf8", input, stdio: ["pipe", "pipe", "pipe"] }).trim();
  } catch (e) {
    if (allowFail) return null;
    throw new Error(`gh ${a.join(" ")} failed:\n${e.stderr || e.message}`);
  }
}
const git = (a) => (DRY ? (console.log("[dry-run] git", a.join(" ")), "") : execFileSync("git", a, { cwd: ROOT, encoding: "utf8" }).trim());
const json = (s) => JSON.parse(s || "null");
const tmpFile = (name, content) => { const p = join(TMP, name); writeFileSync(p, content); return p; };

const manifest = JSON.parse(readFileSync(join(ROOT, ".github/issues/manifest.json"), "utf8"));
const team = JSON.parse(readFileSync(join(ROOT, ".github/team.json"), "utf8"));
const D = JSON.parse(readFileSync(join(ROOT, "docs/planning/wbs_data.json"), "utf8"));

// 1. Auth + target ------------------------------------------------------------------------------
if (gh(["auth", "status"], { allowFail: true }) === null) {
  console.error("Not logged in. Run `gh auth login` first."); process.exit(1);
}
const owner = opt("--owner", json(gh(["api", "user"])).login);
const name = opt("--name", "or-intelligence");
const full = `${owner}/${name}`;
const visibility = flag("--public") ? "--public" : "--private";
console.log(`Target repository: ${full} (${visibility.slice(2)})`);

// 2. Repository ----------------------------------------------------------------------------------
const existing = gh(["repo", "view", full, "--json", "name,isEmpty,defaultBranchRef"], { allowFail: true });
if (existing) {
  const info = json(existing);
  if (!flag("--use-existing")) {
    console.error(`Repository ${full} already exists (empty: ${info.isEmpty}). Nothing changed.\n`
      + "Inspect it first; re-run with --use-existing to add labels/issues/protection to it.");
    process.exit(2);
  }
  if (!info.isEmpty) console.log("Repository has commits: the initial push is skipped (no overwrite).");
  else pushInitial();
} else {
  gh(["repo", "create", full, visibility, "--description", `${D.project.name}: ${D.project.tagline}`, "--disable-wiki"]);
  pushInitial();
}

function pushInitial() {
  const remotes = execFileSync("git", ["remote"], { cwd: ROOT, encoding: "utf8" }).split(/\s+/);
  if (!remotes.includes("origin")) git(["remote", "add", "origin", `https://github.com/${full}.git`]);
  git(["push", "-u", "origin", "main"]);
  const hasDevelop = execFileSync("git", ["branch", "--list", "develop"], { cwd: ROOT, encoding: "utf8" }).trim();
  if (!hasDevelop) git(["branch", "develop", "main"]);
  git(["push", "-u", "origin", "develop"]);
}

gh(["api", "-X", "PATCH", `repos/${full}`, "-F", "delete_branch_on_merge=true", "-F", "allow_squash_merge=true",
  "-F", "allow_merge_commit=true", "-F", "allow_rebase_merge=false", "-f", "default_branch=main"], { allowFail: true });

// 3. Labels -------------------------------------------------------------------------------------
for (const l of manifest.labels) gh(["label", "create", l.name, "--repo", full, "--color", l.color, "--description", l.description, "--force"]);
console.log(`labels: ${manifest.labels.length} ensured`);

// 4. Milestones ---------------------------------------------------------------------------------
const msExisting = json(gh(["api", `repos/${full}/milestones?state=all&per_page=100`])) ?? [];
for (const m of manifest.milestones) {
  if (msExisting.some((x) => x.title === m.title)) continue;
  gh(["api", "-X", "POST", `repos/${full}/milestones`, "-f", `title=${m.title}`, "-f", `due_on=${new Date(m.due_on).toISOString()}`,
    "-f", `description=${m.description}`]);
}
console.log(`milestones: ${manifest.milestones.length} ensured`);

// 5. Issues -------------------------------------------------------------------------------------
const listed = json(gh(["issue", "list", "--repo", full, "--state", "all", "--limit", "500", "--json", "number,title,body"])) ?? [];
const numbers = {};
const created = [];
for (const is of manifest.issues) {
  const hit = listed.find((x) => x.title === is.title);
  if (hit) { numbers[is.wbs] = hit.number; continue; }
  const a = ["issue", "create", "--repo", full, "--title", is.title, "--body-file", tmpFile(`${is.wbs}.md`, is.body),
    "--milestone", is.milestone];
  for (const l of is.labels) a.push("--label", l);
  const gu = team.members[is.member]?.github;
  if (gu) a.push("--assignee", gu);
  const url = gh(a);
  const n = Number((url.match(/\/issues\/(\d+)/) || [])[1]);
  numbers[is.wbs] = n || `<${is.wbs}>`;
  created.push(is.wbs);
  console.log(`issue #${n} ${is.title}`);
}
// second pass: turn {{#x.y.z}} placeholders into real #numbers
const fill = (body) => body.replace(/\{\{#([\d.]+)\}\}/g, (_, id) => (typeof numbers[id] === "number" ? `#${numbers[id]}` : `WBS ${id}`));
for (const is of manifest.issues) {
  const hit = listed.find((x) => x.title === is.title);
  if (!created.includes(is.wbs) && !(hit && hit.body.includes("{{#"))) continue;
  if (typeof numbers[is.wbs] !== "number") continue;
  gh(["issue", "edit", String(numbers[is.wbs]), "--repo", full, "--body-file", tmpFile(`${is.wbs}.filled.md`, fill(is.body))]);
}
if (!DRY) writeFileSync(join(ROOT, ".github/issues/issue_numbers.json"), JSON.stringify(numbers, null, 2) + "\n");
console.log(`issues: ${created.length} created, ${manifest.issues.length - created.length} already existed`);

// 6. Branch protection ---------------------------------------------------------------------------
const allUsers = Object.values(team.members).every((m) => m.github);
const protection = {
  required_status_checks: { strict: false, contexts: ["Python (ruff + pytest)", "Web (build + vitest)", "Repo hygiene (no data, weights or secrets)"] },
  enforce_admins: false,
  required_pull_request_reviews: { required_approving_review_count: 1, require_code_owner_reviews: allUsers, dismiss_stale_reviews: false },
  restrictions: null,
  allow_force_pushes: false,
  allow_deletions: false,
};
for (const branch of ["main", "develop"]) {
  const r = gh(["api", "-X", "PUT", `repos/${full}/branches/${branch}/protection`, "--input", tmpFile(`prot-${branch}.json`, JSON.stringify(protection))], { allowFail: true });
  console.log(r === null
    ? `[WARN] branch protection on ${branch} failed. Private repos on a free personal plan cannot use protection; `
      + "use GitHub Pro (free with the Student Developer Pack), a GitHub Team org, or a public repo, then re-run with --use-existing."
    : `branch protection: ${branch} protected (PR + 1 approval + CI)`);
}

// 7. Collaborators (only with --invite) ---------------------------------------------------------
if (flag("--invite")) {
  for (const [id, m] of Object.entries(team.members)) {
    if (!m.github || m.github === owner) continue;
    gh(["api", "-X", "PUT", `repos/${full}/collaborators/${m.github}`, "-f", "permission=push"], { allowFail: true });
    console.log(`invited ${m.github} (Member ${id})`);
  }
} else {
  console.log("collaborators: skipped (re-run with --invite after filling .github/team.json)");
}
console.log(`\nDone: https://github.com/${full}`);
