# LifeOS Setup Guide

Complete setup instructions for getting LifeOS running on your system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Keys Setup](#api-keys-setup)
5. [Google Calendar Setup](#google-calendar-setup)
6. [Email Setup](#email-setup)
7. [Running LifeOS](#running-lifeos)
8. [Raspberry Pi 5 Setup](#raspberry-pi-5-setup)

## System Requirements

### Minimum Requirements
- Python 3.9 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection

### Recommended
- Python 3.11+
- 8GB RAM
- SSD storage
- Raspberry Pi 5 (8GB) for dedicated deployment

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/lifeos-v1.git
cd lifeos-v1
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import fastapi, anthropic, sqlalchemy; print('All packages installed successfully')"
```

## Configuration

### 1. Create Environment File

```bash
cp .env.example .env
```

### 2. Edit Configuration

Open `.env` in your text editor and configure the following:

```bash
# Required: Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional: Email Configuration
EMAIL_SERVER=imap.gmail.com
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Optional: Google Calendar
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## API Keys Setup

### Anthropic Claude API (Required)

1. **Sign up** at https://console.anthropic.com/
2. **Navigate to** API Keys section
3. **Create new API key**
4. **Copy key** and add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
5. **Add credits** to your account (pay-as-you-go)

**Pricing (as of 2024):**
- Claude 3.5 Sonnet: ~$3 per million input tokens
- Typical usage: $5-20/month for personal use

### Alternative: OpenAI API (Optional)

If you prefer OpenAI instead of Claude:

1. Get API key from https://platform.openai.com/
2. Update `.env`:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-xxxxxxxxxxxxx
   ```

## Google Calendar Setup

### 1. Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Calendar API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Application type: **Desktop app**
6. Download the credentials JSON file

### 2. Configure Credentials

```bash
# Move downloaded file to project directory
mv ~/Downloads/client_secret_*.json credentials.json
```

### 3. First Authentication

On first run, LifeOS will:
1. Open browser for Google OAuth
2. Ask for calendar access permission
3. Save token to `token.json`

The token will auto-refresh, no need to re-authenticate.

## Email Setup

### Gmail Setup

1. **Enable IMAP** in Gmail settings
2. **Create App Password**:
   - Go to Google Account → Security
   - Enable 2-Factor Authentication
   - Generate App Password for "Mail"
3. **Configure `.env`**:
   ```
   EMAIL_SERVER=imap.gmail.com
   EMAIL_PORT=993
   EMAIL_USERNAME=your.email@gmail.com
   EMAIL_PASSWORD=your-16-char-app-password
   EMAIL_USE_SSL=True
   ```

### Other Email Providers

**Outlook/Office 365:**
```
EMAIL_SERVER=outlook.office365.com
EMAIL_PORT=993
```

**iCloud:**
```
EMAIL_SERVER=imap.mail.me.com
EMAIL_PORT=993
```

**Custom IMAP:**
- Check your email provider's IMAP settings
- Update server and port accordingly

## Running LifeOS

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with auto-reload
export DEBUG=True
export API_RELOAD=True
python main.py
```

Access at: `http://localhost:8000`

### Production Mode

```bash
# Run normally
python main.py
```

### Running in Background

**Linux/macOS (using screen):**
```bash
screen -S lifeos
source venv/bin/activate
python main.py
# Press Ctrl+A, then D to detach
# Reattach with: screen -r lifeos
```

**Using systemd service:**

Create `/etc/systemd/system/lifeos.service`:
```ini
[Unit]
Description=LifeOS Personal AI
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/lifeos-v1
Environment="PATH=/path/to/lifeos-v1/venv/bin"
ExecStart=/path/to/lifeos-v1/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lifeos
sudo systemctl start lifeos
```

## Raspberry Pi 5 Setup

### Recommended Pi 5 Configuration
- **Model**: Raspberry Pi 5 (8GB RAM recommended)
- **Storage**: 64GB+ microSD or NVMe SSD
- **OS**: Raspberry Pi OS (64-bit)
- **Power**: Official Pi 5 power supply

### Installation Steps

1. **Install Raspberry Pi OS**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python 3.11**
   ```bash
   sudo apt install python3.11 python3.11-venv python3-pip -y
   ```

3. **Clone and Setup LifeOS**
   ```bash
   cd ~
   git clone https://github.com/yourusername/lifeos-v1.git
   cd lifeos-v1
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure for Pi**
   ```bash
   # Edit .env
   nano .env

   # Set to bind to all interfaces
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

5. **Setup Auto-Start**
   ```bash
   # Add to ~/.bashrc or create systemd service (see above)
   ```

6. **Access from Network**
   - Find Pi IP: `hostname -I`
   - Access from browser: `http://192.168.x.x:8000`

### Performance Tips for Pi 5
- Use NVMe SSD instead of microSD for better performance
- Allocate more GPU memory if needed: `sudo raspi-config`
- Consider enabling zram: `sudo apt install zram-tools`

## Verification

### Test the Installation

1. **Check API health**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Access web interface**:
   Open `http://localhost:8000` in browser

3. **Test API endpoints**:
   Visit `http://localhost:8000/docs` for interactive API docs

## Troubleshooting

### Issue: Port 8000 Already in Use

```bash
# Find process using port
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Change port in .env
API_PORT=8001
```

### Issue: SQLite Database Locked

```bash
# Delete and recreate database
rm lifeos.db
python main.py
```

### Issue: Google Calendar Auth Fails

```bash
# Delete existing token and re-authenticate
rm token.json
python main.py
```

### Issue: Import Errors

```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Next Steps

After setup:
1. **Create your first task** via the web interface
2. **Sync your calendar** to see upcoming events
3. **Generate a daily plan** using the AI planner
4. **Upload a PDF** to test document processing

## Need Help?

- Check GitHub Issues
- Review logs in `logs/` directory
- Enable debug mode for detailed error messages

---

**Setup Complete!** You're ready to use LifeOS 🚀
