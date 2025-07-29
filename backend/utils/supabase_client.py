from supabase import create_client, Client
import os
from config import Config

class SupabaseClient:
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_API_KEY
        self.client: Client = create_client(self.url, self.key)

    def get_client(self):
        return self.client

# Global instance
supabase_client = SupabaseClient()
