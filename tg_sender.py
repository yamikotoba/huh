import argparse
import sys
import requests
import logging

from config import TG_BOT_TOKEN, TG_CHAT_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()

def main():
    parser = argparse.ArgumentParser(description="Send message to Telegram")
    parser.add_argument("--text", type=str, help="Text to send directly (optional)")
    parser.add_argument("--file", type=str, help="File containing text to send (рекомендуется для модели)")
    
    args = parser.parse_args()
    
    text = ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        except Exception as e:
            logging.error(f"Could not read file {args.file}: {e}")
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        logging.error("Не указан текст. Используйте --text или --file")
        sys.exit(1)
        
    if text:
        try:
            send_telegram_message(text)
            logging.info("Успешно отправлено в Telegram.")
        except Exception as e:
            logging.error(f"Ошибка при отправке: {e}")

if __name__ == "__main__":
    main()
