'use client';

import LeftSidebar from './LeftSidebar';
import RightSidebar from './RightSidebar';

interface AppLayoutProps {
    children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
    return (
        <div className="min-h-screen bg-black text-white">
            {/* Left Sidebar - fixed */}
            <LeftSidebar />

            {/* Right Sidebar - fixed */}
            <RightSidebar />

            {/* Main Content - centered between fixed sidebars */}
            <main
                className="min-h-screen border-l border-r relative"
                style={{
                    marginLeft: '275px',
                    marginRight: '350px',
                    maxWidth: '600px',
                    borderColor: 'var(--syn-border)',
                    zIndex: 1,
                }}
            >
                {children}
            </main>
        </div>
    );
}
