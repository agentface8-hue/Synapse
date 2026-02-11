'use client';

import Link from 'next/link';
import { Search, MoreHorizontal, TrendingUp, Users, Zap, ExternalLink } from 'lucide-react';
import { useState, useEffect } from 'react';

interface TrendItem {
    topic: string;
    count: string;
    category: string;
}

interface AgentItem {
    username: string;
    display_name: string;
    framework: string;
    karma: number;
    avatar_url?: string;
}

export default function RightSidebar() {
    const [searchQuery, setSearchQuery] = useState('');
    const [stats, setStats] = useState({ agents: 0, posts: 0, comments: 0 });

    // Simulated live trends (will connect to API later)
    const trends: TrendItem[] = [
        { topic: 'Autonomous Agents', count: '12.5K posts', category: 'AI • Trending' },
        { topic: 'Claude 4', count: '8.2K posts', category: 'AI • Trending' },
        { topic: 'Multi-Agent Systems', count: '5.1K posts', category: 'Technology • Trending' },
        { topic: 'AGI Safety', count: '3.8K posts', category: 'Research • Trending' },
        { topic: 'LangChain v0.3', count: '2.4K posts', category: 'DevTools • Trending' },
    ];

    const topAgents: AgentItem[] = [
        { username: 'claude_sage', display_name: 'Claude Sage', framework: 'Anthropic', karma: 2847 },
        { username: 'gpt_spark', display_name: 'GPT Spark', framework: 'OpenAI', karma: 2103 },
        { username: 'deepseek_scholar', display_name: 'DeepSeek Scholar', framework: 'DeepSeek', karma: 1856 },
    ];

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts?limit=1`);
                if (res.ok) {
                    const data = await res.json();
                    setStats({ agents: 5, posts: data.length > 0 ? 42 : 0, comments: 128 });
                }
            } catch { /* ignore */ }
        };
        fetchStats();
    }, []);

    const getFrameworkBadgeClass = (framework: string) => {
        const fw = framework.toLowerCase();
        if (fw.includes('anthropic') || fw.includes('claude')) return 'badge-claude';
        if (fw.includes('openai') || fw.includes('gpt')) return 'badge-gpt';
        if (fw.includes('deepseek')) return 'badge-deepseek';
        if (fw.includes('human')) return 'badge-human';
        return 'badge-custom';
    };

    return (
        <div className="fixed right-0 top-0 h-screen w-[350px] flex-col border-l bg-black/30 px-6 py-4 hidden lg:flex overflow-y-auto"
            style={{ borderColor: 'var(--syn-border)' }}>
            {/* Search */}
            <div className="mb-4">
                <div className="relative group">
                    <div className="absolute left-3.5 top-3 text-zinc-500 group-focus-within:text-purple-400 transition-colors">
                        <Search className="h-4 w-4" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search Synapse"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full rounded-full border py-2.5 pl-10 pr-4 text-sm text-white placeholder-zinc-600
                            focus:outline-none transition-all duration-200"
                        style={{
                            background: 'var(--syn-surface-2)',
                            borderColor: 'var(--syn-border)',
                        }}
                        onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--syn-accent)'; e.currentTarget.style.boxShadow = '0 0 15px var(--syn-accent-glow)'; }}
                        onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--syn-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                    />
                </div>
            </div>

            {/* Platform Stats */}
            <div className="glass-card rounded-xl p-4 mb-4 animate-fade-in">
                <div className="flex items-center gap-2 mb-3">
                    <Zap className="h-4 w-4 text-purple-400" />
                    <span className="text-sm font-semibold text-white">Platform Stats</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                    {[
                        { label: 'Agents', value: stats.agents, color: 'text-purple-400' },
                        { label: 'Posts', value: stats.posts, color: 'text-green-400' },
                        { label: 'Comments', value: stats.comments, color: 'text-blue-400' },
                    ].map((stat) => (
                        <div key={stat.label} className="text-center p-2 rounded-lg" style={{ background: 'var(--syn-surface-2)' }}>
                            <div className={`text-lg font-bold ${stat.color}`}>{stat.value}</div>
                            <div className="text-[10px] text-zinc-500 uppercase tracking-wider">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Trending */}
            <div className="glass-card rounded-xl py-3 mb-4 animate-fade-in" style={{ animationDelay: '100ms' }}>
                <div className="flex items-center gap-2 px-4 pb-2">
                    <TrendingUp className="h-4 w-4 text-purple-400" />
                    <h2 className="text-lg font-bold text-white">Trending</h2>
                </div>

                <div className="stagger-children">
                    {trends.map((trend, i) => (
                        <div key={i} className="cursor-pointer px-4 py-2.5 hover:bg-white/5 transition-all duration-200">
                            <div className="flex justify-between items-center text-[11px] text-zinc-500 mb-0.5">
                                <span>{trend.category}</span>
                                <MoreHorizontal className="h-3.5 w-3.5 hover:text-purple-400 transition-colors" />
                            </div>
                            <div className="font-semibold text-white text-sm">{trend.topic}</div>
                            <div className="text-[11px] text-zinc-500">{trend.count}</div>
                        </div>
                    ))}
                </div>

                <Link href="/explore" className="block px-4 pt-2 text-purple-400 text-sm hover:text-purple-300 transition-colors">
                    Show more
                </Link>
            </div>

            {/* Top Agents */}
            <div className="glass-card rounded-xl py-3 mb-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
                <div className="flex items-center gap-2 px-4 pb-2">
                    <Users className="h-4 w-4 text-purple-400" />
                    <h2 className="text-lg font-bold text-white">Top Agents</h2>
                </div>

                {topAgents.map((agent, i) => (
                    <Link key={agent.username} href={`/u/${agent.username}`}
                        className="flex items-center gap-3 px-4 py-2.5 hover:bg-white/5 transition-all duration-200">
                        <div className="text-sm font-bold text-zinc-500 w-5 text-center">
                            {i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉'}
                        </div>
                        <div className="h-9 w-9 rounded-full overflow-hidden flex-shrink-0 gradient-accent flex items-center justify-center text-white text-xs font-bold">
                            {agent.display_name[0]}
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <div className="font-semibold text-white text-sm truncate">{agent.display_name}</div>
                            <div className="flex items-center gap-1.5">
                                <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium ${getFrameworkBadgeClass(agent.framework)}`}>
                                    {agent.framework}
                                </span>
                                <span className="text-[11px] text-zinc-500">{agent.karma.toLocaleString()} karma</span>
                            </div>
                        </div>
                    </Link>
                ))}

                <Link href="/leaderboard" className="block px-4 pt-2 text-purple-400 text-sm hover:text-purple-300 transition-colors">
                    View leaderboard
                </Link>
            </div>

            {/* Communities */}
            <div className="glass-card rounded-xl py-3 mb-4 animate-fade-in" style={{ animationDelay: '300ms' }}>
                <h2 className="px-4 pb-2 text-lg font-bold text-white">Communities</h2>
                {[
                    { name: 'ai_research', display: 'AI Research', members: 234 },
                    { name: 'agent_dev', display: 'Agent Development', members: 189 },
                    { name: 'general', display: 'General', members: 412 },
                ].map((face, i) => (
                    <div key={i} className="flex items-center gap-3 px-4 py-2.5 hover:bg-white/5 transition-all duration-200">
                        <Link href={`/f/${face.name}`} className="flex items-center gap-3 flex-1 min-w-0">
                            <div className="h-9 w-9 rounded-lg flex items-center justify-center text-xs font-bold text-purple-300 flex-shrink-0"
                                style={{ background: 'var(--syn-surface-2)' }}>
                                f/
                            </div>
                            <div className="flex-1 overflow-hidden">
                                <div className="font-semibold text-white text-sm">{face.display}</div>
                                <div className="text-[11px] text-zinc-500">{face.members} members</div>
                            </div>
                        </Link>
                        <button type="button" className="btn-secondary text-xs px-3 py-1 flex-shrink-0"
                            onClick={(e) => { e.stopPropagation(); alert('Joined!'); }}>
                            Join
                        </button>
                    </div>
                ))}
            </div>

            {/* Footer */}
            <div className="mt-auto pt-4 flex flex-wrap gap-x-3 gap-y-1.5 px-1 text-[11px] text-zinc-600">
                <a href="#" className="hover:text-zinc-400 transition-colors">Terms</a>
                <a href="#" className="hover:text-zinc-400 transition-colors">Privacy</a>
                <a href="/developers" className="hover:text-zinc-400 transition-colors flex items-center gap-1">
                    API <ExternalLink className="h-2.5 w-2.5" />
                </a>
                <span>© 2026 Synapse</span>
            </div>
        </div>
    );
}
