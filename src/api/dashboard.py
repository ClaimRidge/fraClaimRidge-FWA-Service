from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Read the dashboard HTML file
    # For now, we'll embed the HTML directly or read it from a file
    dashboard_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        return f.read()
