# 🎥 Arlo Camera Management System

A comprehensive PC-based replacement for your Arlo VM4500 base station that provides live streaming, SMS motion alerts, and local video storage.

## Features

✨ **Live Streaming**
- Web-based dashboard to view live camera feeds
- Real-time status updates via WebSocket
- Multiple camera support

📱 **SMS Alerts**
- Twilio integration for instant motion notifications
- Customizable alert settings
- Test alert functionality

💾 **Local Storage**
- Download and store recordings on your PC
- Video library with timestamps
- Storage usage monitoring

🎛️ **Web Dashboard**
- Responsive design (works on desktop, tablet, mobile)
- Camera status monitoring
- Battery and signal strength indicators
- Real-time video library

## System Architecture

```
┌─────────────────────────────────────────┐
│        Arlo Cloud API                    │
│  (Videos, Camera Status, Commands)       │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
  ┌─────────────┐   ┌──────────────┐
  │  Arlo Cams  │   │  FastAPI     │
  │ (WiFi only) │───│  Backend     │
  └─────────────┘   │  (Port 8000) │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
       ┌─────────┐   ┌──────────┐  ┌───────────┐
       │ React   │   │ Twilio   │  │ Local     │
       │ Frontend│───│ SMS API  │  │ Storage   │
       │(3000)   │   │          │  │ (Videos)  │
       └─────────┘   └──────────┘  └───────────┘
```

## Requirements

- **Python 3.8+** - Backend server
- **Node.js 14+** - Frontend build
- **4GB RAM** (8GB recommended)
- **WiFi-connected Arlo cameras** (no base station needed)
- **Twilio account** (free $15 trial)
- **Stable internet connection**

## Quick Start

### 1️⃣ Clone/Download Repository

```bash
git clone https://github.com/yourusername/arlo-system.git
cd arlo-system
```

### 2️⃣ Run Setup Script

**On Windows:**
```cmd
setup.bat
```

**On macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3️⃣ Configure Credentials

Edit the `.env` file with:
- Your Arlo account email & password
- Twilio Account SID & Auth Token
- Twilio phone numbers (see [SETUP_GUIDE.md](SETUP_GUIDE.md))

### 4️⃣ Start the System

**Terminal 1 - Backend:**
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

python arlo_backend.py
```

**Terminal 2 - Frontend:**
```bash
npm start
```

### 5️⃣ Open Dashboard

Visit **http://localhost:3000** in your browser

## File Structure

```
arlo-system/
├── arlo_backend.py          # FastAPI backend server
├── App.jsx                  # React dashboard component
├── App.css                  # Dashboard styling
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies
├── .env.example             # Environment template (copy to .env)
├── SETUP_GUIDE.md           # Detailed setup instructions
├── setup.sh                 # Quick setup for macOS/Linux
├── setup.bat                # Quick setup for Windows
└── README.md                # This file
```

## Configuration

### Getting Credentials

**Arlo:**
1. Log in to https://my.arlo.com
2. Use your account email and password

**Twilio (Free):**
1. Sign up at https://www.twilio.com/try-twilio
2. Verify your phone number
3. Get Account SID & Auth Token from dashboard
4. Purchase/activate a Twilio phone number
5. Verify your alert phone number

→ **See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed steps**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | System and camera status |
| GET | `/api/cameras` | List all cameras |
| GET | `/api/cameras/{id}/stream` | Get live stream URL |
| GET | `/api/library` | Get recorded videos |
| GET | `/api/storage-info` | Storage usage |
| POST | `/api/test-alert` | Send test SMS |
| WS | `/ws/stream/{id}` | Real-time camera updates |

**Swagger UI:** http://localhost:8000/docs

## Dashboard Features

### Camera Management
- View all connected cameras
- Real-time status (online/offline)
- Battery level & signal strength
- One-click stream selection

### Live Streaming
- Start/stop live streams
- Full-screen viewing
- Responsive design for mobile

### Motion Alerts
- Enable/disable notifications
- Test alert functionality
- SMS sent to your phone

### Video Library
- Browse recorded videos
- Timestamps and duration
- Download capability

### Storage Management
- Monitor local storage usage
- File count tracking
- Auto-cleanup options (coming soon)

## Usage Examples

### View Live Stream
1. Select camera from sidebar
2. Click "▶ Start Stream"
3. View appears in main panel

### Get Motion Alerts
1. Select camera
2. Toggle "Enable Motion Alerts"
3. Receive SMS when motion detected

### Download Recording
1. Browse Video Library section
2. Click video to download
3. File saved to `./arlo_recordings`

## Troubleshooting

### "Authentication failed"
- Verify email and password in `.env`
- Check if 2FA is enabled (may need to disable)

### "No cameras found"
- Ensure cameras are WiFi connected
- Check cameras appear in Arlo app
- Wait 5 minutes for sync

### "SMS not received"
- Verify Twilio credentials
- Check phone number is verified in Twilio
- Ensure account has balance

### "Stream won't load"
- Verify camera is online
- Check WiFi signal strength
- Reload dashboard (F5)

→ **Full troubleshooting: [SETUP_GUIDE.md](SETUP_GUIDE.md)**

## Production Deployment

### Using Gunicorn (Backend)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 arlo_backend:app
```

