<div align="center">

# Londopy's agent skills

**Tools that make what your coding agent does silently legible — which skills registered, which MCP servers will fail and why, which settings file won, and who signed your commits. For Claude Code, Codex, Cursor, Gemini CLI, Copilot, OpenCode and every other Agent Skills host.**

[![CI](https://github.com/Londopy/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/Londopy/agent-skills/actions/workflows/ci.yml)
[![Sync](https://github.com/Londopy/agent-skills/actions/workflows/sync.yml/badge.svg)](https://github.com/Londopy/agent-skills/actions/workflows/sync.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen)](#the-skills)
[![Agent Skills](https://img.shields.io/badge/Agent_Skills-spec-111)](https://agentskills.io)
[![Works with](https://img.shields.io/badge/works_with-Claude_Code_%7C_Codex_%7C_Cursor_%7C_Gemini_CLI_%7C_Copilot_%7C_OpenCode-D97757)](#install)

</div>

---

Every coding agent registers skills, starts MCP servers, merges settings files and signs commits — and tells you nothing about any of it until something's missing. Each also keeps those things in a different place: Claude Code in `~/.claude`, Codex in `~/.codex` and `~/.agents`, Cursor in `~/.cursor`, Gemini in `~/.gemini`. Each skill here rebuilds one of those silent steps from disk, for the host you're in, with the reasons attached, then repairs or reports. Every one is a single stdlib-only Python script that also runs as a plain CLI, read-only unless you pass `--apply`, with `--json` and `--strict` for tooling and CI.

This repo is the whole family in one install. Each skill also lives in its own repo, which is the source of truth; the copies here are synced from upstream by [`sync.py`](sync.py), pinned in [`skills.lock.json`](skills.lock.json), and CI fails if they drift. (This repo was `claude-skills` until 2026-09-21; the old URL redirects.)

## The skills

| | Skill | Answers | Hosts | Repo |
|---|---|---|---|---|
| <a href="docs/skill-rollcall.png"><img src="docs/skill-rollcall.png" width="220" alt="skill-rollcall demo"></a> | **[skill-rollcall](skills/skill-rollcall/SKILL.md)** | Which skills are registered, which are new since the session started, which will *never* register and why — for the host you're in, or all of them side by side. `--lint` for why one doesn't trigger (and for Claude-only frontmatter other hosts ignore), `--audit` for what to read before running a skill you just installed, `--fix` for the folder moves that repair it. Knows the Agent Skills spec, the shared `.agents/skills` convention and Codex's `skills.config` disables. | reads Claude Code, Codex, Cursor, Gemini CLI, Copilot, OpenCode, Amp, Goose, Kiro, Windsurf, Cline/Zed/Warp | [Londopy/skill-rollcall](https://github.com/Londopy/skill-rollcall) |
| <a href="docs/mcp-rollcall.png"><img src="docs/mcp-rollcall.png" width="220" alt="mcp-rollcall demo"></a> | **[mcp-rollcall](skills/mcp-rollcall/SKILL.md)** | Which MCP servers will fail to connect and exactly why — missing command, dead path, unset variable, nothing listening on the port — and, with `--probe`, the server's own stderr, tool count and context cost that the host discards. Reads every host's config shape: `config.toml`, `mcp.json`, `settings.json`, `mcp-config.json`, `opencode.json`. | reads Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI, VS Code, Windsurf, OpenCode | [Londopy/mcp-rollcall](https://github.com/Londopy/mcp-rollcall) |
| <a href="docs/settings-effective.png"><img src="docs/settings-effective.png" width="220" alt="settings-effective demo"></a> | **[settings-effective](skills/settings-effective/SKILL.md)** | The merged Claude Code settings actually in effect, with the file that decided each key; and why the one you set isn't applying — wrong-scope file, shadowed value, `allow` outranked by `ask`, typo, a file skipped for bad JSON. `--explain` any of 231 keys. | inspects Claude Code's settings; runs from any host and says so | [Londopy/settings-effective](https://github.com/Londopy/settings-effective) |
| <a href="docs/git-attribution.png"><img src="docs/git-attribution.png" width="220" alt="git-attribution demo"></a> | **[git-attribution](skills/git-attribution/SKILL.md)** | Is an agent still adding `Co-Authored-By` to your commits, which commits already carry it (pushed vs local), a rewrite that strips it with a backup, and a pre-push hook that keeps it out. Knows Claude Code's setting, that Codex's is a workspace policy with nothing local to flip, and the trailers of Copilot, Cursor, Gemini, Devin and Aider. | any host; detects which one you're in | [Londopy/git-attribution](https://github.com/Londopy/git-attribution) |

## Install

The layout here — `skills/<name>/SKILL.md` + `scripts/<tool>.py` — is the [Agent Skills](https://agentskills.io) standard, so the same folders work in every host.

**Everything, `skills` CLI** — 79 agents supported (global; `--copy` because symlinks need Developer Mode on Windows):

```bash
npx skills add Londopy/agent-skills -g --copy                    # picks the agents it finds on your machine
npx skills add Londopy/agent-skills -g --copy -a codex -a cursor   # named agents
npx skills add Londopy/agent-skills -g --copy --all              # every agent, no prompts
```

**Everything, as one Claude Code plugin** (in an interactive `claude` session):

```
/plugin marketplace add Londopy/agent-skills
/plugin install londopy-skills@agent-skills
```

**One at a time** — the same marketplace lists each skill individually, sourced from its own repo:

```
/plugin install mcp-rollcall@agent-skills
```

**Codex:** `$skill-installer` with this repo's URL, or the copy below into `~/.agents/skills/`.

**By hand** — copy the four folders into the host's skills directory:

```bash
git clone https://github.com/Londopy/agent-skills
cp -r agent-skills/skills/* ~/.claude/skills/          # Claude Code
cp -r agent-skills/skills/* ~/.agents/skills/          # Codex, Cline, Zed, Warp (the universal path)
cp -r agent-skills/skills/* ~/.cursor/skills/          # Cursor
cp -r agent-skills/skills/* ~/.gemini/skills/          # Gemini CLI
cp -r agent-skills/skills/* ~/.copilot/skills/         # GitHub Copilot
cp -r agent-skills/skills/* ~/.config/opencode/skills/ # OpenCode
cp -r agent-skills/skills/* .agents/skills/            # one project, every host that walks .agents/
```

Most hosts watch their skills folders, so they show up without a restart. `/skill-rollcall` (Claude Code) or `$skill-rollcall` (Codex) confirms it — that's what it's for.

## How the copies stay honest

- `python sync.py` clones each upstream repo at its default branch, copies `skills/<name>/` and its demo image here, and writes the commit and version to `skills.lock.json`.
- `python sync.py --check` exits 1 if any copy differs from upstream. CI runs it on every push, then runs skill-rollcall over the four skills for every host, lint and audit in strict mode.
- A [weekly workflow](.github/workflows/sync.yml) re-syncs and commits any change as the repo owner, so a fix landing upstream reaches this bundle without a manual step.
- Bugs and PRs go to the individual repos. A change made here would be overwritten on the next sync.

## Conventions the family shares

- `skills/<name>/SKILL.md` + one `scripts/<tool>.py`, Python 3.10+, stdlib only. Frontmatter follows the Agent Skills spec (`name`, `description`, `license`, `compatibility`, `metadata`); an optional `agents/openai.yaml` carries Codex / ChatGPT UI metadata and is ignored elsewhere.
- Host detection from the environment (`CLAUDECODE`, `CODEX_SANDBOX`, `CURSOR_AGENT`, `GEMINI_CLI`), `--agent` to override, `all` when nothing identifies the host. The report always says which host it resolved and why.
- Read-only by default; mutation only behind `--fix --apply` (or `--guard --apply`), always after a printed plan.
- `--json` for tooling, `--strict` for CI, `--problems-only` when only findings matter.
- A SKILL.md that says which mode to run from what the user asked, tells the agent to answer the question before summarizing, and ends with what the tool *cannot* do.
- Tests on throwaway fixtures, a 3-OS × 2-Python CI matrix (3.10 exercises the stdlib TOML fallback, 3.13 checks it against `tomllib`), and a `docs/demo.png` rendered from real output.

## License

MIT, same as each upstream repo.
