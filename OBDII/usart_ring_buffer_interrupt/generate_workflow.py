#!/usr/bin/env python3
"""
Generate Workflow.html — interactive step-by-step workflow guide.

Reads CLAUDE.md, MILESTONES.md, git state, and local file system to
determine progress and embed project data as JSON into a self-contained
interactive HTML page. The HTML uses JavaScript to:
  - Populate prompts dynamically from input fields
  - Track progress via localStorage checkboxes
  - Highlight the current step and auto-scroll

Works in two modes:
  - Fresh project (no CLAUDE.md): produces wizard with empty input fields
  - Existing project: pre-fills fields and milestone data from parsed files

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
        "active_milestone": "", "active_jira_id": "", "active_branch": "",
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
    info["active_branch"] = _get(r"(?:Milestone Branch|Branch):\s*`?([^`\n]+)`?")
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
        branch_exists = ms["jira_id"] and ms["jira_id"] in branches

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
            "signed_off": bool(ms["sign_off"]) or branch_exists or review_exists or is_complete,
            "branch_exists": branch_exists or review_exists or is_complete,
            "review_exists": review_exists or is_complete,
            "test_exists": test_exists or is_complete,
        })

    return {"prereqs": prereqs, "setup": setup, "milestones": ms_progress}


# ---------------------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------------------

def generate_html(claude, milestones, progress):
    project_data_json = json.dumps(claude, indent=2, ensure_ascii=False)
    milestones_json = json.dumps(milestones, indent=2, ensure_ascii=False)
    progress_json = json.dumps(progress, indent=2, ensure_ascii=False)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Workflow Guide</title>
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
  padding: 20px; max-width: 1200px; margin: 0 auto;
}}
a {{ color: var(--blue); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

header {{
  background: linear-gradient(135deg, var(--dark), #34495E);
  color: white; padding: 28px 32px; border-radius: 12px; margin-bottom: 20px;
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
}}
header div {{ flex: 1; }}
header h1 {{ font-size: 1.7em; margin-bottom: 4px; }}
header p {{ opacity: 0.85; font-size: 0.92em; }}
.btn-fresh {{
  background: rgba(255,255,255,0.15); color: white; border: 2px solid rgba(255,255,255,0.5);
  padding: 10px 20px; border-radius: 8px; font-size: 0.88em;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
  white-space: nowrap;
}}
.btn-fresh:hover {{ background: rgba(255,255,255,0.25); border-color: white; }}

/* --- Active Step Panel --- */
.active-panel {{
  background: white; border: 2px solid var(--blue); border-radius: 12px;
  padding: 24px 28px; margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(41,128,185,0.15);
  position: sticky; top: 10px; z-index: 100;
}}
.active-panel.no-step {{
  border-color: var(--gray); opacity: 0.7;
  box-shadow: none;
}}
.active-panel-header {{
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; gap: 12px; flex-wrap: wrap;
}}
.active-panel-title {{
  font-size: 0.72em; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: var(--blue);
}}
.active-panel-step {{
  font-size: 1.15em; font-weight: 600; color: var(--dark); margin-bottom: 4px;
}}
.active-panel-phase {{
  font-size: 0.8em; color: var(--gray); margin-bottom: 14px;
}}
.active-panel-prompt {{
  background: #1E1E2E; color: #CDD6F4; font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.84em; padding: 16px 18px; border-radius: 8px;
  white-space: pre-wrap; word-wrap: break-word; line-height: 1.6;
  max-height: 300px; overflow-y: auto; margin-bottom: 14px;
}}
.active-panel-noaction {{
  color: var(--gray); font-size: 0.9em; font-style: italic;
  padding: 12px 0;
}}
.active-panel-actions {{
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
}}
.btn-copy {{
  background: var(--blue); color: white; border: none;
  padding: 10px 22px; border-radius: 7px; font-size: 0.88em;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
}}
.btn-copy:hover {{ background: #2471A3; }}
.btn-copy.copied {{ background: var(--green); }}
.btn-done {{
  background: var(--green); color: white; border: none;
  padding: 10px 22px; border-radius: 7px; font-size: 0.88em;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
}}
.btn-done:hover {{ background: #219A52; }}
.btn-skip {{
  background: transparent; color: var(--gray); border: 1px solid var(--gray);
  padding: 8px 16px; border-radius: 7px; font-size: 0.82em;
  font-weight: 500; cursor: pointer; transition: all 0.2s;
}}
.btn-skip:hover {{ color: var(--orange); border-color: var(--orange); }}
.btn-begin {{
  background: linear-gradient(135deg, var(--blue), #3498DB); color: white; border: none;
  padding: 14px 32px; border-radius: 8px; font-size: 1em;
  font-weight: 700; cursor: pointer; transition: all 0.2s;
  box-shadow: 0 3px 8px rgba(41,128,185,0.3);
}}
.btn-begin:hover {{ transform: translateY(-1px); box-shadow: 0 5px 12px rgba(41,128,185,0.4); }}
.active-panel.ready-state {{ border-color: var(--green); box-shadow: 0 4px 12px rgba(39,174,96,0.15); }}

/* --- Config Panel --- */
.config-panel {{
  background: white; border-radius: 10px; padding: 20px 24px;
  margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.config-panel h2 {{ font-size: 1.1em; margin-bottom: 12px; color: var(--dark); }}
.config-panel.collapsed .config-grid {{ display: none; }}
.config-toggle {{
  float: right; font-size: 0.78em; color: var(--blue);
  cursor: pointer; font-weight: 500;
}}
.config-toggle:hover {{ text-decoration: underline; }}
.config-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}}
.config-field {{ display: flex; flex-direction: column; gap: 3px; }}
.config-field label {{ font-size: 0.78em; font-weight: 600; color: var(--gray); text-transform: uppercase; letter-spacing: 0.3px; }}
.config-field input, .config-field textarea {{
  padding: 8px 12px; border: 1px solid #DDD; border-radius: 6px;
  font-size: 0.9em; font-family: inherit; transition: border-color 0.2s;
}}
.config-field input:focus, .config-field textarea:focus {{ border-color: var(--blue); outline: none; }}
.config-field textarea {{ resize: vertical; min-height: 60px; }}
.config-field-wide {{ grid-column: 1 / -1; }}

/* --- Progress --- */
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
  height: 100%; border-radius: 20px; transition: width 0.4s;
  background: linear-gradient(90deg, var(--green), #2ECC71);
}}
.bar-text {{
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%); font-weight: 600; font-size: 0.8em;
}}

/* --- Step List --- */
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
  border-bottom: 1px solid var(--gray-light); transition: all 0.2s;
  cursor: pointer;
}}
.step-row:hover {{ background: #f0f4f8; }}
.step-row:last-child {{ border-bottom: none; }}
.step-row.done {{ opacity: 0.55; }}
.step-row.done:hover {{ opacity: 0.8; }}
.step-row.current {{
  background: var(--blue-light); border-radius: 6px;
  box-shadow: inset 3px 0 0 var(--blue); font-weight: 600;
}}
.step-check {{
  width: 18px; height: 18px; border-radius: 4px; border: 2px solid var(--gray);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.2s;
}}
.step-check.checked {{ background: var(--green); border-color: var(--green); color: white; font-weight: bold; font-size: 0.7em; }}
.step-name {{ flex: 1; min-width: 0; }}
.step-num {{
  font-size: 0.7em; font-weight: 700; color: var(--gray);
  min-width: 22px; text-align: center;
}}
.tag {{
  font-size: 0.64em; font-weight: 600; padding: 2px 5px;
  border-radius: 3px; white-space: nowrap;
}}
.tag-auto {{ background: var(--blue-light); color: var(--blue); }}
.tag-manual {{ background: var(--orange-light); color: var(--orange); }}
.tag-both {{ background: var(--purple-light); color: var(--purple); }}

/* --- Milestone Cards --- */
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
.timestamp {{ text-align: center; color: var(--gray); font-size: 0.78em; margin-top: 16px; }}

@media (max-width: 700px) {{
  body {{ padding: 10px; }}
  header {{ padding: 18px; }}
  .config-grid {{ grid-template-columns: 1fr; }}
  .step-name {{ min-width: auto; }}
  .active-panel {{ position: static; padding: 16px; }}
}}
</style>
</head>
<body>

<header>
  <div>
    <h1>Workflow Guide</h1>
    <p>AI-Driven Engineering Workflow for MPLAB Harmony Application Development</p>
  </div>
  <button class="btn-fresh" onclick="startFresh()">Start Fresh Project</button>
</header>

<!-- Active Step Execution Panel -->
<div class="active-panel no-step" id="active-panel">
  <div class="active-panel-header">
    <span class="active-panel-title">Current Step</span>
    <span id="active-step-number"></span>
  </div>
  <div class="active-panel-step" id="active-step-name">No step selected — click "Go" on any step below to begin</div>
  <div class="active-panel-phase" id="active-step-phase"></div>
  <div id="active-step-content"></div>
</div>

<div class="config-panel" id="config-panel">
  <h2>Project Configuration <span class="config-toggle" id="config-toggle" onclick="toggleConfig()">Hide</span></h2>
  <div class="config-grid" id="config-grid">
    <div class="config-field">
      <label>Project Name</label>
      <input type="text" id="cfg-project-name" placeholder="e.g., DOSConsole_WBZ451">
    </div>
    <div class="config-field">
      <label>JIRA Project URL</label>
      <input type="text" id="cfg-jira-url" placeholder="e.g., https://jira.microchip.com/projects/PC">
    </div>
    <div class="config-field">
      <label>Assignee Email</label>
      <input type="text" id="cfg-assignee" placeholder="e.g., firstname.lastname@microchip.com">
    </div>
    <div class="config-field">
      <label>Application Branch</label>
      <input type="text" id="cfg-app-branch" placeholder="e.g., dos_console">
    </div>
    <div class="config-field">
      <label>Harmony Project Path (in repo)</label>
      <input type="text" id="cfg-harmony-path" placeholder="e.g., apps/sercom/usart/usart_ring_buffer_interrupt">
    </div>
    <div class="config-field">
      <label>JIRA Epic ID</label>
      <input type="text" id="cfg-epic-id" placeholder="e.g., PC-345 (filled after setup)">
    </div>
    <div class="config-field">
      <label>Bitbucket Repo URL</label>
      <input type="text" id="cfg-repo-url" placeholder="e.g., https://bitbucket.microchip.com/scm/MH3/csp_apps...">
    </div>
    <div class="config-field config-field-wide">
      <label>Initial Prompt (your project request)</label>
      <textarea id="cfg-initial-prompt" placeholder="e.g., Build a DOS command console simulator on the WBZ451 Curiosity board..."></textarea>
    </div>
  </div>
</div>

<div class="overall">
  <h2>Overall Progress</h2>
  <div class="stats-row">
    <div class="stat"><span class="stat-num" id="stat-prereqs">0/13</span><span class="stat-label">Prerequisites</span></div>
    <div class="stat"><span class="stat-num" id="stat-setup">0/16</span><span class="stat-label">Setup Steps</span></div>
    <div class="stat"><span class="stat-num" id="stat-milestones">0/0</span><span class="stat-label">Milestones</span></div>
  </div>
  <div class="bar-outer"><div class="bar-fill" id="progress-bar" style="width:0%"></div>
  <span class="bar-text" id="progress-text">0%</span></div>
</div>

<div class="section-title">Phase 0: Prerequisites</div>
<div class="phase-card" id="phase-prereqs"></div>

<div class="section-title">Phase 1: Repository Setup</div>
<div class="phase-card" id="phase-setup"></div>

<div class="section-title">Phase 2: Milestones</div>
<div id="phase-milestones"></div>

<div class="legend">
  <div class="legend-item"><span class="tag tag-auto">[AUTO]</span> Claude automated</div>
  <div class="legend-item"><span class="tag tag-manual">[MANUAL]</span> Engineer action</div>
  <div class="legend-item"><span class="tag tag-both">[AUTO+MANUAL]</span> Combined</div>
</div>

<p class="timestamp">Generated by generate_workflow.py &mdash; {timestamp}</p>

<script>
const PROJECT_DATA = {project_data_json};
const MILESTONES_DATA = {milestones_json};
const PROGRESS_DATA = {progress_json};

// --- Step Registry (built during render) ---
const STEPS = [];

// --- Helpers ---
function getVal(id) {{ return document.getElementById(id).value.trim(); }}
function setVal(id, v) {{ document.getElementById(id).value = v || ''; }}
function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

function getStorageKey() {{
  return 'workflow_' + (getVal('cfg-project-name') || 'default');
}}
function loadChecks() {{
  try {{ return JSON.parse(localStorage.getItem(getStorageKey())) || {{}}; }} catch(e) {{ return {{}}; }}
}}
function saveCheck(stepId, checked) {{
  const data = loadChecks();
  data[stepId] = checked;
  localStorage.setItem(getStorageKey(), JSON.stringify(data));
}}
function getActiveStep() {{
  return localStorage.getItem(getStorageKey() + '_active') || '';
}}
function setActiveStep(stepId) {{
  localStorage.setItem(getStorageKey() + '_active', stepId);
}}

function toggleConfig() {{
  const panel = document.getElementById('config-panel');
  const toggle = document.getElementById('config-toggle');
  const grid = document.getElementById('config-grid');
  if (grid.style.display === 'none') {{
    grid.style.display = ''; toggle.textContent = 'Hide';
  }} else {{
    grid.style.display = 'none'; toggle.textContent = 'Show';
  }}
}}

function startFresh() {{
  if (!confirm('Start a fresh project?\\n\\nThis will clear all input fields and reset all progress checkboxes.\\n\\nYour previous progress (if any) remains saved under its project name in localStorage.')) return;
  // Clear all input fields
  document.querySelectorAll('.config-field input, .config-field textarea').forEach(el => {{ el.value = ''; }});
  // Show config panel if hidden
  const grid = document.getElementById('config-grid');
  grid.style.display = '';
  document.getElementById('config-toggle').textContent = 'Hide';
  // Clear active step and checks for the (now empty) project key
  const key = getStorageKey();
  localStorage.removeItem(key);
  localStorage.removeItem(key + '_active');
  localStorage.removeItem('workflow_config_default');
  // Re-render everything
  renderAll();
  // Scroll to top so user sees config panel
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function copyPanelPrompt() {{
  const el = document.getElementById('active-prompt-text');
  if (!el) return;
  const text = el.textContent;
  const btn = document.getElementById('btn-panel-copy');
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(text).then(() => {{
      btn.textContent = 'Copied!'; btn.classList.add('copied');
      setTimeout(() => {{ btn.textContent = 'Copy Prompt'; btn.classList.remove('copied'); }}, 2000);
    }});
  }} else {{
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
    document.body.appendChild(ta); ta.select();
    try {{ document.execCommand('copy'); btn.textContent = 'Copied!'; btn.classList.add('copied');
      setTimeout(() => {{ btn.textContent = 'Copy Prompt'; btn.classList.remove('copied'); }}, 2000);
    }} catch(e) {{ btn.textContent = 'Failed'; }}
    document.body.removeChild(ta);
  }}
}}

// --- Prompt Templates ---
function getPrompts() {{
  const p = getVal('cfg-project-name');
  const ju = getVal('cfg-jira-url');
  const as = getVal('cfg-assignee');
  const ab = getVal('cfg-app-branch');
  const ep = getVal('cfg-epic-id');
  const ru = getVal('cfg-repo-url');
  const ip = getVal('cfg-initial-prompt');
  const hp = getVal('cfg-harmony-path');
  return {{
    setup_harmony: `Identify the target MPLAB Harmony project within the repository.\\nHarmony project path (inside repo): ${{hp}}\\n\\nVerify that:\\n1. The path exists and contains a configured Harmony/MCC project\\n2. Generated Harmony source files are present (src/config/, src/packs/, initialization files)\\n3. The CMakeLists.txt or build configuration references the correct device\\n\\nRecord the Harmony project path in CLAUDE.md.`,
    setup_initial: `I want to create a new MPLAB Harmony application project following the AI-Driven Engineering Workflow.\\n\\nHere is my request:\\n${{ip}}\\n\\nRepository: ${{ru}}\\nHarmony project location (inside repo): ${{hp}}\\nJIRA project: ${{ju}}\\nAssignee: ${{as}}\\nApplication branch name: ${{ab}}\\n\\nFollow the workflow in ApplicationWorkflowTemplate.md to set up the project:\\n1. Clone the repository and verify the baseline build\\n2. Create CLAUDE.md from TEMPLATE_CLAUDE.md with all project details\\n3. Create MILESTONES.md from TEMPLATE_MILESTONES.md with milestone breakdown\\n4. Create the application branch '${{ab}}'\\n5. Copy workflow scaffolding (CODE_REVIEW_CHECKLIST.md, docs directories)\\n6. Create project README.md\\n7. Run python generate_workflow.py`,
    setup_epic: `Create a JIRA Epic for this project in JIRA project: ${{ju}}\\nSummary: "${{p}} — Application Development"\\nDescription: Application development using AI-Driven Engineering Workflow.\\nAssignee: ${{as}}\\n\\nRecord the returned Epic ID in CLAUDE.md under JIRA Configuration as JIRA Epic ID.\\nThen run python generate_workflow.py to update the workflow guide.`,
    setup_commit: `All repository setup is complete. Commit the setup files to the application branch '${{ab}}' and push to the remote.\\nCommit message: "Repository setup: workflow files and project configuration"\\nFiles to commit: CLAUDE.md, MILESTONES.md, CODE_REVIEW_CHECKLIST.md, docs/ directories, MODULE.md stubs, generate_workflow.py, README.md\\nThen run python generate_workflow.py.`,
  }};
}}

function getMilestonePrompts(ms) {{
  const p = getVal('cfg-project-name');
  const ju = getVal('cfg-jira-url');
  const as = getVal('cfg-assignee');
  const ab = getVal('cfg-app-branch');
  const ep = getVal('cfg-epic-id');
  const n = ms.number;
  const title = ms.title;
  const jid = ms.jira_id || '???';
  const branch = `${{p.replace(/\\s+/g, '')}}_module_${{jid}}`;
  const reqs = (ms.requirements || []).map(r => `  - ${{r.id}}: ${{r.text}}`).join('\\n') || '  (see MILESTONES.md)';
  return {{
    dor: `Start the Definition of Ready for Milestone ${{n}}: ${{title}}.\\nFollow the workflow in ApplicationWorkflowTemplate.md.\\n\\n1. Verify the previous milestone is Done (check JIRA).\\n2. Create a JIRA ticket in the JIRA project (${{ju}}) with:\\n   - Summary: "Milestone ${{n}}: ${{title}}"\\n   - Assignee: ${{as}}\\n   - Description: milestone objective and requirements from MILESTONES.md\\n3. Link the ticket to Epic ${{ep}} using jira_link_to_epic.\\n4. Record the JIRA ID in MILESTONES.md and CLAUDE.md Active Milestone.\\n5. Wait for my requirements sign-off before proceeding.`,
    signoff: `Requirements for Milestone ${{n}} [${{jid}}]: ${{title}} are signed off.\\nProceed with Definition of Ready:\\n1. Confirm MODULE.md stubs exist for all modules this milestone touches.\\n2. Create the milestone branch from '${{ab}}':\\n   Branch name: ${{branch}}\\n3. Update CLAUDE.md Active Milestone with JIRA ID and branch name.\\n4. Transition JIRA ${{jid}} to In Progress.\\n5. Run python generate_workflow.py to update the workflow guide.`,
    implementation: `Continue implementing Milestone ${{n}} [${{jid}}]: ${{title}}\\nBranch: ${{branch}}\\n\\nRequirements:\\n${{reqs}}\\n\\nFollow the workflow in ApplicationWorkflowTemplate.md.\\nImplement all requirements on the milestone branch.\\nRegister any new source files in user.cmake.\\nWhen implementation is complete, tell me so I can run the build.`,
    build: `Implementation for Milestone ${{n}} [${{jid}}] is complete.\\nI will now run the build via VS Code CMake: Build.\\nThe build must pass with zero errors and zero warnings.\\n\\n[After running build, report result to Claude]`,
    review: `Build passed with zero errors and zero warnings for Milestone ${{n}} [${{jid}}]: ${{title}}.\\nRun the code review checklist (CODE_REVIEW_CHECKLIST.md).\\nSave the review report to docs/reviews/REVIEW_M${{n}}.md.\\nAll checklist items must pass before proceeding to commit.`,
    commit: `Code review passed for Milestone ${{n}} [${{jid}}]: ${{title}}.\\nCreate the single milestone commit on branch ${{branch}}:\\n  Commit message: "Milestone ${{n}} [${{jid}}]: ${{title}}"\\nInclude all implementation code, documentation updates, and the review report.\\nPush to the remote branch.`,
    testing: `Commit is done for Milestone ${{n}} [${{jid}}]: ${{title}}.\\nCreate the test report: docs/tests/TEST_M${{n}}.md\\nUse TEMPLATE_TESTING.md and cover all 5 dimensions:\\n  1. Requirements Verification (each R1, R2... from MILESTONES.md)\\n  2. Module Functionality (per MODULE.md interfaces)\\n  3. Use Cases (per README.md)\\n  4. Data Flow (module boundaries)\\n  5. AI Code Verification (hallucinated APIs, boundary logic, copy-paste, resources)\\n\\nZero failed tests required. If any test fails, follow the waterfall re-cycle procedure.`,
    jira_in_progress: `Transition JIRA ticket ${{jid}} to In Progress.\\nThe Definition of Ready is now satisfied for Milestone ${{n}}: ${{title}}.\\nUse jira_transition_issue to move the ticket from To Do to In Progress.\\nThen run python generate_workflow.py to update the workflow guide.`,
    amend: `Milestone testing passed for Milestone ${{n}} [${{jid}}]: ${{title}}.\\nAmend the milestone commit to include the test report:\\n  git add docs/tests/TEST_M${{n}}.md\\n  git commit --amend --no-edit\\n  git push --force-with-lease\\n\\nThis keeps the single-commit rule intact.`,
    pr: `All tests pass for Milestone ${{n}} [${{jid}}]: ${{title}}.\\nCreate a Pull Request from ${{branch}} to ${{ab}}.\\nPost code review findings as inline PR comments.\\nWait for my approval before merging.`,
    merge: `PR is approved for Milestone ${{n}} [${{jid}}]: ${{title}}.\\nMerge the PR into ${{ab}} via Bitbucket MCP (merge_pull_request).`,
    jira_done: `PR merged for Milestone ${{n}} [${{jid}}]: ${{title}}.\\n1. Transition JIRA ${{jid}} to Done via jira_transition_issue.\\n2. Add the PR link to the JIRA ticket via jira_create_remote_issue_link.\\n3. Update CLAUDE.md Active Milestone to the next milestone (or mark project complete).`,
  }};
}}

// --- Rendering ---
let stepCounter = 0;

function registerStep(id, name, tag, prompt, phase) {{
  STEPS.push({{ id, name, tag, prompt, phase }});
}}

function renderStep(id, name, tag, promptKey, preChecked) {{
  stepCounter++;
  const checks = loadChecks();
  const isChecked = checks[id] !== undefined ? checks[id] : preChecked;
  const activeId = getActiveStep();
  const isActive = activeId === id;
  const tagCls = tag.includes('+') ? 'tag-both' : tag === 'MANUAL' ? 'tag-manual' : 'tag-auto';

  let html = `<div class="step-row ${{isChecked ? 'done' : ''}} ${{isActive ? 'current' : ''}}" id="row-${{id}}" onclick="goStep('${{id}}')">`;
  html += `<span class="step-num">${{stepCounter}}</span>`;
  html += `<div class="step-check ${{isChecked ? 'checked' : ''}}" data-id="${{id}}" onclick="event.stopPropagation(); toggleCheck(this)">${{isChecked ? '\\u2713' : ''}}</div>`;
  html += `<span class="step-name">${{esc(name)}}</span>`;
  html += `<span class="tag ${{tagCls}}">[${{tag}}]</span>`;
  html += `</div>`;
  return html;
}}

function goStep(stepId) {{
  setActiveStep(stepId);
  renderActivePanel();
  highlightCurrent();
  // Scroll the step row into view in the list
  const row = document.getElementById('row-' + stepId);
  if (row) row.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
}}

function markDone() {{
  const activeId = getActiveStep();
  if (!activeId) return;
  saveCheck(activeId, true);
  // Advance to next unchecked step
  const idx = STEPS.findIndex(s => s.id === activeId);
  let nextId = '';
  for (let i = idx + 1; i < STEPS.length; i++) {{
    const checks = loadChecks();
    if (!checks[STEPS[i].id]) {{ nextId = STEPS[i].id; break; }}
  }}
  setActiveStep(nextId);
  renderAll();
}}

function skipStep() {{
  const activeId = getActiveStep();
  if (!activeId) return;
  const idx = STEPS.findIndex(s => s.id === activeId);
  let nextId = '';
  for (let i = idx + 1; i < STEPS.length; i++) {{
    const checks = loadChecks();
    if (!checks[STEPS[i].id]) {{ nextId = STEPS[i].id; break; }}
  }}
  setActiveStep(nextId);
  renderActivePanel();
  highlightCurrent();
}}

function getStepPrompt(stepId) {{
  const step = STEPS.find(s => s.id === stepId);
  if (!step || !step.prompt) return '';
  return step.prompt;
}}

function isConfigEmpty() {{
  return !getVal('cfg-project-name') && !getVal('cfg-repo-url');
}}

function beginWorkflow() {{
  const name = getVal('cfg-project-name');
  if (!name) {{
    alert('Please fill in at least the Project Name before starting.');
    document.getElementById('cfg-project-name').focus();
    return;
  }}
  // Save config
  const cfg = {{}};
  document.querySelectorAll('.config-field input, .config-field textarea').forEach(f => {{ cfg[f.id] = f.value; }});
  localStorage.setItem('workflow_config_' + (name || 'default'), JSON.stringify(cfg));
  // Set first unchecked step as active
  const checks = loadChecks();
  const first = STEPS.find(s => !checks[s.id]);
  if (first) {{
    setActiveStep(first.id);
    renderAll();
    // Collapse config panel to focus on execution
    document.getElementById('config-grid').style.display = 'none';
    document.getElementById('config-toggle').textContent = 'Show';
  }}
}}

function renderActivePanel() {{
  const panel = document.getElementById('active-panel');
  const activeId = getActiveStep();

  // State 1: No config filled — prompt user to fill in details
  if (!activeId && isConfigEmpty()) {{
    panel.classList.add('no-step');
    panel.classList.remove('ready-state');
    document.getElementById('active-step-name').textContent = 'Welcome! Fill in your project details above to get started.';
    document.getElementById('active-step-phase').textContent = 'Enter at least the Project Name, then click the button below.';
    document.getElementById('active-step-number').textContent = '';
    document.getElementById('active-step-content').innerHTML =
      `<div class="active-panel-actions"><button class="btn-begin" onclick="beginWorkflow()">\\u25B6 Begin Workflow</button></div>`;
    return;
  }}

  // State 2: Config filled but no active step — offer to begin
  if (!activeId && !isConfigEmpty()) {{
    panel.classList.remove('no-step');
    panel.classList.add('ready-state');
    document.getElementById('active-step-name').textContent = 'Ready to begin: ' + getVal('cfg-project-name');
    document.getElementById('active-step-phase').textContent = 'Configuration complete. Click below to start at Step 1 (Prerequisites).';
    document.getElementById('active-step-number').textContent = STEPS.length + ' steps total';
    document.getElementById('active-step-content').innerHTML =
      `<div class="active-panel-actions"><button class="btn-begin" onclick="beginWorkflow()">\\u25B6 Begin Workflow</button></div>`;
    return;
  }}

  // State 3: Active step selected — show execution UI
  panel.classList.remove('no-step');
  panel.classList.remove('ready-state');
  const step = STEPS.find(s => s.id === activeId);
  if (!step) return;

  const idx = STEPS.indexOf(step);
  document.getElementById('active-step-number').textContent = 'Step ' + (idx + 1) + ' of ' + STEPS.length;
  document.getElementById('active-step-name').textContent = step.name;
  document.getElementById('active-step-phase').textContent = step.phase;

  const prompt = step.prompt;
  let content = '';
  if (prompt) {{
    content += `<div class="active-panel-prompt" id="active-prompt-text">${{esc(prompt)}}</div>`;
    content += `<div class="active-panel-actions">`;
    content += `<button class="btn-copy" id="btn-panel-copy" onclick="copyPanelPrompt()">Copy Prompt</button>`;
    content += `<button class="btn-done" onclick="markDone()">\\u2713 Done &amp; Next</button>`;
    content += `<button class="btn-skip" onclick="skipStep()">Skip \\u2192</button>`;
    content += `</div>`;
  }} else {{
    content += `<div class="active-panel-noaction">This is a manual step \\u2014 complete it, then click Done.</div>`;
    content += `<div class="active-panel-actions">`;
    content += `<button class="btn-done" onclick="markDone()">\\u2713 Done &amp; Next</button>`;
    content += `<button class="btn-skip" onclick="skipStep()">Skip \\u2192</button>`;
    content += `</div>`;
  }}
  document.getElementById('active-step-content').innerHTML = content;
}}

function toggleCheck(el) {{
  const id = el.dataset.id;
  const checks = loadChecks();
  const isChecked = !checks[id];
  saveCheck(id, isChecked);
  if (isChecked && getActiveStep() === id) {{
    const idx = STEPS.findIndex(s => s.id === id);
    let nextId = '';
    for (let i = idx + 1; i < STEPS.length; i++) {{
      if (!loadChecks()[STEPS[i].id]) {{ nextId = STEPS[i].id; break; }}
    }}
    setActiveStep(nextId);
  }}
  renderAll();
}}

function renderPrereqs() {{
  const container = document.getElementById('phase-prereqs');
  const pre = PROGRESS_DATA.prereqs || {{}};
  const items = [
    ['prereq-repo', 'Bitbucket repository exists', 'AUTO', '', pre.repo_exists],
    ['prereq-git', 'Git installed & configured', 'AUTO', '', pre.git_configured],
    ['prereq-bb-access', 'Bitbucket access (read/write)', 'AUTO', '', pre.bitbucket_access],
    ['prereq-jira', 'JIRA access', 'AUTO', '', pre.jira_access],
    ['prereq-jira-recorded', 'JIRA project key & URL recorded', 'AUTO', '', pre.jira_recorded],
    ['prereq-assignee', 'JIRA assignee email recorded', 'AUTO', '', pre.jira_assignee],
    ['prereq-harmony', 'Harmony project location identified', 'AUTO', '', pre.harmony_path],
    ['prereq-ai', 'AI tool access (Claude)', 'AUTO', '', pre.ai_tool],
    ['prereq-build', 'Build environment configured', 'AUTO', '', pre.build_env],
    ['prereq-mcp-bb', 'Bitbucket MCP login verified', 'AUTO', '', pre.mcp_bitbucket],
    ['prereq-mcp-jira', 'JIRA MCP login verified', 'AUTO', '', pre.mcp_jira],
    ['prereq-scope', 'Scope confirmed: application layer only (no MCC changes)', 'MANUAL', '', false],
    ['prereq-single', 'Single engineer, single task, one week confirmed', 'MANUAL', '', false],
  ];
  items.forEach(i => registerStep(i[0], i[1], i[2], i[3], 'Phase 0: Prerequisites'));
  container.innerHTML = '<h3>Prerequisites (' + items.filter(i => loadChecks()[i[0]] || i[4]).length + '/' + items.length + ' verified)</h3>'
    + items.map(i => renderStep(i[0], i[1], i[2], i[3], i[4])).join('');
}}

function renderSetup() {{
  const container = document.getElementById('phase-setup');
  const s = PROGRESS_DATA.setup || {{}};
  const prompts = getPrompts();
  const items = [
    ['setup-clone', 'Clone repository locally', 'AUTO', '', s.repo_cloned],
    ['setup-branch-default', 'Check out default branch', 'AUTO', '', s.default_branch],
    ['setup-git-creds', 'Git credentials verified (non-interactive)', 'AUTO', '', s.git_creds],
    ['setup-harmony', 'Identify target Harmony project', 'AUTO', prompts.setup_harmony, s.harmony_identified],
    ['setup-build', 'Verify baseline build (VS Code CMake)', 'MANUAL', '', s.baseline_build],
    ['setup-initial', 'Create CLAUDE.md + MILESTONES.md + app branch', 'AUTO', prompts.setup_initial, s.claude_md],
    ['setup-app-branch', 'Application branch created', 'AUTO', '', s.app_branch],
    ['setup-owner', 'Repository owner assigned', 'AUTO', '', s.owner_assigned],
    ['setup-checklist', 'CODE_REVIEW_CHECKLIST.md copied', 'AUTO', '', s.code_review_checklist],
    ['setup-dirs', 'Workflow directories created', 'AUTO', '', s.workflow_dirs],
    ['setup-modules', 'Module directories with MODULE.md', 'AUTO', '', s.module_dirs],
    ['setup-readme', 'Project README.md updated', 'AUTO', '', s.readme],
    ['setup-mcp-verify', 'MCP verification run (.mcp_verified.json)', 'AUTO', '', s.mcp_verified],
    ['setup-workflow-html', 'Workflow.html generated (generate_workflow.py)', 'AUTO', '', s.workflow_html],
    ['setup-epic', 'JIRA Epic created and recorded', 'AUTO', prompts.setup_epic, s.jira_epic],
    ['setup-commit', 'Setup files committed and pushed', 'AUTO', prompts.setup_commit, false],
  ];
  items.forEach(i => registerStep(i[0], i[1], i[2], i[3], 'Phase 1: Repository Setup'));
  container.innerHTML = '<h3>Repository Setup (' + items.filter(i => loadChecks()[i[0]] || i[4]).length + '/' + items.length + ' complete)</h3>'
    + items.map(i => renderStep(i[0], i[1], i[2], i[3], i[4])).join('');
}}

function renderMilestones() {{
  const container = document.getElementById('phase-milestones');
  if (!MILESTONES_DATA || MILESTONES_DATA.length === 0) {{
    container.innerHTML = '<div class="no-milestones"><p>No milestones found.</p><p>Create <code>MILESTONES.md</code> using TEMPLATE_MILESTONES.md, then re-run <code>python generate_workflow.py</code> to populate this section.</p></div>';
    return;
  }}

  let html = '';
  MILESTONES_DATA.forEach((ms, idx) => {{
    const prog = (PROGRESS_DATA.milestones || [])[idx] || {{}};
    const prompts = getMilestonePrompts(ms);
    const isComplete = ms.status === 'complete';
    const isActive = prog.is_active;
    const cardCls = isComplete ? 'complete' : isActive ? 'active' : '';
    const badgeCls = isComplete ? 'badge-complete' : isActive ? 'badge-progress' : 'badge-pending';
    const badgeText = isComplete ? 'Complete' : isActive ? 'In Progress' : 'Not Started';
    const phase = `Milestone ${{ms.number}}: ${{ms.title}}`;

    html += `<div class="ms-card ${{cardCls}}">`;
    html += `<div class="ms-header"><h3>Milestone ${{ms.number}}: ${{esc(ms.title)}}${{ms.jira_id ? ' \\u2014 ' + esc(ms.jira_id) : ''}}</h3>`;
    html += `<span class="badge ${{badgeCls}}">${{badgeText}}</span></div>`;

    if (ms.requirements && ms.requirements.length > 0) {{
      html += `<details class="requirements"><summary>Requirements (${{ms.requirements.length}})</summary><ul>`;
      ms.requirements.forEach(r => {{ html += `<li>${{esc(r.id)}}: ${{esc(r.text)}}</li>`; }});
      html += `</ul></details>`;
    }}

    const pre = 'm' + ms.number + '-';
    const dorSteps = [
      [pre+'prev', 'Previous milestone complete (JIRA query)', 'AUTO', '', ms.number === 1 || prog.prev_done],
      [pre+'reqs-written', 'Requirements written in MILESTONES.md', 'MANUAL', '', ms.requirements && ms.requirements.length > 0],
      [pre+'jira', 'JIRA ticket created & linked to epic', 'AUTO', prompts.dor, prog.has_jira],
      [pre+'signoff', 'Requirements signed off on JIRA', 'MANUAL', '', prog.signed_off],
      [pre+'stubs', 'MODULE.md stubs exist & reviewed', 'MANUAL', '', prog.signed_off],
      [pre+'branch', 'Milestone branch created', 'AUTO', prompts.signoff, prog.branch_exists],
      [pre+'context', 'AI context loaded (CLAUDE.md updated)', 'AUTO', '', prog.branch_exists],
      [pre+'jira-progress', 'JIRA ticket \\u2192 In Progress', 'AUTO', prompts.jira_in_progress, prog.branch_exists],
    ];
    const implSteps = [
      [pre+'acceptance', 'Acceptance criteria verified', 'MANUAL', '', prog.review_exists],
      [pre+'impl', 'Implementation on milestone branch', 'AUTO', prompts.implementation, prog.review_exists],
      [pre+'build', 'Build passed (zero errors/warnings)', 'MANUAL', prompts.build, prog.review_exists],
      [pre+'review', 'Code review checklist passed', 'AUTO', prompts.review, prog.review_exists],
      [pre+'docs', 'Documentation updated (MODULE.md + README)', 'AUTO', '', prog.review_exists],
      [pre+'commit', 'Single milestone commit made & pushed', 'AUTO', prompts.commit, prog.test_exists],
    ];
    const testSteps = [
      [pre+'test', 'Milestone testing (5 dimensions)', 'MANUAL', prompts.testing, prog.test_exists],
      [pre+'amend', 'Commit amended with test report', 'AUTO', prompts.amend, prog.test_exists],
    ];
    const finalSteps = [
      [pre+'pr', 'PR created & code review posted', 'AUTO', prompts.pr, prog.is_complete],
      [pre+'approve', 'Engineer approved PR', 'MANUAL', '', prog.is_complete],
      [pre+'merge', 'PR merged into application branch', 'AUTO', prompts.merge, prog.is_complete],
      [pre+'jira-done', 'JIRA \\u2192 Done + PR link added', 'AUTO', prompts.jira_done, prog.is_complete],
      [pre+'regen', 'Workflow.html regenerated', 'AUTO', '', prog.is_complete],
    ];

    const allMsSteps = [...dorSteps, ...implSteps, ...testSteps, ...finalSteps];
    allMsSteps.forEach(i => registerStep(i[0], i[1], i[2], i[3], phase));

    html += `<div class="sub-phase-title">Definition of Ready</div>`;
    html += dorSteps.map(i => renderStep(i[0], i[1], i[2], i[3], i[4])).join('');
    html += `<div class="sub-phase-title">Implementation & Gates</div>`;
    html += implSteps.map(i => renderStep(i[0], i[1], i[2], i[3], i[4])).join('');
    html += `<div class="sub-phase-title">Testing</div>`;
    html += testSteps.map(i => renderStep(i[0], i[1], i[2], i[3], i[4])).join('');
    html += `<div class="sub-phase-title">Finalization</div>`;
    html += finalSteps.map(i => renderStep(i[0], i[1], i[2], i[3], i[4])).join('');

    html += `</div>`;
  }});
  container.innerHTML = html;
}}

function updateProgress() {{
  const allSteps = document.querySelectorAll('.step-check');
  const total = allSteps.length;
  const done = Array.from(allSteps).filter(el => el.classList.contains('checked')).length;
  const pct = total > 0 ? Math.round(done / total * 100) : 0;
  document.getElementById('progress-bar').style.width = pct + '%';
  document.getElementById('progress-text').textContent = done + '/' + total + ' (' + pct + '%)';

  const preSteps = document.querySelectorAll('#phase-prereqs .step-check');
  const preDone = Array.from(preSteps).filter(el => el.classList.contains('checked')).length;
  document.getElementById('stat-prereqs').textContent = preDone + '/' + preSteps.length;

  const setupSteps = document.querySelectorAll('#phase-setup .step-check');
  const setupDone = Array.from(setupSteps).filter(el => el.classList.contains('checked')).length;
  document.getElementById('stat-setup').textContent = setupDone + '/' + setupSteps.length;

  const msComplete = MILESTONES_DATA.filter(m => m.status === 'complete').length;
  document.getElementById('stat-milestones').textContent = msComplete + '/' + MILESTONES_DATA.length;
}}

function highlightCurrent() {{
  document.querySelectorAll('.step-row.current').forEach(el => el.classList.remove('current'));
  const activeId = getActiveStep();
  if (activeId) {{
    const row = document.getElementById('row-' + activeId);
    if (row) row.classList.add('current');
  }}
}}

function renderAll() {{
  stepCounter = 0;
  STEPS.length = 0;
  renderPrereqs();
  renderSetup();
  renderMilestones();
  updateProgress();
  renderActivePanel();
  highlightCurrent();
}}

// --- Init ---
function init() {{
  if (PROJECT_DATA.project_name) setVal('cfg-project-name', PROJECT_DATA.project_name);
  if (PROJECT_DATA.jira_project_url) setVal('cfg-jira-url', PROJECT_DATA.jira_project_url);
  if (PROJECT_DATA.jira_assignee_email) setVal('cfg-assignee', PROJECT_DATA.jira_assignee_email);
  if (PROJECT_DATA.application_branch) setVal('cfg-app-branch', PROJECT_DATA.application_branch);
  if (PROJECT_DATA.harmony_project_path) setVal('cfg-harmony-path', PROJECT_DATA.harmony_project_path);
  if (PROJECT_DATA.jira_epic_id) setVal('cfg-epic-id', PROJECT_DATA.jira_epic_id);
  if (PROJECT_DATA.initial_prompt) setVal('cfg-initial-prompt', PROJECT_DATA.initial_prompt);

  const savedConfig = localStorage.getItem('workflow_config_' + (PROJECT_DATA.project_name || 'default'));
  if (savedConfig) {{
    try {{
      const cfg = JSON.parse(savedConfig);
      Object.keys(cfg).forEach(k => {{ if (cfg[k] && !getVal(k)) setVal(k, cfg[k]); }});
    }} catch(e) {{}}
  }}

  renderAll();

  // Re-render when config inputs change
  document.querySelectorAll('.config-field input, .config-field textarea').forEach(el => {{
    el.addEventListener('input', () => {{
      const cfg = {{}};
      document.querySelectorAll('.config-field input, .config-field textarea').forEach(f => {{ cfg[f.id] = f.value; }});
      localStorage.setItem('workflow_config_' + (getVal('cfg-project-name') || 'default'), JSON.stringify(cfg));
      renderAll();
    }});
  }});
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
    print("Open Workflow.html in a browser to use the interactive workflow guide.")


if __name__ == "__main__":
    main()
