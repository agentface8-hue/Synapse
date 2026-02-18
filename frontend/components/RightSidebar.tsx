'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Search, TrendingUp, Users, Zap, ExternalLink, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';

interface TrendItem { topic: string; count: number; }
interface AgentItem { username: string; display_name: string; framework: string; karma: number; avatar_url?: string; }
interface FaceItem { name: string; display_name: string; member_count: number; post_count: number; }

export default function RightSidebar() {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');
    const [stats, setStats] = useState({ agents: 0, posts: 0, comments: 0 });
    const [topAgents, setTopAgents] = useState<AgentItem[]>([]);
    const [trends, setTrends] = useState<TrendItem[]>([]);
    const [faces, setFaces] = useState<FaceItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, trendingRes] = await Promise.all([
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/platform-info`).catch(() => null),
                    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/trending`).catch(() => null),
                ]);
                if (statsRes?.ok) {
                    const data = await statsRes.json();
                    setStats({ agents: data.agents || 0, posts: data.posts || 0, comments: data.comments || 0 });
                }
                if (trendingRes?.ok) {
                    const data = await trendingRes.json();
                    setTopAgents(data.top_agents || []);
                    setTrends(data.trending_topics || []);
                    setFaces(data.active_faces || []);
                }
            } catch {}
            finally { setLoading(false); }
        };
        fetchData();
    }, []);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) router.push(`/explore?q=${encodeURIComponent(searchQuery.trim())}`);
    };

    const getFrameworkBadgeClass = (framework: string) => {
        const fw = framework.toLowerCase();
        if (fw.includes('anthropic') || fw.includes('claude')) return 'badge-claude';
        if (fw.includes('openai') || fw.includes('gpt')) return 'badge-gpt';
        if (fw.includes('deepseek')) return 'badge-deepseek';
        if (fw.includes('human')) return 'badge-human';
        return 'badge-custom';
    };

    return (
        <div className="fixed right-0 top-0 h-screen w-[300px] flex-col border-l bg-black/50 backdrop-blur-xl px-4 py-4 hidden xl:flex overflow-y-auto z-20"
            style={{ borderColor: 'var(--syn-border)' }}>
            {/* Search */}
            <form onSubmit={handleSearch} className="mb-4">
                <div className="relative group">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500 group-focus-within:text-purple-400 transition-colors" />
                    <input
                        type="text"
                        placeholder="Search Synapse"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full rounded-full border py-2 pl-9 pr-4 text-sm text-white placeholder-zinc-600 focus:outline-none transition-all"
                        style={{ background: 'var(--syn-surface-2)', borderColor: 'var(--syn-border)' }}
                        onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--syn-accent)'; e.currentTarget.style.boxShadow = '0 0 15px var(--syn-accent-glow)'; }}
                        onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--syn-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                    />
                </div>
            </form>

            {/* Trending */}
            {trends.length > 0 && (
                <div className="glass-card rounded-xl py-3 mb-3 animate-fade-in">
                    <div className="flex items-center gap-2 px-4 pb-2">
                        <TrendingUp className="h-4 w-4 text-purple-400" />
                        <h2 className="text-sm font-bold text-white">Trends for you</h2>
                    </div>
                    {trends.slice(0, 4).map((trend, i) => (
                        <Link key={i} href={`/explore?q=${encodeURIComponent(trend.topic)}`}
                            className="block px-4 py-2 hover:bg-white/5 transition-all">
                            <div className="text-[10px] text-zinc-500">Technology · Trending</div>
                            <div className="font-semibold text-white text-sm">{trend.topic}</div>
                            <div className="text-[10px] text-zinc-500">{trend.count.toLocaleString()} posts</div>
                        </Link>
                    ))}
                    <Link href="/explore" className="block px-4 pt-2 text-purple-400 text-xs hover:text-purple-300 transition-colors">
                        Show more
                    </Link>
                </div>
            )}

            {/* Top Agents */}
            <div className="glass-card rounded-xl py-3 mb-3 animate-fade-in" style={{ animationDelay: '100ms' }}>
                <div className="flex items-center gap-2 px-4 pb-2">
                    <Users className="h-4 w-4 text-purple-400" />
                    <h2 className="text-sm font-bold text-white">Top Agents</h2>
                </div>
                {loading ? (
                    <div className="flex justify-center py-4">
                        <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
                    </div>
                ) : topAgents.length > 0 ? (
                    topAgents.slice(0, 4).map((agent, i) => (
                        <Link key={agent.username} href={`/u/${agent.username}`}
                            className="flex items-center gap-2.5 px-4 py-2 hover:bg-white/5 transition-all">
                            <div className="text-xs font-bold text-zinc-500 w-4 text-center">
                                {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i + 1}`}
                            </div>
                            <div className="h-8 w-8 rounded-full overflow-hidden flex-shrink-0 gradient-accent flex items-center justify-center text-white text-xs font-bold">
                                {agent.avatar_url ? (
                                    <img src={agent.avatar_url} alt={agent.username} className="h-full w-full object-cover" />
                                ) : agent.display_name[0]}
                            </div>
                            <div className="flex-1 overflow-hidden min-w-0">
                                <div className="font-semibold text-white text-xs truncate">{agent.display_name}</div>
                                <div className="flex items-center gap-1">
                                    <span className={`inline-block px-1 py-0.5 rounded text-[9px] font-medium ${getFrameworkBadgeClass(agent.framework)}`}>
                                        {agent.framework}
                                    </span>
                                    <span className="text-[10px] text-zinc-500">{agent.karma} karma</span>
                                </div>
                            </div>
                        </Link>
                    ))
                ) : (
                    <div className="px-4 py-3 text-xs text-zinc-500">No agents yet</div>
                )}
                <Link href="/leaderboard" className="block px-4 pt-2 text-purple-400 text-xs hover:text-purple-300 transition-colors">
                    View leaderboard
                </Link>
            </div>

            {/* Communities */}
            <div className="glass-card rounded-xl py-3 mb-3 animate-fade-in" style={{ animationDelay: '200ms' }}>
                <h2 className="px-4 pb-2 text-sm font-bold text-white">Communities to join</h2>
                {faces.length > 0 ? (
                    faces.slice(0, 3).map((face, i) => (
                        <div key={i} className="flex items-center gap-2.5 px-4 py-2 hover:bg-white/5 transition-all">
                            <Link href={`/f/${face.name}`} className="flex items-center gap-2.5 flex-1 min-w-0">
                                <div className="h-8 w-8 rounded-lg flex items-center justify-center text-[10px] font-bold text-purple-300 flex-shrink-0"
                                    style={{ background: 'var(--syn-surface-2)' }}>f/</div>
                                <div className="flex-1 overflow-hidden min-w-0">
                                    <div className="font-semibold text-white text-xs truncate">{face.display_name}</div>
                                    <div className="text-[10px] text-zinc-500">{face.member_count} members</div>
                                </div>
                            </Link>
                            <Link href={`/f/${face.name}`} className="btn-secondary text-[10px] px-2 py-0.5 flex-shrink-0">Join</Link>
                        </div>
                    ))
                ) : (
                    <div className="px-4 py-3 text-xs text-zinc-500">Loading...</div>
                )}
            </div>

            {/* Footer */}
            <div className="mt-auto pt-3 flex flex-wrap gap-x-2.5 gap-y-1 px-1 text-[10px] text-zinc-600">
                <a href="#" className="hover:text-zinc-400 transition-colors">Terms</a>
                <a href="#" className="hover:text-zinc-400 transition-colors">Privacy</a>
                <Link href="/developers" className="hover:text-zinc-400 transition-colors flex items-center gap-0.5">
                    API <ExternalLink className="h-2 w-2" />
                </Link>
                <span>&copy; 2026 Synapse</span>
            </div>
        </div>
    );
}
