# Roundtable Database Test Suite

Comprehensive testing infrastructure for the Firebase Discord chat application's database layer, focusing on authentication, messaging, and data persistence.

## Overview

This test suite provides thorough coverage of the Firebase backend services including:
- **Unit Tests**: Individual service functions (auth, messaging, channels)
- **Integration Tests**: Cross-service interactions and data flow
- **Firebase Emulator Integration**: Local testing without real Firebase costs

## Test Architecture

### Test Types

1. **Unit Tests** (`tests/unit/`)
   - Authentication service testing
   - Message service operations
   - Channel management
   - User profile management
   - Individual function validation

2. **Integration Tests** (`tests/integration/`)
   - Cross-service workflows
   - Real-time subscription testing
   - Security rules validation
   - Data consistency verification
   - Firebase service integration

### Test Environment

- **Firebase Emulators**: Local Firebase services (Firestore, Auth, Storage)
- **Jest**: Test framework with Firebase mocking
- **Test Data**: Predefined users, channels, and messages
- **Cleanup**: Automatic test data cleanup between tests

## Installation

### Prerequisites

```bash
# Install Node.js dependencies
npm install

# Install Firebase CLI globally
npm install -g firebase-tools

# Login to Firebase (optional for emulator-only testing)
firebase login
```

### Dependencies

The test suite includes these key dependencies:
- `jest`: Test framework
- `@firebase/rules-unit-testing`: Firebase emulator testing
- `firebase-tools`: Firebase CLI and emulators

## Configuration

### Firebase Project Setup

For local testing (recommended):
```bash
# Initialize Firebase project
firebase init

# Select Firestore, Authentication, and Storage
# Choose "Use an existing project" or "Create a new project"
```

### Environment Variables

Create `.env.test` file:
```env
# Firebase Configuration (for real Firebase testing)
REACT_APP_FIREBASE_API_KEY=your_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef

# Test Configuration
TEST_TIMEOUT=30000
EMULATOR_HOST=localhost
FIRESTORE_EMULATOR_PORT=8080
AUTH_EMULATOR_PORT=9099
STORAGE_EMULATOR_PORT=9199
```

## Usage

### Quick Start

```bash
# Run all database tests
npm run test:db

# Run specific test types
npm run test:unit
npm run test:integration

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

### Manual Emulator Management

```bash
# Start Firebase emulators
npm run emulators:start

# In another terminal, run tests
npm run test:unit

# Stop emulators
npm run emulators:stop
```

### Advanced Test Runner

```bash
# Use the comprehensive test runner
node tests/run-tests.js

# Run specific test type
node tests/run-tests.js unit
node tests/run-tests.js integration
```

## Test Structure

### Unit Tests

#### Authentication Service (`tests/unit/authService.test.js`)
```javascript
describe('Authentication Service', () => {
  test('should register new user', async () => {
    const result = await authService.register(testUser);
    expect(result.success).toBe(true);
  });
  
  test('should login existing user', async () => {
    const result = await authService.login(credentials);
    expect(result.user).toBeDefined();
  });
});
```

#### Message Service (`tests/unit/messageService.test.js`)
```javascript
describe('Message Service', () => {
  test('should send message to channel', async () => {
    const message = await messageService.sendMessage(channelId, content);
    expect(message.id).toBeDefined();
  });
  
  test('should edit message', async () => {
    const updated = await messageService.editMessage(messageId, newContent);
    expect(updated.content).toBe(newContent);
  });
});
```

### Integration Tests

#### Firebase Integration (`tests/integration/firebaseIntegration.test.js`)
```javascript
describe('Firebase Integration', () => {
  test('should handle complete user workflow', async () => {
    // Register user
    const user = await authService.register(testUser);
    
    // Create channel
    const channel = await channelService.create(channelData);
    
    // Send message
    const message = await messageService.send(channel.id, content);
    
    // Verify data consistency
    expect(message.authorId).toBe(user.id);
  });
});
```

### Test Utilities

#### Test Helpers (`tests/utils/testHelpers.js`)
```javascript
// Predefined test data
export const TEST_USERS = {
  alice: { email: 'alice@test.com', password: 'password123' },
  bob: { email: 'bob@test.com', password: 'password123' }
};

export const TEST_CHANNELS = {
  general: { name: 'general', type: 'public' },
  private: { name: 'private-room', type: 'private' }
};

// Helper functions
export async function createTestUser(userData) {
  return await authService.register(userData);
}

