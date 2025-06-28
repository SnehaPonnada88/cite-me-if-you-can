from fastapi import APIRouter
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.usage_tracker import get_usage

router = APIRouter()

@router.get("/api/usage_count")
def usage_count():
    return get_usage()
