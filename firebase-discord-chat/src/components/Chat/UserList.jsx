import React, { useState, useEffect } from 'react';
import { channelService } from '../../services/channelService';

const UserList = ({ channelId }) => {
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!channelId) return;

        const fetchMembers = async () => {
            try {
                setLoading(true);
                const membersData = await channelService.getChannelMembers(channelId);
                setMembers(membersData);
            } catch (error) {
                console.error('Error fetching channel members:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchMembers();
    }, [channelId]);

    const getStatusColor = (status) => {
        switch (status) {
            case 'online':
                return 'bg-discord-green';
            case 'away':
                return 'bg-discord-yellow';
            case 'offline':
            default:
                return 'bg-discord-gray-400';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'online':
                return 'Online';
            case 'away':
                return 'Away';
            case 'offline':
            default:
                return 'Offline';
        }
    };

    if (loading) {
        return (
            <div className="p-4">
                <div className="text-discord-gray-300 text-sm">Loading members...</div>
            </div>
        );
    }

    const onlineMembers = members.filter(member => member.status === 'online');
    const awayMembers = members.filter(member => member.status === 'away');
    const offlineMembers = members.filter(member => member.status === 'offline');

    const MemberGroup = ({ title, members, showStatus = true }) => {
        if (members.length === 0) return null;

        return (
            <div className="mb-4">
                <h4 className="text-discord-gray-300 text-xs font-medium uppercase tracking-wide mb-2">
                    {title} — {members.length}
                </h4>
                <div className="space-y-1">
                    {members.map((member) => (
                        <div
                            key={member.id}
                            className="flex items-center space-x-2 p-1 rounded hover:bg-discord-darkest cursor-pointer"
                        >
                            {/* Avatar with Status */}
                            <div className="relative">
                                <div className="w-8 h-8 rounded-full bg-discord-blurple flex items-center justify-center">
                                    <span className="text-xs font-medium text-white">
                                        {member.username?.charAt(0)?.toUpperCase() || 'U'}
                                    </span>
                                </div>
                                {showStatus && (
                                    <div
                                        className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-discord-darker ${getStatusColor(
                                            member.status
                                        )}`}
                                    />
                                )}
                            </div>

                            {/* User Info */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-1">
                                    <span className="text-sm text-white truncate">
                                        {member.username || 'Anonymous'}
                                    </span>
                                </div>
                                {showStatus && (
                                    <div className="text-xs text-discord-gray-400">
                                        {getStatusText(member.status)}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="p-4 h-full overflow-y-auto">
            <h3 className="text-discord-gray-300 text-sm font-medium uppercase tracking-wide mb-4">
                Members
            </h3>

            <MemberGroup title="Online" members={onlineMembers} />
            <MemberGroup title="Away" members={awayMembers} />
            <MemberGroup title="Offline" members={offlineMembers} />

            {members.length === 0 && (
                <div className="text-center text-discord-gray-400 py-8">
                    <p className="text-sm">No members found</p>
                </div>
            )}
        </div>
    );
};

export default UserList; 