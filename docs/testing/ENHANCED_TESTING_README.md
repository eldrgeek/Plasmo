# Enhanced Continuous Testing System

## Overview

The Enhanced Continuous Testing System provides comprehensive automated testing for the Plasmo Chrome extension with intelligent file watching, dual endpoint testing, and integrated WebRTC room state management tests.

## Features

### 🧪 Test Types
- **CDP Tests**: Chrome Debug Protocol tests for extension functionality
- **WebRTC Tests**: Socket.IO room state management and peer connection tests
- **Dual Endpoint Testing**: Local server + tunnel endpoint validation

### 🎯 Smart File Watching
- **Intelligent Triggers**: Only runs relevant tests based on file changes
- **Debounced Execution**: Prevents test spam during rapid file changes
- **Pattern-Based Mapping**: Files automatically mapped to appropriate test suites

### 📊 Real-time Monitoring
- **Web Dashboard**: Results displayed on http://localhost:3001
- **Health Endpoints**: Monitoring at http://localhost:8083/health
- **Structured Logging**: Detailed test execution logs

## Quick Start

### 1. Prerequisites
```bash
# Ensure virtual environment is active
source venv/bin/activate

# Install required dependencies
pip install python-socketio aiohttp websockets watchdog
```

### 2. Start Services
```bash
# Start Socket.IO server
python socketio_server_python.py

# Start Chrome with debug protocol
./launch-chrome-debug.sh
```

### 3. Run Enhanced Tests
```bash
# Option 1: Use convenience script
./run_enhanced_tests.sh

# Option 2: Run directly
python continuous_test_runner_enhanced.py
```

## File-to-Test Mapping

The system intelligently determines which tests to run based on file changes:

### WebRTC Tests Triggered By:
- `socketio_server_python.py` - Socket.IO server changes
- `socketio_server.js` - Node.js server changes  
- `service_manager.py` - Service management changes
- `webrtc_test_suite.py` - Test suite changes
- `test_room_client.py` - Test client changes
- `dashboard_perfect.py` - Dashboard changes
- `test_*.py` - Any test file changes

### Basic CDP Tests Triggered By:
- `popup.tsx` - Extension popup changes
- `background.ts` - Extension background script changes
- `options.tsx` - Extension options page changes
- `contents/` - Content script changes
- `mcp_server.py` - MCP server changes
- Any `.ts`, `.tsx`, `.js`, `.jsx`, `.html`, `.css` files

## WebRTC Test Suite

### Test Coverage
1. **Basic Connection** - Socket.IO connection establishment
2. **Room Join/Leave Cycle** - State management validation
3. **Multi-Client State Sync** - Peer list synchronization
4. **Heartbeat Functionality** - Connection keepalive
5. **Peer List Request** - Manual state queries
6. **Server Health Check** - Endpoint availability

### Dual Endpoint Testing
- **Local Server**: `http://localhost:3001`
- **Tunnel Server**: `https://monad-socketio.loca.lt`

### Example Output
```
🧪 Running WebRTC tests on http://localhost:3001
✅ Local tests: 6/6 passed
🧪 Running WebRTC tests on https://monad-socketio.loca.lt
❌ Tunnel tests: 0/1 passed (tunnel not available)
```

## Usage Examples

### Run Specific Test Types
```python
# Run only WebRTC tests
await test_runner.run_test_cycle("manual", {'webrtc'})

# Run only CDP tests  
await test_runner.run_test_cycle("manual", {'basic'})

# Run both (default)
await test_runner.run_test_cycle("manual", {'basic', 'webrtc'})
```

### File Change Triggers
```bash
# Editing Socket.IO server triggers WebRTC tests
vim socketio_server_python.py

# Editing popup triggers CDP tests
vim popup.tsx

# Editing test files triggers both
vim test_room_client.py
```

## Monitoring & Health Checks

### Health Endpoints
- **Enhanced Test Runner**: http://localhost:8083/health
- **Socket.IO Server**: http://localhost:3001/health
- **Chrome Debug Protocol**: http://localhost:9222/json

### Log Files
- **Test Execution**: `logs/continuous_testing.log`
- **Latest Results**: `logs/latest_test_results.json`

### Dashboard Integration
All test results are automatically sent to the web dashboard at http://localhost:3001 for real-time monitoring.

## Advanced Configuration

### Custom File Mappings
Edit `file_test_mappings` in `continuous_test_runner_enhanced.py`:

```python
self.file_test_mappings = {
    'my_custom_file.py': ['webrtc', 'basic'],
    'special_*.js': ['webrtc'],
    'components/': ['basic']
}
```

### Test Debouncing
Adjust timing in the constructor:

```python
self.test_debounce_seconds = 3  # Wait 3 seconds after file change
```

### Endpoint Configuration
Modify server URLs:

```python
self.socketio_server = "http://localhost:3001"
self.tunnel_server = "https://your-tunnel.loca.lt"
```

## Troubleshooting

### Common Issues

#### WebRTC Tests Failing
```bash
# Check Socket.IO server
curl http://localhost:3001/health

# Check tunnel connectivity  
curl https://monad-socketio.loca.lt/health
```

#### CDP Tests Failing
```bash
# Check Chrome debug protocol
curl http://localhost:9222/json

# Restart Chrome with debug flags
./launch-chrome-debug.sh
```

#### File Watching Not Working
```bash
# Check file permissions
ls -la continuous_test_runner_enhanced.py

# Verify watchdog installation
pip show watchdog
```

### Debug Mode
Enable debug logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing Tools

### Service Manager
The enhanced test runner integrates with the existing service manager and can be started as part of the development environment.

### Continuous Test Runner
This enhanced version extends the original `continuous_test_runner.py` with WebRTC capabilities while maintaining backward compatibility.

### Dashboard Integration
Test results automatically appear in the web dashboard alongside other system metrics and monitoring data.

## Best Practices

### Development Workflow
1. **Start Services**: Launch Socket.IO server and Chrome debug
2. **Run Enhanced Tests**: Use `./run_enhanced_tests.sh`
3. **Develop Iteratively**: Tests run automatically on file changes
4. **Monitor Dashboard**: Watch real-time results at http://localhost:3001

### Test Organization
- Keep WebRTC tests focused on Socket.IO functionality
- Use CDP tests for Chrome extension behavior
- Leverage dual endpoint testing for production validation

### Performance Optimization
- Tests are debounced to prevent excessive execution
- Smart file mapping reduces unnecessary test runs
- Parallel endpoint testing maximizes coverage efficiency

## Future Enhancements

- **Test Parallelization**: Run CDP and WebRTC tests simultaneously
- **Custom Test Suites**: User-defined test collections
- **Performance Benchmarking**: Automated performance regression detection
- **CI/CD Integration**: GitHub Actions workflow integration
- **Test Result History**: Long-term test performance tracking 