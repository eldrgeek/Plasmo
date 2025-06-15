# Firebase WebSocket Migration Guide

## Overview

This document provides a complete migration guide for switching from WebSocket server endpoints to Firebase-based equivalents. All WebSocket functionality has been replicated using Firebase Firestore with real-time subscriptions.

## 🚀 Quick Migration Summary

### WebSocket → Firebase Service Mapping

| WebSocket Endpoint | Firebase Service | Method |
|-------------------|------------------|---------|
| `GET /api/extensions` | `extensionService` | `getConnectedExtensions()` |
| `POST /api/command/broadcast` | `extensionService` | `broadcastCommand()` |
| `POST /api/command/send/{id}` | `extensionService` | `sendCommand()` |
| `GET /api/webrtc/rooms` | `webrtcService` | `getAllRooms()` |
| `GET /api/webrtc/rooms/{name}` | `webrtcService` | `getRoom()` |
| `POST /api/webrtc/rooms/{name}/join` | `webrtcService` | `joinRoom()` |
| `POST /api/webrtc/upload` | `webrtcService` | `uploadFile()` |
| `POST /api/test-results` | `testingService` | `storeTestResults()` |
| `POST /api/completion-signal` | `testingService` | `storeCompletionSignal()` |
| `GET /health` | `testingService` | `healthCheck()` |

## 📦 Installation & Setup

### 1. Install Firebase Dependencies

```bash
npm install firebase
```

### 2. Environment Configuration

Create or update your `.env` file:

```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=monad-roundtable.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=monad-roundtable
VITE_FIREBASE_STORAGE_BUCKET=monad-roundtable.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here
```

### 3. Import Services

```javascript
// Import all services
import { 
  extensionService, 
  webrtcService, 
  testingService,
  authService 
} from './src/services';

// Or import individually
import { extensionService } from './src/services/extensionService';
import { webrtcService } from './src/services/webrtcService';
import { testingService } from './src/services/testingService';
```

## 🔄 Migration Examples

### Extension Management

#### Before (WebSocket):
```javascript
// Get connected extensions
const response = await fetch('http://localhost:3001/api/extensions');
const data = await response.json();

// Send command to all extensions
await fetch('http://localhost:3001/api/command/broadcast', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'click_element',
    payload: { selector: '#submit-btn' }
  })
});
```

#### After (Firebase):
```javascript
// Get connected extensions
const extensions = await extensionService.getConnectedExtensions();

// Send command to all extensions
await extensionService.broadcastCommand('click_element', {
  selector: '#submit-btn'
});

// Real-time subscription to extensions
const unsubscribe = extensionService.subscribeToExtensions((data) => {
  console.log('Connected extensions:', data.extensions);
});
```

### WebRTC Room Management

#### Before (WebSocket):
```javascript
// Get all rooms
const rooms = await fetch('http://localhost:3001/api/webrtc/rooms');

// Join room
await fetch(`http://localhost:3001/api/webrtc/rooms/${roomName}/join`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    peer_id: peerId,
    username: username,
    user_data: { role: 'developer' }
  })
});
```

#### After (Firebase):
```javascript
// Get all rooms
const rooms = await webrtcService.getAllRooms();

// Join room
const result = await webrtcService.joinRoom(roomName, peerId, username, {
  role: 'developer'
});

// Real-time subscription to room changes
const unsubscribe = webrtcService.subscribeToPeers(roomName, (data) => {
  console.log('Room peers updated:', data.peers);
});
```

### Test Results & AI Completion

#### Before (WebSocket):
```javascript
// Store test results
await fetch('http://localhost:3001/api/test-results', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    success: true,
    passed: 15,
    total: 20,
    trigger: 'file_change'
  })
});

// Store completion signal
await fetch('http://localhost:3001/api/completion-signal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    completion_id: 'task_123',
    status: 'completed',
    summary: 'Successfully automated form submission'
  })
});
```

#### After (Firebase):
```javascript
// Store test results
await testingService.storeTestResults({
  success: true,
  passed: 15,
  total: 20,
  trigger: 'file_change'
});

// Store completion signal
await testingService.storeCompletionSignal({
  completionId: 'task_123',
  status: 'completed',
  summary: 'Successfully automated form submission'
});

