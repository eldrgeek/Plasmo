import React, { useState } from 'react';

const ChannelList = ({ channels, activeChannel, onChannelSelect, onCreateChannel }) => {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newChannelName, setNewChannelName] = useState('');
    const [newChannelDescription, setNewChannelDescription] = useState('');

    const handleCreateSubmit = async (e) => {
        e.preventDefault();
        if (!newChannelName.trim()) return;

        try {
            await onCreateChannel(newChannelName.trim(), newChannelDescription.trim());
            setNewChannelName('');
            setNewChannelDescription('');
            setShowCreateForm(false);
        } catch (error) {
            console.error('Error creating channel:', error);
        }
    };

    const handleCancel = () => {
        setNewChannelName('');
        setNewChannelDescription('');
        setShowCreateForm(false);
    };

    return (
        <div className="p-4">
            {/* Channels Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-discord-gray-300 text-sm font-medium uppercase tracking-wide">
                    Text Channels
                </h3>
                <button
                    onClick={() => setShowCreateForm(true)}
                    className="text-discord-gray-300 hover:text-white p-1 rounded"
                    title="Create Channel"
                >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                    </svg>
                </button>
            </div>

            {/* Create Channel Form */}
            {showCreateForm && (
                <div className="mb-4 p-3 bg-discord-darkest rounded">
                    <form onSubmit={handleCreateSubmit} className="space-y-3">
                        <div>
                            <label className="block text-xs font-medium text-discord-gray-300 mb-1">
                                CHANNEL NAME
                            </label>
                            <input
                                type="text"
                                value={newChannelName}
                                onChange={(e) => setNewChannelName(e.target.value)}
                                placeholder="new-channel"
                                className="w-full px-2 py-1 bg-discord-dark border border-discord-gray-500 rounded text-white text-sm"
                                autoFocus
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-discord-gray-300 mb-1">
                                DESCRIPTION (OPTIONAL)
                            </label>
                            <input
                                type="text"
                                value={newChannelDescription}
                                onChange={(e) => setNewChannelDescription(e.target.value)}
                                placeholder="Channel description"
                                className="w-full px-2 py-1 bg-discord-dark border border-discord-gray-500 rounded text-white text-sm"
                            />
                        </div>
                        <div className="flex space-x-2">
                            <button
                                type="submit"
                                disabled={!newChannelName.trim()}
                                className="px-3 py-1 bg-discord-blurple hover:bg-blue-700 disabled:bg-gray-600 text-white text-sm rounded"
                            >
                                Create
                            </button>
                            <button
                                type="button"
                                onClick={handleCancel}
                                className="px-3 py-1 bg-transparent hover:bg-discord-gray-500 text-discord-gray-300 text-sm rounded"
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Channel List */}
            <div className="space-y-1">
                {channels.map((channel) => (
                    <div
                        key={channel.id}
                        onClick={() => onChannelSelect(channel)}
                        className={`channel-item flex items-center p-2 rounded cursor-pointer ${activeChannel?.id === channel.id
                                ? 'active bg-discord-blurple text-white'
                                : 'text-discord-gray-300 hover:text-white hover:bg-discord-gray-500'
                            }`}
                    >
                        <div className="mr-2 text-discord-gray-400">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center">
                                <span className="text-sm font-medium truncate">
                                    {channel.name}
                                </span>
                            </div>
                            {channel.description && (
                                <p className="text-xs text-discord-gray-400 truncate">
                                    {channel.description}
                                </p>
                            )}
                        </div>
                        {channel.lastMessage && (
                            <div className="ml-2 w-2 h-2 bg-discord-red rounded-full"></div>
                        )}
                    </div>
                ))}
            </div>

            {channels.length === 0 && !showCreateForm && (
                <div className="text-center text-discord-gray-400 py-8">
                    <p className="text-sm">No channels yet</p>
                    <button
                        onClick={() => setShowCreateForm(true)}
                        className="mt-2 text-discord-blurple hover:underline text-sm"
                    >
                        Create the first channel
                    </button>
                </div>
            )}
        </div>
    );
};

export default ChannelList; 