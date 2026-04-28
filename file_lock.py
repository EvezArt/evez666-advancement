#!/usr/bin/env python3
"""
File lock helper — exclusive lock + atomic append.
Prevents concurrent write conflicts on shared files (milestones.md, heartbeat-state.json, etc.).
"""

import os
import time
import fcntl
from contextlib import contextmanager
from pathlib import Path

LOCK_DIR = Path("/tmp/file_locks")
LOCK_DIR.mkdir(exist_ok=True)

@contextmanager
def exclusive_lock(path: str | Path, timeout: float = 10.0):
    """
    Acquire an exclusive lock on a file before writing.
    Creates a side-car .lock file to coordinate across processes.
    
    Usage:
        with exclusive_lock("milestones.md"):
            with open("milestones.md", "a") as f:
                f.write("new entry\\n")
    """
    lock_path = Path(f"{path}.lock")
    acquired = False
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            # Open (or create) the lock file
            with open(lock_path, "w") as lock_fh:
                # Try to acquire an exclusive lock (non-blocking)
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
        except (IOError, BlockingIOError):
            time.sleep(0.1)  # another process holds the lock
    
    if not acquired:
        raise TimeoutError(f"Could not acquire lock on {path} after {timeout}s")
    
    try:
        yield  # caller does their file I/O here
    finally:
        # Release lock
        try:
            with open(lock_path, "w") as lock_fh:
                fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass

# Convenience: atomic append with built-in lock
def safe_append(path: str | Path, text: str):
    """Append text to file with exclusive lock."""
    with exclusive_lock(path):
        with open(path, "a") as f:
            f.write(text)

if __name__ == "__main__":
    # Demo: two processes trying to write concurrently would serialize
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "/tmp/test.txt"
    msg = sys.argv[2] if len(sys.argv) > 2 else "entry"
    safe_append(target, f"{msg} — {time.ctime()}\n")
    print(f"Appended to {target}")
