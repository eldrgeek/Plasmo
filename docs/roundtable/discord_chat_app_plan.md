# Discord-Style Chat Application - Development Plan

## Section 0: Firebase Backend Implementation

### 0.1 Firebase Project Setup

**Status: READY FOR IMPLEMENTATION**

The Discord-style chat application will use Firebase for backend services:

#### Firebase Services Used:
- **Firebase Authentication**: User registration, login, and session management
- **Cloud Firestore**: Real-time database for messages, channels, and user data
- **Firebase Hosting**: Deploy the React application
- **Firebase Storage**: File and image uploads in chat
- **Cloud Functions**: Server-side logic for complex operations

### 0.2 Firestore Database Structure

**Database Collections:**

#### Users Collection (`/users/{userId}`)
```javascript
{
  uid: string,           // Firebase Auth UID
  username: string,      // Display name
  email: string,         // Email address
  avatar: string,        // Avatar URL or default
  status: 'online' | 'offline' | 'away',
  createdAt: timestamp,
  lastSeen: timestamp,
  preferences: {
    theme: 'dark' | 'light',
    notifications: boolean
  }
}
```

#### Channels Collection (`/channels/{channelId}`)
```javascript
{
  id: string,            // Auto-generated ID
  name: string,          // Channel name
  description: string,   // Channel description
  type: 'public' | 'private',
  createdBy: string,     // User UID
  createdAt: timestamp,
  members: string[],     // Array of user UIDs
  lastMessage: {
    content: string,
    authorId: string,
    timestamp: timestamp
  }
}
```

#### Messages Subcollection (`/channels/{channelId}/messages/{messageId}`)
```javascript
{
  id: string,            // Auto-generated ID
  content: string,       // Message text
  authorId: string,      // User UID
  authorName: string,    // User display name (denormalized)
  timestamp: timestamp,
  edited: timestamp,     // If message was edited
  replyTo: string,       // Reference to parent message ID
  reactions: {
    '👍': string[],      // Array of user UIDs who reacted
    '❤️': string[],
    // ... other emojis
  },
  attachments: [{
    type: 'image' | 'file',
    url: string,
    name: string,
    size: number
  }]
}
```

#### Direct Messages (`/directMessages/{conversationId}`)
```javascript
{
  id: string,            // Auto-generated ID
  participants: string[], // Array of 2 user UIDs
  createdAt: timestamp,
  lastMessage: {
    content: string,
    authorId: string,
    timestamp: timestamp
  }
}
```

#### DM Messages Subcollection (`/directMessages/{conversationId}/messages/{messageId}`)
```javascript
{
  id: string,
  content: string,
  authorId: string,
  authorName: string,
  timestamp: timestamp,
  edited: timestamp,
  reactions: object,
  attachments: array
}
```

### 0.3 Firebase Security Rules

