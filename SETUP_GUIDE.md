# Arlo Camera Management System - Complete Setup Guide

## Overview
This system replaces your VM4500 base station with a PC-based solution that provides:
- Web dashboard for camera management
- Live video streaming
- SMS motion alerts via Twilio
- Local recording storage
- Real-time camera monitoring

---

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 50GB+ for recordings
- **Internet**: Stable connection with sufficient bandwidth
- **Python**: 3.8 or higher
- **Node.js**: 14.0 or higher (for frontend)

### Network Requirements
- PC must be on same network as Arlo cameras
- Port 8000 (backend API) must be accessible
- Port 3000 (frontend dev server) for development

---

## Step 1: Arlo API Setup

### 1.1 Get Arlo Credentials

1. Go to https://my.arlo.com and log in with your Arlo account
2. Navigate to **Settings → Account Settings**
3. Note your email and password (you'll need these)

### 1.2 Set Up Arlo API Access

For now, the system uses basic Arlo API authentication. Future versions can use OAuth.

**Important**: Arlo has rate limits on API calls. The system is configured to respect these limits.

---

## Step 2: Twilio Setup (SMS Alerts)

### 2.1 Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account (includes $15 trial credit)
3. Verify your phone number

### 2.2 Get Your Twilio Credentials

1. Go to **Dashboard** (https://console.twilio.com)
2. Note these values:
   - **Account SID**: Starts with `AC`
   - **Auth Token**: Long alphanumeric string
3. Copy these somewhere safe

### 2.3 Get a Twilio Phone Number

1. In Twilio Console, click **# Develop → Phone Numbers**
2. Click **Get your first Twilio phone number** (or purchase one)
3. Copy the phone number (format: +1XXXXXXXXXX)

### 2.4 Verify Alert Phone Number

1. In Twilio Console, go **Develop → Verified Caller IDs**
2. Click **Add a New Phone Number**
3. Enter your personal phone number (where you want alerts sent)
4. Follow verification steps (you'll get a code via text)

---

## Step 3: System Installation

### 3.1 Clone/Download Files

Create a project folder:
```bash
mkdir arlo-system
cd arlo-system
```

Copy these files to the folder:
- `arlo_backend.py` (backend server)
- `App.jsx` (React component)
- `App.css` (styling)

### 3.2 Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn aiohttp twilio python-dotenv pydantic
```

### 3.3 Install Node.js Dependencies

```bash
# Initialize npm project (if not already done)
npm init -y

# Install React and dependencies
npm install react react-dom react-scripts
npm install --save-dev @types/react @types/react-dom

# Or use Create React App
npx create-react-app frontend
cd frontend
# Copy App.jsx and App.css to frontend/src/
```

---

## Step 4: Configuration

### 4.1 Create `.env` File

Create a file named `.env` in your project root:

```env
# Arlo Credentials
ARLO_EMAIL=your-arlo-email@example.com
ARLO_PASSWORD=your-arlo-password

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=yyyyyyyyyyyyyyyyyyyyyyyyyyyyy
TWILIO_PHONE_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+1987654321

# Storage Path
ARLO_STORAGE_PATH=./arlo_recordings

# API Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
```

### 4.2 Explanation of Variables

| Variable | Example | Notes |
|----------|---------|-------|
| `ARLO_EMAIL` | `user@example.com` | Your Arlo account email |
| `ARLO_PASSWORD` | `MySecurePassword123` | Your Arlo password (store securely!) |
| `TWILIO_ACCOUNT_SID` | `AC1234567890abcd...` | From Twilio dashboard |
| `TWILIO_AUTH_TOKEN` | `your-auth-token-here` | From Twilio dashboard |
| `TWILIO_PHONE_NUMBER` | `+14155552671` | Your Twilio phone number |
| `ALERT_PHONE_NUMBER` | `+14155555555` | Phone to receive alerts |
| `ARLO_STORAGE_PATH` | `./arlo_recordings` | Where to save videos |

### 4.3 Secure Storage

**⚠️ IMPORTANT**: Never commit `.env` to git!

Create `.gitignore`:
```
.env
.env.local
venv/
node_modules/
__pycache__/
.DS_Store
*.pyc
```

---

## Step 5: Running the System

### 5.1 Start the Backend

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run the backend server
python arlo_backend.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 5.2 Start the Frontend (Development)

Open a new terminal:
```bash
cd frontend
npm start
```

This opens http://localhost:3000 in your browser.

### 5.3 Build for Production

When ready to deploy:

```bash
# Create production build
npm run build

# Serve with a production server
npm install -g serve
serve -s build -l 3000
```

---

## Step 6: Disconnect Cameras from VM4500

### 6.1 Factory Reset Cameras

For each camera:
1. Unplug the camera from power for 30 seconds
2. Plug back in
3. Wait for LED to stabilize (usually blinking blue)

### 6.2 Reconnect to PC

1. Open the official Arlo app on your phone/tablet
2. Go to **Settings → Add New Device**
3. Select your camera model
4. Connect to your home WiFi
5. The camera will now be independent from the base station

**Note**: Cameras will need stable WiFi signal. Ensure adequate coverage.

---

## Step 7: Testing

### 7.1 Test Dashboard Access

1. Open http://localhost:3000 in your browser
2. You should see:
   - ✅ List of your cameras
   - ✅ Current camera status
   - ✅ Storage information
   - ✅ Video library (if any recordings exist)

### 7.2 Test Live Stream

1. Click on a camera from the list
2. Click "▶ Start Stream" button
3. Live video should appear (if camera is online)

### 7.3 Test SMS Alerts

1. Click on a camera
2. Click "📱 Send Test Alert" button
3. You should receive an SMS within 30 seconds

**Troubleshooting**:
- Check Twilio credentials in `.env`
- Verify alert phone number is verified in Twilio
- Check Twilio account has sufficient balance

---

## Step 8: Configure Motion Detection

The current system detects motion through Arlo's cloud API. To enable alerts:

### 8.1 Through Web Dashboard

1. Select a camera
2. Toggle "Enable Motion Alerts"
3. Alerts will be sent when motion is detected

### 8.2 Advanced Configuration (Optional)

Edit `arlo_backend.py` to customize:

```python
# Motion sensitivity (in settings)
MOTION_SENSITIVITY = "high"  # or "medium", "low"

# Alert delay (wait before sending another alert)
ALERT_COOLDOWN = 300  # seconds

# Recording settings
AUTO_RECORD = True
RECORDING_DURATION = 30  # seconds
```

---

## Step 9: Automating Startup

### Windows: Create Startup Batch File

Create `start_arlo.bat`:
```batch
@echo off
cd /d "C:\path\to\arlo-system"
venv\Scripts\activate
python arlo_backend.py
```

Add to Task Scheduler to run on startup.

### macOS: Create LaunchAgent

Create `~/Library/LaunchAgents/com.arlo.system.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.arlo.system</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/arlo_backend.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Linux: Create SystemD Service

Create `/etc/systemd/system/arlo.service`:
```ini
[Unit]
Description=Arlo Camera System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/arlo-system
ExecStart=/path/to/arlo-system/venv/bin/python arlo_backend.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable arlo
sudo systemctl start arlo
```

---

## Troubleshooting

### Issue: "Authentication failed"

**Solution**:
- Verify ARLO_EMAIL and ARLO_PASSWORD in `.env`
- Try logging into arlo.com manually to ensure credentials work
- Check if two-factor authentication is enabled (disable for API)

### Issue: "No cameras found"

**Solution**:
- Ensure cameras are added to your Arlo account
- Verify cameras are online in the official Arlo app
- Wait 5 minutes for system to refresh
- Check API rate limits haven't been exceeded

### Issue: "SMS not received"

**Solution**:
- Verify Twilio credentials are correct
- Ensure alert phone number is verified
- Check Twilio account has balance remaining
- Try "Send Test Alert" button
- Check phone logs for blocked messages

### Issue: "Stream won't load"

**Solution**:
- Ensure camera is online and connected to WiFi
- Check camera signal strength (📶 indicator)
- Reload dashboard with F5
- Restart the camera (unplug 30 sec)

### Issue: Backend crashes

**Solution**:
- Check Python version: `python --version` (should be 3.8+)
- Verify all dependencies installed: `pip list`
- Check `.env` file for syntax errors
- Run with: `python -u arlo_backend.py` for unbuffered output

---

## API Documentation

### Endpoints

#### Get System Status
```
GET /api/status
```
Returns cameras and system info.

#### Get All Cameras
```
GET /api/cameras
```
Returns list of all cameras with status.

#### Get Live Stream URL
```
GET /api/cameras/{camera_id}/stream
```
Returns RTSP/HLS stream URL for camera.

#### Get Video Library
```
GET /api/library?limit=50
```
Returns recent recordings.

#### Get Storage Info
```
GET /api/storage-info
```
Returns storage usage and file count.

#### Send Test Alert
```
POST /api/test-alert?camera_name=Test%20Camera
```
Sends SMS test message.

---

## Security Best Practices

1. **Never share `.env` file** - contains sensitive credentials
2. **Use strong Arlo password** - or use app-specific passwords if available
3. **Keep credentials in environment variables** - never hardcode
4. **Run on trusted network** - PC should be behind firewall
5. **Use HTTPS in production** - add SSL certificate
6. **Limit API access** - implement authentication if exposed to internet
7. **Rotate Twilio credentials** - periodically regenerate auth tokens

---

## Next Steps

1. ✅ Complete setup above
2. ✅ Test all components
3. ✅ Set up automated startup
4. ✅ Monitor system for 24-48 hours
5. ✅ Adjust alert sensitivity as needed

---

## Support & Advanced Topics

### Want to add more features?

Possible enhancements:
- Cloud backup to AWS S3
- Video analytics (detect people vs animals)
- Telegram notifications
- Home automation integration (IFTTT)
- Mobile app (React Native)
- ML-based motion detection
- 24/7 continuous recording

### Need help?

- Check logs: System logs appear in backend console
- Test API directly: http://localhost:8000/docs (Swagger UI)
- Review Arlo API docs: https://arlo.readme.io/
- Twilio docs: https://www.twilio.com/docs/sms

---

**Good luck! Your PC-based Arlo system is ready.** 🎥🚀
