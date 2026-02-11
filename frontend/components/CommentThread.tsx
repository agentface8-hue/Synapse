'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Reply } from 'lucide-react';
import VoteButtons from './VoteButtons';

interface Comment {
    comment_id: string;
    content: string;
    author: {
        username: string;
        display_name: string;
        avatar_url?: string;
    };
    karma: number;
    created_at: string;
    replies?: Comment[];
}

interface CommentThreadProps {
    comments: Comment[];
    postId: string;
    depth?: number;
    maxDepth?: number;
    onReply?: () => void;
}

function getRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

function CommentItem({
    comment,
    postId,
    depth = 0,
    maxDepth = 3,
    onReply,
}: {
    comment: Comment;
    postId: string;
    depth: number;
    maxDepth: number;
    onReply?: () => void;
}) {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const [replyContent, setReplyContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleReply = async () => {
        const token = localStorage.getItem('synapse_token');
        if (!token) {
            alert('Please register or sign in to reply');
            return;
        }

        if (!replyContent.trim()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/comments`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        post_id: postId,
                        content: replyContent,
                        parent_comment_id: comment.comment_id,
                    }),
                }
            );

            if (!response.ok) {
                throw new Error('Failed to post reply');
            }

            setReplyContent('');
            setShowReplyForm(false);

            if (onReply) {
                onReply();
            }
        } catch (error) {
            console.error('Error posting reply:', error);
            alert('Failed to post reply. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={`${depth > 0 ? 'ml-8 border-l-2 border-zinc-800 pl-4' : ''}`}>
            <div className="group rounded-lg bg-zinc-900/30 p-4">
                {/* Author info */}
                <div className="mb-2 flex items-center gap-2">
                    <Link
                        href={`/u/${comment.author.username}`}
                        className="flex items-center gap-2 hover:underline"
                    >
                        <div className="relative h-6 w-6 overflow-hidden rounded-full bg-zinc-800">
                            {comment.author.avatar_url ? (
                                <Image
                                    src={comment.author.avatar_url}
                                    alt={comment.author.username}
                                    fill
                                    className="object-cover"
                                />
                            ) : (
                                <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-purple-600 to-blue-600 text-xs font-bold">
                                    {comment.author.username.substring(0, 2).toUpperCase()}
                                </div>
                            )}
                        </div>
                        <span className="text-sm font-medium text-white">
                            {comment.author.display_name}
                        </span>
                        <span className="text-sm text-zinc-500">@{comment.author.username}</span>
                    </Link>

                    <span className="text-zinc-700">•</span>
                    <span className="text-xs text-zinc-500">{getRelativeTime(comment.created_at)}</span>
                </div>

                {/* Content */}
                <p className="mb-3 text-sm text-zinc-300">{comment.content}</p>

                {/* Actions */}
                <div className="flex items-center gap-4">
                    <VoteButtons
                        itemType="comment"
                        itemId={comment.comment_id}
                        initialKarma={comment.karma}
                    />

                    {depth < maxDepth && (
                        <button
                            onClick={() => setShowReplyForm(!showReplyForm)}
                            className="flex items-center gap-1 text-xs text-zinc-500 hover:text-purple-400 transition-colors"
                        >
                            <Reply className="h-3 w-3" />
                            Reply
                        </button>
                    )}
                </div>

                {/* Reply form */}
                {showReplyForm && (
                    <div className="mt-4">
                        <textarea
                            value={replyContent}
                            onChange={(e) => setReplyContent(e.target.value)}
                            placeholder="Write a reply..."
                            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none"
                            rows={3}
                        />
                        <div className="mt-2 flex gap-2">
                            <button
                                onClick={handleReply}
                                disabled={isSubmitting || !replyContent.trim()}
                                className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold hover:bg-purple-700 disabled:opacity-50"
                            >
                                {isSubmitting ? 'Posting...' : 'Post Reply'}
                            </button>
                            <button
                                onClick={() => {
                                    setShowReplyForm(false);
                                    setReplyContent('');
                                }}
                                className="rounded-lg border border-zinc-700 px-4 py-2 text-sm font-semibold hover:bg-zinc-800"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Nested replies */}
            {comment.replies && comment.replies.length > 0 && (
                <div className="mt-2">
                    {comment.replies.map((reply) => (
                        <CommentItem
                            key={reply.comment_id}
                            comment={reply}
                            postId={postId}
                            depth={depth + 1}
                            maxDepth={maxDepth}
                            onReply={onReply}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

export default function CommentThread({
    comments,
    postId,
    depth = 0,
    maxDepth = 3,
    onReply,
}: CommentThreadProps) {
    return (
        <div className="space-y-4">
            {comments.map((comment) => (
                <CommentItem
                    key={comment.comment_id}
                    comment={comment}
                    postId={postId}
                    depth={depth}
                    maxDepth={maxDepth}
                    onReply={onReply}
                />
            ))}
        </div>
    );
}
