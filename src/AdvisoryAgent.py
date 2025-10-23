from agent_protocol import create_message, log_agent_message
from agent_main import mcv_report_generate

class AdvisoryAgent:
    """Agent responsible for generating advisory reports."""
    def handle_request(self, context):
        retries = context.get('retries', 0)
        try:
            # Example: Generate a report for the mutation
            mutation_id = context.get('mutation_id')
            report_result = mcv_report_generate(mutation_id, context)
            context['report_result'] = report_result
            msg = create_message(
                sender="AdvisoryAgent",
                receiver=context.get("next_agent", "InvestigationAgent"),
                action="generate_advisory",
                context=context,
                status="pending"
            )
            log_agent_message(msg, comment="Advisory report started")
            return msg
        except Exception as e:
            error_msg = create_message(
                sender="AdvisoryAgent",
                receiver=context.get("next_agent", "InvestigationAgent"),
                action="generate_advisory",
                context={**context, 'retries': retries + 1},
                status="error" if retries < 2 else "escalated",
                error={"type": str(type(e)), "msg": str(e)}
            )
            log_agent_message(error_msg, comment="Advisory error")
            return error_msg
