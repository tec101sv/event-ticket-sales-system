from supabase import create_client
from config import Config
import psycopg2
from psycopg2.extras import RealDictCursor

class SupabaseDB:
    _instance = None
    _client = None
    _pg_conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = create_client(Config.SUPABASE_URL, Config.SUPABASE_API_KEY)
        if self._pg_conn is None:
            try:
                self._pg_conn = psycopg2.connect(Config.DATABASE_URL)
            except Exception as e:
                print(f"PostgreSQL connection error: {e}")

    def get_client(self):
        return self._client

    def execute_query(self, table_or_query, query_type='select', query_params=None, fetch=None):
        """
        Execute a query on Supabase.
        If table_or_query contains SQL, execute it directly.
        Otherwise, use the table-based approach.
        """
        try:
            # If it's a SQL query (contains spaces and SQL keywords)
            if ' ' in table_or_query and any(keyword in table_or_query.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                return self._execute_sql(table_or_query, query_params, fetch)
            
            # Otherwise, use table-based approach
            if query_type == 'select':
                response = self._client.table(table_or_query).select('*').execute()
                return response.data
            elif query_type == 'insert':
                response = self._client.table(table_or_query).insert(query_params).execute()
                return response.data
            elif query_type == 'update':
                # query_params should include 'values' and 'filter'
                response = self._client.table(table_or_query).update(query_params['values']).eq(**query_params['filter']).execute()
                return response.data
            elif query_type == 'delete':
                # query_params should include 'filter'
                response = self._client.table(table_or_query).delete().eq(**query_params['filter']).execute()
                return response.data
            else:
                raise ValueError('Unsupported query type')
        except Exception as e:
            print(f"Supabase query error: {e}")
            raise

    def _execute_sql(self, query, params=None, fetch=None):
        """Execute raw SQL query using PostgreSQL connection"""
        try:
            if not self._pg_conn or self._pg_conn.closed:
                self._pg_conn = psycopg2.connect(Config.DATABASE_URL)
            
            with self._pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                if fetch == 'one':
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch == True or fetch == 'all':
                    results = cursor.fetchall()
                    return [dict(row) for row in results] if results else []
                else:
                    # For INSERT/UPDATE/DELETE operations
                    self._pg_conn.commit()
                    if cursor.description:  # If query returns data
                        results = cursor.fetchall()
                        return [dict(row) for row in results] if results else []
                    return True
                    
        except Exception as e:
            if self._pg_conn:
                self._pg_conn.rollback()
            print(f"SQL execution error: {e}")
            raise

# Global Supabase client instance
supabase_db = SupabaseDB()

def init_database():
    """
    Supabase manages schema via SQL editor or migrations outside this client.
    This function can be used to verify connection.
    """
    try:
        # Simple test query
        data = supabase_db.execute_query('users')
        print(f"Supabase connection test successful, users count: {len(data)}")
        return True
    except Exception as e:
        print(f"Error testing Supabase connection: {e}")
        return False

def get_db():
    return supabase_db
