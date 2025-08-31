import psycopg2
import os
import polars as pl
from psycopg2 import pool
from psycopg2.extras import execute_values

class FishDatabase:
    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        """Initialize the connection pool if not already done."""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST", "localhost"),
                    port=os.getenv("DB_PORT", "5432")
                )
                print("PostgreSQL connection pool initialized successfully")
            except Exception as e:
                print(f"Error initializing connection pool: {e}")
                raise

    def __init__(self):
        """Ensure the pool is initialized."""
        if FishDatabase._connection_pool is None:
            FishDatabase.initialize_pool()
        self.connection = None

    def get_connection(self):
        """Get a connection from the pool."""
        try:
            self.connection = FishDatabase._connection_pool.getconn()
            print("Retrieved connection from pool")
            return self.connection
        except Exception as e:
            print(f"Error retrieving connection from pool: {e}")
            return None

    def release_connection(self):
        """Return the connection to the pool."""
        if self.connection:
            FishDatabase._connection_pool.putconn(self.connection)
            print("Connection returned to pool")
            self.connection = None

    def close_connection(self):
        """Close the current connection (not typically needed with pooling)."""
        if self.connection:
            self.release_connection()
            print("Connection closed (returned to pool)")

    def close_all_connections(self):
        """Close all connections in the pool (e.g., for app shutdown)."""
        if FishDatabase._connection_pool:
            FishDatabase._connection_pool.closeall()
            print("All connections in pool closed")
            FishDatabase._connection_pool = None

    def query_to_df(self, query, params=None):
        """Execute a query and return results as a Polars DataFrame."""
        conn = self.get_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # Check if query returns results
                    colnames = [desc[0] for desc in cursor.description]
                    print(f"Column names: {colnames}")
                    rows = cursor.fetchall()
                    df = pl.DataFrame(rows, schema=colnames, orient="row")
                    return df
                return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            self.release_connection()