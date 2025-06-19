import { 
  collection, 
  doc,
  getDoc,
  getDocs,
  updateDoc,
  setDoc,
  deleteDoc,
  query, 
  where,
  orderBy, 
  limit,
  onSnapshot,
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const userService = {
  // Get user by ID
  async getUser(userId) {
    try {
      const userDoc = await getDoc(doc(db, 'users', userId));
      if (userDoc.exists()) {
        return { id: userDoc.id, ...userDoc.data() };
      } else {
        throw new Error('User not found');
      }
    } catch (error) {
      console.error('Error getting user:', error);
      throw error;
    }
  },
  
  // Get multiple users by IDs
  async getUsers(userIds) {
    try {
      const users = await Promise.all(
        userIds.map(async (userId) => {
          try {
            const userDoc = await getDoc(doc(db, 'users', userId));
            return userDoc.exists() ? { id: userDoc.id, ...userDoc.data() } : null;
          } catch (error) {
            console.error(`Error getting user ${userId}:`, error);
            return null;
          }
        })
      );
      
      return users.filter(user => user !== null);
    } catch (error) {
      console.error('Error getting users:', error);
      throw error;
    }
  },
  
  // Search users by username
  async searchUsers(searchTerm, limit = 20) {
    try {
      // Note: This is a basic implementation. For production, consider using
      // Algolia or implementing a more sophisticated search
      const q = query(
        collection(db, 'users'),
        orderBy('username'),
        limit(limit)
      );
      
      const snapshot = await getDocs(q);
      const users = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      // Client-side filtering (not ideal for large datasets)
      return users.filter(user => 
        user.username.toLowerCase().includes(searchTerm.toLowerCase())
      );
    } catch (error) {
      console.error('Error searching users:', error);
      throw error;
    }
  },
  
  // Get online users
  async getOnlineUsers() {
    try {
      const q = query(
        collection(db, 'users'),
        where('status', '==', 'online'),
        orderBy('lastSeen', 'desc')
      );
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error getting online users:', error);
      throw error;
    }
  },
  
  // Subscribe to online users
  subscribeToOnlineUsers(callback) {
    const q = query(
      collection(db, 'users'),
      where('status', 'in', ['online', 'away']),
      orderBy('lastSeen', 'desc')
    );
    
    return onSnapshot(q, (snapshot) => {
      const users = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      callback(users);
    });
  },
  
  // Subscribe to user presence changes
  subscribeToUserPresence(userId, callback) {
    return onSnapshot(doc(db, 'users', userId), (doc) => {
      if (doc.exists()) {
        const userData = { id: doc.id, ...doc.data() };
        callback(userData);
      }
    });
  },
  
  // Update user profile
  async updateProfile(updates) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const userRef = doc(db, 'users', auth.currentUser.uid);
      await updateDoc(userRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  },
  
  // Update user status
  async updateStatus(status) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const userRef = doc(db, 'users', auth.currentUser.uid);
      await updateDoc(userRef, {
        status,
        lastSeen: serverTimestamp()
      });
    } catch (error) {
      console.error('Error updating status:', error);
      throw error;
    }
  },
  
  // Set user as typing in a channel
  async setTyping(channelId, isTyping = true) {
    if (!auth.currentUser) return;
    
    try {
      const typingRef = doc(db, 'typing', `${channelId}_${auth.currentUser.uid}`);
      
      if (isTyping) {
        await setDoc(typingRef, {
          userId: auth.currentUser.uid,
          username: auth.currentUser.displayName || 'Anonymous',
          channelId,
          timestamp: serverTimestamp()
        });
        
        // Auto-remove typing indicator after 3 seconds
        setTimeout(async () => {
          try {
            await deleteDoc(typingRef);
          } catch (error) {
            // Ignore errors when removing typing indicator
          }
        }, 3000);
      } else {
        await deleteDoc(typingRef);
      }
    } catch (error) {
      console.error('Error setting typing status:', error);
    }
  },
  
  // Subscribe to typing indicators for a channel
  subscribeToTyping(channelId, callback) {
    const q = query(
      collection(db, 'typing'),
      where('channelId', '==', channelId)
    );
    
    return onSnapshot(q, (snapshot) => {
      const typingUsers = snapshot.docs
        .map(doc => doc.data())
        .filter(typing => typing.userId !== auth.currentUser?.uid); // Exclude current user
      
      callback(typingUsers);
    });
  },
  
  // Get user's channel memberships
  async getUserChannels(userId) {
    try {
      const q = query(
        collection(db, 'channels'),
        where('members', 'array-contains', userId)
      );
      
      const snapshot = await getDocs(q);
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error getting user channels:', error);
      throw error;
    }
  },
  
  // Get users in a channel
  async getChannelUsers(channelId) {
    try {
      const channelDoc = await getDoc(doc(db, 'channels', channelId));
      if (!channelDoc.exists()) {
        throw new Error('Channel not found');
      }
      
      const channelData = channelDoc.data();
      
      // For public channels, get all online users
      if (channelData.type === 'public') {
        return await this.getOnlineUsers();
      }
      
      // For private channels, get only members
      if (channelData.members && channelData.members.length > 0) {
        return await this.getUsers(channelData.members);
      }
      
      return [];
    } catch (error) {
      console.error('Error getting channel users:', error);
      throw error;
    }
  },
  
  // Subscribe to users in a channel
  subscribeToChannelUsers(channelId, callback) {
    // First get the channel to determine type
    const channelUnsubscribe = onSnapshot(doc(db, 'channels', channelId), (channelDoc) => {
      if (!channelDoc.exists()) return;
      
      const channelData = channelDoc.data();
      
      if (channelData.type === 'public') {
        // For public channels, subscribe to online users
        return this.subscribeToOnlineUsers(callback);
      } else if (channelData.members && channelData.members.length > 0) {
        // For private channels, get member details
        this.getUsers(channelData.members).then(callback);
      }
    });
    
    return channelUnsubscribe;
  },
  
  // Update last seen timestamp
  async updateLastSeen() {
    if (!auth.currentUser) return;
    
    try {
      const userRef = doc(db, 'users', auth.currentUser.uid);
      await updateDoc(userRef, {
        lastSeen: serverTimestamp()
      });
    } catch (error) {
      console.error('Error updating last seen:', error);
    }
  },
  
  // Get user statistics
  async getUserStats(userId) {
    try {
      // This would require additional collections or cloud functions
      // For now, return basic stats
      const user = await this.getUser(userId);
      
      return {
        joinDate: user.createdAt,
        lastSeen: user.lastSeen,
        status: user.status,
        // Additional stats would be calculated here
        messageCount: 0, // Would need to aggregate from messages
        channelCount: 0  // Would need to aggregate from channel memberships
      };
    } catch (error) {
      console.error('Error getting user stats:', error);
      throw error;
    }
  }
}; 