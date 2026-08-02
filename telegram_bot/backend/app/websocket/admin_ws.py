import json
import asyncio
import logging
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.logs import ErrorLog

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for admin panel."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        dead = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.add(connection)
        for conn in dead:
            self.active_connections.discard(conn)


manager = ConnectionManager()


@router.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket, db: DBSession = Depends(get_db)):
    """Admin WebSocket for real-time notifications."""
    await manager.connect(websocket)
    try:
        # Send heartbeat and error notifications
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Check for new errors every 30s
                recent_errors = db.query(ErrorLog).filter(
                    ErrorLog.is_fixed == False
                ).order_by(ErrorLog.created_at.desc()).limit(5).all()

                if recent_errors:
                    await websocket.send_json({
                        "type": "error_update",
                        "errors": [
                            {
                                "id": e.id,
                                "service": e.service,
                                "error_type": e.error_type,
                                "severity": e.severity,
                                "created_at": str(e.created_at),
                            }
                            for e in recent_errors
                        ],
                    })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)