"""
Robust data access layer for all CSV files in /data/.
Provides standardized read/write functions and schema validation hooks.
"""
import os
import pandas as pd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

# Map of canonical CSV filenames
CSV_FILES = {
    'users': 'users.csv',
    'hr_mutations': 'hr_mutations.csv',
    'authorisations': 'authorisations.csv',
    'role_authorisations': 'role_authorisations.csv',
    'roles': 'roles.csv',
    'sickLeave': 'sickLeave.csv',
    'vacation': 'vacation.csv',
    'audit_trail': 'audit_trail.csv',
}

def get_csv_path(name):
    """Get the absolute path to a CSV file by logical name."""
    if name not in CSV_FILES:
        raise ValueError(f"Unknown CSV file: {name}")
    return os.path.join(DATA_DIR, CSV_FILES[name])

def read_csv(name, **kwargs):
    """Read a CSV file by logical name, preserving comments and header."""
    path = get_csv_path(name)
    # By default, skip comment lines
    return pd.read_csv(path, comment='#', **kwargs)

def write_csv(name, df, **kwargs):
    """Write a DataFrame to a CSV file by logical name, preserving header and comments if present."""
    path = get_csv_path(name)
    # Optionally, preserve comments and header
    # For now, just overwrite (extend as needed)
    df.to_csv(path, index=False, **kwargs)

def get_audit_trail_for_mutation(mutation_id):
    """Return all audit trail entries for a given mutation_id as a DataFrame."""
    df = read_csv('audit_trail')
    return df[df['MutationID'] == str(mutation_id)]

def rotate_audit_log(max_size_mb=1):
    """Archive audit_trail.csv if it exceeds max_size_mb (default 1MB)."""
    path = get_csv_path('audit_trail')
    if os.path.exists(path) and os.path.getsize(path) > max_size_mb * 1024 * 1024:
        import shutil
        from datetime import datetime
        archive_name = f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        archive_path = os.path.join(os.path.dirname(path), archive_name)
        shutil.move(path, archive_path)
        # Recreate empty audit_trail.csv with header
        with open(path, 'w', encoding='utf-8') as f:
            f.write("AuditID,MutationID,Timestamp,OldStatus,NewStatus,Agent,Comment\n")
        return archive_path
    return None


# --- CSV Schema Definitions (from /docs/csv_schemas.md) ---
CSV_SCHEMAS = {
    'authorisations': [
        {'name': 'AuthorisationID', 'type': 'string', 'required': True},
        {'name': 'UserID', 'type': 'string', 'required': True},
        {'name': 'RoleID', 'type': 'string', 'required': True},
        {'name': 'System', 'type': 'string', 'required': True},
        {'name': 'AccessLevel', 'type': 'string', 'required': True},
        {'name': 'GrantedBy', 'type': 'string', 'required': True},
        {'name': 'GrantedOn', 'type': 'date', 'required': True},
        {'name': 'ExpiresOn', 'type': 'date', 'required': False},
        {'name': 'Status', 'type': 'string', 'required': True},
    ],
    'hr_mutations': [
        {'name': 'MutationID', 'type': 'string', 'required': True},
        {'name': 'Timestamp', 'type': 'datetime', 'required': True},
        {'name': 'ChangedBy', 'type': 'string', 'required': True},
        {'name': 'ChangedFor', 'type': 'string', 'required': True},
        {'name': 'ChangeType', 'type': 'string', 'required': True},
        {'name': 'FieldChanged', 'type': 'string', 'required': True},
        {'name': 'OldValue', 'type': 'string', 'required': False},
        {'name': 'NewValue', 'type': 'string', 'required': True},
        {'name': 'Environment', 'type': 'string', 'required': True},
        {'name': 'Metadata', 'type': 'string', 'required': False},
        {'name': 'change_investigation', 'type': 'string', 'required': True},
        {'name': 'Reason', 'type': 'string', 'required': False},
        {'name': 'ManagerID', 'type': 'string', 'required': False},
    ],
    'role_authorisations': [
        {'name': 'RoleID', 'type': 'string', 'required': True},
        {'name': 'System', 'type': 'string', 'required': True},
        {'name': 'AccessLevel', 'type': 'string', 'required': True},
    ],
    'roles': [
        {'name': 'RoleID', 'type': 'string', 'required': True},
        {'name': 'RoleName', 'type': 'string', 'required': True},
        {'name': 'Department', 'type': 'string', 'required': True},
        {'name': 'Description', 'type': 'string', 'required': False},
        {'name': 'DefaultAuthorisations', 'type': 'string', 'required': False},
    ],
    'users': [
        {'name': 'UserID', 'type': 'string', 'required': True},
        {'name': 'Name', 'type': 'string', 'required': True},
        {'name': 'Department', 'type': 'string', 'required': True},
        {'name': 'JobTitle', 'type': 'string', 'required': True},
        {'name': 'Status', 'type': 'string', 'required': True},
        {'name': 'Email', 'type': 'string', 'required': True},
        {'name': 'Manager', 'type': 'string', 'required': False},
        {'name': 'HireDate', 'type': 'date', 'required': True},
        {'name': 'TerminationDate', 'type': 'date', 'required': False},
        {'name': 'Environment', 'type': 'string', 'required': True},
    ],
    'sickLeave': [
        {'name': 'UserID', 'type': 'string', 'required': True},
        {'name': 'StartDate', 'type': 'date', 'required': True},
        {'name': 'EndDate', 'type': 'date', 'required': True},
        {'name': 'Status', 'type': 'string', 'required': True},
    ],
    'vacation': [
        {'name': 'UserID', 'type': 'string', 'required': True},
        {'name': 'StartDate', 'type': 'date', 'required': True},
        {'name': 'EndDate', 'type': 'date', 'required': True},
        {'name': 'Status', 'type': 'string', 'required': True},
    ],
    'audit_trail': [
        {'name': 'AuditID', 'type': 'string', 'required': True},
        {'name': 'MutationID', 'type': 'string', 'required': True},
        {'name': 'Timestamp', 'type': 'datetime', 'required': True},
        {'name': 'OldStatus', 'type': 'string', 'required': False},
        {'name': 'NewStatus', 'type': 'string', 'required': True},
        {'name': 'Agent', 'type': 'string', 'required': True},
        {'name': 'Comment', 'type': 'string', 'required': False},
    ],
}

