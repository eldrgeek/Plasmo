import { 
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
  onSnapshot,
  serverTimestamp,
  arrayUnion,
  arrayRemove
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const channelService = {
  // Create a new channel
  async createChannel(name, description = '', type = 'public', members = []) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelData = {
        name,
        description,
        type,
        createdBy: auth.currentUser.uid,
        createdAt: serverTimestamp(),
        members: type === 'private' ? [auth.currentUser.uid, ...members] : [],
        lastMessage: null,
        messageCount: 0
      };
      
      const docRef = await addDoc(collection(db, 'channels'), channelData);
      return { id: docRef.id, ...channelData };
    } catch (error) {
      console.error('Error creating channel:', error);
      throw error;
    }
  },
  
  // Get all public channels
  async getPublicChannels() {
    try {
      const q = query(
        collection(db, 'channels'),
        where('type', '==', 'public'),
        orderBy('createdAt', 'desc')
      );
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error getting public channels:', error);
      throw error;
    }
  },
  
  // Get user's channels (public + private channels they're members of)
  async getUserChannels(userId) {
    try {
      const publicQuery = query(
        collection(db, 'channels'),
        where('type', '==', 'public'),
        orderBy('createdAt', 'desc')
      );
      
      const privateQuery = query(
        collection(db, 'channels'),
        where('members', 'array-contains', userId),
        orderBy('createdAt', 'desc')
      );
      
      const [publicSnapshot, privateSnapshot] = await Promise.all([
        getDocs(publicQuery),
        getDocs(privateQuery)
      ]);
      
      const publicChannels = publicSnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      const privateChannels = privateSnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      // Combine and deduplicate
      const allChannels = [...publicChannels];
      privateChannels.forEach(privateChannel => {
        if (!allChannels.find(channel => channel.id === privateChannel.id)) {
          allChannels.push(privateChannel);
        }
      });
      
      return allChannels.sort((a, b) => b.createdAt - a.createdAt);
    } catch (error) {
      console.error('Error getting user channels:', error);
      throw error;
    }
  },
  
  // Subscribe to user's channels in real-time
  subscribeToUserChannels(userId, callback) {
    const publicQuery = query(
      collection(db, 'channels'),
      where('type', '==', 'public'),
      orderBy('createdAt', 'desc')
    );
    
    const privateQuery = query(
      collection(db, 'channels'),
      where('members', 'array-contains', userId),
      orderBy('createdAt', 'desc')
    );
    
    let publicChannels = [];
    let privateChannels = [];
    
    const updateChannels = () => {
      const allChannels = [...publicChannels];
      privateChannels.forEach(privateChannel => {
        if (!allChannels.find(channel => channel.id === privateChannel.id)) {
          allChannels.push(privateChannel);
        }
      });
      callback(allChannels.sort((a, b) => b.createdAt - a.createdAt));
    };
    
    const unsubscribePublic = onSnapshot(publicQuery, (snapshot) => {
      publicChannels = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      updateChannels();
    });
    
    const unsubscribePrivate = onSnapshot(privateQuery, (snapshot) => {
      privateChannels = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      updateChannels();
    });
    
    return () => {
      unsubscribePublic();
      unsubscribePrivate();
    };
  },
  
  // Get channel by ID
  async getChannel(channelId) {
    try {
      const docRef = doc(db, 'channels', channelId);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
      } else {
        throw new Error('Channel not found');
      }
    } catch (error) {
      console.error('Error getting channel:', error);
      throw error;
    }
  },
  
  // Subscribe to channel changes
  subscribeToChannel(channelId, callback) {
    return onSnapshot(doc(db, 'channels', channelId), (doc) => {
      if (doc.exists()) {
        callback({ id: doc.id, ...doc.data() });
      }
    });
  },
  
  // Join a private channel
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
  
  // Leave a private channel
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
  
  // Update channel info
  async updateChannel(channelId, updates) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelRef = doc(db, 'channels', channelId);
      await updateDoc(channelRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Error updating channel:', error);
      throw error;
    }
  },
  
  // Delete channel (only by creator)
  async deleteChannel(channelId) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const channelRef = doc(db, 'channels', channelId);
      const channelDoc = await getDoc(channelRef);
      
      if (!channelDoc.exists()) {
        throw new Error('Channel not found');
      }
      
      const channelData = channelDoc.data();
      if (channelData.createdBy !== auth.currentUser.uid) {
        throw new Error('Only channel creator can delete the channel');
      }
      
      await deleteDoc(channelRef);
    } catch (error) {
      console.error('Error deleting channel:', error);
      throw error;
    }
  },
  
  // Update last message info
  async updateLastMessage(channelId, messageData) {
    try {
      const channelRef = doc(db, 'channels', channelId);
      await updateDoc(channelRef, {
        lastMessage: {
          content: messageData.content,
          authorId: messageData.authorId,
          authorName: messageData.authorName,
          timestamp: messageData.timestamp
        }
      });
    } catch (error) {
      console.error('Error updating last message:', error);
      throw error;
    }
  }
}; 