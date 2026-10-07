import sqlite3
import uuid
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from config import DB_PATH, GEMINI_API_KEY, TAVILY_API_KEY

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_keys_table():
    conn = get_connection()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,         -- 'gemini', 'openai', 'groq', 'tavily'
            api_key TEXT NOT NULL,
            model TEXT NOT NULL,            -- e.g. 'gemini-flash-latest', 'gpt-4o-mini'
            is_active INTEGER DEFAULT 0,
            created_at TEXT
        );
        """)
    conn.close()
    bootstrap_initial_keys()

def bootstrap_initial_keys():
    """Migrate initial .env keys into the manager if table is empty"""
    conn = get_connection()
    with conn:
        cursor = conn.execute("SELECT COUNT(*) FROM api_keys")
        count = cursor.fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            if GEMINI_API_KEY:
                conn.execute("""
                INSERT INTO api_keys (id, name, provider, api_key, model, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (f"key_{uuid.uuid4().hex[:8]}", "Default Gemini Flash", "gemini", GEMINI_API_KEY, "gemini-flash-latest", now))
            
            if TAVILY_API_KEY:
                conn.execute("""
                INSERT INTO api_keys (id, name, provider, api_key, model, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (f"key_{uuid.uuid4().hex[:8]}", "Default Tavily Search", "tavily", TAVILY_API_KEY, "tavily-advanced", now))
    conn.close()

def get_all_keys(provider_type: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if provider_type:
        cursor = conn.execute("SELECT * FROM api_keys WHERE provider = ? ORDER BY created_at DESC", (provider_type,))
    else:
        cursor = conn.execute("SELECT * FROM api_keys ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def add_api_key(name: str, provider: str, api_key: str, model: str, set_active: bool = True) -> str:
    """Adds a new named API key and optionally activates it, changing the agent's model"""
    conn = get_connection()
    key_id = f"key_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    
    with conn:
        # If setting active and it's an LLM provider, deactivate other LLM keys
        is_llm = provider in ["gemini", "openai", "groq"]
        if set_active:
            if is_llm:
                conn.execute("UPDATE api_keys SET is_active = 0 WHERE provider IN ('gemini', 'openai', 'groq')")
            elif provider == "tavily":
                conn.execute("UPDATE api_keys SET is_active = 0 WHERE provider = 'tavily'")

        conn.execute("""
        INSERT INTO api_keys (id, name, provider, api_key, model, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (key_id, name.strip(), provider.lower().strip(), api_key.strip(), model.strip(), 1 if set_active else 0, now))
    conn.close()
    return key_id

def delete_api_key(key_id: str) -> bool:
    """Deletes an API key. If it was active, activates another existing key of the same category."""
    conn = get_connection()
    with conn:
        # Check if the deleted key was active
        cursor = conn.execute("SELECT provider, is_active FROM api_keys WHERE id = ?", (key_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
            
        provider = row["provider"]
        was_active = row["is_active"]
        
        conn.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
        
        # If it was active, activate the most recent remaining key
        if was_active:
            is_llm = provider in ["gemini", "openai", "groq"]
            if is_llm:
                conn.execute("""
                UPDATE api_keys SET is_active = 1 WHERE id = (
                    SELECT id FROM api_keys WHERE provider IN ('gemini', 'openai', 'groq') ORDER BY created_at DESC LIMIT 1
                )
                """)
            else:
                conn.execute("""
                UPDATE api_keys SET is_active = 1 WHERE id = (
                    SELECT id FROM api_keys WHERE provider = 'tavily' ORDER BY created_at DESC LIMIT 1
                )
                """)
    conn.close()
    return True

def set_active_key(key_id: str) -> bool:
    """Sets a specific key as active, dynamically changing the agent's model"""
    conn = get_connection()
    with conn:
        cursor = conn.execute("SELECT provider FROM api_keys WHERE id = ?", (key_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        
        provider = row["provider"]
        is_llm = provider in ["gemini", "openai", "groq"]
        
        if is_llm:
            conn.execute("UPDATE api_keys SET is_active = 0 WHERE provider IN ('gemini', 'openai', 'groq')")
        else:
            conn.execute("UPDATE api_keys SET is_active = 0 WHERE provider = 'tavily'")
            
        conn.execute("UPDATE api_keys SET is_active = 1 WHERE id = ?", (key_id,))
    conn.close()
    return True

def get_active_llm() -> Dict[str, Any]:
    """Returns the currently active LLM configuration (provider, api_key, model, name)"""
    conn = get_connection()
    cursor = conn.execute("""
    SELECT * FROM api_keys 
    WHERE is_active = 1 AND provider IN ('gemini', 'openai', 'groq') 
    LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    
    # Fallback to config default
    return {
        "id": "default",
        "name": "Fallback Gemini Flash",
        "provider": "gemini",
        "api_key": GEMINI_API_KEY,
        "model": "gemini-flash-latest",
        "is_active": 1
    }

def get_active_search_key() -> str:
    """Returns the currently active Tavily API key"""
    conn = get_connection()
    cursor = conn.execute("SELECT api_key FROM api_keys WHERE is_active = 1 AND provider = 'tavily' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row and row["api_key"]:
        return row["api_key"]
    return TAVILY_API_KEY

def mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "********"
    return f"{key[:6]}...{key[-4:]}"

# Initialize on import
init_keys_table()
