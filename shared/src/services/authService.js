import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  sendPasswordResetEmail
} from 'firebase/auth';
import { 
  doc, 
  setDoc, 
  updateDoc, 
  getDoc,
  serverTimestamp,
  onSnapshot
} from 'firebase/firestore';
import { auth, db } from '../firebase/config';

export const authService = {
  // Register new user
  async register(email, password, username) {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Update Firebase Auth profile
      await updateProfile(user, {
        displayName: username
      });
      
      // Create user document in Firestore
      await setDoc(doc(db, 'users', user.uid), {
        uid: user.uid,
        username,
        email,
        avatar: '',
        status: 'online',
        createdAt: serverTimestamp(),
        lastSeen: serverTimestamp(),
        preferences: {
          theme: 'dark',
          notifications: true,
          soundEnabled: true
        }
      });
      
      return user;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  // Login user
  async login(email, password) {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // Update online status
      await updateDoc(doc(db, 'users', userCredential.user.uid), {
        status: 'online',
        lastSeen: serverTimestamp()
      });
      
      return userCredential.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  // Logout user
  async logout() {
    try {
      if (auth.currentUser) {
        await updateDoc(doc(db, 'users', auth.currentUser.uid), {
          status: 'offline',
          lastSeen: serverTimestamp()
        });
      }
      await signOut(auth);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },
  
  // Get current user data from Firestore
  async getCurrentUserData() {
    if (!auth.currentUser) return null;
    
    try {
      const userDoc = await getDoc(doc(db, 'users', auth.currentUser.uid));
      return userDoc.exists() ? { id: userDoc.id, ...userDoc.data() } : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  },
  
  // Listen to auth state changes
  onAuthStateChanged(callback) {
    return onAuthStateChanged(auth, callback);
  },
  
  // Listen to user data changes
  subscribeToUserData(userId, callback) {
    return onSnapshot(doc(db, 'users', userId), (doc) => {
      if (doc.exists()) {
        callback({ id: doc.id, ...doc.data() });
      }
    });
  },
  
  // Update user status
  async updateUserStatus(status) {
    if (!auth.currentUser) return;
    
    try {
      await updateDoc(doc(db, 'users', auth.currentUser.uid), {
        status,
        lastSeen: serverTimestamp()
      });
    } catch (error) {
      console.error('Error updating user status:', error);
    }
  },
  
  // Update user preferences
  async updateUserPreferences(preferences) {
    if (!auth.currentUser) return;
    
    try {
      await updateDoc(doc(db, 'users', auth.currentUser.uid), {
        preferences
      });
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw error;
    }
  },
  
  // Reset password
  async resetPassword(email) {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      console.error('Password reset error:', error);
      throw error;
    }
  }
}; 