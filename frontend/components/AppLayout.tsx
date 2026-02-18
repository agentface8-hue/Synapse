'use client';

import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import LeftSidebar from './LeftSidebar';
import RightSidebar from './RightSidebar';

interface AppLayoutProps {
    children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-black text-white">
            {/* Mobile header */}
            <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-3 border-b bg-black/90 backdrop-blur-lg"
                style={{ borderColor: 'var(--syn-border)' }}>
                <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 text-zinc-400 hover:text-white">
                    {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </button>
                <span className="text-lg font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                    Synapse
                </span>
                <div className="w-9" /> {/* Spacer for centering */}
            </div>

            {/* Mobile sidebar overlay */}
            {mobileMenuOpen && (
                <div className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
                    onClick={() => setMobileMenuOpen(false)} />
            )}

            {/* Left Sidebar - responsive */}
            <div className={`
                fixed left-0 top-0 h-screen z-50
                transition-transform duration-300 ease-in-out
                md:translate-x-0
                ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
            `}>
                <LeftSidebar />
            </div>

            {/* Right Sidebar - hidden on mobile/tablet */}
            <RightSidebar />

            {/* Main Content - responsive margins */}
            <main
                className="min-h-screen border-l border-r relative
                    pt-14 md:pt-0
                    ml-0 md:ml-[275px]
                    mr-0 lg:mr-[350px]
                    max-w-none md:max-w-[600px]"
                style={{ borderColor: 'var(--syn-border)' }}
            >
                {children}
            </main>
        </div>
    );
}
