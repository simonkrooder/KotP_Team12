import csv
import os

IN_FILE = 'audit_trail.csv'
OUT_FILE = 'audit_trail_clean.csv'
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
in_path = os.path.join(DATA_DIR, IN_FILE)
out_path = os.path.join(DATA_DIR, OUT_FILE)

def clean_audit_trail():
    with open(in_path, encoding='utf-8') as f:
        lines = f.readlines()
    # Find header
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('AuditID'):
            header_idx = i
            break
    if header_idx is None:
        print('No header found!')
        return
    # Write header and clean rows
    with open(out_path, 'w', encoding='utf-8', newline='') as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['AuditID','MutationID','Timestamp','OldStatus','NewStatus','Agent','Comment'])
        buf = ''
        for line in lines[header_idx+1:]:
            if not line.strip():
                continue
            # Merge lines until a valid row is formed
            if buf:
                buf += '\n' + line.rstrip('\n')
            else:
                buf = line.rstrip('\n')
            try:
                reader = csv.reader([buf])
                row = next(reader)
                if len(row) == 7:
                    writer.writerow(row)
                    buf = ''
            except Exception:
                # Not a valid row yet, keep buffering
                continue
        # If buffer remains, try to write it if valid
        if buf:
            try:
                reader = csv.reader([buf])
                row = next(reader)
                if len(row) == 7:
                    writer.writerow(row)
            except Exception:
                pass
    print(f'Cleaned audit trail written to {out_path}')

if __name__ == '__main__':
    clean_audit_trail()