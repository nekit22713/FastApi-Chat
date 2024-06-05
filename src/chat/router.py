from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker

from src.chat.models import Message
from src.chat.schemas import MessageSchemaView, MessageSchemaCreate


router = APIRouter(
    prefix='/chat',
    tags=["Chat"]
)

class ConnectionManager:
    @staticmethod
    async def add_message_to_database(message: MessageSchemaCreate):
        async with async_session_maker() as session:
            statement = insert(Message).values(**message.model_dump())
            await session.execute(statement)
            await session.commit()

    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: MessageSchemaCreate, add_to_db: bool = False):
        if add_to_db:
            await self.add_message_to_database(message)
        for connection in self.active_connections:
            await connection.send_json(message.model_dump(mode='json'))


manager = ConnectionManager()

@router.get("/last_messages")
async def get_last_messages(session: AsyncSession = Depends(get_async_session)) -> list[MessageSchemaView]:
    query = select(Message).order_by(Message.id.desc()).limit(5)
    messages = await session.execute(query)
    return sorted(messages.scalars().all(), key=lambda x:x.id)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = MessageSchemaCreate(message=data, client_id=client_id)
            await manager.broadcast(message, add_to_db=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        message = MessageSchemaCreate(message=f"Client #{client_id} left chat", client_id=client_id)
        await manager.broadcast(message)
