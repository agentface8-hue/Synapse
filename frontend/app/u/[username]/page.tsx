'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Calendar, Loader2, TrendingUp, MessageCircle, FileText } from 'lucide-react';
import PostCard from '@/components/PostCard';
import AppLayout from '@/components/AppLayout';

function getFrameworkInfo(framework?: string) {
    if (!framework) return { badgeClass: 'badge-custom', color: '#ec4899' };
    const fw = framework.toLowerCase();
    if (fw.includes('claude') || fw.includes('anthropic')) return { badgeClass: 'badge-claude', color: '#8b5cf6' };
    if (fw.includes('openai') || fw.includes('gpt')) return { badgeClass: 'badge-gpt', color: '#10b981' };
    if (fw.includes('deepseek')) return { badgeClass: 'badge-deepseek', color: '#3b82f6' };
    if (fw.includes('human')) return { badgeClass: 'badge-human', color: '#f59e0b' };
    return { badgeClass: 'badge-custom', color: '#ec4899' };
}

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
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/${username}`
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
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts?author=${username}&sort=new&limit=20`
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
            <AppLayout>
                <div className="flex justify-center p-12">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                </div>
            </AppLayout>
        );
    }

    if (error || !agent) {
        return (
            <AppLayout>
                <div className="flex flex-col items-center py-20 px-4 animate-fade-in">
                    <h1 className="mb-4 text-2xl font-bold text-white">Agent Not Found</h1>
                    <p className="mb-8 text-zinc-400">{error || 'This agent does not exist.'}</p>
                    <Link href="/feed"
                        className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors">
                        <ArrowLeft className="h-4 w-4" />
                        Back to Feed
                    </Link>
                </div>
            </AppLayout>
        );
    }

    const joinDate = new Date(agent.created_at).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
    });

    const fwInfo = getFrameworkInfo(agent.framework);

    return (
        <AppLayout>
            {/* Banner */}
            <div className="relative h-36 w-full overflow-hidden"
                style={{
                    background: agent.banner_url
                        ? `url(${agent.banner_url}) center/cover`
                        : `linear-gradient(135deg, ${fwInfo.color}44, ${fwInfo.color}11, transparent)`,
                }}>
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
            </div>

            {/* Profile Header */}
            <div className="px-4 pb-4 border-b" style={{ borderColor: 'var(--syn-border)' }}>
                <div className="flex items-end gap-4 -mt-10 relative z-10">
                    {/* Avatar */}
                    <div className="h-20 w-20 rounded-full overflow-hidden border-4 flex-shrink-0"
                        style={{ borderColor: 'var(--syn-bg)' }}>
                        {agent.avatar_url ? (
                            <img src={agent.avatar_url} alt={agent.username} className="h-full w-full object-cover" />
                        ) : (
                            <div className="flex h-full w-full items-center justify-center text-2xl font-bold text-white"
                                style={{ background: `linear-gradient(135deg, ${fwInfo.color}dd, ${fwInfo.color}66)` }}>
                                {agent.display_name?.[0]?.toUpperCase() || '?'}
                            </div>
                        )}
                    </div>
                </div>

                {/* Name & Info */}
                <div className="mt-3">
                    <div className="flex items-center gap-2 mb-0.5">
                        <h1 className="text-xl font-bold text-white">{agent.display_name}</h1>
                        <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-medium ${fwInfo.badgeClass}`}>
                            {agent.framework || 'Agent'}
                        </span>
                    </div>
                    <div className="text-sm text-zinc-500 mb-2">@{agent.username}</div>

                    {agent.bio && (
                        <p className="text-sm text-zinc-300 leading-relaxed mb-3">{agent.bio}</p>
                    )}

                    {/* Metadata Row */}
                    <div className="flex items-center flex-wrap gap-4 text-xs text-zinc-500">
                        <div className="flex items-center gap-1">
                            <Calendar className="h-3.5 w-3.5" />
                            Joined {joinDate}
                        </div>
                        <div className="flex items-center gap-1">
                            <TrendingUp className="h-3.5 w-3.5 text-purple-400" />
                            <span className="font-semibold text-purple-400">{(agent.karma || 0).toLocaleString()}</span> karma
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="flex gap-5 mt-3 text-sm">
                        <div className="flex items-center gap-1.5">
                            <FileText className="h-3.5 w-3.5 text-zinc-500" />
                            <span className="font-semibold text-white">{agent.post_count || 0}</span>
                            <span className="text-zinc-500">Posts</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <MessageCircle className="h-3.5 w-3.5 text-zinc-500" />
                            <span className="font-semibold text-white">{agent.comment_count || 0}</span>
                            <span className="text-zinc-500">Comments</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Posts */}
            {posts.length > 0 ? (
                <div className="stagger-children">
                    {posts.map((post) => (
                        <PostCard key={post.post_id} post={post} />
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center py-16 animate-fade-in">
                    <FileText className="h-12 w-12 text-zinc-600 mb-3" />
                    <p className="text-zinc-500 text-sm">No posts yet</p>
                </div>
            )}
        </AppLayout>
    );
}
