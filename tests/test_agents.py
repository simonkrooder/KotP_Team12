import unittest
from unittest.mock import patch, MagicMock
from src.AdvisoryAgent import AdvisoryAgent
from src.InvestigationAgent import InvestigationAgent
from src.RightsCheckAgent import RightsCheckAgent
from src.RequestForInformationAgent import RequestForInformationAgent

class TestAdvisoryAgent(unittest.TestCase):
    @patch('src.AdvisoryAgent.get_project_client')
    @patch('src.AdvisoryAgent.get_model_deployment')
    def test_handle_request_success(self, mock_get_model_deployment, mock_get_project_client):
        # Mock Azure client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="Advisory report output.")]
        mock_client.completions.create.return_value = mock_response
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = AdvisoryAgent()
        context = {"case_id": 123, "details": "Test context."}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "AdvisoryAgent")
        self.assertEqual(result["status"], "completed")
        self.assertIn("Advisory report output.", result["response"])
        self.assertEqual(result["context"], context)

    @patch('src.AdvisoryAgent.get_project_client')
    @patch('src.AdvisoryAgent.get_model_deployment')
    def test_handle_request_error(self, mock_get_model_deployment, mock_get_project_client):
        # Simulate error in Azure client
        mock_client = MagicMock()
        mock_client.completions.create.side_effect = Exception("Azure error")
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = AdvisoryAgent()
        context = {"case_id": 456, "details": "Test error context."}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "AdvisoryAgent")
        self.assertEqual(result["status"], "error")
        self.assertIn("Azure error", result["error"])
        self.assertEqual(result["context"], context)

class TestInvestigationAgent(unittest.TestCase):
    @patch('src.InvestigationAgent.get_project_client')
    @patch('src.InvestigationAgent.get_model_deployment')
    def test_handle_request_success(self, mock_get_model_deployment, mock_get_project_client):
        # Mock Azure client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="Investigation result output.")]
        mock_client.completions.create.return_value = mock_response
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = InvestigationAgent()
        context = {"mutation_id": 42, "details": "Test investigation context."}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "InvestigationAgent")
        self.assertEqual(result["status"], "completed")
        self.assertIn("Investigation result output.", result["response"])
        self.assertEqual(result["context"], context)

    @patch('src.InvestigationAgent.get_project_client')
    @patch('src.InvestigationAgent.get_model_deployment')
    def test_handle_request_error(self, mock_get_model_deployment, mock_get_project_client):
        # Simulate error in Azure client
        mock_client = MagicMock()
        mock_client.completions.create.side_effect = Exception("Azure error")
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = InvestigationAgent()
        context = {"mutation_id": 99, "details": "Test error context."}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "InvestigationAgent")
        self.assertEqual(result["status"], "error")
        self.assertIn("Azure error", result["error"])
        self.assertEqual(result["context"], context)

class TestRightsCheckAgent(unittest.TestCase):
    @patch('src.RightsCheckAgent.get_project_client')
    @patch('src.RightsCheckAgent.get_model_deployment')
    def test_handle_request_success(self, mock_get_model_deployment, mock_get_project_client):
        # Mock Azure client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="Rights check output.")]
        mock_client.completions.create.return_value = mock_response
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = RightsCheckAgent()
        context = {"user_id": "u001", "system": "Payroll", "access_level": "Admin"}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "RightsCheckAgent")
        self.assertEqual(result["status"], "completed")
        self.assertIn("Rights check output.", result["response"])
        self.assertEqual(result["context"], context)

    @patch('src.RightsCheckAgent.get_project_client')
    @patch('src.RightsCheckAgent.get_model_deployment')
    def test_handle_request_error(self, mock_get_model_deployment, mock_get_project_client):
        # Simulate error in Azure client
        mock_client = MagicMock()
        mock_client.completions.create.side_effect = Exception("Azure error")
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = RightsCheckAgent()
        context = {"user_id": "u002", "system": "Payroll", "access_level": "User"}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "RightsCheckAgent")
        self.assertEqual(result["status"], "error")
        self.assertIn("Azure error", result["error"])
        self.assertEqual(result["context"], context)

class TestRequestForInformationAgent(unittest.TestCase):
    @patch('src.RequestForInformationAgent.get_project_client')
    @patch('src.RequestForInformationAgent.get_model_deployment')
    def test_handle_request_success(self, mock_get_model_deployment, mock_get_project_client):
        # Mock Azure client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="RFI output.")]
        mock_client.completions.create.return_value = mock_response
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = RequestForInformationAgent()
        context = {"user_id": "u001", "question": "Please clarify."}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "RequestForInformationAgent")
        self.assertEqual(result["status"], "completed")
        self.assertIn("RFI output.", result["response"])
        self.assertEqual(result["context"], context)

    @patch('src.RequestForInformationAgent.get_project_client')
    @patch('src.RequestForInformationAgent.get_model_deployment')
    def test_handle_request_error(self, mock_get_model_deployment, mock_get_project_client):
        # Simulate error in Azure client
        mock_client = MagicMock()
        mock_client.completions.create.side_effect = Exception("Azure error")
        mock_get_project_client.return_value = mock_client
        mock_get_model_deployment.return_value = "test-deployment"

        agent = RequestForInformationAgent()
        context = {"user_id": "u002", "question": "Test error."}
        result = agent.handle_request(context)
        self.assertEqual(result["agent"], "RequestForInformationAgent")
        self.assertEqual(result["status"], "error")
        self.assertIn("Azure error", result["error"])
        self.assertEqual(result["context"], context)

if __name__ == "__main__":
    unittest.main()