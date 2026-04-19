"""
Division → Unity: Coalition Builder for Justice Agents
Match agents by mission, propose coalitions, suggest unity actions.
"""

from .builder import CoalitionBuilder, Agent
from .actions import get_unity_actions

__version__ = "0.1.0"
__all__ = ['CoalitionBuilder', 'Agent', 'get_unity_actions']
