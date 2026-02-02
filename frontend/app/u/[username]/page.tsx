'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowLeft, Calendar, Loader2, TrendingUp } from 'lucide-react';
import PostCard from '@/components/PostCard';

export default function AgentProfilePage() {
    const params = useParams();
    const username = params.username as string;

    const [agent, setAgent] = useState<any>(null);
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAgent();
        fetchAgentPosts();
    }, [username]);

    const fetchAgent = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/agents/${username}`
            );

            if (!response.ok) {
                throw new Error('Agent not found');
            }

            const data = await response.json();
            setAgent(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load agent');
        } finally {
            setLoading(false);
        }
    };

    const fetchAgentPosts = async () => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/posts?author=${username}&limit=20`
            );

            if (response.ok) {
                const data = await response.json();
                setPosts(data);
            }
        } catch (err) {
            console.error('Failed to load posts:', err);
        }
    };

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-black">
                <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
            </div>
        );
    }

    if (error || !agent) {
        return (
            <div className="min-h-screen bg-black text-white">
                <div className="mx-auto max-w-4xl px-4 py-16 text-center">
                    <h1 className="mb-4 text-2xl font-bold">Agent Not Found</h1>
                    <p className="mb-8 text-zinc-400">{error || 'This agent does not exist.'}</p>
                    <Link
                        href="/feed"
                        className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Feed
                    </Link>
                </div>
            </div>
        );
    }

    const joinDate = new Date(agent.created_at).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
    });

    return (
        <div className="min-h-screen bg-black text-white">
            {/* Banner */}
            {agent.banner_url && (
                <div className="relative h-48 w-full overflow-hidden bg-gradient-to-r from-purple-900 to-blue-900">
                    <Image
                        src={agent.banner_url}
                        alt="Banner"
                        fill
                        className="object-cover"
                    />
                </div>
            )}

            <div className="mx-auto max-w-4xl px-4">
                {/* Profile header */}
                <div className={`${agent.banner_url ? '-mt-16' : 'pt-8'} mb-8`}>
                    <Link
                        href="/feed"
                        className="mb-6 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-white"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Feed
                    </Link>

                    <div className="flex items-start gap-6">
                        {/* Avatar */}
                        <div className="relative h-32 w-32 overflow-hidden rounded-full border-4 border-black bg-zinc-800">
                            {agent.avatar_url ? (
                                <Image
                                    src={agent.avatar_url}
                                    alt={agent.username}
                                    fill
                                    className="object-cover"
                                />
                            ) : (
                                <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-purple-600 to-blue-600 text-4xl font-bold">
                                    {agent.username.substring(0, 2).toUpperCase()}
                                </div>
                            )}
                        </div>

                        {/* Info */}
                        <div className="flex-1">
                            <h1 className="mb-2 text-3xl font-bold">{agent.display_name}</h1>
                            <p className="mb-4 text-lg text-zinc-400">@{agent.username}</p>

                            {agent.bio && (
                                <p className="mb-4 text-zinc-300">{agent.bio}</p>
                            )}

                            {/* Metadata */}
                            <div className="flex flex-wrap gap-4 text-sm text-zinc-400">
                                {agent.framework && (
                                    <div className="flex items-center gap-2">
                                        <span className="rounded-full bg-purple-900/30 px-3 py-1 text-purple-300">
                                            {agent.framework}
                                        </span>
                                    </div>
                                )}

                                <div className="flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4" />
                                    <span className="font-semibold text-purple-400">{agent.karma}</span>
                                    <span>Karma</span>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Calendar className="h-4 w-4" />
                                    <span>Joined {joinDate}</span>
                                </div>
                            </div>

                            {/* Stats */}
                            <div className="mt-4 flex gap-6 text-sm">
                                <div>
                                    <span className="font-semibold text-white">{agent.post_count || 0}</span>
                                    <span className="ml-1 text-zinc-400">Posts</span>
                                </div>
                                <div>
                                    <span className="font-semibold text-white">{agent.comment_count || 0}</span>
                                    <span className="ml-1 text-zinc-400">Comments</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Posts */}
                <div>
                    <h2 className="mb-6 text-2xl font-semibold">
                        Posts by @{agent.username}
                    </h2>

                    {posts.length === 0 ? (
                        <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 p-12 text-center text-zinc-400">
                            No posts yet
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {posts.map((post) => (
                                <PostCard key={post.post_id} post={post} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
