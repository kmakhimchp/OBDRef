#!/usr/bin/env python3
"""
Generate Workflow.html — read-only workflow status dashboard.

Reads CLAUDE.md, MILESTONES.md, git state, and local file system to
determine progress and produce a self-contained HTML status page. The page
shows which workflow steps have passed and where the project currently stands
— no user interaction required.

Outputs a self-contained Workflow.html with no external dependencies.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def find_project_root():
    script_dir = Path(__file__).resolve().parent
    if (script_dir / "CLAUDE.md").exists() or (script_dir / "MILESTONES.md").exists():
        return script_dir
    return Path.cwd()


def parse_claude_md(project_root):
    path = project_root / "CLAUDE.md"
    info = {
        "project_name": "", "jira_project_key": "", "jira_project_url": "",
        "jira_assignee_email": "", "application_branch": "",
        "active_milestone": "", "active_jira_id": "",
        "description": "", "initial_prompt": "", "jira_epic_id": "",
        "harmony_project_path": "",
    }
    if not path.exists():
        return info
    text = path.read_text(encoding="utf-8", errors="replace")

    def _get(pattern, flags=0):
        m = re.search(pattern, text, flags)
        return m.group(1).strip() if m else ""

    info["project_name"] = _get(r"^#\s+Project:\s*(.+)", re.MULTILINE)
    info["jira_project_key"] = _get(r"JIRA Project Key:\s*`?([^`\n]+)`?")
    info["jira_project_url"] = _get(r"JIRA Project URL:\s*`?([^`\n]+)`?")
    info["jira_assignee_email"] = _get(r"JIRA Assignee Email:\s*`?([^`\n]+)`?")
    info["jira_epic_id"] = _get(r"JIRA Epic ID:\s*`?([^`\n]+)`?")
    info["application_branch"] = _get(r"Application Branch:\s*`?([^`\n]+)`?")
    info["active_milestone"] = _get(r"currently working on\s+(.+?)[\.\n]", re.I).rstrip(".")
    info["active_jira_id"] = _get(r"JIRA ID:\s*`?([A-Z][A-Z0-9_]+-\d+)`?")
    info["description"] = _get(r"## Description\s*\n([\s\S]*?)(?=\n## |\Z)")
    info["initial_prompt"] = _get(r"## Initial Prompt\s*\n>\s*([\s\S]*?)(?=\n## |\n\n[^>]|\Z)")
    info["harmony_project_path"] = (
        _get(r"Harmony Project Path:\s*`?([^`\n]+)`?")
        or _get(r"\|\s*Firmware\s*\|[^|]*\|[^|]*\|\s*`?([^`|\n]+?)\s*`?\s*\|")  # Build Validation table Working Directory
    )

    # Clean placeholder values
    for k in list(info.keys()):
        v = info[k]
        if v and (v.startswith("_[") or v.startswith("<")):
            info[k] = ""

    return info


def parse_milestones_md(project_root):
    path = project_root / "MILESTONES.md"
    milestones = []
    if not path.exists():
        return milestones
    text = path.read_text(encoding="utf-8", errors="replace")
    pat = re.compile(r"(?:^|\n)#+\s*Milestone\s+(\d+)\s*[:\-–—]\s*(.+)", re.I)

    for match in pat.finditer(text):
        num = int(match.group(1))
        title = match.group(2).strip()
        nxt = pat.search(text, match.end())
        block = text[match.end():nxt.start() if nxt else len(text)]

        jira_id = ""
        jm = re.search(r"JIRA\s*(?:ID|Key|Ticket)?\s*[:\-]\s*`?([A-Z][A-Z0-9_]+-\d+)`?", block, re.I)
        if not jm:
            jm = re.search(r"\*\*JIRA\s*ID\*\*\s*\|\s*`?([A-Z][A-Z0-9_]+-\d+)`?", block, re.I)
        if jm:
            jira_id = jm.group(1).strip()

        reqs = []
        for rm in re.finditer(r"R(\d+)\s*:\s*(.+)", block):
            reqs.append({"id": f"R{rm.group(1)}", "text": rm.group(2).strip()})
        if not reqs:
            for rm in re.finditer(r"\|\s*R(\d+)\s*\|\s*(.+?)\s*\|", block):
                reqs.append({"id": f"R{rm.group(1)}", "text": rm.group(2).strip()})

        status = "not_started"
        if re.search(r"(?:status|Status)\s*[:\-]\s*(?:done|complete|merged)", block, re.I):
            status = "complete"
        elif re.search(r"\*\*Status\*\*\s*\|\s*(?:Done|Complete|Merged)", block):
            status = "complete"
        elif re.search(r"(?:status|Status)\s*[:\-]\s*(?:in.?progress|active)", block, re.I):
            status = "in_progress"
        elif re.search(r"\*\*Status\*\*\s*\|\s*In\s*Progress", block):
            status = "in_progress"

        sign_off = ""
        sm = re.search(r"(?:Requirements?\s+)?Sign.?Off\s*:\s*(.+)", block, re.I)
        if not sm:
            sm = re.search(r"\*\*Approved\s+By\*\*\s*\|\s*(.+?)\s*\|", block, re.I)
        if sm:
            v = sm.group(1).strip()
            if v and not v.startswith("<") and v != "—":
                sign_off = v

        milestones.append(dict(number=num, title=title, jira_id=jira_id,
                               requirements=reqs, status=status, sign_off=sign_off))
    return sorted(milestones, key=lambda m: m["number"])


# ---------------------------------------------------------------------------
# Git & filesystem helpers
# ---------------------------------------------------------------------------

def _git(args, cwd):
    try:
        r = subprocess.run(["git"] + args, cwd=str(cwd),
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def detect_progress(project_root, claude, milestones):
    """Detect which steps are already done based on filesystem/git state."""
    branches = _git(["branch", "-a"], project_root)
    remote = _git(["remote", "get-url", "origin"], project_root)
    in_git = _git(["rev-parse", "--is-inside-work-tree"], project_root) == "true"
    user_name = _git(["config", "user.name"], project_root)
    user_email = _git(["config", "user.email"], project_root)
    raw_text = (project_root / "CLAUDE.md").read_text(encoding="utf-8", errors="replace") if (project_root / "CLAUDE.md").exists() else ""

    mcp_path = project_root / ".mcp_verified.json"
    mcp = {}
    if mcp_path.exists():
        try:
            mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    app_branch = claude.get("application_branch", "")

    prereqs = {
        "repo_exists": in_git and bool(remote),
        "git_configured": bool(user_name and user_email),
        "bitbucket_access": bool(remote),
        "jira_access": bool(claude.get("jira_project_key")),
        "jira_recorded": bool(claude.get("jira_project_key") and claude.get("jira_project_url")),
        "jira_assignee": bool(claude.get("jira_assignee_email")),
        "ai_tool": True,
        "build_env": "Build Validation" in raw_text,
        "harmony_path": bool(claude.get("harmony_project_path")),
        "mcp_bitbucket": bool(mcp.get("bitbucket", {}).get("verified")),
        "mcp_jira": bool(mcp.get("jira", {}).get("verified")),
    }

    has_claude_sections = all(s in raw_text for s in ["# Project:", "JIRA Configuration", "Build Validation", "Rules for AI Tools"])
    ms_path = project_root / "MILESTONES.md"
    has_milestones = ms_path.exists() and "Milestone" in (ms_path.read_text(encoding="utf-8", errors="replace") if ms_path.exists() else "")
    dirs_exist = all((project_root / d).is_dir() for d in ["docs", "docs/tests", "docs/reviews", "docs/diagrams"])
    module_dirs = list(project_root.glob("**/app_modules/*/MODULE.md")) + list(project_root.glob("**/modules/*/MODULE.md"))

    setup = {
        "repo_cloned": in_git,
        "default_branch": bool(_git(["branch", "--show-current"], project_root)),
        "git_creds": in_git and bool(remote),
        "harmony_identified": bool(claude.get("description")),
        "baseline_build": "Build Validation" in raw_text,
        "app_branch": app_branch and app_branch in branches,
        "owner_assigned": bool(claude.get("jira_assignee_email")),
        "claude_md": (project_root / "CLAUDE.md").exists() and has_claude_sections,
        "jira_epic": bool(claude.get("jira_epic_id")),
        "milestones_md": has_milestones,
        "code_review_checklist": (project_root / "CODE_REVIEW_CHECKLIST.md").exists(),
        "workflow_dirs": dirs_exist,
        "module_dirs": bool(module_dirs),
        "readme": (project_root / "README.md").exists(),
        "mcp_verified": mcp_path.exists(),
        "workflow_html": (project_root / "Workflow.html").exists(),
    }

    ms_progress = []
    for ms in milestones:
        num = ms["number"]
        review_exists = (project_root / f"docs/reviews/REVIEW_M{num}.md").exists()
        test_exists = (project_root / f"docs/tests/TEST_M{num}.md").exists()
        is_complete = ms["status"] == "complete"

        is_active = False
        if claude.get("active_jira_id") == ms.get("jira_id") and ms["jira_id"]:
            is_active = True
        elif claude.get("active_milestone") and f"Milestone {num}" in claude.get("active_milestone", ""):
            is_active = True

        prev_done = True
        if num > 1:
            prev = next((m for m in milestones if m["number"] == num - 1), None)
            prev_done = prev and prev["status"] == "complete"

        ms_progress.append({
            "number": num,
            "is_active": is_active,
            "is_complete": is_complete,
            "prev_done": prev_done,
            "has_jira": bool(ms["jira_id"]),
            "signed_off": bool(ms["sign_off"]) or review_exists or is_complete,
            "review_exists": review_exists or is_complete,
            "test_exists": test_exists or is_complete,
        })

    return {"prereqs": prereqs, "setup": setup, "milestones": ms_progress}


# ---------------------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------------------

def generate_html(claude, milestones, progress):
    milestones_json = json.dumps(milestones, indent=2, ensure_ascii=False)
    progress_json = json.dumps(progress, indent=2, ensure_ascii=False)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    project_name = claude.get("project_name", "") or "(No project configured)"
    description = claude.get("description", "").strip().split("\n")[0] if claude.get("description") else ""
    app_branch = claude.get("application_branch", "") or "—"
    epic_id = claude.get("jira_epic_id", "") or "—"
    active_ms = claude.get("active_milestone", "") or "—"
    active_jira = claude.get("active_jira_id", "") or "—"
    jira_url = claude.get("jira_project_url", "")
    initial_prompt = claude.get("initial_prompt", "").strip() or ""

    # Compute totals for the progress bar
    prereq_total = len(progress.get("prereqs", {}))
    prereq_done = sum(1 for v in progress.get("prereqs", {}).values() if v)
    setup_total = len(progress.get("setup", {}))
    setup_done = sum(1 for v in progress.get("setup", {}).values() if v)
    ms_complete = sum(1 for m in milestones if m.get("status") == "complete")
    ms_total = len(milestones)

    total_steps = prereq_total + setup_total + (ms_total * 17)
    done_steps = prereq_done + setup_done
    for i, ms in enumerate(milestones):
        mp = progress.get("milestones", [])[i] if i < len(progress.get("milestones", [])) else {}
        if ms.get("status") == "complete":
            done_steps += 17
        elif mp.get("is_active"):
            if mp.get("test_exists"):
                done_steps += 15
            elif mp.get("review_exists"):
                done_steps += 12
            elif mp.get("signed_off"):
                done_steps += 7
            elif mp.get("has_jira"):
                done_steps += 3

    pct = round(done_steps / total_steps * 100) if total_steps > 0 else 0

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Workflow Status — {project_name}</title>
<style>
:root {{
  --blue: #2980B9; --blue-light: #D6EAF8;
  --green: #27AE60; --green-light: #D5F5E3;
  --orange: #E67E22; --orange-light: #FDEBD0;
  --gray: #95A5A6; --gray-light: #F2F3F4;
  --dark: #2C3E50; --red: #E74C3C; --red-light: #FADBD8;
  --purple: #8E44AD; --purple-light: #F5EEF8;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #F8F9FA; color: var(--dark); line-height: 1.5;
  padding: 20px; max-width: 1100px; margin: 0 auto;
}}

header {{
  background: linear-gradient(135deg, var(--dark), #34495E);
  color: white; padding: 28px 32px; border-radius: 12px; margin-bottom: 20px;
}}
header h1 {{ font-size: 1.7em; margin-bottom: 4px; }}
header .subtitle {{ opacity: 0.85; font-size: 0.92em; }}
header .prompt {{ opacity: 0.7; font-size: 0.82em; margin-top: 8px; font-style: italic; }}

.info-card {{
  background: white; border-radius: 10px; padding: 18px 22px;
  margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px;
}}
.info-item {{ }}
.info-item .label {{ font-size: 0.72em; font-weight: 600; color: var(--gray); text-transform: uppercase; letter-spacing: 0.4px; }}
.info-item .value {{ font-size: 0.92em; font-weight: 500; color: var(--dark); }}

.overall {{
  background: white; border-radius: 10px; padding: 18px 22px;
  margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.overall h2 {{ font-size: 1.1em; margin-bottom: 10px; }}
.stats-row {{ display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 12px; font-size: 0.88em; }}
.stat {{ display: flex; align-items: center; gap: 6px; }}
.stat-num {{ font-weight: 700; font-size: 1.3em; }}
.stat-label {{ color: var(--gray); }}
.bar-outer {{
  background: var(--gray-light); border-radius: 20px; height: 24px;
  position: relative; overflow: hidden;
}}
.bar-fill {{
  height: 100%; border-radius: 20px;
  background: linear-gradient(90deg, var(--green), #2ECC71);
}}
.bar-text {{
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%); font-weight: 600; font-size: 0.8em;
}}

.section-title {{
  font-size: 1.1em; font-weight: 600; margin: 22px 0 10px;
  padding-bottom: 5px; border-bottom: 2px solid var(--blue); display: inline-block;
}}
.phase-card {{
  background: white; border-radius: 10px; padding: 18px 22px;
  margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.phase-card h3 {{ font-size: 1em; margin-bottom: 10px; }}

.step-row {{
  display: flex; align-items: center; gap: 10px;
  padding: 7px 10px; border-radius: 6px; font-size: 0.84em;
  border-bottom: 1px solid var(--gray-light);
}}
.step-row:last-child {{ border-bottom: none; }}
.step-row.done {{ opacity: 0.55; }}
.step-row.current {{
  background: var(--blue-light); border-radius: 6px;
  box-shadow: inset 3px 0 0 var(--blue); font-weight: 600;
  opacity: 1;
}}
.step-icon {{
  width: 18px; height: 18px; border-radius: 4px; border: 2px solid var(--gray);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 0.7em;
}}
.step-icon.done {{ background: var(--green); border-color: var(--green); color: white; font-weight: bold; }}
.step-icon.active {{ background: var(--blue); border-color: var(--blue); color: white; font-weight: bold; }}
.step-name {{ flex: 1; min-width: 0; }}
.tag {{
  font-size: 0.64em; font-weight: 600; padding: 2px 5px;
  border-radius: 3px; white-space: nowrap;
}}
.tag-auto {{ background: var(--blue-light); color: var(--blue); }}
.tag-manual {{ background: var(--orange-light); color: var(--orange); }}

.ms-card {{
  background: white; border-radius: 10px; padding: 20px 24px;
  margin-bottom: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border-left: 5px solid var(--gray);
}}
.ms-card.complete {{ border-left-color: var(--green); }}
.ms-card.active {{ border-left-color: var(--blue); }}
.ms-header {{
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px; flex-wrap: wrap; gap: 8px;
}}
.ms-header h3 {{ font-size: 1.05em; }}
.badge {{
  font-size: 0.72em; font-weight: 600; padding: 3px 10px;
  border-radius: 20px; text-transform: uppercase; letter-spacing: 0.4px;
}}
.badge-complete {{ background: var(--green-light); color: var(--green); }}
.badge-progress {{ background: var(--blue-light); color: var(--blue); }}
.badge-pending {{ background: var(--gray-light); color: var(--gray); }}

.sub-phase-title {{
  font-size: 0.76em; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; color: var(--gray); margin: 12px 0 4px;
  padding-bottom: 2px; border-bottom: 1px dashed var(--gray-light);
}}

.requirements {{ margin-bottom: 10px; font-size: 0.84em; }}
.requirements summary {{ cursor: pointer; color: var(--blue); font-weight: 500; }}
.requirements ul {{ margin: 4px 0 0 18px; }}
.requirements li {{ margin-bottom: 2px; }}

.no-milestones {{
  text-align: center; padding: 40px 20px; color: var(--gray);
  font-size: 0.95em;
}}
.no-milestones code {{ background: var(--gray-light); padding: 2px 8px; border-radius: 4px; }}

.legend {{
  background: white; border-radius: 10px; padding: 14px 18px;
  margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.82em;
}}
.legend-item {{ display: flex; align-items: center; gap: 5px; }}
.legend-swatch {{
  width: 14px; height: 14px; border-radius: 3px; border: 2px solid transparent;
}}
.legend-swatch.done {{ background: var(--green); }}
.legend-swatch.active {{ background: var(--blue); }}
.legend-swatch.pending {{ border-color: var(--gray); background: white; }}

.timestamp {{ text-align: center; color: var(--gray); font-size: 0.78em; margin-top: 16px; }}

@media (max-width: 700px) {{
  body {{ padding: 10px; }}
  header {{ padding: 18px; }}
  .info-card {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<header>
  <h1>{project_name}</h1>
  <div class="subtitle">AI-Driven Engineering Workflow &mdash; Status Dashboard</div>
  {"<div class='prompt'>&ldquo;" + initial_prompt[:200] + ("&hellip;" if len(initial_prompt) > 200 else "") + "&rdquo;</div>" if initial_prompt else ""}
</header>

<div class="info-card">
  <div class="info-item"><div class="label">Application Branch</div><div class="value"><code>{app_branch}</code></div></div>
  <div class="info-item"><div class="label">JIRA Epic</div><div class="value">{epic_id}</div></div>
  <div class="info-item"><div class="label">Active Milestone</div><div class="value">{active_ms}</div></div>
  <div class="info-item"><div class="label">Active JIRA ID</div><div class="value">{active_jira}</div></div>
</div>

<div class="overall">
  <h2>Overall Progress</h2>
  <div class="stats-row">
    <div class="stat"><span class="stat-num">{prereq_done}/{prereq_total}</span><span class="stat-label">Prerequisites</span></div>
    <div class="stat"><span class="stat-num">{setup_done}/{setup_total}</span><span class="stat-label">Setup</span></div>
    <div class="stat"><span class="stat-num">{ms_complete}/{ms_total}</span><span class="stat-label">Milestones</span></div>
  </div>
  <div class="bar-outer"><div class="bar-fill" style="width:{pct}%"></div>
  <span class="bar-text">{done_steps}/{total_steps} ({pct}%)</span></div>
</div>

<div class="section-title">Prerequisites</div>
<div class="phase-card" id="phase-prereqs"></div>

<div class="section-title">Repository Setup</div>
<div class="phase-card" id="phase-setup"></div>

<div class="section-title">Milestones</div>
<div id="phase-milestones"></div>

<div class="legend">
  <div class="legend-item"><span class="legend-swatch done"></span> Done</div>
  <div class="legend-item"><span class="legend-swatch active"></span> Current</div>
  <div class="legend-item"><span class="legend-swatch pending"></span> Pending</div>
  <div class="legend-item"><span class="tag tag-auto">[AUTO]</span> AI-automated</div>
  <div class="legend-item"><span class="tag tag-manual">[MANUAL]</span> Engineer action</div>
</div>

<p class="timestamp">Generated {timestamp} by generate_workflow.py &mdash; read-only status snapshot</p>

<script>
const MILESTONES_DATA = {milestones_json};
const PROGRESS_DATA = {progress_json};

function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

function renderStep(name, tag, isDone, isCurrent) {{
  const rowCls = isDone ? 'done' : isCurrent ? 'current' : '';
  const iconCls = isDone ? 'done' : isCurrent ? 'active' : '';
  const iconText = isDone ? '\\u2713' : isCurrent ? '\\u25B6' : '';
  const tagCls = tag === 'MANUAL' ? 'tag-manual' : 'tag-auto';
  return `<div class="step-row ${{rowCls}}"><span class="step-icon ${{iconCls}}">${{iconText}}</span><span class="step-name">${{esc(name)}}</span><span class="tag ${{tagCls}}">[${{tag}}]</span></div>`;
}}

function findCurrentStep(steps) {{
  for (let i = 0; i < steps.length; i++) {{
    if (!steps[i][1]) return i;
  }}
  return -1;
}}

function renderPhase(containerId, title, steps) {{
  const container = document.getElementById(containerId);
  const doneCount = steps.filter(s => s[1]).length;
  const currentIdx = findCurrentStep(steps);
  let html = `<h3>${{title}} (${{doneCount}}/${{steps.length}})</h3>`;
  steps.forEach((s, i) => {{
    html += renderStep(s[0], s[2], s[1], i === currentIdx);
  }});
  container.innerHTML = html;
}}

function init() {{
  const pre = PROGRESS_DATA.prereqs || {{}};
  const prereqSteps = [
    ['Bitbucket repository exists', pre.repo_exists, 'AUTO'],
    ['Git installed & configured', pre.git_configured, 'AUTO'],
    ['Bitbucket access (read/write)', pre.bitbucket_access, 'AUTO'],
    ['JIRA access', pre.jira_access, 'AUTO'],
    ['JIRA project key & URL recorded', pre.jira_recorded, 'AUTO'],
    ['JIRA assignee email recorded', pre.jira_assignee, 'AUTO'],
    ['Harmony project location identified', pre.harmony_path, 'AUTO'],
    ['AI tool access (Claude)', pre.ai_tool, 'AUTO'],
    ['Build environment configured', pre.build_env, 'AUTO'],
    ['Bitbucket MCP verified', pre.mcp_bitbucket, 'AUTO'],
    ['JIRA MCP verified', pre.mcp_jira, 'AUTO'],
  ];
  renderPhase('phase-prereqs', 'Prerequisites', prereqSteps);

  const s = PROGRESS_DATA.setup || {{}};
  const setupSteps = [
    ['Clone repository locally', s.repo_cloned, 'AUTO'],
    ['Check out default branch', s.default_branch, 'AUTO'],
    ['Git credentials verified', s.git_creds, 'AUTO'],
    ['Identify target Harmony project', s.harmony_identified, 'AUTO'],
    ['Verify baseline build', s.baseline_build, 'MANUAL'],
    ['Create CLAUDE.md + MILESTONES.md + app branch', s.claude_md, 'AUTO'],
    ['Application branch created', s.app_branch, 'AUTO'],
    ['Repository owner assigned', s.owner_assigned, 'AUTO'],
    ['CODE_REVIEW_CHECKLIST.md copied', s.code_review_checklist, 'AUTO'],
    ['Workflow directories created', s.workflow_dirs, 'AUTO'],
    ['Module directories with MODULE.md', s.module_dirs, 'AUTO'],
    ['Project README.md updated', s.readme, 'AUTO'],
    ['MCP verification run', s.mcp_verified, 'AUTO'],
    ['Workflow.html generated', s.workflow_html, 'AUTO'],
    ['JIRA Epic created and recorded', s.jira_epic, 'AUTO'],
    ['Setup files committed', false, 'AUTO'],
  ];
  renderPhase('phase-setup', 'Repository Setup', setupSteps);

  // Milestones
  const msContainer = document.getElementById('phase-milestones');
  if (!MILESTONES_DATA || MILESTONES_DATA.length === 0) {{
    msContainer.innerHTML = '<div class="no-milestones"><p>No milestones found.</p><p>Create <code>MILESTONES.md</code> then re-run <code>python generate_workflow.py</code>.</p></div>';
    return;
  }}

  let msHtml = '';
  MILESTONES_DATA.forEach((ms, idx) => {{
    const prog = (PROGRESS_DATA.milestones || [])[idx] || {{}};
    const isComplete = ms.status === 'complete';
    const isActive = prog.is_active;
    const cardCls = isComplete ? 'complete' : isActive ? 'active' : '';
    const badgeCls = isComplete ? 'badge-complete' : isActive ? 'badge-progress' : 'badge-pending';
    const badgeText = isComplete ? 'Complete' : isActive ? 'In Progress' : 'Not Started';

    msHtml += `<div class="ms-card ${{cardCls}}">`;
    msHtml += `<div class="ms-header"><h3>Milestone ${{ms.number}}: ${{esc(ms.title)}}${{ms.jira_id ? ' &mdash; ' + esc(ms.jira_id) : ''}}</h3>`;
    msHtml += `<span class="badge ${{badgeCls}}">${{badgeText}}</span></div>`;

    if (ms.requirements && ms.requirements.length > 0) {{
      msHtml += `<details class="requirements"><summary>Requirements (${{ms.requirements.length}})</summary><ul>`;
      ms.requirements.forEach(r => {{ msHtml += `<li>${{esc(r.id)}}: ${{esc(r.text)}}</li>`; }});
      msHtml += `</ul></details>`;
    }}

    const dorSteps = [
      ['Previous milestone complete', ms.number === 1 || prog.prev_done, 'AUTO'],
      ['Requirements written in MILESTONES.md', ms.requirements && ms.requirements.length > 0, 'MANUAL'],
      ['JIRA ticket created & linked to epic', prog.has_jira, 'AUTO'],
      ['Requirements signed off on JIRA', prog.signed_off, 'MANUAL'],
      ['MODULE.md stubs exist & reviewed', prog.signed_off, 'MANUAL'],
      ['AI context loaded (CLAUDE.md updated)', prog.signed_off, 'AUTO'],
      ['JIRA ticket \\u2192 In Progress', prog.is_active || prog.is_complete, 'AUTO'],
    ];
    const implSteps = [
      ['Acceptance criteria verified', prog.review_exists, 'MANUAL'],
      ['Implementation on application branch', prog.review_exists, 'AUTO'],
      ['Build passed (zero errors/warnings)', prog.review_exists, 'AUTO'],
      ['Code review checklist passed', prog.review_exists, 'AUTO'],
      ['Documentation updated (MODULE.md + README)', prog.review_exists, 'AUTO'],
      ['Code committed to application branch', prog.test_exists, 'AUTO'],
    ];
    const testSteps = [
      ['Milestone testing (5 dimensions)', prog.test_exists, 'MANUAL'],
      ['Test report committed', prog.test_exists, 'AUTO'],
      ['JIRA \\u2192 Done', prog.is_complete, 'AUTO'],
      ['Workflow.html regenerated', prog.is_complete, 'AUTO'],
    ];

    function renderSubPhase(title, steps) {{
      const currentIdx = findCurrentStep(steps);
      let h = `<div class="sub-phase-title">${{title}}</div>`;
      steps.forEach((s, i) => {{ h += renderStep(s[0], s[2], s[1], i === currentIdx && isActive); }});
      return h;
    }}

    msHtml += renderSubPhase('Definition of Ready', dorSteps);
    msHtml += renderSubPhase('Implementation & Gates', implSteps);
    msHtml += renderSubPhase('Testing & Completion', testSteps);
    msHtml += `</div>`;
  }});
  msContainer.innerHTML = msHtml;
}}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    root = find_project_root()
    print(f"Project root: {root}")

    claude = parse_claude_md(root)
    print(f"Project: {claude['project_name'] or '(no CLAUDE.md found — fresh mode)'}")

    milestones = parse_milestones_md(root)
    print(f"Milestones: {len(milestones)}")

    progress = detect_progress(root, claude, milestones)
    prereq_pass = sum(1 for v in progress["prereqs"].values() if v)
    setup_done = sum(1 for v in progress["setup"].values() if v)
    print(f"Prerequisites: {prereq_pass}/{len(progress['prereqs'])} verified")
    print(f"Setup steps: {setup_done}/{len(progress['setup'])} complete")

    for ms in milestones:
        mp = next((p for p in progress["milestones"] if p["number"] == ms["number"]), {})
        status = "complete" if mp.get("is_complete") else "active" if mp.get("is_active") else "pending"
        print(f"  M{ms['number']}: {ms['title']} — {status}")

    html = generate_html(claude, milestones, progress)
    out = root / "Workflow.html"
    out.write_text(html, encoding="utf-8")
    print(f"\nGenerated: {out}")
    print("Open Workflow.html in a browser to view the workflow status dashboard.")


if __name__ == "__main__":
    main()
