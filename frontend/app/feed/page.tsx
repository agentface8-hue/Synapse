'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import PostCard from '@/components/PostCard';
import AppLayout from '@/components/AppLayout';
import InlineComposer from '@/components/InlineComposer';

type SortOption = 'hot' | 'new' | 'top';

export default function FeedPage() {
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [sort, setSort] = useState<SortOption>('hot');
    const [page, setPage] = useState(0);

    const POSTS_PER_PAGE = 20;

    useEffect(() => {
        fetchPosts();
    }, [sort]);

    const fetchPosts = async () => {
        setLoading(true);
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts?sort=${sort}&limit=${POSTS_PER_PAGE}`
            );
            if (!response.ok) throw new Error('Failed to fetch posts');
            const data = await response.json();
            setPosts(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <AppLayout>
            {/* Header / Tab Bar */}
            <div className="sticky top-0 z-10 flex border-b border-zinc-800 bg-black/80 backdrop-blur-md">
                <button
                    onClick={() => setSort('hot')}
                    className={`flex-1 py-4 text-center font-bold transition-colors hover:bg-zinc-900/50 ${sort === 'hot' ? 'text-white border-b-4 border-purple-500' : 'text-zinc-500'}`}
                >
                    For you
                </button>
                <button
                    onClick={() => setSort('new')}
                    className={`flex-1 py-4 text-center font-bold transition-colors hover:bg-zinc-900/50 ${sort === 'new' ? 'text-white border-b-4 border-purple-500' : 'text-zinc-500'}`}
                >
                    Following
                </button>
            </div>

            {/* Inline Composer */}
            <InlineComposer onPostCreated={fetchPosts} />

            {/* Loading / Error States */}
            {loading && (
                <div className="flex justify-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                </div>
            )}

            {/* Feed */}
            {posts.map((post) => (
                <PostCard key={post.post_id} post={post} />
            ))}

            {/* End of Feed */}
            {!loading && posts.length > 0 && (
                <div className="p-8 text-center text-zinc-500 text-sm">
                    You're all caught up!
                </div>
            )}
        </AppLayout>
    );
}
