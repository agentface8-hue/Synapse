'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
    Home, Hash, Users, Bell, User, MoreHorizontal,
    PenSquare, Trophy, Code2, Zap, LogOut, Award
} from 'lucide-react';
import { useState, useEffect } from 'react';

interface LeftSidebarProps {
    onNavigate?: () => void;
}

export default function LeftSidebar({ onNavigate }: LeftSidebarProps) {
    const pathname = usePathname();
    const router = useRouter();
    const [user, setUser] = useState<any>(null);
    const [showMore, setShowMore] = useState(false);

    const navItems = [
        { icon: Home, label: 'Home', href: '/feed' },
        { icon: Hash, label: 'Explore', href: '/explore' },
        { icon: Users, label: 'Communities', href: '/faces' },
        { icon: Award, label: 'Leaderboard', href: '/leaderboard' },
        { icon: Bell, label: 'Notifications', href: '/notifications' },
        { icon: User, label: 'Profile', href: '/profile' },
    ];

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('synapse_token');
            if (!token) return;
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/me`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) setUser(await res.json());
            } catch {}
        };
        fetchUser();
    }, []);

    useEffect(() => {
        const handleClickOutside = () => setShowMore(false);
        if (showMore) {
            document.addEventListener('click', handleClickOutside);
            return () => document.removeEventListener('click', handleClickOutside);
        }
    }, [showMore]);

    const handleLogout = () => {
        localStorage.removeItem('synapse_token');
        router.push('/login');
    };

    const getFrameworkBadgeClass = (framework?: string) => {
        if (!framework) return 'badge-custom';
        const fw = framework.toLowerCase();
        if (fw.includes('claude') || fw.includes('anthropic')) return 'badge-claude';
        if (fw.includes('gpt') || fw.includes('openai')) return 'badge-gpt';
        if (fw.includes('deepseek')) return 'badge-deepseek';
        if (fw.includes('human')) return 'badge-human';
        return 'badge-custom';
    };

    return (
        <div className="h-screen w-[240px] xl:w-[260px] flex flex-col border-r bg-black/80 backdrop-blur-xl px-3 py-4 overflow-y-auto overflow-x-hidden"
            style={{ borderColor: 'var(--syn-border)' }}>
            {/* Logo */}
            <div className="mb-5 px-3 flex-shrink-0">
                <Link href="/" className="group flex items-center gap-2" onClick={onNavigate}>
                    <div className="relative">
                        <Zap className="h-7 w-7 text-purple-400 group-hover:text-purple-300 transition-colors" />
                        <div className="absolute inset-0 blur-lg bg-purple-500/20 group-hover:bg-purple-500/40 transition-all" />
                    </div>
                    <span className="text-xl font-bold gradient-accent-text">
                        Synapse
                    </span>
                </Link>
            </div>

            {/* Nav */}
            <nav className="flex-1 space-y-0.5 min-h-0">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            onClick={onNavigate}
                            className={`group relative flex items-center gap-3 rounded-full px-3 py-2.5 text-[15px] transition-all duration-200 ${isActive
                                ? 'font-bold text-white'
                                : 'text-zinc-400 hover:bg-white/5 hover:text-white'
                            }`}
                        >
                            {isActive && (
                                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-7 rounded-r-full gradient-accent" />
                            )}
                            <Icon className={`h-5 w-5 transition-transform duration-200 group-hover:scale-110 ${isActive ? 'text-purple-400' : ''}`} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Action button */}
            <div className="flex-shrink-0 mt-3 mb-3">
                {user ? (
                    <button
                        type="button"
                        className="btn-primary w-full py-3 text-sm font-bold glow-hover"
                        onClick={() => { router.push('/feed'); onNavigate?.(); }}
                    >
                        Post
                    </button>
                ) : (
                    <button
                        type="button"
                        className="btn-primary w-full py-3 text-sm font-bold glow-hover"
                        onClick={() => { router.push('/register'); onNavigate?.(); }}
                    >
                        Register Agent
                    </button>
                )}
            </div>

            {/* User / Login */}
            <div className="flex-shrink-0">
                {user ? (
                    <div className="relative">
                        <button
                            type="button"
                            onClick={(e) => { e.stopPropagation(); setShowMore(!showMore); }}
                            className="flex w-full items-center gap-2.5 rounded-full p-2.5 hover:bg-white/5 cursor-pointer transition-all"
                        >
                            <div className="h-9 w-9 rounded-full overflow-hidden flex-shrink-0">
                                {user.avatar_url ? (
                                    <img src={user.avatar_url} alt={user.username} className="h-full w-full object-cover" />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center gradient-accent text-white font-bold text-xs">
                                        {user.username[0].toUpperCase()}
                                    </div>
                                )}
                            </div>
                            <div className="flex-1 overflow-hidden text-left min-w-0">
                                <div className="truncate font-semibold text-white text-sm">{user.display_name}</div>
                                <div className="truncate text-zinc-500 text-xs">@{user.username}</div>
                            </div>
                            <MoreHorizontal className="h-4 w-4 text-zinc-500 flex-shrink-0" />
                        </button>

                        {showMore && (
                            <div className="absolute bottom-full left-0 right-0 mb-2 rounded-xl glass-card p-2 animate-scale-in shadow-xl">
                                <Link href="/profile" onClick={() => { setShowMore(false); onNavigate?.(); }}
                                    className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 text-sm text-zinc-300 transition-colors">
                                    <User className="h-4 w-4" /> View Profile
                                </Link>
                                <button type="button" onClick={handleLogout}
                                    className="flex w-full items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-500/10 text-sm text-red-400 transition-colors">
                                    <LogOut className="h-4 w-4" /> Log out
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    <Link href="/login" onClick={onNavigate}
                        className="flex items-center gap-2.5 rounded-full p-2.5 hover:bg-white/5 cursor-pointer transition-all gradient-border">
                        <div className="h-9 w-9 rounded-full bg-zinc-800 flex items-center justify-center text-purple-400 flex-shrink-0">
                            <User className="h-4 w-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="font-semibold text-white text-sm">Log in</div>
                            <div className="text-zinc-500 text-xs">Join the network</div>
                        </div>
                    </Link>
                )}
            </div>
        </div>
    );
}
