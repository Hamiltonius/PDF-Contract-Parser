# LifeOS v1.0 - Personal AI Operating System

LifeOS is your personal AI-powered operating system that helps manage your digital life. It integrates with your calendar, email, and documents to provide intelligent task management, scheduling, and planning powered by Claude AI.

## Features

### 🤖 AI Agent System
- **Task Manager**: Intelligent task creation, prioritization, and scheduling
- **Calendar Agent**: Calendar sync, free time finder, meeting scheduler
- **Email Agent**: Email processing, task extraction, auto-summarization
- **Planner Agent**: Daily/weekly planning, schedule optimization

### 📄 Document Processing
- PDF parsing and text extraction
- Automatic task extraction from documents
- Metadata extraction

### 📅 Calendar Integration
- Google Calendar synchronization
- Find free time slots
- Meeting time suggestions
- Event conflict detection

### 📧 Email Management
- IMAP email synchronization
- AI-powered email summarization
- Automatic task extraction from emails
- Draft email replies

### 📊 Dashboard
- Today's overview
- Upcoming tasks and deadlines
- Calendar events
- Email summary

## Tech Stack

- **Backend**: FastAPI + Python 3.9+
- **AI**: Anthropic Claude API
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Integrations**: Google Calendar API, IMAP email

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

### Basic Installation

```bash
# Clone repository
git clone https://github.com/yourusername/lifeos-v1.git
cd lifeos-v1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and credentials

# Run the application
python main.py
```

Access the web interface at `http://localhost:8000`

## Configuration

### Required API Keys

1. **Anthropic API Key** (for Claude AI)
   - Get from: https://console.anthropic.com/
   - Set in `.env`: `ANTHROPIC_API_KEY=your_key`

2. **Google Calendar API** (optional)
   - Enable Google Calendar API in Google Cloud Console
   - Download `credentials.json`
   - First run will prompt for OAuth authentication

3. **Email IMAP** (optional)
   - Gmail users: Enable "Less secure app access" or use App Password
   - Set credentials in `.env`

## Usage

### API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Web Interface

Navigate through tabs:
- **Dashboard**: Overview of tasks, calendar, and emails
- **Tasks**: Create and manage tasks with AI prioritization
- **Calendar**: Sync and view calendar events
- **Email**: Sync emails and extract tasks
- **Planner**: Generate AI-powered daily/weekly plans
- **Documents**: Upload and process PDF documents

## Project Structure

```
lifeos-v1/
├── agents/              # AI agent modules
│   ├── base_agent.py
│   ├── task_manager.py
│   ├── calendar_agent.py
│   ├── email_agent.py
│   └── planner_agent.py
├── api/                 # FastAPI application
│   ├── server.py
│   └── routes.py
├── database/            # Database models and setup
│   ├── models.py
│   └── init_db.py
├── ingestion/           # Data ingestion modules
│   ├── pdf_parser.py
│   ├── calendar_sync.py
│   └── email_sync.py
├── frontend/            # Web interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── main.py              # Application entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Development

### Running in Development Mode

```bash
# Enable debug mode and auto-reload
export DEBUG=True
export API_RELOAD=True
python main.py
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

## Roadmap

### v1.1 (Upcoming)
- [ ] Task dependencies and subtasks
- [ ] Natural language task creation
- [ ] Voice input support
- [ ] Mobile-responsive UI improvements

### v2.0 (Future)
- [ ] Multi-user support
- [ ] Team collaboration features
- [ ] Advanced analytics and insights
- [ ] Integration with more services (Slack, Notion, etc.)

## Troubleshooting

### Common Issues

**Issue**: "No module named 'anthropic'"
- **Solution**: Activate virtual environment and run `pip install -r requirements.txt`

**Issue**: Calendar sync fails
- **Solution**: Ensure `credentials.json` is in the project root and run authentication flow

**Issue**: Database errors
- **Solution**: Delete `lifeos.db` and restart the application to recreate database

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/lifeos-v1/issues
- Documentation: See [SETUP.md](SETUP.md)

## Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Google Calendar API](https://developers.google.com/calendar)

---

**LifeOS v1.0** - Your Personal AI Operating System
