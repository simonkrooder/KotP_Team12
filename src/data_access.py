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

# Optional: add schema validation hooks here
def validate_schema(name, df):
    """Validate DataFrame columns/types against documented schema (stub)."""
    # TODO: Implement schema validation using /docs/csv_schemas.md
    pass
