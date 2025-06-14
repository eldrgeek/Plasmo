import { 
  collection, 
  doc,
  addDoc, 
  updateDoc,
  deleteDoc,
  getDoc,
  getDocs,
  setDoc,
  query, 
  where,
  orderBy, 
  limit,
  startAfter,
  onSnapshot,
  serverTimestamp,
  increment
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';
import { channelService } from './channelService';

export const messageService = {
  // Send message to channel
  async sendMessage(channelId, content, replyTo = null, attachments = []) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageData = {
        content,
        authorId: auth.currentUser.uid,
        authorName: auth.currentUser.displayName || 'Anonymous',
        timestamp: serverTimestamp(),
        edited: null,
        replyTo,
        reactions: {},
        attachments,
        deleted: false
      };
      
      const messagesRef = collection(db, 'channels', channelId, 'messages');
      const docRef = await addDoc(messagesRef, messageData);
      
      // Update channel's last message and message count
      await channelService.updateLastMessage(channelId, messageData);
      await updateDoc(doc(db, 'channels', channelId), {
        messageCount: increment(1)
      });
      
      return { id: docRef.id, ...messageData };
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },
  
  // Send direct message
  async sendDirectMessage(recipientId, content, attachments = []) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      // Create or get conversation ID (sorted user IDs)
      const participants = [auth.currentUser.uid, recipientId].sort();
      const conversationId = participants.join('_');
      
      // Check if conversation exists, create if not
      const conversationRef = doc(db, 'directMessages', conversationId);
      const conversationDoc = await getDoc(conversationRef);
      
      if (!conversationDoc.exists()) {
        await setDoc(conversationRef, {
          participants,
          createdAt: serverTimestamp(),
          lastMessage: null
        });
      }
      
      // Send message
      const messageData = {
        content,
        authorId: auth.currentUser.uid,
        authorName: auth.currentUser.displayName || 'Anonymous',
        timestamp: serverTimestamp(),
        edited: null,
        reactions: {},
        attachments,
        deleted: false
      };
      
      const messagesRef = collection(db, 'directMessages', conversationId, 'messages');
      const docRef = await addDoc(messagesRef, messageData);
      
      // Update conversation's last message
      await updateDoc(conversationRef, {
        lastMessage: {
          content: messageData.content,
          authorId: messageData.authorId,
          timestamp: messageData.timestamp
        }
      });
      
      return { id: docRef.id, ...messageData };
    } catch (error) {
      console.error('Error sending direct message:', error);
      throw error;
    }
  },
  
  // Get messages with pagination
  async getMessages(channelId, limitCount = 50, lastMessage = null) {
    try {
      const messagesRef = collection(db, 'channels', channelId, 'messages');
      let q = query(
        messagesRef, 
        where('deleted', '==', false),
        orderBy('timestamp', 'desc'), 
        limit(limitCount)
      );
      
      if (lastMessage) {
        q = query(
          messagesRef,
          where('deleted', '==', false),
          orderBy('timestamp', 'desc'),
          startAfter(lastMessage.timestamp),
          limit(limitCount)
        );
      }
      
      const snapshot = await getDocs(q);
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return messages.reverse(); // Return in chronological order
    } catch (error) {
      console.error('Error getting messages:', error);
      throw error;
    }
  },
  
  // Subscribe to messages in real-time
  subscribeToMessages(channelId, callback, limitCount = 50) {
    const messagesRef = collection(db, 'channels', channelId, 'messages');
    const q = query(
      messagesRef, 
      where('deleted', '==', false),
      orderBy('timestamp', 'desc'), 
      limit(limitCount)
    );
    
    return onSnapshot(q, (snapshot) => {
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      callback(messages.reverse()); // Return in chronological order
    });
  },
  
  // Subscribe to direct messages
  subscribeToDirectMessages(conversationId, callback, limitCount = 50) {
    const messagesRef = collection(db, 'directMessages', conversationId, 'messages');
    const q = query(
      messagesRef,
      where('deleted', '==', false),
      orderBy('timestamp', 'desc'),
      limit(limitCount)
    );
    
    return onSnapshot(q, (snapshot) => {
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      callback(messages.reverse());
    });
  },
  
  // Get user's direct message conversations
  async getDirectMessageConversations(userId) {
    try {
      const q = query(
        collection(db, 'directMessages'),
        where('participants', 'array-contains', userId),
        orderBy('lastMessage.timestamp', 'desc')
      );
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error getting DM conversations:', error);
      throw error;
    }
  },
  
  // Subscribe to DM conversations
  subscribeToDirectMessageConversations(userId, callback) {
    const q = query(
      collection(db, 'directMessages'),
      where('participants', 'array-contains', userId),
      orderBy('lastMessage.timestamp', 'desc')
    );
    
    return onSnapshot(q, (snapshot) => {
      const conversations = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      callback(conversations);
    });
  },
  
  // Edit message
  async editMessage(channelId, messageId, newContent, isDM = false) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageRef = isDM 
        ? doc(db, 'directMessages', channelId, 'messages', messageId)
        : doc(db, 'channels', channelId, 'messages', messageId);
      
      const messageDoc = await getDoc(messageRef);
      if (!messageDoc.exists()) {
        throw new Error('Message not found');
      }
      
      const messageData = messageDoc.data();
      if (messageData.authorId !== auth.currentUser.uid) {
        throw new Error('Can only edit your own messages');
      }
      
      await updateDoc(messageRef, {
        content: newContent,
        edited: serverTimestamp()
      });
    } catch (error) {
      console.error('Error editing message:', error);
      throw error;
    }
  },
  
  // Delete message (soft delete)
  async deleteMessage(channelId, messageId, isDM = false) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageRef = isDM 
        ? doc(db, 'directMessages', channelId, 'messages', messageId)
        : doc(db, 'channels', channelId, 'messages', messageId);
      
      const messageDoc = await getDoc(messageRef);
      if (!messageDoc.exists()) {
        throw new Error('Message not found');
      }
      
      const messageData = messageDoc.data();
      if (messageData.authorId !== auth.currentUser.uid) {
        throw new Error('Can only delete your own messages');
      }
      
      await updateDoc(messageRef, {
        deleted: true,
        deletedAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Error deleting message:', error);
      throw error;
    }
  },
  
  // Add reaction to message
  async addReaction(channelId, messageId, emoji, isDM = false) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageRef = isDM 
        ? doc(db, 'directMessages', channelId, 'messages', messageId)
        : doc(db, 'channels', channelId, 'messages', messageId);
      
      const messageDoc = await getDoc(messageRef);
      if (!messageDoc.exists()) {
        throw new Error('Message not found');
      }
      
      const messageData = messageDoc.data();
      const reactions = messageData.reactions || {};
      const emojiReactions = reactions[emoji] || [];
      
      // Toggle reaction (add if not present, remove if present)
      const userIndex = emojiReactions.indexOf(auth.currentUser.uid);
      if (userIndex === -1) {
        emojiReactions.push(auth.currentUser.uid);
      } else {
        emojiReactions.splice(userIndex, 1);
      }
      
      // Update reactions object
      if (emojiReactions.length === 0) {
        delete reactions[emoji];
      } else {
        reactions[emoji] = emojiReactions;
      }
      
      await updateDoc(messageRef, { reactions });
    } catch (error) {
      console.error('Error adding reaction:', error);
      throw error;
    }
  },
  
  // Search messages
  async searchMessages(channelId, searchTerm, isDM = false) {
    try {
      const messagesRef = isDM 
        ? collection(db, 'directMessages', channelId, 'messages')
        : collection(db, 'channels', channelId, 'messages');
      
      // Note: Firestore doesn't support full-text search natively
      // This is a basic implementation - consider using Algolia or similar for production
      const q = query(
        messagesRef,
        where('deleted', '==', false),
        orderBy('timestamp', 'desc'),
        limit(100)
      );
      
      const snapshot = await getDocs(q);
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      // Client-side filtering (not ideal for large datasets)
      return messages.filter(message => 
        message.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    } catch (error) {
      console.error('Error searching messages:', error);
      throw error;
    }
  },
  
  // Get message by ID
  async getMessage(channelId, messageId, isDM = false) {
    try {
      const messageRef = isDM 
        ? doc(db, 'directMessages', channelId, 'messages', messageId)
        : doc(db, 'channels', channelId, 'messages', messageId);
      
      const messageDoc = await getDoc(messageRef);
      if (messageDoc.exists()) {
        return { id: messageDoc.id, ...messageDoc.data() };
      } else {
        throw new Error('Message not found');
      }
    } catch (error) {
      console.error('Error getting message:', error);
      throw error;
    }
  }
}; 