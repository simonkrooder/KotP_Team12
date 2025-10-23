import unittest
import os
import uuid
from datetime import datetime, timedelta
from src.pending_actions import add_pending_action, get_pending_actions, update_action_response, PENDING_ACTIONS_PATH

class TestPendingActions(unittest.TestCase):
    def setUp(self):
        # Clean up the CSV before each test
        if os.path.exists(PENDING_ACTIONS_PATH):
            os.remove(PENDING_ACTIONS_PATH)
        from src.pending_actions import init_pending_actions_csv
        init_pending_actions_csv()

    def test_add_and_get_pending_action(self):
        action_id = str(uuid.uuid4())
        add_pending_action({
            'action_id': action_id,
            'type': 'send_notification',
            'recipient_id': 'user1',
            'context': 'Test context',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'response': ''
        })
        actions = get_pending_actions(recipient_id='user1', status='pending')
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['action_id'], action_id)

    def test_update_action_response(self):
        action_id = str(uuid.uuid4())
        add_pending_action({
            'action_id': action_id,
            'type': 'send_notification',
            'recipient_id': 'user2',
            'context': 'Test context 2',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'response': ''
        })
        update_action_response(action_id, 'My response')
        actions = get_pending_actions(recipient_id='user2', status='responded')
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['response'], 'My response')

if __name__ == '__main__':
    unittest.main()
