import { 
  collection, 
  doc,
  addDoc,
  setDoc,
  getDocs,
  getDoc,
  query,
  where,
  limit,
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const databaseService = {
  // Initialize default channels
  async initializeDefaultChannels() {
    try {
      const defaultChannels = [
        {
          name: 'general',
          description: 'General discussion for everyone',
          type: 'public',
          createdBy: 'system',
          createdAt: serverTimestamp(),
          members: [],
          lastMessage: null,
          messageCount: 0
        },
        {
          name: 'random',
          description: 'Random conversations and off-topic discussions',
          type: 'public',
          createdBy: 'system',
          createdAt: serverTimestamp(),
          members: [],
          lastMessage: null,
          messageCount: 0
        },
        {
          name: 'announcements',
          description: 'Important announcements and updates',
          type: 'public',
          createdBy: 'system',
          createdAt: serverTimestamp(),
          members: [],
          lastMessage: null,
          messageCount: 0
        }
      ];

      // Check if channels already exist
      const channelsSnapshot = await getDocs(collection(db, 'channels'));
      if (channelsSnapshot.empty) {
        console.log('Creating default channels...');
        
        for (const channelData of defaultChannels) {
          await addDoc(collection(db, 'channels'), channelData);
        }
        
        console.log('Default channels created successfully');
      } else {
        console.log('Channels already exist, skipping initialization');
      }
    } catch (error) {
      console.error('Error initializing default channels:', error);
      throw error;
    }
  },

  // Create welcome message in general channel
  async createWelcomeMessage() {
    try {
      // Find the general channel
      const channelsQuery = query(
        collection(db, 'channels'),
        where('name', '==', 'general')
      );
      
      const channelsSnapshot = await getDocs(channelsQuery);
      if (channelsSnapshot.empty) {
        console.log('General channel not found, skipping welcome message');
        return;
      }

      const generalChannel = channelsSnapshot.docs[0];
      const channelId = generalChannel.id;

      // Check if welcome message already exists
      const messagesSnapshot = await getDocs(
        collection(db, 'channels', channelId, 'messages')
      );

      if (messagesSnapshot.empty) {
        const welcomeMessage = {
          content: '🎉 Welcome to Roundtable! This is the general channel where everyone can chat. Feel free to introduce yourself and start conversations!',
          authorId: 'system',
          authorName: 'Roundtable Bot',
          timestamp: serverTimestamp(),
          edited: null,
          replyTo: null,
          reactions: {},
          attachments: [],
          deleted: false
        };

        await addDoc(collection(db, 'channels', channelId, 'messages'), welcomeMessage);
        console.log('Welcome message created successfully');
      }
    } catch (error) {
      console.error('Error creating welcome message:', error);
    }
  },

  // Initialize database with default data
  async initializeDatabase() {
    try {
      console.log('Initializing Roundtable database...');
      
      await this.initializeDefaultChannels();
      await this.createWelcomeMessage();
      
      console.log('Database initialization completed successfully');
    } catch (error) {
      console.error('Error initializing database:', error);
      throw error;
    }
  },

  // Get database statistics
  async getDatabaseStats() {
    try {
      const [channelsSnapshot, usersSnapshot] = await Promise.all([
        getDocs(collection(db, 'channels')),
        getDocs(collection(db, 'users'))
      ]);

      const stats = {
        totalChannels: channelsSnapshot.size,
        totalUsers: usersSnapshot.size,
        publicChannels: 0,
        privateChannels: 0,
        onlineUsers: 0
      };

      // Count channel types
      channelsSnapshot.docs.forEach(doc => {
        const data = doc.data();
        if (data.type === 'public') {
          stats.publicChannels++;
        } else {
          stats.privateChannels++;
        }
      });

      // Count online users
      usersSnapshot.docs.forEach(doc => {
        const data = doc.data();
        if (data.status === 'online') {
          stats.onlineUsers++;
        }
      });

      return stats;
    } catch (error) {
      console.error('Error getting database stats:', error);
      throw error;
    }
  },

  // Clean up old data (maintenance function)
  async cleanupOldData() {
    try {
      console.log('Starting database cleanup...');
      
      // Clean up old typing indicators (older than 5 minutes)
      const typingSnapshot = await getDocs(collection(db, 'typing'));
      const now = new Date();
      const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);

      for (const doc of typingSnapshot.docs) {
        const data = doc.data();
        if (data.timestamp && data.timestamp.toDate() < fiveMinutesAgo) {
          await doc.ref.delete();
        }
      }

      console.log('Database cleanup completed');
    } catch (error) {
      console.error('Error during database cleanup:', error);
    }
  },

  // Backup user data (for export functionality)
  async backupUserData(userId) {
    if (!auth.currentUser || auth.currentUser.uid !== userId) {
      throw new Error('Unauthorized: Can only backup your own data');
    }

    try {
      const userData = {
        user: null,
        channels: [],
        messages: [],
        directMessages: []
      };

      // Get user data
      const userDoc = await getDoc(doc(db, 'users', userId));
      if (userDoc.exists()) {
        userData.user = { id: userDoc.id, ...userDoc.data() };
      }

      // Get user's channels
      const channelsQuery = query(
        collection(db, 'channels'),
        where('members', 'array-contains', userId)
      );
      const channelsSnapshot = await getDocs(channelsQuery);
      userData.channels = channelsSnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));

      // Get user's messages (this would be expensive for large datasets)
      // In production, you'd want to limit this or use Cloud Functions
      for (const channel of userData.channels) {
        const messagesQuery = query(
          collection(db, 'channels', channel.id, 'messages'),
          where('authorId', '==', userId)
        );
        const messagesSnapshot = await getDocs(messagesQuery);
        const channelMessages = messagesSnapshot.docs.map(doc => ({
          id: doc.id,
          channelId: channel.id,
          channelName: channel.name,
          ...doc.data()
        }));
        userData.messages.push(...channelMessages);
      }

      return userData;
    } catch (error) {
      console.error('Error backing up user data:', error);
      throw error;
    }
  },

  // Health check for database connection
  async healthCheck() {
    try {
      // Try to read from a collection
      const testQuery = query(collection(db, 'channels'), limit(1));
      await getDocs(testQuery);
      
      return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        message: 'Database connection is working'
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        message: error.message,
        error: error.code
      };
    }
  }
}; 