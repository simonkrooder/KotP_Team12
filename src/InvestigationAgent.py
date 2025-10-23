from agent_protocol import create_message, log_agent_message
from agent_main import mcv_data_lookup

class InvestigationAgent:
    """Agent responsible for orchestrating investigations."""
    def handle_request(self, context):
        retries = context.get('retries', 0)
        try:
            # Example: Lookup mutation in hr_mutations.csv
            mutation_id = context.get('mutation_id')
            findings = mcv_data_lookup('hr_mutations.csv', {'MutationID': mutation_id})
            context['findings'] = findings
            msg = create_message(
                sender="InvestigationAgent",
                receiver=context.get("next_agent", "RightsCheckAgent"),
                action="investigate",
                context=context,
                status="started"
            )
            log_agent_message(msg, comment="Investigation started")
            return msg
        except Exception as e:
            error_msg = create_message(
                sender="InvestigationAgent",
                receiver=context.get("next_agent", "RightsCheckAgent"),
                action="investigate",
                context={**context, 'retries': retries + 1},
                status="error" if retries < 2 else "escalated",
                error={"type": str(type(e)), "msg": str(e)}
            )
            log_agent_message(error_msg, comment="Investigation error")
            return error_msg
