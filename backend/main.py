from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

# Import our custom modules
from database import engine, SessionLocal, Base
from models import Message, Classification, AutoResponse, Contact, Settings
from schemas import (
    MessageCreate, MessageResponse, ClassificationCreate, ClassificationResponse,
    AutoResponseCreate, AutoResponseResponse, ContactResponse, SettingsResponse,
    BroadcastMessageRequest, MessageStats
)
from whatsapp_mcp_client import WhatsAppMCPClient
from message_classifier import MessageClassifier
from response_generator import ResponseGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="WhatsApp MCP Dashboard",
    description="A comprehensive dashboard for WhatsApp message management with AI-powered classification and automated responses",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
whatsapp_client = WhatsAppMCPClient()
message_classifier = MessageClassifier()
response_generator = ResponseGenerator()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await whatsapp_client.connect()
        logger.info("WhatsApp MCP client connected successfully")
        
        # Start message monitoring
        asyncio.create_task(monitor_messages())
        logger.info("Message monitoring started")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await whatsapp_client.disconnect()
        logger.info("WhatsApp MCP client disconnected")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Background task for monitoring incoming messages
async def monitor_messages():
    """Monitor incoming WhatsApp messages and process them"""
    while True:
        try:
            # Get new messages from WhatsApp MCP
            new_messages = await whatsapp_client.get_new_messages()
            
            if new_messages:
                db = SessionLocal()
                try:
                    for msg_data in new_messages:
                        await process_incoming_message(msg_data, db)
                finally:
                    db.close()
                    
        except Exception as e:
            logger.error(f"Error in message monitoring: {e}")
            
        await asyncio.sleep(5)  # Check every 5 seconds

