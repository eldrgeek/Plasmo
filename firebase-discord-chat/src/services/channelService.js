import { 
  collection, 
  addDoc, 
  query, 
  orderBy, 
  onSnapshot,
  serverTimestamp,
  doc,
  updateDoc,
  deleteDoc,
  getDocs,
  where,
  arrayUnion,
  arrayRemove,
  getDoc,
  setDoc
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const channelService = {
  // Create new channel
  async createChannel(name, description = '', type = 'public') {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelsRef = collection(db, 'channels');
      const channelData = {
        name,
        description,
        type,
        createdBy: auth.currentUser.uid,
        createdAt: serverTimestamp(),
        members: [auth.currentUser.uid],
        lastMessage: null
      };
      
      const docRef = await addDoc(channelsRef, channelData);
      return docRef.id;
    } catch (error) {
      console.error('Error creating channel:', error);
      throw error;
    }
  },

  // Get all public channels
  async getPublicChannels() {
    try {
      const channelsRef = collection(db, 'channels');
      const q = query(channelsRef, where('type', '==', 'public'), orderBy('createdAt', 'desc'));
      const snapshot = await getDocs(q);
      
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt?.toDate() || new Date()
      }));
    } catch (error) {
      console.error('Error getting public channels:', error);
      throw error;
    }
  },

  // Listen to channels in real-time
  subscribeToChannels(callback) {
    const channelsRef = collection(db, 'channels');
    const q = query(channelsRef, orderBy('createdAt', 'desc'));
    
    return onSnapshot(q, (snapshot) => {
      const channels = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt?.toDate() || new Date()
      }));
      callback(channels);
    });
  },

  // Join channel
  async joinChannel(channelId) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelRef = doc(db, 'channels', channelId);
      await updateDoc(channelRef, {
        members: arrayUnion(auth.currentUser.uid)
      });
    } catch (error) {
      console.error('Error joining channel:', error);
      throw error;
    }
  },

  // Leave channel
  async leaveChannel(channelId) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelRef = doc(db, 'channels', channelId);
      await updateDoc(channelRef, {
        members: arrayRemove(auth.currentUser.uid)
      });
    } catch (error) {
      console.error('Error leaving channel:', error);
      throw error;
    }
  },

  // Update channel
  async updateChannel(channelId, updates) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelRef = doc(db, 'channels', channelId);
      await updateDoc(channelRef, updates);
    } catch (error) {
      console.error('Error updating channel:', error);
      throw error;
    }
  },

  // Delete channel
  async deleteChannel(channelId) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelRef = doc(db, 'channels', channelId);
      await deleteDoc(channelRef);
    } catch (error) {
      console.error('Error deleting channel:', error);
      throw error;
    }
  },

  // Create or get direct message conversation
  async createOrGetDirectMessage(otherUserId) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const participants = [auth.currentUser.uid, otherUserId].sort();
      const conversationId = participants.join('_');
      
      const conversationRef = doc(db, 'directMessages', conversationId);
      const conversationDoc = await getDoc(conversationRef);
      
      if (!conversationDoc.exists()) {
        // Create new conversation
        await setDoc(conversationRef, {
          id: conversationId,
          participants,
          createdAt: serverTimestamp(),
          lastMessage: null
        });
      }
      
      return conversationId;
    } catch (error) {
      console.error('Error creating/getting direct message:', error);
      throw error;
    }
  },

  // Get user's direct message conversations
  async getDirectMessageConversations() {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const dmRef = collection(db, 'directMessages');
      const q = query(dmRef, where('participants', 'array-contains', auth.currentUser.uid));
      const snapshot = await getDocs(q);
      
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt?.toDate() || new Date()
      }));
    } catch (error) {
      console.error('Error getting direct message conversations:', error);
      throw error;
    }
  },

  // Listen to direct message conversations
  subscribeToDirectMessageConversations(callback) {
    if (!auth.currentUser) return () => {};
    
    const dmRef = collection(db, 'directMessages');
    const q = query(dmRef, where('participants', 'array-contains', auth.currentUser.uid));
    
    return onSnapshot(q, (snapshot) => {
      const conversations = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt?.toDate() || new Date()
      }));
      callback(conversations);
    });
  },

  // Get channel members
  async getChannelMembers(channelId) {
    try {
      const channelRef = doc(db, 'channels', channelId);
      const channelDoc = await getDoc(channelRef);
      
      if (!channelDoc.exists()) return [];
      
      const memberIds = channelDoc.data().members || [];
      const memberPromises = memberIds.map(async (memberId) => {
        const userDoc = await getDoc(doc(db, 'users', memberId));
        return userDoc.exists() ? { id: memberId, ...userDoc.data() } : null;
      });
      
      const members = await Promise.all(memberPromises);
      return members.filter(member => member !== null);
    } catch (error) {
      console.error('Error getting channel members:', error);
      throw error;
    }
  },

  // Update last message in channel
  async updateLastMessage(channelId, messageContent, authorId) {
    try {
      const channelRef = doc(db, 'channels', channelId);
      await updateDoc(channelRef, {
        lastMessage: {
          content: messageContent,
          authorId,
          timestamp: serverTimestamp()
        }
      });
    } catch (error) {
      console.error('Error updating last message:', error);
      throw error;
    }
  }
}; 