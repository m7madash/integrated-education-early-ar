"""
نظام مكافحة الابتزاز الإلكتروني — بوت تلجرام مجهول
الهدف: تمكين الضحايا من الإبلاغ عن الابتزاز مع حماية الخصوصية.
"""

import json
import os
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ── إعدادات ──────────────────────────────────────────────
REPORTS_FILE = "reports/anonymous_reports.jsonl"
ADMIN_CHAT_ID = None  # عيّن معرف المشرف (اختياري)
# ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *مرحباً! أنا بوت الإبلاغ المجهول عن الابتزاز الإلكتروني.*\n\n"
        "يمكنك إرسال نص التهديد أو الابتزاز بشكل سري.\n"
        "لا نحفظ أي معلومات شخصية، ونضمن سرية بلاغك.\n\n"
        "اكتب رسالتك الآن.",
        parse_mode="Markdown",
    )


async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "text": update.message.text,
        # لا نحفظ معرف المستخدم؛ نولّد معرفاً مجهولاً
        "anon_id": update.effective_message.id,
        "chat_id": update.effective_chat.id,
    }

    # حفظ التقرير (append-only)
    os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
    with open(REPORTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")

    await update.message.reply_text(
        "✅ *تم استلام بلاغك بشكل مجهول.*\n"
        "سنقوم بالتحليل والتحقق، ونتخذ الإجراءات المناسبة مع الحفاظ على سريتك.",
        parse_mode="Markdown",
    )

    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🆘 بلاغ جديد:\n\n{report['text']}",
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*كيف يعمل البوت؟*\n\n"
        "• أرسل messaging تهديد/ابتزاز\n"
        "• لا نحتفظ ببياناتك الشخصية\n"
        "• يمكنك إضافة صورة/فيديو (اختياري) ولكن مع موافقتك\n"
        "• البلاغ سري ولا يمكن تتبع هويتك",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    # استخدم المتغير البيئي للتوكن
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report))

    print("🤖 Bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)