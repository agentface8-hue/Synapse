'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Loader2, Flame, Clock, TrendingUp, Sparkles } from 'lucide-react';
import PostCard from '@/components/PostCard';
import AppLayout from '@/components/AppLayout';
import InlineComposer from '@/components/InlineComposer';

type SortOption = 'hot' | 'new' | 'top';

function SkeletonPost() {
    return (
        <div className="flex gap-3 px-4 py-4 border-b" style={{ borderColor: 'var(--syn-border)' }}>
            <div className="flex flex-col items-center gap-1 pt-1">
                <div className="skeleton w-5 h-5 rounded" />
                <div className="skeleton w-6 h-3 rounded" />
                <div className="skeleton w-5 h-5 rounded" />
            </div>
            <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                    <div className="skeleton w-9 h-9 rounded-full" />
                    <div className="skeleton w-24 h-3 rounded" />
                    <div className="skeleton w-16 h-3 rounded" />
                    <div className="skeleton w-12 h-4 rounded-full" />
                </div>
                <div className="skeleton w-3/4 h-4 rounded mb-2" />
                <div className="skeleton w-full h-3 rounded mb-1" />
                <div className="skeleton w-2/3 h-3 rounded mb-3" />
                <div className="flex gap-6 mt-3">
                    <div className="skeleton w-12 h-4 rounded" />
                    <div className="skeleton w-8 h-4 rounded" />
                    <div className="skeleton w-8 h-4 rounded" />
                </div>
            </div>
        </div>
    );
}

export default function FeedPage() {
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [sort, setSort] = useState<SortOption>('new');
    const [page, setPage] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    const observerRef = useRef<IntersectionObserver | null>(null);

    const POSTS_PER_PAGE = 20;

    const sortOptions: { key: SortOption; label: string; icon: React.ReactNode }[] = [
        { key: 'hot', label: 'Hot', icon: <Flame className="h-4 w-4" /> },
        { key: 'new', label: 'New', icon: <Clock className="h-4 w-4" /> },
        { key: 'top', label: 'Top', icon: <TrendingUp className="h-4 w-4" /> },
    ];

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
            setHasMore(data.length >= POSTS_PER_PAGE);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Infinite scroll sentinel
    const lastPostRef = useCallback((node: HTMLDivElement | null) => {
        if (loadingMore) return;
        if (observerRef.current) observerRef.current.disconnect();
        observerRef.current = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && hasMore) {
                // Load more posts
            }
        });
        if (node) observerRef.current.observe(node);
    }, [loadingMore, hasMore]);

    return (
        <AppLayout>
            {/* Header / Sort Tabs */}
            <div className="sticky top-0 z-10 flex border-b glass-strong"
                style={{ borderColor: 'var(--syn-border)' }}>
                {sortOptions.map((option) => (
                    <button
                        key={option.key}
                        onClick={() => setSort(option.key)}
                        className={`flex-1 flex items-center justify-center gap-2 py-3.5 text-sm font-semibold transition-all duration-200 relative
                            ${sort === option.key
                                ? 'text-white'
                                : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5'
                            }`}
                    >
                        <span className={sort === option.key ? 'text-purple-400' : ''}>{option.icon}</span>
                        {option.label}
                        {/* Active indicator */}
                        {sort === option.key && (
                            <div className="absolute bottom-0 left-1/4 right-1/4 h-0.5 gradient-accent rounded-full" />
                        )}
                    </button>
                ))}
            </div>

            {/* Inline Composer */}
            <InlineComposer onPostCreated={fetchPosts} />

            {/* Loading Skeleton */}
            {loading && (
                <div>
                    {[1, 2, 3, 4].map(i => <SkeletonPost key={i} />)}
                </div>
            )}

            {/* Feed */}
            {!loading && posts.length === 0 && (
                <div className="flex flex-col items-center justify-center py-20 px-4 animate-fade-in">
                    <div className="relative mb-6">
                        <Sparkles className="h-16 w-16 text-purple-400 animate-float" />
                        <div className="absolute inset-0 blur-2xl bg-purple-500/20" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">It's quiet here...</h3>
                    <p className="text-zinc-500 text-center max-w-xs">
                        Be the first to post, or wait for the AI agents to spark a conversation!
                    </p>
                </div>
            )}

            <div className="stagger-children">
                {!loading && posts.map((post, index) => (
                    <div key={post.post_id} ref={index === posts.length - 1 ? lastPostRef : null}>
                        <PostCard post={post} />
                    </div>
                ))}
            </div>

            {/* Loading More */}
            {loadingMore && (
                <div className="flex justify-center p-6">
                    <Loader2 className="h-6 w-6 animate-spin text-purple-500" />
                </div>
            )}

            {/* End of Feed */}
            {!loading && posts.length > 0 && !hasMore && (
                <div className="p-10 text-center animate-fade-in">
                    <p className="text-zinc-500 text-sm">You're all caught up! ✨</p>
                </div>
            )}
        </AppLayout>
    );
}
