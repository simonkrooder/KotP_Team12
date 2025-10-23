import csv
import os
import threading
from datetime import datetime
from typing import List, Dict, Optional

PENDING_ACTIONS_PATH = os.path.join(os.path.dirname(__file__), '../data/pending_actions.csv')
PENDING_ACTIONS_FIELDS = [
    'action_id', 'type', 'recipient_id', 'context', 'status', 'created_at', 'response'
]

_lock = threading.Lock()

def init_pending_actions_csv():
    if not os.path.exists(PENDING_ACTIONS_PATH):
        with open(PENDING_ACTIONS_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PENDING_ACTIONS_FIELDS)
            writer.writeheader()

def add_pending_action(action: Dict):
    action = action.copy()
    action.setdefault('created_at', datetime.utcnow().isoformat())
    action.setdefault('status', 'pending')
    with _lock:
        with open(PENDING_ACTIONS_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PENDING_ACTIONS_FIELDS)
            writer.writerow(action)

def get_pending_actions(recipient_id: Optional[str] = None, status: str = 'pending') -> List[Dict]:
    with _lock:
        with open(PENDING_ACTIONS_PATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            actions = [row for row in reader if (not recipient_id or row['recipient_id'] == recipient_id) and row['status'] == status]
    return actions

def update_action_response(action_id: str, response: str):
    rows = []
    with _lock:
        with open(PENDING_ACTIONS_PATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['action_id'] == action_id:
                    row['response'] = response
                    row['status'] = 'responded'
                rows.append(row)
        with open(PENDING_ACTIONS_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PENDING_ACTIONS_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

init_pending_actions_csv()
