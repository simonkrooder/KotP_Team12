import asyncio
from src.InvestigationAgent import InvestigationAgent
from src.RightsCheckAgent import RightsCheckAgent
from src.RequestForInformationAgent import RequestForInformationAgent
from src.AdvisoryAgent import AdvisoryAgent
from src.agent_protocol import create_message, log_agent_message, AgentMessage
import logging



# Minimal async orchestrator for Azure SDK-based agents
async def main():
    logging.basicConfig(level=logging.INFO)
    # Instantiate agents
    investigation_agent = InvestigationAgent()
    rights_check_agent = RightsCheckAgent()
    rfi_agent = RequestForInformationAgent()
    advisory_agent = AdvisoryAgent()

    # Initialize agents if needed (async)
    await asyncio.gather(
        investigation_agent.initialize(),
        rights_check_agent.initialize(),
        rfi_agent.initialize(),
        advisory_agent.initialize(),
    )


    # Initial context for the workflow
    context = {
        "mutation_id": "1001",
        "user_id": "u001",
        "system": "Payroll",
        "access_level": "Admin",
        "old_status": "Pending",
        "new_status": "Investigation Started"
    }

    # Step 1: InvestigationAgent
    msg1 = create_message(
        sender="Orchestrator",
        receiver="InvestigationAgent",
        action="start_investigation",
        context=context,
        status="pending"
    )
    log_agent_message(msg1, comment="Orchestrator to InvestigationAgent")
    result1 = await investigation_agent.post_message(msg1.dict())
    logging.info(f"InvestigationAgent result: {result1}")

    # Step 2: RightsCheckAgent
    msg2 = create_message(
        sender="InvestigationAgent",
        receiver="RightsCheckAgent",
        action="check_rights",
        context=result1.get("context", {}),
        status="pending",
        correlation_id=msg1.correlation_id
    )
    log_agent_message(msg2, comment="InvestigationAgent to RightsCheckAgent")
    result2 = await rights_check_agent.post_message(msg2.dict())
    logging.info(f"RightsCheckAgent result: {result2}")

    # Step 3: RequestForInformationAgent
    msg3 = create_message(
        sender="RightsCheckAgent",
        receiver="RequestForInformationAgent",
        action="request_clarification",
        context=result2.get("context", {}),
        status="pending",
        correlation_id=msg1.correlation_id
    )
    log_agent_message(msg3, comment="RightsCheckAgent to RequestForInformationAgent")
    result3 = await rfi_agent.post_message(msg3.dict())
    logging.info(f"RequestForInformationAgent result: {result3}")

    # Step 4: AdvisoryAgent
    msg4 = create_message(
        sender="RequestForInformationAgent",
        receiver="AdvisoryAgent",
        action="generate_advisory",
        context=result3.get("context", {}),
        status="pending",
        correlation_id=msg1.correlation_id
    )
    log_agent_message(msg4, comment="RequestForInformationAgent to AdvisoryAgent")
    result4 = await advisory_agent.post_message(msg4.dict())
    logging.info(f"AdvisoryAgent result: {result4}")

    print("Workflow complete. Advisory report:", result4.get("response"))

if __name__ == "__main__":
    asyncio.run(main())
