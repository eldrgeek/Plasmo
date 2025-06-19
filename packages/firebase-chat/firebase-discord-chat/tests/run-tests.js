#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const config = {
  firebase: {
    emulatorPort: 8080,
    authPort: 9099,
    storagePort: 9199
  },
  timeouts: {
    emulatorStart: 30000,
    testRun: 300000 // 5 minutes
  }
};

class DatabaseTestRunner {
  constructor() {
    this.processes = [];
    this.cleanup = this.cleanup.bind(this);
    
    // Handle cleanup on exit
    process.on('SIGINT', this.cleanup);
    process.on('SIGTERM', this.cleanup);
    process.on('exit', this.cleanup);
  }

  async run(testType = 'all') {
    console.log('🚀 Starting Roundtable Database Test Suite');
    console.log(`📋 Test Type: ${testType}`);
    
    try {
      // Step 1: Start Firebase emulators
      await this.startFirebaseEmulators();
      
      // Step 2: Run database tests
      const results = await this.runTests(testType);
      
      // Step 3: Generate report
      await this.generateReport(results);
      
      console.log('✅ Database test suite completed successfully');
      process.exit(0);
      
    } catch (error) {
      console.error('❌ Database test suite failed:', error.message);
      process.exit(1);
    }
  }

  async startFirebaseEmulators() {
    console.log('🔥 Starting Firebase emulators...');
    
    // Check if already running
    try {
      const response = await fetch(`http://localhost:${config.firebase.emulatorPort}`);
      console.log('✅ Firebase emulators already running');
      return;
    } catch (error) {
      // Emulators not running, start them
    }
    
    const emulatorProcess = spawn('firebase', [
      'emulators:start',
      '--only', 'firestore,auth,storage',
      '--project', 'roundtable-test'
    ], {
      stdio: 'pipe',
      cwd: process.cwd()
    });
    
    this.processes.push(emulatorProcess);
    
    return new Promise((resolve, reject) => {
      let output = '';
      const timeout = setTimeout(() => {
        reject(new Error('Firebase emulators failed to start within timeout'));
      }, config.timeouts.emulatorStart);
      
      emulatorProcess.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        
        if (text.includes('All emulators ready')) {
          clearTimeout(timeout);
          console.log('✅ Firebase emulators started');
          resolve();
        }
      });
      
      emulatorProcess.stderr.on('data', (data) => {
        console.error('Emulator error:', data.toString());
      });
      
      emulatorProcess.on('error', (error) => {
        clearTimeout(timeout);
        reject(error);
      });
    });
  }

  async runTests(testType) {
    const results = {};
    
    switch (testType) {
      case 'unit':
        results.unit = await this.runUnitTests();
        break;
      case 'integration':
        results.integration = await this.runIntegrationTests();
        break;
      case 'all':
      default:
        results.unit = await this.runUnitTests();
        results.integration = await this.runIntegrationTests();
        break;
    }
    
    return results;
  }

  async runUnitTests() {
    console.log('🧪 Running database unit tests...');
    
    return new Promise((resolve, reject) => {
      const testProcess = spawn('npm', ['run', 'test:unit'], {
        stdio: 'pipe',
        cwd: process.cwd()
      });
      
      let output = '';
      let errorOutput = '';
      
      testProcess.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        console.log(text);
      });
      
      testProcess.stderr.on('data', (data) => {
        const text = data.toString();
        errorOutput += text;
        console.error(text);
      });
      
      testProcess.on('close', (code) => {
        const result = {
          success: code === 0,
          output,
          errorOutput,
          exitCode: code
        };
        
        if (code === 0) {
          console.log('✅ Database unit tests passed');
        } else {
          console.log('❌ Database unit tests failed');
        }
        
        resolve(result);
      });
      
      testProcess.on('error', (error) => {
        reject(error);
      });
    });
  }

  async runIntegrationTests() {
    console.log('🔗 Running database integration tests...');
    
    return new Promise((resolve, reject) => {
      const testProcess = spawn('npm', ['run', 'test:integration'], {
        stdio: 'pipe',
        cwd: process.cwd()
      });
      
      let output = '';
      let errorOutput = '';
      
      testProcess.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        console.log(text);
      });
      
      testProcess.stderr.on('data', (data) => {
        const text = data.toString();
        errorOutput += text;
        console.error(text);
      });
      
      testProcess.on('close', (code) => {
        const result = {
          success: code === 0,
          output,
          errorOutput,
          exitCode: code
        };
        
        if (code === 0) {
          console.log('✅ Database integration tests passed');
        } else {
          console.log('❌ Database integration tests failed');
        }
        
        resolve(result);
      });
      
      testProcess.on('error', (error) => {
        reject(error);
      });
    });
  }

  async generateReport(results) {
    console.log('📊 Generating database test report...');
    
    const report = {
      timestamp: new Date().toISOString(),
      testType: 'database',
      summary: {
        total: Object.keys(results).length,
        passed: Object.values(results).filter(r => r.success).length,
        failed: Object.values(results).filter(r => !r.success).length
      },
      results
    };
    
    // Write report to file
    const reportPath = path.join(__dirname, 'database-test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Print summary
    console.log('\n📋 Database Test Summary:');
    console.log(`   Total: ${report.summary.total}`);
    console.log(`   Passed: ${report.summary.passed}`);
    console.log(`   Failed: ${report.summary.failed}`);
    
    if (report.summary.failed > 0) {
      console.log('\n❌ Failed Tests:');
      Object.entries(results).forEach(([type, result]) => {
        if (!result.success) {
          console.log(`   - ${type}: Exit code ${result.exitCode}`);
        }
      });
    }
    
    console.log(`\n📄 Full report saved to: ${reportPath}`);
  }

  cleanup() {
    console.log('\n🧹 Cleaning up processes...');
    
    this.processes.forEach((process, index) => {
      try {
        if (!process.killed) {
          process.kill('SIGTERM');
          console.log(`✅ Killed process ${index + 1}`);
        }
      } catch (error) {
        console.error(`❌ Error killing process ${index + 1}:`, error.message);
      }
    });
    
    this.processes = [];
  }
}

// CLI interface
if (require.main === module) {
  const testType = process.argv[2] || 'all';
  const validTypes = ['unit', 'integration', 'all'];
  
  if (!validTypes.includes(testType)) {
    console.error(`❌ Invalid test type: ${testType}`);
    console.error(`   Valid types: ${validTypes.join(', ')}`);
    process.exit(1);
  }
  
  const runner = new DatabaseTestRunner();
  runner.run(testType);
}

module.exports = DatabaseTestRunner; 