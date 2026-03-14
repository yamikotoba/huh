import os
import json
import logging
from dotenv import load_dotenv
from config import DATA_DIR
from tg_sender import send_telegram_message
import google.generativeai as genai

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Настройка API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY is not set.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Инструкция для модели (Системный промпт)
# Мы просим модель вернуть JSON, чтобы скрипт мог программно перебрать важные сообщения и отправить их.
SYSTEM_PROMPT = """
Ты — интеллектуальный ассистент студента. Твоя общая задача — находить важную учебную информацию в новых сообщениях ВКонтакте.

Тебе на вход подаются переписки (разделенные '--- ВК СООБЩЕНИЕ (ID: ...) ---').
Тщательно проанализируй их и отбери только:
1. Домашние задания: ищи паттерны (указание предмета/даты, после чего идет пояснение задания). Игнорируй просто вопросы студентов из разряда "Что задали?".
2. Организационная информация: отмены пар, переносы, зачеты, экзамены, автоматы.

Игнорируй обычную студенческую болтовню.

ТВОЙ ОТВЕТ ДОЛЖЕН БЫТЬ СТРОГО В ФОРМАТЕ JSON — списком объектов с одним полем "text" (форматированный HTML текст для Telegram-бота).
Используй теги <b>Текст</b> для выделения важного и <i>Текст</i> для предмета/примечаний. Заменяй < и > на &lt; и &gt;.

ПРИМЕР ТВОЕГО ВЫХОДА (просто JSON и ничего больше):
[
  {
    "text": "🚨 <b>Важное сообщение: Домашка!</b>\n<i>Дз по пупр:</i>\nПодготовить сочинение по теме \"My favourite drink\"..."
  },
  {
    "text": "🚨 <b>Внимание: Перенос пары!</b>\nЗавтрашняя лекция ко второй паре будет в аудитории 404."
  }
]
"""

def analyze_and_send():
    file_path = os.path.join(DATA_DIR, "to_analyze.txt")
    if not os.path.exists(file_path):
        logging.info("Файл to_analyze.txt не найден. Завершение.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content or "Новых сообщений за последнее время нет" in content:
        logging.info("Нет новых сообщений для анализа.")
        return

    logging.info("Отправка сообщений в Gemini для анализа...")
    model = genai.GenerativeModel('gemini-2.5-flash-8b', system_instruction=SYSTEM_PROMPT)
    
    try:
        response = model.generate_content(
            content,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        # Парсим ответ как JSON
        results = json.loads(response.text)
        
        if not results:
            logging.info("Модель не нашла важных сообщений.")
            return

        logging.info(f"Найдено {len(results)} важных сообщений. Начинаем отправку...")
        
        for msg_item in results:
            text = msg_item.get("text")
            if text:
                send_telegram_message(text)
                logging.info("Отправлено уведомление в Telegram.")
                
    except Exception as e:
        logging.error(f"Ошибка при обращении к Gemini или парсинге JSON: {e}")

if __name__ == "__main__":
    analyze_and_send()
