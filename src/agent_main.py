import os
import requests
from dotenv import load_dotenv
from InvestigationAgent import InvestigationAgent
from RightsCheckAgent import RightsCheckAgent
from RequestForInformationAgent import RequestForInformationAgent
from AdvisoryAgent import AdvisoryAgent
from agent_protocol import AgentMessage

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

MCV_SERVER_URL = os.getenv("MCV_SERVER_URL", "http://localhost:8000")

# --- MCV server tool call helpers ---
def mcv_authorization_check(user_id, system, access_level):
    url = f"{MCV_SERVER_URL}/api/authorization/check"
    payload = {"user_id": user_id, "system": system, "access_level": access_level}
    return requests.post(url, json=payload).json()

def mcv_data_lookup(file, query):
    url = f"{MCV_SERVER_URL}/api/data/lookup"
    payload = {"file": file, "query": query}
    return requests.post(url, json=payload).json()

def mcv_notify_send(recipient_id, subject, body, context=None):
    url = f"{MCV_SERVER_URL}/api/notify/send"
    payload = {"recipient_id": recipient_id, "subject": subject, "body": body, "context": context or {}}
    return requests.post(url, json=payload).json()

def mcv_report_generate(mutation_id, context):
    url = f"{MCV_SERVER_URL}/api/report/generate"
    payload = {"mutation_id": mutation_id, "context": context}
    return requests.post(url, json=payload).json()

class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "InvestigationAgent": InvestigationAgent(),
            "RightsCheckAgent": RightsCheckAgent(),
            "RequestForInformationAgent": RequestForInformationAgent(),
            "AdvisoryAgent": AdvisoryAgent(),
        }

    def route_message(self, msg: AgentMessage):
        """Route a message to the appropriate agent based on receiver."""
        agent = self.agents.get(msg.receiver)
        if not agent:
            raise ValueError(f"Unknown agent: {msg.receiver}")
        return agent.handle_request(msg.context)

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    # Full end-to-end workflow
    initial_context = {
        "mutation_id": "1001",
        "user_id": "u001",
        "system": "Payroll",
        "access_level": "Admin",
        "next_agent": "RightsCheckAgent",
        "old_status": "Pending",
        "new_status": "Investigation Started"
    }
    # Step 1: InvestigationAgent
    msg1 = orchestrator.agents["InvestigationAgent"].handle_request(initial_context)
    # Step 2: RightsCheckAgent
    msg2 = orchestrator.route_message(msg1)
    # Step 3: RequestForInformationAgent
    msg3 = orchestrator.route_message(msg2)
    # Step 4: AdvisoryAgent
    msg4 = orchestrator.route_message(msg3)
    # Step 5: (Optional) Loop back or finalize as needed
    print("Workflow complete. Advisory report:", msg4.context.get('report_result'))
