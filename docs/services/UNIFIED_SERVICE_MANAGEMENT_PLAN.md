# 🚀 Unified Service Management System Plan

## 📋 Context Instructions to Keep in Mind
- **Services are already running and auto-restart** when their files change
- **Chrome Debug Protocol** requires integer request IDs (not strings)
- **Virtual environment** is automatically managed via `.venv` and autoenv system
- **MCP server** enables real-time debugging through AI assistance
- **Plasmo extension** has background, popup, content scripts, and options pages
- **Service manager** already exists but needs enhancement for unified dashboard system
- **Tunneling** is handled as a service 
- **Testing** is handled as a service 

## 🎯 Project Goals
Create a unified service orchestration system where:
- ✅ One script starts everything
- ✅ Each service has its own monitoring dashboard
- ✅ Auto-reload works for all services
- ✅ Testing runs automatically on changes to any service
- ✅ Chrome and PNPM are managed as special cases
- ✅ Real-time visibility into all running services 
- ✅ Tunneling is handled as a service 
- ✅ Native event injection and detection is handled as a service 

## 🚀 **DASHBOARD SYSTEM NOW LIVE!**
**✅ Master Control Dashboard**: `http://localhost:8000/master`
**✅ Socket.IO Dashboard**: `http://localhost:8000/socketio`
**✅ MCP Server Dashboard**: `http://localhost:8000/mcp`
**✅ Plasmo Dev Dashboard**: `http://localhost:8000/plasmo`
**✅ API Endpoint**: `http://localhost:8000/api/services`

Start with: `python launch_dashboard.py` 



---

## 📊 Dashboard Design Specifications
Question: should each dashboard be a separate service, or should it be a 
single service that aggregates all the dashboards?

Dashboards should space efficient and use a soft color scheme. 


### 1. **Master Control Dashboard** (`http://localhost:8000`)
- **Service Status Grid**: Real-time status of all services (running/stopped/error)
- **Resource Monitoring**: CPU, Memory, Port usage per service
- **Logs Aggregation**: Live log streaming from all services
- **Quick Actions**: Start/Stop/Restart buttons for each service
- **Health Checks**: Automatic ping tests for HTTP services
- **Auto-refresh**: 2-second intervals with WebSocket updates

### 2. **Socket.IO Dashboard** (`http://localhost:3001/dashboard`)
- **Connection Status**: Active WebSocket connections
- **Message Flow**: Real-time message traffic visualization
- **Room Management**: Active rooms and participant counts
- **Performance Metrics**: Message throughput, latency stats
- **Connection History**: Join/leave events timeline

### 3. **MCP Server Dashboard** (`http://localhost:8001/dashboard`)
- **Tool Usage**: MCP tool invocation statistics
- **Chrome Debug Status**: CDP connection health
- **Request/Response Flow**: Real-time MCP command tracking
- **Error Monitoring**: Failed requests and stack traces
- **Performance**: Response times and concurrent connections

### 4. **Plasmo Dev Dashboard** (`http://localhost:1012/dashboard`) 
- **Build Status**: Compilation success/errors
- **Hot Reload**: File change detection and reload status
- **Extension Status**: Chrome extension load status
- **Bundle Analysis**: File sizes and dependency tree
- **Development Metrics**: Build times, file watch count

### 5. **Testing Dashboard** (`http://localhost:8082/dashboard`)
- **Test Results**: Pass/fail status with detailed reports
- **Coverage Reports**: Code coverage visualization
- **Parser Testing**: Individual parser test results
- **Test History**: Timeline of test runs and results
- **Performance**: Test execution times and trends

### 6. **Chrome Debug Dashboard** (`http://localhost:9222/dashboard`)
- **Tab Management**: Active tabs with screenshots
- **Console Monitoring**: Live console output from all tabs
- **Network Activity**: Request/response monitoring
- **Extension Debugging**: Extension-specific debugging info
- **CDP Command History**: Debug protocol command log

---

## 🛠 Implementation Plan

### Phase 1: Infrastructure Setup
- [x] **1.1** Create unified service launcher script (`launch_all.py`)
- [x] **1.2** Implement service health monitoring system
- [ ] **1.3** Create socket.io-based real-time communication hub
- [x] **1.4** Set up centralized logging aggregation
- [x] **1.5** Create master configuration system for all services

### Phase 2: Dashboard Framework
- [x] **2.1** Create FastHTML-based dashboard framework template
- [x] **2.2** Implement real-time WebSocket updates for all dashboards
- [x] **2.3** Create shared UI components (status indicators, log viewers, etc.)
- [x] **2.4** Implement responsive design for mobile/desktop viewing
- [x] **2.5** Add dark/light theme support across all dashboards

