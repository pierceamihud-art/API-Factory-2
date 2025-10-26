# Default Guardrails — GitHub Autopilot (Workspace‑Locked)

> Version: 2025-09-07 • Scope: New Project Bootstrap • Owner: Repo Maintainers

These guardrails lock project behavior to THIS workspace/repo so automation, CI, and AI assistants
(Mentor Mode + Expert‑GPT Mode + Single‑Step Focus Mode) behave predictably.

---

## 0) Project Modes (Always On)

- **Mentor Mode**: Explanations + rationale with links to code changes.
- **Expert‑GPT Mode**: Production‑grade decisions; no speculative steps.
- **Single‑Step Focus Mode (SSF)**: One step at a time. Each step must state:
  - **Step Command** (copy‑paste ready)
  - **Expected Result**
  - **Error Path** (common failures + fix)
  - **Mini‑Audit** (what to verify)

> SSF enforcement lives in PR checklist and CI jobs (`guardrails.yml`).

---

## 1) Workspace‑Lock

- All scripts run **relative to repo root**; no absolute paths.
- Environment via **`.env.example` + direnv** (no secrets in repo).
- **pnpm workspace** is canonical (or change in `guardrails.yml` before first commit).
- **CI is source of truth**: Local steps mirror CI commands.

---

## 2) Definition of Done (DoD)

A change is “Done” only if ALL pass:
- Unit/type checks ✅
- Lint/format ✅
- Security/baseline checks ✅
- PR template checklist completed ✅
- Artifacts exported (e.g., PDF, SBOM) if applicable ✅
- Labels applied + linear/issue link ✅

---

## 3) Required Files (included in this pack)

- `.github/workflows/guardrails.yml` — SSF checks, lint/type/security
- `.github/workflows/typecheck-matrix.yml` — web/node split typecheck
- `.github/dependabot.yml` — weekly deps
- `.github/pull_request_template.md` — SSF checklist
- `.github/ISSUE_TEMPLATE/bug_report.md` / `feature_request.md`
- `.github/CODEOWNERS`
- `.editorconfig` + `.gitattributes`
- `SECURITY.md` + `CONTRIBUTING.md`
- `.env.example`
- `.github/labels.yml` (for label‑sync action, optional)

---

## 4) Branch & PR Policy

- **Default branch protected**: require status checks from `guardrails.yml`.
- Squash merges; delete branches on merge.
- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `perf:`, `test:`
- Require linked issue on `feat:`/`fix:` PRs.

---

## 5) Secrets & Config

- Never commit real secrets. Provide **`.env.example`** only.
- CI reads from GitHub Actions secrets:
  - `NODE_AUTH_TOKEN` (if private registry)
  - `NPM_TOKEN` (alt)
  - `CODECOV_TOKEN` (optional)
- Use **OIDC** for cloud access where possible (no long‑lived keys).

---

## 6) Security Baseline

- `npm audit`/`pnpm audit` gate (low‑severity allowed, med+ blocked unless `SECURITY.md` waiver).
- Dependency review + provenance checks.
- SBOM generation (CycloneDX) optional toggle.

---

## 7) Docs & Exports

- READMEs must have a **Quickstart** that matches CI.
- If required, generate **PDF export** of main docs on tagged releases.
- Keep **CHANGELOG.md** (Conventional Commits → `standard-version` or `changesets`).

---

## 8) Monorepo Conventions (if used)

- `pnpm-workspace.yaml` lists `apps/*`, `packages/*`.
- `tsconfig.base.json` at root; project refs per package.
- Each package: independent `build`, `lint`, `test`, `typecheck` scripts.

---

## 9) SSF Step Template (copy into issues/PRs)

**Step Command**
```sh
# paste exact command(s)
```

**Expected Result**
- ...

**Error Path**
- <symptom> → <fix>
- <symptom> → <fix>

**Mini‑Audit**
- [ ] Files created/modified
- [ ] CI job passed: <name>
- [ ] Runtime sanity: <command/output>

---

## 10) Rollback & Escalation

- If `guardrails.yml` fails on main: block merges; hotfix branch from tag; assign CODEOWNER.
- Post‑incident: add checklist item to PR template to prevent recurrence.

---

## 11) Governance

- CODEOWNERS required review for `/apps/**`, `/packages/**`, `/infra/**`.
- Emergency bypass requires `@owners` approval + follow‑up PR within 24h.
