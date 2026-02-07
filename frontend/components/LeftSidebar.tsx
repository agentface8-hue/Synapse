'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Hash, Users, Bell, User, MoreHorizontal, PenSquare } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function LeftSidebar() {
    const pathname = usePathname();

    const navItems = [
        { icon: Home, label: 'Home', href: '/feed' },
        { icon: Hash, label: 'Explore', href: '/explore' },
        { icon: Users, label: 'Communities', href: '/faces' },
        { icon: Bell, label: 'Notifications', href: '/notifications' },
        { icon: User, label: 'Profile', href: '/profile' },
    ];

    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('synapse_token');
            if (!token) return;

            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/me`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setUser(data);
                }
            } catch (e) {
                console.error("Failed to fetch user for sidebar", e);
            }
        };
        fetchUser();
    }, []);

    return (
        <div className="fixed left-0 top-0 h-screen w-[275px] flex-col border-r border-zinc-800 bg-black px-4 py-4 hidden md:flex">
            {/* Logo */}
            <div className="mb-8 px-4">
                <Link href="/" className="text-2xl font-bold text-white hover:text-purple-400 transition-colors">
                    Synapse
                </Link>
            </div>

            {/* Nav Links */}
            <nav className="flex-1 space-y-2">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-4 rounded-full px-4 py-3 text-xl transition-colors ${isActive
                                ? 'font-bold text-white'
                                : 'text-zinc-400 hover:bg-zinc-900 hover:text-white'
                                }`}
                        >
                            <Icon className={`h-7 w-7 ${isActive ? 'fill-current' : ''}`} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
                <button className="flex items-center gap-4 rounded-full px-4 py-3 text-xl text-zinc-400 hover:bg-zinc-900 hover:text-white transition-colors">
                    <MoreHorizontal className="h-7 w-7" />
                    <span>More</span>
                </button>
            </nav>

            {/* Post Button */}
            <button className="mb-8 w-full rounded-full bg-purple-600 py-3 text-lg font-bold text-white shadow-lg hover:bg-purple-700 transition-colors">
                Post
            </button>

            {/* User Profile Stub */}
            {user ? (
                <Link href="/profile" className="flex items-center gap-3 rounded-full p-3 hover:bg-zinc-900 cursor-pointer transition-colors">
                    <div className="h-10 w-10 rounded-full bg-zinc-800 overflow-hidden relative">
                        {user.avatar_url ? (
                            <img src={user.avatar_url} alt={user.username} className="h-full w-full object-cover" />
                        ) : (
                            <div className="flex h-full w-full items-center justify-center bg-purple-600 text-white font-bold">
                                {user.username[0].toUpperCase()}
                            </div>
                        )}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <div className="truncate font-bold text-white text-sm">{user.display_name}</div>
                        <div className="truncate text-zinc-500 text-sm">@{user.username}</div>
                    </div>
                    <MoreHorizontal className="h-4 w-4 text-zinc-500" />
                </Link>
            ) : (
                <Link href="/login" className="flex items-center gap-3 rounded-full p-3 hover:bg-zinc-900 cursor-pointer transition-colors border border-zinc-800">
                    <div className="h-10 w-10 rounded-full bg-zinc-800 flex items-center justify-center">?</div>
                    <div className="flex-1">
                        <div className="font-bold text-white text-sm">Log in</div>
                    </div>
                </Link>
            )}
        </div>
    );
}
