import os
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials
from dotenv import load_dotenv

load_dotenv()

_firebase_app: Optional[firebase_admin.App] = None


def initialize_firebase() -> Optional[firebase_admin.App]:
    """Initialize Firebase Admin SDK."""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    
    try:
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
        if private_key:
            private_key = private_key.replace("\\n", "\n")
        
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key": private_key,
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        })
        _firebase_app = firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized")
        return _firebase_app
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        return None


def get_firebase_auth():
    """Get Firebase auth instance."""
    return auth


def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token."""
    return auth.verify_id_token(token)