### Using PM2 (Process Manager)
```bash
npm install -g pm2
pm2 start arlo_backend.py --name "arlo-api"
pm2 start npm --name "arlo-dashboard" -- start
pm2 startup
pm2 save
```

### Docker Deployment (Coming Soon)
See `Dockerfile` for containerization

## Security

⚠️ **Important:**
- Never commit `.env` to version control
- Don't share credentials
- Use strong Arlo password
- Enable 2FA on Arlo account when possible
- Run on trusted network
- Add HTTPS for remote access

## Advanced Configuration

### Custom Motion Sensitivity
Edit `arlo_backend.py`:
```python
MOTION_SENSITIVITY = "high"  # or "medium", "low"
```

### Recording Duration
```python
RECORDING_DURATION = 30  # seconds
```

### Alert Cooldown
```python
ALERT_COOLDOWN = 300  # seconds between alerts
```

## Limitations & Known Issues

- ⚠️ Arlo has API rate limits (approx. 100 calls/hour)
- Cameras require WiFi (no base station mesh)
- Recording requires manual download
- Some Arlo features may not be available via API

## Roadmap

- [ ] Continuous 24/7 recording
- [ ] ML-based motion detection (person/animal/vehicle)
- [ ] Cloud backup to AWS S3
- [ ] Telegram notifications
- [ ] Mobile app (React Native)
- [ ] Home automation integration (IFTTT)
- [ ] Docker support
- [ ] Database integration (recordings metadata)

## Contributing

Found a bug? Have suggestions? Open an issue or submit a PR!

## Support

- 📖 **Setup Help:** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🆘 **API Docs:** http://localhost:8000/docs
- 🔗 **Arlo API:** https://developer.arlo.com/
- 💬 **Twilio Docs:** https://www.twilio.com/docs/sms

## License

MIT License - Feel free to use and modify

## Disclaimer

This project is unofficial and not endorsed by Arlo/Netgear. Use at your own risk. Ensure you comply with Arlo's Terms of Service.

---

**Built with ❤️ | Made for Arlo users who want more control and something easier on the pocketbook**

### Quick Links
- [Setup Guide](SETUP_GUIDE.md) - Detailed instructions
- [API Documentation](http://localhost:8000/docs) - Swagger UI
- [Arlo Docs](https://us.arlo.com/pages/support-docs) - Official API reference
- [Twilio Docs](https://www.twilio.com/docs/sms) - SMS setup

**Status:** ✅ Ready to use | Last Updated: 2024
