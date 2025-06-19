# Plasmo Monorepo Structure

This repository has been refactored into a monorepo structure for better organization and development workflow.

## Structure

```
plasmo/
├── packages/
│   ├── chrome-extension/     # Plasmo Chrome extension
│   ├── mcp-server/          # Model Context Protocol server
│   ├── socketio-server/     # Socket.IO communication server
│   ├── dashboard-framework/ # Shared dashboard components
│   └── firebase-chat/       # Firebase chat application
├── shared/
│   ├── src/                 # Shared source code
│   ├── types/               # Shared TypeScript types
│   └── python-common/       # Shared Python utilities
├── docs/                    # Documentation
├── scripts/                 # Build and deployment scripts
├── package.json             # Root workspace configuration
├── pnpm-workspace.yaml      # PNPM workspace config
└── pyproject.toml           # Python workspace config
```

## Development Setup

### Prerequisites
- Node.js >= 18.0.0
- Python >= 3.8
- pnpm >= 8.0.0

### Installation

1. **Install Node.js dependencies:**
   ```bash
   pnpm install
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -e ./packages/mcp-server
   pip install -e ./packages/dashboard-framework
   ```

3. **Install browser for automation:**
   ```bash
   pnpm install-browser
   ```

## Available Commands

### Chrome Extension
```bash
pnpm dev                    # Start extension in development mode
pnpm build                  # Build extension for production
pnpm package                # Package extension for distribution
```

### Services
```bash
pnpm start-mcp             # Start MCP server
pnpm start-socketio        # Start Socket.IO server
pnpm start-dashboard       # Start dashboard server
pnpm start-all             # Start all services
```

### Firebase
```bash
pnpm firebase-automate     # Run Firebase console automation
pnpm firebase-example      # Run Firebase automation example
```

## Package Dependencies

### Chrome Extension (`packages/chrome-extension/`)
- **Tech Stack:** TypeScript, React, Plasmo
- **Dependencies:** React, Socket.IO client, Chrome APIs
- **Build Output:** `build/` directory

### MCP Server (`packages/mcp-server/`)
- **Tech Stack:** Python, FastMCP, AsyncIO
- **Dependencies:** FastMCP, WebSockets, Chrome Debug Protocol
- **Features:** AI assistant tools, Chrome debugging

### Socket.IO Server (`packages/socketio-server/`)
- **Tech Stack:** Python/Node.js, Socket.IO
- **Dependencies:** Socket.IO, FastAPI/Express
- **Features:** Real-time communication hub

### Dashboard Framework (`packages/dashboard-framework/`)
- **Tech Stack:** Python, FastHTML
- **Dependencies:** FastHTML, FastAPI, WebSockets
- **Features:** Reusable dashboard components for all services

### Firebase Chat (`packages/firebase-chat/`)
- **Tech Stack:** React, Firebase, TypeScript
- **Dependencies:** Firebase SDK, React
- **Features:** Real-time chat application

## Shared Code

### `shared/src/`
- Firebase service configurations
- Common TypeScript interfaces

### `shared/python-common/`
- Base service classes
- Common utilities and helpers

### `shared/types/`
- Shared TypeScript type definitions

## Development Workflow

1. **Single Package Development:**
   ```bash
   cd packages/chrome-extension
   pnpm dev
   ```

2. **Cross-Package Changes:**
   ```bash
   # Make changes to multiple packages
   git add .
   git commit -m "Update across packages"
   ```

3. **Adding Dependencies:**
   ```bash
   # Add to specific package
   pnpm --filter chrome-extension add package-name
   
   # Add to root workspace
   pnpm add -D package-name
   ```

## Migration Notes

- All services remain functionally independent
- Shared code is now centralized in `shared/`
- Package imports may need updating after migration
- Service discovery and communication patterns remain unchanged

## Benefits of This Structure

1. **Better Organization:** Clear separation of concerns
2. **Shared Code:** Centralized common utilities and types
3. **Unified Development:** Single repository for related services
4. **Easier Testing:** Test services working together
5. **Consistent Tooling:** Shared linting, formatting, and build tools