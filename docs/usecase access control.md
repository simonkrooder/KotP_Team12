---
## User Story
As a compliance controller, I need an intelligent agent that reviews all access changes and user actions daily, validates them against authorization rules and process history, and either automatically applies legitimate changes or flags anomalies for review. This ensures that every change is compliant, traceable, and actionable without manual effort.

## Objective

## Problem Statement
Organizations struggle to maintain control over user permissions after they are granted. Manual reviews are slow, reactive, and prone to error. Processes like salary changes or system updates require strict approval chains, but these are often bypassed or misused. Current systems lack continuous oversight, leaving businesses exposed to compliance risks and security breaches.

## Benefit
The agent introduces a proactive, automated control mechanism. It validates every change against:
- Authorization lists (who is allowed to do what),
- Process rules (e.g., salary changes require manager initiation and CFO approval),
- Historical context (is this event expected?).
Legitimate changes are auto-applied, while anomalies trigger immediate notifications with clear next steps. This reduces compliance risk, accelerates workflows, and ensures audit readiness.

## In Scope
- Daily scheduled review of all permission changes and user actions.
- Integration with:
	- Authorization list,
	- Event data (including procedure validation and history),
	- Change list.
- Automatic application of valid changes.
- Immediate email notifications to controllers for anomalies, including:
	- Issue summary,
	- Reason for flag,
	- Follow-up questions,
	- Direct ticket link.
- Logging for audit purposes.

## Out of Scope
- Initial granting of permissions.
- Real-time monitoring (only daily batch review).
- Manual remediation or ticket resolution.
- Advanced predictive analytics or ML-based anomaly detection (future phase).
- Integration with external SOAR or SIEM tools (future phase).

## Process Flow
**Programmable Flow (Left)**
- Authorization List → RPA extracts roles and exceptions.
- Event Data → Includes:
	- Event details,
	- Procedure validation,
	- Historical check.
- RPA correlates authorization and event data.
- Generates Change List with:
	- Approved changes (auto-push),
	- Flagged anomalies (send to agent).

**Agent Flow (Right)**
- Receives flagged anomalies from Change List.
- Performs contextual review.
- Sends email to controller with:
	- Summary of issue,
	- Why it’s a risk,
	- Follow-up questions,
	- Ticket link.
- Controller reviews and acts.

## Final Thoughts
This MVP combines deterministic automation (programmable flow) with intelligent oversight (agent). It ensures:
- Every change is validated against rules and history.
- Legitimate changes are applied without delay.
- Anomalies are escalated with actionable insights.
- Compliance becomes continuous, not periodic.
The unique identifier per process guarantees traceability across all steps, making the system auditable and scalable.
