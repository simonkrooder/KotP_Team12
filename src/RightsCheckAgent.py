from agent_protocol import create_message, log_agent_message
from agent_main import mcv_authorization_check

class RightsCheckAgent:
    """Agent responsible for checking user rights."""
    def handle_request(self, context):
        retries = context.get('retries', 0)
        try:
            # Example: Check authorization for user and system
            user_id = context.get('user_id')
            system = context.get('system', 'Payroll')
            access_level = context.get('access_level', 'Admin')
            auth_result = mcv_authorization_check(user_id, system, access_level)
            context['auth_result'] = auth_result
            msg = create_message(
                sender="RightsCheckAgent",
                receiver=context.get("next_agent", "RequestForInformationAgent"),
                action="check_rights",
                context=context,
                status="pending"
            )
            log_agent_message(msg, comment="Rights check started")
            return msg
        except Exception as e:
            error_msg = create_message(
                sender="RightsCheckAgent",
                receiver=context.get("next_agent", "RequestForInformationAgent"),
                action="check_rights",
                context={**context, 'retries': retries + 1},
                status="error" if retries < 2 else "escalated",
                error={"type": str(type(e)), "msg": str(e)}
            )
            log_agent_message(error_msg, comment="Rights check error")
            return error_msg
