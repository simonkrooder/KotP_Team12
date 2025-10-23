## CSV Schemas: Multi-Agent Access Control Demo

This document defines the schema for each CSV data file used in the project. It includes column names, data types, required fields, and a brief description of each file's purpose.

---

### authorisations.csv
**Purpose:** Tracks current and historical user-system authorizations for access control.
**Columns:**
| Column         | Type     | Required | Description                                                      |
|---------------|----------|----------|------------------------------------------------------------------|
| AuthorisationID| string   | Yes      | Unique identifier for each authorization record                  |
| UserID        | string   | Yes      | Reference to user in users.csv                                   |
| RoleID        | string   | Yes      | Reference to role in roles.csv                                   |
| System        | string   | Yes      | Name of the system/application being accessed                    |
| AccessLevel   | string   | Yes      | Level of access granted (Admin, User, Viewer)                    |
| GrantedBy     | string   | Yes      | User ID of the person who granted this authorization             |
| GrantedOn     | date     | Yes      | Date when the authorization was granted (YYYY-MM-DD)             |
| ExpiresOn     | date     | No       | Date when authorization expires (YYYY-MM-DD, empty if no expiry) |
| Status        | string   | Yes      | Current status (Active, Revoked)                                 |

---

### hr_mutations.csv
**Purpose:** Audit log of all HR data changes and mutations over time.
**Columns:**
| Column              | Type     | Required | Description                                                      |
|---------------------|----------|----------|------------------------------------------------------------------|
| MutationID          | string   | Yes      | Unique sequential identifier for each change record              |
| Timestamp           | datetime | Yes      | ISO 8601 timestamp of when the change occurred                   |
| ChangedBy           | string   | Yes      | User ID of the person who made the change                        |
| ChangedFor          | string   | Yes      | User ID of the person whose data was changed                     |
| ChangeType          | string   | Yes      | Type of change (Create, Update, Terminate)                       |
| FieldChanged        | string   | Yes      | Specific field that was modified                                 |
| OldValue            | string   | No       | Previous value before the change                                 |
| NewValue            | string   | Yes      | New value after the change                                       |
| Environment         | string   | Yes      | System environment (HRProd, HRTest)                              |
| Metadata            | string   | No       | Additional context (JSON-like format)                            |
| change_investigation| string   | Yes      | Status code for investigation workflow (Pending, Approved, etc.) |
| Reason              | string   | No       | Reason for the change                                            |
| ManagerID           | string   | No       | UserID of the manager responsible for validation                 |

---

### role_authorisations.csv
**Purpose:** Defines which systems each role can access and at what level.
**Columns:**
| Column      | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| RoleID      | string | Yes      | Reference to role in roles.csv                   |
| System      | string | Yes      | Name of the system/application                   |
| AccessLevel | string | Yes      | Level of access for this role-system combination |

---

### roles.csv
**Purpose:** Master data for job roles and their associated system access permissions.
**Columns:**
| Column               | Type   | Required | Description                                              |
|----------------------|--------|----------|----------------------------------------------------------|
| RoleID               | string | Yes      | Unique identifier for each role                          |
| RoleName             | string | Yes      | Human-readable name of the role                          |
| Department           | string | Yes      | Department this role belongs to                          |
| Description          | string | No       | Brief description of the role's responsibilities         |
| DefaultAuthorisations| string | No       | Default system access pattern (System:AccessLevel format)|

---

### users.csv
**Purpose:** Master employee data containing personal information, job details, and current status.
**Columns:**
| Column         | Type   | Required | Description                                         |
|----------------|--------|----------|-----------------------------------------------------|
| UserID         | string | Yes      | Unique identifier for each user                     |
| Name           | string | Yes      | Full name of the employee                           |
| Department     | string | Yes      | Department the employee belongs to                  |
| JobTitle       | string | Yes      | Current job title/position                          |
| Status         | string | Yes      | Current employment status (Active, Terminated, etc.)|
| Email          | string | Yes      | Primary email address                               |
| Manager        | string | No       | UserID of the employee's direct manager             |
| HireDate       | date   | Yes      | Date when employee was hired (YYYY-MM-DD)           |
| TerminationDate| date   | No       | Date when employment ended (empty if still active)   |
| Environment    | string | Yes      | System environment assignment (HRProd, HRTest)       |

---

### sickLeave.csv
**Purpose:** Tracks user sick leave periods for validation in agentic investigation workflows.
**Columns:**
| Column    | Type   | Required | Description                                  |
|-----------|--------|----------|----------------------------------------------|
| UserID    | string | Yes      | Reference to user in users.csv               |
| StartDate | date   | Yes      | Start date of sick leave (YYYY-MM-DD)        |
| EndDate   | date   | Yes      | End date of sick leave (YYYY-MM-DD)          |
| Status    | string | Yes      | Approval status of the sick leave            |

---

### vacation.csv
**Purpose:** Tracks user vacation periods for validation in agentic investigation workflows.
**Columns:**
| Column    | Type   | Required | Description                                  |
|-----------|--------|----------|----------------------------------------------|
| UserID    | string | Yes      | Reference to user in users.csv               |
| StartDate | date   | Yes      | Start date of vacation (YYYY-MM-DD)          |
| EndDate   | date   | Yes      | End date of vacation (YYYY-MM-DD)            |
| Status    | string | Yes      | Approval status of the vacation              |

---

### audit_trail.csv
**Purpose:** Logs all agent actions and status changes for traceability and compliance.
**Columns:**
| Column     | Type     | Required | Description                                         |
|------------|----------|----------|-----------------------------------------------------|
| AuditID    | string   | Yes      | Unique identifier for each audit log entry          |
| MutationID | string   | Yes      | Reference to the HR mutation being audited          |
| Timestamp  | datetime | Yes      | ISO 8601 timestamp of the action                    |
| OldStatus  | string   | No       | Previous status before the change                   |
| NewStatus  | string   | Yes      | New status after the change                         |
| Agent      | string   | Yes      | Name of the agent or process making the change      |
| Comment    | string   | No       | Additional context or reason for the status change  |

---

**How to use:**
- Reference this file when reading or writing CSVs in code.
- Update this schema if the data model evolves.