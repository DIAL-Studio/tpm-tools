#!/usr/bin/env python3
"""pm-agent-harness-kit MCP server and CLI — Phase 5 harness infrastructure.

Requires: Python >= 3.8 (stdlib only: sqlite3, json, sys, os, argparse, datetime, pathlib)
          3.12+ recommended.

Usage:
  pm-ahk init [--scope global|project]   Interactive harness setup
  pm-ahk serve                            Start MCP server (stdio JSON-RPC)
  pm-ahk serve-http [--port 5431]          Start MCP server (HTTP — requires flask)
  pm-ahk status                           Show initiative backlog
  pm-ahk initiative add                   Interactively add to backlog
  pm-ahk initiative list [--status <s>]   List initiatives
  pm-ahk initiative done <id|slug>        Mark initiative as done
"""

from __future__ import annotations

import argparse
import datetime
import http.server
import json
import os
import select
import sqlite3
import socketserver
import sys
import textwrap
import webbrowser
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

VERSION = "2.0.0"
REPO_OWNER = "DIAL-Studio"
REPO_NAME = "pm-agent-harness-kit"
REMOTE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main"
COLUMNS = 80

# ── Colors ───────────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"


def green(s): return f"{GREEN}{s}{RESET}"
def cyan(s): return f"{CYAN}{s}{RESET}"
def yellow(s): return f"{YELLOW}{s}{RESET}"
def red(s): return f"{RED}{s}{RESET}"
def bold(s): return f"{BOLD}{s}{RESET}"
def dim(s): return f"{DIM}{s}{RESET}"
def magenta(s): return f"{MAGENTA}{s}{RESET}"


# ── Docs path helper ─────────────────────────────────────────────────────────

def docs_dir() -> Path:
    """Resolve the PM docs directory (global or repo)."""
    base = Path(__file__).resolve().parent
    # Installed in ~/.config/opencode/
    installed = base / "pm-ahk-docs"
    if installed.exists():
        return installed
    # Installed in ~/.claude/ or similar
    if base.parent.name != "opencode" and base.parent.name != "skls":
        return installed
    # Repo root fallback
    repo = base.parent / "pm-ahk-docs"
    if not repo.exists():
        repo.mkdir(parents=True, exist_ok=True)
    return repo


# ── DB Path resolution ───────────────────────────────────────────────────────

def resolve_db_path(scope: str = "global", cwd: str | None = None) -> Path:
    """Resolve .harness/ path based on scope."""
    cwd = cwd or os.getcwd()
    if scope == "project":
        base = Path(cwd)
    else:
        base = Path.home() / ".config" / "opencode"
    harness_dir = base / ".harness"
    harness_dir.mkdir(parents=True, exist_ok=True)
    return harness_dir / "harness.db"


# ── DB helpers ───────────────────────────────────────────────────────────────

INIT_SQL = """
CREATE TABLE IF NOT EXISTS initiatives (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK(status IN ('pending','discovery','strategy','spec','review','approved','blocked','done')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  archived_at TEXT
);

CREATE TABLE IF NOT EXISTS actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  initiative_id INTEGER NOT NULL,
  agent TEXT NOT NULL,
  action_type TEXT NOT NULL,
  content TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'in_progress'
    CHECK(status IN ('in_progress','completed')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at TEXT,
  summary TEXT,
  FOREIGN KEY (initiative_id) REFERENCES initiatives(id)
);

CREATE TABLE IF NOT EXISTS action_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action_id INTEGER NOT NULL,
  file_path TEXT NOT NULL,
  operation TEXT NOT NULL CHECK(operation IN ('read','created','modified','deleted')),
  notes TEXT,
  FOREIGN KEY (action_id) REFERENCES actions(id)
);

CREATE TABLE IF NOT EXISTS action_tools (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action_id INTEGER NOT NULL,
  tool_name TEXT NOT NULL,
  args_json TEXT,
  result_summary TEXT,
  called_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (action_id) REFERENCES actions(id)
);

CREATE TABLE IF NOT EXISTS criteria (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  initiative_id INTEGER NOT NULL,
  criterion TEXT NOT NULL,
  met INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (initiative_id) REFERENCES initiatives(id)
);
"""


