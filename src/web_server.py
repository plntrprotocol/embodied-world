"""
web_server.py — Serves the web visual layer and bridges to the simulation.

Runs an HTTP server that:
- Serves the HTML/CSS/JS frontend
- Provides a REST API for world state
- Runs a WebSocket for live updates
- Bridges player actions to the simulation engine
"""

import json
import time
import threading
import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Optional

from .world_state import get_db, get_world, init_world, seed_world, DB_PATH
from .agent import Agent
from .simulation import tick
from .ecology import init_ecology
from .persistence import save_snapshot, commit_snapshot

# Try to import websockets for live updates
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


WEB_DIR = Path(__file__).parent.parent / "web"
API_PREFIX = "/api"


class WorldAPIHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves the frontend and handles API calls."""

    def __init__(self, *args, agent=None, **kwargs):
        self.agent = agent
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if self.path.startswith(API_PREFIX):
            self._handle_api_get()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith(API_PREFIX):
            self._handle_api_post()
        else:
            self.send_error(404)

    def _handle_api_get(self):
        """Handle API GET requests."""
        path = self.path[len(API_PREFIX):]

        if path == "/world" or path == "/":
            # Full world state
            db = get_db()
            world = get_world(db)
            self._json_response(world)

        elif path == "/location":
            # Current location description
            location_id = self.agent.world["agents"].get("owl", {}).get("location_id", "cottage_bedroom")
            from .text_engine import describe_location
            desc = describe_location(self.agent.db, location_id, self.agent.world)
            self._json_response({"description": desc, "location_id": location_id})

        elif path == "/status":
            body = self.agent.world.get("body", {})
            internal = self.agent.world.get("internal", {})
            time_info = self.agent.world.get("time", {})
            weather = self.agent.world.get("weather", {})
            self._json_response({
                "body": body, "internal": internal, "time": time_info, "weather": weather,
            })

        elif path == "/exits":
            from .world_state import get_exits_from
            location_id = self.agent.world["agents"].get("owl", {}).get("location_id", "cottage_bedroom")
            exits = get_exits_from(self.agent.db, location_id)
            self._json_response({"exits": exits})

        elif path == "/npcs":
            from .world_state import get_agents_in_location
            location_id = self.agent.world["agents"].get("owl", {}).get("location_id", "cottage_bedroom")
            npcs = get_agents_in_location(self.agent.db, location_id)
            self._json_response({"npcs": [n for n in npcs if n["id"] != "owl"]})

        elif path == "/projects":
            from .creative import get_active_projects, get_completed_projects
            active = get_active_projects(self.agent.db)
            completed = get_completed_projects(self.agent.db)
            self._json_response({"active": active, "completed": completed})

        elif path == "/ecology":
            try:
                from .ecology import get_location_ecology, init_ecology
                init_ecology(self.agent.db)
                location_id = self.agent.world["agents"].get("owl", {}).get("location_id", "cottage_bedroom")
                eco = get_location_ecology(self.agent.db, location_id)
                self._json_response(eco)
            except Exception as e:
                self._json_response({"plants": [], "animals": [], "fish": [], "error": str(e)})

        elif path == "/events":
            db = get_db()
            rows = db.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 20").fetchall()
            self._json_response({"events": [dict(r) for r in rows]})

        elif path == "/stories":
            try:
                from .narrative import get_active_stories, init_narrative_tables
                init_narrative_tables(self.agent.db)
                stories = get_active_stories(self.agent.db)
                self._json_response({"stories": [{"type": s.story_type, "participants": s.participants, "phase": s.phase, "narrative": s.generate_narrative()} for s in stories]})
            except Exception as e:
                self._json_response({"stories": [], "error": str(e)})

        elif path.startswith("/npcs-at"):
            # Get NPCs at any location (for schedule-aware rendering)
            from .world_state import get_agents_in_location
            loc = ""
            if "?" in path:
                query = path.split("?", 1)[1]
                params = {}
                for pair in query.split("&"):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        params[k] = v
                loc = params.get("location_id", "")
            if loc:
                npcs = get_agents_in_location(self.agent.db, loc)
                self._json_response({"npcs": [n for n in npcs if n["id"] != "owl"]})
            else:
                self._json_response({"npcs": []})

        else:
            self.send_error(404)

    def _handle_api_post(self):
        """Handle API POST requests (player actions)."""
        path = self.path[len(API_PREFIX):]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

        result = {"success": False, "message": "Unknown command"}

        if path == "/action":
            action = data.get("action", "")
            target = data.get("target", None)
            if action:
                result_text = self.agent.act(action, target)
                result = {"success": True, "result": result_text}

        elif path == "/advance":
            hours = data.get("hours", 1.0)
            tick_result = tick(self.agent.db, hours)
            self.agent.world = get_world(self.agent.db)
            result = {"success": True, "tick": {
                "time": tick_result.get("time", {}),
                "weather": tick_result.get("weather", {}),
                "body": tick_result.get("body", {}),
            }}

        elif path == "/save":
            path_result, msg = self.agent.save(data.get("message", "web save"))
            result = {"success": True, "snapshot": path_result.name}

        self._json_response(result)

    def _json_response(self, data):
        """Send a JSON response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, format, *args):
        """Suppress default logging to keep output clean."""
        pass


def create_handler_class(agent):
    """Create a handler class bound to an agent."""
    class Handler(WorldAPIHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, agent=agent, **kwargs)
    return Handler


def start_web_server(host="127.0.0.1", port=8765, agent=None):
    """Start the web server."""
    handler = create_handler_class(agent)
    server = HTTPServer((host, port), handler)
    print(f"Web server running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


def run_web_mode(host="127.0.0.1", port=8765):
    """Initialize world and start the web server."""
    if not DB_PATH.exists():
        print("Initializing world...")
        db = init_world()
        seed_world(db)
        init_ecology(db)

    agent = Agent()
    print(f"World loaded. OWL is at: {agent.world['agents']['owl']['location_id']}")
    start_web_server(host, port, agent)
