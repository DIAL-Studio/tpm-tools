#!/usr/bin/env python3
"""MCP over HTTP/SSE server for pm-agent-harness-kit — using Flask.

Implements the MCP Streamable HTTP transport with SSE for reliable
bidirectional communication with opencode and Claude Code.

Requirements: flask (pip install flask)

Usage:
  python3 pm-ahk-server.py --port 5431
"""

from __future__ import annotations

import json
import os
import queue
import sqlite3
import sys
import threading
import uuid
from pathlib import Path

import flask

# Reuse db logic from pm-ahk.py
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import importlib.util as _util
_spec = _util.spec_from_file_location("_ahk", str(SCRIPT_DIR / "pm-ahk.py"))
_ahk = _util.module_from_spec(_spec)
_spec.loader.exec_module(_ahk)

app = flask.Flask(__name__)
DB_PATH = None

STATUS_FLOW = ["pending", "discovery", "strategy", "spec", "review", "approved", "blocked", "done"]

# Active SSE connections: session_id → queue (for sending responses back)
_sse_clients: dict[str, queue.Queue] = {}
_sse_lock = threading.Lock()

MCP_TOOLS = [
    {"name": "initiatives_create", "description": "Create a new initiative",
     "inputSchema": {"type": "object", "properties": {
         "title": {"type": "string"}, "slug": {"type": "string"},
         "description": {"type": "string"}}, "required": ["title"]}},
    {"name": "initiatives_list", "description": "List initiatives",
     "inputSchema": {"type": "object", "properties": {"status": {"type": "string"}}}},
    {"name": "initiatives_claim", "description": "Claim a pending initiative",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "initiatives_update", "description": "Change initiative status",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}, "status": {"type": "string"}},
     "required": ["id", "status"]}},
    {"name": "initiatives_get", "description": "Get initiative details",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "actions_write", "description": "Log an agent action",
     "inputSchema": {"type": "object", "properties": {
         "initiative_id": {"type": "integer"}, "agent": {"type": "string"},
         "action_type": {"type": "string"}, "content": {"type": "string"}},
     "required": ["initiative_id", "agent", "action_type", "content"]}},
    {"name": "actions_get", "description": "Get action history",
     "inputSchema": {"type": "object", "properties": {"initiative_id": {"type": "integer"}}, "required": ["initiative_id"]}},
    {"name": "handoff_read", "description": "Read previous agent's output",
     "inputSchema": {"type": "object", "properties": {"initiative_id": {"type": "integer"}}, "required": ["initiative_id"]}},
    {"name": "criteria_add", "description": "Add acceptance criterion",
     "inputSchema": {"type": "object", "properties": {
         "initiative_id": {"type": "integer"}, "criterion": {"type": "string"}},
     "required": ["initiative_id", "criterion"]}},
    {"name": "criteria_list", "description": "List criteria",
     "inputSchema": {"type": "object", "properties": {"initiative_id": {"type": "integer"}}, "required": ["initiative_id"]}},
    {"name": "criteria_check", "description": "Mark criterion as met",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
]


def get_conn():
    return _ahk.get_conn(DB_PATH)


