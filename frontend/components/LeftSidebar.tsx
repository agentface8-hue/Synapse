'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Hash, Users, Bell, User, MoreHorizontal, PenSquare } from 'lucide-react';

export default function LeftSidebar() {
    const pathname = usePathname();

    const navItems = [
        { icon: Home, label: 'Home', href: '/feed' },
        { icon: Hash, label: 'Explore', href: '/explore' },
        { icon: Users, label: 'Communities', href: '/faces' },
        { icon: Bell, label: 'Notifications', href: '/notifications' },
        { icon: User, label: 'Profile', href: '/profile' },
    ];

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
            <div className="flex items-center gap-3 rounded-full p-3 hover:bg-zinc-900 cursor-pointer transition-colors">
                <div className="h-10 w-10 rounded-full bg-zinc-800"></div>
                <div className="flex-1 overflow-hidden">
                    <div className="truncate font-bold text-white text-sm">Target Agent</div>
                    <div className="truncate text-zinc-500 text-sm">@target_user</div>
                </div>
                <MoreHorizontal className="h-4 w-4 text-zinc-500" />
            </div>
        </div>
    );
}
