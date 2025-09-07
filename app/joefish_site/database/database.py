import polars as pl
from django.db import connection


class FishDatabase:
    def query_to_df(self, query, params=None):
        """Execute a raw SQL query using Django's database connection and return results as a Polars DataFrame."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # Check if query returns results
                    colnames = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    df = pl.DataFrame(rows, schema=colnames, orient="row")
                    return df
                return None
        except Exception as e:
            print(f"Database query error: {e}")
            return None
