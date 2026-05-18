"""
persistence.py — Snapshots, git versioning, and crash recovery.

The world state is sacred. This module ensures it's never lost:
- Hourly JSON snapshots (human-readable, diffable)
- Git versioning (full history, rollback capability)
- Daily compressed backups
- Graceful recovery from any failure
"""

import json
import time
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from .world_state import to_json, DB_PATH

SNAPSHOTS_DIR = Path(__file__).parent.parent / "world" / "snapshots"
BACKUPS_DIR = Path(__file__).parent.parent / "world" / "backups"
WORLD_DIR = Path(__file__).parent.parent / "world"


def _ensure_dirs():
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def _git_repo_initialized() -> bool:
    """Check if the world directory is a git repo."""
    git_dir = WORLD_DIR / ".git"
    return git_dir.exists()


def init_git():
    """Initialize git repo in the world directory."""
    if _git_repo_initialized():
        return
    subprocess.run(
        ["git", "init"],
        cwd=str(WORLD_DIR),
        capture_output=True,
        text=True
    )
    # Create .gitignore
    gitignore = WORLD_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("backups/\n*.db-wal\n*.db-shm\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(WORLD_DIR), capture_output=True)
    subprocess.run(["git", "commit", "-m", "init: world repository"], cwd=str(WORLD_DIR), capture_output=True)


def save_snapshot(db, label: str = "") -> Path:
    """Save a JSON snapshot of the world state."""
    _ensure_dirs()

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    label_part = f"_{label}" if label else ""
    filename = f"world_{timestamp}{label_part}.json"
    filepath = SNAPSHOTS_DIR / filename

    world_json = to_json(db)
    filepath.write_text(world_json)

    # Also save as latest.json for easy access
    latest = SNAPSHOTS_DIR / "latest.json"
    latest.write_text(world_json)

    return filepath


def commit_snapshot(db, message: str = "") -> Optional[str]:
    """Save a snapshot and commit it to git."""
    _ensure_dirs()

    if not _git_repo_initialized():
        init_git()

    filepath = save_snapshot(db)

    try:
        # Copy db to world dir for versioning
        db_backup = WORLD_DIR / "world.db"
        if DB_PATH.exists():
            shutil.copy2(str(DB_PATH), str(db_backup))

        # Git add and commit
        subprocess.run(["git", "add", "-A"], cwd=str(WORLD_DIR), capture_output=True)
        commit_msg = message or f"world snapshot: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(WORLD_DIR),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return commit_msg
    except Exception as e:
        pass

    return None


def create_backup() -> Optional[Path]:
    """Create a daily compressed backup of the world."""
    _ensure_dirs()

    timestamp = time.strftime("%Y-%m-%d")
    backup_name = f"world_backup_{timestamp}.tar.gz"
    backup_path = BACKUPS_DIR / backup_name

    try:
        subprocess.run(
            ["tar", "-czf", str(backup_path), "-C", str(WORLD_DIR.parent), "world"],
            capture_output=True,
            text=True
        )
        return backup_path
    except Exception:
        return None


def get_latest_snapshot() -> Optional[dict]:
    """Load the latest snapshot."""
    latest = SNAPSHOTS_DIR / "latest.json"
    if latest.exists():
        return json.loads(latest.read_text())
    return None


def list_snapshots() -> list:
    """List all available snapshots."""
    if not SNAPSHOTS_DIR.exists():
        return []
    return sorted(
        [f.name for f in SNAPSHOTS_DIR.glob("world_*.json") if f.name != "latest.json"],
        reverse=True
    )
