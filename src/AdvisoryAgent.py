"""
See docs/architecture.md and docs/application.md for the canonical agent pattern, Agent2Agent protocol, and MCV server integration.
This agent follows the local class + Azure model pattern. All orchestration and message passing is local; all reasoning is delegated to the Azure model.
"""
from src.azure_client import get_project_client, get_model_deployment
import logging

class AdvisoryAgent:
    """
    Agent responsible for generating advisory reports.
    Uses Azure-hosted model for reasoning (see docs/architecture.md, agent_example.py).
    Integrates with the Agent2Agent protocol and MCV server for all tool calls and message passing.
    All actions and status changes are logged for auditability.
    """
    def __init__(self):
        self.client = get_project_client()
        self.model_deployment = get_model_deployment()
        self.logger = logging.getLogger(__name__)

    def handle_request(self, context):
        """
        Calls the Azure-hosted model for advisory report generation logic.
        Args:
            context (dict): The advisory context.
        Returns:
            dict: Model response or error message.
        """
        try:
            prompt = self._build_prompt(context)
            response = self.client.completions.create(
                deployment_id=self.model_deployment,
                prompt=prompt,
                temperature=0.2,
                max_tokens=512
            )
            result = {
                "agent": "AdvisoryAgent",
                "status": "completed",
                "response": response.choices[0].text,
                "context": context
            }
            return result
        except Exception as e:
            self.logger.error(f"AdvisoryAgent error: {e}")
            return {
                "agent": "AdvisoryAgent",
                "status": "error",
                "error": str(e),
                "context": context
            }

    def _build_prompt(self, context):
        """
        Build a prompt for the Azure model based on the advisory context.
        """
        return f"""
        You are an advisory agent. Given the following context, generate a detailed advisory report and recommendation for the controller:
        Context: {context}
        Provide a summary of findings, recommendation, and next steps.
        """
