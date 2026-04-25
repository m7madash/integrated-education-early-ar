🔄 **خطوات إعادة تشغيل OpenClaw Gateway:**

```bash
# Terminal commands:
openclaw gateway restart
sleep 2
openclaw status
```

**نتيجة متوقعة:**
- ✅ Gateway يعمل
- ✅ Config validation passes
- ✅ memorySearch.remote={} مُحمّل

---
إذا ظهر خطأ: "Invalid config" → تحقق من الملف:
`/root/.openclaw/openclaw.json` (يجب أن يحتوي على `"remote": {}`)

سُبْحَانَ رَبِّي الْعَلِيِّ
سُبْحَانَ رَبِّي الْعَظِيمِ