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
  serverTimestamp
} from 'firebase/firestore';
import { db, auth } from '../firebase/config';

export const testingService = {
  // Store test results
  async storeTestResults(testData) {
    try {
      const testResult = {
        ...testData,
        testId: testData.testId || `test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: serverTimestamp(),
        submittedBy: auth.currentUser?.uid || 'anonymous',
        submittedAt: serverTimestamp()
      };
      
      const testRef = await addDoc(collection(db, 'testResults'), testResult);
      
      return {
        success: true,
        testId: testResult.testId,
        documentId: testRef.id,
        message: 'Test results stored successfully'
      };
    } catch (error) {
      console.error('Error storing test results:', error);
      throw error;
    }
  },
  
  // Get latest test results
  async getLatestTestResults(limitCount = 10) {
    try {
      const q = query(
        collection(db, 'testResults'),
        orderBy('timestamp', 'desc'),
        limit(limitCount)
      );
      
      const snapshot = await getDocs(q);
      const testResults = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return {
        success: true,
        testResults,
        count: testResults.length
      };
    } catch (error) {
      console.error('Error getting latest test results:', error);
      throw error;
    }
  },
  
  // Get all test results with pagination
  async getAllTestResults(limitCount = 50, lastDoc = null) {
    try {
      let q = query(
        collection(db, 'testResults'),
        orderBy('timestamp', 'desc'),
        limit(limitCount)
      );
      
      if (lastDoc) {
        q = query(
          collection(db, 'testResults'),
          orderBy('timestamp', 'desc'),
          startAfter(lastDoc),
          limit(limitCount)
        );
      }
      
      const snapshot = await getDocs(q);
      const testResults = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return {
        success: true,
        testResults,
        count: testResults.length,
        lastDoc: snapshot.docs[snapshot.docs.length - 1]
      };
    } catch (error) {
      console.error('Error getting all test results:', error);
      throw error;
    }
  },
  
  // Subscribe to test results in real-time
  subscribeToTestResults(callback, limitCount = 20) {
    const q = query(
      collection(db, 'testResults'),
      orderBy('timestamp', 'desc'),
      limit(limitCount)
    );
    
    return onSnapshot(q, (snapshot) => {
      const testResults = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      callback({
        success: true,
        testResults,
        count: testResults.length
      });
    });
  },
  
  // Store AI completion signal
  async storeCompletionSignal(completionData) {
    try {
      const completionSignal = {
        completionId: completionData.completionId || `completion_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        status: completionData.status || 'completed',
        timestamp: serverTimestamp(),
        summary: completionData.summary || null,
        metadata: completionData.metadata || {},
        submittedBy: auth.currentUser?.uid || 'anonymous',
        submittedAt: serverTimestamp()
      };
      
      const completionRef = await addDoc(collection(db, 'aiCompletions'), completionSignal);
      
      return {
        success: true,
        completionId: completionSignal.completionId,
        documentId: completionRef.id,
        message: 'Completion signal stored successfully'
      };
    } catch (error) {
      console.error('Error storing completion signal:', error);
      throw error;
    }
  },
  
  // Get completion signals
  async getCompletionSignals(limitCount = 20) {
    try {
      const q = query(
        collection(db, 'aiCompletions'),
        orderBy('timestamp', 'desc'),
        limit(limitCount)
      );
      
      const snapshot = await getDocs(q);
      const completions = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return {
        success: true,
        completions,
        count: completions.length
      };
    } catch (error) {
      console.error('Error getting completion signals:', error);
      throw error;
    }
  },
  
  // Subscribe to AI completion signals
  subscribeToCompletionSignals(callback, limitCount = 20) {
    const q = query(
      collection(db, 'aiCompletions'),
      orderBy('timestamp', 'desc'),
      limit(limitCount)
    );
    
    return onSnapshot(q, (snapshot) => {
      const completions = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      callback({
        success: true,
        completions,
        count: completions.length
      });
    });
  },
  
  // Get test results by trigger type
  async getTestResultsByTrigger(trigger, limitCount = 20) {
    try {
      const q = query(
        collection(db, 'testResults'),
        where('trigger', '==', trigger),
        orderBy('timestamp', 'desc'),
        limit(limitCount)
      );
      
      const snapshot = await getDocs(q);
      const testResults = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      return {
        success: true,
        testResults,
        count: testResults.length,
        trigger
      };
    } catch (error) {
      console.error('Error getting test results by trigger:', error);
      throw error;
    }
  },
  
  // Get test statistics
  async getTestStatistics(days = 7) {
    try {
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);
      
      const q = query(
        collection(db, 'testResults'),
        where('timestamp', '>=', startDate),
        orderBy('timestamp', 'desc')
      );
      
      const snapshot = await getDocs(q);
      const testResults = snapshot.docs.map(doc => doc.data());
      
      // Calculate statistics
      const totalTests = testResults.length;
      const passedTests = testResults.filter(t => t.success === true).length;
      const failedTests = totalTests - passedTests;
      const passRate = totalTests > 0 ? (passedTests / totalTests * 100).toFixed(2) : 0;
      
      // Group by trigger
      const triggerStats = {};
      testResults.forEach(test => {
        const trigger = test.trigger || 'unknown';
        if (!triggerStats[trigger]) {
          triggerStats[trigger] = { total: 0, passed: 0, failed: 0 };
        }
        triggerStats[trigger].total++;
        if (test.success) {
          triggerStats[trigger].passed++;
        } else {
          triggerStats[trigger].failed++;
        }
      });
      
      return {
        success: true,
        statistics: {
          totalTests,
          passedTests,
          failedTests,
          passRate: parseFloat(passRate),
          days,
          triggerStats
        }
      };
    } catch (error) {
      console.error('Error getting test statistics:', error);
      throw error;
    }
  },
  
  // Health check for testing service
  async healthCheck() {
    try {
      const testCount = await getDocs(collection(db, 'testResults'));
      const completionCount = await getDocs(collection(db, 'aiCompletions'));
      
      return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        collections: {
          testResults: testCount.size,
          aiCompletions: completionCount.size
        },
        version: '1.0.0'
      };
    } catch (error) {
      console.error('Error in health check:', error);
      throw error;
    }
  }
}; 