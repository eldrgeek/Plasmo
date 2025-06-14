import React from 'react';

const Header = ({ channel, onToggleSidebar }) => {
    return (
        <div className="bg-discord-dark border-b border-discord-darkest p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
                {/* Mobile Menu Button */}
                <button
                    onClick={onToggleSidebar}
                    className="lg:hidden text-discord-gray-300 hover:text-white p-1"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                </button>

                {/* Channel Info */}
                {channel && (
                    <div className="flex items-center space-x-2">
                        <div className="text-discord-gray-300">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <h2 className="text-white font-semibold text-lg">
                            {channel.name}
                        </h2>
                        {channel.description && (
                            <span className="text-discord-gray-300 text-sm">
                                {channel.description}
                            </span>
                        )}
                    </div>
                )}
            </div>

            {/* Header Actions */}
            <div className="flex items-center space-x-2">
                {/* Channel Settings (for future features) */}
                {channel && (
                    <button className="text-discord-gray-300 hover:text-white p-2 rounded">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                        </svg>
                    </button>
                )}
            </div>
        </div>
    );
};

export default Header; 