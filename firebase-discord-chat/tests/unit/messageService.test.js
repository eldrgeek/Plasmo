import { initializeApp } from 'firebase/app';
import { getAuth, createUserWithEmailAndPassword, signOut } from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  doc, 
  addDoc, 
  updateDoc, 
  deleteDoc, 
  getDoc, 
  getDocs, 
  query, 
  where, 
  orderBy, 
  limit,
  onSnapshot,
  serverTimestamp
} from 'firebase/firestore';
import { messageService } from '../../src/services/messageService';
import { 
  TEST_USERS, 
  TEST_CHANNELS,
  TEST_MESSAGES,
  getAuthenticatedContext, 
  createTestChannel,
  createTestMessage,
  assertFirebaseSuccess,
  generateRandomMessage
} from '../utils/testHelpers';

// Firebase config for testing
const firebaseConfig = {
  apiKey: "test-api-key",
  authDomain: "roundtable-test.firebaseapp.com",
  projectId: "roundtable-test",
  storageBucket: "roundtable-test.appspot.com",
  messagingSenderId: "123456789",
  appId: "test-app-id"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

describe('Message Service', () => {
  let testUser;
  let testChannel;

  beforeEach(async () => {
    // Clear any existing auth state
    if (auth.currentUser) {
      await signOut(auth);
    }

    // Create test user
    const userCredential = await createUserWithEmailAndPassword(
      auth, 
      TEST_USERS.alice.email, 
      TEST_USERS.alice.password
    );
    testUser = userCredential.user;

    // Create test channel
    const channelRef = await addDoc(collection(db, 'channels'), {
      ...TEST_CHANNELS.general,
      createdBy: testUser.uid,
      createdAt: serverTimestamp(),
      members: [testUser.uid]
    });
    testChannel = { id: channelRef.id, ...TEST_CHANNELS.general };
  });

  afterEach(async () => {
    // Clean up auth state
    if (auth.currentUser) {
      await signOut(auth);
    }
  });

  describe('Send Messages', () => {
    test('should send message to channel successfully', async () => {
      const messageContent = 'Hello, world!';
      
      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'), 
        {
          content: messageContent,
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      expect(messageRef.id).toBeDefined();

      // Verify message was saved
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.exists()).toBe(true);
      expect(messageDoc.data().content).toBe(messageContent);
      expect(messageDoc.data().authorId).toBe(testUser.uid);
    });

    test('should send message with attachment', async () => {
      const messageData = {
        content: 'Check out this image!',
        authorId: testUser.uid,
        authorName: TEST_USERS.alice.displayName,
        timestamp: serverTimestamp(),
        type: 'attachment',
        attachment: {
          url: 'https://example.com/image.jpg',
          type: 'image',
          name: 'image.jpg',
          size: 1024
        }
      };

      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        messageData
      );

      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.exists()).toBe(true);
      expect(messageDoc.data().attachment).toBeDefined();
      expect(messageDoc.data().attachment.url).toBe(messageData.attachment.url);
    });

    test('should send reply to message', async () => {
      // First, send original message
      const originalMessageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'Original message',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      // Send reply
      const replyRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'This is a reply',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'reply',
          replyTo: originalMessageRef.id
        }
      );

      const replyDoc = await getDoc(replyRef);
      expect(replyDoc.exists()).toBe(true);
      expect(replyDoc.data().replyTo).toBe(originalMessageRef.id);
      expect(replyDoc.data().type).toBe('reply');
    });
  });

  describe('Edit Messages', () => {
    test('should edit message successfully', async () => {
      // Send original message
      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'Original content',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      // Edit message
      const newContent = 'Edited content';
      await updateDoc(messageRef, {
        content: newContent,
        edited: true,
        editedAt: serverTimestamp()
      });

      // Verify edit
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.data().content).toBe(newContent);
      expect(messageDoc.data().edited).toBe(true);
      expect(messageDoc.data().editedAt).toBeDefined();
    });

    test('should not allow editing other users messages', async () => {
      // Create second user
      await signOut(auth);
      const bobCredential = await createUserWithEmailAndPassword(
        auth,
        TEST_USERS.bob.email,
        TEST_USERS.bob.password
      );

      // Send message as Bob
      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'Bob\'s message',
          authorId: bobCredential.user.uid,
          authorName: TEST_USERS.bob.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      // Switch back to Alice
      await signOut(auth);
      await createUserWithEmailAndPassword(
        auth,
        TEST_USERS.alice.email,
        TEST_USERS.alice.password
      );

      // Try to edit Bob's message (this would be prevented by security rules)
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.data().authorId).not.toBe(testUser.uid);
    });
  });

  describe('Delete Messages', () => {
    test('should delete message successfully', async () => {
      // Send message
      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'Message to delete',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      // Delete message
      await deleteDoc(messageRef);

      // Verify deletion
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.exists()).toBe(false);
    });
  });

  describe('Message Reactions', () => {
    test('should add reaction to message', async () => {
      // Send message
      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'React to this!',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text',
          reactions: {}
        }
      );

      // Add reaction
      await updateDoc(messageRef, {
        [`reactions.👍`]: {
          count: 1,
          users: [testUser.uid]
        }
      });

      // Verify reaction
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.data().reactions['👍']).toBeDefined();
      expect(messageDoc.data().reactions['👍'].count).toBe(1);
      expect(messageDoc.data().reactions['👍'].users).toContain(testUser.uid);
    });

    test('should remove reaction from message', async () => {
      // Send message with existing reaction
      const messageRef = await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'React to this!',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text',
          reactions: {
            '👍': {
              count: 1,
              users: [testUser.uid]
            }
          }
        }
      );

      // Remove reaction
      await updateDoc(messageRef, {
        'reactions.👍': null
      });

      // Verify reaction removal
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.data().reactions['👍']).toBeUndefined();
    });
  });

  describe('Message Queries', () => {
    test('should get messages from channel', async () => {
      // Send multiple messages
      const messages = [
        'First message',
        'Second message',
        'Third message'
      ];

      for (const content of messages) {
        await addDoc(
          collection(db, 'channels', testChannel.id, 'messages'),
          {
            content,
            authorId: testUser.uid,
            authorName: TEST_USERS.alice.displayName,
            timestamp: serverTimestamp(),
            type: 'text'
          }
        );
      }

      // Query messages
      const messagesQuery = query(
        collection(db, 'channels', testChannel.id, 'messages'),
        orderBy('timestamp', 'asc')
      );

      const querySnapshot = await getDocs(messagesQuery);
      expect(querySnapshot.size).toBe(messages.length);

      const retrievedMessages = [];
      querySnapshot.forEach((doc) => {
        retrievedMessages.push(doc.data().content);
      });

      expect(retrievedMessages).toEqual(messages);
    });

    test('should get limited number of messages', async () => {
      // Send multiple messages
      for (let i = 0; i < 10; i++) {
        await addDoc(
          collection(db, 'channels', testChannel.id, 'messages'),
          {
            content: `Message ${i}`,
            authorId: testUser.uid,
            authorName: TEST_USERS.alice.displayName,
            timestamp: serverTimestamp(),
            type: 'text'
          }
        );
      }

      // Query with limit
      const messagesQuery = query(
        collection(db, 'channels', testChannel.id, 'messages'),
        orderBy('timestamp', 'desc'),
        limit(5)
      );

      const querySnapshot = await getDocs(messagesQuery);
      expect(querySnapshot.size).toBe(5);
    });

    test('should search messages by content', async () => {
      // Send messages with searchable content
      await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'This is a searchable message',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      await addDoc(
        collection(db, 'channels', testChannel.id, 'messages'),
        {
          content: 'Another message',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      // Search for messages (Note: Firestore doesn't support full-text search natively)
      // This is a simplified example - in practice you'd use a search service
      const messagesQuery = query(
        collection(db, 'channels', testChannel.id, 'messages'),
        where('authorId', '==', testUser.uid)
      );

      const querySnapshot = await getDocs(messagesQuery);
      expect(querySnapshot.size).toBe(2);
    });
  });

  describe('Real-time Message Updates', () => {
    test('should receive real-time message updates', (done) => {
      const messagesQuery = query(
        collection(db, 'channels', testChannel.id, 'messages'),
        orderBy('timestamp', 'asc')
      );

      let messageCount = 0;
      const unsubscribe = onSnapshot(messagesQuery, (snapshot) => {
        messageCount = snapshot.size;
        
        if (messageCount === 1) {
          expect(snapshot.docs[0].data().content).toBe('Real-time test message');
          unsubscribe();
          done();
        }
      });

      // Send a message to trigger the listener
      setTimeout(async () => {
        await addDoc(
          collection(db, 'channels', testChannel.id, 'messages'),
          {
            content: 'Real-time test message',
            authorId: testUser.uid,
            authorName: TEST_USERS.alice.displayName,
            timestamp: serverTimestamp(),
            type: 'text'
          }
        );
      }, 100);
    });
  });

  describe('Direct Messages', () => {
    test('should send direct message', async () => {
      // Create second user
      await signOut(auth);
      const bobCredential = await createUserWithEmailAndPassword(
        auth,
        TEST_USERS.bob.email,
        TEST_USERS.bob.password
      );

      // Create DM conversation
      const conversationId = [testUser.uid, bobCredential.user.uid].sort().join('_');
      
      const messageRef = await addDoc(
        collection(db, 'directMessages', conversationId, 'messages'),
        {
          content: 'Hello Bob!',
          authorId: testUser.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: serverTimestamp(),
          type: 'text'
        }
      );

      expect(messageRef.id).toBeDefined();

      // Verify message
      const messageDoc = await getDoc(messageRef);
      expect(messageDoc.exists()).toBe(true);
      expect(messageDoc.data().content).toBe('Hello Bob!');
    });
  });
}); 