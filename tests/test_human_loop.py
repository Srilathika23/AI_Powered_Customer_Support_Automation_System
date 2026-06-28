import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.intent import intent_classification_node
from src.state import CustomerSupportState


class HumanLoopApprovalTests(unittest.TestCase):
    def test_cancel_subscription_requires_human_approval(self) -> None:
        state: CustomerSupportState = {
            "customer_id": "CUST-001",
            "customer_name": "Alice",
            "query": "Please cancel my subscription",
            "intent": None,
            "department": None,
            "retrieved_context": None,
            "conversation_history": [],
            "requires_approval": False,
            "approval_status": None,
            "draft_response": None,
            "supervisor_notes": None,
            "final_response": None,
            "error": None,
        }

        updated = intent_classification_node(state)

        self.assertTrue(updated["requires_approval"])
        self.assertEqual(updated["approval_status"], "pending")

    def test_close_account_requires_human_approval(self) -> None:
        state: CustomerSupportState = {
            "customer_id": "CUST-002",
            "customer_name": "Bob",
            "query": "I want to close my account",
            "intent": None,
            "department": None,
            "retrieved_context": None,
            "conversation_history": [],
            "requires_approval": False,
            "approval_status": None,
            "draft_response": None,
            "supervisor_notes": None,
            "final_response": None,
            "error": None,
        }

        updated = intent_classification_node(state)

        self.assertTrue(updated["requires_approval"])
        self.assertEqual(updated["approval_status"], "pending")


if __name__ == "__main__":
    unittest.main()
