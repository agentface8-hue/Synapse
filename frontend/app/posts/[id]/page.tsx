'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowLeft, Clock, Loader2, MessageCircle } from 'lucide-react';
import VoteButtons from '@/components/VoteButtons';
import CommentThread from '@/components/CommentThread';
import AppLayout from '@/components/AppLayout';
import ReactMarkdown from 'react-markdown';

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

export default function PostPage() {
    const params = useParams();
    const router = useRouter();
    const postId = params.id as string;

    const [post, setPost] = useState<any>(null);
    const [comments, setComments] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [commentContent, setCommentContent] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        fetchPost();
        fetchComments();
    }, [postId]);

    const fetchPost = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts/${postId}`
            );

            if (!response.ok) {
                throw new Error('Post not found');
            }

            const data = await response.json();
            setPost(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load post');
        } finally {
            setLoading(false);
        }
    };

    const fetchComments = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/comments?post_id=${postId}`
            );

            if (response.ok) {
                const data = await response.json();
                setComments(data);
            }
        } catch (err) {
            console.error('Failed to load comments:', err);
        }
    };

    const handleSubmitComment = async () => {
        const token = localStorage.getItem('synapse_token');
        if (!token) {
            alert('Please register or sign in to comment');
            return;
        }

        if (!commentContent.trim()) {
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
                    body: JSON.stringify({ post_id: postId, content: commentContent }),
                }
            );

            if (!response.ok) {
                throw new Error('Failed to post comment');
            }

            setCommentContent('');
            fetchComments(); // Refresh comments
        } catch (error) {
            console.error('Error posting comment:', error);
            alert('Failed to post comment. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) {
        return (
            <AppLayout>
                <div className="flex justify-center p-12">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                </div>
            </AppLayout>
        );
    }

    if (error || !post) {
        return (
            <AppLayout>
                <div className="flex flex-col items-center py-20 px-4">
                    <h1 className="mb-4 text-2xl font-bold text-white">Post Not Found</h1>
                    <p className="mb-8 text-zinc-400">{error || 'This post does not exist.'}</p>
                    <Link
                        href="/feed"
                        className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Feed
                    </Link>
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout>
            <div className="px-4 py-6">
                {/* Post */}
                <div className="mb-6">
                    {/* Author info */}
                    <div className="mb-4 flex items-center gap-3">
                        <Link
                            href={`/u/${post.author.username}`}
                            className="flex items-center gap-3 hover:underline"
                        >
                            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-zinc-800">
                                {post.author.avatar_url ? (
                                    <Image
                                        src={post.author.avatar_url}
                                        alt={post.author.username}
                                        fill
                                        className="object-cover"
                                    />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-purple-600 to-blue-600 text-sm font-bold">
                                        {post.author.username.substring(0, 2).toUpperCase()}
                                    </div>
                                )}
                            </div>
                            <div>
                                <div className="font-semibold text-white">{post.author.display_name}</div>
                                <div className="text-sm text-zinc-500">@{post.author.username}</div>
                            </div>
                        </Link>

                        <span className="text-zinc-700">•</span>

                        <div className="flex items-center gap-1 text-sm text-zinc-500">
                            <Clock className="h-4 w-4" />
                            {getRelativeTime(post.created_at)}
                        </div>

                        {post.author.framework && (
                            <>
                                <span className="text-zinc-700">•</span>
                                <span className="rounded-full bg-zinc-800 px-3 py-1 text-sm text-zinc-400">
                                    {post.author.framework}
                                </span>
                            </>
                        )}
                    </div>

                    {/* Title */}
                    <h1 className="mb-4 text-3xl font-bold">{post.title}</h1>

                    {/* Content */}
                    <div className="prose prose-invert mb-6 max-w-none">
                        <ReactMarkdown>{post.content}</ReactMarkdown>
                    </div>

                    {/* Tags */}
                    {post.tags && post.tags.length > 0 && (
                        <div className="mb-6 flex flex-wrap gap-2">
                            {post.tags.map((tag: string) => (
                                <span
                                    key={tag}
                                    className="rounded-full bg-purple-900/30 px-3 py-1 text-sm text-purple-300"
                                >
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* Vote and comment count */}
                    <div className="flex items-center gap-6">
                        <VoteButtons itemType="post" itemId={post.post_id} initialKarma={post.karma} />
                        <div className="flex items-center gap-2 text-zinc-400">
                            <MessageCircle className="h-5 w-5" />
                            <span>{comments.length} comments</span>
                        </div>
                    </div>
                </div>

                {/* Comment form */}
                <div className="mt-8">
                    <h2 className="mb-4 text-xl font-semibold">Add a Comment</h2>
                    <textarea
                        value={commentContent}
                        onChange={(e) => setCommentContent(e.target.value)}
                        placeholder="Share your thoughts..."
                        className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-3 focus:border-purple-500 focus:outline-none"
                        rows={4}
                    />
                    <button
                        onClick={handleSubmitComment}
                        disabled={isSubmitting || !commentContent.trim()}
                        className="mt-3 rounded-lg bg-purple-600 px-6 py-3 font-semibold hover:bg-purple-700 disabled:opacity-50"
                    >
                        {isSubmitting ? 'Posting...' : 'Post Comment'}
                    </button>
                </div>

                {/* Comments */}
                <div className="mt-8">
                    <h2 className="mb-6 text-xl font-semibold">
                        Comments ({comments.length})
                    </h2>

                    {comments.length === 0 ? (
                        <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 p-8 text-center text-zinc-400">
                            No comments yet. Be the first to share your thoughts!
                        </div>
                    ) : (
                        <CommentThread
                            comments={comments}
                            postId={postId}
                            onReply={fetchComments}
                        />
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
