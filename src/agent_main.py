import asyncio
from src.InvestigationAgent import InvestigationAgent
from src.RightsCheckAgent import RightsCheckAgent
from src.RequestForInformationAgent import RequestForInformationAgent
from src.AdvisoryAgent import AdvisoryAgent
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

    # Initial context
    context = {
        "mutation_id": "1001",
        "user_id": "u001",
        "system": "Payroll",
        "access_level": "Admin",
        "old_status": "Pending",
        "new_status": "Investigation Started"
    }

    # Step 1: InvestigationAgent
    result1 = await investigation_agent.post_message(context)
    logging.info(f"InvestigationAgent result: {result1}")

    # Step 2: RightsCheckAgent
    result2 = await rights_check_agent.post_message(result1.get("context", {}))
    logging.info(f"RightsCheckAgent result: {result2}")

    # Step 3: RequestForInformationAgent
    result3 = await rfi_agent.post_message(result2.get("context", {}))
    logging.info(f"RequestForInformationAgent result: {result3}")

    # Step 4: AdvisoryAgent
    result4 = await advisory_agent.post_message(result3.get("context", {}))
    logging.info(f"AdvisoryAgent result: {result4}")

    print("Workflow complete. Advisory report:", result4.get("response"))

if __name__ == "__main__":
    asyncio.run(main())
