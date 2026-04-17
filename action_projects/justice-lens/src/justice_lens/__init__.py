"""JusticeLens — Bias detection for agent decisions."""
__version__ = "0.1.0"
__author__ = "OpenClaw Action Projects — Injustice → Justice mission"

from .audit import BiasAuditor, audit_dataset

__all__ = ['BiasAuditor', 'audit_dataset']
