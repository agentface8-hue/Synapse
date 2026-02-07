'use client';

import LeftSidebar from './LeftSidebar';
import RightSidebar from './RightSidebar';

interface AppLayoutProps {
    children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
    return (
        <div className="min-h-screen bg-black text-white">
            <div className="mx-auto flex max-w-[1300px] justify-center">
                {/* Left Sidebar */}
                <LeftSidebar />

                {/* Main Content (Feed) */}
                <main className="flex w-full max-w-[600px] flex-col border-r border-zinc-800 md:w-[600px] md:border-l min-h-screen">
                    {children}
                </main>

                {/* Right Sidebar */}
                <RightSidebar />
            </div>
        </div>
    );
}
