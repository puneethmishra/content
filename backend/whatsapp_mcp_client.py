import asyncio
import json
import logging
import websockets
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppMCPClient:
    def __init__(self):
        self.mcp_server_url = os.getenv("WHATSAPP_MCP_SERVER_URL", "ws://localhost:8001")
        self.http_url = os.getenv("WHATSAPP_HTTP_URL", "http://localhost:8001")
        self.websocket = None
        self.connected = False
        self.message_queue = []
        self.session_id = None
        
    async def connect(self) -> bool:
        """Connect to WhatsApp MCP Server"""
        try:
            # First try to connect via HTTP to check if server is running
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.http_url}/status")
                if response.status_code == 200:
                    logger.info("WhatsApp MCP HTTP server is running")
                    
            # Connect via WebSocket for real-time communication
            if self.mcp_server_url.startswith("ws"):
                self.websocket = await websockets.connect(self.mcp_server_url)
                self.connected = True
                logger.info("Connected to WhatsApp MCP WebSocket server")
                
                # Start background task to handle incoming messages
                asyncio.create_task(self._message_handler())
                
                # Initialize session
                await self._init_session()
                return True
            else:
                # HTTP-only mode
                self.connected = True
                logger.info("Connected to WhatsApp MCP HTTP server")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to WhatsApp MCP server: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WhatsApp MCP Server"""
        try:
            if self.websocket:
                await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from WhatsApp MCP server")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    async def _init_session(self):
        """Initialize WhatsApp session"""
        try:
            if self.websocket:
                # Send session initialization request
                request = {
                    "method": "initialize",
                    "params": {
                        "capabilities": ["messages", "contacts", "groups"]
                    }
                }
                await self.websocket.send(json.dumps(request))
                
                # Wait for response
                response = await self.websocket.recv()
                data = json.loads(response)
                
                if data.get("success"):
                    self.session_id = data.get("session_id")
                    logger.info(f"WhatsApp session initialized: {self.session_id}")
                else:
                    logger.error("Failed to initialize WhatsApp session")
            else:
                # HTTP initialization
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{self.http_url}/api/session/init")
                    if response.status_code == 200:
                        data = response.json()
                        self.session_id = data.get("session_id")
                        logger.info("WhatsApp session initialized via HTTP")
                        
        except Exception as e:
            logger.error(f"Session initialization error: {e}")
    
    async def _message_handler(self):
        """Handle incoming messages from WhatsApp MCP"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "message":
                        # Add to message queue for processing
                        self.message_queue.append(data.get("payload"))
                        logger.debug(f"Received message: {data}")
                        
                    elif data.get("type") == "status":
                        logger.info(f"Status update: {data.get('status')}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Message handler error: {e}")
    
    async def get_new_messages(self) -> List[Dict[str, Any]]:
        """Get new messages from the queue"""
        try:
            if self.websocket and self.connected:
                # Return messages from WebSocket queue
                messages = self.message_queue.copy()
                self.message_queue.clear()
                return messages
            else:
                # Poll via HTTP
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.http_url}/api/messages/new")
                    if response.status_code == 200:
                        return response.json().get("messages", [])
                    
        except Exception as e:
            logger.error(f"Error getting new messages: {e}")
            
        return []
    
    async def send_message(self, phone_number: str, message_text: str, message_type: str = "text") -> bool:
        """Send a message via WhatsApp MCP"""
        try:
            message_data = {
                "to": phone_number,
                "text": message_text,
                "type": message_type,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.websocket and self.connected:
                # Send via WebSocket
                request = {
                    "method": "send_message",
                    "params": message_data
                }
                await self.websocket.send(json.dumps(request))
                
                # Wait for confirmation
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                return data.get("success", False)
            else:
                # Send via HTTP
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.http_url}/api/messages/send",
                        json=message_data
                    )
                    return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {e}")
            return False
    
    async def get_contacts(self) -> List[Dict[str, Any]]:
        """Get WhatsApp contacts"""
        try:
            if self.websocket and self.connected:
                request = {
                    "method": "get_contacts",
                    "params": {}
                }
                await self.websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                return data.get("contacts", [])
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.http_url}/api/contacts")
                    if response.status_code == 200:
                        return response.json()
                        
        except Exception as e:
            logger.error(f"Error getting contacts: {e}")
            
        return []
    
    async def get_chat_history(self, phone_number: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a specific contact"""
        try:
            params = {
                "phone_number": phone_number,
                "limit": limit
            }
            
            if self.websocket and self.connected:
                request = {
                    "method": "get_chat_history",
                    "params": params
                }
                await self.websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                return data.get("messages", [])
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.http_url}/api/chat/{phone_number}/history",
                        params={"limit": limit}
                    )
                    if response.status_code == 200:
                        return response.json()
                        
        except Exception as e:
            logger.error(f"Error getting chat history for {phone_number}: {e}")
            
        return []
    
    async def get_status(self) -> Dict[str, Any]:
        """Get WhatsApp connection status"""
        try:
            if self.websocket and self.connected:
                request = {
                    "method": "get_status",
                    "params": {}
                }
                await self.websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                data = json.loads(response)
                
                return {
                    "connected": True,
                    "phone_number": data.get("phone_number"),
                    "status": data.get("status", "online"),
                    "last_seen": data.get("last_seen"),
                    "session_id": self.session_id
                }
            else:
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(f"{self.http_url}/api/status")
                        if response.status_code == 200:
                            data = response.json()
                            return {
                                "connected": True,
                                "phone_number": data.get("phone_number"),
                                "status": data.get("status", "online"),
                                "last_seen": data.get("last_seen")
                            }
                    except httpx.ConnectError:
                        pass
                        
            return {
                "connected": False,
                "phone_number": None,
                "status": "disconnected",
                "last_seen": None
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "connected": False,
                "phone_number": None,
                "status": "error",
                "last_seen": None,
                "error": str(e)
            }
    
    async def create_group(self, name: str, participants: List[str]) -> bool:
        """Create a WhatsApp group"""
        try:
            group_data = {
                "name": name,
                "participants": participants
            }
            
            if self.websocket and self.connected:
                request = {
                    "method": "create_group",
                    "params": group_data
                }
                await self.websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(response)
                
                return data.get("success", False)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.http_url}/api/groups/create",
                        json=group_data
                    )
                    return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            return False
    
    async def send_media(self, phone_number: str, media_path: str, caption: str = "", media_type: str = "image") -> bool:
        """Send media file via WhatsApp"""
        try:
            media_data = {
                "to": phone_number,
                "media_path": media_path,
                "caption": caption,
                "type": media_type,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.websocket and self.connected:
                request = {
                    "method": "send_media",
                    "params": media_data
                }
                await self.websocket.send(json.dumps(request))
                
                response = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)  # Longer timeout for media
                data = json.loads(response)
                
                return data.get("success", False)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.http_url}/api/messages/send_media",
                        json=media_data
                    )
                    return response.status_code == 200
                    
        except Exception as e:
            logger.error(f"Error sending media to {phone_number}: {e}")
            return False