@app.route("/sse")
def sse():
    """SSE endpoint — opencode connects here first."""
    session_id = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()

    with _sse_lock:
        _sse_clients[session_id] = q

    def generate():
        # Send the endpoint event with session_id
        yield f"event: endpoint\ndata: /message?session_id={session_id}\n\n"

        # Keep connection alive, waiting for responses
        while True:
            try:
                msg = q.get(timeout=30)  # timeout to send keepalive
                if msg == "__close__":
                    break
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                yield ": keepalive\n\n"  # SSE comment (keepalive)

    with _sse_lock:
        response = flask.Response(generate(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"

    # Cleanup on disconnect
    old_close = response.call_on_close
    def cleanup():
        with _sse_lock:
            _sse_clients.pop(session_id, None)
        if old_close:
            old_close()
    response.call_on_close = cleanup

    return response


@app.route("/message", methods=["POST"])
def message():
    """MCP message endpoint — receives JSON-RPC, sends response via SSE."""
    session_id = flask.request.args.get("session_id")
    if not session_id:
        return flask.jsonify({"jsonrpc": "2.0", "error": {"code": -32600, "message": "missing session_id"},
                              "id": None}), 400

    data = flask.request.get_json(silent=True)
    if not data or "method" not in data:
        return flask.jsonify({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid request"},
                              "id": data.get("id") if data else None}), 400

    method = data["method"]
    params = data.get("params", {})
    req_id = data.get("id")

    try:
        if method == "initialize":
            result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
            _send_response(session_id, result, req_id)
        elif method == "tools/list":
            result = {"tools": MCP_TOOLS}
            _send_response(session_id, result, req_id)
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            result = _handle_tool_call(tool_name.replace("_", "."), tool_args)
            _send_response(session_id, result, req_id)
        elif method == "notifications/initialized":
            pass  # no response needed
        else:
            _send_error(session_id, -32601, f"method not found: {method}", req_id)
    except Exception as e:
        _send_error(session_id, -32000, str(e), req_id)

    return flask.jsonify({"status": "ok"}), 202


def _send_response(session_id: str, result: dict, req_id: int | None) -> None:
    with _sse_lock:
        q = _sse_clients.get(session_id)
        if q:
            q.put({"jsonrpc": "2.0", "result": result, "id": req_id})


def _send_error(session_id: str, code: int, msg: str, req_id: int | None) -> None:
    with _sse_lock:
        q = _sse_clients.get(session_id)
        if q:
            q.put({"jsonrpc": "2.0", "error": {"code": code, "message": msg}, "id": req_id})


def _handle_tool_call(tool: str, args: dict) -> dict | str:
    conn = get_conn()
    cur = conn.cursor()

    if tool == "initiatives.create":
        slug = args.get("slug") or _ahk.slugify(args["title"])
        desc = args.get("description", "")
        try:
            cur.execute("INSERT INTO initiatives (slug, title, description) VALUES (?, ?, ?)",
                        (slug, args["title"], desc))
            conn.commit()
            return {"id": cur.lastrowid, "slug": slug, "title": args["title"], "status": "pending"}
        except sqlite3.IntegrityError:
            return {"error": f"slug '{slug}' already exists"}

    elif tool == "initiatives.list":
        sf = args.get("status")
        if sf:
            cur.execute("SELECT id, slug, title, status, updated_at FROM initiatives WHERE status = ? ORDER BY updated_at DESC", (sf,))
        else:
            cur.execute("SELECT id, slug, title, status, updated_at FROM initiatives ORDER BY updated_at DESC")
        return [dict(r) for r in cur.fetchall()]

    elif tool == "initiatives.claim":
        iid = args["id"]
        cur.execute("UPDATE initiatives SET status='discovery',updated_at=datetime('now') WHERE id=? AND status='pending'", (iid,))
        conn.commit()
        if cur.rowcount == 0:
            cur.execute("SELECT title,status FROM initiatives WHERE id=?", (iid,))
            r = cur.fetchone()
            if r:
                return {"claimed": False, "id": iid, "title": r["title"], "status": "already " + r["status"]}
            return {"error": f"initiative {iid} not found"}
        return {"claimed": True, "id": iid}

    elif tool == "initiatives.update":
        iid, s = args["id"], args["status"]
        if s not in STATUS_FLOW:
            return {"error": f"invalid status '{s}'"}
        cur.execute("UPDATE initiatives SET status=?,updated_at=datetime('now') WHERE id=?", (s, iid))
        conn.commit()
        return {"id": iid, "status": s}

    elif tool == "initiatives.get":
        cur.execute("SELECT * FROM initiatives WHERE id=?", (args["id"],))
        r = cur.fetchone()
        return dict(r) if r else {"error": "not found"}

    elif tool == "actions.write":
        cur.execute("INSERT INTO actions (initiative_id,agent,action_type,content) VALUES (?,?,?,?)",
                    (args["initiative_id"], args["agent"], args["action_type"], args["content"]))
        conn.commit()
        return {"id": cur.lastrowid}

    elif tool == "actions.get":
        cur.execute("SELECT agent,action_type,content,created_at FROM actions WHERE initiative_id=? ORDER BY created_at",
                    (args["initiative_id"],))
        return [dict(r) for r in cur.fetchall()]

    elif tool == "handoff.read":
        cur.execute("SELECT content,agent,action_type,created_at FROM actions WHERE initiative_id=? ORDER BY created_at DESC LIMIT 1",
                    (args["initiative_id"],))
        r = cur.fetchone()
        return dict(r) if r else {"content": None, "agent": None, "action_type": None}

    elif tool == "criteria.add":
        cur.execute("INSERT INTO criteria (initiative_id,criterion) VALUES (?,?)",
                    (args["initiative_id"], args["criterion"]))
        conn.commit()
        return {"id": cur.lastrowid, "criterion": args["criterion"], "met": False}

    elif tool == "criteria.list":
        cur.execute("SELECT id,criterion,met FROM criteria WHERE initiative_id=? ORDER BY id",
                    (args["initiative_id"],))
        return [dict(r) for r in cur.fetchall()]

    elif tool == "criteria.check":
        cur.execute("UPDATE criteria SET met=1 WHERE id=?", (args["id"],))
        conn.commit()
        return {"id": args["id"], "met": True}

    return {"error": f"unknown tool: {tool}"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="pm-agent-harness-kit MCP over HTTP/SSE server")
    parser.add_argument("--port", type=int, default=5431, help="HTTP port (default: 5431)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--db", help="Path to harness.db")
    opts = parser.parse_args()

    global DB_PATH
    if opts.db:
        DB_PATH = Path(opts.db)
    else:
        project_db = Path.cwd() / ".harness" / "harness.db"
        global_db = Path.home() / ".config" / "opencode" / ".harness" / "harness.db"
        DB_PATH = project_db if project_db.exists() else global_db

    _ahk.init_db(str(DB_PATH))

    print(f"\n  MCP over HTTP/SSE server: http://{opts.host}:{opts.port}")
    print(f"  Database: {DB_PATH}")
    print(f"  Press Ctrl+C to stop.\n")

    app.run(host=opts.host, port=opts.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
