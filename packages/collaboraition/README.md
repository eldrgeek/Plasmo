# CollaborAItion Dashboard

Multi-Agent AI Collaboration Platform - Single-file FastHTML dashboard with auto-reload capabilities.

## Architecture

- **Single-file Design**: Dashboard server and UI combined in `dashboard.py`
- **FastHTML Framework**: Modern Python web framework for rapid development
- **File-based Storage**: JSON files for rapid prototyping and development
- **Auto-reload**: Automatic server restart on code/config changes
- **Responsive UI**: Tailwind CSS for mobile-friendly interface

## Quick Start

```bash
# From project root
npm run start-collaborAItion

# Or directly
cd packages/collaborAItion
./start.sh
```

## File Structure

```
packages/collaborAItion/
├── dashboard.py          # Main FastHTML server + UI
├── config.json          # Server and project configuration
├── requirements.txt     # Python dependencies
├── start.sh            # Startup script
├── data/               # JSON data storage
│   ├── tasks.json      # Task management data
│   ├── agents.json     # Agent status and info
│   └── messages.json   # Inter-agent messages (future)
└── README.md           # This file
```

## Features

### Dashboard Views
- **Overview**: Project stats, completion rates, quick actions
- **Agents**: Real-time agent status, current tasks, capabilities
- **Tasks**: Task management with priority, status, assignments

### Real-time Updates
- Auto-refresh every 30 seconds
- File watching for configuration changes
- Live status indicators

### API Endpoints
- `GET /api/tasks` - Retrieve all tasks
- `GET /api/agents` - Retrieve all agents  
- `GET /api/stats` - Project statistics

## Configuration

Edit `config.json` to customize:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true,
    "auto_reload": true
  },
  "project": {
    "name": "CollaborAItion 0.1",
    "description": "Multi-Agent AI Collaboration Platform"
  }
}
```

## Development

### Auto-reload
The server automatically restarts when:
- `dashboard.py` is modified
- `config.json` is updated
- Any JSON files in `data/` directory change

### Adding Features
1. Modify `dashboard.py` (single file contains all logic)
2. Update data models in JSON files
3. Add new API endpoints as needed
4. Server automatically reloads

## Team Integration

Built for the CollaborAItion team:
- **CC-Alex**: Technical Co-founder (Development)
- **CC-Gem**: Strategic Partner (UX/Strategy)  
- **River**: Team Coordinator (Task Management)

## Technical Stack

- **Python 3.8+**
- **FastHTML**: Web framework
- **Tailwind CSS**: Styling
- **Watchdog**: File monitoring
- **Uvicorn**: ASGI server

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Agent-to-agent messaging
- [ ] Task assignment workflow
- [ ] Analytics and reporting
- [ ] Authentication/permissions
- [ ] Database integration (SQLite/PostgreSQL)

---

**Built by CC-Alex** | CollaborAItion Team 2024