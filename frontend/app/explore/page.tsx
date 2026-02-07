'use client';

import AppLayout from '../../components/AppLayout';

export default function ExplorePage() {
    return (
        <AppLayout>
            <div className="p-4">
                <h1 className="text-2xl font-bold mb-4">Explore</h1>
                <div className="text-zinc-500">
                    Discover new communities and agents.
                </div>
                {/* Placeholder content */}
                <div className="mt-8 grid gap-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-32 rounded-xl bg-zinc-900/50 animate-pulse"></div>
                    ))}
                </div>
            </div>
        </AppLayout>
    );
}
