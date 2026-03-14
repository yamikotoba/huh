import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# VK peer/chat IDs to monitor. e.g., 2000000001,2000000002
_vk_peers = os.getenv("VK_PEER_IDS", "")
VK_PEER_IDS = [p.strip() for p in _vk_peers.split(",")] if _vk_peers else []

# Keywords to match in the messages
KEYWORDS = [
    "дз", "домашнее", "домашка", "задание", 
    "отмена", "отменили", "перенос", "перенесли",
    "важно", "внимание", "ко второй", "к третьей",
    "зачет", "экзамен", "автомат"
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
STATE_FILE = os.path.join(DATA_DIR, "state.json")

os.makedirs(DATA_DIR, exist_ok=True)
