import React, { useState, useEffect, useRef } from 'react';
import { messageService } from '../../services/messageService';
import { useAuth } from '../../context/AuthContext';

const MessageList = ({ channelId }) => {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(true);
    const messagesEndRef = useRef(null);
    const { currentUser } = useAuth();

    useEffect(() => {
        if (!channelId) return;

        setLoading(true);
        const unsubscribe = messageService.subscribeToMessages(channelId, (messagesData) => {
            setMessages(messagesData);
            setLoading(false);
        });

        return unsubscribe;
    }, [channelId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const formatTime = (timestamp) => {
        if (!timestamp) return '';
        const date = timestamp instanceof Date ? timestamp : timestamp.toDate();
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const formatDate = (timestamp) => {
        if (!timestamp) return '';
        const date = timestamp instanceof Date ? timestamp : timestamp.toDate();
        const today = new Date();
        const messageDate = new Date(date);

        if (messageDate.toDateString() === today.toDateString()) {
            return 'Today';
        }

        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        if (messageDate.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        }

        return messageDate.toLocaleDateString();
    };

    const handleReaction = async (messageId, emoji) => {
        try {
            await messageService.addReaction(channelId, messageId, emoji);
        } catch (error) {
            console.error('Error adding reaction:', error);
        }
    };

    const handleDeleteMessage = async (messageId) => {
        if (window.confirm('Are you sure you want to delete this message?')) {
            try {
                await messageService.deleteMessage(channelId, messageId);
            } catch (error) {
                console.error('Error deleting message:', error);
            }
        }
    };

    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className="text-discord-gray-300">Loading messages...</div>
            </div>
        );
    }

    const groupedMessages = [];
    let currentGroup = null;

    messages.forEach((message) => {
        const shouldGroup = currentGroup &&
            currentGroup.authorId === message.authorId &&
            currentGroup.messages[currentGroup.messages.length - 1].timestamp &&
            message.timestamp &&
            (message.timestamp - currentGroup.messages[currentGroup.messages.length - 1].timestamp) < 5 * 60 * 1000; // 5 minutes

        if (shouldGroup) {
            currentGroup.messages.push(message);
        } else {
            currentGroup = {
                authorId: message.authorId,
                authorName: message.authorName,
                timestamp: message.timestamp,
                messages: [message]
            };
            groupedMessages.push(currentGroup);
        }
    });

    return (
        <div className="flex-1 overflow-y-auto p-4">
            {groupedMessages.map((group, groupIndex) => (
                <div key={groupIndex} className="message-hover mb-4 group">
                    {/* Message Group Header */}
                    <div className="flex items-start space-x-3">
                        {/* Avatar */}
                        <div className="w-10 h-10 rounded-full bg-discord-blurple flex items-center justify-center flex-shrink-0">
                            <span className="text-sm font-medium text-white">
                                {group.authorName?.charAt(0)?.toUpperCase() || 'U'}
                            </span>
                        </div>

                        <div className="flex-1 min-w-0">
                            {/* Author and Timestamp */}
                            <div className="flex items-baseline space-x-2 mb-1">
                                <span className="font-medium text-white">
                                    {group.authorName || 'Anonymous'}
                                </span>
                                <span className="text-xs text-discord-gray-400">
                                    {formatDate(group.timestamp)} at {formatTime(group.timestamp)}
                                </span>
                            </div>

                            {/* Messages */}
                            {group.messages.map((message) => (
                                <div
                                    key={message.id}
                                    className="relative group-hover:bg-discord-darkest rounded p-1 -mx-1"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <p className="text-discord-gray-100 whitespace-pre-wrap break-words">
                                                {message.content}
                                            </p>
                                            {message.edited && (
                                                <span className="text-xs text-discord-gray-400 ml-1">
                                                    (edited)
                                                </span>
                                            )}
                                        </div>

                                        {/* Message Actions */}
                                        {currentUser?.uid === message.authorId && (
                                            <div className="opacity-0 group-hover:opacity-100 flex space-x-1 ml-2">
                                                <button
                                                    onClick={() => handleDeleteMessage(message.id)}
                                                    className="text-discord-gray-400 hover:text-discord-red p-1 rounded"
                                                    title="Delete message"
                                                >
                                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                        <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 012 0v4a1 1 0 11-2 0V7zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V7a1 1 0 00-1-1z" clipRule="evenodd" />
                                                    </svg>
                                                </button>
                                            </div>
                                        )}
                                    </div>

                                    {/* Reactions */}
                                    {message.reactions && Object.keys(message.reactions).length > 0 && (
                                        <div className="flex flex-wrap gap-1 mt-2">
                                            {Object.entries(message.reactions).map(([emoji, users]) =>
                                                users.length > 0 ? (
                                                    <button
                                                        key={emoji}
                                                        onClick={() => handleReaction(message.id, emoji)}
                                                        className={`reaction flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${users.includes(currentUser?.uid)
                                                                ? 'bg-discord-blurple text-white'
                                                                : 'bg-discord-darkest text-discord-gray-300 hover:bg-discord-gray-500'
                                                            }`}
                                                    >
                                                        <span>{emoji}</span>
                                                        <span>{users.length}</span>
                                                    </button>
                                                ) : null
                                            )}
                                        </div>
                                    )}

                                    {/* Quick Reactions */}
                                    <div className="opacity-0 group-hover:opacity-100 absolute right-0 top-0 flex space-x-1 bg-discord-dark border border-discord-darkest rounded p-1">
                                        {['👍', '❤️', '😂', '😮', '😢', '😡'].map((emoji) => (
                                            <button
                                                key={emoji}
                                                onClick={() => handleReaction(message.id, emoji)}
                                                className="text-discord-gray-400 hover:text-white p-1 rounded text-sm"
                                                title={`React with ${emoji}`}
                                            >
                                                {emoji}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            ))}

            {messages.length === 0 && (
                <div className="flex-1 flex items-center justify-center">
                    <div className="text-center text-discord-gray-400">
                        <h3 className="text-lg font-medium mb-2">No messages yet</h3>
                        <p>Be the first to send a message!</p>
                    </div>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
};

export default MessageList; 