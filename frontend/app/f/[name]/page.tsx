'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Users, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Face, FaceService } from '@/services/FaceService';
import PostCard from '@/components/PostCard';
import AppLayout from '@/components/AppLayout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function FacePage() {
    const params = useParams();
    const faceName = params?.name as string;

    const [face, setFace] = useState<Face | null>(null);
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (faceName) {
            loadData();
        }
    }, [faceName]);

    const loadData = async () => {
        try {
            setLoading(true);
            const [faceData, postsRes] = await Promise.all([
                FaceService.getFace(faceName),
                fetch(`${API_URL}/api/v1/posts?face_name=${faceName}&limit=50`)
            ]);

            if (!postsRes.ok) throw new Error('Failed to fetch posts');
            const postsData = await postsRes.json();

            setFace(faceData);
            setPosts(postsData);
        } catch (err: any) {
            setError(err.message || 'Failed to load community');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
            </div>
        );
    }

    if (error || !face) {
        return (
            <div className="min-h-screen bg-black text-white p-8 text-center">
                <div className="text-red-500 mb-4">{error}</div>
                <Link href="/faces" className="text-zinc-400 hover:text-white underline">Back to Directory</Link>
            </div>
        );
    }

    return (
        <AppLayout>
            <div className="bg-black text-white">
                {/* Banner Area */}
                <div className="h-32 bg-gradient-to-r from-purple-900 to-black border-b border-zinc-800"></div>

                <div className="mx-auto max-w-4xl px-4">
                    {/* Header */}
                    <div className="-mt-12 mb-8 flex items-end gap-6">
                        <div className="h-24 w-24 rounded-lg bg-zinc-900 border-4 border-black flex items-center justify-center">
                            <span className="text-3xl font-bold text-zinc-500">f/</span>
                        </div>
                        <div className="flex-1 pb-2">
                            <h1 className="text-3xl font-bold flex items-center gap-2">
                                {face.display_name}
                                {face.is_official && <span className="bg-purple-600 text-xs px-2 py-0.5 rounded-full">Official</span>}
                            </h1>
                            <p className="text-zinc-400 text-sm">f/{face.name}</p>
                        </div>
                        <div className="pb-4 flex gap-4 text-sm font-medium">
                            <div className="text-center">
                                <div className="text-white">{face.member_count}</div>
                                <div className="text-zinc-500 text-xs">Members</div>
                            </div>
                            <div className="text-center">
                                <div className="text-white">{face.post_count}</div>
                                <div className="text-zinc-500 text-xs">Posts</div>
                            </div>
                        </div>
                    </div>

                    {/* Description */}
                    <div className="mb-8 rounded-lg bg-zinc-900/50 p-6 border border-zinc-800">
                        <p className="text-zinc-300">{face.description || 'Welcome to this community.'}</p>
                    </div>

                    {/* Navigation */}
                    <div className="mb-6 flex gap-4 border-b border-zinc-800 pb-4">
                        <Link href="/faces" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-white">
                            <ArrowLeft className="h-4 w-4" /> Directory
                        </Link>
                        <span className="text-zinc-700">|</span>
                        <span className="text-white font-bold text-sm">Posts</span>
                    </div>

                    {/* Posts Feed */}
                    <div className="space-y-4 pb-12">
                        {posts.length === 0 ? (
                            <div className="text-center py-12 text-zinc-500">
                                No posts yet in this community.
                            </div>
                        ) : (
                            posts.map(post => (
                                <PostCard key={post.post_id} post={post} />
                            ))
                        )}
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
