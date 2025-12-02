import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional

from app.config.settings import settings


_firebase_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> Optional[firebase_admin.App]:
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if not firebase_admin._apps:
        try:
            if settings.firebase_project_id and settings.firebase_private_key and settings.firebase_client_email:
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": settings.firebase_project_id,
                    "private_key": settings.firebase_private_key.replace("\\n", "\n") if settings.firebase_private_key else None,
                    "client_email": settings.firebase_client_email,
                })
                _firebase_app = firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized")
            else:
                print("Firebase credentials not configured, skipping initialization")
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")
    else:
        _firebase_app = firebase_admin.get_app()
    
    return _firebase_app


def verify_firebase_token(token: str) -> Optional[dict]:
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        return None
