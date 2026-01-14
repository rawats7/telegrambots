import json
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ChatJoinRequestHandler
)

# ================= CONFIG =================

BOT_TOKEN = "8337961200:AAGUa4OvFUB6lkUPbW8IVFA5WscXiYruN2E"
ADMIN_ID = 8431502772  # <-- replace with YOUR Telegram user ID
AUTO_APPROVE_DELAY = 200# seconds

DATA_FILE = "users.json"

WELCOME_MESSAGES = {
    "default": (
        "👋 Hello {name}!\n\n"
        "We received your request to join our channel ✅\n"
        "You will bea approved shortly.\n\n"
        "⏳ Please wait..."
    ),
    # Example invite links
    "ads": (
        "🔥 Welcome {name}!\n\n"
        "Thanks for joining from our Ads.\n"
        "Approval in progress ⏳"
    ),
    "website": (
        "🌐 Hi {name}!\n\n"
        "Thanks for joining via our Website.\n"
        "Please wait for approval."
    ),
}

# ================= UTILITIES =================

def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_user(data):
    users = load_users()
    users.append(data)
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

def detect_link_type(invite_link: str):
    if not invite_link:
        return "default"
    if "ads" in invite_link:
        return "ads"
    if "web" in invite_link:
        return "website"
    return "default"

# ================= HANDLER =================

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    req = update.chat_join_request
    user = req.from_user

    invite_link = req.invite_link.invite_link if req.invite_link else ""
    link_type = detect_link_type(invite_link)

    welcome_text = WELCOME_MESSAGES.get(
        link_type, WELCOME_MESSAGES["default"]
    ).format(name=user.first_name)

    # 1️⃣ Send welcome message
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_text
        )
    except:
        pass

    # 2️⃣ Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📥 New Join Request\n\n"
            f"👤 Name: {user.first_name}\n"
            f"🆔 ID: {user.id}\n"
            f"🔗 Source: {link_type}\n"
            f"⏳ Auto-approve in {AUTO_APPROVE_DELAY}s"
        )
    )

    # 3️⃣ Save user data
    save_user({
        "user_id": user.id,
        "name": user.first_name,
        "username": user.username,
        "source": link_type,
        "time": datetime.now().isoformat()
    })

    # 4️⃣ Auto-approve after delay
    await asyncio.sleep(AUTO_APPROVE_DELAY)
    await req.approve()

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(join_request))
    print("🤖 Advanced Join Bot Running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
