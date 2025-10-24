"""
Agent2Agent Protocol Module
--------------------------
Defines the canonical message schema and helpers for agent-to-agent communication.
All agent messages should use this schema for traceability and auditability.

References:
- /docs/architecture.md (Agent2Agent Protocol Message Schema)
- /docs/application.md

Usage Example:
    from agent_protocol import AgentMessage, create_message, log_agent_message
    msg = create_message(
        sender="InvestigationAgent",
        receiver="RightsCheckAgent",
        action="check_rights",
        context={"mutation_id": "1001", "user_id": "u001"},
        status="pending"
    )
    log_agent_message(msg)
"""

import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
import os

# Path to audit log (reuse audit_trail.csv)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
AUDIT_FILE = os.path.join(DATA_DIR, 'audit_trail.csv')

class AgentMessage(BaseModel):
    sender: str
    receiver: str
    action: str
    context: Dict[str, Any]
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str
    error: Optional[Dict[str, Any]] = None

    class Config:
        extra = 'allow'


def create_message(sender: str, receiver: str, action: str, context: dict, status: str = "pending", correlation_id: Optional[str] = None, error: Optional[dict] = None) -> AgentMessage:
    """Create a new Agent2Agent protocol message."""
    return AgentMessage(
        sender=sender,
        receiver=receiver,
        action=action,
        context=context,
        correlation_id=correlation_id or str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        status=status,
        error=error
    )


def validate_message(msg: dict) -> bool:
    """Validate a message dict against the Agent2Agent schema."""
    try:
        AgentMessage(**msg)
        return True
    except ValidationError as e:
        print(f"Agent2Agent message validation error: {e}")
        return False


def log_agent_message(msg: AgentMessage, comment: Optional[str] = None):
    """Log an agent message to audit_trail.csv (preserving comments and header)."""
    import csv
    # Log rotation: archive if file exceeds 5MB
    MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
    if os.path.exists(AUDIT_FILE) and os.path.getsize(AUDIT_FILE) > MAX_LOG_SIZE:
        archive_name = AUDIT_FILE.replace('.csv', f'_archive_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.csv')
        os.rename(AUDIT_FILE, archive_name)
    # Prepare row
    audit_id = str(uuid.uuid4())[:8]
    timestamp = msg.timestamp
    mutation_id = msg.context.get('mutation_id')
    if not mutation_id:
        # Try to infer from nested context (e.g., if context is a result dict)
        if isinstance(msg.context, dict):
            for v in msg.context.values():
                if isinstance(v, dict) and 'MutationID' in v:
                    mutation_id = v['MutationID']
                    break
        if not mutation_id:
            mutation_id = 'unknown'
    old_status = msg.context.get('old_status', '')
    new_status = msg.context.get('new_status', msg.status)
    agent = msg.sender
    # Prepare comment field as string
    if comment is not None:
        if not isinstance(comment, str):
            comment_str = json.dumps(comment, ensure_ascii=False)
        else:
            comment_str = comment
    else:
        comment_str = json.dumps(msg.dict(), ensure_ascii=False)
    row = [audit_id, mutation_id, timestamp, old_status, new_status, agent, comment_str]
    # Write header if file does not exist
    write_header = not os.path.exists(AUDIT_FILE)
    with open(AUDIT_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if write_header:
            writer.writerow(["AuditID", "MutationID", "Timestamp", "OldStatus", "NewStatus", "Agent", "Comment"])
        writer.writerow(row)
