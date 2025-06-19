import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getStorage, connectStorageEmulator } from 'firebase/storage';

// Test user data
export const TEST_USERS = {
  alice: {
    uid: 'alice-test-uid',
    email: 'alice@test.com',
    displayName: 'Alice Test',
    password: 'testpassword123'
  },
  bob: {
    uid: 'bob-test-uid',
    email: 'bob@test.com',
    displayName: 'Bob Test',
    password: 'testpassword123'
  },
  charlie: {
    uid: 'charlie-test-uid',
    email: 'charlie@test.com',
    displayName: 'Charlie Test',
    password: 'testpassword123'
  }
};

// Test channel data
export const TEST_CHANNELS = {
  general: {
    id: 'general-test-id',
    name: 'general',
    description: 'General discussion',
    type: 'public',
    createdBy: TEST_USERS.alice.uid
  },
  private: {
    id: 'private-test-id',
    name: 'private-channel',
    description: 'Private channel',
    type: 'private',
    createdBy: TEST_USERS.alice.uid,
    members: [TEST_USERS.alice.uid, TEST_USERS.bob.uid]
  }
};

// Test message data
export const TEST_MESSAGES = {
  simple: {
    content: 'Hello, world!',
    authorId: TEST_USERS.alice.uid,
    authorName: TEST_USERS.alice.displayName
  },
  withAttachment: {
    content: 'Check out this file',
    authorId: TEST_USERS.bob.uid,
    authorName: TEST_USERS.bob.displayName,
    attachments: [{
      name: 'test.pdf',
      url: 'https://example.com/test.pdf',
      size: 1024
    }]
  },
  reply: {
    content: 'This is a reply',
    authorId: TEST_USERS.charlie.uid,
    authorName: TEST_USERS.charlie.displayName,
    replyTo: 'original-message-id'
  }
};

// Helper to create authenticated context for testing
export function getAuthenticatedContext(testEnv, user) {
  return testEnv.authenticatedContext(user.uid, {
    email: user.email,
    name: user.displayName
  });
}

// Helper to create unauthenticated context
export function getUnauthenticatedContext(testEnv) {
  return testEnv.unauthenticatedContext();
}

// Helper to wait for async operations
export function waitFor(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Helper to create test data in Firestore
export async function createTestUser(context, userData) {
  const db = context.firestore();
  await db.collection('users').doc(userData.uid).set({
    email: userData.email,
    displayName: userData.displayName,
    createdAt: new Date(),
    status: 'online',
    preferences: {
      theme: 'dark',
      notifications: true
    }
  });
}

export async function createTestChannel(context, channelData) {
  const db = context.firestore();
  await db.collection('channels').doc(channelData.id).set({
    name: channelData.name,
    description: channelData.description,
    type: channelData.type,
    createdBy: channelData.createdBy,
    createdAt: new Date(),
    members: channelData.members || [],
    messageCount: 0
  });
}

export async function createTestMessage(context, channelId, messageData) {
  const db = context.firestore();
  const messageRef = await db.collection('channels').doc(channelId)
    .collection('messages').add({
      ...messageData,
      timestamp: new Date(),
      edited: null,
      reactions: {},
      deleted: false
    });
  return messageRef.id;
}

// Helper to generate random test data
export function generateRandomUser() {
  const id = Math.random().toString(36).substr(2, 9);
  return {
    uid: `user-${id}`,
    email: `user${id}@test.com`,
    displayName: `Test User ${id}`,
    password: 'testpassword123'
  };
}

export function generateRandomChannel() {
  const id = Math.random().toString(36).substr(2, 9);
  return {
    id: `channel-${id}`,
    name: `test-channel-${id}`,
    description: `Test channel ${id}`,
    type: Math.random() > 0.5 ? 'public' : 'private',
    createdBy: TEST_USERS.alice.uid
  };
}

export function generateRandomMessage() {
  const id = Math.random().toString(36).substr(2, 9);
  return {
    content: `Test message ${id}`,
    authorId: TEST_USERS.alice.uid,
    authorName: TEST_USERS.alice.displayName
  };
}

// Helper to assert Firebase operation results
export function assertFirebaseSuccess(result) {
  expect(result).toBeDefined();
  expect(result.success).toBe(true);
}

export function assertFirebaseError(error, expectedCode) {
  expect(error).toBeDefined();
  if (expectedCode) {
    expect(error.code).toBe(expectedCode);
  }
}

// Helper to mock Firebase timestamp
export function mockTimestamp() {
  return {
    toDate: () => new Date(),
    seconds: Math.floor(Date.now() / 1000),
    nanoseconds: 0
  };
}

// Helper to clean up test data
export async function cleanupTestData(context) {
  const db = context.firestore();
  
  // Delete all test collections
  const collections = ['users', 'channels', 'messages', 'directMessages'];
  
  for (const collectionName of collections) {
    const snapshot = await db.collection(collectionName).get();
    const batch = db.batch();
    
    snapshot.docs.forEach(doc => {
      batch.delete(doc.ref);
    });
    
    if (snapshot.docs.length > 0) {
      await batch.commit();
    }
  }
} 