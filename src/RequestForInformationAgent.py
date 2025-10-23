from agent_protocol import create_message, log_agent_message
from agent_main import mcv_notify_send

class RequestForInformationAgent:
    """Agent responsible for requesting and validating information from users/managers."""
    def handle_request(self, context):
        retries = context.get('retries', 0)
        try:
            # Example: Send a mocked notification to user
            recipient_id = context.get('user_id')
            subject = "Clarification Needed"
            body = "Please provide more information about your mutation."
            notify_result = mcv_notify_send(recipient_id, subject, body, context)
            context['notify_result'] = notify_result
            msg = create_message(
                sender="RequestForInformationAgent",
                receiver=context.get("next_agent", "AdvisoryAgent"),
                action="request_info",
                context=context,
                status="pending"
            )
            log_agent_message(msg, comment="Request for information started")
            return msg
        except Exception as e:
            error_msg = create_message(
                sender="RequestForInformationAgent",
                receiver=context.get("next_agent", "AdvisoryAgent"),
                action="request_info",
                context={**context, 'retries': retries + 1},
                status="error" if retries < 2 else "escalated",
                error={"type": str(type(e)), "msg": str(e)}
            )
            log_agent_message(error_msg, comment="Request for information error")
            return error_msg
