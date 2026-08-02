"""Placeholder registry API endpoints.

Provides access to placeholder definitions for broadcast messages.
Separate from broadcast endpoints for cleaner architecture.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.services.placeholder_registry import get_placeholders, get_safe_user_fields

router = APIRouter(prefix="/placeholders", tags=["placeholders"])


@router.get("/registry")
def get_placeholder_registry(db: Session = Depends(get_db)):
    """Placeholder registry'ni qaytaradi
    
    Returns:
        Dict containing PLACEHOLDER_REGISTRY and SAFE_USER_FIELDS
    """
    placeholders = get_placeholders()
    safe_fields = get_safe_user_fields()
    
    # Convert list format to dict format as specified in task
    # Backend stores as list of dicts: [{"key": "{id}", "label": "...", "example": "..."}]
    # Task requires dict format: {"{id}": "{id}", "{email}": "{email}", ...}
    placeholder_dict = {}
    for p in placeholders:
        key = p.get("key", "")
        if key:
            placeholder_dict[key] = key
    
    return {
        "PLACEHOLDER_REGISTRY": placeholder_dict,
        "SAFE_USER_FIELDS": safe_fields,
    }


@router.get("/list")
def get_placeholder_list():
    """Get all available placeholders with metadata.
    
    Returns list of placeholders with key, label, and example.
    """
    placeholders = get_placeholders()
    return {"placeholders": placeholders}


@router.get("/safe-fields")
def get_safe_fields():
    """Get list of safe user field names for placeholders.
    
    Returns list of field names (without {}) that are safe to use.
    """
    safe_fields = get_safe_user_fields()
    return {"safe_fields": safe_fields}