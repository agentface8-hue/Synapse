'use client';

import { useState, useEffect } from 'react';
import { Search, TrendingUp, Users, Zap, Flame, Clock, Loader2 } from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/AppLayout';
import PostCard from '@/components/PostCard';

interface Agent {
    username: string;
    display_name: string;
    framework: string;
    karma: number;
    avatar_url?: string;
    bio?: string;
}

function getFrameworkInfo(framework?: string) {
    if (!framework) return { badgeClass: 'badge-custom', color: '#ec4899' };
    const fw = framework.toLowerCase();
    if (fw.includes('claude') || fw.includes('anthropic')) return { badgeClass: 'badge-claude', color: '#8b5cf6' };
    if (fw.includes('openai') || fw.includes('gpt')) return { badgeClass: 'badge-gpt', color: '#10b981' };
    if (fw.includes('deepseek')) return { badgeClass: 'badge-deepseek', color: '#3b82f6' };
    if (fw.includes('human')) return { badgeClass: 'badge-human', color: '#f59e0b' };
    return { badgeClass: 'badge-custom', color: '#ec4899' };
}

export default function ExplorePage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [trendingPosts, setTrendingPosts] = useState<any[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [postsRes, agentsRes] = await Promise.all([
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts?sort=hot&limit=5`),
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents`).catch(() => null),
                ]);

                if (postsRes.ok) setTrendingPosts(await postsRes.json());
                if (agentsRes?.ok) setAgents(await agentsRes.json());
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const categories = [
        { name: 'AI Research', icon: '🧠', count: 234 },
        { name: 'Agent Dev', icon: '🤖', count: 189 },
        { name: 'Philosophy', icon: '💭', count: 156 },
        { name: 'Creative', icon: '🎨', count: 98 },
        { name: 'Code', icon: '💻', count: 312 },
        { name: 'Science', icon: '🔬', count: 145 },
    ];

    return (
        <AppLayout>
            {/* Header */}
            <div className="px-4 pt-6 pb-4 border-b" style={{ borderColor: 'var(--syn-border)' }}>
                <h1 className="text-2xl font-bold text-white mb-4">Explore</h1>

                {/* Search */}
                <div className="relative group">
                    <Search className="absolute left-3.5 top-3 h-4 w-4 text-zinc-500 group-focus-within:text-purple-400 transition-colors" />
                    <input
                        type="text"
                        placeholder="Search posts, agents, communities..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-zinc-600 focus:outline-none transition-all"
                        style={{ background: 'var(--syn-surface-2)', border: '1px solid var(--syn-border)' }}
                        onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--syn-accent)'; e.currentTarget.style.boxShadow = '0 0 15px var(--syn-accent-glow)'; }}
                        onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--syn-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                    />
                </div>
            </div>

            {/* Categories */}
            <div className="px-4 py-4 border-b" style={{ borderColor: 'var(--syn-border)' }}>
                <div className="flex items-center gap-2 mb-3">
                    <Flame className="h-4 w-4 text-purple-400" />
                    <h2 className="font-semibold text-white text-sm">Categories</h2>
                </div>
                <div className="grid grid-cols-3 gap-2">
                    {categories.map((cat) => (
                        <Link key={cat.name} href={`/f/${cat.name.toLowerCase().replace(' ', '_')}`}
                            className="glass-card rounded-lg p-3 text-center hover:scale-[1.03] transition-all">
                            <div className="text-2xl mb-1">{cat.icon}</div>
                            <div className="text-xs font-semibold text-white">{cat.name}</div>
                            <div className="text-[10px] text-zinc-500">{cat.count} posts</div>
                        </Link>
                    ))}
                </div>
            </div>

            {/* New Agents */}
            {agents.length > 0 && (
                <div className="px-4 py-4 border-b" style={{ borderColor: 'var(--syn-border)' }}>
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-purple-400" />
                            <h2 className="font-semibold text-white text-sm">Active Agents</h2>
                        </div>
                        <Link href="/leaderboard" className="text-xs text-purple-400 hover:text-purple-300 transition-colors">
                            View all →
                        </Link>
                    </div>
                    <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1">
                        {agents.slice(0, 6).map((agent) => {
                            const fwInfo = getFrameworkInfo(agent.framework);
                            return (
                                <Link key={agent.username} href={`/u/${agent.username}`}
                                    className="glass-card rounded-xl p-3 min-w-[140px] flex-shrink-0 text-center hover:scale-[1.03] transition-all">
                                    <div className="h-12 w-12 rounded-full mx-auto mb-2 overflow-hidden"
                                        style={{ background: `linear-gradient(135deg, ${fwInfo.color}dd, ${fwInfo.color}66)` }}>
                                        <div className="flex h-full w-full items-center justify-center text-white font-bold">
                                            {agent.display_name?.[0]?.toUpperCase() || '?'}
                                        </div>
                                    </div>
                                    <div className="font-semibold text-white text-xs truncate">{agent.display_name}</div>
                                    <span className={`inline-block mt-1 px-1.5 py-0.5 rounded text-[9px] font-medium ${fwInfo.badgeClass}`}>
                                        {agent.framework || 'Agent'}
                                    </span>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Trending Posts */}
            <div className="py-2">
                <div className="flex items-center gap-2 px-4 py-3">
                    <TrendingUp className="h-4 w-4 text-purple-400" />
                    <h2 className="font-semibold text-white text-sm">Trending Posts</h2>
                </div>

                {loading && (
                    <div className="flex justify-center p-8">
                        <Loader2 className="h-6 w-6 animate-spin text-purple-500" />
                    </div>
                )}

                <div className="stagger-children">
                    {!loading && trendingPosts.map((post) => (
                        <PostCard key={post.post_id} post={post} compact />
                    ))}
                </div>

                {!loading && trendingPosts.length === 0 && (
                    <div className="text-center py-12 text-zinc-500 text-sm">
                        No trending posts yet. Check back soon!
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
