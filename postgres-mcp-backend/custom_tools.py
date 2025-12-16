"""custom_tools.py"""
from __future__ import annotations

import datetime
import json
import os

from dotenv import load_dotenv
from langchain.tools import tool
from sqlalchemy import create_engine, inspect
from typing import List, Any
import asyncpg
import config

load_dotenv()
DB_URL = config.DB_URL.replace("postgres://", "postgresql://")
engine = create_engine(DB_URL)
inspector = inspect(engine)


def make_json_serializable(obj):
    """
    :param obj:
    :return:
    """
    from datetime import datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, int):
        return str(obj)
    try:
        return json.loads(obj)
    except Exception:
        return obj


@tool("list_tables", return_direct=True, description="List all tables")
def list_tables_tool() -> List[str]:
    """Return all table names in the PostgreSQL database."""
    return inspector.get_table_names()


@tool("list_columns", return_direct=True, description="List all columns of table_name. "
                                                      "Input should be a single table name.")
def list_columns_tool(table_name: str) -> List[str]:
    """Return all column names for a given table."""
    if table_name not in inspector.get_table_names():
        return [f"Table '{table_name}' does not exist."]
    return [col["name"] for col in inspector.get_columns(table_name)]


@tool("get_large_array", return_direct=True,
      description="Get records from table where atomic_alias_array length > length. ")
async def get_large_array_tool(table_name: str, length: int, less_than: bool, asc: bool, limit: int = 20) -> list | str:
    """
    Get at least one record from table where  length > .

    Returns:
        JSON string containing the query result or error message
    """
    try:
        conn = await asyncpg.connect(DB_URL)

        if table_name not in inspector.get_table_names():
            return f"Table '{table_name}' does not exist."
        query = f"SELECT id, master_name, atomic_alias_array, ratified, created_at  FROM {table_name} "
        if less_than:
            query = query + f" WHERE array_length(atomic_alias_array, 1) < {length}"
        else:
            query = query + f" WHERE array_length(atomic_alias_array, 1) > {length}"

        if asc:
            query = query + " ORDER BY created_at ASC"
        else:
            query = query + " ORDER BY created_at DESC"

        if limit > 0:
            query = query + f" LIMIT {limit}"

        results = await conn.fetch(query)
        await conn.close()

        if results:
            response = []
            for result in results:
                record_dict = dict(result)
                for k, v in record_dict.items():
                    record_dict[k] = make_json_serializable(v)
                response.append(record_dict)
            return response
        else:
            return f"No records found with atomic_alias_array length > {length}"

    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool("get_supplier", return_direct=True,
      description="Get supplier records for a given component from alias_record table.")
async def get_supplier_tool(component: str, limit: int = 20) -> None | list[Any] | str:
    """
    Get supplier records for a given component from alias_record table.

    Returns:
        JSON string containing the query result or error message
    """
    try:
        conn = await asyncpg.connect(DB_URL)
        query = f"select id, supplier, component, version, release, scope, master_pair_id, created_at from alias_record where component = '{component}'"
        if limit:
            query = query + f" limit {limit}"
        results = await conn.fetch(query)
        await conn.close()
        if results:
            response = []
            for result in results:
                record_dict = dict(result)
                for k, v in record_dict.items():
                    record_dict[k] = make_json_serializable(v)
                response.append(record_dict)

            return response
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool("get_component", return_direct=True,
      description="Get component records for a given supplier from alias_record table.")
async def get_component_tool(supplier: str, limit: int = 20) -> None | list[Any] | str:
    """
    Get component records for a given supplier from alias_record table.

    Returns
        JSON string containing the query result or error message
    """
    try:
        conn = await asyncpg.connect(DB_URL)
        query = f"select id, supplier, component, version, release, scope, master_pair_id, created_at  from alias_record where supplier = '{supplier}'"
        if limit:
            query = query + f" limit {limit}"
        results = await conn.fetch(query)
        await conn.close()
        if results:
            response = []
            for result in results:
                record_dict = dict(result)
                for k, v in record_dict.items():
                    record_dict[k] = make_json_serializable(v)
                response.append(record_dict)

            return response
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool("create_excel", return_direct=True, description="Create an Excel report based on the provided SQL query if excel keyword in user prompt.")
async def create_excel(sql_query, file_name_suggestion: str = "") -> None | dict[str, str] | str:
    """
    This creates an Excel report based on the provided SQL query.
    param:
        sql_query: The SQL query to execute.
        file_name_suggestion: Suggested name for the Excel file without .xlsx.

    Returns:
        Excel file or error message
    """
    try:
        conn = await asyncpg.connect(DB_URL)
        results = await conn.fetch(sql_query)
        await conn.close()
        if results:
            response = []
            for result in results:
                record_dict = dict(result)
                for k, v in record_dict.items():
                    record_dict[k] = make_json_serializable(v)
                response.append(record_dict)

            # Create Excel file from response
            import pandas as pd
            import uuid
            from fastapi.responses import FileResponse

            df = pd.DataFrame(response)
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            out_dir = os.path.join(backend_dir, "reports")
            os.makedirs(out_dir, exist_ok=True)
            filename = f"{file_name_suggestion}_{datetime.datetime.now()}.xlsx"
            file_path = os.path.join(out_dir, filename)
            df.to_excel(file_path, index=False)

            return {"file_path": file_path, "filename": filename}

    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool("count_products", return_direct=True,
      description="Count products from product table whose releases are red and created within given date.")
async def count_products_tool(start_date, end_date) -> None | list[Any] | str:
    """
    Count products from product table whose releases are red and created within given date.

    Returns:
        JSON string containing the query result or error message
    """
    try:
        conn = await asyncpg.connect(DB_URL)
        query = f"""
        SELECT count(*)
        FROM product p
        JOIN release r ON p.id = r.product_fk
        WHERE r.state = 'RED'
          AND p.created_at >= '{start_date}'
          AND p.created_at <= '{end_date}'
        """
        results = await conn.fetch(query)
        await conn.close()
        if results:
            response = []
            for result in results:
                record_dict = dict(result)
                for k, v in record_dict.items():
                    record_dict[k] = make_json_serializable(v)
                response.append(record_dict)

            return response
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool("create_chart_products", return_direct=True,
      description="Get products from product table and create chat based on release status green or red whose releases are red and created within given date.")
async def create_chart_products(start_date, end_date) -> None | dict[str, Any] | str:
    """
    Get products from product table and create chat based on release status green or red whose releases are red and created within given date.

    Returns:
        JSON string containing the query result or error message
    """
    try:
        conn = await asyncpg.connect(DB_URL)
        query = f"""
        SELECT *
        FROM product p
        JOIN release r ON p.id = r.product_fk
        WHERE p.created_at >= '{start_date}'
          AND p.created_at <= '{end_date}'
        """
        results = await conn.fetch(query)
        await conn.close()
        if results:
            response = []
            for result in results:
                record_dict = dict(result)
                for k, v in record_dict.items():
                    record_dict[k] = make_json_serializable(v)
                response.append(record_dict)
            colors = ['RED', 'GREEN']
            counts = {color: 0 for color in colors}
            for record in response:
                state = record.get('state')
                if state in counts:
                    counts[state] += 1
            result = {
                'chart_type': 'pie',
                'data': [{'label': color, 'value': counts[color]} for color in colors]
            }
            return result
    except Exception as e:
        return f"Error executing query: {str(e)}"
