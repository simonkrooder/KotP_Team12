import unittest
import os
import pandas as pd
from src.agent_main import AgentOrchestrator
from src.data_access import get_audit_trail_for_mutation, write_csv, read_csv

class TestIntegrationWorkflow(unittest.TestCase):
    def setUp(self):
        # Create a minimal mutation in hr_mutations.csv
        self.mutation_id = 'test1234'
        hr_mut_df = pd.DataFrame([
            {
                "MutationID": self.mutation_id,
                "Timestamp": "2025-10-23T10:00:00",
                "ChangedBy": "u001",
                "ChangedFor": "u002",
                "ChangeType": "Update",
                "FieldChanged": "Salary",
                "OldValue": "50000",
                "NewValue": "52000",
                "Environment": "HRProd",
                "Metadata": "{}",
                "change_investigation": "Pending",
                "Reason": "Annual raise",
                "ManagerID": "u003"
            }
        ])
        write_csv('hr_mutations', hr_mut_df)

    def test_full_workflow(self):
        orchestrator = AgentOrchestrator()
        context = {
            "mutation_id": self.mutation_id,
            "user_id": "u001",
            "system": "Payroll",
            "access_level": "Admin",
            "old_status": "Pending",
            "new_status": "Investigation Started"
        }
        # Step 1: InvestigationAgent
        result1 = orchestrator.route("InvestigationAgent", context)
        self.assertIn("status", result1)
        # Step 2: RightsCheckAgent
        result2 = orchestrator.route("RightsCheckAgent", result1.get("context", {}))
        self.assertIn("status", result2)
        # Step 3: RequestForInformationAgent
        result3 = orchestrator.route("RequestForInformationAgent", result2.get("context", {}))
        self.assertIn("status", result3)
        # Step 4: AdvisoryAgent
        result4 = orchestrator.route("AdvisoryAgent", result3.get("context", {}))
        self.assertIn("status", result4)
        # Check audit trail exists for this mutation
        audit_df = get_audit_trail_for_mutation(self.mutation_id)
        self.assertIsInstance(audit_df, pd.DataFrame)

    def tearDown(self):
        # Clean up test mutation from hr_mutations.csv
        hr_mut_df = read_csv('hr_mutations')
        hr_mut_df = hr_mut_df[hr_mut_df['MutationID'] != self.mutation_id]
        write_csv('hr_mutations', hr_mut_df)

    def test_orchestrator_escalation(self):
        """Test that the orchestrator escalates after repeated agent errors."""
        orchestrator = AgentOrchestrator()
        # Pass invalid context to force agent error
        context = {"invalid": "data"}
        # Use a non-existent agent to force error
        with self.assertRaises(ValueError):
            orchestrator.route("NonExistentAgent", context)

        # Patch an agent to always return error
        class FailingAgent:
            def handle_request(self, context):
                return {"status": "error", "error": "forced error", "context": context}
        orchestrator.agents["FailingAgent"] = FailingAgent()
        result = orchestrator.route("FailingAgent", context, max_retries=2)
        self.assertEqual(result["status"], "escalated")
        self.assertIn("Manual intervention", result["escalation"])

    def test_invalid_context(self):
        """Test agent handling of missing required context fields."""
        orchestrator = AgentOrchestrator()
        # Missing required fields for InvestigationAgent
        context = {}
        result = orchestrator.route("InvestigationAgent", context)
        self.assertIn("status", result)
        # Should not raise, but may return error or escalated status
        self.assertIn(result["status"], ["completed", "error", "escalated"])

if __name__ == "__main__":
    unittest.main()