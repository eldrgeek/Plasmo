# 🤖 Bolt.new Integration Guide for Roundtable Chat

This guide shows you exactly how to integrate the Roundtable database backend with Bolt.new or any other AI coding assistant.

## 📦 Step 1: Install Firebase

In your Bolt.new project, run:

```bash
npm install firebase
```

## 🔧 Step 2: Environment Setup

Create a `.env` file in your project root:

```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=monad-roundtable.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=monad-roundtable
VITE_FIREBASE_STORAGE_BUCKET=monad-roundtable.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here
```

**Get these values from:**
1. [Firebase Console](https://console.firebase.google.com/)
2. Select `monad-roundtable` project
3. Project Settings ⚙️ → Your apps → Web app config

## 📁 Step 3: Copy Database Services

Copy these files from the Roundtable backend to your Bolt.new project:

```
src/
├── firebase/
│   └── config.js                 # Firebase configuration
└── services/
    ├── authService.js            # Authentication
    ├── channelService.js         # Channel management
    ├── messageService.js         # Real-time messaging
    ├── userService.js            # User management
    ├── storageService.js         # File uploads
    └── databaseService.js        # Database utilities
```

## 🚀 Step 4: Basic Integration Example

Here's a complete example for Bolt.new:

### App.jsx
```jsx
import React, { useEffect, useState } from 'react';
import { authService, databaseService } from './src/services/authService';
import LoginForm from './components/LoginForm';
import ChatApp from './components/ChatApp';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize database with default channels
    databaseService.initializeDatabase().catch(console.error);

    // Listen for authentication state changes
    const unsubscribe = authService.onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading Roundtable...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {user ? <ChatApp user={user} /> : <LoginForm />}
    </div>
  );
}

export default App;
```

### LoginForm.jsx
```jsx
import React, { useState } from 'react';
import { authService } from '../src/services/authService';

function LoginForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await authService.login(email, password);
      } else {
        await authService.register(email, password, username);
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6 text-white">
          {isLogin ? 'Login to Roundtable' : 'Join Roundtable'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              required
            />
          )}
          
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            required
          />
          
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            required
          />
          
          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded disabled:opacity-50"
          >
            {loading ? 'Loading...' : (isLogin ? 'Login' : 'Sign Up')}
          </button>
        </form>
        
        <p className="text-center mt-4 text-gray-400">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-blue-400 hover:text-blue-300"
          >
            {isLogin ? 'Sign up' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default LoginForm;
```

### ChatApp.jsx
```jsx
import React, { useEffect, useState } from 'react';
import { channelService, messageService, authService } from '../src/services';

function ChatApp({ user }) {
  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    // Subscribe to user's channels
    const unsubscribeChannels = channelService.subscribeToUserChannels(
      user.uid,
      (channels) => {
        setChannels(channels);
        if (!activeChannel && channels.length > 0) {
          setActiveChannel(channels[0]);
        }
      }
    );

    return unsubscribeChannels;
  }, [user.uid]);

  useEffect(() => {
    if (!activeChannel) return;

    // Subscribe to messages in active channel
    const unsubscribeMessages = messageService.subscribeToMessages(
      activeChannel.id,
      setMessages
    );

    return unsubscribeMessages;
  }, [activeChannel]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeChannel) return;

    try {
      await messageService.sendMessage(activeChannel.id, newMessage.trim());
      setNewMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-white">Roundtable</h1>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-white text-sm"
          >
            Logout
          </button>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-gray-400 text-sm font-semibold mb-2">CHANNELS</h3>
          {channels.map((channel) => (
            <button
              key={channel.id}
              onClick={() => setActiveChannel(channel)}
              className={`w-full text-left p-2 rounded hover:bg-gray-700 ${
                activeChannel?.id === channel.id ? 'bg-gray-700' : ''
              }`}
            >
              <span className="text-gray-300"># {channel.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeChannel ? (
          <>
            {/* Header */}
            <div className="bg-gray-800 p-4 border-b border-gray-700">
              <h2 className="text-white font-semibold"># {activeChannel.name}</h2>
              {activeChannel.description && (
                <p className="text-gray-400 text-sm">{activeChannel.description}</p>
              )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div key={message.id} className="flex space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-bold">
                      {message.authorName?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-white font-semibold">{message.authorName}</span>
                      <span className="text-gray-400 text-xs">
                        {message.timestamp?.toDate?.()?.toLocaleTimeString() || 'Now'}
                      </span>
                    </div>
                    <p className="text-gray-300">{message.content}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <form onSubmit={sendMessage} className="p-4 bg-gray-800">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder={`Message #${activeChannel.name}`}
                className="w-full p-3 bg-gray-700 text-white rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-gray-400">Select a channel to start chatting</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatApp;
```

## 🎯 Step 5: Tell Bolt.new What to Build

Use this prompt with Bolt.new:

```
I have a Firebase backend for a Discord-style chat app called Roundtable. 

I've already set up:
- Firebase authentication, Firestore, and Storage
- Complete backend services for real-time messaging
- Database with channels, messages, users, and file uploads

Please create a modern React chat interface that uses these existing services:

Services available:
- authService: login, register, logout, user management
- channelService: create/join channels, real-time channel updates  
- messageService: send/receive messages, reactions, file attachments
- userService: user presence, typing indicators, user search
- storageService: file uploads, avatars, image sharing

The UI should be:
- Discord-style dark theme with sidebar and main chat area
- Real-time messaging with live updates
- Channel list with public/private channels
- User list showing online status
- Message reactions and file sharing
- Responsive design for mobile/desktop

Import the services from './src/services/' and use the methods documented in DATABASE_API.md.

Focus on creating a beautiful, modern chat interface - the backend is already complete.
```

## 🔥 Step 6: Advanced Features

Once you have the basic chat working, you can add:

### Real-time Typing Indicators
```jsx
import { userService } from '../src/services/userService';

// In your message input component
const handleTyping = () => {
  userService.setTyping(activeChannel.id, true);
};

const handleStopTyping = () => {
  userService.setTyping(activeChannel.id, false);
};
```

### File Uploads
```jsx
import { storageService, messageService } from '../src/services';

const handleFileUpload = async (file) => {
  try {
    const fileData = await storageService.uploadChatImage(
      file, 
      activeChannel.id,
      (progress) => console.log(`Upload: ${progress}%`)
    );
    
    await messageService.sendMessage(
      activeChannel.id, 
      'Shared an image', 
      null, 
      [fileData]
    );
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

### Message Reactions
```jsx
const addReaction = async (messageId, emoji) => {
  try {
    await messageService.addReaction(activeChannel.id, messageId, emoji);
  } catch (error) {
    console.error('Failed to add reaction:', error);
  }
};
```

## 🚨 Common Issues & Solutions

### Issue: "Firebase not configured"
**Solution**: Make sure your `.env` file has all the Firebase config values and restart your dev server.

### Issue: "Permission denied"
**Solution**: The Firestore security rules are already set up. Make sure you're logged in and the user has proper permissions.

### Issue: "Module not found"
**Solution**: Make sure you've copied all the service files to the correct paths in your project.

### Issue: Real-time updates not working
**Solution**: Check that you're properly subscribing to the real-time listeners and cleaning them up in useEffect.

## 📚 Complete API Reference

See `DATABASE_API.md` for the complete documentation of all available methods and their parameters.

## 🎉 You're Ready!

With this setup, you have a production-ready chat backend that supports:
- ✅ Real-time messaging
- ✅ User authentication  
- ✅ File uploads and sharing
- ✅ Channel management
- ✅ User presence and typing indicators
- ✅ Message reactions and editing
- ✅ Direct messaging
- ✅ Search functionality

Just focus on building a beautiful UI - the backend handles everything else! 