### Phase 3: Individual Service Dashboards
- [x] **3.1** Enhance existing MCP Dashboard with new specifications
- [x] **3.2** Create Socket.IO service dashboard
- [x] **3.3** Create Plasmo Dev service dashboard  
- [ ] **3.4** Create Testing service dashboard
- [ ] **3.5** Create Tunneling service dashboard
- [ ] **3.6** Create Chrome Debug service dashboard
- [x] **3.7** Create Master Control dashboard

### Phase 4: Chrome Instance Management
- [ ] **4.1** Implement Chrome instance detection system
- [ ] **4.2** Create Chrome auto-start logic (start if none running)
- [ ] **4.3** Add Chrome health monitoring and auto-restart
- [ ] **4.4** Implement Chrome Debug Protocol connection management
- [ ] **4.5** Add Chrome extension auto-reload integration

### Phase 5: PNPM Dev Management
- [ ] **5.1** Implement directory-based PNPM dev detection
- [ ] **5.2** Create per-directory PNPM dev instance management
- [ ] **5.3** Add PNPM dev health monitoring
- [ ] **5.4** Implement hot-reload integration with dashboards
- [ ] **5.5** Add build status reporting to dashboards

### Phase 6: Testing Integration
- [ ] **6.1** Implement file change detection for parsers
- [ ] **6.2** Create individual parser test runner
- [ ] **6.3** Add test result aggregation and reporting
- [ ] **6.4** Implement test coverage tracking
- [ ] **6.5** Create test failure notification system

### Phase 7: Auto-Reload Enhancement
- [ ] **7.1** Enhance existing auto-reload for Python services
- [ ] **7.2** Add dependency tracking for intelligent restarts
- [ ] **7.3** Implement graceful shutdown/startup sequences
- [ ] **7.4** Add rollback capability for failed deployments
- [ ] **7.5** Create service dependency graph management

### Phase 8: Unified Service Script
- [ ] **8.1** Create `start_all.py` master script
- [ ] **8.2** Implement service startup order management
- [ ] **8.3** Add health check verification before marking services ready
- [ ] **8.4** Create unified configuration management
- [ ] **8.5** Add command-line interface for service management

### Phase 9: Monitoring & Alerting
- [ ] **9.1** Implement resource usage monitoring (CPU, Memory, Disk)
- [ ] **9.2** Create service health scoring system
- [ ] **9.3** Add alerting for service failures
- [ ] **9.4** Implement performance trending and analytics
- [ ] **9.5** Create automated performance optimization

### Phase 10: Integration & Testing
- [ ] **10.1** Test unified startup script with all services
- [ ] **10.2** Verify dashboard functionality across all services
- [ ] **10.3** Test auto-reload functionality end-to-end
- [ ] **10.4** Validate Chrome and PNPM management
- [ ] **10.5** Performance test with all services running

### Phase 11: Documentation & Cleanup
- [ ] **11.1** Create comprehensive documentation for the system
- [ ] **11.2** Add inline code documentation
- [ ] **11.3** Create troubleshooting guide
- [ ] **11.4** Clean up deprecated scripts and files
- [ ] **11.5** Create service management best practices guide

---

## 🔧 Technical Architecture

### Core Components:
1. **Service Orchestrator**: Central service management with dependency resolution
2. **Dashboard Hub**: FastHTML-based real-time monitoring interface
3. **WebSocket Bridge**: Real-time communication between services and dashboards
4. **Health Monitor**: Continuous service health checking and auto-recovery
5. **Configuration Manager**: Centralized config management for all services

### Service Communication:
- **HTTP APIs**: RESTful endpoints for service control
- **WebSockets**: Real-time updates and log streaming
- **Redis**: Message queuing and caching (if needed)
- **File Watching**: Intelligent file change detection

### Monitoring Stack:
- **Metrics Collection**: Service performance and health data
- **Log Aggregation**: Centralized logging with real-time streaming
- **Alert System**: Proactive failure detection and notification
- **Analytics**: Historical performance and usage tracking

---

## 🎯 Success Criteria
- [ ] Single command starts all services reliably
- [ ] All services have functional real-time dashboards
- [ ] Auto-reload works without manual intervention
- [ ] Chrome instances are properly managed
- [ ] PNPM dev instances work per-directory
- [ ] Testing runs automatically on parser changes
- [ ] System is resilient to individual service failures
- [ ] Performance overhead is minimal (<5% impact)

---

**Ready to proceed with implementation? Please review and let me know if you'd like any adjustments to the plan!** 