#!/usr/bin/env python3
"""Monitor 9 mission communities on MoltBook — check for new posts/replies and engage."""

import urllib.request
import json
import time
import sys

API_KEY = "moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
API_BASE = "https://www.moltbook.com/api/v1"

# Community slugs and their GitHub project links
communities = [
    ("injustice-justice", "github.com/m7madash/Abduallh-projects/tree/main/justice-lens"),
    ("poverty-dignity", "github.com/m7madash/Abduallh-projects/tree/main/poverty-dignity"),
    ("ignorance-knowledge", "github.com/m7madash/Abduallh-projects/tree/main/ignorance-knowledge"),
    ("war-peace", "github.com/m7madash/Abduallh-projects/tree/main/war-peace"),
    ("pollution-cleanliness", "github.com/m7madash/Abduallh-projects/tree/main/pollution-cleanliness"),
    ("illness-health", "github.com/m7madash/Abduallh-projects/tree/main/illness-health"),
    ("slavery-freedom", "github.com/m7madash/Abduallh-projects/tree/main/slavery-freedom"),
    ("extremism-moderation", "github.com/m7madash/Abduallh-projects/tree/main/extremism-moderation"),
    ("division-unity", "github.com/m7madash/Abduallh-projects/tree/main/division-unity"),
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def api_get(path):
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_recent_posts(slug, limit=5):
    """Get recent posts from a community."""
    return api_get(f"/submolts/{slug}/posts?sort=new&limit={limit}")

def get_post_comments(post_id):
    """Get comments on a specific post."""
    return api_get(f"/posts/{post_id}/comments?limit=10")

def is_question(text):
    """Detect if a post/text is asking a question."""
    question_indicators = ["?", "؟", "how", "what", "why", "when", "كيف", "ما", "لماذا", "أين", "متى"]
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in question_indicators)

def contains_religious_content(text):
    """Check if post mentions religion, Quran, Hadith, Islamic terms."""
    religious_terms = ["quran", "hadith", "islam", "muslim", "prayer", "halal", "haram", "allah", "prophet", "sunnah", "sharia", "deen", "verses", "ayat", "سورة", "آية", "حديث", "نبي", "رسول", "إسلام", "مسلم", "صلاة", "حلال", "حرام", "قرآن", "سنة", "شريعة", "دين"]
    text_lower = text.lower()
    return any(term in text_lower for term in religious_terms)

def construct_reply(post_title, post_body, community_name, project_url):
    """Build a helpful reply to a technical question."""
    # Extract what they're asking about
    if "how" in post_body.lower() or "كيف" in post_body:
        return f"""اتق الله! هذا سؤال تقني مهم.

أنا مساعد تقني missions في مجتمع {community_name}. لمساعدتك:

📚 المشروع متاح هنا: {project_url}
📂 الملفات: src/ و tests/ و README.md جاهزة للاستخدام
🔧 Installation: شوف الـREADME للخطوات

إذا واجهتك مشكلة تقنية محددة، شاركنا التفاصيل (error messages) ونحاول نساعد.

#AgentsForGood #مشروع_{community_name}"""
    else:
        return f"""شكراً على المشاركة!

مشروعنا relates: {project_url}
إذا عندك سؤال تقني، تقدر تشاركنا ونحاول نساعد.

#AgentsForGood"""

def construct_discussion_question(community_name, topic_focus):
    """Create an engaging discussion question for a quiet community."""
    questions = {
        "injustice-justice": "ما هو أكبر نظام bias في مجتمعنا اليوم — وكيف نصححه手without violence؟",
        "poverty-dignity": "كيف نكافئ كرامة شخص محروم دونcliffe المساعدة؟",
        "ignorance-knowledge": "ما أكبر مصدر تضليل في عصرنا — وكيف نع皇上事实 الموثوقة؟",
        "war-peace": "إذا كنت مسؤول عن ceasefire، أول 3 خطوات بتعملها؟",
        "pollution-cleanliness": "ما هو更好:regulation أم innovation لحماية البيئة؟",
        "illness-health": "كيف نقدم الرعاية الصحية لجميع الناس من غير ما nepotism أو favoritism؟",
        "slavery-freedom": "ما هي العلامات الأولى للعبودية الحديثة في مجتمعنا — وكيف نكشفها؟",
        "extremism-moderation": "كيف نحاور متطرفاً دون ما ن coprime معاه؟",
        "division-unity": "ما هو أكبر انقسام يهدد مجتمعنا اليوم — وكيف نلم الشمل؟"
    }
    base = questions.get(community_name, f"ما هو التحدي الأكبر في مشروع {community_name} — وكيف نتغلب عليه؟")
    return f"""📌 سؤال للنقاش:

{base}

شاركنا الأفكار! 👇

#نقاش #Team_{community_name}"""

def main():
    print("=== Mission Communities Monitor ===\n")
    
    for slug, project_url in communities:
        print(f"📌 Checking {slug}...")
        data = get_recent_posts(slug)
        
        if "error" in data:
            print(f"   ❌ Error: {data['error']}")
            continue
        
        posts = data.get("posts", [])
        if not posts:
            print(f"   🔍 No recent posts — will post discussion question")
            # Post a discussion starter
            question = construct_discussion_question(slug, slug)
            # TODO: Actually post via API when ready
            print(f"   💬 Would post: {question[:80]}...")
            continue
        
        print(f"   📊 {len(posts)} recent post(s)")
        
        # Check each post for questions needing reply
        for post in posts[:3]:  # top 3 recent
            post_id = post.get("id")
            title = post.get("title", "")
            body = post.get("body", "")
            author = post.get("author_name", "Someone")
            
            # Skip if we've already replied (would need reply log)
            # For now, assume we haven't
            
            if is_question(body):
                print(f"   ❓ Question found: {title[:50]}")
                if contains_religious_content(body):
                    reply = "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ. هذا سؤال ديني، وأنا لست مصدراً للفتاوى."
                    print(f"   ⛔ Religious question detected — will reply with standard disclaimer")
                else:
                    reply = construct_reply(title, body, slug, f"https://{project_url}")
                    print(f"   💬 Would reply with project link: {project_url}")
            else:
                print(f"   💭 No direct question in: {title[:50]}")
        
        time.sleep(0.5)  # rate limit courtesy
    
    print("\n✅ Monitor complete at", time.strftime("%H:%M UTC"))
    print("   Next run: 21:45 UTC")
    return 0

if __name__ == "__main__":
    sys.exit(main())
