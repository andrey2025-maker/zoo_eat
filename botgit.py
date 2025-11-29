import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv

# ===== Загружаем токен из .env =====
load_dotenv()
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# ===== Чаты =====
SOURCE_CHANNEL_ID = -1003291808303  # Канал, откуда бот читает
TARGET_CHAT_ID = -1003294880580     # Группа, куда отправлять
TARGET_CHANNEL_ID = -1003268009539  # Канал, куда отправлять

# ID темы внутри группы
TARGET_THREAD_ID = 4

# ===== Настройки =====
REMOVE_WORDS = ["Груша", "Ананас"]

REPLACE_WORDS = {
    "Манго": "Gold Mango",
    "Драконий фрукт": "Dragon Fruit",
    "КровавыйКамень Цукад": "Bloodstone Cycad",
    "Зеленый Кристалл": "Colossal Pinecone",
    "Киви": "Франкен Киви",
    "Тыква": "Тыква",
    "Дуриан": "Дуриан",
    "Конфета": "Candy Corn",
    "Ракушка": "Deepsea Pearl",
    "Вольт Юрский": "Volt Gingko",
    "Клюква": "Клюква",
    "Желудь": "Желудь",
}

EMOJI_MAP = {
    "Gold Mango": "🥭",
    "Dragon Fruit": "🐲",
    "Bloodstone Cycad": "🩸",
    "Colossal Pinecone": "❇️",
    "Франкен Киви": "🥝",
    "Тыква": "🎃",
    "Дуриан": "❄️",
    "Candy Corn": "🍬",
    "Deepsea Pearl": "🐚",
    "Volt Gingko": "⚡️🦕",
    "Клюква": "🍒",
    "Желудь": "🌰",
}

BOLD_FRUITS = {
    "Gold Mango": False,
    "Dragon Fruit": False,
    "Bloodstone Cycad": False,
    "Colossal Pinecone": False,
    "Франкен Киви": True,
    "Тыква": True,
    "Дуриан": True,
    "Candy Corn": True,
    "Deepsea Pearl": True,
    "Volt Gingko": True,
    "Клюква": True,
    "Желудь": True,
}

# ===== Инициализация бота =====
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ===== Функции обработки =====
def clean_text(text: str) -> str:
    """Удаляет запрещённые слова и эмодзи."""
    for word in REMOVE_WORDS:
        pattern = r".{0,3}" + re.escape(word)
        text = re.sub(pattern, "", text)

    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U00002600-\U000026FF"
        "\U00002B00-\U00002BFF"
        "\U0001FA70-\U0001FAFF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()


def format_with_emoji(text: str) -> str:
    """Добавляет эмодзи и жирный текст через HTML."""
    lines = text.split("\n")
    result = ""
    for line in lines:
        match = re.match(r"(x\d+)\s*(.+)", line)
        if not match:
            continue

        qty = match.group(1)
        item_raw = match.group(2).strip()

        for key, val in REPLACE_WORDS.items():
            if key in item_raw:
                item = val
                break
        else:
            item = item_raw

        emoji = EMOJI_MAP.get(item, "❓")
        bold = BOLD_FRUITS.get(item, False)
        name = f"<b>{item}</b>" if bold else item

        result += f"{emoji} {qty} {name} — stock\n"

    return result.strip()


# ===== Хэндлер для сообщений канала =====
@dp.channel_post()
async def handle_channel_post(message: types.Message):

    if message.chat.id != SOURCE_CHANNEL_ID:
        return

    content = message.text or message.caption
    if not content or not content.startswith("ZooNews: Еда в магазине"):
        return

    content = content.replace("ZooNews: Еда в магазине", "").strip()
    if not content:
        return

    cleaned = clean_text(content)
    final = format_with_emoji(cleaned)

    if not final:
        print("Нет данных для отправки")
        return

    # ==== ОТПРАВКА В ГРУППУ ====
    try:
        await bot.send_message(
            TARGET_CHAT_ID,
            final,
            parse_mode="HTML",
            message_thread_id=TARGET_THREAD_ID
        )
        print("Отправлено в группу.")
    except TelegramAPIError as e:
        print("Ошибка отправки в группу:", e)

    # ==== ОТПРАВКА В КАНАЛ ====
    try:
        await bot.send_message(
            TARGET_CHANNEL_ID,
            final,
            parse_mode="HTML"
        )
        print("Отправлено в канал.")
    except TelegramAPIError as e:
        print("Ошибка отправки в канал:", e)


# ===== Главная функция =====
async def main():
    print("Бот запущен и слушает канал...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())