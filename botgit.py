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

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


def clean_text(text: str) -> str:
    """Удаляет слова из REMOVE_WORDS и эмодзи."""
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
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text).strip()


def format_with_emoji(text: str):
    """Форматирование текста с эмодзи и жирным шрифтом через HTML."""
    lines = text.split("\n")
    result_text = ""

    for line in lines:
        match = re.match(r"(x\d+)\s*(.+)", line)
        if match:
            quantity = match.group(1)
            item_orig = match.group(2).strip()

            for key in REPLACE_WORDS:
                if key in item_orig:
                    item_cleaned = REPLACE_WORDS[key]
                    break
            else:
                item_cleaned = item_orig

            print(f"Обрабатываем: '{item_orig}' -> '{item_cleaned}'")

            emoji = EMOJI_MAP.get(item_cleaned, "❓")

            is_bold = BOLD_FRUITS.get(item_cleaned, False)
            display_name = f"<b>{item_cleaned}</b>" if is_bold else item_cleaned

            text_line = f"{emoji} {quantity} {display_name} — stock"
            result_text += text_line + "\n"

    return result_text.strip()


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
    final_text = format_with_emoji(cleaned_content)

    if not final_text:
        print("Нет строк с товарами для отправки")
        return

    try:
        await bot.send_message(
            TARGET_CHAT_ID,
            final_text,
            parse_mode="HTML"  # <--- HTML будет работать
        )
        print(f"Отправлено:\n{final_text}\n")
    except TelegramAPIError as e:
        print(f"Ошибка при отправке: {e}")


async def main():
    print("Бот запущен. Жду новые сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())