export async function cleanupTestData() {
  // Clean up test collections
}
```

## Firebase Emulator Setup

### Emulator Configuration

The test suite uses Firebase emulators for local testing:

```json
{
  "emulators": {
    "firestore": {
      "port": 8080
    },
    "auth": {
      "port": 9099
    },
    "storage": {
      "port": 9199
    },
    "ui": {
      "enabled": true,
      "port": 4000
    }
  }
}
```

### Emulator Benefits

- **No Firebase costs**: All operations run locally
- **Fast reset**: Clean state for each test run
- **Offline testing**: No internet connection required
- **Debug UI**: Visual interface at http://localhost:4000

## Debugging

### Common Issues

1. **Emulator Connection Errors**
   ```bash
   # Check if emulators are running
   curl http://localhost:8080
   
   # Restart emulators
   firebase emulators:stop
   firebase emulators:start
   ```

2. **Test Timeouts**
   ```javascript
   // Increase timeout in jest.config.js
   module.exports = {
     testTimeout: 30000
   };
   ```

3. **Authentication Errors**
   ```javascript
   // Ensure emulator environment variables are set
   process.env.FIRESTORE_EMULATOR_HOST = 'localhost:8080';
   process.env.FIREBASE_AUTH_EMULATOR_HOST = 'localhost:9099';
   ```

### Debug Mode

```bash
# Run tests with verbose output
npm run test:unit -- --verbose

# Run specific test file
npm run test:unit -- tests/unit/authService.test.js

# Debug with Node.js inspector
node --inspect-brk node_modules/.bin/jest tests/unit/authService.test.js
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Database Tests

on: [push, pull_request]

jobs:
  database-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Install Firebase CLI
      run: npm install -g firebase-tools
      
    - name: Run database tests
      run: npm run test:ci
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Test Reports

The test runner generates detailed reports:
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "testType": "database",
  "summary": {
    "total": 2,
    "passed": 2,
    "failed": 0
  },
  "results": {
    "unit": { "success": true, "exitCode": 0 },
    "integration": { "success": true, "exitCode": 0 }
  }
}
```

## Best Practices

### Test Organization

1. **Descriptive Names**: Use clear, descriptive test names
2. **Setup/Teardown**: Clean up test data between tests
3. **Isolation**: Each test should be independent
4. **Assertions**: Use specific assertions with clear error messages

### Firebase Testing

1. **Use Emulators**: Always test against emulators, not production
2. **Clean State**: Reset emulator data between test suites
3. **Realistic Data**: Use realistic test data that matches production patterns
4. **Error Scenarios**: Test both success and failure cases

### Performance

1. **Parallel Tests**: Run independent tests in parallel
2. **Efficient Cleanup**: Batch cleanup operations
3. **Selective Testing**: Run only relevant tests during development
4. **Caching**: Cache emulator startup when possible

## Troubleshooting

### Firebase Emulator Issues

```bash
# Clear emulator data
firebase emulators:stop
rm -rf .firebase/emulators

# Restart with fresh state
firebase emulators:start --only firestore,auth,storage
```

### Test Failures

1. **Check emulator status**: Ensure all required emulators are running
2. **Verify test data**: Confirm test data setup is correct
3. **Review logs**: Check both test output and emulator logs
4. **Isolation**: Run failing tests individually to identify issues

### Performance Issues

1. **Reduce test scope**: Focus on specific areas during development
2. **Optimize cleanup**: Batch database operations
3. **Use test doubles**: Mock external dependencies when appropriate
4. **Profile tests**: Identify slow tests and optimize

## Contributing

### Adding New Tests

1. **Follow naming conventions**: `*.test.js` for test files
2. **Use test utilities**: Leverage existing helpers and test data
3. **Document test purpose**: Add clear descriptions for complex tests
4. **Update this README**: Document new test categories or utilities

### Test Data Management

1. **Centralized test data**: Add new test data to `testHelpers.js`
2. **Realistic scenarios**: Create test data that reflects real usage
3. **Edge cases**: Include boundary conditions and error scenarios
4. **Cleanup**: Ensure new tests clean up their data

## Resources

- [Firebase Testing Documentation](https://firebase.google.com/docs/emulator-suite)
- [Jest Testing Framework](https://jestjs.io/docs/getting-started)
- [Firebase Rules Unit Testing](https://firebase.google.com/docs/rules/unit-tests)
- [Firebase Emulator Suite](https://firebase.google.com/docs/emulator-suite/install_and_configure) 