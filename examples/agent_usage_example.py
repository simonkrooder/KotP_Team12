"""
Minimal example usage for all agents using the Azure model pattern.
"""

from src.AdvisoryAgent import AdvisoryAgent
from src.InvestigationAgent import InvestigationAgent
from src.RightsCheckAgent import RightsCheckAgent
from src.RequestForInformationAgent import RequestForInformationAgent

def run_advisory_agent():
    agent = AdvisoryAgent()
    context = {"case_id": 1, "details": "Example advisory context."}
    result = agent.handle_request(context)
    print("AdvisoryAgent result:", result)

def run_investigation_agent():
    agent = InvestigationAgent()
    context = {"mutation_id": 42, "details": "Example investigation context."}
    result = agent.handle_request(context)
    print("InvestigationAgent result:", result)

def run_rights_check_agent():
    agent = RightsCheckAgent()
    context = {"user_id": "u001", "system": "Payroll", "access_level": "Admin"}
    result = agent.handle_request(context)
    print("RightsCheckAgent result:", result)

def run_request_for_information_agent():
    agent = RequestForInformationAgent()
    context = {"user_id": "u001", "question": "Please clarify your recent change."}
    result = agent.handle_request(context)
    print("RequestForInformationAgent result:", result)

if __name__ == "__main__":
    run_advisory_agent()
    run_investigation_agent()
    run_rights_check_agent()
    run_request_for_information_agent()