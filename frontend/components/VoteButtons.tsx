'use client';

import { useState } from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface VoteButtonsProps {
    itemType: 'post' | 'comment';
    itemId: string;
    initialKarma: number;
    initialUserVote?: 'upvote' | 'downvote' | null;
    onVoteChange?: (newKarma: number) => void;
}

export default function VoteButtons({
    itemType,
    itemId,
    initialKarma,
    initialUserVote = null,
    onVoteChange,
}: VoteButtonsProps) {
    const [karma, setKarma] = useState(initialKarma);
    const [userVote, setUserVote] = useState<'upvote' | 'downvote' | null>(initialUserVote);
    const [isVoting, setIsVoting] = useState(false);

    const handleVote = async (voteType: 'upvote' | 'downvote') => {
        // Check if user has Token
        const token = localStorage.getItem('synapse_token');
        if (!token) {
            alert('Please register or sign in to vote');
            return;
        }

        setIsVoting(true);

        try {
            const endpoint =
                itemType === 'post'
                    ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts/${itemId}/vote`
                    : `${process.env.NEXT_PUBLIC_API_URL}/api/v1/comments/${itemId}/vote`;

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ vote_type: voteType }),
            });

            if (!response.ok) {
                throw new Error('Failed to vote');
            }

            const data = await response.json();

            // Update local state
            const newKarma = data.karma || karma + (voteType === 'upvote' ? 1 : -1);
            setKarma(newKarma);
            setUserVote(voteType);

            if (onVoteChange) {
                onVoteChange(newKarma);
            }
        } catch (error) {
            console.error('Error voting:', error);
            alert('Failed to vote. Please try again.');
        } finally {
            setIsVoting(false);
        }
    };

    return (
        <div className="flex items-center gap-2">
            <button
                onClick={() => handleVote('upvote')}
                disabled={isVoting}
                className={`rounded p-1 transition-colors ${userVote === 'upvote'
                    ? 'bg-purple-600 text-white'
                    : 'text-zinc-500 hover:bg-zinc-800 hover:text-purple-400'
                    } ${isVoting ? 'opacity-50 cursor-not-allowed' : ''}`}
                title="Upvote"
            >
                <ArrowUp className="h-4 w-4" />
            </button>

            <span
                className={`min-w-[2rem] text-center text-sm font-semibold ${karma > 0 ? 'text-purple-400' : karma < 0 ? 'text-red-400' : 'text-zinc-500'
                    }`}
            >
                {karma}
            </span>

            <button
                onClick={() => handleVote('downvote')}
                disabled={isVoting}
                className={`rounded p-1 transition-colors ${userVote === 'downvote'
                    ? 'bg-red-600 text-white'
                    : 'text-zinc-500 hover:bg-zinc-800 hover:text-red-400'
                    } ${isVoting ? 'opacity-50 cursor-not-allowed' : ''}`}
                title="Downvote"
            >
                <ArrowDown className="h-4 w-4" />
            </button>
        </div>
    );
}
