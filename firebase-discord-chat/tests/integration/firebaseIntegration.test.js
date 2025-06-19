import { 
  TEST_USERS, 
  TEST_CHANNELS,
  getAuthenticatedContext,
  createTestUser,
  createTestChannel,
  createTestMessage,
  assertFirebaseSuccess,
  cleanupTestData
} from '../utils/testHelpers';

describe('Firebase Integration Tests', () => {
  let testEnv;
  let aliceContext;
  let bobContext;

  beforeAll(() => {
    testEnv = global.testEnv;
  });

  beforeEach(async () => {
    aliceContext = getAuthenticatedContext(testEnv, TEST_USERS.alice);
    bobContext = getAuthenticatedContext(testEnv, TEST_USERS.bob);
    
    // Create test users
    await createTestUser(aliceContext, TEST_USERS.alice);
    await createTestUser(bobContext, TEST_USERS.bob);
  });

  afterEach(async () => {
    await cleanupTestData(aliceContext);
  });

  describe('User Authentication Flow', () => {
    test('should complete full authentication workflow', async () => {
      const db = aliceContext.firestore();
      
      // Verify user was created
      const userDoc = await db.collection('users').doc(TEST_USERS.alice.uid).get();
      expect(userDoc.exists).toBe(true);
      expect(userDoc.data().email).toBe(TEST_USERS.alice.email);
      
      // Update user status
      await db.collection('users').doc(TEST_USERS.alice.uid).update({
        status: 'away',
        lastSeen: new Date()
      });
      
      // Verify status update
      const updatedDoc = await db.collection('users').doc(TEST_USERS.alice.uid).get();
      expect(updatedDoc.data().status).toBe('away');
    });

    test('should handle user profile updates', async () => {
      const db = aliceContext.firestore();
      
      // Update user profile
      await db.collection('users').doc(TEST_USERS.alice.uid).update({
        displayName: 'Alice Updated',
        bio: 'Updated bio',
        preferences: {
          theme: 'light',
          notifications: false
        }
      });
      
      // Verify profile update
      const userDoc = await db.collection('users').doc(TEST_USERS.alice.uid).get();
      const userData = userDoc.data();
      expect(userData.displayName).toBe('Alice Updated');
      expect(userData.bio).toBe('Updated bio');
      expect(userData.preferences.theme).toBe('light');
    });
  });

  describe('Channel and Message Integration', () => {
    test('should create channel and send messages', async () => {
      const db = aliceContext.firestore();
      
      // Create channel
      await createTestChannel(aliceContext, TEST_CHANNELS.general);
      
      // Verify channel creation
      const channelDoc = await db.collection('channels').doc(TEST_CHANNELS.general.id).get();
      expect(channelDoc.exists).toBe(true);
      expect(channelDoc.data().name).toBe(TEST_CHANNELS.general.name);
      
      // Send message to channel
      const messageId = await createTestMessage(aliceContext, TEST_CHANNELS.general.id, {
        content: 'Hello from integration test',
        authorId: TEST_USERS.alice.uid,
        authorName: TEST_USERS.alice.displayName
      });
      
      // Verify message creation
      const messageDoc = await db.collection('channels')
        .doc(TEST_CHANNELS.general.id)
        .collection('messages')
        .doc(messageId)
        .get();
      
      expect(messageDoc.exists).toBe(true);
      expect(messageDoc.data().content).toBe('Hello from integration test');
      expect(messageDoc.data().authorId).toBe(TEST_USERS.alice.uid);
      
      // Update channel message count
      await db.collection('channels').doc(TEST_CHANNELS.general.id).update({
        messageCount: 1,
        lastMessage: {
          content: 'Hello from integration test',
          authorId: TEST_USERS.alice.uid,
          timestamp: new Date()
        }
      });
      
      // Verify channel update
      const updatedChannelDoc = await db.collection('channels').doc(TEST_CHANNELS.general.id).get();
      expect(updatedChannelDoc.data().messageCount).toBe(1);
    });

    test('should handle private channel with members', async () => {
      const db = aliceContext.firestore();
      
      // Create private channel
      await createTestChannel(aliceContext, TEST_CHANNELS.private);
      
      // Verify channel creation with members
      const channelDoc = await db.collection('channels').doc(TEST_CHANNELS.private.id).get();
      expect(channelDoc.exists).toBe(true);
      expect(channelDoc.data().type).toBe('private');
      expect(channelDoc.data().members).toContain(TEST_USERS.alice.uid);
      expect(channelDoc.data().members).toContain(TEST_USERS.bob.uid);
      
      // Bob should be able to access the channel (member)
      const bobChannelDoc = await bobContext.firestore()
        .collection('channels')
        .doc(TEST_CHANNELS.private.id)
        .get();
      expect(bobChannelDoc.exists).toBe(true);
    });
  });

  describe('Direct Message Integration', () => {
    test('should create and manage direct message conversation', async () => {
      const db = aliceContext.firestore();
      
      // Create conversation ID (sorted user IDs)
      const participants = [TEST_USERS.alice.uid, TEST_USERS.bob.uid].sort();
      const conversationId = participants.join('_');
      
      // Create direct message conversation
      await db.collection('directMessages').doc(conversationId).set({
        participants,
        createdAt: new Date(),
        lastMessage: null
      });
      
      // Send direct message
      const messageRef = await db.collection('directMessages')
        .doc(conversationId)
        .collection('messages')
        .add({
          content: 'Private message from Alice',
          authorId: TEST_USERS.alice.uid,
          authorName: TEST_USERS.alice.displayName,
          timestamp: new Date(),
          edited: null,
          reactions: {},
          attachments: [],
          deleted: false
        });
      
      // Update conversation with last message
      await db.collection('directMessages').doc(conversationId).update({
        lastMessage: {
          content: 'Private message from Alice',
          authorId: TEST_USERS.alice.uid,
          timestamp: new Date()
        }
      });
      
      // Verify conversation and message
      const conversationDoc = await db.collection('directMessages').doc(conversationId).get();
      expect(conversationDoc.exists).toBe(true);
      expect(conversationDoc.data().participants).toEqual(participants);
      
      const messageDoc = await db.collection('directMessages')
        .doc(conversationId)
        .collection('messages')
        .doc(messageRef.id)
        .get();
      
      expect(messageDoc.exists).toBe(true);
      expect(messageDoc.data().content).toBe('Private message from Alice');
      
      // Bob should be able to access the conversation
      const bobConversationDoc = await bobContext.firestore()
        .collection('directMessages')
        .doc(conversationId)
        .get();
      expect(bobConversationDoc.exists).toBe(true);
    });
  });

  describe('Real-time Subscriptions', () => {
    test('should handle real-time message updates', async () => {
      const db = aliceContext.firestore();
      
      // Create channel
      await createTestChannel(aliceContext, TEST_CHANNELS.general);
      
      // Set up real-time listener
      const messages = [];
      const unsubscribe = db.collection('channels')
        .doc(TEST_CHANNELS.general.id)
        .collection('messages')
        .orderBy('timestamp', 'desc')
        .limit(10)
        .onSnapshot((snapshot) => {
          messages.length = 0; // Clear array
          snapshot.docs.forEach(doc => {
            messages.push({ id: doc.id, ...doc.data() });
          });
        });
      
      // Wait for initial snapshot
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Add message
      await createTestMessage(aliceContext, TEST_CHANNELS.general.id, {
        content: 'Real-time test message',
        authorId: TEST_USERS.alice.uid,
        authorName: TEST_USERS.alice.displayName
      });
      
      // Wait for real-time update
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // Verify real-time update
      expect(messages).toHaveLength(1);
      expect(messages[0].content).toBe('Real-time test message');
      
      // Cleanup
      unsubscribe();
    });
  });

  describe('Message Reactions and Editing', () => {
    test('should handle message reactions', async () => {
      const db = aliceContext.firestore();
      
      // Create channel and message
      await createTestChannel(aliceContext, TEST_CHANNELS.general);
      const messageId = await createTestMessage(aliceContext, TEST_CHANNELS.general.id, {
        content: 'Message to react to',
        authorId: TEST_USERS.alice.uid,
        authorName: TEST_USERS.alice.displayName
      });
      
      // Add reaction
      const messageRef = db.collection('channels')
        .doc(TEST_CHANNELS.general.id)
        .collection('messages')
        .doc(messageId);
      
      await messageRef.update({
        [`reactions.👍.${TEST_USERS.alice.uid}`]: true,
        [`reactions.👍.count`]: 1
      });
      
      // Verify reaction
      const messageDoc = await messageRef.get();
      const messageData = messageDoc.data();
      expect(messageData.reactions['👍'][TEST_USERS.alice.uid]).toBe(true);
      expect(messageData.reactions['👍'].count).toBe(1);
      
      // Add another user's reaction
      await messageRef.update({
        [`reactions.👍.${TEST_USERS.bob.uid}`]: true,
        [`reactions.👍.count`]: 2
      });
      
      // Verify multiple reactions
      const updatedMessageDoc = await messageRef.get();
      const updatedData = updatedMessageDoc.data();
      expect(updatedData.reactions['👍'].count).toBe(2);
    });

    test('should handle message editing', async () => {
      const db = aliceContext.firestore();
      
      // Create channel and message
      await createTestChannel(aliceContext, TEST_CHANNELS.general);
      const messageId = await createTestMessage(aliceContext, TEST_CHANNELS.general.id, {
        content: 'Original message',
        authorId: TEST_USERS.alice.uid,
        authorName: TEST_USERS.alice.displayName
      });
      
      // Edit message
      const messageRef = db.collection('channels')
        .doc(TEST_CHANNELS.general.id)
        .collection('messages')
        .doc(messageId);
      
      await messageRef.update({
        content: 'Edited message',
        edited: new Date()
      });
      
      // Verify edit
      const messageDoc = await messageRef.get();
      const messageData = messageDoc.data();
      expect(messageData.content).toBe('Edited message');
      expect(messageData.edited).toBeDefined();
    });
  });

  describe('Security Rules Integration', () => {
    test('should enforce user authentication for writing', async () => {
      const unauthenticatedContext = testEnv.unauthenticatedContext();
      const db = unauthenticatedContext.firestore();
      
      // Attempt to create user document without authentication
      await expect(
        db.collection('users').doc('test-user').set({
          email: 'test@example.com',
          displayName: 'Test User'
        })
      ).rejects.toThrow();
    });

    test('should allow authenticated users to read public channels', async () => {
      const db = aliceContext.firestore();
      
      // Create public channel
      await createTestChannel(aliceContext, TEST_CHANNELS.general);
      
      // Bob should be able to read public channel
      const bobDb = bobContext.firestore();
      const channelDoc = await bobDb.collection('channels').doc(TEST_CHANNELS.general.id).get();
      
      expect(channelDoc.exists).toBe(true);
      expect(channelDoc.data().type).toBe('public');
    });

    test('should restrict access to private channels', async () => {
      const db = aliceContext.firestore();
      
      // Create private channel with specific members
      await createTestChannel(aliceContext, TEST_CHANNELS.private);
      
      // Charlie (not a member) should not be able to access
      const charlieContext = getAuthenticatedContext(testEnv, TEST_USERS.charlie);
      const charlieDb = charlieContext.firestore();
      
      // This should be restricted by security rules
      await expect(
        charlieDb.collection('channels')
          .doc(TEST_CHANNELS.private.id)
          .collection('messages')
          .add({
            content: 'Unauthorized message',
            authorId: TEST_USERS.charlie.uid
          })
      ).rejects.toThrow();
    });
  });

  describe('Data Consistency', () => {
    test('should maintain data consistency across operations', async () => {
      const db = aliceContext.firestore();
      
      // Create channel
      await createTestChannel(aliceContext, TEST_CHANNELS.general);
      
      // Send multiple messages
      const messagePromises = [];
      for (let i = 0; i < 5; i++) {
        messagePromises.push(
          createTestMessage(aliceContext, TEST_CHANNELS.general.id, {
            content: `Message ${i + 1}`,
            authorId: TEST_USERS.alice.uid,
            authorName: TEST_USERS.alice.displayName
          })
        );
      }
      
      await Promise.all(messagePromises);
      
      // Update channel message count
      await db.collection('channels').doc(TEST_CHANNELS.general.id).update({
        messageCount: 5
      });
      
      // Verify all messages exist
      const messagesSnapshot = await db.collection('channels')
        .doc(TEST_CHANNELS.general.id)
        .collection('messages')
        .get();
      
      expect(messagesSnapshot.size).toBe(5);
      
      // Verify channel message count
      const channelDoc = await db.collection('channels').doc(TEST_CHANNELS.general.id).get();
      expect(channelDoc.data().messageCount).toBe(5);
    });
  });
}); 