**Firestore Security Rules:**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own user document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
      allow read: if request.auth != null; // Others can read basic info
    }
    
    // Channel access rules
    match /channels/{channelId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null && 
        request.auth.uid == resource.data.createdBy;
      allow update: if request.auth != null && 
        (request.auth.uid == resource.data.createdBy || 
         request.auth.uid in resource.data.members);
    }
    
    // Messages in channels
    match /channels/{channelId}/messages/{messageId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null && 
        request.auth.uid == request.resource.data.authorId;
      allow update, delete: if request.auth != null && 
        request.auth.uid == resource.data.authorId;
    }
    
    // Direct messages
    match /directMessages/{conversationId} {
      allow read, write: if request.auth != null && 
        request.auth.uid in resource.data.participants;
    }
    
    match /directMessages/{conversationId}/messages/{messageId} {
      allow read: if request.auth != null && 
        request.auth.uid in get(/databases/$(database)/documents/directMessages/$(conversationId)).data.participants;
      allow create: if request.auth != null && 
        request.auth.uid == request.resource.data.authorId;
      allow update, delete: if request.auth != null && 
        request.auth.uid == resource.data.authorId;
    }
  }
}
```

### 0.4 Implementation Guide for bolt.new

**Step-by-step Firebase integration:**

1. **Create Firebase Project** (You'll do this in Firebase Console)
   - Go to https://console.firebase.google.com/
   - Create new project: "discord-chat-app"
   - Enable Authentication (Email/Password, Google OAuth)
   - Enable Firestore Database
   - Enable Storage for file uploads

2. **Initialize Firebase in React App:**
   ```bash
   # In bolt.new, create React app with Firebase:
   npm install firebase react-router-dom
   ```

3. **Firebase Configuration (`src/firebase/config.js`):**
   ```javascript
   import { initializeApp } from 'firebase/app';
   import { getAuth } from 'firebase/auth';
   import { getFirestore } from 'firebase/firestore';
   import { getStorage } from 'firebase/storage';
   
   const firebaseConfig = {
     // Your Firebase config object
   };
   
   const app = initializeApp(firebaseConfig);
   export const auth = getAuth(app);
   export const db = getFirestore(app);
   export const storage = getStorage(app);
   export default app;
   ```

4. **React Components Structure:**
   ```
   src/
   ├── components/
   │   ├── Auth/
   │   │   ├── LoginForm.jsx
   │   │   ├── RegisterForm.jsx
   │   │   └── ProtectedRoute.jsx
   │   ├── Chat/
   │   │   ├── ChannelList.jsx
   │   │   ├── MessageList.jsx
   │   │   ├── MessageInput.jsx
   │   │   ├── UserList.jsx
   │   │   └── TypingIndicator.jsx
   │   ├── Layout/
   │   │   ├── Sidebar.jsx
   │   │   ├── Header.jsx
   │   │   └── ChatContainer.jsx
   │   └── Common/
   │       ├── Avatar.jsx
   │       └── EmojiPicker.jsx
   ├── hooks/
   │   ├── useAuth.js
   │   ├── useFirestore.js
   │   ├── useChannels.js
   │   └── useMessages.js
   ├── services/
   │   ├── authService.js
   │   ├── channelService.js
   │   ├── messageService.js
   │   └── storageService.js
   ├── context/
   │   ├── AuthContext.js
   │   └── ChatContext.js
   └── firebase/
       ├── config.js
       └── firestore.rules
   ```

5. **Firebase Service Integration:**
   ```javascript
   // services/authService.js
   import { 
     signInWithEmailAndPassword, 
     createUserWithEmailAndPassword,
     signOut,
     onAuthStateChanged 
   } from 'firebase/auth';
   import { doc, setDoc, updateDoc } from 'firebase/firestore';
   import { auth, db } from '../firebase/config';
   
   export const authService = {
     // Register new user
     async register(email, password, username) {
       const userCredential = await createUserWithEmailAndPassword(auth, email, password);
       const user = userCredential.user;
       
       // Create user document in Firestore
       await setDoc(doc(db, 'users', user.uid), {
         uid: user.uid,
         username,
         email,
         avatar: '',
         status: 'online',
         createdAt: new Date(),
         lastSeen: new Date()
       });
       
       return user;
     },
     
     // Login user
     async login(email, password) {
       const userCredential = await signInWithEmailAndPassword(auth, email, password);
       
       // Update online status
       await updateDoc(doc(db, 'users', userCredential.user.uid), {
         status: 'online',
         lastSeen: new Date()
       });
       
       return userCredential.user;
     },
     
     // Logout user
     async logout() {
       if (auth.currentUser) {
         await updateDoc(doc(db, 'users', auth.currentUser.uid), {
           status: 'offline',
           lastSeen: new Date()
         });
       }
       await signOut(auth);
     }
   };
   ```

6. **Real-time Message Service:**
   ```javascript
   // services/messageService.js
   import { 
     collection, 
     addDoc, 
     query, 
     orderBy, 
     limit, 
     onSnapshot,
     serverTimestamp 
   } from 'firebase/firestore';
   import { db } from '../firebase/config';
   
   export const messageService = {
     // Send message to channel
     async sendMessage(channelId, content, authorId, authorName) {
       const messagesRef = collection(db, 'channels', channelId, 'messages');
       await addDoc(messagesRef, {
         content,
         authorId,
         authorName,
         timestamp: serverTimestamp(),
         reactions: {},
         attachments: []
       });
     },
     
     // Listen to messages in real-time
     subscribeToMessages(channelId, callback) {
       const messagesRef = collection(db, 'channels', channelId, 'messages');
       const q = query(messagesRef, orderBy('timestamp', 'desc'), limit(50));
       
       return onSnapshot(q, (snapshot) => {
         const messages = snapshot.docs.map(doc => ({
           id: doc.id,
           ...doc.data()
         }));
         callback(messages.reverse());
       });
     }
   };
   ```

### 0.5 Development Sequence

1. **Set up Firebase project and authentication**
2. **Create basic login/register forms**
3. **Implement real-time message listeners**
4. **Build channel management system**
5. **Add user presence and status**
6. **Implement direct messaging**
7. **Add advanced features (reactions, file uploads)**

---

## Project Overview
Building a Discord-like chat application starting with human-to-human communication, with the future goal of integrating AI participants that can engage autonomously or when summoned.

## Development Philosophy
- **Iterative Development**: Build in phases, starting minimal and adding complexity
- **AI-Ready Architecture**: Design with future AI integration in mind
- **User-Controlled AI**: When AI is added, users will configure AI behavior patterns

## Phase 1: Core Chat Foundation (Human-to-Human)

### 1.1 Basic User System
**Current Step Status: NOT STARTED**

**Requirements:**
- Simple username/password registration
- User login/logout
- Basic user profiles (username, avatar placeholder)
- Online/offline status indicators

**Implementation Notes:**
- Use localStorage for initial development (no backend required)
- Store user data as JSON objects
- Simple authentication state management

**Acceptance Criteria:**
- [ ] Users can register with username/password
- [ ] Users can log in and out
- [ ] User status (online/offline) is visible
- [ ] Basic profile display with username

### 1.2 Channel System
**Current Step Status: NOT STARTED**

**Requirements:**
- Create channels (like Discord channels)
- Channel list sidebar
- Switch between channels
- Channel names and descriptions

**Implementation Notes:**
- Channels are containers for messages
- Each channel has unique ID and metadata
- Simple channel creation interface

**Acceptance Criteria:**
- [ ] Users can create new channels
- [ ] Channel list displays in sidebar
- [ ] Users can switch between channels
- [ ] Active channel is highlighted

### 1.3 Real-Time Messaging
**Current Step Status: NOT STARTED**

**Requirements:**
- Send and receive text messages in channels
- Real-time message updates
- Message timestamps
- Message author identification

**Implementation Notes:**
- For development: simulate real-time with periodic polling or WebSockets if available
- Message data structure: {id, author, content, timestamp, channelId}
- Auto-scroll to latest messages

**Acceptance Criteria:**
- [ ] Users can send text messages
- [ ] Messages appear instantly for sender
- [ ] Messages show author and timestamp
- [ ] Message history persists when switching channels

### 1.4 Private Messaging
**Current Step Status: NOT STARTED**

**Requirements:**
- Direct messages between users
- Private message interface
- User list for starting DMs

**Implementation Notes:**
- Private channels are special channel type with 2 participants
- User picker interface for starting DMs
- DM channels appear in sidebar differently than public channels

**Acceptance Criteria:**
- [ ] Users can start private conversations
- [ ] Private messages are separate from public channels
- [ ] DM list shows other participant's name and status

## Phase 2: Enhanced Chat Features

### 2.1 Message Features
**Current Step Status: NOT STARTED**

**Requirements:**
- Message editing and deletion
- Message reactions/emojis
- Message threading/replies
- File and image sharing

### 2.2 User Experience Improvements
**Current Step Status: NOT STARTED**

**Requirements:**
- Message search
- Notification system
- Typing indicators
- Message formatting (bold, italic, code blocks)

## Phase 3: AI Integration Preparation

### 3.1 Participant Architecture
**Current Step Status: NOT STARTED**

**Requirements:**
- Abstract "participant" concept (humans and future AI)
- Participant configuration system
- Participant behavior settings framework

### 3.2 AI Participant Foundation
**Current Step Status: NOT STARTED**

**Requirements:**
- AI participant creation interface
- Configuration options:
  - Activity level (how often they participate unprompted)
  - Topic interests/expertise areas
  - Personality traits (formal/casual, supportive/challenging)
  - Response timing patterns
  - Trigger conditions for autonomous participation

## Phase 4: AI Integration

### 4.1 AI Provider Integration
**Current Step Status: NOT STARTED**

**Requirements:**
- Support for multiple AI APIs (OpenAI, Anthropic, etc.)
- User-configurable AI API keys
- AI response generation and integration

### 4.2 AI Behavior Engine
**Current Step Status: NOT STARTED**

**Requirements:**
- Autonomous participation logic
- Context awareness for AI responses
- User summon/mention system for AI participants

## Technical Architecture Notes

### Technology Stack Recommendations
- **Frontend**: React with TypeScript for type safety
- **Styling**: Tailwind CSS for rapid UI development
- **State Management**: React Context or Zustand for simple state
- **Real-time**: WebSocket simulation or actual WebSocket implementation
- **Storage**: localStorage for development, prepare for backend database

### Data Models

#### User
```typescript
interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  status: 'online' | 'offline' | 'away';
  createdAt: Date;
}
```

#### Channel
```typescript
interface Channel {
  id: string;
  name: string;
  description?: string;
  type: 'public' | 'private';
  participants: string[]; // user IDs
  createdAt: Date;
  createdBy: string; // user ID
}
```

#### Message
```typescript
interface Message {
  id: string;
  content: string;
  authorId: string;
  channelId: string;
  timestamp: Date;
  edited?: Date;
  replyTo?: string; // message ID
}
```

#### Future: AI Participant
```typescript
interface AIParticipant {
  id: string;
  name: string;
  model: string; // 'gpt-4', 'claude-3', etc.
  config: {
    activityLevel: number; // 1-10
    topics: string[];
    personality: string;
    responseDelay: number; // ms
    autonomousMode: boolean;
  };
  apiKey?: string;
}
```

## Current Development Instructions

**STATUS: Ready for Step 1.1 - Basic User System**

The next step is to implement the Basic User System (1.1). This includes:
1. Create a simple registration/login interface
2. Implement user authentication state
3. Add online/offline status tracking
4. Create basic user profile display

Focus on creating a clean, Discord-like UI with a dark theme and modern design patterns.

## Usage Instructions for AI Development Assistant

When ready for the next step, use the command: "Do the next step" and reference this document for the current phase requirements and acceptance criteria.

---

## Comments & Suggestions

### Technical Observations:

1. **Backend Foundation**: Your existing Socket.IO server already has excellent infrastructure for WebRTC and real-time communication. The chat application can leverage this existing architecture.

2. **Authentication Strategy**: The plan uses simple username/password authentication for development. Consider adding JWT tokens for better security once you move beyond localStorage.

3. **Data Persistence**: The current plan uses in-memory storage (Maps/Sets) for development. This means data resets when the server restarts. Consider adding a simple JSON file persistence layer or SQLite database for better development experience.

4. **WebSocket Connection Management**: Your existing server already handles connection cleanup and heartbeat monitoring, which is perfect for a chat application.

### Recommended Improvements:

1. **Message Pagination**: Add pagination to message history endpoints to handle channels with thousands of messages efficiently.

2. **Rate Limiting**: Implement rate limiting on message sending to prevent spam (e.g., max 10 messages per minute per user).

3. **File Sharing**: Your existing server supports file uploads via `/api/webrtc/upload`. This can be reused for image/file sharing in chat.

4. **Typing Indicators**: Implement typing indicators with automatic timeout (stop showing "typing" after 3 seconds of inactivity).

5. **Message Search**: Add a simple text search across message history.

### Integration Notes:

1. **Bolt.new Limitations**: Since bolt.new runs in a sandboxed environment, ensure your Socket.IO server allows CORS from bolt.new's domain.

2. **Development Workflow**: Test the Socket.IO events first with a simple HTML page before building the full React application.

3. **Error Handling**: Add comprehensive error handling for network disconnections and failed message delivery.

4. **State Management**: Consider using Redux or Zustand for complex state management as the application grows.

### Security Considerations:

1. **Input Validation**: Sanitize all user inputs to prevent XSS attacks.
2. **Channel Permissions**: Implement proper authorization checks for private channels.
3. **Message Encryption**: Consider end-to-end encryption for private messages in future versions.

### Performance Optimizations:

1. **Message Caching**: Cache recent messages in memory for faster loading.
2. **Connection Pooling**: Reuse Socket.IO connections when possible.
3. **Lazy Loading**: Load channel history on-demand rather than all at once.

### Future AI Integration Preparedness:

The current architecture is well-suited for AI integration because:
- Socket.IO events can easily accommodate AI participants
- Your MCP server can be integrated to provide AI responses
- The modular design allows adding AI participants without major refactoring

The plan provides a solid foundation for building a Discord-like chat application with your existing Socket.IO infrastructure.