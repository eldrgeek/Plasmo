#!/usr/bin/env node

import { spawn } from 'child_process';
import { EventEmitter } from 'events';
import fs from 'fs/promises';
import path from 'path';

/**
 * Manages the lifecycle of the actual MCP server
 * Provides hot reload capabilities and health monitoring
 */
export class ServerManager extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.config = {
            serverScript: config.serverScript || '../mcp_server.py',
            serverArgs: config.serverArgs || ['--stdio'],
            restartDelay: config.restartDelay || 1000,
            healthCheckInterval: config.healthCheckInterval || 5000,
            maxRestarts: config.maxRestarts || 10,
            ...config
        };
        
        this.serverProcess = null;
        this.isStarting = false;
        this.isHealthy = false;
        this.restartCount = 0;
        this.lastRestart = 0;
        this.healthCheckTimer = null;
        this.pendingRequests = new Map();
        this.requestId = 0;
    }

    /**
     * Start the MCP server
     */
    async start() {
        if (this.isStarting || this.serverProcess) {
            throw new Error('Server is already starting or running');
        }

        console.log('🚀 Starting MCP server...');
        this.isStarting = true;
        
        try {
            await this._spawnServer();
            this._startHealthCheck();
            this.emit('started');
            console.log('✅ MCP server started successfully');
        } catch (error) {
            this.isStarting = false;
            console.error('❌ Failed to start MCP server:', error);
            throw error;
        }
    }

    /**
     * Stop the MCP server
     */
    async stop() {
        console.log('🛑 Stopping MCP server...');
        
        this._stopHealthCheck();
        
        if (this.serverProcess) {
            this.serverProcess.kill('SIGTERM');
            
            // Wait for graceful shutdown
            await new Promise((resolve) => {
                const timeout = setTimeout(() => {
                    if (this.serverProcess) {
                        this.serverProcess.kill('SIGKILL');
                    }
                    resolve();
                }, 5000);
                
                this.serverProcess.on('exit', () => {
                    clearTimeout(timeout);
                    resolve();
                });
            });
        }
        
        this.serverProcess = null;
        this.isHealthy = false;
        this.isStarting = false;
        this.emit('stopped');
        console.log('✅ MCP server stopped');
    }

    /**
     * Restart the MCP server
     */
    async restart() {
        console.log('🔄 Restarting MCP server...');
        
        const now = Date.now();
        if (now - this.lastRestart < this.config.restartDelay) {
            console.log('⏳ Restart too soon, waiting...');
            await new Promise(resolve => setTimeout(resolve, this.config.restartDelay));
        }
        
        if (this.restartCount >= this.config.maxRestarts) {
            throw new Error(`Maximum restart count (${this.config.maxRestarts}) exceeded`);
        }
        
        this.restartCount++;
        this.lastRestart = now;
        
        await this.stop();
        await this.start();
        
        this.emit('restarted');
        console.log('✅ MCP server restarted successfully');
    }

    /**
     * Send a request to the server
     */
    async sendRequest(request) {
        if (!this.isHealthy) {
            throw new Error('Server is not healthy');
        }

        return new Promise((resolve, reject) => {
            const id = ++this.requestId;
            const requestWithId = { ...request, id };
            
            this.pendingRequests.set(id, { resolve, reject, timestamp: Date.now() });
            
            // Set timeout for request
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error('Request timeout'));
                }
            }, 30000);
            
            this._writeToServer(JSON.stringify(requestWithId) + '\n');
        });
    }

    /**
     * Check if server is healthy
     */
    async isServerHealthy() {
        try {
            const response = await this.sendRequest({
                jsonrpc: '2.0',
                method: 'tools/list',
                params: {}
            });
            return response && !response.error;
        } catch (error) {
            return false;
        }
    }

    /**
     * Spawn the actual server process
     */
    async _spawnServer() {
        const serverPath = path.resolve(this.config.serverScript);
        
        // Check if server script exists
        try {
            await fs.access(serverPath);
        } catch (error) {
            throw new Error(`Server script not found: ${serverPath}`);
        }

        const args = [...this.config.serverArgs];
        console.log(`📄 Spawning: python3 ${serverPath} ${args.join(' ')}`);
        
        this.serverProcess = spawn('python3', [serverPath, ...args], {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env }
        });

        this.serverProcess.on('error', (error) => {
            console.error('❌ Server process error:', error);
            this.emit('error', error);
        });

        this.serverProcess.on('exit', (code, signal) => {
            console.log(`🔚 Server process exited with code ${code}, signal ${signal}`);
            this.serverProcess = null;
            this.isHealthy = false;
            this.isStarting = false;
            this.emit('exit', code, signal);
        });

        this.serverProcess.stdout.on('data', (data) => {
            this._handleServerOutput(data);
        });

        this.serverProcess.stderr.on('data', (data) => {
            console.error('📝 Server stderr:', data.toString());
        });

        // Wait for server to be ready
        await new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Server startup timeout'));
            }, 10000);

            const checkReady = async () => {
                try {
                    if (await this.isServerHealthy()) {
                        clearTimeout(timeout);
                        this.isHealthy = true;
                        this.isStarting = false;
                        resolve();
                    } else {
                        setTimeout(checkReady, 500);
                    }
                } catch (error) {
                    setTimeout(checkReady, 500);
                }
            };

            setTimeout(checkReady, 1000); // Give server time to start
        });
    }

    /**
     * Handle output from server
     */
    _handleServerOutput(data) {
        const lines = data.toString().split('\n').filter(line => line.trim());
        
        for (const line of lines) {
            try {
                const response = JSON.parse(line);
                
                if (response.id && this.pendingRequests.has(response.id)) {
                    const { resolve } = this.pendingRequests.get(response.id);
                    this.pendingRequests.delete(response.id);
                    resolve(response);
                } else {
                    // Unsolicited message or notification
                    this.emit('message', response);
                }
            } catch (error) {
                // Not JSON, probably log output
                console.log('📝 Server output:', line);
            }
        }
    }

    /**
     * Write data to server stdin
     */
    _writeToServer(data) {
        if (this.serverProcess && this.serverProcess.stdin.writable) {
            this.serverProcess.stdin.write(data);
        } else {
            throw new Error('Server stdin not writable');
        }
    }

    /**
     * Start health check monitoring
     */
    _startHealthCheck() {
        this.healthCheckTimer = setInterval(async () => {
            const healthy = await this.isServerHealthy();
            
            if (this.isHealthy && !healthy) {
                console.log('💔 Server health check failed, restarting...');
                this.isHealthy = false;
                this.emit('unhealthy');
                
                try {
                    await this.restart();
                } catch (error) {
                    console.error('❌ Failed to restart server:', error);
                    this.emit('error', error);
                }
            } else if (!this.isHealthy && healthy) {
                console.log('💚 Server health restored');
                this.isHealthy = true;
                this.emit('healthy');
            }
        }, this.config.healthCheckInterval);
    }

    /**
     * Stop health check monitoring
     */
    _stopHealthCheck() {
        if (this.healthCheckTimer) {
            clearInterval(this.healthCheckTimer);
            this.healthCheckTimer = null;
        }
    }
}

export default ServerManager;
