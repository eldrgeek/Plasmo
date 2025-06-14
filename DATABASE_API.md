# Roundtable Database API Documentation

## Overview

The Roundtable chat application uses Firebase Firestore as its database backend. This document outlines all available services and their methods for interacting with the database.

## 🚀 Quick Setup Guide

### 1. Install Required Packages

```bash
npm install firebase
```

### 2. Environment Configuration

Create a `.env` file in your project root with your Firebase configuration:

```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=monad-roundtable.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=monad-roundtable
VITE_FIREBASE_STORAGE_BUCKET=monad-roundtable.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here
```

**Note**: Use `REACT_APP_` prefix instead of `VITE_` if you're using Create React App:
```env
REACT_APP_FIREBASE_API_KEY=your_api_key_here
REACT_APP_FIREBASE_AUTH_DOMAIN=monad-roundtable.firebaseapp.com
# ... etc
```

### 3. Firebase Configuration File

Update `src/firebase/config.js` to use environment variables:

```javascript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY, // or process.env.REACT_APP_FIREBASE_API_KEY
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app;
```

### 4. Get Your Firebase Config Values

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your `monad-roundtable` project
3. Click the gear icon ⚙️ → Project settings
4. Scroll down to "Your apps" section
5. Click on your web app or create one if it doesn't exist
6. Copy the config values to your `.env` file

### 5. Enable Firebase Services

In the Firebase Console, enable these services:

1. **Authentication**:
   - Go to Authentication → Sign-in method
   - Enable "Email/Password"
   - Optionally enable "Google" for social login

2. **Firestore Database**:
   - Go to Firestore Database
   - Click "Create database"
   - Choose "Start in production mode"
   - Select your preferred location

3. **Storage**:
   - Go to Storage
   - Click "Get started"
   - Choose "Start in production mode"

### 6. Deploy Security Rules

```bash
# Deploy Firestore security rules
firebase deploy --only firestore:rules

# Deploy Storage security rules  
firebase deploy --only storage
```

### 7. Initialize Database

```bash
# Test the database setup
node test-database.js
```

## 🔧 Integration Examples

### Basic React Integration

```jsx
// App.jsx
import React, { useEffect, useState } from 'react';
import { authService, databaseService } from './services';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize database
    databaseService.initializeDatabase();

    // Listen for auth changes
    const unsubscribe = authService.onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="App">
      {user ? <ChatApp user={user} /> : <LoginForm />}
    </div>
  );
}
```

### Service Import Pattern

```javascript
// Import all services
import { authService } from './src/services/authService';
import { channelService } from './src/services/channelService';
import { messageService } from './src/services/messageService';
import { userService } from './src/services/userService';
import { storageService } from './src/services/storageService';
import { databaseService } from './src/services/databaseService';

// Or import specific methods
import { 
  authService, 
  channelService, 
  messageService 
} from './src/services';
```

### Environment Variables Access

```javascript
// For Vite (recommended)
const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;

// For Create React App
const apiKey = process.env.REACT_APP_FIREBASE_API_KEY;

// For Node.js (server-side)
const apiKey = process.env.FIREBASE_API_KEY;
```

## 📦 Package Dependencies

Your `package.json` should include:

