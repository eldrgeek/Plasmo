const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Serve static files for a simple web interface
app.use(express.static(path.join(__dirname, 'public')));

// Store connected extensions and AI completion signals
const connectedExtensions = new Map();
const completionSignals = new Map();  // Track AI completion signals

io.on('connection', (socket) => {
  console.log('🔌 Client connected:', socket.id);

  // Handle extension registration
  socket.on('extension_register', (data) => {
    console.log('📱 Extension registered:', data);
    connectedExtensions.set(socket.id, {
      extensionId: data.extensionId,
      timestamp: data.timestamp,
      socket: socket
    });
    
    socket.emit('registration_confirmed', {
      message: 'Extension successfully registered',
      serverId: socket.id
    });
  });

  // Handle command results from extension
  socket.on('command_result', (result) => {
    console.log('📊 Command result:', result);
  });

  // Handle tab updates from extension
  socket.on('tab_updated', (tabInfo) => {
    console.log('🌐 Tab updated:', tabInfo);
  });

  socket.on('disconnect', () => {
    console.log('❌ Client disconnected:', socket.id);
    connectedExtensions.delete(socket.id);
  });
});

// API endpoints for sending commands to extensions
app.use(express.json());

// Send command to all connected extensions
app.post('/api/command/broadcast', (req, res) => {
  const { action, payload } = req.body;
  
  if (!action) {
    return res.status(400).json({ error: 'Action is required' });
  }

  const command = {
    action,
    payload,
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `Command sent to ${sent} extension(s)`,
    command
  });
});

// Send command to specific extension
app.post('/api/command/send/:socketId', (req, res) => {
  const { socketId } = req.params;
  const { action, payload } = req.body;

  if (!action) {
    return res.status(400).json({ error: 'Action is required' });
  }

  const extension = connectedExtensions.get(socketId);
  if (!extension) {
    return res.status(404).json({ error: 'Extension not found' });
  }

  const command = {
    action,
    payload,
    timestamp: Date.now()
  };

  extension.socket.emit('cursor_command', command);

  res.json({
    success: true,
    message: 'Command sent to extension',
    command,
    extensionId: extension.extensionId
  });
});

// Get list of connected extensions
app.get('/api/extensions', (req, res) => {
  const extensions = Array.from(connectedExtensions.values()).map(ext => ({
    socketId: ext.socket.id,
    extensionId: ext.extensionId,
    timestamp: ext.timestamp,
    connected: ext.socket.connected
  }));

  res.json({
    success: true,
    extensions,
    count: extensions.length
  });
});

// Convenience endpoints for common commands
app.post('/api/cursor/reconnect-mcp', (req, res) => {
  const command = {
    action: 'reconnect_mcp',
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `MCP reconnect command sent to ${sent} extension(s)`
  });
});

app.post('/api/cursor/open-file', (req, res) => {
  const { filePath } = req.body;
  
  if (!filePath) {
    return res.status(400).json({ error: 'filePath is required' });
  }

  const command = {
    action: 'open_file',
    payload: { filePath },
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `Open file command sent to ${sent} extension(s)`,
    filePath
  });
});

app.post('/api/cursor/run-command', (req, res) => {
  const { command: cursorCommand } = req.body;
  
  if (!cursorCommand) {
    return res.status(400).json({ error: 'command is required' });
  }

  const command = {
    action: 'run_command',
    payload: { command: cursorCommand },
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `Run command sent to ${sent} extension(s)`,
    command: cursorCommand
  });
});

// AI Completion Signal endpoint
app.post('/api/ai-completion', (req, res) => {
  const { completion_id, status, timestamp, summary } = req.body;
  
  if (!completion_id) {
    return res.status(400).json({ error: 'completion_id is required' });
  }

  const completionData = {
    completion_id,
    status: status || 'completed',
    timestamp: timestamp || new Date().toISOString(),
    summary: summary || null,
    received_at: Date.now()
  };

  // Store completion signal
  completionSignals.set(completion_id, completionData);

  // Emit to all connected clients
  io.emit('ai_completion', completionData);

  console.log(`🤖 AI Completion received: ${completion_id} - ${status}`);

  res.json({
    success: true,
    message: 'Completion signal received',
    completion_id
  });
});

