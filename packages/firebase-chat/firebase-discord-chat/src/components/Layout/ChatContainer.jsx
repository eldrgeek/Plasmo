import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import ChannelList from '../Chat/ChannelList';
import MessageList from '../Chat/MessageList';
import MessageInput from '../Chat/MessageInput';
import UserList from '../Chat/UserList';
import Header from './Header';
import { channelService } from '../../services/channelService';

const ChatContainer = () => {
    const { userData, logout } = useAuth();
    const [channels, setChannels] = useState([]);
    const [activeChannel, setActiveChannel] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        // Subscribe to channels
        const unsubscribe = channelService.subscribeToChannels((channelsData) => {
            setChannels(channelsData);
            // Set first channel as active if none selected
            if (!activeChannel && channelsData.length > 0) {
                setActiveChannel(channelsData[0]);
            }
        });

        return unsubscribe;
    }, [activeChannel]);

    const handleChannelSelect = (channel) => {
        setActiveChannel(channel);
        setSidebarOpen(false); // Close sidebar on mobile after selection
    };

    const handleCreateChannel = async (name, description) => {
        try {
            await channelService.createChannel(name, description);
        } catch (error) {
            console.error('Error creating channel:', error);
        }
    };

    return (
        <div className="flex h-screen bg-discord-dark text-white">
            {/* Sidebar - Channel List */}
            <div className={`sidebar bg-discord-darker w-72 flex-shrink-0 ${sidebarOpen ? 'open' : ''}`}>
                <div className="flex flex-col h-full">
                    {/* Server Header */}
                    <div className="bg-discord-darkest p-4 border-b border-discord-darkest">
                        <h1 className="text-white font-semibold text-lg">Discord Chat</h1>
                    </div>

                    {/* Channel List */}
                    <div className="flex-1 overflow-y-auto">
                        <ChannelList
                            channels={channels}
                            activeChannel={activeChannel}
                            onChannelSelect={handleChannelSelect}
                            onCreateChannel={handleCreateChannel}
                        />
                    </div>

                    {/* User Panel */}
                    <div className="bg-discord-darkest p-3 flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 rounded-full bg-discord-blurple flex items-center justify-center">
                                <span className="text-sm font-medium">
                                    {userData?.username?.charAt(0)?.toUpperCase() || 'U'}
                                </span>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white truncate">
                                    {userData?.username || 'User'}
                                </p>
                                <p className="text-xs text-discord-gray-300 truncate">
                                    {userData?.status || 'online'}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            className="text-discord-gray-300 hover:text-white p-1 rounded"
                            title="Logout"
                        >
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <Header
                    channel={activeChannel}
                    onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                />

                {/* Chat Messages */}
                <div className="flex-1 flex min-h-0">
                    <div className="flex-1 flex flex-col">
                        {activeChannel ? (
                            <>
                                <MessageList channelId={activeChannel.id} />
                                <MessageInput
                                    channelId={activeChannel.id}
                                    placeholder={`Message #${activeChannel.name}`}
                                />
                            </>
                        ) : (
                            <div className="flex-1 flex items-center justify-center">
                                <div className="text-center text-discord-gray-300">
                                    <h3 className="text-xl font-medium mb-2">Welcome to Discord Chat!</h3>
                                    <p>Select a channel to start chatting</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* User List - Desktop Only */}
                    <div className="hidden lg:block w-60 bg-discord-darker">
                        {activeChannel && (
                            <UserList channelId={activeChannel.id} />
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}
        </div>
    );
};

export default ChatContainer; 