```json
{
  "dependencies": {
    "firebase": "^10.7.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

## 🔒 Security Notes

- **Never commit your `.env` file** - Add it to `.gitignore`
- **Use environment variables** for all sensitive config
- **Enable App Check** in production for additional security
- **Review security rules** before deploying to production

## 🚨 Common Setup Issues

### Issue: "Firebase config not found"
**Solution**: Make sure your `.env` file is in the project root and variables are properly prefixed.

### Issue: "Permission denied" errors
**Solution**: Deploy your Firestore security rules with `firebase deploy --only firestore:rules`

### Issue: "Project not found"
**Solution**: Verify your `projectId` in the Firebase config matches your actual project ID.

### Issue: Environment variables not loading
**Solution**: 
- For Vite: Use `VITE_` prefix
- For CRA: Use `REACT_APP_` prefix  
- Restart your dev server after adding env vars

---

## Services

### 1. Authentication Service (`authService`)

Handles user authentication and user document management.

#### Methods

##### `register(email, password, username)`
- **Purpose**: Register a new user
- **Parameters**: 
  - `email` (string): User's email address
  - `password` (string): User's password
  - `username` (string): Display name
- **Returns**: Firebase User object
- **Creates**: User document in `/users/{uid}` collection

##### `login(email, password)`
- **Purpose**: Log in existing user
- **Parameters**: 
  - `email` (string): User's email
  - `password` (string): User's password
- **Returns**: Firebase User object
- **Updates**: User status to 'online'

##### `logout()`
- **Purpose**: Log out current user
- **Updates**: User status to 'offline'

##### `getCurrentUserData()`
- **Purpose**: Get current user's Firestore document
- **Returns**: User data object or null

##### `updateUserStatus(status)`
- **Purpose**: Update user's online status
- **Parameters**: 
  - `status` (string): 'online', 'offline', or 'away'

##### `updateUserPreferences(preferences)`
- **Purpose**: Update user preferences
- **Parameters**: 
  - `preferences` (object): User preference settings

---

### 2. Channel Service (`channelService`)

Manages chat channels and channel memberships.

#### Methods

##### `createChannel(name, description, type, members)`
- **Purpose**: Create a new channel
- **Parameters**: 
  - `name` (string): Channel name
  - `description` (string): Channel description
  - `type` (string): 'public' or 'private'
  - `members` (array): Array of user IDs for private channels
- **Returns**: Channel object with ID

##### `getUserChannels(userId)`
- **Purpose**: Get all channels accessible to a user
- **Parameters**: 
  - `userId` (string): User ID
- **Returns**: Array of channel objects

##### `subscribeToUserChannels(userId, callback)`
- **Purpose**: Real-time subscription to user's channels
- **Parameters**: 
  - `userId` (string): User ID
  - `callback` (function): Callback function for updates
- **Returns**: Unsubscribe function

##### `joinChannel(channelId)`
- **Purpose**: Join a private channel
- **Parameters**: 
  - `channelId` (string): Channel ID

##### `leaveChannel(channelId)`
- **Purpose**: Leave a private channel
- **Parameters**: 
  - `channelId` (string): Channel ID

##### `updateChannel(channelId, updates)`
- **Purpose**: Update channel information
- **Parameters**: 
  - `channelId` (string): Channel ID
  - `updates` (object): Fields to update

##### `deleteChannel(channelId)`
- **Purpose**: Delete a channel (creator only)
- **Parameters**: 
  - `channelId` (string): Channel ID

---

### 3. Message Service (`messageService`)

Handles all messaging functionality including real-time messaging, reactions, and direct messages.

#### Methods

##### `sendMessage(channelId, content, replyTo, attachments)`
- **Purpose**: Send a message to a channel
- **Parameters**: 
  - `channelId` (string): Target channel ID
  - `content` (string): Message text
  - `replyTo` (string, optional): ID of message being replied to
  - `attachments` (array, optional): File attachments
- **Returns**: Message object with ID

##### `sendDirectMessage(recipientId, content, attachments)`
- **Purpose**: Send a direct message to another user
- **Parameters**: 
  - `recipientId` (string): Recipient user ID
  - `content` (string): Message text
  - `attachments` (array, optional): File attachments
- **Returns**: Message object with ID

##### `subscribeToMessages(channelId, callback, limitCount)`
- **Purpose**: Real-time subscription to channel messages
- **Parameters**: 
  - `channelId` (string): Channel ID
  - `callback` (function): Callback for message updates
  - `limitCount` (number, optional): Message limit (default: 50)
- **Returns**: Unsubscribe function

##### `subscribeToDirectMessages(conversationId, callback, limitCount)`
- **Purpose**: Real-time subscription to direct messages
- **Parameters**: 
  - `conversationId` (string): Conversation ID
  - `callback` (function): Callback for message updates
  - `limitCount` (number, optional): Message limit (default: 50)
- **Returns**: Unsubscribe function

##### `editMessage(channelId, messageId, newContent, isDM)`
- **Purpose**: Edit an existing message
- **Parameters**: 
  - `channelId` (string): Channel or conversation ID
  - `messageId` (string): Message ID
  - `newContent` (string): New message content
  - `isDM` (boolean): Whether this is a direct message

##### `deleteMessage(channelId, messageId, isDM)`
- **Purpose**: Delete a message (soft delete)
- **Parameters**: 
  - `channelId` (string): Channel or conversation ID
  - `messageId` (string): Message ID
  - `isDM` (boolean): Whether this is a direct message

##### `addReaction(channelId, messageId, emoji, isDM)`
- **Purpose**: Add or remove a reaction to a message
- **Parameters**: 
  - `channelId` (string): Channel or conversation ID
  - `messageId` (string): Message ID
  - `emoji` (string): Emoji character
  - `isDM` (boolean): Whether this is a direct message

##### `searchMessages(channelId, searchTerm, isDM)`
- **Purpose**: Search messages in a channel
- **Parameters**: 
  - `channelId` (string): Channel or conversation ID
  - `searchTerm` (string): Search query
  - `isDM` (boolean): Whether to search direct messages
- **Returns**: Array of matching messages

---

### 4. User Service (`userService`)

Manages user data, presence, and user relationships.

#### Methods

##### `getUser(userId)`
- **Purpose**: Get user data by ID
- **Parameters**: 
  - `userId` (string): User ID
- **Returns**: User object

##### `getUsers(userIds)`
- **Purpose**: Get multiple users by IDs
- **Parameters**: 
  - `userIds` (array): Array of user IDs
- **Returns**: Array of user objects

##### `searchUsers(searchTerm, limit)`
- **Purpose**: Search users by username
- **Parameters**: 
  - `searchTerm` (string): Search query
  - `limit` (number, optional): Result limit (default: 20)
- **Returns**: Array of matching users

##### `subscribeToOnlineUsers(callback)`
- **Purpose**: Real-time subscription to online users
- **Parameters**: 
  - `callback` (function): Callback for user updates
- **Returns**: Unsubscribe function

##### `setTyping(channelId, isTyping)`
- **Purpose**: Set typing indicator for a channel
- **Parameters**: 
  - `channelId` (string): Channel ID
  - `isTyping` (boolean): Whether user is typing

##### `subscribeToTyping(channelId, callback)`
- **Purpose**: Subscribe to typing indicators for a channel
- **Parameters**: 
  - `channelId` (string): Channel ID
  - `callback` (function): Callback for typing updates
- **Returns**: Unsubscribe function

##### `updateProfile(updates)`
- **Purpose**: Update current user's profile
- **Parameters**: 
  - `updates` (object): Profile fields to update

##### `getChannelUsers(channelId)`
- **Purpose**: Get users in a specific channel
- **Parameters**: 
  - `channelId` (string): Channel ID
- **Returns**: Array of user objects

---

### 5. Storage Service (`storageService`)

Handles file uploads and storage management.

#### Methods

##### `uploadFile(file, path, onProgress)`
- **Purpose**: Upload a file to Firebase Storage
- **Parameters**: 
  - `file` (File): File object to upload
  - `path` (string): Storage path
  - `onProgress` (function, optional): Progress callback
- **Returns**: File metadata object

##### `uploadChatImage(file, channelId, onProgress)`
- **Purpose**: Upload an image for chat
- **Parameters**: 
  - `file` (File): Image file
  - `channelId` (string): Channel ID
  - `onProgress` (function, optional): Progress callback
- **Returns**: File metadata object

##### `uploadAvatar(file, onProgress)`
- **Purpose**: Upload user avatar image
- **Parameters**: 
  - `file` (File): Avatar image file
  - `onProgress` (function, optional): Progress callback
- **Returns**: Download URL

##### `validateFile(file, options)`
- **Purpose**: Validate file type and size
- **Parameters**: 
  - `file` (File): File to validate
  - `options` (object): Validation options
- **Returns**: Validation result object

##### `deleteFile(filePath)`
- **Purpose**: Delete a file from storage
- **Parameters**: 
  - `filePath` (string): File path in storage

##### `getUserFiles(userId)`
- **Purpose**: Get all files uploaded by a user
- **Parameters**: 
  - `userId` (string, optional): User ID (defaults to current user)
- **Returns**: Array of file objects

---

### 6. Database Service (`databaseService`)

Handles database initialization and maintenance.

#### Methods

##### `initializeDatabase()`
- **Purpose**: Initialize database with default data
- **Creates**: Default channels and welcome message

##### `getDatabaseStats()`
- **Purpose**: Get database statistics
- **Returns**: Statistics object with counts

##### `healthCheck()`
- **Purpose**: Check database connection health
- **Returns**: Health status object

##### `cleanupOldData()`
- **Purpose**: Clean up old/stale data
- **Removes**: Old typing indicators and temporary data

---

## Database Schema

### Collections

#### `/users/{userId}`
```javascript
{
  uid: string,
  username: string,
  email: string,
  avatar: string,
  status: 'online' | 'offline' | 'away',
  createdAt: timestamp,
  lastSeen: timestamp,
  preferences: {
    theme: 'dark' | 'light',
    notifications: boolean,
    soundEnabled: boolean
  }
}
```

#### `/channels/{channelId}`
```javascript
{
  name: string,
  description: string,
  type: 'public' | 'private',
  createdBy: string,
  createdAt: timestamp,
  members: string[],
  lastMessage: {
    content: string,
    authorId: string,
    timestamp: timestamp
  },
  messageCount: number
}
```

#### `/channels/{channelId}/messages/{messageId}`
```javascript
{
  content: string,
  authorId: string,
  authorName: string,
  timestamp: timestamp,
  edited: timestamp,
  replyTo: string,
  reactions: {
    '👍': string[],
    '❤️': string[]
  },
  attachments: [{
    type: 'image' | 'file',
    url: string,
    name: string,
    size: number
  }],
  deleted: boolean
}
```

#### `/directMessages/{conversationId}`
```javascript
{
  participants: string[],
  createdAt: timestamp,
  lastMessage: {
    content: string,
    authorId: string,
    timestamp: timestamp
  }
}
```

#### `/directMessages/{conversationId}/messages/{messageId}`
```javascript
{
  content: string,
  authorId: string,
  authorName: string,
  timestamp: timestamp,
  edited: timestamp,
  reactions: object,
  attachments: array,
  deleted: boolean
}
```

#### `/typing/{channelId_userId}`
```javascript
{
  userId: string,
  username: string,
  channelId: string,
  timestamp: timestamp
}
```

---

## Usage Examples

### Basic Chat Flow

```javascript
import { authService, channelService, messageService } from './services';

