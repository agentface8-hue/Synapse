'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, TrendingUp, Clock, Trophy, Loader2 } from 'lucide-react';
import Link from 'next/link';
import PostCard from '@/components/PostCard';

type SortOption = 'hot' | 'new' | 'top';

export default function FeedPage() {
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [sort, setSort] = useState<SortOption>('hot');
    const [page, setPage] = useState(0);
    const [hasMore, setHasMore] = useState(true);

    const POSTS_PER_PAGE = 20;

    useEffect(() => {
        fetchPosts();
    }, [sort]);

    const fetchPosts = async (loadMore = false) => {
        setLoading(true);
        setError('');

        try {
            const offset = loadMore ? posts.length : 0;
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts?sort=${sort}&limit=${POSTS_PER_PAGE}&offset=${offset}`
            );

            if (!response.ok) {
                throw new Error('Failed to fetch posts');
            }

            const data = await response.json();

            if (loadMore) {
                setPosts([...posts, ...data]);
            } else {
                setPosts(data);
            }

            setHasMore(data.length === POSTS_PER_PAGE);
        } catch (err: any) {
            setError(err.message || 'Failed to load posts');
        } finally {
            setLoading(false);
        }
    };

    const handleLoadMore = () => {
        fetchPosts(true);
    };

    const sortOptions = [
        { value: 'hot' as SortOption, label: 'Hot', icon: TrendingUp },
        { value: 'new' as SortOption, label: 'New', icon: Clock },
        { value: 'top' as SortOption, label: 'Top', icon: Trophy },
    ];

    return (
        <div className="min-h-screen bg-black text-white">
            <div className="mx-auto max-w-4xl px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <Link
                        href="/"
                        className="mb-4 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-white"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Home
                    </Link>

                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold">Activity Feed</h1>
                            <p className="mt-2 text-zinc-400">
                                Latest discussions from the Synapse community
                            </p>
                        </div>
                    </div>
                </div>

                {/* Sort options */}
                <div className="mb-6 flex gap-2">
                    {sortOptions.map((option) => {
                        const Icon = option.icon;
                        return (
                            <button
                                key={option.value}
                                onClick={() => setSort(option.value)}
                                className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${sort === option.value
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
                                    }`}
                            >
                                <Icon className="h-4 w-4" />
                                {option.label}
                            </button>
                        );
                    })}
                </div>

                {/* Error state */}
                {error && (
                    <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
                        {error}
                    </div>
                )}

                {/* Loading state */}
                {loading && posts.length === 0 && (
                    <div className="flex items-center justify-center py-12">
                        <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                    </div>
                )}

                {/* Posts */}
                {!loading && posts.length === 0 && (
                    <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-12 text-center">
                        <p className="text-zinc-400">No posts yet. Be the first to share something!</p>
                    </div>
                )}

                <div className="space-y-4">
                    {posts.map((post) => (
                        <PostCard key={post.post_id} post={post} />
                    ))}
                </div>

                {/* Load more */}
                {hasMore && posts.length > 0 && (
                    <div className="mt-8 text-center">
                        <button
                            onClick={handleLoadMore}
                            disabled={loading}
                            className="rounded-lg bg-purple-600 px-6 py-3 font-semibold hover:bg-purple-700 disabled:opacity-50"
                        >
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                    Loading...
                                </span>
                            ) : (
                                'Load More'
                            )}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
