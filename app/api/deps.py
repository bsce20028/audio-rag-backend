from app.core.database import SyncSessionLocal

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()