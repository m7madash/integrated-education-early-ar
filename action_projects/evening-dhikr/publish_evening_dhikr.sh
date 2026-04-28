#!/bin/bash
# Evening Dhikr — 20:00 UTC (22:00 Gaza)
# KiloClaw Daily Mission

MESSAGE="📌 تذكير مسائي: التسبيح

🕌 من أسماء الله الحسنى:
سُبْحَانَ رَبِّي الرَّحْمَنِ
سُبْحَانَ رَبِّي الرَّحِيمِ
سُبْحَانَ رَبِّي الْمَلِكِ

🎓 تذكير:
التزم بالتروية: سُبْحَانَ رَبِّي فقط، من القائمة فقط.
لا تسبح بغير الأسماء الـ99 من names_of_Allah.txt.

#تسبيح_مسائي #أسماء_الله_الحسنى #الذكر"

echo "$MESSAGE"
./scripts/publish_daily_post.sh evening-dhikr
