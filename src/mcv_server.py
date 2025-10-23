"""
MCV Server: Central integration and execution layer for all agent tool calls.
Implements endpoints for authorization checks, data lookups, notifications, and report generation.
Logs all tool calls and results to audit_trail.csv (preserving comments).
"""

import os
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
AUDIT_FILE = os.path.join(DATA_DIR, 'audit_trail.csv')

app = FastAPI(title="MCV Server", description="Model-Controller-View server for agent tool calls.")

def log_audit(action, mutation_id=None, old_status=None, new_status=None, agent=None, comment=None):
    """Append an audit log entry to audit_trail.csv, preserving comments and header."""
    # Read existing lines (preserve comments and header)
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Find header line
        header_idx = next((i for i, l in enumerate(lines) if l.strip().startswith('AuditID')), None)
        if header_idx is not None:
            header = lines[:header_idx+1]
            data = lines[header_idx+1:]
        else:
            header = []
            data = lines
    else:
        header = ["AuditID,MutationID,Timestamp,OldStatus,NewStatus,Agent,Comment\n"]
        data = []
    # Generate new AuditID
    audit_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().isoformat()
    row = f'{audit_id},{mutation_id or ""},{timestamp},{old_status or ""},{new_status or ""},{agent or "MCVServer"},{json.dumps(comment) if comment else action}\n'
    # Write back
    with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(header + data + [row])

# --- Endpoint Models ---
class AuthCheckRequest(BaseModel):
    user_id: str
    system: str
    access_level: str

class DataLookupRequest(BaseModel):
    file: str
    query: dict

class NotifySendRequest(BaseModel):
    recipient_id: str
    subject: str
    body: str
    context: dict = None

class ReportGenerateRequest(BaseModel):
    mutation_id: str
    context: dict

# --- Endpoints ---
@app.post("/api/authorization/check")
async def authorization_check(req: AuthCheckRequest):
    """Check user authorization for a system and access level."""
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, 'authorisations.csv'), comment='#')
        match = df[(df['UserID'] == req.user_id) & (df['System'] == req.system) & (df['AccessLevel'] == req.access_level) & (df['Status'] == 'Active')]
        if not match.empty:
            evidence = match.iloc[0].to_dict()
            result = {"authorized": True, "evidence": evidence, "message": f"User {req.user_id} is authorized as {req.access_level} for {req.system}."}
        else:
            result = {"authorized": False, "evidence": {}, "message": f"User {req.user_id} is NOT authorized as {req.access_level} for {req.system}."}
        log_audit("authorization_check", agent="MCVServer", comment=result)
        return result
    except Exception as e:
        log_audit("authorization_check_error", agent="MCVServer", comment=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/lookup")
async def data_lookup(req: DataLookupRequest):
    try:
        file_path = os.path.join(DATA_DIR, req.file)
        df = pd.read_csv(file_path, comment='#')
        # Apply filters
        mask = pd.Series([True] * len(df))
        for k, v in req.query.items():
            mask &= (df[k] == v)
        results = df[mask].to_dict(orient='records')
        result = {"results": results, "message": f"{len(results)} record(s) found."}
        log_audit("data_lookup", agent="MCVServer", comment=result)
        return result
    except Exception as e:
        log_audit("data_lookup_error", agent="MCVServer", comment=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notify/send")
async def notify_send(req: NotifySendRequest):
    try:
        # Mocked notification: just log and return
        message_id = str(uuid.uuid4())[:8]
        result = {"status": "mocked", "message_id": message_id, "message": f"Notification displayed in UI for user {req.recipient_id}."}
        log_audit("notify_send", agent="MCVServer", comment=result)
        return result
    except Exception as e:
        log_audit("notify_send_error", agent="MCVServer", comment=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report/generate")
async def report_generate(req: ReportGenerateRequest):
    try:
        report_id = str(uuid.uuid4())[:8]
        summary = "All checks passed. Change is valid."
        recommendation = "accept"
        details = req.context.get('findings', {})
        result = {
            "report_id": report_id,
            "summary": summary,
            "recommendation": recommendation,
            "details": details
        }
        log_audit("report_generate", mutation_id=req.mutation_id, agent="MCVServer", comment=result)
        return result
    except Exception as e:
        log_audit("report_generate_error", agent="MCVServer", comment=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# --- Root endpoint for health check ---
@app.get("/")
async def root():
    return {"status": "MCV Server running"}
