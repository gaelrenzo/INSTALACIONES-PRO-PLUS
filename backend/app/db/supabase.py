import os
from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL: str | None = None
_SUPABASE_KEY: str | None = None
_CLIENT: Client | None = None


def get_supabase() -> Client:
    global _SUPABASE_URL, _SUPABASE_KEY, _CLIENT
    if _CLIENT is None:
        _SUPABASE_URL = os.getenv("SUPABASE_URL")
        _SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        if not _SUPABASE_URL or not _SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL y SUPABASE_KEY son requeridos en .env")
        _CLIENT = create_client(_SUPABASE_URL, _SUPABASE_KEY)
    return _CLIENT