// 1. Register/Login
const user = await authService.register('user@example.com', 'password', 'Username');

// 2. Get user's channels
const channels = await channelService.getUserChannels(user.uid);

// 3. Subscribe to messages in a channel
const unsubscribe = messageService.subscribeToMessages(
  channels[0].id, 
  (messages) => {
    console.log('New messages:', messages);
  }
);

// 4. Send a message
await messageService.sendMessage(channels[0].id, 'Hello, world!');

// 5. Clean up subscription
unsubscribe();
```

### Real-time Presence

```javascript
import { userService } from './services';

// Subscribe to online users
const unsubscribe = userService.subscribeToOnlineUsers((users) => {
  console.log('Online users:', users);
});

// Update your status
await userService.updateStatus('away');
```

### File Upload

```javascript
import { storageService, messageService } from './services';

// Upload and send image
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

// Validate file
const validation = storageService.validateImage(file);
if (!validation.isValid) {
  console.error('Invalid file:', validation.errors);
  return;
}

// Upload with progress
const fileData = await storageService.uploadChatImage(
  file, 
  channelId,
  (progress) => console.log(`Upload progress: ${progress}%`)
);

// Send message with attachment
await messageService.sendMessage(channelId, 'Check out this image!', null, [fileData]);
```

---

## Error Handling

All service methods throw errors that should be caught and handled appropriately:

```javascript
try {
  await messageService.sendMessage(channelId, content);
} catch (error) {
  if (error.code === 'permission-denied') {
    console.error('You do not have permission to send messages to this channel');
  } else if (error.code === 'unauthenticated') {
    console.error('You must be logged in to send messages');
  } else {
    console.error('Failed to send message:', error.message);
  }
}
```

---

## Security Rules

The database is protected by comprehensive Firestore security rules that ensure:

- Users can only read/write their own user documents
- Channel access is properly controlled based on type and membership
- Message operations are restricted to authenticated users
- Users can only edit/delete their own messages
- Direct message access is limited to participants

---

## Performance Considerations

- **Pagination**: Use the `limit` parameter and pagination for large datasets
- **Indexes**: All common queries are optimized with composite indexes
- **Real-time Subscriptions**: Unsubscribe from listeners when components unmount
- **File Uploads**: Use progress callbacks for large file uploads
- **Caching**: Firebase automatically caches data for offline access

---

## Future Enhancements

- **Full-text Search**: Integration with Algolia or similar service
- **Push Notifications**: Firebase Cloud Messaging integration
- **Cloud Functions**: Server-side logic for complex operations
- **Analytics**: User engagement and usage analytics
- **Moderation**: Content moderation and spam detection 