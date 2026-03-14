import json
import logging
import time
import os
import vk_api

from config import VK_TOKEN, VK_PEER_IDS, DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    if not VK_TOKEN or not VK_PEER_IDS:
        logging.error("VK_TOKEN or VK_PEER_IDS not set in .env")
        return

    logging.info("Authorizing in VK...")
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
    except Exception as e:
        logging.error(f"VK Authorization failed: {e}")
        return

    week_ago = int(time.time()) - 7 * 24 * 3600
    
    new_messages = []
    
    for peer_id in VK_PEER_IDS:
        logging.info(f"Fetching messages for peer_id: {peer_id}")
        try:
            response = vk.messages.getHistory(peer_id=peer_id, count=200)
            items = response.get("items", [])
            
            for msg in items:
                # Фильтруем сообщения старше 7 дней
                if msg.get("date", 0) < week_ago:
                    continue
                    
                msg_id = msg.get("id") or msg.get("conversation_message_id")
                uid = f"{peer_id}_{msg_id}"
                
                textParts = [msg.get("text", "")]
                for fwd in msg.get("fwd_messages", []):
                    textParts.append(fwd.get("text", ""))
                text = "\n".join(t for t in textParts if t).strip()
                if text:
                    new_messages.append({
                        "uid": uid,
                        "text": text,
                        "date": msg.get("date")
                    })
                    
        except Exception as e:
            logging.error(f"Failed to fetch from {peer_id}: {e}")

    # Сортируем от старых к новым для удобного хронологического чтения
    new_messages.sort(key=lambda x: x["date"])
    
    output_path = os.path.join(DATA_DIR, "to_analyze.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        if not new_messages:
            f.write("Новых сообщений за последнее время нет.\n")
        else:
            for m in new_messages:
                readable_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(m['date']))
                f.write(f"--- ВК СООБЩЕНИЕ (ID: {m['uid']} | ДАТА: {readable_date}) ---\n")
                f.write(f"{m['text']}\n\n")
                
    logging.info(f"Found {len(new_messages)} new messages to analyze. Saved to {output_path}")
    print(f"Готово. Количество новых сообщений для анализа моделью: {len(new_messages)}.")
    print(f"Файл: {output_path}")

if __name__ == "__main__":
    main()
