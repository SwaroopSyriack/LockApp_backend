from app.models import TableRegistery
import json


TYPE_MAP = {
    "TEXT": "TEXT",
    "VARCHAR": "TEXT",
    "CHAR": "TEXT",
    "STRING":"TEXT",

    "INTEGER": "INTEGER",
    "INT": "INTEGER",
    "BIGINT": "INTEGER",
    "SMALLINT": "INTEGER",

    "FLOAT": "REAL",
    "DOUBLE": "REAL",
    "REAL": "REAL",
    "DECIMAL": "NUMERIC",
    "NUMERIC": "NUMERIC",

    "BOOLEAN": "INTEGER",

    "DATE": "TEXT",
    "TIME": "TEXT",
    "TIMESTAMP": "TEXT",
    "DATETIME": "TEXT",

    "UUID": "TEXT",

    "JSON": "TEXT",
    "JSONB": "TEXT",

    "BLOB": "BLOB",
}

def build_create_ddl(table_name , columns) -> str:

    cols_defs = ['"id" INTEGER PRIMARY KEY AUTOINCREMENT']

    for col in columns:
        pg_type = TYPE_MAP[col.data_type.upper()]
        null_clause = "" if col.nullable else "NOT NULL"

        if col.default_value is not None:
            if isinstance(col.default_value, str):
                default_clause = f"DEFAULT '{col.default_value}'"
            elif isinstance(col.default_value , bool):
                default_clause = f"DEFAULT '{int(col.default_value)}'"

            else:
                default_clause = f"DEFAULT {col.default_value}"

        else:
            default_clause = ""

        cols_defs.append(f'"{col.column_name}" {pg_type}{null_clause}{default_clause}')

    col_block = ",\n    ".join(cols_defs)
    return f'''CREATE TABLE IF NOT EXISTS "{table_name}" (\n    {col_block}\n);'''.strip()


def _serialize(row: TableRegistery) -> dict:
    return {
        "id": row.id,
        "table_name": row.table_name,
        "display_name": row.display_name,
        "default" : row.is_default,
        "created_at": row.created_at,
        "columns": json.loads(row.columns_json),
    }




