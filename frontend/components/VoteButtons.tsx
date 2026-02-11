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

    const handleVote = async (e: React.MouseEvent, voteType: 'upvote' | 'downvote') => {
        e.preventDefault();
        e.stopPropagation();

        const token = localStorage.getItem('synapse_token');
        if (!token) {
            alert('Please register or sign in to vote');
            return;
        }

        if (isVoting) return;
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

            // Toggle vote: if same vote again, remove it
            if (userVote === voteType) {
                setUserVote(null);
                setKarma(initialKarma);
            } else {
                const newKarma = data.karma ?? karma + (voteType === 'upvote' ? 1 : -1);
                setKarma(newKarma);
                setUserVote(voteType);
                if (onVoteChange) onVoteChange(newKarma);
            }
        } catch (error) {
            console.error('Error voting:', error);
        } finally {
            setIsVoting(false);
        }
    };

    return (
        <div className="flex flex-col items-center gap-0.5">
            <button
                type="button"
                onClick={(e) => handleVote(e, 'upvote')}
                disabled={isVoting}
                className={`rounded-md p-1.5 transition-all duration-150 ${userVote === 'upvote'
                    ? 'bg-purple-600/20 text-purple-400 scale-110'
                    : 'text-zinc-500 hover:bg-white/10 hover:text-purple-400'
                    } ${isVoting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                title="Upvote"
            >
                <ArrowUp className="h-5 w-5" />
            </button>

            <span
                className={`text-xs font-bold tabular-nums ${karma > 0 ? 'text-purple-400' : karma < 0 ? 'text-red-400' : 'text-zinc-500'
                    }`}
            >
                {karma}
            </span>

            <button
                type="button"
                onClick={(e) => handleVote(e, 'downvote')}
                disabled={isVoting}
                className={`rounded-md p-1.5 transition-all duration-150 ${userVote === 'downvote'
                    ? 'bg-red-600/20 text-red-400 scale-110'
                    : 'text-zinc-500 hover:bg-white/10 hover:text-red-400'
                    } ${isVoting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                title="Downvote"
            >
                <ArrowDown className="h-5 w-5" />
            </button>
        </div>
    );
}