import numpy as np
from pandas.api.types import is_string_dtype, is_datetime64_any_dtype

def _check_type(series, expected_type):
    if expected_type == 'string':
        return is_string_dtype(series) or series.dtype == object
    if expected_type == 'date':
        # Accept string or datetime for date, and allow empty/NaN for optional columns
        # If all non-empty values are string or datetime, it's valid
        mask = (~series.isna()) & (series.astype(str).str.strip() != '')
        if mask.any():
            filtered = series.loc[mask]
            return (is_string_dtype(series) or is_datetime64_any_dtype(series)
                    or filtered.apply(lambda x: isinstance(x, str) or pd.isna(x)).all())
        return True
    if expected_type == 'datetime':
        return is_datetime64_any_dtype(series) or is_string_dtype(series)
    return True  # fallback

def validate_schema(name, df):
    """Validate DataFrame columns/types against documented schema."""
    schema = CSV_SCHEMAS.get(name)
    if not schema:
        return True  # No schema to validate
    errors = []
    # Check required columns
    for col in schema:
        if col['required'] and col['name'] not in df.columns:
            errors.append(f"Missing required column: {col['name']}")
    # Check for extra columns
    for c in df.columns:
        if c not in [col['name'] for col in schema]:
            errors.append(f"Unexpected column: {c}")
    # Check types (best effort)
    for col in schema:
        if col['name'] in df.columns:
            if not _check_type(df[col['name']], col['type']):
                errors.append(f"Column {col['name']} has wrong type (expected {col['type']})")
        if col['required'] and col['name'] in df.columns:
            if df[col['name']].isnull().any() or (df[col['name']]=='' ).any():
                errors.append(f"Column {col['name']} has missing values")
    if errors:
        raise ValueError(f"Schema validation failed for {name}:\n" + '\n'.join(errors))
    return True

# Integrate schema validation into read_csv and write_csv
_ORIG_read_csv = read_csv
def read_csv(name, **kwargs):
    df = _ORIG_read_csv(name, **kwargs)
    # Ensure OldValue/NewValue are string for hr_mutations
    if name == 'hr_mutations':
        for col in ['OldValue', 'NewValue']:
            if col in df.columns:
                df[col] = df[col].astype(str)
    validate_schema(name, df)
    return df

_ORIG_write_csv = write_csv
def write_csv(name, df, **kwargs):
    # Ensure OldValue/NewValue are string for hr_mutations
    if name == 'hr_mutations':
        for col in ['OldValue', 'NewValue']:
            if col in df.columns:
                df[col] = df[col].astype(str)
    validate_schema(name, df)
    _ORIG_write_csv(name, df, **kwargs)
