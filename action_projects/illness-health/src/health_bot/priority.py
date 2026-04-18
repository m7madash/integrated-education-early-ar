"""
Health Command Priority Engine
Determines urgency of health-related requests
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

class Priority(Enum):
    """Health request priority levels"""
    CRITICAL = 1   # Immediate (heart attack, severe bleeding, unconscious)
    URGENT = 2     # Within 1 hour (high fever child, severe pain, mental crisis)
    ROUTINE = 3    # Within 24 hours (general symptoms, medication questions)
    INFORMATIONAL = 4  # Low priority (wellness tips, diet)
    UNKNOWN = 5    # Unclear — needs clarification

@dataclass
class HealthRequest:
    """A health-related command/request"""
    text: str
    user_id: Optional[str] = None
    context: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.context is None:
            self.context = {}

class PriorityEngine:
    """Determines priority of health commands"""
    
    def __init__(self):
        # Critical keywords (must be exact or very close)
        self.critical_patterns = [
            "heart attack", "chemia", "نوبة قلبية", "جلطة",
            "severe bleeding", "نزيف شديد", " hemorrhage",
            "unconscious", "فاقد الوعي", "لا أتنفس",
            "can't breathe", "لا أستطيع التنفس", "ضيق تنفس حاد",
            "كسم", "كهرب", "صدمة",  # Gaza dialect emergencies
        ]
        
        # Urgent keywords
        self.urgent_patterns = [
            "high fever", "حمى عالية", "child", "طفل",
            "severe pain", "ألم شديد", " excruciating",
            "suicidal", "أريد الانتحار", "kill myself",
            "pregnancy", "حمل", "مضاعفات حمل",
            "chest pain", "ألم في الصدر",
        ]
        
        # Routine keywords
        self.routine_patterns = [
            "symptom", "عرج", "أعراض", "feeling sick",
            "medicine", "دواء", "medication", "علاج",
            "appointment", "موعد", "طبيب", "clinic",
            "test result", "نتيجة تحليل",
        ]
        
        # Informational keywords
        self.info_patterns = [
            "diet", "غذاء", "food", "أكل",
            "exercise", "رياضة", "tired", "تعب",
            "wellness", "صحة عامة", "نصائح",
            "prevention", "وقاية", "نصائح",
        ]
    
    def assess(self, request: HealthRequest) -> Priority:
        """Assess priority of a health request"""
        text_lower = request.text.lower()
        
        # Check critical (immediate)
        for pattern in self.critical_patterns:
            if pattern.lower() in text_lower:
                return Priority.CRITICAL
        
        # Check urgent
        for pattern in self.urgent_patterns:
            if pattern.lower() in text_lower:
                return Priority.URGENT
        
        # Check routine
        for pattern in self.routine_patterns:
            if pattern.lower() in text_lower:
                return Priority.ROUTINE
        
        # Check informational
        for pattern in self.info_patterns:
            if pattern.lower() in text_lower:
                return Priority.INFORMATIONAL
        
        # Default: unknown (ask for clarification)
        return Priority.UNKNOWN
    
    def get_response_time(self, priority: Priority) -> str:
        """Get recommended response time for priority level"""
        times = {
            Priority.CRITICAL: "**IMMEDIATE** — Call emergency services NOW",
            Priority.URGENT: "Within 1 hour — Seek urgent care",
            Priority.ROUTINE: "Within 24 hours — Schedule appointment",
            Priority.INFORMATIONAL: "When available — Educational response",
            Priority.UNKNOWN: "Need more info — Ask clarifying questions"
        }
        return times.get(priority, "Unknown priority")
    
    def suggest_action(self, request: HealthRequest, priority: Priority) -> Dict[str, Any]:
        """Suggest action based on priority"""
        actions = {
            Priority.CRITICAL: {
                "action": "EMERGENCY_PROTOCOL",
                "steps": [
                    "1. Ask for location (if not provided)",
                    "2. Call emergency services (if in Gaza: 101)",
                    "3. Provide immediate first aid instructions",
                    "4. Stay on line until help arrives"
                ],
                "escalate_to": "human_emergency_responder"
            },
            Priority.URGENT: {
                "action": "URGENT_TRIAGE",
                "steps": [
                    "1. Get symptoms details",
                    "2. Find nearest open clinic",
                    "3. Contact clinic to expect patient",
                    "4. Provide transport info"
                ],
                "escalate_to": "clinic_director"
            },
            Priority.ROUTINE: {
                "action": "SCHEDULE_CONSULTATION",
                "steps": [
                    "1. Log request with timestamp",
                    "2. Add to queue for doctor review",
                    "3. Send acknowledgment to patient",
                    "4. Schedule within 24h"
                ],
                "escalate_to": "medical_coordinator"
            },
            Priority.INFORMATIONAL: {
                "action": "PROVIDE_GUIDANCE",
                "steps": [
                    "1. Query knowledge base",
                    "2. Send verified health tips",
                    "3. Link to trusted sources (WHO, MOH)",
                    "4. Offer to escalate if needed"
                ],
                "escalate_to": None
            },
            Priority.UNKNOWN: {
                "action": "CLARIFY",
                "steps": [
                    "1. Ask clarifying questions",
                    "2. Determine symptoms severity",
                    "3. Re-assess priority after clarification"
                ],
                "escalate_to": None
            }
        }
        return actions.get(priority, {"action": "UNKNOWN", "steps": [], "escalate_to": None})