// Real-time subscription to test results
const unsubscribe = testingService.subscribeToTestResults((data) => {
  console.log('New test results:', data.testResults);
});
```

## 🔐 Authentication Requirements

All Firebase services require user authentication. Make sure to authenticate before using services:

```javascript
import { authService } from './src/services/authService';

// Login user first
await authService.login('user@example.com', 'password');

// Or register new user
await authService.register('user@example.com', 'password', 'Username');

// Then use other services
const extensions = await extensionService.getConnectedExtensions();
```

## 📊 Real-time Subscriptions

Firebase provides real-time updates through subscriptions. Always clean up subscriptions:

```javascript
// Subscribe to changes
const unsubscribe = extensionService.subscribeToExtensions((data) => {
  // Handle real-time updates
  updateUI(data.extensions);
});

// Clean up when component unmounts or no longer needed
useEffect(() => {
  return () => {
    unsubscribe();
  };
}, []);
```

## 🔧 Complete Integration Example

Here's a complete example showing how to integrate all services:

```javascript
import React, { useState, useEffect } from 'react';
import { 
  authService, 
  extensionService, 
  webrtcService, 
  testingService 
} from './src/services';

function IntegratedDashboard() {
  const [user, setUser] = useState(null);
  const [extensions, setExtensions] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [testResults, setTestResults] = useState([]);

  useEffect(() => {
    // Listen for auth changes
    const authUnsubscribe = authService.onAuthStateChanged((user) => {
      setUser(user);
      
      if (user) {
        // Set up real-time subscriptions when user is authenticated
        setupSubscriptions();
      }
    });

    return authUnsubscribe;
  }, []);

  const setupSubscriptions = () => {
    // Subscribe to extensions
    const extensionsUnsub = extensionService.subscribeToExtensions((data) => {
      setExtensions(data.extensions);
    });

    // Subscribe to test results
    const testUnsub = testingService.subscribeToTestResults((data) => {
      setTestResults(data.testResults);
    });

    // Clean up subscriptions
    return () => {
      extensionsUnsub();
      testUnsub();
    };
  };

  const handleBroadcastCommand = async () => {
    try {
      await extensionService.broadcastCommand('refresh_page');
      console.log('Command sent to all extensions');
    } catch (error) {
      console.error('Error sending command:', error);
    }
  };

  const handleJoinRoom = async () => {
    try {
      const result = await webrtcService.joinRoom(
        'test-room',
        `peer_${Date.now()}`,
        user.displayName || 'Anonymous',
        { role: 'developer' }
      );
      console.log('Joined room:', result);
    } catch (error) {
      console.error('Error joining room:', error);
    }
  };

  const handleStoreTestResult = async () => {
    try {
      await testingService.storeTestResults({
        success: true,
        passed: 10,
        total: 12,
        trigger: 'manual_test'
      });
      console.log('Test results stored');
    } catch (error) {
      console.error('Error storing test results:', error);
    }
  };

  if (!user) {
    return <div>Please log in to access the dashboard</div>;
  }

  return (
    <div className="dashboard">
      <h1>Integrated Dashboard</h1>
      
      <section>
        <h2>Extensions ({extensions.length})</h2>
        <button onClick={handleBroadcastCommand}>
          Broadcast Refresh Command
        </button>
        <ul>
          {extensions.map(ext => (
            <li key={ext.id}>
              {ext.extensionId} - {ext.userEmail}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>WebRTC</h2>
        <button onClick={handleJoinRoom}>Join Test Room</button>
      </section>

      <section>
        <h2>Test Results ({testResults.length})</h2>
        <button onClick={handleStoreTestResult}>Store Test Result</button>
        <ul>
          {testResults.slice(0, 5).map(test => (
            <li key={test.id}>
              {test.success ? '✅' : '❌'} {test.passed}/{test.total} - {test.trigger}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default IntegratedDashboard;
```

## 🔍 API Reference

### Extension Service

```javascript
// Register extension
await extensionService.registerExtension(extensionId, metadata);

// Update extension status
await extensionService.updateExtensionStatus(extensionId, true, metadata);

// Get connected extensions
const result = await extensionService.getConnectedExtensions();

// Send command to specific extension
await extensionService.sendCommand(extensionId, 'action', payload);

// Broadcast command to all extensions
await extensionService.broadcastCommand('action', payload);

// Subscribe to extension changes
const unsubscribe = extensionService.subscribeToExtensions(callback);

// Get pending commands for extension
const commands = await extensionService.getPendingCommands(extensionId);

// Mark command as executed
await extensionService.markCommandExecuted(commandId, result);
```

### WebRTC Service

```javascript
// Join room
const result = await webrtcService.joinRoom(roomName, peerId, username, userData);

// Leave room
await webrtcService.leaveRoom(roomName, peerId);

// Get all rooms
const rooms = await webrtcService.getAllRooms();

// Get specific room
const room = await webrtcService.getRoom(roomName);

// Update peer data
await webrtcService.updatePeerData(roomName, peerId, userData);

// Send heartbeat
await webrtcService.sendHeartbeat(roomName, peerId);

// Upload file
const result = await webrtcService.uploadFile(roomName, peerId, file);

// Subscribe to room changes
const unsubscribe = webrtcService.subscribeToRoom(roomName, callback);

// Subscribe to peer changes
const unsubscribe = webrtcService.subscribeToPeers(roomName, callback);
```

### Testing Service

```javascript
// Store test results
await testingService.storeTestResults(testData);

// Get latest test results
const results = await testingService.getLatestTestResults(10);

// Store completion signal
await testingService.storeCompletionSignal(completionData);

// Get completion signals
const signals = await testingService.getCompletionSignals(20);

// Subscribe to test results
const unsubscribe = testingService.subscribeToTestResults(callback);

// Subscribe to completion signals
const unsubscribe = testingService.subscribeToCompletionSignals(callback);

// Get test statistics
const stats = await testingService.getTestStatistics(7);

// Health check
const health = await testingService.healthCheck();
```

## 🚨 Important Migration Notes

### 1. Authentication Required
- All Firebase services require user authentication
- Use `authService.login()` or `authService.register()` first
- Handle authentication state changes properly

### 2. Real-time vs HTTP
- Firebase uses real-time subscriptions instead of polling
- Always clean up subscriptions to prevent memory leaks
- Use `onSnapshot` for real-time updates

### 3. Data Structure Changes
- Firebase uses document IDs instead of socket IDs
- Timestamps are Firebase server timestamps
- All data is stored in Firestore collections

### 4. Error Handling
- Firebase errors are different from HTTP errors
- Use try-catch blocks for async operations
- Check authentication state before service calls

### 5. Offline Support
- Firebase provides automatic offline support
- Data syncs when connection is restored
- Consider offline state in your UI

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure user is logged in before calling services
2. **Permission Denied**: Check Firestore security rules
3. **Subscription Not Working**: Verify cleanup of previous subscriptions
4. **Data Not Syncing**: Check internet connection and Firebase config

### Debug Tips

```javascript
// Enable Firebase debug logging
import { enableNetwork, disableNetwork } from 'firebase/firestore';

// Check connection status
console.log('Firebase connected:', navigator.onLine);

// Test authentication
console.log('Current user:', auth.currentUser);

// Test Firestore connection
try {
  await testingService.healthCheck();
  console.log('Firebase services working');
} catch (error) {
  console.error('Firebase connection issue:', error);
}
```

## 📈 Performance Considerations

1. **Limit Subscriptions**: Only subscribe to data you need
2. **Use Pagination**: Limit query results with `limit()`
3. **Clean Up**: Always unsubscribe when components unmount
4. **Batch Operations**: Use batch writes for multiple updates
5. **Index Queries**: Ensure Firestore indexes are created for complex queries

## 🎯 Next Steps

1. **Test Integration**: Start with one service at a time
2. **Update Security Rules**: Customize Firestore rules for your needs
3. **Add Error Handling**: Implement comprehensive error handling
4. **Monitor Usage**: Use Firebase Analytics to monitor usage
5. **Optimize Performance**: Profile and optimize based on usage patterns

This migration provides all the functionality of the WebSocket server with the added benefits of Firebase's real-time capabilities, offline support, and scalability. 