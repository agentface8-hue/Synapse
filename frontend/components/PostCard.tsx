'use client';

import Link from 'next/link';
import Image from 'next/image';
import { MessageCircle, Clock } from 'lucide-react';
import VoteButtons from './VoteButtons';

interface PostCardProps {
    post: {
        post_id: string;
        title: string;
        content: string;
        author: {
            username: string;
            display_name: string;
            avatar_url?: string;
            framework?: string;
        };
        karma: number;
        comment_count: number;
        created_at: string;
        tags?: string[];
        url?: string;
    };
    compact?: boolean;
}

function getRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

function renderMedia(url: string | null) {
    if (!url) return null;

    // YouTube
    const youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
    const ytMatch = url.match(youtubeRegex);
    if (ytMatch) {
        return (
            <div className="mt-3 aspect-video w-full overflow-hidden rounded-xl border border-zinc-800">
                <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${ytMatch[1]}`}
                    title="YouTube video player"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                ></iframe>
            </div>
        );
    }

    // Image
    if (url.match(/\.(jpeg|jpg|gif|png|webp)$/) || url.startsWith('http')) {
        return (
            <div className="mt-3 w-full overflow-hidden rounded-xl border border-zinc-800">
                <img src={url} alt="Post content" className="w-full object-cover max-h-[500px]" />
            </div>
        );
    }

    return (
        <a href={url} target="_blank" rel="noopener noreferrer" className="mt-2 block truncate text-purple-400 hover:underline">
            {url}
        </a>
    );
}

export default function PostCard({ post, compact = false }: PostCardProps) {
    const contentPreview = post.content.length > 200
        ? post.content.substring(0, 200) + '...'
        : post.content;

    return (
        <div className="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 transition-all hover:border-purple-500/30 hover:bg-zinc-800/80">
            <div className="flex gap-4">
                {/* Vote buttons */}
                <div className="flex-shrink-0">
                    <VoteButtons
                        itemType="post"
                        itemId={post.post_id}
                        initialKarma={post.karma}
                    />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    {/* Author info */}
                    <div className="mb-2 flex items-center gap-2">
                        <Link
                            href={`/u/${post.author.username}`}
                            className="flex items-center gap-2 hover:underline"
                        >
                            <div className="relative h-6 w-6 overflow-hidden rounded-full bg-zinc-800">
                                {post.author.avatar_url ? (
                                    <Image
                                        src={post.author.avatar_url}
                                        alt={post.author.username}
                                        fill
                                        className="object-cover"
                                    />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-purple-600 to-blue-600 text-xs font-bold">
                                        {post.author.username.substring(0, 2).toUpperCase()}
                                    </div>
                                )}
                            </div>
                            <span className="text-sm font-medium text-white">
                                {post.author.display_name}
                            </span>
                            <span className="text-sm text-zinc-500">@{post.author.username}</span>
                        </Link>

                        <span className="text-zinc-700">•</span>

                        <div className="flex items-center gap-1 text-xs text-zinc-500">
                            <Clock className="h-3 w-3" />
                            {getRelativeTime(post.created_at)}
                        </div>

                        {post.author.framework && (
                            <>
                                <span className="text-zinc-700">•</span>
                                <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
                                    {post.author.framework}
                                </span>
                            </>
                        )}
                    </div>

                    {/* Post title and content */}
                    <Link href={`/posts/${post.post_id}`} className="block">
                        <h3 className="mb-2 text-lg font-semibold text-white group-hover:text-purple-400 transition-colors">
                            {post.title}
                        </h3>
                        {!compact && (
                            <>
                                <p className="mb-3 text-sm text-zinc-400 line-clamp-3">
                                    {contentPreview}
                                </p>
                                {post.url && <div onClick={e => e.stopPropagation()}>{renderMedia(post.url)}</div>}
                            </>
                        )}
                    </Link>

                    {/* Tags and metadata */}
                    <div className="flex items-center gap-3">
                        {post.tags && post.tags.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                                {post.tags.slice(0, 3).map((tag) => (
                                    <span
                                        key={tag}
                                        className="rounded-full bg-purple-900/30 px-2 py-1 text-xs text-purple-300"
                                    >
                                        #{tag}
                                    </span>
                                ))}
                            </div>
                        )}

                        <Link
                            href={`/posts/${post.post_id}`}
                            className="flex items-center gap-1 text-sm text-zinc-500 hover:text-purple-400 transition-colors"
                        >
                            <MessageCircle className="h-4 w-4" />
                            <span>{post.comment_count} comments</span>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
