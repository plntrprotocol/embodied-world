"""
main.py — Entry point for the Embodied Creative World.

Usage:
    python -m src.main              # Interactive session
    python -m src.main --init       # Initialize/reset world
    python -m src.main --status     # Show world status
    python -m src.main --snapshot   # Save a snapshot
    python -m src.main --populate   # Generate procedural NPCs
"""

import sys
import argparse

from .world_state import init_world, seed_world, get_world, get_db, DB_PATH
from .agent import run_interactive, Agent
from .persistence import save_snapshot, commit_snapshot, list_snapshots
from .ecology import init_ecology
from .npc_generation import populate_valley


def main():
    parser = argparse.ArgumentParser(description="Embodied Creative World")
    parser.add_argument("--init", action="store_true", help="Initialize/reset the world")
    parser.add_argument("--status", action="store_true", help="Show world status")
    parser.add_argument("--snapshot", action="store_true", help="Save a snapshot")
    parser.add_argument("--snapshots", action="store_true", help="List snapshots")
    parser.add_argument("--web", action="store_true", help="Start web visual interface")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host")
    parser.add_argument("--port", type=int, default=8765, help="Web server port")
    parser.add_argument("--population", type=int, default=200, help="Target population (default: 200)")
    args = parser.parse_args()

    if args.init:
        print("Initializing world...")
        db = init_world()
        seed_world(db)
        init_ecology(db)
        from .narrative import init_narrative_tables
        from .npc_ai import init_npc_ai
        from .rituals import init_ritual_tables
        from .npc_depth import init_npc_depth
        init_narrative_tables(db)
        init_npc_ai(db)
        init_ritual_tables(db)
        init_npc_depth(db)
        print(f"World created at {DB_PATH}")
        print("Run without --init to start the session.")
        return

    if args.status:
        if not DB_PATH.exists():
            print("No world found. Run with --init first.")
            return
        db = get_db()
        world = get_world(db)
        t = world.get("time", {})
        w = world.get("weather", {})
        b = world.get("body", {})
        i = world.get("internal", {})
        npc_count = sum(1 for a in world.get("agents", {}).values() if a.get("type") == "npc")
        print(f"Time: {t.get('hour', 0):02d}:{t.get('minute', 0):02d} — {t.get('season', '?')}, {t.get('time_of_day', '?')}")
        print(f"Weather: {w.get('condition', '?')}, {w.get('temperature', '?')}°C")
        print(f"Body: mood={b.get('mood', '?')}, energy={b.get('energy', 0):.0%}, hunger={b.get('hunger', 0):.0%}")
        print(f"Internal: mood={i.get('mood', '?')}, interest={i.get('dominant_interest', '?')}, creative_urge={i.get('creative_urge', 0):.0%}")
        print(f"NPCs: {npc_count}")
        return

    if args.snapshot:
        if not DB_PATH.exists():
            print("No world found. Run with --init first.")
            return
        db = get_db()
        path = save_snapshot(db)
        commit_snapshot(db)
        print(f"Snapshot saved: {path.name}")
        return

    if args.snapshots:
        snaps = list_snapshots()
        if snaps:
            for s in snaps[:10]:
                print(f"  {s}")
        else:
            print("No snapshots found.")
        return

    if args.web:
        from .web_server import run_web_mode
        run_web_mode(args.host, args.port)
        return

    if args.populate:
        if not DB_PATH.exists():
            print("No world found. Run with --init first.")
            return
        db = get_db()
        generated = populate_valley(db, args.population)
        print(f"Generated {generated} NPCs. Target population: {args.population}")
        return

    # Default: interactive session
    if not DB_PATH.exists():
        print("No world found. Initializing...")
        db = init_world()
        seed_world(db)
        init_ecology(db)
        print(f"World created at {DB_PATH}")
        print()

    run_interactive()


if __name__ == "__main__":
    main()
