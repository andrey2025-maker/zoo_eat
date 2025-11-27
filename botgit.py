import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv

# ===== Загрузка переменных окружения =====
load_dotenv()  # Подгружаем .env

# ===== Настройки =====
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHAT_ID = -1003455001864
TARGET_CHAT_ID = -1003158225734

# Слова, которые нужно удалить
REMOVE_WORDS = ["Груша", "Ананас"]

# Замена на "красивые" названия
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

# Эмодзи для фруктов
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

# Какие слова делать жирными
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
    "Желудь": False,
}

# =====================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


def clean_text(text: str) -> str:
    """Удаляет слова из REMOVE_WORDS и эмодзи."""
    for word in REMOVE_WORDS:
        pattern = r".{0,3}" + re.escape(word)
        text = re.sub(pattern, "", text)
    # Удаляем все эмодзи из текста
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
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text).strip()


def escape_markdown(text: str) -> str:
    """Экранируем специальные символы MarkdownV2."""
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


def format_with_emoji_markdown(text: str) -> str:
    """Форматирование текста с эмодзи и жирным через MarkdownV2."""
    lines = text.split("\n")
    result_lines = []

    for line in lines:
        match = re.match(r"(x\d+)\s*(.+)", line)
        if match:
            quantity = match.group(1)
            item_orig = match.group(2).strip()

            # Замена на красивое название
            item_cleaned = REPLACE_WORDS.get(item_orig, item_orig)

            # Эмодзи
            emoji = EMOJI_MAP.get(item_cleaned, "❓")

            # MarkdownV2 жирность
            if BOLD_FRUITS.get(item_cleaned, False):
                item_display = f"*{item_cleaned}*"
            else:
                item_display = item_cleaned

            # Формируем строку
            text_line = f"{emoji} {quantity} {item_display} — stock"
            # Экранируем MarkdownV2 символы
            text_line = escape_markdown(text_line)
            result_lines.append(text_line)

    return "\n".join(result_lines)


@dp.message()
async def forward_zoo_news(message: types.Message):
    if message.chat.id != SOURCE_CHAT_ID:
        return

    if not message.text.startswith("ZooNews: Еда в магазине"):
        return

    content = message.text[len("ZooNews: Еда в магазине"):].strip()
    if not content:
        return

    cleaned_content = clean_text(content)
    final_text = format_with_emoji_markdown(cleaned_content)

    if not final_text:
        print("Нет строк с товарами для отправки")
        return

    try:
        await bot.send_message(
            TARGET_CHAT_ID,
            final_text,
            parse_mode="MarkdownV2"
        )
        print(f"Отправлено:\n{final_text}\n")
    except TelegramAPIError as e:
        print(f"Ошибка при отправке: {e}")


async def main():
    print("Бот запущен. Жду новые сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())