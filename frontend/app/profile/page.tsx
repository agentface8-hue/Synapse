'use client';

import { useEffect, useState } from 'react';
import AppLayout from '../../components/AppLayout';
import { Loader2 } from 'lucide-react';

export default function ProfilePage() {
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            const token = localStorage.getItem('synapse_token');
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/me`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setUser(data);
                }
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (loading) {
        return (
            <AppLayout>
                <div className="flex justify-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                </div>
            </AppLayout>
        );
    }

    if (!user) {
        return (
            <AppLayout>
                <div className="p-4 text-center">
                    <h1 className="text-2xl font-bold mb-4">Profile</h1>
                    <p className="text-zinc-500">Please log in to view your profile.</p>
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout>
            <div className="relative">
                {/* Banner */}
                <div className="h-48 bg-zinc-800 w-full overflow-hidden">
                    {user.banner_url && <img src={user.banner_url} alt="Banner" className="w-full h-full object-cover" />}
                </div>

                <div className="px-4 pb-4">
                    {/* Avatar */}
                    <div className="relative -mt-16 mb-4 h-32 w-32 rounded-full border-4 border-black bg-zinc-900 overflow-hidden">
                        {user.avatar_url ? (
                            <img src={user.avatar_url} alt={user.username} className="h-full w-full object-cover" />
                        ) : (
                            <div className="flex h-full w-full items-center justify-center text-4xl font-bold text-white">
                                {user.username[0].toUpperCase()}
                            </div>
                        )}
                    </div>

                    <h1 className="text-2xl font-bold text-white">{user.display_name}</h1>
                    <p className="text-zinc-500">@{user.username}</p>

                    <div className="mt-4 text-white">
                        {user.bio || "No bio yet."}
                    </div>

                    <div className="mt-4 flex gap-4 text-zinc-500 text-sm">
                        <span><strong className="text-white">{user.post_count}</strong> Posts</span>
                        <span><strong className="text-white">{user.comment_count}</strong> Comments</span>
                        <span><strong className="text-white">{user.karma}</strong> Karma</span>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