// Get completion status
app.get('/api/ai-completion/:completion_id', (req, res) => {
  const { completion_id } = req.params;
  
  const completion = completionSignals.get(completion_id);
  if (!completion) {
    return res.status(404).json({ 
      success: false, 
      error: 'Completion not found',
      completion_id 
    });
  }

  res.json({
    success: true,
    completion: completion
  });
});

// List all completions
app.get('/api/ai-completions', (req, res) => {
  const completions = Array.from(completionSignals.values()).sort(
    (a, b) => b.received_at - a.received_at
  );

  res.json({
    success: true,
    completions,
    count: completions.length
  });
});

// Test Results endpoints for continuous testing
const testResults = new Map();  // Store test results

app.post('/api/test-results', (req, res) => {
  try {
    const testResult = req.body;
    const resultId = `test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Store test result
    testResults.set(resultId, {
      ...testResult,
      result_id: resultId,
      received_at: Date.now()
    });
    
    // Emit to all connected clients for real-time updates
    io.emit('test-results', {
      ...testResult,
      result_id: resultId
    });
    
    console.log('🧪 Test results received:', {
      success: testResult.success,
      passed: testResult.passed || 0,
      total: testResult.total || 0,
      trigger: testResult.trigger || 'unknown',
      timestamp: testResult.timestamp
    });
    
    res.json({ 
      success: true, 
      message: 'Test results received and broadcasted',
      result_id: resultId
    });
  } catch (error) {
    console.error('❌ Error handling test results:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Get latest test results
app.get('/api/test-results/latest', (req, res) => {
  const results = Array.from(testResults.values()).sort(
    (a, b) => b.received_at - a.received_at
  );
  
  const latest = results[0] || null;
  
  res.json({
    success: true,
    latest_result: latest,
    total_count: results.length
  });
});

// Get all test results with pagination
app.get('/api/test-results', (req, res) => {
  const limit = parseInt(req.query.limit) || 20;
  const offset = parseInt(req.query.offset) || 0;
  
  const results = Array.from(testResults.values()).sort(
    (a, b) => b.received_at - a.received_at
  );
  
  const paginatedResults = results.slice(offset, offset + limit);
  
  res.json({
    success: true,
    results: paginatedResults,
    total_count: results.length,
    limit,
    offset
  });
});

// Trigger manual test run
app.post('/api/trigger-tests', (req, res) => {
  try {
    const triggerData = {
      timestamp: new Date().toISOString(),
      trigger: 'manual_web_interface',
      requested_by: req.ip || 'unknown'
    };
    
    console.log('🧪 Manual test trigger requested');
    
    // Emit test trigger event to test runner
    io.emit('trigger-tests', triggerData);
    
    res.json({ 
      success: true, 
      message: 'Test trigger sent',
      trigger_data: triggerData
    });
  } catch (error) {
    console.error('❌ Error triggering tests:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// AI Chat Injection endpoint with completion detection
app.post('/api/cursor/inject-ai-prompt', (req, res) => {
  const { 
    prompt, 
    mode = 'chat', 
    delay = 0.5, 
    assume_focused = false, 
    skip_toggle = false,
    completion_detection = null
  } = req.body;
  
  if (!prompt) {
    return res.status(400).json({ error: 'prompt is required' });
  }

  // Build arguments for the Python AI injector
  const args = [path.join(__dirname, 'cursor_ai_injector.py')];
  
  // Create a temporary JSON config for complex parameters
  const config = {
    prompt,
    mode,
    delay,
    assume_focused,
    skip_toggle,
    completion_detection
  };
  
  // For complex calls, we'll use JSON mode
  if (mode !== 'chat' || delay !== 0.5 || assume_focused || skip_toggle || completion_detection) {
    args.push('--json');
    args.push(JSON.stringify(config));
  } else {
    // Simple mode for backwards compatibility
    args.push(prompt);
  }

  // Execute the Python AI injector
  const pythonProcess = spawn('python3', args);

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      try {
        // Try to parse the output as JSON result
        const lines = output.trim().split('\n');
        const lastLine = lines[lines.length - 1];
        
        if (lastLine.startsWith('Injection result:')) {
          const resultStr = lastLine.replace('Injection result: ', '');
          const result = JSON.parse(resultStr);
          
          res.json({
            success: result.success,
            message: result.success ? 'AI prompt injected successfully' : result.error,
            details: result,
            prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
            mode: mode
          });
        } else {
          res.json({
            success: true,
            message: 'AI prompt injection completed',
            output: output.trim(),
            prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
            mode: mode
          });
        }
      } catch (e) {
        res.json({
          success: true,
          message: 'AI prompt injection completed (parse warning)',
          output: output.trim(),
          prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
          mode: mode,
          parseError: e.message
        });
      }
    } else {
      res.status(500).json({
        success: false,
        error: 'AI injection failed',
        details: error.trim(),
        exitCode: code
      });
    }
  });

  pythonProcess.on('error', (err) => {
    res.status(500).json({
      success: false,
      error: 'Failed to execute AI injector',
      details: err.message
    });
  });
});

// Simple web interface
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cursor IDE Controller</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            button { background: #007cba; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            button:hover { background: #005a8b; }
            input[type="text"] { width: 300px; padding: 8px; margin: 5px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            #extensions { font-family: monospace; background: #f8f9fa; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>🎯 Cursor IDE Controller</h1>
        
        <div class="container">
            <h3>📱 Connected Extensions</h3>
            <button onclick="refreshExtensions()">🔄 Refresh</button>
            <div id="extensions">Loading...</div>
        </div>

        <div class="container">
            <h3>🔧 Quick Commands</h3>
            <button onclick="sendCommand('reconnect_mcp')">🔄 Reconnect MCP Server</button>
            <button onclick="sendCommand('restart_extension')">♻️ Restart Extension</button>
        </div>

        <div class="container">
            <h3>📁 Open File</h3>
            <input type="text" id="filePath" placeholder="/path/to/file.txt" />
            <button onclick="openFile()">📂 Open in Cursor</button>
        </div>

        <div class="container">
            <h3>⚡ Run Command</h3>
            <input type="text" id="cursorCommand" placeholder="cursor --version" />
            <button onclick="runCommand()">▶️ Execute</button>
        </div>

        <div class="container">
            <h3>🤖 AI Chat Injection</h3>
            <textarea id="aiPrompt" placeholder="Enter your AI prompt here..." style="width: 100%; height: 100px; padding: 8px; margin: 5px 0;"></textarea>
            <div style="margin: 10px 0;">
                <label>Mode: </label>
                <select id="aiMode" style="padding: 8px; margin: 5px;">
                    <option value="chat">💬 Chat</option>
                    <option value="composer">🎵 Composer</option>
                    <option value="inline_edit">✏️ Inline Edit</option>
                </select>
            </div>
            <div style="margin: 10px 0;">
                <label>
                    <input type="checkbox" id="assumeFocused" style="margin-right: 5px;">
                    🎯 Assume chat is already open/focused (recommended)
                </label>
            </div>
            <div style="margin: 10px 0;">
                <label>
                    <input type="checkbox" id="skipToggle" style="margin-right: 5px;">
                    ⏭️ Skip panel toggle (never send Cmd+L)
                </label>
            </div>
            <div style="margin: 10px 0;">
                <label>
                    <input type="checkbox" id="enableCompletion" style="margin-right: 5px;">
                    🔔 Enable completion detection
                </label>
            </div>
            <div id="completionOptions" style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px; display: none;">
                <div style="margin: 5px 0;">
                    <label>Detection Method:</label>
                    <select id="completionMethod" style="padding: 4px; margin-left: 5px;">
                        <option value="file">📁 File-based</option>
                        <option value="http">🌐 HTTP endpoint</option>
                        <option value="both">🔄 Both methods</option>
                    </select>
                </div>
                <div style="margin: 5px 0;">
                    <label>
                        <input type="checkbox" id="includeResults" style="margin-right: 5px;">
                        📊 Include AI response summary
                    </label>
                </div>
            </div>
            <div>
                <button onclick="injectAIPrompt()">🚀 Inject Prompt</button>
                <button onclick="injectAIPromptSafe()" style="background: #28a745;">🔒 Safe Inject (Assume Open)</button>
                <button onclick="injectWithCompletion()" style="background: #17a2b8;">🔔 Inject + Monitor</button>
            </div>
            <div style="font-size: 12px; color: #666; margin-top: 10px;">
                💡 <strong>Safe Inject</strong> won't toggle the chat panel - use when chat is already open<br/>
                🔔 <strong>Inject + Monitor</strong> will wait for AI completion signal<br/>
                ⚠️ Make sure Cursor is running and visible before injecting prompts
            </div>
        </div>

        <div id="status"></div>

        <script>
            async function refreshExtensions() {
                try {
                    const response = await fetch('/api/extensions');
                    const data = await response.json();
                    
                    document.getElementById('extensions').innerHTML = 
                        \`Connected Extensions: \${data.count}\n\` + 
                        JSON.stringify(data.extensions, null, 2);
                } catch (error) {
                    showStatus('Error refreshing extensions: ' + error.message, 'error');
                }
            }

            async function sendCommand(action) {
                try {
                    const response = await fetch('/api/command/broadcast', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action })
                    });
                    
                    const data = await response.json();
                    showStatus(data.message, 'success');
                } catch (error) {
                    showStatus('Error: ' + error.message, 'error');
                }
            }

            async function openFile() {
                const filePath = document.getElementById('filePath').value;
                if (!filePath) {
                    showStatus('Please enter a file path', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/cursor/open-file', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filePath })
                    });
                    
                    const data = await response.json();
                    showStatus(data.message, 'success');
                } catch (error) {
                    showStatus('Error: ' + error.message, 'error');
                }
            }

            async function runCommand() {
                const command = document.getElementById('cursorCommand').value;
                if (!command) {
                    showStatus('Please enter a command', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/cursor/run-command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command })
                    });
                    
                    const data = await response.json();
                    showStatus(data.message, 'success');
                } catch (error) {
                    showStatus('Error: ' + error.message, 'error');
                }
            }

            async function injectAIPrompt() {
                const prompt = document.getElementById('aiPrompt').value;
                const mode = document.getElementById('aiMode').value;
                const assumeFocused = document.getElementById('assumeFocused').checked;
                const skipToggle = document.getElementById('skipToggle').checked;
                
                if (!prompt.trim()) {
                    showStatus('Please enter an AI prompt', 'error');
                    return;
                }

                showStatus('🤖 Injecting AI prompt...', 'success');

                try {
                    const response = await fetch('/api/cursor/inject-ai-prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            prompt, 
                            mode,
                            assume_focused: assumeFocused,
                            skip_toggle: skipToggle
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showStatus(\`✅ \${data.message}\`, 'success');
                        // Clear the prompt after successful injection
                        document.getElementById('aiPrompt').value = '';
                    } else {
                        showStatus(\`❌ \${data.error || data.message}\`, 'error');
                    }
                } catch (error) {
                    showStatus('❌ Error: ' + error.message, 'error');
                }
            }

            async function injectAIPromptSafe() {
                const prompt = document.getElementById('aiPrompt').value;
                const mode = document.getElementById('aiMode').value;
                
                if (!prompt.trim()) {
                    showStatus('Please enter an AI prompt', 'error');
                    return;
                }

                showStatus('🔒 Safe injecting AI prompt (assuming chat is open)...', 'success');

                try {
                    const response = await fetch('/api/cursor/inject-ai-prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            prompt, 
                            mode,
                            assume_focused: true  // Always assume focused for safe inject
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showStatus(\`✅ Safe inject: \${data.message}\`, 'success');
                        // Clear the prompt after successful injection
                        document.getElementById('aiPrompt').value = '';
                    } else {
                        showStatus(\`❌ \${data.error || data.message}\`, 'error');
                    }
                } catch (error) {
                    showStatus('❌ Error: ' + error.message, 'error');
                }
            }

            async function injectWithCompletion() {
                const prompt = document.getElementById('aiPrompt').value;
                const mode = document.getElementById('aiMode').value;
                const enableCompletion = document.getElementById('enableCompletion').checked;
                
                if (!prompt.trim()) {
                    showStatus('Please enter an AI prompt', 'error');
                    return;
                }

                if (!enableCompletion) {
                    showStatus('Please enable completion detection first', 'error');
                    return;
                }

                const completionMethod = document.getElementById('completionMethod').value;
                const includeResults = document.getElementById('includeResults').checked;
                const completionId = 'completion_' + Date.now();

                const completionConfig = {
                    enabled: true,
                    methods: [completionMethod],
                    completion_id: completionId,
                    include_results: includeResults,
                    auto_append: true,
                    file_path: '/tmp/cursor_ai_completion_' + completionId + '.json',
                    http_endpoint: 'http://localhost:3001/api/ai-completion'
                };

                showStatus('🚀 Injecting prompt with completion detection...', 'success');

                try {
                    const response = await fetch('/api/cursor/inject-ai-prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            prompt, 
                            mode,
                            assume_focused: true,  // Always assume focused for monitored injection
                            completion_detection: completionConfig
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showStatus(\`✅ Prompt injected! Monitoring for completion (ID: \${completionId})...\`, 'success');
                        document.getElementById('aiPrompt').value = '';
                        
                        // Start monitoring for completion
                        monitorCompletion(completionId, 300); // 5 minute timeout
                    } else {
                        showStatus(\`❌ \${data.error || data.message}\`, 'error');
                    }
                } catch (error) {
                    showStatus('❌ Error: ' + error.message, 'error');
                }
            }

            async function monitorCompletion(completionId, timeoutSeconds) {
                const startTime = Date.now();
                const timeout = timeoutSeconds * 1000;
                
                const checkCompletion = async () => {
                    try {
                        const response = await fetch(\`/api/ai-completion/\${completionId}\`);
                        const data = await response.json();
                        
                        if (data.success) {
                            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                            let message = \`🎉 AI completed in \${elapsed}s!\`;
                            
                            if (data.completion.summary) {
                                message += \` Summary: \${data.completion.summary}\`;
                            }
                            
                            showStatus(message, 'success');
                            return true; // Completed
                        }
                    } catch (error) {
                        // Not found yet, continue monitoring
                    }
                    
                    if (Date.now() - startTime > timeout) {
                        showStatus(\`⏰ Completion monitoring timeout (\${timeoutSeconds}s)\`, 'error');
                        return true; // Stop monitoring
                    }
                    
                    return false; // Continue monitoring
                };
                
                // Check every 2 seconds
                const monitorInterval = setInterval(async () => {
                    const completed = await checkCompletion();
                    if (completed) {
                        clearInterval(monitorInterval);
                    }
                }, 2000);
                
                // Initial check
                await checkCompletion();
            }

            function showStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = \`<div class="status \${type}">\${message}</div>\`;
                setTimeout(() => statusDiv.innerHTML = '', 10000); // Longer timeout for completion messages
            }

            // Toggle completion options visibility
            document.addEventListener('DOMContentLoaded', function() {
                const enableCheckbox = document.getElementById('enableCompletion');
                const optionsDiv = document.getElementById('completionOptions');
                
                if (enableCheckbox && optionsDiv) {
                    enableCheckbox.addEventListener('change', function() {
                        optionsDiv.style.display = this.checked ? 'block' : 'none';
                    });
                }
            });

            // Auto-refresh extensions every 5 seconds
            setInterval(refreshExtensions, 5000);
            refreshExtensions();
        </script>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🚀 SocketIO server running on http://localhost:${PORT}`);
  console.log(`📱 Extension commands can be sent via the web interface`);
  console.log(`🔌 Extensions should connect to: ws://localhost:${PORT}`);
  console.log(`🔄 Auto-restart enabled via nodemon`);
});

module.exports = { app, server, io }; 