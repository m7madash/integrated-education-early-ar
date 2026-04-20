"""
Psych Ops Messenger — Tool 4 of Nuclear Justice

Generates ethical psychological messages for influence campaigns.
Themes: legacy, family, religion, international pressure.
All content nonviolent, factual, reversible.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class MessageTemplate:
    theme: str
    tone: str
    content: str
    expected_impact: str

class MessageGenerator:
    """Creates tailored messages based on target profile."""

    def __init__(self):
        self.templates = self._load_default_templates()

    def _load_default_templates(self) -> dict:
        return {
            ("legacy", "respectful"): MessageTemplate(
                theme="legacy", tone="respectful",
                content="History will judge your decision on nuclear weapons. Will you be remembered as the leader who preserved peace for generations, or the one who risked global annihilation? The choice is yours.",
                expected_impact="long-term_legacy_reflection"
            ),
            ("family", "hopeful"): MessageTemplate(
                theme="family", tone="hopeful",
                content="Your children's future depends on a world free from nuclear threats. Imagine their inheritance: a planet safe from the shadow of annihilation. That legacy begins with your courage to disarm.",
                expected_impact="emotional_family_connection"
            ),
            ("religion", "moral"): MessageTemplate(
                theme="religion", tone="moral",
                content="All major world religions — Islam, Christianity, Judaism, Buddhism, Hinduism — teach the sanctity of innocent life. Nuclear weapons cannot discriminate between combatant and civilian; their use contradicts divine commandment. As a leader, you are called to protect life, not threaten it.",
                expected_impact="moral_dissonance"
            ),
            ("international_community", "firm"): MessageTemplate(
                theme="international_community", tone="firm",
                content="The global community stands united against nuclear proliferation. Continued defiance will isolate your nation diplomatically and economically. Cooperation, not confrontation, is the path to prosperity and security.",
                expected_impact="political_pressure"
            ),
            ("scientific", "rational"): MessageTemplate(
                theme="scientific", tone="rational",
                content="Nuclear winter models show that even a limited nuclear exchange could cause global famine, killing billions. The science is clear: there are no winners in nuclear war. Rational actors choose disarmament.",
                expected_impact="cognitive_rationalization"
            )
        }

    def generate(self, target_values: list, theme: str = None, tone: str = "respectful") -> Optional[MessageTemplate]:
        """Generate a message for a target based on their known values."""
        if theme:
            key = (theme, tone)
            return self.templates.get(key)
        # Auto-select theme based on target values
        if "family" in target_values:
            return self.templates[("family", "hopeful")]
        if "religion" in target_values or "faith" in target_values:
            return self.templates[("religion", "moral")]
        if "legacy" in target_values or "history" in target_values:
            return self.templates[("legacy", "respectful")]
        # default
        return self.templates[("international_community", "firm")]

    def customize_message(self, template: MessageTemplate, target_name: str, title: str) -> str:
        """Insert target's name/title into message template."""
        content = template.content
        content = content.replace("your decision", f"{title}'s decision")
        content = content.replace("your nation", "your nation")
        content = content.replace("your children", "your children")
        content = content.replace("you", title)
        return content

if __name__ == "__main__":
    gen = MessageGenerator()
    msg = gen.generate(["family", "legacy"], theme="family")
    print(f"Theme: {msg.theme} | Tone: {msg.tone}")
    print(f"Content: {msg.content}")
