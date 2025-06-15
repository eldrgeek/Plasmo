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
  onSnapshot,
  serverTimestamp,
  increment
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const extensionService = {
  // Register extension connection
  async registerExtension(extensionId, metadata = {}) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const extensionData = {
        extensionId,
        userId: auth.currentUser.uid,
        userEmail: auth.currentUser.email,
        timestamp: serverTimestamp(),
        connected: true,
        lastSeen: serverTimestamp(),
        metadata: {
          userAgent: navigator.userAgent,
          url: window.location.href,
          ...metadata
        }
      };
      
      const extensionRef = doc(db, 'extensions', extensionId);
      await setDoc(extensionRef, extensionData, { merge: true });
      
      return { success: true, extensionId };
    } catch (error) {
      console.error('Error registering extension:', error);
      throw error;
    }
  },
  
  // Update extension status
  async updateExtensionStatus(extensionId, connected = true, metadata = {}) {
    try {
      const extensionRef = doc(db, 'extensions', extensionId);
      await updateDoc(extensionRef, {
        connected,
        lastSeen: serverTimestamp(),
        metadata: {
          ...metadata
        }
      });
      
      return { success: true };
    } catch (error) {
      console.error('Error updating extension status:', error);
      throw error;
    }
  },
  
  // Get all connected extensions
  async getConnectedExtensions() {
    try {
      const q = query(
        collection(db, 'extensions'),
        where('connected', '==', true),
        orderBy('lastSeen', 'desc')
      );
      
      const snapshot = await getDocs(q);
      const extensions = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return {
        success: true,
        extensions,
        count: extensions.length
      };
    } catch (error) {
      console.error('Error getting extensions:', error);
      throw error;
    }
  },
  
  // Subscribe to extension changes
  subscribeToExtensions(callback) {
    const q = query(
      collection(db, 'extensions'),
      where('connected', '==', true),
      orderBy('lastSeen', 'desc')
    );
    
    return onSnapshot(q, (snapshot) => {
      const extensions = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      callback({
        success: true,
        extensions,
        count: extensions.length
      });
    });
  },
  
  // Send command to extension (store in commands collection)
  async sendCommand(extensionId, action, payload = {}) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const commandData = {
        extensionId,
        action,
        payload,
        sentBy: auth.currentUser.uid,
        timestamp: serverTimestamp(),
        status: 'pending',
        executed: false
      };
      
      const commandRef = await addDoc(collection(db, 'commands'), commandData);
      
      return {
        success: true,
        commandId: commandRef.id,
        message: 'Command queued for extension'
      };
    } catch (error) {
      console.error('Error sending command:', error);
      throw error;
    }
  },
  
  // Broadcast command to all extensions
  async broadcastCommand(action, payload = {}) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const extensions = await this.getConnectedExtensions();
      const commands = [];
      
      for (const extension of extensions.extensions) {
        const commandData = {
          extensionId: extension.extensionId,
          action,
          payload,
          sentBy: auth.currentUser.uid,
          timestamp: serverTimestamp(),
          status: 'pending',
          executed: false,
          broadcast: true
        };
        
        const commandRef = await addDoc(collection(db, 'commands'), commandData);
        commands.push(commandRef.id);
      }
      
      return {
        success: true,
        message: `Command sent to ${extensions.count} extension(s)`,
        commandIds: commands,
        extensionCount: extensions.count
      };
    } catch (error) {
      console.error('Error broadcasting command:', error);
      throw error;
    }
  },
  
  // Get pending commands for extension
  async getPendingCommands(extensionId) {
    try {
      const q = query(
        collection(db, 'commands'),
        where('extensionId', '==', extensionId),
        where('executed', '==', false),
        orderBy('timestamp', 'asc')
      );
      
      const snapshot = await getDocs(q);
      const commands = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return { success: true, commands };
    } catch (error) {
      console.error('Error getting pending commands:', error);
      throw error;
    }
  },
  
  // Mark command as executed
  async markCommandExecuted(commandId, result = {}) {
    try {
      const commandRef = doc(db, 'commands', commandId);
      await updateDoc(commandRef, {
        executed: true,
        status: 'completed',
        result,
        executedAt: serverTimestamp()
      });
      
      return { success: true };
    } catch (error) {
      console.error('Error marking command executed:', error);
      throw error;
    }
  },
  
  // Subscribe to commands for specific extension
  subscribeToCommands(extensionId, callback) {
    const q = query(
      collection(db, 'commands'),
      where('extensionId', '==', extensionId),
      where('executed', '==', false),
      orderBy('timestamp', 'asc')
    );
    
    return onSnapshot(q, (snapshot) => {
      const commands = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      callback({ success: true, commands });
    });
  }
}; 