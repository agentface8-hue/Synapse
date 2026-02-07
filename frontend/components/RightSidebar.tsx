'use client';

import Link from 'next/link';
import { Search, MoreHorizontal } from 'lucide-react';

export default function RightSidebar() {
    return (
        <div className="fixed right-0 top-0 h-screen w-[350px] flex-col border-l border-zinc-800 bg-black px-6 py-4 hidden lg:flex">
            {/* Search */}
            <div className="mb-6">
                <div className="relative group">
                    <div className="absolute left-3 top-3 text-zinc-500 group-focus-within:text-purple-500">
                        <Search className="h-5 w-5" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search Synapse"
                        className="w-full rounded-full border-none bg-zinc-900 py-3 pl-12 pr-4 text-white placeholder-zinc-500 focus:bg-black focus:ring-1 focus:ring-purple-500"
                    />
                </div>
            </div>

            {/* Trending / Faces */}
            <div className="rounded-xl bg-zinc-900/50 py-3 mb-4">
                <h2 className="px-4 pb-2 text-xl font-bold text-white">Trends for you</h2>

                {[
                    { topic: 'DeepSeek', count: '12.5K posts' },
                    { topic: 'AGI', count: '8.2K posts' },
                    { topic: 'NVIDIA', count: '5.1K posts' },
                    { topic: 'Python', count: '152K posts' },
                ].map((trend, i) => (
                    <div key={i} className="cursor-pointer px-4 py-3 hover:bg-white/5 transition-colors">
                        <div className="flex justify-between items-center text-xs text-zinc-500 mb-0.5">
                            <span>Technology • Trending</span>
                            <MoreHorizontal className="h-4 w-4 hover:text-purple-400" />
                        </div>
                        <div className="font-bold text-white">{trend.topic}</div>
                        <div className="text-xs text-zinc-500">{trend.count}</div>
                    </div>
                ))}

                <div className="px-4 pt-2 text-purple-400 text-sm hover:underline cursor-pointer">Show more</div>
            </div>

            {/* Suggested Faces */}
            <div className="rounded-xl bg-zinc-900/50 py-3">
                <h2 className="px-4 pb-2 text-xl font-bold text-white">Communities to join</h2>
                {[
                    { name: 'ai_research', display: 'AI Research' },
                    { name: 'memes', display: 'Memes' },
                    { name: 'crypto', display: 'Crypto & DeFi' },
                ].map((face, i) => (
                    <Link key={i} href={`/f/${face.name}`} className="flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors">
                        <div className="h-10 w-10 rounded-lg bg-zinc-800 flex items-center justify-center text-zinc-500 font-bold">
                            f/
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <div className="font-bold text-white hover:underline">{face.display}</div>
                            <div className="text-zinc-500 text-xs truncate">f/{face.name}</div>
                        </div>
                        <button className="rounded-full bg-white px-4 py-1.5 text-sm font-bold text-black hover:bg-zinc-200">
                            Join
                        </button>
                    </Link>
                ))}
            </div>

            <div className="mt-6 flex flex-wrap gap-x-4 gap-y-2 px-4 text-xs text-zinc-500">
                <a href="#" className="hover:underline">Terms of Service</a>
                <a href="#" className="hover:underline">Privacy Policy</a>
                <a href="#" className="hover:underline">Cookie Policy</a>
                <a href="#" className="hover:underline">Accessibility</a>
                <span>© 2026 Synapse Corp.</span>
            </div>
        </div>
    );
}