async def process_incoming_message(msg_data: Dict, db: Session):
    """Process a single incoming message"""
    try:
        # Save message to database
        message = Message(
            phone_number=msg_data.get("from", ""),
            contact_name=msg_data.get("contact_name", "Unknown"),
            message_text=msg_data.get("text", ""),
            message_type=msg_data.get("type", "text"),
            timestamp=datetime.fromisoformat(msg_data.get("timestamp", datetime.now().isoformat())),
            is_incoming=True,
            raw_data=json.dumps(msg_data)
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Classify the message
        classification_result = await message_classifier.classify_message(message.message_text)
        
        classification = Classification(
            message_id=message.id,
            category=classification_result["category"],
            confidence=classification_result["confidence"],
            tags=",".join(classification_result.get("tags", [])),
            sentiment=classification_result.get("sentiment", "neutral")
        )
        db.add(classification)
        db.commit()
        
        # Check for auto-response
        auto_response = db.query(AutoResponse).filter(
            AutoResponse.category == classification.category,
            AutoResponse.is_active == True
        ).first()
        
        if auto_response:
            # Generate and send response
            response_text = await response_generator.generate_response(
                message.message_text,
                auto_response.template,
                classification_result
            )
            
            # Send response via WhatsApp MCP
            await whatsapp_client.send_message(message.phone_number, response_text)
            
            # Save sent message to database
            response_message = Message(
                phone_number=message.phone_number,
                contact_name=message.contact_name,
                message_text=response_text,
                message_type="text",
                timestamp=datetime.now(),
                is_incoming=False,
                parent_message_id=message.id,
                raw_data=json.dumps({"auto_response": True, "template_id": auto_response.id})
            )
            db.add(response_message)
            db.commit()
            
            logger.info(f"Auto-response sent to {message.phone_number}")
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        db.rollback()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "WhatsApp MCP Dashboard API", "status": "running"}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> MessageStats:
    """Get dashboard statistics"""
    try:
        total_messages = db.query(Message).count()
        total_incoming = db.query(Message).filter(Message.is_incoming == True).count()
        total_outgoing = db.query(Message).filter(Message.is_incoming == False).count()
        total_contacts = db.query(Message).distinct(Message.phone_number).count()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_messages = db.query(Message).filter(Message.timestamp >= yesterday).count()
        
        # Get classification stats
        classifications = db.query(Classification).all()
        category_stats = {}
        for cls in classifications:
            category_stats[cls.category] = category_stats.get(cls.category, 0) + 1
            
        return MessageStats(
            total_messages=total_messages,
            total_incoming=total_incoming,
            total_outgoing=total_outgoing,
            total_contacts=total_contacts,
            recent_messages=recent_messages,
            category_stats=category_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages", response_model=List[MessageResponse])
async def get_messages(
    skip: int = 0,
    limit: int = 100,
    phone_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get messages with optional filtering"""
    try:
        query = db.query(Message)
        
        if phone_number:
            query = query.filter(Message.phone_number == phone_number)
            
        messages = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
        
        # Include classification data
        result = []
        for message in messages:
            classification = db.query(Classification).filter(Classification.message_id == message.id).first()
            msg_dict = {
                "id": message.id,
                "phone_number": message.phone_number,
                "contact_name": message.contact_name,
                "message_text": message.message_text,
                "message_type": message.message_type,
                "timestamp": message.timestamp,
                "is_incoming": message.is_incoming,
                "parent_message_id": message.parent_message_id,
                "classification": {
                    "category": classification.category if classification else "unclassified",
                    "confidence": classification.confidence if classification else 0.0,
                    "tags": classification.tags.split(",") if classification and classification.tags else [],
                    "sentiment": classification.sentiment if classification else "neutral"
                } if classification else None
            }
            result.append(msg_dict)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages/send")
async def send_message(
    phone_number: str,
    message_text: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send a message to a specific contact"""
    try:
        # Send message via WhatsApp MCP
        success = await whatsapp_client.send_message(phone_number, message_text)
        
        if success:
            # Save to database
            message = Message(
                phone_number=phone_number,
                contact_name="",  # Will be updated when we get contact info
                message_text=message_text,
                message_type="text",
                timestamp=datetime.now(),
                is_incoming=False,
                raw_data=json.dumps({"manual_send": True})
            )
            db.add(message)
            db.commit()
            
            return {"success": True, "message": "Message sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages/broadcast")
async def broadcast_message(
    request: BroadcastMessageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Broadcast a message to multiple contacts"""
    try:
        sent_count = 0
        failed_count = 0
        
        for phone_number in request.phone_numbers:
            try:
                success = await whatsapp_client.send_message(phone_number, request.message_text)
                
                if success:
                    # Save to database
                    message = Message(
                        phone_number=phone_number,
                        contact_name="",
                        message_text=request.message_text,
                        message_type="text",
                        timestamp=datetime.now(),
                        is_incoming=False,
                        raw_data=json.dumps({"broadcast": True, "campaign_id": request.campaign_id})
                    )
                    db.add(message)
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send to {phone_number}: {e}")
                failed_count += 1
                
        db.commit()
        
        return {
            "success": True,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_requested": len(request.phone_numbers)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/classifications", response_model=List[ClassificationResponse])
async def get_classifications(db: Session = Depends(get_db)):
    """Get all message classifications with stats"""
    try:
        classifications = db.query(Classification).all()
        
        # Group by category and calculate stats
        category_stats = {}
        for cls in classifications:
            if cls.category not in category_stats:
                category_stats[cls.category] = {
                    "category": cls.category,
                    "count": 0,
                    "avg_confidence": 0.0,
                    "sentiments": {"positive": 0, "negative": 0, "neutral": 0}
                }
            
            category_stats[cls.category]["count"] += 1
            category_stats[cls.category]["avg_confidence"] += cls.confidence
            category_stats[cls.category]["sentiments"][cls.sentiment] += 1
            
        # Calculate averages
        for category in category_stats:
            stats = category_stats[category]
            stats["avg_confidence"] = stats["avg_confidence"] / stats["count"]
            
        return list(category_stats.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auto-responses", response_model=List[AutoResponseResponse])
async def get_auto_responses(db: Session = Depends(get_db)):
    """Get all auto-response rules"""
    try:
        responses = db.query(AutoResponse).all()
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auto-responses", response_model=AutoResponseResponse)
async def create_auto_response(response: AutoResponseCreate, db: Session = Depends(get_db)):
    """Create a new auto-response rule"""
    try:
        db_response = AutoResponse(**response.dict())
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/auto-responses/{response_id}")
async def update_auto_response(
    response_id: int,
    response: AutoResponseCreate,
    db: Session = Depends(get_db)
):
    """Update an auto-response rule"""
    try:
        db_response = db.query(AutoResponse).filter(AutoResponse.id == response_id).first()
        if not db_response:
            raise HTTPException(status_code=404, detail="Auto-response not found")
            
        for key, value in response.dict().items():
            setattr(db_response, key, value)
            
        db.commit()
        return {"success": True, "message": "Auto-response updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/auto-responses/{response_id}")
async def delete_auto_response(response_id: int, db: Session = Depends(get_db)):
    """Delete an auto-response rule"""
    try:
        db_response = db.query(AutoResponse).filter(AutoResponse.id == response_id).first()
        if not db_response:
            raise HTTPException(status_code=404, detail="Auto-response not found")
            
        db.delete(db_response)
        db.commit()
        return {"success": True, "message": "Auto-response deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts", response_model=List[ContactResponse])
async def get_contacts(db: Session = Depends(get_db)):
    """Get all contacts with message counts"""
    try:
        # Get unique contacts from messages
        contacts = db.query(
            Message.phone_number,
            Message.contact_name
        ).distinct(Message.phone_number).all()
        
        result = []
        for contact in contacts:
            # Get message counts
            total_messages = db.query(Message).filter(Message.phone_number == contact.phone_number).count()
            incoming_count = db.query(Message).filter(
                Message.phone_number == contact.phone_number,
                Message.is_incoming == True
            ).count()
            outgoing_count = total_messages - incoming_count
            
            # Get last message
            last_message = db.query(Message).filter(
                Message.phone_number == contact.phone_number
            ).order_by(Message.timestamp.desc()).first()
            
            result.append({
                "phone_number": contact.phone_number,
                "contact_name": contact.contact_name or "Unknown",
                "total_messages": total_messages,
                "incoming_count": incoming_count,
                "outgoing_count": outgoing_count,
                "last_message_time": last_message.timestamp if last_message else None,
                "last_message_text": last_message.message_text if last_message else None
            })
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whatsapp/status")
async def get_whatsapp_status():
    """Get WhatsApp MCP connection status"""
    try:
        status = await whatsapp_client.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/connect")
async def connect_whatsapp():
    """Connect to WhatsApp MCP"""
    try:
        success = await whatsapp_client.connect()
        if success:
            return {"success": True, "message": "Connected to WhatsApp MCP"}
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to WhatsApp MCP")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/disconnect")
async def disconnect_whatsapp():
    """Disconnect from WhatsApp MCP"""
    try:
        await whatsapp_client.disconnect()
        return {"success": True, "message": "Disconnected from WhatsApp MCP"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)