"""
Health Triage System
Processes incoming health commands and routes by priority
"""

from .priority import PriorityEngine, HealthRequest, Priority
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

class HealthTriage:
    """Main triage system for health requests"""
    
    def __init__(self, knowledge_base_path: str = None):
        self.priority_engine = PriorityEngine()
        self.knowledge_base = self._load_knowledge(knowledge_base_path)
        
    def _load_knowledge(self, path: str = None):
        """Load medical knowledge base (simple JSON for now)"""
        if path:
            with open(path, 'r') as f:
                return json.load(f)
        return {
            "emergency_numbers": {
                "gaza": "101",
                "west_bank": "101",
                "general": "911"
            },
            "common_conditions": {
                "fever": {"treatment": "paracetamol", "when_to_see_doctor": "fever > 39°C lasting > 3 days"},
                "headache": {"treatment": "rest, hydration", "when_to_see_doctor": "severe, sudden, with fever"},
                "cough": {"treatment": "honey, fluids", "when_to_see_doctor": "blood in mucus, > 2 weeks"}
            }
        }
    
    def process_request(self, text: str, user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a health request and return priority-based response"""
        
        # Create request object
        request = HealthRequest(
            text=text,
            user_id=user_id,
            context=context or {}
        )
        
        # Assess priority
        priority = self.priority_engine.assess(request)
        
        # Get action plan
        action_plan = self.priority_engine.suggest_action(request, priority)
        
        # Build response
        response = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "request": text,
            "priority": priority.name,
            "priority_level": priority.value,
            "response_time": self.priority_engine.get_response_time(priority),
            "action_plan": action_plan,
            "next_steps": action_plan["steps"],
            "requires_human": priority in [Priority.CRITICAL, Priority.URGENT]
        }
        
        # Log for audit
        self._log_decision(response)
        
        return response
    
    def _log_decision(self, response: Dict[str, Any]):
        """Log triage decision for learning"""
        log_entry = f"[{response['timestamp']}] PRIORITY={response['priority']} USER={response['user_id']} REQUEST={response['request'][:50]}"
        # In production: write to structured log file
        print(f"📋 Triage log: {log_entry}")
