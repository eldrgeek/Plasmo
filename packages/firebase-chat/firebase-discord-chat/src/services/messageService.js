import { 
  collection, 
  addDoc, 
  query, 
  orderBy, 
  limit, 
  onSnapshot,
  serverTimestamp,
  doc,
  updateDoc,
  deleteDoc,
  where,
  getDocs
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const messageService = {
  // Send message to channel
  async sendMessage(channelId, content, replyTo = null) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messagesRef = collection(db, 'channels', channelId, 'messages');
      const messageData = {
        content,
        authorId: auth.currentUser.uid,
        authorName: auth.currentUser.displayName || 'Anonymous',
        timestamp: serverTimestamp(),
        reactions: {},
        attachments: []
      };
      
      if (replyTo) {
        messageData.replyTo = replyTo;
      }
      
      await addDoc(messagesRef, messageData);
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Send direct message
  async sendDirectMessage(conversationId, content) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messagesRef = collection(db, 'directMessages', conversationId, 'messages');
      await addDoc(messagesRef, {
        content,
        authorId: auth.currentUser.uid,
        authorName: auth.currentUser.displayName || 'Anonymous',
        timestamp: serverTimestamp(),
        reactions: {},
        attachments: []
      });
    } catch (error) {
      console.error('Error sending direct message:', error);
      throw error;
    }
  },

  // Listen to messages in real-time
  subscribeToMessages(channelId, callback) {
    const messagesRef = collection(db, 'channels', channelId, 'messages');
    const q = query(messagesRef, orderBy('timestamp', 'desc'), limit(50));
    
    return onSnapshot(q, (snapshot) => {
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        timestamp: doc.data().timestamp?.toDate() || new Date()
      }));
      callback(messages.reverse());
    });
  },

  // Listen to direct messages in real-time
  subscribeToDirectMessages(conversationId, callback) {
    const messagesRef = collection(db, 'directMessages', conversationId, 'messages');
    const q = query(messagesRef, orderBy('timestamp', 'desc'), limit(50));
    
    return onSnapshot(q, (snapshot) => {
      const messages = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        timestamp: doc.data().timestamp?.toDate() || new Date()
      }));
      callback(messages.reverse());
    });
  },

  // Edit message
  async editMessage(channelId, messageId, newContent) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageRef = doc(db, 'channels', channelId, 'messages', messageId);
      await updateDoc(messageRef, {
        content: newContent,
        edited: serverTimestamp()
      });
    } catch (error) {
      console.error('Error editing message:', error);
      throw error;
    }
  },

  // Delete message
  async deleteMessage(channelId, messageId) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageRef = doc(db, 'channels', channelId, 'messages', messageId);
      await deleteDoc(messageRef);
    } catch (error) {
      console.error('Error deleting message:', error);
      throw error;
    }
  },

  // Add reaction to message
  async addReaction(channelId, messageId, emoji) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const messageRef = doc(db, 'channels', channelId, 'messages', messageId);
      const reactionPath = `reactions.${emoji}`;
      
      // Get current reactions to check if user already reacted
      const messageDoc = await getDocs(query(collection(db, 'channels', channelId, 'messages'), where('__name__', '==', messageId)));
      const currentReactions = messageDoc.docs[0]?.data()?.reactions || {};
      const currentEmojiReactions = currentReactions[emoji] || [];
      
      let updatedReactions;
      if (currentEmojiReactions.includes(auth.currentUser.uid)) {
        // Remove reaction
        updatedReactions = currentEmojiReactions.filter(uid => uid !== auth.currentUser.uid);
      } else {
        // Add reaction
        updatedReactions = [...currentEmojiReactions, auth.currentUser.uid];
      }
      
      await updateDoc(messageRef, {
        [reactionPath]: updatedReactions
      });
    } catch (error) {
      console.error('Error adding reaction:', error);
      throw error;
    }
  },

  // Search messages
  async searchMessages(channelId, searchTerm) {
    try {
      const messagesRef = collection(db, 'channels', channelId, 'messages');
      const q = query(messagesRef, orderBy('timestamp', 'desc'), limit(100));
      
      const snapshot = await getDocs(q);
      const messages = snapshot.docs
        .map(doc => ({ id: doc.id, ...doc.data() }))
        .filter(message => 
          message.content.toLowerCase().includes(searchTerm.toLowerCase())
        );
      
      return messages;
    } catch (error) {
      console.error('Error searching messages:', error);
      throw error;
    }
  }
}; 