def migrate_schema(conn: sqlite3.Connection) -> None:
    """Add missing columns/tables to existing databases (safe idempotent)."""
    cur = conn.cursor()
    # Actions table evolution
    for col, typ in [("status", "TEXT NOT NULL DEFAULT 'completed'"),
                     ("completed_at", "TEXT"),
                     ("summary", "TEXT")]:
        try:
            cur.execute(f"ALTER TABLE actions ADD COLUMN {col} {typ}")
        except sqlite3.OperationalError:
            pass
    # Initiatives: archived_at
    try:
        cur.execute("ALTER TABLE initiatives ADD COLUMN archived_at TEXT")
    except sqlite3.OperationalError:
        pass
    # New tables (CREATE IF NOT EXISTS — safe for all DBs)
    cur.execute("""CREATE TABLE IF NOT EXISTS action_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        operation TEXT NOT NULL CHECK(operation IN ('read','created','modified','deleted')),
        notes TEXT,
        FOREIGN KEY (action_id) REFERENCES actions(id))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS action_tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_id INTEGER NOT NULL,
        tool_name TEXT NOT NULL,
        args_json TEXT,
        result_summary TEXT,
        called_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (action_id) REFERENCES actions(id))""")
    # Backfill status on existing actions
    try:
        cur.execute("UPDATE actions SET status = 'completed' WHERE status IS NULL OR status NOT IN ('in_progress','completed')")
    except sqlite3.OperationalError:
        pass
    conn.commit()

STATUS_FLOW = ["pending", "discovery", "strategy", "spec", "review", "approved", "blocked", "done"]


def get_conn(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str | Path) -> None:
    conn = get_conn(db_path)
    conn.executescript(INIT_SQL)
    conn.commit()
    conn.close()


# ── MCP Protocol (JSON-RPC over stdio, binary I/O) ───────────────────────────

def _read_fd(n: int = 1) -> bytes | None:
    """Read n bytes from stdin, handling EAGAIN/EWOULDBLOCK."""
    while True:
        try:
            data = os.read(0, n)
            return data
        except BlockingIOError:
            select.select([0], [], [], 0.1)
        except OSError:
            return None


def mcp_read() -> dict | None:
    """Read a JSON-RPC message from stdin (via os.read for unbuffered I/O)."""
    try:
        header = b""
        while True:
            ch = _read_fd()
            if ch is None or ch == b"":
                return None
            if ch in (b"\r", b"\n"):
                if ch == b"\r":
                    _read_fd()
                break
            header += ch

        if not header.startswith(b"Content-Length:"):
            return None

        length = int(header.split(b":")[1].strip())
        # Consume blank line
        blank = _read_fd()
        if blank is None:
            return None
        if blank == b"\r":
            _read_fd()
        # Read exactly N bytes
        body = b""
        while len(body) < length:
            chunk = _read_fd(length - len(body))
            if chunk is None or chunk == b"":
                return None
            body += chunk

        return json.loads(body.decode("utf-8"))
    except Exception as exc:
        sys.stderr.write(f"[pm-ahk] mcp_read error: {exc}\n")
        sys.stderr.flush()
        return None


def mcp_send(obj: dict) -> None:
    """Send a JSON-RPC message to stdout (binary)."""
    body = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
    sys.stdout.buffer.flush()


def mcp_send(obj: dict) -> None:
    """Send a JSON-RPC message to stdout (binary mode)."""
    body = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode())
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


# ── Tool handlers ────────────────────────────────────────────────────────────

def slugify(title: str) -> str:
    return title.lower().replace(" ", "-").replace("/", "-")[:50]


