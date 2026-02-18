'use client';

import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import LeftSidebar from './LeftSidebar';
import RightSidebar from './RightSidebar';
import Link from 'next/link';

interface AppLayoutProps {
    children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-black text-white">
            {/* Mobile top bar - only on small screens */}
            <div className="lg:hidden fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-3 border-b bg-black/95 backdrop-blur-lg"
                style={{ borderColor: 'var(--syn-border)' }}>
                <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-1.5 text-zinc-400 hover:text-white transition-colors">
                    {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </button>
                <Link href="/" className="text-lg font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                    Synapse
                </Link>
                <div className="w-8" />
            </div>

            {/* Mobile overlay */}
            {mobileMenuOpen && (
                <div className="lg:hidden fixed inset-0 z-40 bg-black/70 backdrop-blur-sm"
                    onClick={() => setMobileMenuOpen(false)} />
            )}

            {/* Left Sidebar */}
            <div className={`
                fixed left-0 top-0 h-screen z-50
                transition-transform duration-300 ease-in-out
                lg:translate-x-0
                ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
            `}>
                <LeftSidebar onNavigate={() => setMobileMenuOpen(false)} />
            </div>

            {/* Right Sidebar - desktop only */}
            <RightSidebar />

            {/* Main content area */}
            <main
                className="min-h-screen relative
                    pt-14 lg:pt-0
                    ml-0 lg:ml-[240px] xl:ml-[260px]
                    mr-0 xl:mr-[300px]"
            >
                <div className="max-w-[620px] mx-auto lg:mx-0 border-x"
                    style={{ borderColor: 'var(--syn-border)' }}>
                    {children}
                </div>
            </main>
        </div>
    );
}
