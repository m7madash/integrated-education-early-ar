"""
Shared utilities for Abdullah's action projects.
Optimizes resource consumption: batch reads, caching, minimal logging.
"""

import os
import json
from pathlib import Path
from functools import lru_cache
from datetime import datetime
from typing import Dict, Any, Optional

# ============================================
# CACHING
# ============================================

class SimpleCache:
    """In-memory cache with TTL."""
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Any] = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = (value, datetime.now())

# Global cache instance
cache = SimpleCache(ttl_seconds=600)  # 10 minutes


# ============================================
# BATCH FILE READING
# ============================================

def read_project_docs(project_path: str, extensions: tuple = ('.md', '.txt', '.py', '.json')) -> Dict[str, str]:
    """
    Read all documentation files in a project at once.
    Returns dict: {filename: content}
    """
    cache_key = f"project_docs_{project_path}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    docs = {}
    project = Path(project_path)
    if not project.exists():
        return docs

    for file in project.rglob('*'):
        if file.is_file() and file.suffix in extensions:
            try:
                # Read only first 100KB per file to avoid memory blowup
                content = file.read_text(encoding='utf-8', errors='ignore')[:100_000]
                docs[file.name] = content
            except Exception:
                continue

    cache.set(cache_key, docs)
    return docs


def read_files_batch(paths: list) -> Dict[str, str]:
    """
    Read multiple files in one batch.
    paths: list of file paths
    Returns: {path: content}
    """
    cache_key = f"batch_{hash(tuple(sorted(paths)))}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    contents = {}
    for path in paths:
        try:
            p = Path(path)
            if p.exists():
                contents[path] = p.read_text(encoding='utf-8', errors='ignore')[:100_000]
        except Exception:
            contents[path] = ""

    cache.set(cache_key, contents)
    return contents


# ============================================
# CONFIG MANAGEMENT
# ============================================

@lru_cache(maxsize=1)
def get_global_config() -> Dict[str, Any]:
    """Load global config once."""
    config_path = Path('/root/.openclaw/workspace/config.json')
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            pass
    return {}


# ============================================
# LOGGING (Summary Only)
# ============================================

class SummaryLogger:
    """Log only summaries, not every step."""

    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def info(self, message: str, details: str = ""):
        """Log a summary line."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if details:
            line = f"[{timestamp}] INFO: {message} | {details}\n"
        else:
            line = f"[{timestamp}] INFO: {message}\n"
        # Append to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line)

    def warn(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{timestamp}] WARN: {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line)

    def error(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{timestamp}] ERROR: {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line)


def get_logger(project_name: str) -> SummaryLogger:
    """Get a logger for a specific project."""
    log_path = Path(f'logs/{project_name}/{datetime.now().strftime("%Y-%m-%d")}.log')
    return SummaryLogger(str(log_path))


# ============================================
# STRING HELPERS
# ============================================

def truncate(text: str, max_length: int = 200) -> str:
    """Truncate text intelligently."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
