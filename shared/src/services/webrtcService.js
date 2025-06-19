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
  increment,
  arrayUnion,
  arrayRemove
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';
import { storageService } from './storageService';

export const webrtcService = {
  // Create or join WebRTC room
  async joinRoom(roomName, peerId, username, userData = {}) {
    if (!auth.currentUser) throw new Error('User not authenticated');
    
    try {
      const roomRef = doc(db, 'webrtcRooms', roomName);
      const roomDoc = await getDoc(roomRef);
      
      // Create room if it doesn't exist
      if (!roomDoc.exists()) {
        await setDoc(roomRef, {
          name: roomName,
          createdAt: serverTimestamp(),
          createdBy: auth.currentUser.uid,
          maxPeers: 100,
          activePeerCount: 0,
          totalPeerCount: 0
        });
      }
      
      // Add peer to room
      const peerData = {
        peerId,
        username,
        userId: auth.currentUser.uid,
        joinedAt: serverTimestamp(),
        lastSeen: serverTimestamp(),
        isActive: true,
        userData: userData || {},
        uploadedFiles: []
      };
      
      const peerRef = doc(db, 'webrtcRooms', roomName, 'peers', peerId);
      await setDoc(peerRef, peerData);
      
      // Update room peer counts
      await updateDoc(roomRef, {
        activePeerCount: increment(1),
        totalPeerCount: increment(1)
      });
      
      // Get updated peer list
      const peers = await this.getRoomPeers(roomName);
      
      return {
        success: true,
        roomName,
        peerId,
        peers: peers.peers,
        activePeers: peers.activePeers,
        totalPeers: peers.totalPeers
      };
    } catch (error) {
      console.error('Error joining room:', error);
      throw error;
    }
  },
  
  // Leave WebRTC room (mark as inactive)
  async leaveRoom(roomName, peerId) {
    try {
      const peerRef = doc(db, 'webrtcRooms', roomName, 'peers', peerId);
      const peerDoc = await getDoc(peerRef);
      
      if (peerDoc.exists() && peerDoc.data().isActive) {
        await updateDoc(peerRef, {
          isActive: false,
          lastSeen: serverTimestamp()
        });
        
        // Update room active peer count
        const roomRef = doc(db, 'webrtcRooms', roomName);
        await updateDoc(roomRef, {
          activePeerCount: increment(-1)
        });
        
        return { success: true };
      }
      
      return { success: false, message: 'Peer not found or already inactive' };
    } catch (error) {
      console.error('Error leaving room:', error);
      throw error;
    }
  },
  
  // Get all WebRTC rooms
  async getAllRooms() {
    try {
      const roomsSnapshot = await getDocs(collection(db, 'webrtcRooms'));
      const rooms = [];
      
      for (const roomDoc of roomsSnapshot.docs) {
        const roomData = roomDoc.data();
        const peers = await this.getRoomPeers(roomDoc.id);
        
        rooms.push({
          name: roomDoc.id,
          ...roomData,
          peers: peers.peers
        });
      }
      
      return { success: true, rooms };
    } catch (error) {
      console.error('Error getting rooms:', error);
      throw error;
    }
  },
  
  // Get specific room information
  async getRoom(roomName) {
    try {
      const roomRef = doc(db, 'webrtcRooms', roomName);
      const roomDoc = await getDoc(roomRef);
      
      if (!roomDoc.exists()) {
        throw new Error('Room not found');
      }
      
      const peers = await this.getRoomPeers(roomName);
      
      return {
        success: true,
        name: roomName,
        ...roomDoc.data(),
        peers: peers.peers
      };
    } catch (error) {
      console.error('Error getting room:', error);
      throw error;
    }
  },
  
  // Get room peers
  async getRoomPeers(roomName, includeInactive = true) {
    try {
      let q = collection(db, 'webrtcRooms', roomName, 'peers');
      
      if (!includeInactive) {
        q = query(q, where('isActive', '==', true));
      }
      
      const snapshot = await getDocs(q);
      const peers = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      const activePeers = peers.filter(p => p.isActive).length;
      
      return {
        success: true,
        peers,
        activePeers,
        totalPeers: peers.length
      };
    } catch (error) {
      console.error('Error getting room peers:', error);
      throw error;
    }
  },
  
  // Update peer user data
  async updatePeerData(roomName, peerId, userData) {
    try {
      const peerRef = doc(db, 'webrtcRooms', roomName, 'peers', peerId);
      const peerDoc = await getDoc(peerRef);
      
      if (!peerDoc.exists()) {
        throw new Error('Peer not found');
      }
      
      await updateDoc(peerRef, {
        userData: {
          ...peerDoc.data().userData,
          ...userData
        },
        lastSeen: serverTimestamp()
      });
      
      return {
        success: true,
        roomName,
        peerId,
        updatedData: userData
      };
    } catch (error) {
      console.error('Error updating peer data:', error);
      throw error;
    }
  },
  
  // Send heartbeat (update last seen)
  async sendHeartbeat(roomName, peerId) {
    try {
      const peerRef = doc(db, 'webrtcRooms', roomName, 'peers', peerId);
      await updateDoc(peerRef, {
        lastSeen: serverTimestamp()
      });
      
      return {
        success: true,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error sending heartbeat:', error);
      throw error;
    }
  },
  
  // Upload file for peer
  async uploadFile(roomName, peerId, file) {
    try {
      // Upload file using storage service
      const uploadResult = await storageService.uploadFile(file, `webrtc/${roomName}/${peerId}`);
      
      // Add file to peer's uploaded files
      const peerRef = doc(db, 'webrtcRooms', roomName, 'peers', peerId);
      await updateDoc(peerRef, {
        uploadedFiles: arrayUnion({
          filename: uploadResult.filename,
          originalName: file.name,
          url: uploadResult.url,
          size: file.size,
          type: file.type,
          uploadedAt: serverTimestamp()
        })
      });
      
      return {
        success: true,
        filename: uploadResult.filename,
        originalFilename: file.name,
        fileUrl: uploadResult.url,
        fileSize: file.size,
        contentType: file.type,
        roomName,
        peerId
      };
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  },
  
  // Subscribe to room changes
  subscribeToRoom(roomName, callback) {
    const roomRef = doc(db, 'webrtcRooms', roomName);
    return onSnapshot(roomRef, (doc) => {
      if (doc.exists()) {
        callback({
          success: true,
          name: roomName,
          ...doc.data()
        });
      }
    });
  },
  
  // Subscribe to peer list changes
  subscribeToPeers(roomName, callback, includeInactive = true) {
    let q = collection(db, 'webrtcRooms', roomName, 'peers');
    
    if (!includeInactive) {
      q = query(q, where('isActive', '==', true));
    }
    
    return onSnapshot(q, (snapshot) => {
      const peers = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      const activePeers = peers.filter(p => p.isActive).length;
      
      callback({
        success: true,
        peers,
        activePeers,
        totalPeers: peers.length
      });
    });
  },
  
  // Clean up inactive peers (admin function)
  async cleanupInactivePeers(roomName, inactiveThresholdMinutes = 30) {
    try {
      const threshold = new Date(Date.now() - inactiveThresholdMinutes * 60 * 1000);
      
      const peersRef = collection(db, 'webrtcRooms', roomName, 'peers');
      const q = query(peersRef, where('isActive', '==', false));
      const snapshot = await getDocs(q);
      
      const batch = [];
      let cleanedCount = 0;
      
      snapshot.docs.forEach(doc => {
        const peerData = doc.data();
        const lastSeen = peerData.lastSeen?.toDate();
        
        if (lastSeen && lastSeen < threshold) {
          batch.push(deleteDoc(doc.ref));
          cleanedCount++;
        }
      });
      
      await Promise.all(batch);
      
      // Update room total peer count
      if (cleanedCount > 0) {
        const roomRef = doc(db, 'webrtcRooms', roomName);
        await updateDoc(roomRef, {
          totalPeerCount: increment(-cleanedCount)
        });
      }
      
      return {
        success: true,
        cleanedCount,
        message: `Cleaned up ${cleanedCount} inactive peers`
      };
    } catch (error) {
      console.error('Error cleaning up inactive peers:', error);
      throw error;
    }
  }
}; 