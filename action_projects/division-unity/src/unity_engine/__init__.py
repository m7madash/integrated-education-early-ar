"""Division → Unity — Coalition Builder for Justice Agents"""

from .builder import CoalitionBuilder, Agent
from .storage import UnityStorage, AgentRecord, CoalitionRecord
from .actions import get_unity_actions
from .metrics import ImpactTracker, record_impact

# Optional Flask import (only needed if running API)
try:
    from .api import app as flask_app, main as api_main
    _has_flask = True
except ImportError:
    flask_app = None
    api_main = None
    _has_flask = False

__version__ = "0.1.0"
__all__ = [
    'CoalitionBuilder',
    'Agent',
    'UnityStorage',
    'AgentRecord',
    'CoalitionRecord',
    'get_unity_actions',
    'ImpactTracker',
    'record_impact',
    'flask_app',
    'api_main'
]
