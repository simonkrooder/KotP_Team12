# Application Documentation

## System Overview
The Access Control Management System is a generative AI-driven agentic system designed to ensure that changes made by users in applications are authorized. The system investigates whether the user who made a change had the appropriate rights. If the user had the rights, the change is approved; otherwise, the system initiates a series of actions to gather context, validate claims, and provide advisory reports to controllers.

The system aims to:
- Automate the validation of changes.
- Reduce manual effort in access control management.
- Ensure compliance and accountability.

## System Features
### 1. Data Files
The system relies on several CSV files to store and process data:
- **`authorisations.csv`**: Contains information about user authorizations for specific systems.
- **`hr_mutations.csv`**: Logs changes made by users, including details such as the field changed, old and new values, and timestamps.
- **`role_authorisations.csv`**: Maps roles to their respective authorizations.
- **`roles.csv`**: Defines roles within the organization.
- **`users.csv`**: Stores user information, including their status and department.
- **`sickLeave.csv`**: Tracks sick leave data for users.

### 2. HR Mutation Entry Page
A dedicated page allows users to enter HR mutations. This page includes dropdowns for selecting users, applications, and other relevant details.

### 3. Agent Trigger
The agent is triggered whenever a new HR mutation is added. It initiates the investigation process.

### 4. Authorization Check
The agent checks if the user who made the change has the necessary authorization. If valid, the change is approved.

### 5. User Clarification
If no authorization is found, the agent drafts and sends an email to the user requesting clarification. The user’s response is processed to validate the claim.

### 6. Manager Verification
The agent sends an email to the manager of the user to verify the user’s claim. The manager’s response is processed to gather additional context.

### 7. Advisory Report
Based on all gathered information, the agent generates an advisory report for the controller. The report includes recommendations:
- Accept the change.
- Reject the change and initiate further investigation.
- Mark the change as correct but requiring manual intervention.

### 8. Insights Page
A page displays the status of change investigations, including metrics, anomalies, and audit trails.

## Data Files
### `authorisations.csv`
- **Columns**: `AuthorisationID`, `UserID`, `System`, `AccessLevel`, `Status`, `GrantedOn`, `ExpiresOn`, `GrantedBy`
- **Purpose**: Tracks user authorizations for systems.

### `hr_mutations.csv`
- **Columns**: `MutationID`, `ChangedFor`, `ChangedBy`, `FieldChanged`, `OldValue`, `NewValue`, `ChangeType`, `Timestamp`, `Environment`, `Metadata`, `change_investigation`, `Reason`, `ManagerID`
- **Purpose**: Logs changes made by users.

### `role_authorisations.csv`
- **Columns**: `RoleID`, `AuthorisationID`
- **Purpose**: Maps roles to authorizations.

### `roles.csv`
- **Columns**: `RoleID`, `RoleName`, `Description`
- **Purpose**: Defines organizational roles.

### `users.csv`
- **Columns**: `UserID`, `Name`, `Department`, `Status`, `ManagerID`
- **Purpose**: Stores user information.

### `sickLeave.csv`
- **Columns**: `UserID`, `StartDate`, `EndDate`, `Reason`
- **Purpose**: Tracks user sick leave data.

## System Workflow
1. **HR Mutation Entry**: A user logs a change in the HR mutation page.
2. **Agent Trigger**: The agent is triggered to investigate the change.
3. **Authorization Check**: The agent checks if the user has the necessary authorization.
4. **User Clarification**: If unauthorized, the agent sends an email to the user for clarification.
5. **Claim Validation**: The agent validates the user’s claim using data such as sick leave records.
6. **Manager Verification**: The agent sends an email to the manager to verify the user’s claim.
7. **Advisory Report**: The agent generates a report for the controller with recommendations.

## Mock System Interactions
Since the system lacks email and other integrations, all interactions are mocked. For example:
- Emails are simulated as logs or notifications within the system.
- Responses are manually entered or mocked for testing purposes.

## Actionable TODOs
### Data Files
- [ ] Verify the structure and content of all CSV files.
- [ ] Add `sickLeave.csv` to the `/data` directory with columns: `UserID`, `StartDate`, `EndDate`, `Reason`.
- [ ] Enhance `hr_mutations.csv` by adding `Reason` and `ManagerID` columns.
- [ ] Enhance `users.csv` by adding a `ManagerID` column.
- [ ] Create an abstraction layer for accessing and managing data files.

### HR Mutation Entry Page
- [ ] Design and implement the HR mutation entry page.
- [ ] Add dropdowns for users, applications, and other fields.
- [ ] Add a field for entering the reason for the change.

### Agent Trigger
- [ ] Implement the agent trigger mechanism for new HR mutations.

### Authorization Check
- [ ] Develop the logic to check user authorizations.
- [ ] Update `change_investigation` in `hr_mutations.csv` for approved changes.

### User Clarification
- [ ] Mock email drafting and sending to users.
- [ ] Implement logic to process user responses.
- [ ] Validate user claims using `sickLeave.csv`.

### Manager Verification
- [ ] Mock email drafting and sending to managers.
- [ ] Implement logic to process manager responses.

### Advisory Report
- [ ] Develop the advisory report generation logic.
- [ ] Include recommendations based on gathered data.

### Insights Page
- [ ] Design and implement the insights page.
- [ ] Display metrics, anomalies, and audit trails.

### General
- [ ] Mock all system interactions for testing.
- [ ] Validate the system workflow with sample data.