def handle_tool_call(conn: sqlite3.Connection, tool: str, args: dict) -> dict | str:
    cur = conn.cursor()

    if tool == "initiatives.create":
        slug = args.get("slug") or slugify(args["title"])
        description = args.get("description", "")
        try:
            cur.execute(
                "INSERT INTO initiatives (slug, title, description) VALUES (?, ?, ?)",
                (slug, args["title"], description),
            )
            conn.commit()
            return {"id": cur.lastrowid, "slug": slug, "title": args["title"], "status": "pending"}
        except sqlite3.IntegrityError:
            return {"error": f"slug '{slug}' already exists"}

    elif tool == "initiatives.list":
        status_filter = args.get("status")
        if status_filter:
            cur.execute(
                "SELECT id, slug, title, status, updated_at FROM initiatives WHERE status = ? ORDER BY updated_at DESC",
                (status_filter,),
            )
        else:
            cur.execute(
                "SELECT id, slug, title, status, updated_at FROM initiatives ORDER BY updated_at DESC"
            )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    elif tool == "initiatives.claim":
        initiative_id = args["id"]
        cur.execute(
            "UPDATE initiatives SET status = 'discovery', updated_at = datetime('now') WHERE id = ? AND status = 'pending'",
            (initiative_id,),
        )
        conn.commit()
        if cur.rowcount == 0:
            cur.execute("SELECT title, status FROM initiatives WHERE id = ?", (initiative_id,))
            row = cur.fetchone()
            if row:
                return {"claimed": False, "id": initiative_id, "title": row["title"],
                        "status": f"already {row['status']}"}
            return {"error": f"initiative {initiative_id} not found"}
        return {"claimed": True, "id": initiative_id}

    elif tool == "initiatives.update":
        initiative_id = args["id"]
        status = args["status"]
        if status not in STATUS_FLOW:
            return {"error": f"invalid status '{status}'. Must be one of: {', '.join(STATUS_FLOW)}"}
        cur.execute(
            "UPDATE initiatives SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, initiative_id),
        )
        conn.commit()
        return {"id": initiative_id, "status": status}

    elif tool == "initiatives.get":
        initiative_id = args["id"]
        cur.execute("SELECT * FROM initiatives WHERE id = ?", (initiative_id,))
        row = cur.fetchone()
        return dict(row) if row else {"error": f"initiative {initiative_id} not found"}

    elif tool == "actions.write":
        cur.execute(
            "INSERT INTO actions (initiative_id, agent, action_type, content) VALUES (?, ?, ?, ?)",
            (args["initiative_id"], args["agent"], args["action_type"], args["content"]),
        )
        conn.commit()
        return {"id": cur.lastrowid, "created_at": datetime.datetime.now().isoformat()}

    elif tool == "actions.get":
        cur.execute(
            "SELECT agent, action_type, content, created_at FROM actions WHERE initiative_id = ? ORDER BY created_at",
            (args["initiative_id"],),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    elif tool == "handoff.read":
        cur.execute(
            "SELECT content, agent, action_type, created_at FROM actions WHERE initiative_id = ? ORDER BY created_at DESC LIMIT 1",
            (args["initiative_id"],),
        )
        row = cur.fetchone()
        if row:
            return dict(row)
        return {"content": None, "agent": None, "action_type": None}

    elif tool == "criteria.add":
        cur.execute(
            "INSERT INTO criteria (initiative_id, criterion) VALUES (?, ?)",
            (args["initiative_id"], args["criterion"]),
        )
        conn.commit()
        return {"id": cur.lastrowid, "criterion": args["criterion"], "met": False}

    elif tool == "criteria.list":
        cur.execute(
            "SELECT id, criterion, met FROM criteria WHERE initiative_id = ? ORDER BY id",
            (args["initiative_id"],),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    elif tool == "criteria.check":
        cur.execute("UPDATE criteria SET met = 1 WHERE id = ?", (args["id"],))
        conn.commit()
        return {"id": args["id"], "met": True}

    elif tool == "initiatives.edit":
        iid = args["id"]
        updates = []
        vals = []
        if "title" in args:
            updates.append("title = ?")
            vals.append(args["title"])
        if "description" in args:
            updates.append("description = ?")
            vals.append(args["description"])
        if not updates:
            return {"error": "no fields to edit"}
        updates.append("updated_at = datetime('now')")
        vals.append(iid)
        cur.execute(f"UPDATE initiatives SET {', '.join(updates)} WHERE id = ?", vals)
        conn.commit()
        return {"id": iid, "edited": True}

    elif tool == "initiatives.archive":
        iid = args["id"]
        cur.execute("UPDATE initiatives SET archived_at = datetime('now'), updated_at = datetime('now') WHERE id = ?", (iid,))
        conn.commit()
        return {"id": iid, "archived": True}

    elif tool == "initiatives.unarchive":
        iid = args["id"]
        cur.execute("UPDATE initiatives SET archived_at = NULL, updated_at = datetime('now') WHERE id = ?", (iid,))
        conn.commit()
        return {"id": iid, "unarchived": True}

    elif tool == "actions.start":
        cur.execute("INSERT INTO actions (initiative_id, agent, action_type, content, status) VALUES (?, ?, ?, '', 'in_progress')",
                    (args["initiative_id"], args["agent"], args.get("action_type", "action")))
        conn.commit()
        action_id = cur.lastrowid
        return {"action_id": action_id, "status": "in_progress"}

    elif tool == "actions.complete":
        aid = args["action_id"]
        summary = args.get("summary", "")
        cur.execute("UPDATE actions SET status = 'completed', completed_at = datetime('now'), summary = ? WHERE id = ?",
                    (summary, aid))
        conn.commit()
        return {"action_id": aid, "status": "completed"}

    elif tool in ("actions.record_file", "actions.record.file"):
        cur.execute("INSERT INTO action_files (action_id, file_path, operation, notes) VALUES (?, ?, ?, ?)",
                    (args["action_id"], args["file_path"], args.get("operation", "modified"), args.get("notes", "")))
        conn.commit()
        return {"id": cur.lastrowid, "file_path": args["file_path"]}

    elif tool in ("actions.record_tool", "actions.record.tool"):
        cur.execute("INSERT INTO action_tools (action_id, tool_name, args_json, result_summary) VALUES (?, ?, ?, ?)",
                    (args["action_id"], args["tool_name"], args.get("args_json", ""), args.get("result_summary", "")))
        conn.commit()
        return {"id": cur.lastrowid, "tool_name": args["tool_name"]}

    elif tool == "skills.search":
        query = args.get("query", "")
        # Search skills dir: check installed path first, then repo path
        base = Path(__file__).resolve().parent
        skills_dir = base / "skills"
        if not skills_dir.exists():
            skills_dir = base.parent / "skills"
        results = []
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if not skill_dir.is_dir() or skill_dir.name.startswith(".") or ".bak" in skill_dir.name:
                    continue
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text()
                    if query.lower() in content.lower():
                        desc = ""
                        for line in content.split("\n"):
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip()
                                break
                        results.append({"name": skill_dir.name, "description": desc})
        return results[:20]

    elif tool == "docs.search":
        query = args.get("query", "")
        scope = args.get("scope", "all")  # 'all', 'skills', 'docs'
        results = []
        if scope in ("all", "skills"):
            base = Path(__file__).resolve().parent
            sd = base / "skills"
            if not sd.exists():
                sd = base.parent / "skills"
            if sd.exists():
                for dir_entry in sd.iterdir():
                    if not dir_entry.is_dir() or dir_entry.name.startswith(".") or ".bak" in dir_entry.name:
                        continue
                    sm = dir_entry / "SKILL.md"
                    if sm.exists() and query.lower() in sm.read_text().lower():
                        desc = ""
                        for line in sm.read_text().split("\n"):
                            if line.startswith("description:"):
                                desc = line.split(":", 1)[1].strip()
                                break
                        results.append({"source": "skill", "name": dir_entry.name, "description": desc})
        if scope in ("all", "docs"):
            dd = docs_dir()
            if dd.exists():
                for md_file in dd.rglob("*.md"):
                    if md_file.is_file() and query.lower() in md_file.read_text().lower():
                        rel = md_file.relative_to(dd)
                        results.append({"source": "doc", "path": str(rel)})
        return results[:20]

    elif tool == "docs.save":
        path = args.get("path", "")
        content = args.get("content", "")
        if not path or not content:
            return {"error": "path and content are required"}
        # Validate path stays within docs dir
        dd = docs_dir()
        full = (dd / path).resolve()
        if not str(full).startswith(str(dd.resolve())):
            return {"error": "path escapes docs directory"}
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        return {"path": str(full), "size": len(content)}  # max 20 results

    elif tool == "pmahk.doctor":
        lib_version = VERSION
        cur.execute("PRAGMA database_list")
        db_info = cur.fetchone()
        db_path = dict(db_info).get("file", "unknown") if db_info else "unknown"
        # Check both paths (installed + repo)
        base = Path(__file__).resolve().parent
        agent_dir = base / "agents"
        if not agent_dir.exists():
            agent_dir = base.parent / "agents"
        skills_dir = base / "skills"
        if not skills_dir.exists():
            skills_dir = base.parent / "skills"
        agents_present = [f.stem for f in agent_dir.glob("pm-*.md")] if agent_dir.exists() else []
        skill_count = len([d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]) if skills_dir.exists() else 0
        return {"lib_version": lib_version, "agents": sorted(agents_present),
                "skills_count": skill_count, "db": db_path}

    return {"error": f"unknown tool: {tool}"}


# ── MCP Tool definitions (for tools/list) ─────────────────────────────────────

MCP_TOOLS = [
    {"name": "initiatives_create", "description": "Create a new initiative in the backlog",
     "inputSchema": {"type": "object", "properties": {
         "title": {"type": "string", "description": "Short action-oriented title"},
         "slug": {"type": "string", "description": "URL-friendly slug (auto-generated if omitted)"},
         "description": {"type": "string", "description": "Goal and context"},
     }, "required": ["title"]}},
    {"name": "initiatives_list", "description": "List initiatives, optionally filtered by status",
     "inputSchema": {"type": "object", "properties": {
         "status": {"type": "string", "description": "Filter: pending|discovery|spec|review|approved|blocked|done"},
     }}},
    {"name": "initiatives_claim", "description": "Atomically claim a pending initiative",
     "inputSchema": {"type": "object", "properties": {
         "id": {"type": "integer", "description": "Initiative ID"},
     }, "required": ["id"]}},
    {"name": "initiatives_update", "description": "Change initiative status",
     "inputSchema": {"type": "object", "properties": {
         "id": {"type": "integer"}, "status": {"type": "string"},
     }, "required": ["id", "status"]}},
    {"name": "initiatives_get", "description": "Get initiative details",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "actions_write", "description": "Log an agent action with content",
     "inputSchema": {"type": "object", "properties": {
         "initiative_id": {"type": "integer"}, "agent": {"type": "string"},
         "action_type": {"type": "string"}, "content": {"type": "string"},
     }, "required": ["initiative_id", "agent", "action_type", "content"]}},
    {"name": "actions_get", "description": "Get full action history for an initiative",
     "inputSchema": {"type": "object", "properties": {"initiative_id": {"type": "integer"}}, "required": ["initiative_id"]}},
    {"name": "handoff_read", "description": "Read the most recent action content (previous agent's output)",
     "inputSchema": {"type": "object", "properties": {"initiative_id": {"type": "integer"}}, "required": ["initiative_id"]}},
    {"name": "criteria_add", "description": "Add an acceptance criterion",
     "inputSchema": {"type": "object", "properties": {
         "initiative_id": {"type": "integer"}, "criterion": {"type": "string"},
     }, "required": ["initiative_id", "criterion"]}},
    {"name": "criteria_list", "description": "List acceptance criteria for an initiative",
     "inputSchema": {"type": "object", "properties": {"initiative_id": {"type": "integer"}}, "required": ["initiative_id"]}},
    {"name": "criteria_check", "description": "Mark an acceptance criterion as met (reviewer only)",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    # -- v2.1: AHK parity tools --
    {"name": "initiatives_edit", "description": "Edit initiative title or description",
     "inputSchema": {"type": "object", "properties": {
         "id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}}, "required": ["id"]}},
    {"name": "initiatives_archive", "description": "Archive an initiative",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "initiatives_unarchive", "description": "Unarchive an initiative",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "actions_start", "description": "Start a new action, returns action_id",
     "inputSchema": {"type": "object", "properties": {
         "initiative_id": {"type": "integer"}, "agent": {"type": "string"}, "action_type": {"type": "string"}},
     "required": ["initiative_id", "agent"]}},
    {"name": "actions_complete", "description": "Close an action with a summary",
     "inputSchema": {"type": "object", "properties": {
         "action_id": {"type": "integer"}, "summary": {"type": "string"}}, "required": ["action_id"]}},
    {"name": "actions_record_file", "description": "Record a file/artifact touched by an action",
     "inputSchema": {"type": "object", "properties": {
         "action_id": {"type": "integer"}, "file_path": {"type": "string"},
         "operation": {"type": "string"}, "notes": {"type": "string"}},
     "required": ["action_id", "file_path"]}},
    {"name": "actions_record_tool", "description": "Record a PM skill used during an action",
     "inputSchema": {"type": "object", "properties": {
         "action_id": {"type": "integer"}, "tool_name": {"type": "string"},
         "args_json": {"type": "string"}, "result_summary": {"type": "string"}},
     "required": ["action_id", "tool_name"]}},
     {"name": "skills_search", "description": "Search the PM skills library",
      "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
     {"name": "docs_search", "description": "Search project PM docs + skills (type: all|skills|docs)",
      "inputSchema": {"type": "object", "properties": {
          "query": {"type": "string", "description": "Search term"},
          "scope": {"type": "string", "description": "all|skills|docs (default: all)"}},
      "required": ["query"]}},
     {"name": "docs_save", "description": "Save a validated document to the PM docs directory",
      "inputSchema": {"type": "object", "properties": {
          "path": {"type": "string", "description": "Relative path (e.g. delivery/prds/checkout-v2.md)"},
          "content": {"type": "string", "description": "Document content"}},
      "required": ["path", "content"]}},
    {"name": "pmahk_doctor", "description": "Check harness version, agent files, and skills sync status",
     "inputSchema": {"type": "object", "properties": {}}},
 ]


# ── MCP serve loop ───────────────────────────────────────────────────────────

def cmd_serve(db_path: str | Path) -> None:
    """Start MCP server - reads JSON-RPC from stdin, writes to stdout."""
    sys.stderr.write(f"[pm-ahk] MCP server starting (stdio)\n")
    sys.stderr.flush()
    conn = get_conn(db_path)
    init_db(db_path)
    migrate_schema(conn)  # add new columns from v2.1.0+

    while True:
        req = mcp_read()
        if req is None:
            sys.stderr.write("[pm-ahk] EOF on stdin, exiting\n")
            sys.stderr.flush()
            break
        
        sys.stderr.write(f"[pm-ahk] Got request: {req.get('method')}\n")
        sys.stderr.flush()

        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        if method == "initialize":
            mcp_send({"jsonrpc": "2.0", "result": {"protocolVersion": "2024-11-05",
                       "serverInfo": {"name": "pm-ahk", "version": VERSION},
                       "capabilities": {"tools": {}}}, "id": req_id})

        elif method == "tools/list":
            mcp_send({"jsonrpc": "2.0", "result": {"tools": MCP_TOOLS}, "id": req_id})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                result = handle_tool_call(conn, tool_name.replace("_", "."), tool_args)
                # MCP format: wrap in content[{type:text, text:json_string}]
                mcp_send({"jsonrpc": "2.0", "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}]
                }, "id": req_id})
            except Exception as e:
                # Error format: content with isError flag
                mcp_send({"jsonrpc": "2.0", "result": {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True
                }, "id": req_id})

        elif method == "notifications/initialized":
            pass

        else:
            mcp_send({"jsonrpc": "2.0", "error": {"code": -32601, "message": f"method not found: {method}"}, "id": req_id})

    conn.close()


# ── CLI: init ────────────────────────────────────────────────────────────────

def prompt(question: str, default: str = "") -> str:
    val = input(f"  {question} [{default}]: ").strip()
    return val if val else default


def cmd_init(scope: str) -> None:
    print()
    print(f"  {bold('pm-agent-harness-kit')} {dim(f'v{VERSION}')}")
    print(f"  {dim('MCP harness initialization')}")
    print()

    # Determine scope
    if scope == "global":
        base_dir = Path.home() / ".config" / "opencode"
        print(f"  {dim('Installing globally:')} {base_dir}")
    else:
        base_dir = Path(os.getcwd())
        print(f"  {dim('Installing in current project:')} {base_dir}")

    harness_dir = base_dir / ".harness"
    db_path = harness_dir / "harness.db"
    feature_json = harness_dir / "feature_list.json"

    # Create directories
    harness_dir.mkdir(parents=True, exist_ok=True)

    # Initialize DB
    init_db(db_path)
    print(f"  {green('✓')} Database: {db_path}")

    # Create feature_list.json
    if not feature_json.exists():
        feature_json.write_text("[\n\n]\n")
        print(f"  {green('✓')} Backlog: {feature_json}")
    else:
        print(f"  {dim('  → feature_list.json already exists, keeping it')}")

    # Add first initiative interactively
    if input(f"  {yellow('Add a first initiative?')} (y/N) ").lower() == "y":
        title = input("  Title: ").strip()
        desc = input("  Description: ").strip()
        conn = get_conn(db_path)
        conn.execute("INSERT INTO initiatives (slug, title, description) VALUES (?, ?, ?)",
                     (slugify(title), title, desc))
        conn.commit()
        conn.close()
        print(f"  {green('✓')} Initiative created: {title}")

    # MCP config snippet (opencode)
    mcp_config = {
        "mcpServers": {
            "pm-ahk": {
                "command": "python3",
                "args": [str(Path(__file__).resolve()), "serve", "--db", str(db_path)],
            }
        }
    }
    print()
    print(f"  {bold('▸ Add to your opencode.json or .opencode/mcp.json:')}")
    print(f"  {json.dumps(mcp_config, indent=2)}")
    print()
    print(f"  {green('Done!')} Run {bold('pm-ahk status')} to see the backlog.")
    print(f"  {dim(f'Python >= 3.8 required (current: {sys.version.split()[0]}) — 3.12+ recommended.')}")


# ── CLI: status ──────────────────────────────────────────────────────────────

def cmd_status(db_path: str | Path) -> None:
    if not os.path.exists(db_path):
        print(f"  {yellow('No harness database found. Run')} pm-ahk init {yellow('first.')}")
        return

    conn = get_conn(db_path)
    cur = conn.execute("SELECT id, slug, title, status, updated_at FROM initiatives ORDER BY updated_at DESC")

    rows = cur.fetchall()
    if not rows:
        print(f"  {yellow('No initiatives yet. Run')} pm-ahk initiative add {yellow('or')} pm-ahk init {yellow('to add one.')}")
        conn.close()
        return

    print(f"  {bold('Initiative Backlog')}")
    print(f"  {dim('─' * 72)}")
    print(f"  {'ID':<4} {'Title':<30} {'Status':<12} {'Updated':<20}")
    print(f"  {'─'*3} {'─'*29} {'─'*11} {'─'*19}")
    for r in rows:
        status_display = r["status"]
        if status_display == "done":
            status_display = green(status_display)
        elif status_display in ("blocked",):
            status_display = red(status_display)
        elif status_display in ("spec", "review"):
            status_display = cyan(status_display)
        print(f"  {r['id']:<4} {r['title'][:29]:<30} {status_display:<28} {r['updated_at'][:19]}")
    conn.close()


# ── CLI: initiative subcommands ──────────────────────────────────────────────

def cmd_initiative(args: argparse.Namespace, db_path: str | Path) -> None:
    conn = get_conn(db_path)

    if args.action == "add":
        title = input("  Title: ").strip()
        desc = input("  Description: ").strip()
        slug = slugify(title)
        try:
            conn.execute("INSERT INTO initiatives (slug, title, description) VALUES (?, ?, ?)",
                         (slug, title, desc))
            conn.commit()
            print(f"  {green('✓')} Created: {title} ({green(slug)})")
        except sqlite3.IntegrityError:
            print(f"  {yellow('A slug conflict occurred. The initiative was probably added before.')}")

    elif args.action == "list":
        status_filter = args.status
        if status_filter:
            cur = conn.execute(
                "SELECT id, slug, title, status, updated_at FROM initiatives WHERE status = ? ORDER BY id",
                (status_filter,),
            )
        else:
            cur = conn.execute("SELECT id, slug, title, status, updated_at FROM initiatives ORDER BY id")
        rows = cur.fetchall()
        if not rows:
            print(f"  {yellow('No initiatives.')}")
        else:
            for r in rows:
                s = r["status"]
                s_display = green(s) if s == "done" else red(s) if s == "blocked" else s
                print(f"  {r['id']:<4} {r['title'][:30]:<32} {s_display:<12} {r['updated_at'][:10]}")
        print(f"  {dim(f'Total: {len(rows)}')}")

    elif args.action == "done":
        identifier = args.id_or_slug
        if identifier.isdigit():
            cur = conn.execute("UPDATE initiatives SET status = 'done', updated_at = datetime('now') WHERE id = ?",
                               (int(identifier),))
        else:
            cur = conn.execute("UPDATE initiatives SET status = 'done', updated_at = datetime('now') WHERE slug = ?",
                               (identifier,))
        conn.commit()
        if cur.rowcount > 0:
            print(f"  {green('✓')} Marked as done: {identifier}")
        else:
            print(f"  {yellow('Not found:')} {identifier}")

    conn.close()


# ── Dashboard HTTP server ─────────────────────────────────────────────────────

DASHBOARD_DIR = Path(__file__).resolve().parent / "pm-ahk-dashboard"

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    conn: sqlite3.Connection = None  # type: ignore

    def log_message(self, *a): pass

    def _json(self, data: dict | list, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _serve_file(self, path: str, content_type: str) -> None:
        file_path = DASHBOARD_DIR / path.lstrip("/")
        if not file_path.exists() or not file_path.is_file():
            file_path = DASHBOARD_DIR / "index.html"
            content_type = "text/html"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path == "/api/overview":
            self._json(_api_overview(self.conn))
        elif path.startswith("/api/initiatives/"):
            parts = path.split("/")
            if len(parts) == 4 and parts[3].isdigit():
                self._json(_api_initiative(self.conn, int(parts[3])))
            else:
                self._json({"error": "invalid id"}, 404)
        elif path == "/api/initiatives":
            self._json(_api_initiatives(self.conn))
        elif path == "/api/agents":
            self._json(_api_agents(self.conn))
        elif path.startswith("/api/"):
            self._json({"error": "not found"}, 404)
        elif path == "/" or path == "":
            self._serve_file("/index.html", "text/html")
        elif path.endswith(".js"):
            self._serve_file(path, "application/javascript")
        elif path.endswith(".css"):
            self._serve_file(path, "text/css")
        else:
            self._serve_file(path, "text/html")


def _api_overview(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    statuses = ["discovery", "strategy", "spec", "review", "approved", "blocked", "done"]
    counts = {}
    for s in statuses:
        cur.execute("SELECT COUNT(*) FROM initiatives WHERE status = ?", (s,))
        counts[s] = cur.fetchone()[0]

    cur.execute("""
        SELECT a.agent, a.action_type, i.title, a.created_at
        FROM actions a JOIN initiatives i ON a.initiative_id = i.id
        ORDER BY a.created_at DESC LIMIT 15
    """)
    recent = [{"agent": r[0], "action_type": r[1], "title": r[2], "created_at": r[3]} for r in cur.fetchall()]

    return {"discovery": counts.get("discovery", 0), "strategy": counts.get("strategy", 0),
            "spec": counts.get("spec", 0), "review": counts.get("review", 0),
            "approved": counts.get("approved", 0), "blocked": counts.get("blocked", 0),
            "done": counts.get("done", 0), "recent_actions": recent}


def _api_initiatives(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.execute("SELECT id, slug, title, description, status, created_at, updated_at FROM initiatives ORDER BY id")
    return [dict(r) for r in cur.fetchall()]


def _api_initiative(conn: sqlite3.Connection, initiative_id: int) -> dict:
    cur = conn.execute("SELECT id, slug, title, description, status, created_at, updated_at FROM initiatives WHERE id = ?",
                       (initiative_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "not found"}
    initiative = dict(row)
    cur.execute("SELECT agent, action_type, content, created_at FROM actions WHERE initiative_id = ? ORDER BY created_at",
               (initiative_id,))
    actions = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT id, criterion, met FROM criteria WHERE initiative_id = ? ORDER BY id",
               (initiative_id,))
    criteria = [dict(r) for r in cur.fetchall()]
    return {"initiative": initiative, "actions": actions, "criteria": criteria}


def _api_agents(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.execute("""
        SELECT agent, COUNT(*) as total_actions, COUNT(DISTINCT initiative_id) as initiatives_count
        FROM actions GROUP BY agent ORDER BY total_actions DESC
    """)
    return [dict(r) for r in cur.fetchall()]


def cmd_dashboard(db_path: str | Path, port: int = 5432, no_open: bool = False) -> None:
    """Start a local HTTP dashboard server."""
    conn = get_conn(db_path)
    DashboardHandler.conn = conn
    DashboardHandler.protocol_version = "HTTP/1.1"

    server = socketserver.ThreadingTCPServer(("127.0.0.1", port), DashboardHandler)
    url = f"http://localhost:{port}"
    print(f"\n  {green('Dashboard')}: {bold(url)}")
    print(f"  {dim('Press Ctrl+C to stop.')}\n")
    if not no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        conn.close()


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=f"pm-agent-harness-kit MCP harness v{VERSION}")
    parser.add_argument("--version", action="version", version=VERSION)

    sub = parser.add_subparsers(dest="command")

    serve_p = sub.add_parser("serve", help="Start MCP server (stdio JSON-RPC)")
    serve_p.add_argument("--db", help="Path to harness.db")
    http_p = sub.add_parser("serve-http", help="Start MCP server over HTTP (requires flask)")
    http_p.add_argument("--port", type=int, default=5431, help="HTTP port (default: 5431)")
    http_p.add_argument("--host", default="127.0.0.1", help="Bind address")
    http_p.add_argument("--db", help="Path to harness.db")
    init_p = sub.add_parser("init", help="Initialize harness database")
    init_p.add_argument("--scope", choices=["global", "project"], default="global",
                        help="Install scope (default: global)")
    init_p.add_argument("--db", help="Path to harness.db")
    status_p = sub.add_parser("status", help="Show initiative backlog")
    status_p.add_argument("--db", help="Path to harness.db")
    dash_p = sub.add_parser("dashboard", help="Start local web dashboard")
    dash_p.add_argument("--port", type=int, default=5432, help="Port (default: 5432)")
    dash_p.add_argument("--no-open", action="store_true", help="Don't open browser")
    dash_p.add_argument("--db", help="Path to harness.db")

    initiative_p = sub.add_parser("initiative", help="Manage initiatives")
    initiative_p.add_argument("action", choices=["add", "list", "done"])
    initiative_p.add_argument("id_or_slug", nargs="?", help="ID or slug for 'done' action")
    initiative_p.add_argument("--status", help="Filter list by status")
    initiative_p.add_argument("--db", help="Path to harness.db")

    opts = parser.parse_args()

    if opts.command is None:
        parser.print_help()
        return

    # Resolve DB path
    if getattr(opts, 'db', None):
        db_path = Path(opts.db)
    else:
        # Try project-local first, then global
        project_db = Path(os.getcwd()) / ".harness" / "harness.db"
        global_db = Path.home() / ".config" / "opencode" / ".harness" / "harness.db"
        db_path = project_db if project_db.exists() else global_db

    if opts.command == "serve":
        init_db(db_path)  # ensure tables exist
        cmd_serve(db_path)
    elif opts.command == "init":
        cmd_init(opts.scope)
    elif opts.command == "status":
        cmd_status(db_path)
    elif opts.command == "initiative":
        cmd_initiative(opts, db_path)
    elif opts.command == "dashboard":
        init_db(db_path)
        cmd_dashboard(db_path, port=opts.port, no_open=opts.no_open)
    elif opts.command == "serve-http":
        server_script = Path(__file__).resolve().parent / "pm-ahk-server.py"
        import subprocess as _sp
        _sp.run(["python3", str(server_script), "--port", str(opts.port),
                 "--host", opts.host, "--db", str(db_path)])


if __name__ == "__main__":
    main()
