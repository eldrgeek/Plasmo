import React, { useState, useRef } from 'react';
import { messageService } from '../../services/messageService';

const MessageInput = ({ channelId, placeholder = "Type a message..." }) => {
    const [message, setMessage] = useState('');
    const [sending, setSending] = useState(false);
    const textareaRef = useRef(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const trimmedMessage = message.trim();
        if (!trimmedMessage || sending) return;

        try {
            setSending(true);
            await messageService.sendMessage(channelId, trimmedMessage);
            setMessage('');
            // Reset textarea height
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setSending(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleTextareaChange = (e) => {
        setMessage(e.target.value);

        // Auto-resize textarea
        const textarea = e.target;
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    };

    return (
        <div className="p-4 bg-discord-dark">
            <form onSubmit={handleSubmit} className="relative">
                <div className="relative">
                    <textarea
                        ref={textareaRef}
                        value={message}
                        onChange={handleTextareaChange}
                        onKeyPress={handleKeyPress}
                        placeholder={placeholder}
                        disabled={sending}
                        className="message-input w-full resize-none overflow-hidden"
                        rows="1"
                    />

                    {/* Send Button */}
                    <button
                        type="submit"
                        disabled={!message.trim() || sending}
                        className="absolute right-3 bottom-3 w-8 h-8 bg-discord-blurple hover:bg-blue-700 disabled:bg-discord-gray-500 disabled:cursor-not-allowed rounded-full flex items-center justify-center transition-colors"
                    >
                        {sending ? (
                            <svg className="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        ) : (
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                            </svg>
                        )}
                    </button>
                </div>

                {/* Typing Hint */}
                <div className="mt-2 text-xs text-discord-gray-400">
                    <span className="font-medium">Shift + Enter</span> to add a new line
                </div>
            </form>
        </div>
    );
};

export default MessageInput; 