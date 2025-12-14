from core.secure_store import SecureStore
from core.api_registry import APIRegistry
import os
import shutil

def test_security():
    print("--- Starting Security Verification ---")
    
    # 1. Setup
    if os.path.exists("test_sessions.db"):
        os.remove("test_sessions.db")
    
    # Init store (uses default 'sessions.db' in code, we might want to override path but code is hardcoded to sessions.db)
    # So we will backup existing if any
    if os.path.exists("sessions.db"):
        shutil.move("sessions.db", "sessions.db.bak")
        
    store = SecureStore()
    
    # 2. Test Encryption
    sid = "test_session_123"
    data = {"llm": "sk-fake-key", "search": "tvly-fake-key"}
    
    print("Encrypting and saving...")
    store.save_session(sid, data)
    
    # 3. Test Decryption
    print("Loading and decrypting...")
    loaded = store.load_session(sid)
    
    if loaded == data:
        print("✅ Decryption successful. Data matches.")
    else:
        print(f"❌ Data mismatch! Expected {data}, got {loaded}")
        
    # 4. Test Persisted File (basic check that it's blob)
    import sqlite3
    conn = sqlite3.connect("sessions.db")
    c = conn.cursor()
    c.execute("SELECT payload FROM sessions WHERE session_id=?", (sid,))
    row = c.fetchone()
    conn.close()
    
    if row and isinstance(row[0], bytes):
        print("✅ Database verification: Payload is bytes (encrypted blob).")
    else:
        print("❌ Database verification failed. Payload not bytes.")

    # 5. Cleanup
    store.delete_session(sid)
    loaded_after = store.load_session(sid)
    if loaded_after is None:
        print("✅ Deletion successful.")
    else:
        print("❌ Deletion failed.")

    # Restore original DB
    if os.path.exists("sessions.db"):
        os.remove("sessions.db")
    if os.path.exists("sessions.db.bak"):
        shutil.move("sessions.db.bak", "sessions.db")

    print("--- Security Verification Complete ---")

if __name__ == "__main__":
    test_security()
