"""
Arlo Camera Management System - Backend Server
Handles API integration, SMS alerts, video streaming, and local storage
"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import aiohttp
import base64

# Third-party imports
from twilio.rest import Client
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Configuration ====================
class Config:
    """Load configuration from environment variables"""
    
    # Arlo API credentials
    ARLO_EMAIL = os.getenv("ARLO_EMAIL", "")
    ARLO_PASSWORD = os.getenv("ARLO_PASSWORD", "")
    
    # Twilio credentials
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")  # Your Twilio number
    ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE_NUMBER", "")   # Where to send alerts
    
    # Local storage
    STORAGE_PATH = Path(os.getenv("ARLO_STORAGE_PATH", "./arlo_recordings"))
    STORAGE_PATH.mkdir(exist_ok=True)
    
    # API endpoints
    ARLO_API_BASE = "https://my.arlo.com/api"
    ARLO_WS_BASE = "wss://myservices.arlo.com"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        if not cls.ARLO_EMAIL:
            missing.append("ARLO_EMAIL")
        if not cls.ARLO_PASSWORD:
            missing.append("ARLO_PASSWORD")
        if not cls.TWILIO_ACCOUNT_SID:
            missing.append("TWILIO_ACCOUNT_SID")
        if not cls.TWILIO_AUTH_TOKEN:
            missing.append("TWILIO_AUTH_TOKEN")
        if not cls.TWILIO_PHONE_NUMBER:
            missing.append("TWILIO_PHONE_NUMBER")
        if not cls.ALERT_PHONE_NUMBER:
            missing.append("ALERT_PHONE_NUMBER")
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

# ==================== Pydantic Models ====================
class CameraInfo(BaseModel):
    id: str
    name: str
    model: str
    status: str
    battery_level: Optional[int]
    signal_strength: Optional[int]

class SystemStatus(BaseModel):
    cameras: List[CameraInfo]
    base_station_id: str
    recording_enabled: bool
    storage_location: str

class MotionAlert(BaseModel):
    camera_id: str
    camera_name: str
    timestamp: datetime
    thumbnail_url: Optional[str]

# ==================== Arlo API Handler ====================
class ArloAPIHandler:
    """Handle all Arlo API interactions"""
    
    def __init__(self):
        self.base_url = Config.ARLO_API_BASE
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.device_id = None
        self.cameras = {}
        
    async def initialize(self):
        """Initialize session and authenticate"""
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        
    async def authenticate(self):
        """Authenticate with Arlo servers"""
        try:
            async with self.session.post(
                f"{self.base_url}/v2/homes/users/login",
                json={
                    "email": Config.ARLO_EMAIL,
                    "password": Config.ARLO_PASSWORD
                }
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Authentication failed: {resp.status}")
                
                data = await resp.json()
                auth_data = data.get('data', {})
                
                self.auth_token = auth_data.get('token')
                self.user_id = auth_data.get('userId')
                self.device_id = auth_data.get('deviceId', 'web')
                
                logger.info("Successfully authenticated with Arlo")
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    async def get_devices(self):
        """Fetch all devices and cameras"""
        try:
            headers = self._get_headers()
            
            async with self.session.get(
                f"{self.base_url}/v2/users/{self.user_id}/devices",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get devices: {resp.status}")
                
                data = await resp.json()
                devices = data.get('data', {})
                
                # Parse cameras
                for device in devices:
                    if device.get('deviceType') in ['arloq', 'arloq2', 'arlo2', 'arlo3', 'arlopro', 'arlopro2', 'arlopro3']:
                        self.cameras[device['deviceId']] = {
                            'id': device['deviceId'],
                            'name': device.get('deviceName', 'Unknown'),
                            'model': device.get('deviceType'),
                            'status': device.get('state', 'unknown'),
                            'battery_level': device.get('batteryLevel'),
                            'signal_strength': device.get('signalStrength'),
                            'base_station_id': device.get('parentId')
                        }
                
                logger.info(f"Found {len(self.cameras)} cameras")
                return self.cameras
                
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            raise
    
    async def get_library(self, limit: int = 50):
        """Fetch recorded videos from library"""
        try:
            headers = self._get_headers()
            
            async with self.session.get(
                f"{self.base_url}/v2/users/{self.user_id}/library",
                headers=headers,
                params={'limit': limit}
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get library: {resp.status}")
                
                data = await resp.json()
                return data.get('data', [])
                
        except Exception as e:
            logger.error(f"Error getting library: {e}")
            raise
    
    async def get_stream_url(self, device_id: str) -> Optional[str]:
        """Get live stream URL for a camera"""
        try:
            headers = self._get_headers()
            
            async with self.session.post(
                f"{self.base_url}/v2/users/{self.user_id}/devices/{device_id}/command",
                headers=headers,
                json={'command': 'startStream'}
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to start stream: {resp.status}")
                    return None
                
                data = await resp.json()
                stream_data = data.get('data', {})
                return stream_data.get('url')
                
        except Exception as e:
            logger.error(f"Error getting stream URL: {e}")
            return None
    
    async def download_video(self, media_id: str, filename: str) -> Optional[str]:
        """Download video from library and save locally"""
        try:
            headers = self._get_headers()
            storage_file = Config.STORAGE_PATH / filename
            
            async with self.session.get(
                f"{self.base_url}/v2/users/{self.user_id}/media/{media_id}/download",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to download video: {resp.status}")
                    return None
                
                with open(storage_file, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)
                
                logger.info(f"Downloaded video to {storage_file}")
                return str(storage_file)
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def _get_headers(self) -> dict:
        """Get headers with authentication"""
        return {
            'Authorization': self.auth_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

# ==================== SMS Alert Handler ====================
class SMSAlertHandler:
    """Handle SMS notifications via Twilio"""
    
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    
    async def send_motion_alert(self, camera_name: str, timestamp: datetime):
        """Send SMS alert for motion detection"""
        try:
            message = self.client.messages.create(
                body=f"🚨 Motion detected on {camera_name} at {timestamp.strftime('%H:%M:%S')}",
                from_=Config.TWILIO_PHONE_NUMBER,
                to=Config.ALERT_PHONE_NUMBER
            )
            logger.info(f"SMS sent: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

# ==================== FastAPI Application ====================
app = FastAPI(title="Arlo Camera Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global handlers
arlo_handler = None
sms_handler = None

# ==================== API Endpoints ====================

@app.on_event("startup")
async def startup():
    """Initialize handlers on startup"""
    global arlo_handler, sms_handler
    
    try:
        Config.validate()
        arlo_handler = ArloAPIHandler()
        sms_handler = SMSAlertHandler()
        await arlo_handler.initialize()
        await arlo_handler.get_devices()
        logger.info("System initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if arlo_handler:
        await arlo_handler.close()

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get system and cameras status"""
    try:
        cameras = []
        for cam_id, cam_info in arlo_handler.cameras.items():
            cameras.append(CameraInfo(**cam_info))
        
        return SystemStatus(
            cameras=cameras,
            base_station_id="PC-Based",
            recording_enabled=True,
            storage_location=str(Config.STORAGE_PATH)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cameras")
async def get_cameras():
    """Get list of all cameras"""
    try:
        return list(arlo_handler.cameras.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cameras/{camera_id}/stream")
async def get_stream(camera_id: str):
    """Get live stream URL for camera"""
    try:
        if camera_id not in arlo_handler.cameras:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        stream_url = await arlo_handler.get_stream_url(camera_id)
        if not stream_url:
            raise HTTPException(status_code=503, detail="Could not get stream URL")
        
        return {"stream_url": stream_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/library")
async def get_library(limit: int = 50):
    """Get recorded videos from library"""
    try:
        videos = await arlo_handler.get_library(limit)
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-alert")
async def test_alert(camera_name: str = "Test Camera"):
    """Send a test SMS alert"""
    try:
        success = await sms_handler.send_motion_alert(camera_name, datetime.now())
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/storage-info")
async def get_storage_info():
    """Get local storage information"""
    try:
        files = list(Config.STORAGE_PATH.glob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            "path": str(Config.STORAGE_PATH),
            "total_files": len(files),
            "total_size_gb": round(total_size / (1024**3), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/stream/{camera_id}")
async def websocket_stream(websocket: WebSocket, camera_id: str):
    """WebSocket endpoint for streaming camera data"""
    await websocket.accept()
    
    try:
        if camera_id not in arlo_handler.cameras:
            await websocket.send_json({"error": "Camera not found"})
            await websocket.close()
            return
        
        # Send initial camera info
        camera_info = arlo_handler.cameras[camera_id]
        await websocket.send_json({
            "type": "camera_info",
            "data": camera_info
        })
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(5)
            camera_info = arlo_handler.cameras[camera_id]
            await websocket.send_json({
                "type": "status_update",
                "timestamp": datetime.now().isoformat(),
                "data": camera_info
            })
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
