import React, { useState, useEffect, useRef } from 'react';

interface Agent {
  id: string;
  role: string;
  status: string;
}

interface Message {
  id: number;
  from: string;
  to: string;
  subject: string;
  message: string;
  timestamp: string;
}

interface LogEntry {
  timestamp: string;
  message: string;
}

const RoundTable: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageCount, setMessageCount] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'failed'>('connecting');
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [messageInput, setMessageInput] = useState<string>('');
  const [logs, setLogs] = useState<LogEntry[]>([{ timestamp: new Date().toLocaleTimeString(), message: 'Round Table Monitor v2.0 - Initializing...' }]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const logEndRef = useRef<HTMLDivElement>(null);

  const log = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-20), { timestamp, message }]);
    console.log(message);
  };

  const makeRequest = async (tool: string, params = {}) => {
    try {
      const response = await fetch(`http://localhost:8000/mcp/tools/${tool}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error: any) {
      log(`❌ ${tool}: ${error.message}`);
      return { success: false, error: error.message };
    }
  };

  const refreshAgents = async () => {
    const result = await makeRequest('list_claude_instances');
    
    if (result.success) {
      const agentList = result.instances || [];
      setAgents(agentList);
      setConnectionStatus('connected');
      log(`✅ Found ${agentList.length} agents`);
    } else {
      setConnectionStatus('failed');
      log(`❌ Failed to get agents: ${result.error}`);
    }
  };

  const loadMessages = async () => {
    const result = await makeRequest('messages', { operation: 'get' });
    
    if (result.success && result.messages) {
      const newMessages = result.messages;
      if (newMessages.length > messageCount) {
        const newCount = newMessages.length - messageCount;
        log(`📨 ${newCount} new messages found`);
        setMessages(newMessages);
        setMessageCount(newMessages.length);
      }
    }
  };

  const sendHumanMessage = async () => {
    if (!selectedAgent || !messageInput.trim()) {
      log('❌ Select an agent and enter a message');
      return;
    }

    const result = await makeRequest('send_inter_instance_message', {
      target_instance_id: selectedAgent,
      subject: 'Message from Human Monitor',
      message: messageInput.trim(),
      sender_role: 'human_monitor'
    });

    if (result.success) {
      log(`✅ Sent message to ${selectedAgent}`);
      setMessageInput('');
      
      // Add human message to display
      const humanMessage: Message = {
        id: Date.now(),
        from: 'human_monitor',
        to: selectedAgent,
        subject: 'Message from Human Monitor',
        message: messageInput.trim(),
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, humanMessage]);
      
      // Refresh messages in a few seconds to see responses
      setTimeout(loadMessages, 3000);
    } else {
      log(`❌ Failed to send message: ${result.error}`);
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setMessageCount(0);
    log('🗑️ Messages cleared');
  };

  const refreshData = async () => {
    log('🔄 Refreshing all data...');
    await refreshAgents();
    await loadMessages();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendHumanMessage();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  useEffect(() => {
    log('🚀 Starting Round Table Monitor...');
    refreshData();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadMessages, 10000);
    
    log('✅ Monitor ready - watching for agent communications!');
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-700';
      case 'failed': return 'bg-red-700';
      default: return 'bg-orange-700';
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return `🟢 Connected - ${agents.length} agents active`;
      case 'failed': return '🔴 Connection failed';
      default: return 'Connecting...';
    }
  };

  const getAgentRole = (agentId: string): string => {
    const agent = agents.find(a => a.id === agentId);
    return agent?.role.replace('_', ' ').toUpperCase() || agentId;
  };

  const getShortId = (id: string): string => {
    return id.substring(id.length - 8);
  };

  return (
    <div className="h-screen bg-gray-900 text-gray-200 overflow-hidden">
      <div className="grid grid-cols-[300px_1fr] h-full">
        {/* Sidebar */}
        <div className="bg-gray-800 border-r border-gray-600 p-5">
          <div className="text-xl font-semibold text-white mb-5">
            🎯 Round Table Monitor
          </div>
          
          <div className={`p-2.5 rounded text-xs mb-2.5 ${getStatusColor()}`}>
            {getStatusText()}
          </div>
          
          <div className="mt-5">
            <h3 className="text-gray-400 text-sm mb-2.5">Active Agents</h3>
            <div className="space-y-2">
              {agents.map(agent => (
                <div
                  key={agent.id}
                  className="p-2.5 bg-gray-700 rounded cursor-pointer transition-colors hover:bg-gray-600"
                  onClick={() => setSelectedAgent(agent.id)}
                >
                  <div className="font-semibold text-white">
                    🤖 {agent.role.replace('_', ' ').toUpperCase()}
                  </div>
                  <div className="text-xs text-gray-400">
                    Status: {agent.status}
                  </div>
                  <div className="text-xs text-gray-500 font-mono">
                    {getShortId(agent.id)}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-5 space-y-2">
            <button
              onClick={refreshData}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-sm transition-colors"
            >
              Refresh All
            </button>
            <button
              onClick={clearMessages}
              className="w-full bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded text-sm transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Main Area */}
        <div className="flex flex-col">
          {/* Header */}
          <div className="p-4 bg-gray-800 border-b border-gray-600">
            <h2 className="text-white text-lg font-semibold">
              🔴 Live Agent Communication Stream
            </h2>
            <div className="text-xs text-gray-400 mt-1">
              Monitoring inter-agent messages in real-time
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-5">
            {/* System Message */}
            <div className="bg-gray-800 rounded-lg p-4 mb-4 border-l-4 border-blue-600">
              <div className="flex items-center mb-2">
                <div className="font-semibold text-white mr-2.5">System</div>
                <div className="text-xs text-gray-400">Now</div>
              </div>
              <div className="leading-relaxed">
                Round Table monitoring initialized. Watching for agent communications...
              </div>
            </div>

            {/* Agent Messages */}
            {messages.slice(-20).map((msg, index) => {
              const isHuman = msg.from === 'human_monitor';
              const time = new Date(msg.timestamp).toLocaleTimeString();
              const fromRole = getAgentRole(msg.from);
              const toRole = getAgentRole(msg.to);
              
              return (
                <div
                  key={msg.id || index}
                  className={`rounded-lg p-4 mb-4 border-l-4 ${
                    isHuman 
                      ? 'bg-gray-900 border-orange-600' 
                      : 'bg-gray-800 border-green-600'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    <div className="font-semibold text-white mr-2.5">
                      {isHuman ? '👤 Human' : fromRole} → {toRole}
                    </div>
                    <div className="text-xs text-gray-400">{time}</div>
                  </div>
                  <div className="leading-relaxed whitespace-pre-wrap">
                    <strong>{msg.subject}</strong>
                    {'\n\n'}{msg.message}
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* Controls */}
          <div className="p-4 bg-gray-800 border-t border-gray-600 flex gap-2.5">
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="w-48 p-2.5 border border-gray-600 rounded bg-gray-700 text-white"
            >
              <option value="">Select agent...</option>
              {agents.map(agent => (
                <option key={agent.id} value={agent.id}>
                  {agent.role} ({getShortId(agent.id)})
                </option>
              ))}
            </select>
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Send message to agents..."
              className="flex-1 p-2.5 border border-gray-600 rounded bg-gray-700 text-white placeholder-gray-400"
            />
            <button
              onClick={sendHumanMessage}
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Log */}
      <div className="fixed bottom-2.5 right-2.5 w-80 bg-gray-900 border border-gray-600 rounded p-2.5 font-mono text-xs max-h-40 overflow-y-auto">
        {logs.map((entry, index) => (
          <div key={index}>
            [{entry.timestamp}] {entry.message}
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
};

export default RoundTable;