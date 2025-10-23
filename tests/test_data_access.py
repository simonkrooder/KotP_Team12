import unittest
import pandas as pd
from src.data_access import validate_schema, CSV_SCHEMAS

class TestDataAccessSchema(unittest.TestCase):
    def test_all_csv_schemas(self):
        # For each schema, create a minimal valid DataFrame and validate
        for name, schema in CSV_SCHEMAS.items():
            columns = [col['name'] for col in schema]
            data = {}
            for col in schema:
                if col['type'] == 'string':
                    data[col['name']] = ['test']
                elif col['type'] == 'date':
                    data[col['name']] = ['2025-10-23']
                elif col['type'] == 'datetime':
                    data[col['name']] = ['2025-10-23T10:00:00']
                else:
                    data[col['name']] = ['test']
            df = pd.DataFrame(data)
            # Should not raise
            validate_schema(name, df)

    def test_missing_required_column(self):
        schema = CSV_SCHEMAS['users']
        columns = [col['name'] for col in schema if not col['required']]
        # Only optional columns
        df = pd.DataFrame({col: ['test'] for col in columns})
        with self.assertRaises(ValueError):
            validate_schema('users', df)

    def test_extra_column(self):
        schema = CSV_SCHEMAS['roles']
        data = {col['name']: ['test'] for col in schema}
        data['ExtraCol'] = ['oops']
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            validate_schema('roles', df)

    def test_missing_value(self):
        schema = CSV_SCHEMAS['hr_mutations']
        data = {col['name']: ['test'] for col in schema}
        # Set a required field to empty string
        data['MutationID'] = ['']
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            validate_schema('hr_mutations', df)

if __name__ == "__main__":
    unittest.main()